# Blockers

<!-- Ungelöste Probleme und gescheiterte Ansätze.
     Wird befüllt, wenn ein Arbeitsschritt nach drei Versuchen nicht gelöst werden konnte
     (CLAUDE.md Abschnitt 10). Gelöste Einträge wandern in den Archiv-Abschnitt. -->

## Blocker-Erkennung (vor dem Dreifach-Versuch)

Ein Problem ist **sofort** als Blocker zu behandeln, ohne drei Versuche abzuwarten, wenn eines dieser Muster zutrifft:

1. **Informationslücke:** Eine für die Lösung nötige Angabe fehlt in allen Pflicht-Dokumenten.
2. **Widerspruch:** Zwei Dokumente geben unvereinbare Vorgaben und kein ADR löst den Konflikt auf.
3. **Fremde Modulgrenze:** Die Lösung würde Änderungen in einem Modul erfordern, das nicht Teil des aktuellen Fahrplan-Schritts ist.
4. **Freigabebedarf:** Die Lösung fällt in eine Kategorie aus CLAUDE.md Abschnitt 4.
5. **Nicht-deterministisches Verhalten:** Das Problem tritt nicht reproduzierbar auf. Nicht-Reproduzierbarkeit ist selbst ein Blocker, keine akzeptierte Eigenschaft.

In diesen Fällen: direkt Eintrag hier anlegen, ohne Dreifach-Versuch.

Für alle anderen Fälle gilt die Dreifach-Regel aus CLAUDE.md Abschnitt 10.

---

## Aktive Blocker

_Keine aktiven Blocker._

