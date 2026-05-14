<script lang="ts">
  import type { Snippet } from "svelte";
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { logout } from "$lib/api/auth";
  import { clearSession } from "$lib/stores/session";
  import type { LayoutData } from "./$types";

  type Props = {
    data: LayoutData;
    children: Snippet;
  };

  let { data, children }: Props = $props();

  const kindLabel: Record<"platform_admin" | "dispatcher" | "carer", string> = {
    platform_admin: "Plattform-Admin",
    dispatcher: "Disponent",
    carer: "Betreuer",
  };

  let isLoggingOut = $state(false);

  async function handleLogout(): Promise<void> {
    if (isLoggingOut) return;
    isLoggingOut = true;
    try {
      await logout();
    } catch {
      // Ignorieren: auch wenn der Logout-Request fehlschlägt, leeren wir den
      // Client-Store und navigieren zum Login. Der Server-Cookie ist beim
      // nächsten Request auch ohne explizites Clear ungültig oder läuft ab.
    } finally {
      clearSession();
      isLoggingOut = false;
      await goto(resolve("/login"), { replaceState: true });
    }
  }
</script>

<header>
  <div class="brand">EB Digital · Disponent</div>
  <div class="session" data-testid="session-info">
    <span class="user">{data.user.username}</span>
    <span class="role">({kindLabel[data.user.kind]})</span>
  </div>
  <button type="button" onclick={handleLogout} disabled={isLoggingOut} data-testid="logout-button">
    {isLoggingOut ? "Abmelden …" : "Abmelden"}
  </button>
</header>

<main>
  {@render children()}
</main>

<style>
  header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1.5rem;
    background-color: #1a4f8a;
    color: white;
  }
  .brand {
    font-weight: 600;
    flex: 1;
  }
  .session {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .role {
    opacity: 0.85;
    font-size: 0.9rem;
  }
  button {
    background-color: white;
    color: #1a4f8a;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
  }
  button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  main {
    max-width: 1080px;
    margin: 2rem auto;
    padding: 0 1.5rem;
  }
</style>
