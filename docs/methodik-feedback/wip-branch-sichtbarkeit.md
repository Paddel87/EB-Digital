# Methodik-Lücke: Ungemergte WIP-Branches sind für die Folge-Session unsichtbar

> **Befund aus EB-Digital, 2026-06-06 (Schritt 4.3a).** Eigenständiges Feedback-Dokument, unabhängig von [`issue-onboarding-luecke.md`](issue-onboarding-luecke.md).
>
> Eine Folge-Session plante und implementierte einen Schritt komplett neu, der bereits auf einem ungemergten Feature-Branch (offener Draft-PR) in Arbeit war — weil die `[IN ARBEIT]`-Spuren ausschließlich auf jenem Branch lagen und in `main` nicht sichtbar waren. Ergebnis: ~1 doppelte Implementierung plus eine doppelte Detail-Plan-Freigabe, aufgelöst erst beim `git push`.

---

## 1. Was passierte (Reproduktion)

1. **Session A (2026-05-28):** Schritt 4.3 begonnen, in 4.3a + 4.3b aufgeteilt, Detail-Plan freigegeben, ADR-020 angelegt, `backend/operations` + `backend/geo`-Plausibilität implementiert (~4.000 Zeilen). Branch `feat/4.3-backend-operations` mit allen Commits **lokal**, dann gepusht als **Draft-PR**. Status laut Branch-Logbuch: „4.3a IN ARBEIT, Verifikation offen". **Nicht nach `main` gemergt.**
2. **Session B (2026-06-06):** Pflichtlektüre nach CLAUDE.md §2 gegen `main`. `main`s `fahrplan.md`/`logbuch.md` kannten Schritt 4.3 nur als unbegonnenen Stub — die `[IN ARBEIT]`-Spuren aus Session A lebten ausschließlich auf dem ungemergten Branch. Folge: 4.3 wurde **neu** geplant (anderer Split 4.3a/b/c), neu freigegeben und neu implementiert.
3. **Aufdeckung:** Erst beim `git push` (Branch-Namens-Kollision, „tip is behind") wurde der Remote-WIP + Draft-PR sichtbar. STOPP → menschliche Entscheidung → Verwerfen der Neu-Implementierung, Fortsetzen des WIP.

## 2. Warum die bestehende Methodik das nicht abfing

- **CLAUDE.md §2 (Pflichtlektüre)** liest `fahrplan.md`, `logbuch.md`, `architecture.md` etc. — implizit **aus dem aktuellen Branch/`main`**. In-flight-Arbeit auf einem anderen, ungemergten Branch ist dort definitionsgemäß nicht enthalten.
- **CLAUDE.md §12 (Sessionende-Disziplin)** verlangt Fahrplan-/Logbuch-Pflege — aber diese Updates landen auf demselben Feature-Branch und werden erst mit dem Merge in `main` sichtbar. Endet eine Session **vor** dem Merge (hier: „Verifikation offen"), bleibt der Stand für jede Session unsichtbar, die von `main` ausgeht.
- **Der Sessionstart-Git-Sync-Check** (Projekt-Praxis seit dem Stale-Base-Vorfall) prüft nur `git fetch` + `git log HEAD..origin/main` — also Divergenz **gegen `main`**, nicht die Existenz **anderer** offener Branches/PRs.

Kernproblem: Es gibt keine Pflicht, vor dem **Planen eines Schritts** zu prüfen, ob genau dieser Schritt bereits woanders in Arbeit ist.

## 3. Vorgeschlagener Patch (CLAUDE.md §2)

**Eingriffs-Stelle:** CLAUDE.md Abschnitt 2, direkt nach der Mindest-Lektüre und vor dem `[SESSIONSTART]`-Eintrag (bzw. als Teil des projektüblichen Git-Sync-Checks).

**Nachher (Ergänzung):**

```markdown
### WIP-Branch-Sichtbarkeits-Check (Pflicht, vor Schritt-Planung)

Vor dem Planen oder Aufnehmen eines Fahrplan-Schritts prüft Claude, ob
dieser Schritt bereits an anderer Stelle in Arbeit ist:

1. `git fetch --prune` und `git branch -r` — gibt es einen Remote-Branch,
   dessen Name oder Commit-Historie auf den geplanten Schritt zeigt
   (z. B. `feat/<schritt>`)?
2. Offene Pull Requests prüfen (z. B. `gh pr list --state open`) — ist der
   Schritt bereits Gegenstand eines (auch *Draft*-) PR?
3. Bei einem Treffer: **STOPP** (Abschnitt 8, Kategorie „Widerspruch /
   unerwarteter Zustand"). Den gefundenen WIP-Stand dem Menschen vorlegen,
   bevor neu geplant oder implementiert wird. Niemals einen Schritt parallel
   neu beginnen, der bereits auf einem ungemergten Branch existiert.

Dieser Check ersetzt nicht den Stale-Base-Check gegen `main`, sondern
ergänzt ihn um die Sicht auf *parallele, noch nicht gemergte* Arbeit.
```

**Begründung:** Verschiebt die Konflikt-Erkennung vom `git push` (zu spät — Plan + Implementierung sind schon passiert) an den Sessionanfang (rechtzeitig — vor jedem Aufwand). Kosten: ein zusätzlicher `gh pr list` + `git branch -r` pro Sessionstart, < 30 Sekunden.

## 4. Optionaler Begleit-Patch (CLAUDE.md §12)

Damit ein WIP-Stand auch ohne aktiven Check auffindbar ist, kann das Sessionende eine **Sichtbarkeits-Spur in `main`** verlangen, wenn eine Session mit ungemergter, mehrtägig liegenbleibender Arbeit endet:

**Eingriffs-Stelle:** CLAUDE.md §12, neuer Punkt.

```markdown
- Endet die Session mit substantieller, noch **nicht gemergter** Arbeit auf
  einem Feature-Branch (z. B. „Implementation fertig, Verifikation offen"),
  wird in `main`s `fahrplan.md` „Aktueller Stand" ein Einzeiler ergänzt:
  „Schritt X.Y IN ARBEIT auf Branch `feat/...` (PR #N) — nicht in `main`".
  Dieser Pointer wird per kleinem Doku-Commit direkt auf `main` gesetzt
  (Ausnahme von der „keine Commits auf Hauptbranch"-Regel, weil rein
  dokumentarisch und kollisionsfrei).
```

**Abwägung:** §4-Variante (Pflicht-Check beim Sessionstart) ist robuster, weil sie nicht von der Disziplin der vorigen Session abhängt. Der §12-Pointer ist ergänzend nützlich, kollidiert aber mit der „keine Commits auf `main`"-Regel und ist daher nur die zweite Wahl. **Empfehlung: §2-Check umsetzen, §12-Pointer optional.**

## 5. Auswirkung auf laufende Projekte

- **§2-Check:** < 30 s Mehraufwand pro Sessionstart; verhindert im Ernstfall eine komplette Doppel-Implementierung (hier: mehrere Stunden Arbeit, die nur durch die zufällige Branch-Namens-Kollision beim Push auffielen).
- Keine Änderung an Code, CI oder Dokument-Struktur. Reine Prozess-Ergänzung im Sessionstart-Ablauf.
