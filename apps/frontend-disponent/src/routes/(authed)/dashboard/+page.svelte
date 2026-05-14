<script lang="ts">
  import { ApiError } from "$lib/api/client";
  import { listTenants, type Tenant, type TenantStatus } from "$lib/api/tenants";
  import type { PageData } from "./$types";

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();

  let tenants = $state<Tenant[] | null>(null);
  let isLoading = $state(false);
  let errorMessage = $state<string | null>(null);

  const isCarer = $derived(data.user.kind === "carer");

  async function loadTenants(): Promise<void> {
    if (isCarer) return;
    isLoading = true;
    errorMessage = null;
    try {
      tenants = await listTenants();
    } catch (cause) {
      if (cause instanceof ApiError) {
        errorMessage =
          cause.kind === "network"
            ? "Server nicht erreichbar."
            : "Mandanten konnten nicht geladen werden.";
      } else {
        errorMessage = "Unerwarteter Fehler beim Laden der Mandanten.";
      }
    } finally {
      isLoading = false;
    }
  }

  $effect(() => {
    void loadTenants();
  });

  function statusLabel(status: TenantStatus): string {
    if (status === "applied") return "Beantragt";
    if (status === "active") return "Aktiv";
    return "Deaktiviert";
  }

  function statusClass(status: TenantStatus): string {
    return `badge badge-${status}`;
  }

  function formatDate(iso: string | null): string {
    if (iso === null) return "—";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return iso;
    return date.toLocaleString("de-DE", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
</script>

<svelte:head>
  <title>Dashboard · EB Digital Disponent</title>
</svelte:head>

{#if isCarer}
  <section class="carer-notice" data-testid="carer-notice">
    <h1>Kein Dashboard-Zugriff</h1>
    <p>
      Phase 2 stellt für die Betreuer-Rolle noch keinen Dashboard-Zugriff bereit. Bitte
      Plattform-Administrator oder einen Disponenten kontaktieren, falls eine Anmeldung als Betreuer
      beabsichtigt war.
    </p>
  </section>
{:else}
  <section>
    <h1>Dashboard</h1>

    <h2>Mandanten</h2>
    {#if isLoading}
      <p data-testid="tenants-loading">Lade Mandanten …</p>
    {:else if errorMessage}
      <p class="error" role="alert" data-testid="tenants-error">{errorMessage}</p>
    {:else if tenants === null || tenants.length === 0}
      <p data-testid="tenants-empty">Keine Mandanten vorhanden.</p>
    {:else}
      <table data-testid="tenants-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Slug</th>
            <th>Status</th>
            <th>Aktiv seit</th>
          </tr>
        </thead>
        <tbody>
          {#each tenants as tenant (tenant.id)}
            <tr data-testid="tenants-row">
              <td>{tenant.name}</td>
              <td><code>{tenant.slug}</code></td>
              <td><span class={statusClass(tenant.status)}>{statusLabel(tenant.status)}</span></td>
              <td>{formatDate(tenant.activated_at)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}

    <h2>Aktive Einsätze</h2>
    <p class="placeholder" data-testid="operations-placeholder">Keine aktiven Einsätze.</p>
    <p class="placeholder-hint">Operations-Funktionalität folgt in Phase 4.</p>
  </section>
{/if}

<style>
  section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  h2 {
    margin-bottom: 0.5rem;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th,
  td {
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid #ddd;
  }
  th {
    background-color: #f4f6f8;
    font-weight: 600;
  }
  .badge {
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
  }
  .badge-applied {
    background-color: #fff4d0;
    color: #6a4d00;
  }
  .badge-active {
    background-color: #d6efdc;
    color: #0a5a2a;
  }
  .badge-deactivated {
    background-color: #e3e3e3;
    color: #555;
  }
  .error {
    color: #a40000;
    background-color: #fbe9e9;
    border: 1px solid #e6b2b2;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    margin: 0;
  }
  .placeholder {
    color: #555;
    font-style: italic;
    margin: 0;
  }
  .placeholder-hint {
    color: #777;
    font-size: 0.9rem;
    margin: 0;
  }
  .carer-notice {
    max-width: 600px;
    margin: 2rem auto;
    text-align: center;
  }
</style>
