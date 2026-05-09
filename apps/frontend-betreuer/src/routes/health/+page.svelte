<script lang="ts">
  import { APP_NAME, APP_VERSION, BUILD_TIME } from "$lib/version";
</script>

<svelte:head>
  <title>Health · {APP_NAME}</title>
</svelte:head>

<h1>Health</h1>
<dl>
  <dt>App</dt>
  <dd><code data-testid="app-name">{APP_NAME}</code></dd>
  <dt>Version</dt>
  <dd><code data-testid="app-version">{APP_VERSION}</code></dd>
  <dt>Build</dt>
  <dd><code data-testid="build-time">{BUILD_TIME}</code></dd>
</dl>

<style>
  dl {
    display: grid;
    grid-template-columns: 8rem 1fr;
    gap: 0.5rem 1rem;
  }
  dt {
    font-weight: 600;
  }
</style>