(Stand Aktive Blocker: 2026-06-11 — keine. Blocker #002 (TomTom-Key) am 2026-06-10 gelöst, siehe „Gelöste Blocker". **Spike L (5.4):** `MAPTILER_API_KEY`-Eingangsbedingung am 2026-06-11 erfüllt — Patrick stellte einen temporären Key bereit, Empirie durchgeführt, Key danach rotiert, `.env` zurück auf Platzhalter. Kein Blocker entstanden.)

(Stand: 2026-05-10. Im Härtungs-Schritt von Modus-2-Schritt 3 wurden keine Blocker identifiziert; alle in Schublade 1 zusammengefassten Grundsatzfragen aus `project-context.md` Abschnitt 11 sind in der Klärungs-Session am 2026-05-07 abschließend entschieden, alle Schublade-2-Punkte als Spikes G–M in `fahrplan.md` Phasen 3 und 5 platziert, alle Schublade-3-Punkte als Roadmap-Meilensteine N/O/P in Phase 7. Blocker #001 wurde am 2026-05-10 ursächlich aufgeklärt und nach „Gelöste Blocker" verschoben.)

### Eintrags-Format (Vorlage – nicht löschen)

```
### Blocker #NNN: [Titel]

- **Datum:** YYYY-MM-DD
- **Fahrplan-Referenz:** [Phase.Schritt-ID]
- **Modul:** [betroffenes Modul]
- **Blocker-Typ:** [Informationslücke | Widerspruch | Fremde Modulgrenze | Freigabebedarf | Nicht-deterministisch | Dreifach-Fehlschlag]
- **Beschreibung:**
  [Was funktioniert nicht, unter welchen Bedingungen tritt das Problem auf.
  Konkret, prüfbar. Keine Spekulation ohne Kennzeichnung.]
- **Reproduktion:**
```

[Exakte Schritte zur Reproduktion, mit Kommandos/Inputs/erwarteter vs. tatsächlicher Ausgabe]

```
- **Versuchte Ansätze (bei Dreifach-Fehlschlag):**
1. [Ansatz 1] – Ergebnis: [...] – Grund des Scheiterns: [...]
2. [Ansatz 2] – Ergebnis: [...] – Grund des Scheiterns: [...]
3. [Ansatz 3] – Ergebnis: [...] – Grund des Scheiterns: [...]
- **Offene Hypothesen:**
- [Was könnte noch versucht werden, braucht aber eine Entscheidung/Information/Freigabe]
- **Benötigt zur Auflösung:**
- [Konkrete Information, Freigabe, externe Klärung – ohne Auslassungen]
- **Vorgeschlagene Entscheidungsfrage:**
[Die spezifische Frage, die der Mensch beantworten soll, in einer Form, aus der eine Antwort direkt abgeleitet werden kann]
```

**Nummerierungs-Regel:** durchgehend, keine Lücken, auch gelöste Blocker behalten ihre Nummer. Erster Eintrag wäre `#001`.

---

## Gelöste Blocker

[Nach Auflösung hierher verschieben. Ergänzungen: "Lösungsdatum", "Lösung", "ADR-Referenz falls zutreffend".
Bei hoher Anzahl: nach `docs/archiv/blockers-YYYY-MM.md` auslagern.]

### Blocker #002: TomTom-API-Key fehlt — TomTom-Empirie von Spike G nicht durchführbar – GELÖST 2026-06-10

- **Ursprüngliche Beschreibung (gekürzt):** `.env` war byte-identisch mit `.env.example`, `TOMTOM_API_KEY`/`MAPTILER_API_KEY` Platzhalter; Orbis Routing v2 und Legacy v1 antworteten 401. TomTom-Szenarien T1/T2/T3 von Schritt 5.1 (Spike G) damit nicht durchführbar (Informationslücke, Muster 1 — Sofort-Blocker ohne Dreifach-Versuch).
- **Lösung:** Patrick stellte am selben Tag einen **temporären** TomTom-API-Key bereit (nur lokale `.env`, gitignored; nach Spike-Abschluss von Patrick gesperrt, `.env` zurück auf Platzhalter). Rückfrage geklärt: benötigt war Routing-API-Zugriff (Orbis v2), nicht Map Display. Smoke: Orbis v2 und v1 beide 200. TomTom-Empirie vollständig durchgeführt (12 Routing- + 1 Traffic-Call), Ergebnisse in [`docs/spikes/spike-g-results.md`](spikes/spike-g-results.md).
- **ADR:** folgt aus Spike G (ADR-Entwurf wartet auf Freigabe — der Blocker selbst erzeugte keinen ADR).
- **Abgeleitete Regel:** Externe-API-Spikes brauchen die Credential-Frage als **Eingangskriterium im Fahrplan-Schritt** (explizit prüfen, bevor der Schritt startet) — Folge-Hinweis für Spike L bereits unter „Aktive Blocker" als 5.4-Eingangsbedingung vermerkt (`MAPTILER_API_KEY` weiterhin Platzhalter).

### Blocker #001: uv-/venv-Korruption nach intensiven Reinstall-/Sync-Sequenzen – GELÖST 2026-05-10

- **Ursprüngliche Beschreibung (gekürzt):** Nach intensiven Sequenzen aus `uv sync` / `uv pip install --reinstall` / `uv run` (insbesondere zwischen Backend- und Frontend-Arbeit) traten in den Schritten 1.4, 1.5, 1.6 (zweimal) und 1.7 immer wieder Import-Fehler auf — primär `ModuleNotFoundError: No module named 'eb_digital'` (Editable-Pattern), sekundär verschiedene Folgesymptome (`pygments.plugin`, `annotated_types.BaseMetadata`, `_argon2_cffi_bindings`, `pytest`). Der Workaround `rm -rf .venv && uv sync --reinstall` wirkte zuverlässig, behob aber nicht die Ursache.
- **Lösung (Diagnose-Spike 2026-05-10):**
  - **Direkte Ursache:** macOS BSD-File-Flag **`UF_HIDDEN`** ist auf allen `.venv`-Dateien gesetzt (nachgewiesen mit `ls -lO`). **Python 3.13** überspringt `.pth`-Dateien mit diesem Flag in `Lib/site.py` mit der Meldung `Skipping hidden .pth file: …` (neues Sicherheits-Verhalten). Damit landet der Editable-Pfad zum `backend/eb_digital`-Source-Tree nie in `sys.path` → `eb_digital` ImportError.
  - **Trigger:** Der Worktree-Stamm `.../EB-Digital/.claude/worktrees/<name>/` und das Eltern-Verzeichnis `.claude/worktrees/` tragen das `hidden`-Flag. Beim **allerersten** `uv sync` in einem neuen Worktree übernimmt uv (oder das macOS-Filesystem beim `mkdir .venv` unter einem hidden Parent) das Flag auf die `.venv`-Inhalte. Folge-Syncs in derselben venv schreiben nicht-hidden Files.
  - **Heilung:** `chflags -R nohidden .venv` — ein-Schritt, idempotent, kein `--reinstall`, kein `rm -rf` nötig. Heilt _alle_ bekannten Symptom-Varianten gleichzeitig.
  - **Tooling-Fix:** [`scripts/fix-venv-flags.sh`](scripts/fix-venv-flags.sh) führt das `chflags`-Kommando idempotent aus; einmal pro Worktree-Lebensdauer manuell auszulösen (nach erstem `uv sync`).
  - **Cross-Check:** Hauptcheckout (`/Users/.../EB-Digital/`) hat keine Hidden-Flags — der Bug ist worktree-spezifisch unter `.claude/worktrees/`.
- **ADR:** keiner. Diagnose ist Bug-Aufklärung mit Tooling-Fix, keine Architektur-Entscheidung. Eine etwaige strategische Folge-Entscheidung „venv-Speicherort außerhalb von `.claude/worktrees/`" ist als `ENTSCHEIDUNG ERFORDERLICH` im Logbuch-Eintrag vom 2026-05-10 vorgelegt; falls sie gewählt wird, entsteht ein OPERATIV-ADR.
- **Abgeleitete Regel (methodisch):** Eine zuverlässige Workaround-Sequenz, die wiederholt nötig wird (≥ 3 Vorfälle der gleichen Klasse), ist selbst ein Indikator für eine offene Ursache. Spätestens beim dritten Vorfall ist ein Diagnose-Spike auszulösen — der Workaround maskiert den Bug, ohne ihn zu lösen.
- **Logbuch-Verweis:** Eintrag vom 2026-05-10 `[PROBLEM-GELÖST]` enthält die vollständige Verifikations-Sequenz.

### Eintrags-Format gelöste Blocker (Vorlage)

```
### Blocker #NNN: [Titel] – GELÖST YYYY-MM-DD

- **Ursprüngliche Beschreibung:** [gekürzt oder Referenz]
- **Lösung:** [was hat funktioniert, warum]
- **ADR:** [falls die Auflösung einen ADR erzeugt hat]
- **Abgeleitete Regel:** [falls eine wiederkehrende Lektion entstanden ist]
```
