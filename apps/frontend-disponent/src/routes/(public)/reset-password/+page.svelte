<script lang="ts">
  import { page } from "$app/state";
  import { resolve } from "$app/paths";
  import { ApiError } from "$lib/api/client";
  import { resetPassword } from "$lib/api/auth";

  const MIN_PASSWORD_LENGTH = 12;

  let newPassword = $state("");
  let passwordConfirm = $state("");
  let isSubmitting = $state(false);
  let errorMessage = $state<string | null>(null);
  let successMessage = $state<string | null>(null);
  let rateLimitedUntil = $state<number | null>(null);
  let remainingSeconds = $state(0);

  const token = $derived(page.url.searchParams.get("token") ?? "");
  const tokenMissing = $derived(token.trim().length === 0);

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

  function validateClientSide(): string | null {
    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      return `Passwort muss mindestens ${MIN_PASSWORD_LENGTH} Zeichen enthalten.`;
    }
    if (newPassword !== passwordConfirm) {
      return "Passwort und Bestätigung stimmen nicht überein.";
    }
    return null;
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (isSubmitting || tokenMissing || rateLimitedUntil !== null) return;
    errorMessage = null;
    successMessage = null;
    const clientError = validateClientSide();
    if (clientError !== null) {
      errorMessage = clientError;
      return;
    }
    isSubmitting = true;
    try {
      await resetPassword(token, newPassword);
      successMessage = "Passwort gesetzt. Sie können sich jetzt anmelden.";
      newPassword = "";
      passwordConfirm = "";
    } catch (cause) {
      if (cause instanceof ApiError) {
        if (cause.kind === "gone") {
          errorMessage =
            "Der Token ist ungültig, abgelaufen oder bereits verwendet. " +
            "Bitte den Plattform-Administrator oder einen Disponenten um einen neuen Token bitten.";
        } else if (cause.kind === "validation") {
          errorMessage = `Passwort muss mindestens ${MIN_PASSWORD_LENGTH} Zeichen enthalten.`;
        } else if (cause.kind === "rate-limit") {
          const wait = cause.retryAfter ?? 60;
          rateLimitedUntil = Date.now() + wait * 1000;
          errorMessage = `Zu viele Versuche. Bitte in ${wait} Sekunden erneut versuchen.`;
        } else if (cause.kind === "network") {
          errorMessage = "Server nicht erreichbar. Bitte Verbindung prüfen.";
        } else {
          errorMessage = "Passwort-Reset fehlgeschlagen. Bitte erneut versuchen.";
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
  <title>Passwort setzen · EB Digital Disponent</title>
</svelte:head>

<section>
  <h1>Passwort setzen</h1>

  {#if tokenMissing}
    <p class="error" role="alert" data-testid="reset-token-missing">
      Es fehlt der Reset-Token in der URL. Bitte den vollständigen Einladungs-Link verwenden.
    </p>
  {:else if successMessage}
    <p class="success" role="status" data-testid="reset-success">{successMessage}</p>
    <p><a href={resolve("/login")}>Zur Anmeldung</a></p>
  {:else}
    <form onsubmit={handleSubmit} novalidate>
      <label>
        Neues Passwort
        <input
          type="password"
          autocomplete="new-password"
          bind:value={newPassword}
          required
          minlength={MIN_PASSWORD_LENGTH}
          disabled={isSubmitting || rateLimitedUntil !== null}
          data-testid="reset-password-new"
        />
      </label>

      <label>
        Passwort bestätigen
        <input
          type="password"
          autocomplete="new-password"
          bind:value={passwordConfirm}
          required
          minlength={MIN_PASSWORD_LENGTH}
          disabled={isSubmitting || rateLimitedUntil !== null}
          data-testid="reset-password-confirm"
        />
      </label>

      <p class="hint">
        Mindestens {MIN_PASSWORD_LENGTH} Zeichen. Länge schlägt Komplexität — bitte eine Passphrase verwenden.
      </p>

      {#if errorMessage}
        <p class="error" role="alert" data-testid="reset-error">{errorMessage}</p>
      {/if}

      {#if rateLimitedUntil !== null && remainingSeconds > 0}
        <p class="rate-limit" data-testid="reset-rate-limit">
          Wiederholung möglich in {remainingSeconds} Sekunde{remainingSeconds === 1 ? "" : "n"}.
        </p>
      {/if}

      <button
        type="submit"
        disabled={isSubmitting || rateLimitedUntil !== null}
        data-testid="reset-submit"
      >
        {isSubmitting ? "Setzen …" : "Passwort setzen"}
      </button>
    </form>
  {/if}
</section>

<style>
  section {
    max-width: 420px;
    margin: 3rem auto;
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
  .success {
    color: #0a5a2a;
    background-color: #e3f3e8;
    border: 1px solid #a5d4b4;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    margin: 0 0 0.5rem 0;
  }
  .rate-limit {
    color: #555;
    font-size: 0.9rem;
    margin: 0;
  }
  .hint {
    color: #555;
    font-size: 0.9rem;
    margin: 0;
  }
</style>
