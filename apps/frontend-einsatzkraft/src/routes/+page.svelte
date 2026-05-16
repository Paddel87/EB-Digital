<script lang="ts">
  import { resolve } from "$app/paths";
  import { APP_NAME } from "$lib/version";
</script>

<svelte:head>
  <title>EB Digital · Einsatzkraft</title>
</svelte:head>

<section>
  <h1>EB Digital — Einsatzkraft</h1>
  <p>
    Diese App brauchst du nur, wenn dir ein Disponent eine <strong>Einsatz-URL</strong> geschickt oder
    einen QR-Code gezeigt hat. Öffne den Link bzw. scanne den QR-Code, um in den Einsatz zu gelangen.
  </p>
  <p class="hint">
    Phase 2 stellt die Anmeldung mit Einsatz-URL und optionalem Zugangscode bereit. Der Bestellpfad
    folgt in Phase 4 (Operations Core), nachdem Spike I die geografische Plausibilitäts-Logik
    geklärt hat.
  </p>
  <p>
    <a href={resolve("/health")}>Health-Status</a> · App: <code>{APP_NAME}</code>
  </p>
</section>

<style>
  section {
    max-width: 480px;
    margin: 3rem auto;
  }
  h1 {
    margin-bottom: 0.5rem;
  }
  p {
    line-height: 1.5;
  }
  .hint {
    color: #555;
    font-size: 0.95rem;
  }
</style>
