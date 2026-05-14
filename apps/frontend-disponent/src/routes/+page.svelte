<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { ApiError } from "$lib/api/client";
  import { me } from "$lib/api/auth";
  import { setSession } from "$lib/stores/session";

  // Der Root-Pfad ist neutral: bei aktiver Session geht es zum Dashboard,
  // sonst zur Anmeldung. Kein eigenes UI nötig — diese Datei ist die einzige
  // Datei in `routes/`, die nicht in einer der Route-Gruppen liegt.

  onMount(async () => {
    try {
      const user = await me();
      setSession(user);
      await goto(resolve("/dashboard"), { replaceState: true });
    } catch (cause) {
      if (cause instanceof ApiError && cause.kind === "auth") {
        await goto(resolve("/login"), { replaceState: true });
      } else {
        // Bei Netzwerk- oder Server-Fehler: trotzdem zum Login schicken;
        // dort wird der Fehler beim Login-Versuch erneut sichtbar.
        await goto(resolve("/login"), { replaceState: true });
      }
    }
  });
</script>

<svelte:head>
  <title>EB Digital · Disponent</title>
</svelte:head>

<p>Weiterleitung …</p>
