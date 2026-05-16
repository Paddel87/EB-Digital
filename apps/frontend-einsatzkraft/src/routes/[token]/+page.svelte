<script lang="ts">
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { ApiError } from "$lib/api/client";
  import { createSession } from "$lib/api/anonymous";
  import { isValid, normalize, ACCESS_CODE_LENGTH } from "$lib/access-code";
  import { setSession } from "$lib/stores/session";
  import type { PageData } from "./$types";

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();

  let codeInput = $state("");
  let isSubmitting = $state(false);
  let errorMessage = $state<string | null>(null);
  let markedInvalidAtRuntime = $state(false);
  let rateLimitedUntil = $state<number | null>(null);
  let remainingSeconds = $state(0);

  const codeValue = $derived(normalize(codeInput));
  const codeIsValid = $derived(isValid(codeValue));
  const accessCodeRequired = $derived(data.info?.access_code_active ?? false);
  const invalidUrl = $derived(data.info === null || markedInvalidAtRuntime);

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

  function handleCodeInput(event: Event): void {
    const target = event.currentTarget as HTMLInputElement;
    const normalized = normalize(target.value);
    if (normalized !== target.value) {
      target.value = normalized;
    }
    codeInput = normalized;
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (isSubmitting || invalidUrl || rateLimitedUntil !== null) return;
    if (accessCodeRequired && !codeIsValid) return;

    isSubmitting = true;
    errorMessage = null;
    const codeForRequest = accessCodeRequired ? codeValue : null;

    try {
      const response = await createSession(data.token, codeForRequest);
      setSession({
        token: data.token,
        sessionId: response.session_id,
        areaLabel: data.info?.area_label ?? "",
        accessCodeActive: accessCodeRequired,
      });
      await goto(resolve(`/${data.token}/dashboard`), { replaceState: true });
    } catch (cause) {
      if (cause instanceof ApiError) {
        if (cause.kind === "auth") {
          errorMessage = "Zugangscode ungültig. Bitte erneut versuchen.";
        } else if (cause.kind === "gone") {
          markedInvalidAtRuntime = true;
          errorMessage = null;
        } else if (cause.kind === "validation") {
          errorMessage =
            "Format des Codes ungültig. Bitte Seite neu laden und Code erneut eingeben.";
        } else if (cause.kind === "rate-limit") {
          const wait = cause.retryAfter ?? 60;
          rateLimitedUntil = Date.now() + wait * 1000;
          errorMessage = `Zu viele Fehlversuche. Bitte in ${wait} Sekunden erneut versuchen.`;
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
  <title>Einsatz-Anmeldung · EB Digital</title>
</svelte:head>

<section>
  {#if invalidUrl}
    <h1>Einsatz-URL ungültig</h1>
    <p class="error" role="alert" data-testid="token-invalid">
      Diese Einsatz-URL ist nicht (mehr) gültig. Bitte beim Disponenten eine aktuelle URL anfordern.
    </p>
    <p>
      <a href={resolve("/")}>Zurück zur Startseite</a>
    </p>
  {:else if data.info !== null}
    <h1>Einsatz-Anmeldung</h1>
    <p class="area" data-testid="area-label">{data.info.area_label}</p>

    <form onsubmit={handleSubmit} novalidate>
      {#if accessCodeRequired}
        <label>
          Zugangscode
          <input
            type="text"
            inputmode="text"
            autocomplete="off"
            autocapitalize="characters"
            spellcheck="false"
            maxlength={ACCESS_CODE_LENGTH}
            value={codeInput}
            oninput={handleCodeInput}
            disabled={isSubmitting || rateLimitedUntil !== null}
            data-testid="access-code-input"
            required
          />
        </label>

        {#if codeInput.length > 0 && !codeIsValid}
          <p class="hint" data-testid="code-hint">
            {ACCESS_CODE_LENGTH} Zeichen aus 0–9 und A–Z (ohne I, L, O, U).
          </p>
        {/if}
      {:else}
        <p class="hint" data-testid="no-code-hint">
          Für diesen Einsatz ist kein Zugangscode notwendig.
        </p>
      {/if}

      {#if errorMessage}
        <p class="error" role="alert" data-testid="submit-error">{errorMessage}</p>
      {/if}

      {#if rateLimitedUntil !== null && remainingSeconds > 0}
        <p class="rate-limit" data-testid="rate-limit-hint">
          Wiederholung möglich in {remainingSeconds} Sekunde{remainingSeconds === 1 ? "" : "n"}.
        </p>
      {/if}

      <button
        type="submit"
        disabled={isSubmitting || rateLimitedUntil !== null || (accessCodeRequired && !codeIsValid)}
        data-testid="submit-button"
      >
        {isSubmitting ? "Anmelden …" : "Anmelden"}
      </button>
    </form>
  {:else}
    <h1>Einsatz-Anmeldung</h1>
    <p data-testid="loading">Lade Einsatz-Information …</p>
  {/if}
</section>

<style>
  section {
    max-width: 420px;
    margin: 3rem auto;
  }
  h1 {
    margin-bottom: 0.25rem;
  }
  .area {
    color: #1a4f8a;
    font-weight: 600;
    font-size: 1.1rem;
    margin: 0 0 1rem 0;
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
    padding: 0.6rem 0.75rem;
    font-size: 1.5rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    border: 1px solid #aaa;
    border-radius: 4px;
    font-family: monospace;
  }
  input:disabled {
    background-color: #f4f4f4;
    color: #777;
  }
  button {
    padding: 0.75rem 1rem;
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
  .hint {
    color: #555;
    font-size: 0.9rem;
    margin: 0;
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
