"""Tests für ``backend/eb_digital/operations/schemas`` (Schritt 4.3a)."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from eb_digital.operations.schemas import (
    OpenOperationRequest,
    OrderItemIn,
    PlaceOrderRequest,
    Polygon,
)

_RING = [[8.80, 53.07], [8.81, 53.07], [8.81, 53.08], [8.80, 53.07]]


# ─── Polygon ──────────────────────────────────────────────────────────────────


def test_polygon_valid() -> None:
    p = Polygon(type="Polygon", coordinates=[_RING])
    assert p.coordinates[0][0] == p.coordinates[0][-1]


def test_polygon_empty_rejected() -> None:
    with pytest.raises(ValidationError):
        Polygon(type="Polygon", coordinates=[])


def test_polygon_too_few_points_rejected() -> None:
    with pytest.raises(ValidationError):
        Polygon(type="Polygon", coordinates=[[[8.8, 53.0], [8.9, 53.0], [8.8, 53.0]]])


def test_polygon_open_ring_rejected() -> None:
    with pytest.raises(ValidationError):
        Polygon(
            type="Polygon", coordinates=[[[8.8, 53.0], [8.9, 53.0], [8.9, 53.1], [8.85, 53.05]]]
        )


def test_polygon_point_wrong_length_rejected() -> None:
    bad = [[8.8, 53.0, 1.0], [8.9, 53.0, 1.0], [8.9, 53.1, 1.0], [8.8, 53.0, 1.0]]
    with pytest.raises(ValidationError):
        Polygon(type="Polygon", coordinates=[bad])


def test_polygon_lng_out_of_range_rejected() -> None:
    bad = [[181.0, 53.0], [8.9, 53.0], [8.9, 53.1], [181.0, 53.0]]
    with pytest.raises(ValidationError):
        Polygon(type="Polygon", coordinates=[bad])


def test_polygon_lat_out_of_range_rejected() -> None:
    bad = [[8.8, 91.0], [8.9, 53.0], [8.9, 53.1], [8.8, 91.0]]
    with pytest.raises(ValidationError):
        Polygon(type="Polygon", coordinates=[bad])


# ─── OrderItemIn ───────────────────────────────────────────────────────────────


def test_order_item_exactly_one_ref_base_ok() -> None:
    item = OrderItemIn(base_item_id=uuid.uuid4(), quantity=2)
    assert item.tenant_extension_id is None


def test_order_item_both_refs_rejected() -> None:
    with pytest.raises(ValidationError):
        OrderItemIn(base_item_id=uuid.uuid4(), tenant_extension_id=uuid.uuid4(), quantity=1)


def test_order_item_no_ref_rejected() -> None:
    with pytest.raises(ValidationError):
        OrderItemIn(quantity=1)


# ─── PlaceOrderRequest ─────────────────────────────────────────────────────────


def test_place_order_gps_ok() -> None:
    req = PlaceOrderRequest(
        items=[OrderItemIn(base_item_id=uuid.uuid4(), quantity=1)],
        location_lat=53.07,
        location_lng=8.80,
        location_accuracy_m=12.0,
    )
    assert req.location_text is None


def test_place_order_text_only_ok() -> None:
    req = PlaceOrderRequest(
        items=[OrderItemIn(base_item_id=uuid.uuid4(), quantity=1)],
        location_text="Marktplatz",
    )
    assert req.location_lat is None


def test_place_order_lat_without_lng_rejected() -> None:
    with pytest.raises(ValidationError):
        PlaceOrderRequest(
            items=[OrderItemIn(base_item_id=uuid.uuid4(), quantity=1)],
            location_lat=53.07,
        )


def test_place_order_neither_gps_nor_text_rejected() -> None:
    with pytest.raises(ValidationError):
        PlaceOrderRequest(items=[OrderItemIn(base_item_id=uuid.uuid4(), quantity=1)])


# ─── OpenOperationRequest ──────────────────────────────────────────────────────


def test_open_operation_requires_area() -> None:
    with pytest.raises(ValidationError):
        OpenOperationRequest(city_label="Bremen", areas=[])


def test_open_operation_threshold_range() -> None:
    with pytest.raises(ValidationError):
        OpenOperationRequest(
            city_label="Bremen",
            areas=[{"area_index": 1, "polygon": {"type": "Polygon", "coordinates": [_RING]}}],  # type: ignore[list-item]
            plausibility_threshold_m=10,  # < 50
        )
