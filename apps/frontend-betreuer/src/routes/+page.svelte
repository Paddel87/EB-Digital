<script lang="ts">
  import { resolve } from "$app/paths";
  import { APP_NAME } from "$lib/version";
</script>

<svelte:head>
  <title>EB Digital · Betreuer</title>
</svelte:head>

<h1>EB Digital — Betreuer</h1>
<p>
  Phase-1-Skelett. Auftragsanzeige, Karte und Turn-by-Turn-Navigation folgen ab Phase 6 (Spike L
  liefert die Tile-Caching-Strategie davor).
</p>
<p>
  <a href={resolve("/health")}>Health-Status</a> · App: <code>{APP_NAME}</code>
</p>
