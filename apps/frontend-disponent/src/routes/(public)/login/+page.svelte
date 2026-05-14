<script lang="ts">
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import { ApiError } from "$lib/api/client";
  import { login } from "$lib/api/auth";
  import { setSession } from "$lib/stores/session";

  let username = $state("");
  let password = $state("");
  let isSubmitting = $state(false);
  let errorMessage = $state<string | null>(null);
  let rateLimitedUntil = $state<number | null>(null);
  let remainingSeconds = $state(0);

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

  // Whitelist erlaubter `next`-Ziele nach Login. Wir akzeptieren nur Pfade,
  // die zu bekannten Routen gehören — verhindert Open-Redirect-Vektoren
  // über das `next`-Query-Param (auch wenn der Layout-Guard 401-Pfade
  // ohnehin zurück nach /login schickt, ist diese Whitelist Defense-in-
  // depth gegen Phishing-Konstrukte wie /login?next=https://evil.example).
  const allowedNextPaths = ["/dashboard"] as const;
  type AllowedNext = (typeof allowedNextPaths)[number];

  function nextPath(): AllowedNext {
    const candidate = page.url.searchParams.get("next");
    if (candidate !== null && (allowedNextPaths as readonly string[]).includes(candidate)) {
      return candidate as AllowedNext;
    }
    return "/dashboard";
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (isSubmitting || rateLimitedUntil !== null) return;
    isSubmitting = true;
    errorMessage = null;
    try {
      const user = await login(username, password);
      setSession(user);
      await goto(resolve(nextPath()), { replaceState: true });
    } catch (cause) {
      if (cause instanceof ApiError) {
        if (cause.kind === "rate-limit") {
          const wait = cause.retryAfter ?? 60;
          rateLimitedUntil = Date.now() + wait * 1000;
          errorMessage = `Zu viele Fehlversuche. Bitte in ${wait} Sekunden erneut versuchen.`;
        } else if (cause.kind === "auth") {
          errorMessage = "Ungültige Anmeldedaten oder Mandant nicht aktiv.";
        } else if (cause.kind === "network") {
          errorMessage = "Server nicht erreichbar. Bitte Verbindung prüfen.";
        } else {
          errorMessage = "Anmeldung fehlgeschlagen. Bitte erneut versuchen.";
        }
      } else {
        errorMessage = "Unerwarteter Fehler. Bitte erneut versuchen.";
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Anmeldung · EB Digital Disponent</title>
</svelte:head>

<section>
  <h1>Anmeldung</h1>
  <p class="hint">EB Digital — Disponenten-Frontend.</p>

  <form onsubmit={handleSubmit} novalidate>
    <label>
      Benutzername
      <input
        type="text"
        autocomplete="username"
        bind:value={username}
        required
        minlength="1"
        maxlength="64"
        disabled={isSubmitting || rateLimitedUntil !== null}
        data-testid="login-username"
      />
    </label>

    <label>
      Passwort
      <input
        type="password"
        autocomplete="current-password"
        bind:value={password}
        required
        minlength="12"
        disabled={isSubmitting || rateLimitedUntil !== null}
        data-testid="login-password"
      />
    </label>

    {#if errorMessage}
      <p class="error" role="alert" data-testid="login-error">{errorMessage}</p>
    {/if}

    {#if rateLimitedUntil !== null && remainingSeconds > 0}
      <p class="rate-limit" data-testid="login-rate-limit">
        Wiederholung möglich in {remainingSeconds} Sekunde{remainingSeconds === 1 ? "" : "n"}.
      </p>
    {/if}

    <button
      type="submit"
      disabled={isSubmitting || rateLimitedUntil !== null}
      data-testid="login-submit"
    >
      {isSubmitting ? "Anmelden …" : "Anmelden"}
    </button>
  </form>
</section>

<style>
  section {
    max-width: 360px;
    margin: 3rem auto;
  }
  h1 {
    margin-bottom: 0.25rem;
  }
  .hint {
    color: #555;
    margin-top: 0;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-weight: 500;
  }
  input {
    padding: 0.5rem 0.6rem;
    font-size: 1rem;
    border: 1px solid #aaa;
    border-radius: 4px;
  }
  input:disabled {
    background-color: #f4f4f4;
    color: #777;
  }
  button {
    padding: 0.6rem 1rem;
    font-size: 1rem;
    font-weight: 600;
    background-color: #1a4f8a;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  button:disabled {
    background-color: #888;
    cursor: not-allowed;
  }
  .error {
    color: #a40000;
    background-color: #fbe9e9;
    border: 1px solid #e6b2b2;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    margin: 0;
  }
  .rate-limit {
    color: #555;
    font-size: 0.9rem;
    margin: 0;
  }
</style>
