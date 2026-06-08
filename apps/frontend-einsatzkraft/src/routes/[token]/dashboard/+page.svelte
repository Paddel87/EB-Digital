<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { ApiError } from "$lib/api/client";
  import { fetchCatalog, type ResolvedCatalogItem } from "$lib/api/catalog";
  import { placeOrder, type AnonymousOrderOut, type PlaceOrderRequest } from "$lib/api/operations";
  import { getCurrentPosition, GeolocationError, type GpsPosition } from "$lib/location";
  import {
    decrementQuantity,
    incrementQuantity,
    isEmpty,
    setQuantity,
    toOrderItems,
    totalQuantity,
    type CartQuantities,
  } from "$lib/stores/cart";
  import { AnonymousRealtimeClient } from "$lib/realtime/ws";
  import { outcomeMessage, statusLabel } from "$lib/order-display";
  import type { PageData } from "./$types";

  type Props = { data: PageData };
  let { data }: Props = $props();

  interface CatalogGroup {
    categoryId: string;
    categoryName: string;
    items: ResolvedCatalogItem[];
  }

  let catalog = $state<ResolvedCatalogItem[] | null>(null);
  let catalogError = $state<string | null>(null);

  let quantities = $state<CartQuantities>({});

  let gps = $state<GpsPosition | null>(null);
  let gpsBusy = $state(false);
  let gpsError = $state<string | null>(null);
  let locationText = $state("");

  let isSubmitting = $state(false);
  let submitError = $state<string | null>(null);
  let rateLimitedUntil = $state<number | null>(null);
  let remainingSeconds = $state(0);

  let order = $state<AnonymousOrderOut | null>(null);
  let liveStatus = $state<string | null>(null);
  let realtimeConnected = $state(false);

  let client: AnonymousRealtimeClient | null = null;

  const grouped = $derived(groupByCategory(catalog ?? []));
  const cartCount = $derived(totalQuantity(quantities));
  const hasLocation = $derived(gps !== null || locationText.trim().length > 0);
  const canSubmit = $derived(
    !isEmpty(quantities) && hasLocation && !isSubmitting && rateLimitedUntil === null,
  );

  function groupByCategory(items: ResolvedCatalogItem[]): CatalogGroup[] {
    // Array-basiert (kein Map) — `svelte/prefer-svelte-reactivity` würde
    // einen built-in Map in der Komponente beanstanden; die Gruppierung ist
    // reine, nicht-reaktive Ableitung über kleinen Katalogen.
    const groups: CatalogGroup[] = [];
    for (const item of items) {
      let group = groups.find((candidate) => candidate.categoryId === item.category_id);
      if (group === undefined) {
        group = { categoryId: item.category_id, categoryName: item.category_name, items: [] };
        groups.push(group);
      }
      group.items.push(item);
    }
    return groups;
  }

  onMount(() => {
    void loadCatalog();
    client = new AnonymousRealtimeClient(data.token, {
      onOrderStatus: (event) => {
        if (order !== null && event.orderId === order.id) {
          liveStatus = event.status;
        }
      },
      onConnectionChange: (connected) => {
        realtimeConnected = connected;
      },
    });
    client.connect();
    return () => {
      client?.close();
      client = null;
    };
  });

  $effect(() => {
    if (rateLimitedUntil === null) {
      remainingSeconds = 0;
      return;
    }
    const tick = () => {
      const remaining = Math.max(0, Math.ceil((rateLimitedUntil! - Date.now()) / 1000));
      remainingSeconds = remaining;
      if (remaining === 0) {
        rateLimitedUntil = null;
      }
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  });

  async function loadCatalog(): Promise<void> {
    catalogError = null;
    try {
      catalog = await fetchCatalog(data.token);
    } catch (cause) {
      catalog = [];
      if (cause instanceof ApiError && cause.kind === "auth") {
        await handleSessionExpiry();
        return;
      }
      catalogError = "Artikel konnten nicht geladen werden. Bitte Seite neu laden.";
    }
  }

  async function handleSessionExpiry(): Promise<void> {
    client?.close();
    client = null;
    await goto(resolve(`/${data.token}`), { replaceState: true });
  }

  function adjust(itemId: string, delta: 1 | -1): void {
    quantities =
      delta === 1 ? incrementQuantity(quantities, itemId) : decrementQuantity(quantities, itemId);
  }

  function onQuantityInput(itemId: string, event: Event): void {
    const target = event.currentTarget as HTMLInputElement;
    const parsed = Number.parseInt(target.value, 10);
    quantities = setQuantity(quantities, itemId, Number.isNaN(parsed) ? 0 : parsed);
  }

  async function requestGps(): Promise<void> {
    gpsBusy = true;
    gpsError = null;
    try {
      gps = await getCurrentPosition();
      locationText = "";
    } catch (cause) {
      gps = null;
      gpsError = mapGeoError(cause);
    } finally {
      gpsBusy = false;
    }
  }

  function clearGps(): void {
    gps = null;
  }

  function mapGeoError(cause: unknown): string {
    if (cause instanceof GeolocationError) {
      if (cause.kind === "permission") {
        return "Standortfreigabe verweigert. Du kannst deinen Standort stattdessen als Text beschreiben.";
      }
      if (cause.kind === "unsupported") {
        return "Dein Gerät unterstützt keine Standortbestimmung. Bitte beschreibe deinen Standort als Text.";
      }
      if (cause.kind === "timeout") {
        return "Standortbestimmung hat zu lange gedauert. Bitte erneut versuchen oder Text verwenden.";
      }
    }
    return "Standort konnte nicht bestimmt werden. Bitte erneut versuchen oder Text verwenden.";
  }

  function setRateLimit(retryAfter: number | null): void {
    const wait = retryAfter ?? 60;
    rateLimitedUntil = Date.now() + wait * 1000;
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (!canSubmit) return;

    isSubmitting = true;
    submitError = null;
    const request: PlaceOrderRequest = { items: toOrderItems(quantities, catalog ?? []) };
    if (gps !== null) {
      request.location_lat = gps.lat;
      request.location_lng = gps.lng;
      request.location_accuracy_m = gps.accuracyM;
    } else {
      request.location_text = locationText.trim();
    }

    try {
      const result = await placeOrder(data.token, request);
      order = result;
      liveStatus = result.status;
      quantities = {};
    } catch (cause) {
      if (cause instanceof ApiError) {
        if (cause.kind === "rate-limit") {
          setRateLimit(cause.retryAfter);
          submitError = "Zu viele Bestellungen. Bitte kurz warten.";
        } else if (cause.kind === "auth") {
          await handleSessionExpiry();
          return;
        } else if (cause.kind === "not-found" || cause.kind === "gone") {
          submitError = "Dieser Einsatz ist nicht mehr aktiv.";
        } else if (cause.kind === "validation") {
          submitError = "Bestellung konnte nicht verarbeitet werden. Bitte Eingaben prüfen.";
        } else if (cause.kind === "network") {
          submitError = "Server nicht erreichbar. Bitte Verbindung prüfen.";
        } else {
          submitError = "Bestellung fehlgeschlagen. Bitte erneut versuchen.";
        }
      } else {
        submitError = "Unerwarteter Fehler. Bitte erneut versuchen.";
      }
    } finally {
      isSubmitting = false;
    }
  }

  function startNewOrder(): void {
    order = null;
    liveStatus = null;
    gps = null;
    locationText = "";
    submitError = null;
  }
</script>

<svelte:head>
  <title>Bestellung · EB Digital Einsatzkraft</title>
</svelte:head>

<section>
  <h1>Versorgung anfordern</h1>
  <p class="area" data-testid="dashboard-area-label">{data.areaLabel}</p>

  {#if order !== null}
    <!-- Tracking-Ansicht (eine aktive Bestellung, 7A) -->
    <div class="tracking" data-testid="order-tracking">
      <p class="outcome" data-testid="order-outcome">
        {outcomeMessage(order.plausibility_outcome)}
      </p>
      <p class="status-line">
        <span class="status-label">Status:</span>
        <span data-testid="order-status">{statusLabel(liveStatus ?? order.status)}</span>
      </p>
      <p class="conn" data-testid="realtime-state">
        {realtimeConnected ? "Live-Aktualisierung aktiv." : "Verbindung wird aufgebaut …"}
      </p>
      <button type="button" onclick={startNewOrder} data-testid="new-order-button">
        Neue Bestellung
      </button>
    </div>
  {:else}
    <!-- Bestell-Ansicht -->
    {#if catalogError}
      <p class="error" role="alert" data-testid="catalog-error">{catalogError}</p>
    {:else if catalog === null}
      <p data-testid="catalog-loading">Lade Artikel …</p>
    {:else if grouped.length === 0}
      <p data-testid="catalog-empty">Für diesen Einsatz sind keine Artikel hinterlegt.</p>
    {:else}
      <form onsubmit={handleSubmit} novalidate>
        <div class="catalog" data-testid="catalog">
          {#each grouped as group (group.categoryId)}
            <fieldset>
              <legend>{group.categoryName}</legend>
              {#each group.items as item (item.id)}
                <div class="item" data-testid="catalog-item">
                  <div class="item-info">
                    <span class="item-name">{item.name}</span>
                    <span class="item-unit">{item.default_unit_label}</span>
                  </div>
                  <div class="stepper">
                    <button
                      type="button"
                      onclick={() => adjust(item.id, -1)}
                      aria-label={`${item.name} verringern`}
                      disabled={(quantities[item.id] ?? 0) === 0}
                    >
                      −
                    </button>
                    <input
                      type="number"
                      inputmode="numeric"
                      min="0"
                      max="10000"
                      value={quantities[item.id] ?? 0}
                      oninput={(event) => onQuantityInput(item.id, event)}
                      aria-label={`Menge ${item.name}`}
                      data-testid="quantity-input"
                    />
                    <button
                      type="button"
                      onclick={() => adjust(item.id, 1)}
                      aria-label={`${item.name} erhöhen`}
                    >
                      +
                    </button>
                  </div>
                </div>
              {/each}
            </fieldset>
          {/each}
        </div>

        <div class="location">
          <h2>Standort</h2>
          {#if gps !== null}
            <p class="gps-ok" data-testid="gps-active">
              GPS-Standort übernommen (Genauigkeit ca. {Math.round(gps.accuracyM)} m).
            </p>
            <button type="button" class="link" onclick={clearGps} data-testid="gps-clear">
              Standort verwerfen
            </button>
          {:else}
            <button type="button" onclick={requestGps} disabled={gpsBusy} data-testid="gps-button">
              {gpsBusy ? "Standort wird bestimmt …" : "Standort freigeben (GPS)"}
            </button>
            {#if gpsError}
              <p class="hint" data-testid="gps-error">{gpsError}</p>
            {/if}
            <label>
              Oder Standort beschreiben
              <input
                type="text"
                maxlength="255"
                bind:value={locationText}
                placeholder="z. B. Kreuzung Hauptstr. / Marktplatz"
                data-testid="location-text"
              />
            </label>
          {/if}
        </div>

        {#if submitError}
          <p class="error" role="alert" data-testid="submit-error">{submitError}</p>
        {/if}
        {#if rateLimitedUntil !== null && remainingSeconds > 0}
          <p class="hint" data-testid="rate-limit-hint">
            Wiederholung möglich in {remainingSeconds} Sekunde{remainingSeconds === 1 ? "" : "n"}.
          </p>
        {/if}

        <button type="submit" disabled={!canSubmit} data-testid="submit-button">
          {isSubmitting ? "Wird gesendet …" : `Bestellung absenden (${cartCount})`}
        </button>
      </form>
    {/if}
  {/if}
</section>

<style>
  section {
    max-width: 560px;
    margin: 2rem auto;
    padding: 0 1rem;
  }
  h1 {
    margin-bottom: 0.25rem;
  }
  .area {
    color: #1a4f8a;
    font-weight: 600;
    font-size: 1.1rem;
    margin: 0 0 1.5rem 0;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  fieldset {
    border: 1px solid #ddd;
    border-radius: 6px;
    margin: 0 0 0.75rem 0;
    padding: 0.5rem 0.75rem 0.75rem;
  }
  legend {
    font-weight: 600;
    color: #333;
    padding: 0 0.4rem;
  }
  .item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid #f0f0f0;
  }
  .item:last-child {
    border-bottom: none;
  }
  .item-info {
    display: flex;
    flex-direction: column;
  }
  .item-name {
    font-weight: 500;
  }
  .item-unit {
    color: #777;
    font-size: 0.85rem;
  }
  .stepper {
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .stepper button {
    width: 2.4rem;
    height: 2.4rem;
    font-size: 1.3rem;
    border: 1px solid #aaa;
    border-radius: 4px;
    background: #f7f7f7;
    cursor: pointer;
  }
  .stepper button:disabled {
    color: #bbb;
    cursor: not-allowed;
  }
  .stepper input {
    width: 3.5rem;
    text-align: center;
    font-size: 1.1rem;
    padding: 0.4rem;
    border: 1px solid #aaa;
    border-radius: 4px;
  }
  .location h2 {
    font-size: 1rem;
    margin: 0 0 0.5rem 0;
  }
  .location label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-top: 0.75rem;
    font-weight: 500;
  }
  .location input[type="text"] {
    padding: 0.6rem 0.75rem;
    font-size: 1rem;
    border: 1px solid #aaa;
    border-radius: 4px;
  }
  button[type="submit"],
  .location > button,
  .tracking button {
    padding: 0.85rem 1rem;
    font-size: 1rem;
    font-weight: 600;
    background-color: #1a4f8a;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  button[type="submit"]:disabled {
    background-color: #888;
    cursor: not-allowed;
  }
  .link {
    background: none;
    border: none;
    color: #1a4f8a;
    text-decoration: underline;
    cursor: pointer;
    padding: 0.25rem 0;
    font-size: 0.9rem;
  }
  .gps-ok {
    color: #1a6f3a;
    font-weight: 500;
    margin: 0;
  }
  .tracking {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
  .outcome {
    font-weight: 600;
    margin: 0;
  }
  .status-line {
    margin: 0;
  }
  .status-label {
    color: #555;
  }
  .conn {
    color: #777;
    font-size: 0.9rem;
    margin: 0;
  }
  .hint {
    color: #555;
    font-size: 0.9rem;
    margin: 0;
  }
  .error {
    color: #a40000;
    background-color: #fbe9e9;
    border: 1px solid #e6b2b2;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    margin: 0;
  }
</style>
