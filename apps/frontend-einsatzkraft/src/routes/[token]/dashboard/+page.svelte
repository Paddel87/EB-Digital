<script lang="ts">
  import type { PageData } from "./$types";

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();
</script>

<svelte:head>
  <title>Angemeldet · EB Digital Einsatzkraft</title>
</svelte:head>

<section>
  <h1>Anmeldung erfolgreich</h1>
  <p class="area" data-testid="dashboard-area-label">{data.areaLabel}</p>

  <p class="placeholder" data-testid="phase-4-placeholder">
    Bestellpfad und Karten-Anzeige folgen in Phase 4 (Operations Core).
  </p>
  <p class="hint">
    Du kannst diese Seite geöffnet lassen — die Sitzung bleibt für die Dauer des Einsatzes (max. 24
    Stunden) aktiv.
  </p>
</section>

<style>
  section {
    max-width: 480px;
    margin: 3rem auto;
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
  .placeholder {
    color: #555;
    font-style: italic;
  }
  .hint {
    color: #777;
    font-size: 0.9rem;
  }
</style>
