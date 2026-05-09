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

### Blocker #001: uv-/venv-Korruption nach intensiven Reinstall-/Sync-Sequenzen

- **Datum:** 2026-05-10 (erstmals dokumentiert; vier Vorfälle in Schritten 1.4, 1.5, 1.6 zweimal, 1.7)
- **Fahrplan-Referenz:** kein einzelner Schritt — taucht quer über Schritt-Verifikationen auf
- **Modul:** Tooling (uv + .venv)
- **Blocker-Typ:** Nicht-deterministisch (Heilung jedes Mal verfügbar, Auslöse-Trigger unklar)
- **Beschreibung:**
  Während Verifikations-Sequenzen mit häufigen `uv sync` / `uv pip install --reinstall` /
  `uv run`-Wechseln (insbesondere zwischen Backend- und Frontend-Arbeit) verliert die `.venv`
  einzelne Komponenten installierter Pakete. Symptome bisher gesehen:
  - `python -m eb_digital` → `ModuleNotFoundError: No module named 'eb_digital'`
    (`_editable_impl_*.pth`-Pattern, Schritt 1.4 + 1.6)
  - `import pygments.plugin` schlägt fehl, obwohl `pygments` installiert (Schritt 1.6)
  - `cannot import name 'BaseMetadata' from 'annotated_types'` (Schritt 1.6)
  - `ModuleNotFoundError: No module named 'pytest'` direkt nach `uv sync` (Schritt 1.7)
  - `ModuleNotFoundError: No module named '_argon2_cffi_bindings'` — argon2-cffi
    installiert, aber Native-Bindings-Submodul fehlt (Schritt 1.7)

  Die Symptome treten **nicht** an gleicher Stelle auf, sind aber alle Manifestationen
  derselben Klasse: ein installiertes Paket ist im venv, aber dessen Resolver-Metadaten,
  Native-Bindings oder Editable-Pointer sind inkonsistent.

- **Reproduktion (best-effort, nicht 100 % deterministisch):**

```
# 1. Initialer healthy state nach `uv sync`.
# 2. Eine Mischung aus:
#    - mehreren `uv pip install --reinstall <pkg>` (gezielt einzelne Pakete)
#    - `uv run pytest` und `uv run python -m eb_digital ...` zwischendrin
#    - parallel `pnpm install` für andere Workspaces (Schritt 1.7)
#    - Anschließend nochmal `uv sync` ohne `--reinstall`
# 3. Beim nächsten Aufruf eines Pakets, das in der venv „sein sollte",
#    schlägt der Import fehl — Symptom variiert.
```

- **Versuchte Ansätze (drei plus, alle Patches statt Lösung):**
  1. `uv sync --reinstall-package eb-digital` — Heilung 1.4-Pattern, schlägt aber bei den
     anderen Symptom-Varianten oft fehl.
  2. `rm -rf .venv && uv sync` — Heilung 1.4 nuklear; in Schritt 1.6 erzeugte das **neue**
     Symptome (`pygments`/`annotated_types` korrupt) — Cache-Wieder­verwendung uv-seitig.
  3. `rm -rf .venv && uv sync --reinstall` (Cache-Bypass) — bisher zuverlässige Heilung
     für alle vier Symptome, aber kostet vollständige Re-Download und ~5 s Build-Zeit pro
     Lauf.
- **Offene Hypothesen:**
  - **uv-Cache-Inkonsistenz:** Wahrscheinlich erstellt uv unter `~/.local/share/uv/` Cache-Einträge,
    die zwischen `--reinstall`-Aufrufen partial korrumpiert werden. Verifikation würde verlangen,
    den uv-Cache nach jedem Symptom zu inspizieren.
  - **macOS-spezifischer Symlink-/Inode-Bug:** Möglicherweise Race condition zwischen
    `.venv`-Schreibern und Filesystem-Layer (apfs).
  - **Native-Wheel-Repacking:** argon2-cffi liefert Native-Bindings als Sub-Package
    (`_argon2_cffi_bindings`); `--reinstall <main>` lässt das Sub-Package nicht reinstallieren.
  - **Worktree-spezifisch:** `.venv` liegt in einem git-worktree-Pfad; macOS könnte über
    `find`-Timestamps oder Spotlight-Indexing intervenieren.
- **Workaround (akzeptiert für jetzt):**
  Bei jedem Symptom: `rm -rf .venv && uv sync --reinstall`. Kein blocker für aktive Schritte
  — Zeit ~5 s. Dokumentiert hier, damit die Häufung sichtbar bleibt.
- **Benötigt zur Auflösung:**
  - Reproduzierbare minimale Repro (aktuell flaky; lässt sich nicht zuverlässig herstellen).
  - Entweder uv-Bug-Report mit Repro oder ADR „uv durch pip+venv ersetzen" (sehr großer Eingriff
    in Schritt 1.1 Repository-Bootstrap, ADR-pflichtig nach CLAUDE.md Abschnitt 4 Punkt 7
    „Build- und Deploy-Pipeline").
- **Vorgeschlagene Entscheidungsfrage:**
  Wenn das Pattern ein fünftes Mal auftritt: Ressourcen-Investment (Repro-Zeit, möglicher
  uv-Issue, möglicher Tool-Wechsel) — oder weiter nuklear heilen und akzeptieren?

(Stand: 2026-05-07. Im Härtungs-Schritt von Modus-2-Schritt 3 wurden keine Blocker identifiziert; alle in Schublade 1 zusammengefassten Grundsatzfragen aus `project-context.md` Abschnitt 11 sind in der Klärungs-Session am 2026-05-07 abschließend entschieden, alle Schublade-2-Punkte als Spikes G–M in `fahrplan.md` Phasen 3 und 5 platziert, alle Schublade-3-Punkte als Roadmap-Meilensteine N/O/P in Phase 7. Damit gibt es keine offenen Architektur- oder Konzept-Lücken, die als Blocker gelten würden — der oben gelistete Blocker #001 ist ein **Tooling-Pattern**, kein Konzept-/Architektur-Defekt.)

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

_Bisher keine Blocker aufgelöst, weil bisher keine Blocker aufgetreten sind._

### Eintrags-Format gelöste Blocker (Vorlage)

```
### Blocker #NNN: [Titel] – GELÖST YYYY-MM-DD

- **Ursprüngliche Beschreibung:** [gekürzt oder Referenz]
- **Lösung:** [was hat funktioniert, warum]
- **ADR:** [falls die Auflösung einen ADR erzeugt hat]
- **Abgeleitete Regel:** [falls eine wiederkehrende Lektion entstanden ist]
```
