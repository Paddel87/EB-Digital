<script lang="ts">
  import { resolve } from "$app/paths";
  import { APP_NAME } from "$lib/version";
</script>

<svelte:head>
  <title>EB Digital · Disponent</title>
</svelte:head>

<h1>EB Digital — Disponent</h1>
<p>
  Phase-1-Skelett. UI folgt ab Phase 2 (Auth + Tenants), Disposition ab Phase 4 (Operations Core).
</p>
<p>
  <a href={resolve("/health")}>Health-Status</a> · App: <code>{APP_NAME}</code>
</p>
