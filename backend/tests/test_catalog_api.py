"""Tests für ``backend/eb_digital/catalog/api`` (Catalog-CRUD + Resolver-Routen).

Berechtigungs-Modell:
  • Plattform-Admin: voller CRUD auf /categories und /base.
  • Disponent: voller CRUD auf /tenant nur für eigenen Tenant.
  • Carer: nur Read auf /catalog (eigener Tenant).
  • Anon: Read auf /anon/{url}/catalog mit Session-Pflicht + IP/URL-Rate-Limit.

Strategie analog ``test_tenants_api``: echtes ``SessionMiddleware``
(Cookie-Round-Trip via Login), ``fakeredis`` als Valkey-Stub, DB-Session
stubbed, Repository- und Use-Case-Funktionen via ``monkeypatch`` ersetzt.
Für den Anon-Pfad wird ``get_current_anonymous_session`` direkt gepatcht,
weil das Cookie-Set über ``POST /anon/.../session`` einen vollen
auth_anonymous-Setup brauchen würde.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth import api as auth_api
from eb_digital.auth.api import get_db_session, get_valkey_client
from eb_digital.auth.hashing import hash_password
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
)
from eb_digital.auth_anonymous.sessions import AnonymousSessionUser
from eb_digital.catalog import api as catalog_api
from eb_digital.catalog import repositories as catalog_repo
from eb_digital.catalog import use_cases as catalog_use_cases
from eb_digital.catalog.models import (
    CatalogCategory,
    CatalogItemBase,
    CatalogItemTenantExtension,
)
from eb_digital.catalog.schemas import ResolvedCatalogItem
from eb_digital.operations.models import OPERATION_STATUS_ACTIVE
from eb_digital.operations.models import Operation as OperationModel
from eb_digital.tenants.use_cases import TenantNotActiveError


class _StubDbSession:
    async def commit(self) -> None:
        return None

    async def execute(self, _stmt: Any) -> Any:
        # Wird nur vom Anon-Endpoint für den Operation-Lookup aufgerufen.
        # Tests setzen `_operation_result` via Closure (siehe make_client).
        return _OperationResult.current


class _OperationResult:
    """Holder für das Operation-Resultat im _StubDbSession.execute-Pfad."""

    current: Any = None

    def __init__(self, op: OperationModel | None) -> None:
        self._op = op

    def scalar_one_or_none(self) -> OperationModel | None:
        return self._op


@pytest.fixture
async def fake_valkey() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    client = fakeredis.aioredis.FakeRedis()
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


def _make_subject(
    *,
    kind: str = KIND_DISPATCHER,
    username: str = "alice",
    password: str = "correcthorsebattery",
    tenant_id: uuid.UUID | None = None,
) -> AuthSubject:
    return AuthSubject(
        kind=kind,  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password(password),
        is_active=True,
        tenant_id=tenant_id
        if tenant_id is not None
        else (None if kind == KIND_PLATFORM_ADMIN else uuid.uuid4()),
    )


def _make_category(name: str = "Getränke") -> CatalogCategory:
    cat = CatalogCategory(name=name)
    cat.id = uuid.uuid4()
    cat.created_at = datetime.now(UTC)
    cat.updated_at = datetime.now(UTC)
    return cat


def _make_base_item(*, is_active: bool = True) -> CatalogItemBase:
    item = CatalogItemBase(
        name="Wasser",
        unit="liter",
        default_unit_label="Liter",
        category_id=uuid.uuid4(),
        is_active=is_active,
    )
    item.id = uuid.uuid4()
    item.created_at = datetime.now(UTC)
    item.updated_at = datetime.now(UTC)
    return item


def _make_override_ext(
    *, tenant_id: uuid.UUID, base_item_id: uuid.UUID
) -> CatalogItemTenantExtension:
    ext = CatalogItemTenantExtension(
        tenant_id=tenant_id,
        base_item_id=base_item_id,
        override_name="Wasser still",
        is_disabled=False,
    )
    ext.id = uuid.uuid4()
    ext.created_at = datetime.now(UTC)
    ext.updated_at = datetime.now(UTC)
    return ext


def _make_own_ext(*, tenant_id: uuid.UUID) -> CatalogItemTenantExtension:
    ext = CatalogItemTenantExtension(
        tenant_id=tenant_id,
        base_item_id=None,
        name="Lokales",
        unit="piece",
        default_unit_label="Stück",
        category_id=uuid.uuid4(),
        is_disabled=False,
    )
    ext.id = uuid.uuid4()
    ext.created_at = datetime.now(UTC)
    ext.updated_at = datetime.now(UTC)
    return ext


def _make_operation(*, status_value: str = OPERATION_STATUS_ACTIVE) -> OperationModel:
    op = OperationModel(
        status=status_value,
        city_label="Bremen Innenstadt",
        url_token="signed-token",
        access_code_active=False,
    )
    op.id = uuid.uuid4()
    op.created_at = datetime.now(UTC)
    op.updated_at = datetime.now(UTC)
    return op


@pytest.fixture
def make_client(
    monkeypatch: pytest.MonkeyPatch,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> Any:
    """Liefert ``make_client(behavior)``.

    ``behavior``-Felder:
      • ``subjects``: dict[username, AuthSubject | None] für Login.
      • ``tenant_login_active``: bool (default True).
      • ``find_category_by_id``: callable | None.
      • ``categories_list``: list[CatalogCategory].
      • ``find_base_item_by_id``: callable | None.
      • ``base_items_list``: list[CatalogItemBase].
      • ``find_extension_by_id``: callable | None.
      • ``extensions_for_tenant``: list[CatalogItemTenantExtension].
      • ``use_case_result``: dict[name, value-or-exception] für create_*/update_* Use-Cases.
      • ``resolver_for_tenant``: list[ResolvedCatalogItem].
      • ``resolver_for_operation``: list[ResolvedCatalogItem].
      • ``anon_session``: AnonymousSessionUser | None.
      • ``url_token_decodes_to``: uuid.UUID | None (für verify_url_token).
      • ``operation_for_anon``: OperationModel | None (Operation-Lookup im Anon-Pfad).
    """

    def _make(behavior: dict[str, Any]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        subjects: dict[str, AuthSubject | None] = behavior.get("subjects", {})

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _fake_find_by_username(_session: Any, username: str) -> AuthSubject | None:
            return subjects.get(username)

        async def _fake_tenant_login_allowed(_db: Any, _subject: AuthSubject) -> bool:
            return bool(behavior.get("tenant_login_active", True))

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api, "find_by_username", _fake_find_by_username)
        monkeypatch.setattr(
            auth_api,
            "_tenant_login_allowed",
            _fake_tenant_login_allowed,
        )

        # Repository-Stubs für Catalog
        if "find_category_by_id" in behavior:
            monkeypatch.setattr(
                catalog_repo,
                "find_category_by_id",
                behavior["find_category_by_id"],
            )
            # use_cases importiert via ``catalog_repo`` → erreichbar.

        async def _fake_list_categories(_session: Any) -> list[CatalogCategory]:
            return list(behavior.get("categories_list", []))

        monkeypatch.setattr(catalog_repo, "list_categories", _fake_list_categories)

        if "find_base_item_by_id" in behavior:
            monkeypatch.setattr(
                catalog_repo,
                "find_base_item_by_id",
                behavior["find_base_item_by_id"],
            )

        async def _fake_list_base_items(
            _session: Any,
            *,
            include_inactive: bool = False,
        ) -> list[CatalogItemBase]:
            items = list(behavior.get("base_items_list", []))
            if not include_inactive:
                items = [i for i in items if i.is_active]
            return items

        monkeypatch.setattr(catalog_repo, "list_base_items", _fake_list_base_items)

        if "find_extension_by_id" in behavior:
            monkeypatch.setattr(
                catalog_repo,
                "find_extension_by_id",
                behavior["find_extension_by_id"],
            )

        async def _fake_list_extensions_for_tenant(
            _session: Any,
            _tenant_id: uuid.UUID,
        ) -> list[CatalogItemTenantExtension]:
            return list(behavior.get("extensions_for_tenant", []))

        monkeypatch.setattr(
            catalog_repo,
            "list_extensions_for_tenant",
            _fake_list_extensions_for_tenant,
        )

        # Use-Case-Stubs
        ucr: dict[str, Any] = behavior.get("use_case_result", {})

        async def _make_uc_stub(name: str, *args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            v = ucr.get(name)
            if isinstance(v, Exception):
                raise v
            return v

        async def _fake_create_category(_session: Any, *, name: str) -> Any:
            del name
            return await _make_uc_stub("create_category")

        async def _fake_create_base_item(_session: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("create_base_item")

        async def _fake_update_base_item(_session: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("update_base_item")

        async def _fake_create_override(_session: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("create_tenant_override")

        async def _fake_create_own(_session: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("create_tenant_own_item")

        async def _fake_update_extension(_session: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("update_tenant_extension")

        async def _fake_resolve_tenant(
            _session: Any,
            _tenant_id: uuid.UUID,
        ) -> list[ResolvedCatalogItem]:
            return list(behavior.get("resolver_for_tenant", []))

        async def _fake_resolve_operation(
            _session: Any,
            _operation_id: uuid.UUID,
        ) -> list[ResolvedCatalogItem]:
            return list(behavior.get("resolver_for_operation", []))

        monkeypatch.setattr(catalog_use_cases, "create_category", _fake_create_category)
        monkeypatch.setattr(catalog_use_cases, "create_base_item", _fake_create_base_item)
        monkeypatch.setattr(catalog_use_cases, "update_base_item", _fake_update_base_item)
        monkeypatch.setattr(catalog_use_cases, "create_tenant_override", _fake_create_override)
        monkeypatch.setattr(catalog_use_cases, "create_tenant_own_item", _fake_create_own)
        monkeypatch.setattr(catalog_use_cases, "update_tenant_extension", _fake_update_extension)
        monkeypatch.setattr(catalog_use_cases, "resolve_catalog_for_tenant", _fake_resolve_tenant)
        monkeypatch.setattr(
            catalog_use_cases, "resolve_catalog_for_operation", _fake_resolve_operation
        )

        # Anon-Pfad-Stubs
        def _fake_anon_session(_request: Any) -> AnonymousSessionUser | None:
            return behavior.get("anon_session")

        monkeypatch.setattr(catalog_api, "get_current_anonymous_session", _fake_anon_session)

        def _fake_verify_url_token(_token: str, _secret: str) -> uuid.UUID | None:
            return behavior.get("url_token_decodes_to")

        monkeypatch.setattr(catalog_api, "verify_url_token", _fake_verify_url_token)

        _OperationResult.current = _OperationResult(behavior.get("operation_for_anon"))

        return TestClient(app)

    return _make


def _login(client: TestClient, *, username: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "correcthorsebattery"},
    )
    assert response.status_code == 200, response.text


# ─── /api/catalog/categories ─────────────────────────────────────────────────


def test_create_category_without_auth_returns_401(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post("/api/catalog/categories", json={"name": "Getränke"})
    assert response.status_code == 401


def test_create_category_as_dispatcher_forbidden(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.post("/api/catalog/categories", json={"name": "Getränke"})
    assert response.status_code == 403


def test_create_category_as_platform_admin_returns_201(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    new_cat = _make_category("Getränke")
    with make_client(
        {
            "subjects": {"patrick": admin},
            "use_case_result": {"create_category": new_cat},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post("/api/catalog/categories", json={"name": "Getränke"})
    assert response.status_code == 201
    assert response.json()["name"] == "Getränke"


def test_create_category_duplicate_name_returns_409(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client(
        {
            "subjects": {"patrick": admin},
            "use_case_result": {
                "create_category": catalog_repo.CategoryNameTakenError("Getränke"),
            },
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post("/api/catalog/categories", json={"name": "Getränke"})
    assert response.status_code == 409


def test_list_categories_as_dispatcher_returns_200(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    cat = _make_category("Getränke")
    with make_client(
        {"subjects": {"alice": dispatcher}, "categories_list": [cat]},
    ) as client:
        _login(client, username="alice")
        response = client.get("/api/catalog/categories")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Getränke"


# ─── /api/catalog/base ───────────────────────────────────────────────────────


def test_create_base_item_as_platform_admin_returns_201(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    new_item = _make_base_item()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "use_case_result": {"create_base_item": new_item},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            "/api/catalog/base",
            json={
                "name": "Wasser",
                "unit": "liter",
                "default_unit_label": "Liter",
                "category_id": str(uuid.uuid4()),
            },
        )
    assert response.status_code == 201
    assert response.json()["name"] == "Wasser"


def test_create_base_item_unknown_category_returns_404(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client(
        {
            "subjects": {"patrick": admin},
            "use_case_result": {
                "create_base_item": catalog_use_cases.CategoryNotFoundError(uuid.uuid4()),
            },
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            "/api/catalog/base",
            json={
                "name": "Wasser",
                "unit": "liter",
                "default_unit_label": "Liter",
                "category_id": str(uuid.uuid4()),
            },
        )
    assert response.status_code == 404


def test_update_base_item_as_dispatcher_forbidden(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.patch(
            f"/api/catalog/base/{uuid.uuid4()}",
            json={"is_active": False},
        )
    assert response.status_code == 403


def test_list_base_items_dispatcher_ignores_include_inactive(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    active = _make_base_item(is_active=True)
    inactive = _make_base_item(is_active=False)
    with make_client(
        {"subjects": {"alice": dispatcher}, "base_items_list": [active, inactive]},
    ) as client:
        _login(client, username="alice")
        response = client.get("/api/catalog/base?include_inactive=true")
    assert response.status_code == 200
    body = response.json()
    # Dispatcher darf nur aktive sehen, auch wenn er ``include_inactive=true`` setzt.
    assert len(body) == 1
    assert body[0]["is_active"] is True


# ─── /api/catalog/tenant ─────────────────────────────────────────────────────


def test_create_override_as_dispatcher_returns_201(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    base_id = uuid.uuid4()
    new_ext = _make_override_ext(tenant_id=tenant_id, base_item_id=base_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {"create_tenant_override": new_ext},
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/catalog/tenant/override",
            json={"base_item_id": str(base_id), "override_name": "Wasser still"},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["base_item_id"] == str(base_id)
    assert body["override_name"] == "Wasser still"


def test_create_override_inactive_base_returns_409(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {
                "create_tenant_override": catalog_use_cases.BaseItemNotActiveError(uuid.uuid4()),
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/catalog/tenant/override",
            json={"base_item_id": str(uuid.uuid4())},
        )
    assert response.status_code == 409


def test_create_override_duplicate_returns_409(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    base_id = uuid.uuid4()
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {
                "create_tenant_override": catalog_repo.DuplicateOverrideError(
                    tenant_id=tenant_id, base_item_id=base_id
                ),
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/catalog/tenant/override",
            json={"base_item_id": str(base_id)},
        )
    assert response.status_code == 409


def test_create_own_item_inactive_tenant_returns_409(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {
                "create_tenant_own_item": TenantNotActiveError(
                    tenant_id=tenant_id, status="deactivated"
                ),
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/catalog/tenant/own",
            json={
                "name": "Lokales",
                "unit": "piece",
                "default_unit_label": "Stück",
                "category_id": str(uuid.uuid4()),
            },
        )
    assert response.status_code == 409


def test_create_own_item_as_carer_forbidden(make_client: Any) -> None:
    carer = _make_subject(kind=KIND_CARER, username="bob")
    with make_client({"subjects": {"bob": carer}}) as client:
        _login(client, username="bob")
        response = client.post(
            "/api/catalog/tenant/own",
            json={
                "name": "Lokales",
                "unit": "piece",
                "default_unit_label": "Stück",
                "category_id": str(uuid.uuid4()),
            },
        )
    assert response.status_code == 403


def test_list_tenant_extensions_pa_without_query_returns_422(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client({"subjects": {"patrick": admin}}) as client:
        _login(client, username="patrick")
        response = client.get("/api/catalog/tenant")
    # PA muss ?tenant_id=... setzen.
    assert response.status_code == 422


def test_list_tenant_extensions_dispatcher_returns_own(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    ext = _make_own_ext(tenant_id=tenant_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "extensions_for_tenant": [ext],
        },
    ) as client:
        _login(client, username="alice")
        response = client.get("/api/catalog/tenant")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["tenant_id"] == str(tenant_id)


def test_patch_extension_cross_tenant_forbidden(make_client: Any) -> None:
    own_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    # Dispatcher gehört zu other_tenant, will Extension von own_tenant bearbeiten.
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=other_tenant)
    ext = _make_own_ext(tenant_id=own_tenant)

    async def _find_ext(_session: Any, _ext_id: uuid.UUID) -> CatalogItemTenantExtension:
        return ext

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_extension_by_id": _find_ext,
        },
    ) as client:
        _login(client, username="alice")
        response = client.patch(
            f"/api/catalog/tenant/{ext.id}",
            json={"is_disabled": True},
        )
    assert response.status_code == 403


def test_patch_extension_unknown_id_returns_404(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)

    async def _find_ext(_session: Any, _ext_id: uuid.UUID) -> None:
        return None

    with make_client(
        {"subjects": {"alice": dispatcher}, "find_extension_by_id": _find_ext},
    ) as client:
        _login(client, username="alice")
        response = client.patch(
            f"/api/catalog/tenant/{uuid.uuid4()}",
            json={"is_disabled": True},
        )
    assert response.status_code == 404


def test_patch_extension_mode_mismatch_returns_409(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    own_ext = _make_own_ext(tenant_id=tenant_id)

    async def _find_ext(_session: Any, _ext_id: uuid.UUID) -> CatalogItemTenantExtension:
        return own_ext

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_extension_by_id": _find_ext,
            "use_case_result": {
                "update_tenant_extension": catalog_use_cases.ExtensionModeError(
                    extension_id=own_ext.id, expected_mode="override"
                ),
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.patch(
            f"/api/catalog/tenant/{own_ext.id}",
            json={"override_name": "X"},
        )
    assert response.status_code == 409


# ─── /api/catalog (Carer Read) ───────────────────────────────────────────────


def test_resolve_for_own_tenant_as_carer_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    carer = _make_subject(kind=KIND_CARER, username="bob", tenant_id=tenant_id)
    resolved = ResolvedCatalogItem(
        id=str(uuid.uuid4()),
        base_item_id=str(uuid.uuid4()),
        source="base",
        name="Wasser",
        unit="liter",
        default_unit_label="Liter",
        description=None,
        category_id=str(uuid.uuid4()),
        category_name="Getränke",
    )
    with make_client(
        {"subjects": {"bob": carer}, "resolver_for_tenant": [resolved]},
    ) as client:
        _login(client, username="bob")
        response = client.get("/api/catalog")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Wasser"


def test_resolve_for_own_tenant_without_auth_returns_401(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.get("/api/catalog")
    assert response.status_code == 401


def test_resolve_for_own_tenant_as_platform_admin_forbidden(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client({"subjects": {"patrick": admin}}) as client:
        _login(client, username="patrick")
        response = client.get("/api/catalog")
    # PA hat kein tenant_id-Binding → 403.
    assert response.status_code == 403


# ─── /api/anon/{url}/catalog ─────────────────────────────────────────────────


def test_anon_catalog_without_session_returns_401(make_client: Any) -> None:
    op_id = uuid.uuid4()
    with make_client({"url_token_decodes_to": op_id}) as client:
        response = client.get("/api/anon/some-token/catalog")
    assert response.status_code == 401


def test_anon_catalog_session_op_mismatch_returns_403(make_client: Any) -> None:
    cookie_op_id = uuid.uuid4()
    url_op_id = uuid.uuid4()  # andere Operation
    anon = AnonymousSessionUser(
        session_id=uuid.uuid4(),
        operation_id=cookie_op_id,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    with make_client(
        {
            "anon_session": anon,
            "url_token_decodes_to": url_op_id,
        },
    ) as client:
        response = client.get("/api/anon/some-token/catalog")
    assert response.status_code == 403


def test_anon_catalog_invalid_token_returns_410(make_client: Any) -> None:
    with make_client({"url_token_decodes_to": None}) as client:
        response = client.get("/api/anon/garbage/catalog")
    assert response.status_code == 410


def test_anon_catalog_happy_path_returns_200(make_client: Any) -> None:
    op = _make_operation()
    anon = AnonymousSessionUser(
        session_id=uuid.uuid4(),
        operation_id=op.id,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    resolved = ResolvedCatalogItem(
        id=str(uuid.uuid4()),
        base_item_id=str(uuid.uuid4()),
        source="base",
        name="Wasser",
        unit="liter",
        default_unit_label="Liter",
        description=None,
        category_id=str(uuid.uuid4()),
        category_name="Getränke",
    )
    with make_client(
        {
            "anon_session": anon,
            "url_token_decodes_to": op.id,
            "operation_for_anon": op,
            "resolver_for_operation": [resolved],
        },
    ) as client:
        response = client.get("/api/anon/valid-token/catalog")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Wasser"


def test_anon_catalog_inactive_operation_returns_410(make_client: Any) -> None:
    op = _make_operation(status_value="closed")
    anon = AnonymousSessionUser(
        session_id=uuid.uuid4(),
        operation_id=op.id,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    with make_client(
        {
            "anon_session": anon,
            "url_token_decodes_to": op.id,
            "operation_for_anon": op,
        },
    ) as client:
        response = client.get("/api/anon/valid-token/catalog")
    assert response.status_code == 410
