<script lang="ts">
  import { resolve } from "$app/paths";
  import { APP_NAME } from "$lib/version";
</script>

<svelte:head>
  <title>EB Digital · Einsatzkraft</title>
</svelte:head>

<h1>EB Digital — Einsatzkraft</h1>
<p>
  Phase-1-Skelett. Anonyme Bestellung über Einsatz-URL folgt ab Phase 4 (Operations Core), nachdem
  Spike I die geografische Plausibilitäts-Logik geklärt hat.
</p>
<p>
  <a href={resolve("/health")}>Health-Status</a> · App: <code>{APP_NAME}</code>
</p>
