# Vision – EB Digital

<!-- Eingangs-Dokument eines Projekts. Wird VOR der Erstellung der anderen Dokumente
     ausgefüllt und bleibt danach als historisches Artefakt im Repo erhalten.
     Zweck: rohe Idee strukturiert erfassen, bevor sie in Konzept und Architektur überführt wird.
     Diese Datei wird nach Initialisierung der anderen Dokumente NICHT mehr verändert –
     spätere Erkenntnisse landen in project-context.md, decisions.md, fahrplan.md.
     Die Vision bleibt als Referenz: „so haben wir es ursprünglich gewollt". -->

## 1. Kernidee

EB Digital ist eine zentrale Multi-Tenant-Plattform für die Echtzeit-Koordination ehrenamtlicher Einsatzbetreuung bei polizeilichen Großlagen. Sie verbindet Disponenten, Betreuungsfahrzeuge und Einsatzkräfte über rollenspezifische Interfaces und ersetzt die heute übliche WhatsApp-Improvisation durch ein strukturiertes, serviceorientiertes Auftragssystem mit Logistik- und Navigationsfunktion.

## 2. Problem und Anlass

- **Welches Problem löst das System?** Fehlende Echtzeit-Koordination zwischen Disponenten, Betreuungsfahrzeugen und Einsatzkräften bei Großlagen.
- **Wer hat dieses Problem auf der Anbieterseite?** Die ehrenamtlichen Strukturen polizeilicher Berufsverbände, die Einsatzbetreuung organisieren – zunächst die DPolG (Initial-Mandant), perspektivisch die GdP und weitere Berufsverbände nach erprobter Praxis.
- **Wer profitiert auf der Bezieherseite?** Einsatzkräfte aus allen polizeilichen Berufsverbänden – nicht zwingend nur Mitglieder des operativ versorgenden Verbands. Cross-Berufsverbands-Versorgung (z. B. DPolG-Betreuung versorgt GdP-Einsatzkräfte und umgekehrt) ist gelebte solidarische Praxis und Teil des Selbstverständnisses des Systems.
- **Wie wird es heute gelöst?** Über WhatsApp-Gruppen: Bedarfsmeldungen werden manuell eingegeben, Fahrzeuge fahren Örtlichkeiten ab, ohne gesicherte Auftragslage oder Echtzeit-Überblick.
- **Warum reicht das nicht?** Kein Lagebild, keine automatische Fahrzeugzuweisung, keine Statusrückmeldung, kein Bestandsüberblick, keine strukturierte Navigation – die gesamte Koordinationslast liegt beim Menschen.

## 3. Zielbild

EB Digital arbeitet mit vier Rollen und zwei Fahrzeugtypen. Die Account-Hierarchie ist top-down: Administrator → Disponent → Betreuer; die Einsatzkraft tritt anonym hinzu.

**Administrator** (technische Rolle, außerhalb des Einsatzbetriebs) installiert die Software auf dem Server, stellt die Betriebsbereitschaft her, pflegt den zentralen Basis-Artikelkatalog, schaltet neu registrierte Mandanten frei und legt Disponent-Accounts an. Im laufenden Einsatzbetrieb tritt der Administrator nicht in Erscheinung.

**Disponent** öffnet die Weboberfläche auf PC oder Tablet und eröffnet einen Betreuungseinsatz mit Startzeit, Endzeit und einem oder mehreren groben Einsatzräumen auf der Karte. Er pflegt die Accounts der Einsatzbetreuungs-Fahrzeuge und Betreuer in seinem Mandanten und erweitert den zentralen Artikelkatalog um mandantenspezifische Artikel. Eingehende Bestellungen erscheinen automatisch als Aufträge. Das System schlägt das passendste Fahrzeug vor – nach Nähe, Route und Beladung – und der Disponent bestätigt oder lässt automatisch zuweisen. Stornierung und Umverteilung von Aufträgen sind ausschließlich seine Hoheit. Bei Bedarf aktiviert er für den jeweiligen Einsatz einen Zugangscode als zusätzliche Sicherungsmaßnahme für die Einsatzkraft-URL. Er beendet den Einsatz. Mehrere Disponenten können einen Einsatz kollaborativ führen; ein Disponent kann mehrere Einsätze parallel bearbeiten.

**Betreuer** startet seine Schicht von der Geschäftsstelle. Sein Fahrzeug ist digital beladen (manuelle Eingabe; automatische Verbrauchsbuchung pro Mandant aktivierbar). Neue Aufträge erhält er automatisch mit Turn-by-Turn-Navigation auf Straßenwegen. Er sieht auf der Karte seine eigene Position, andere Fahrzeuge, die Geschäftsstelle und – falls aktiv – den Versorgungs-Transporter. Auftragsabschluss erfolgt per Knopfdruck. Über einen Hilfe-Knopf kann der Betreuer den Disponenten in Eigennot oder bei Pannen schnell erreichen. Ein interner Chat zwischen Disponent und Betreuer steht für operative Koordination zur Verfügung.

**Einsatzkraft** öffnet eine einsatzspezifische URL auf dem eigenen Gerät. Hat der Disponent einen Zugangscode aktiviert, gibt sie diesen vor dem Bestellvorgang ein – sonst entfällt dieser Schritt. Sie sieht den Artikelkatalog des bedienenden Mandanten (zentraler Basis-Katalog plus dessen mandantenspezifische Erweiterungen), gibt ihren Standort frei oder beschreibt ihn als Text, und gibt ihre Bestellung anonym auf. Sie sieht ausschließlich die eigene Bestellung – keine Aggregate, keine anonymen Listen anderer Bestellungen. Sie verfolgt den Auftragsstatus – eingegangen, übernommen, in Ausführung, erledigt – und sieht, wenn das zugewiesene Fahrzeug sich auf unter 150 Meter nähert. Eine Mitgliedschafts- oder Verbandsprüfung findet nicht statt – die Bezieherseite ist mandantenneutral. Eine Hilfe-Funktion ist auf Einsatzkraft-Seite bewusst nicht vorgesehen; Hilfsersuchen jenseits Verpflegung laufen über den polizeilichen Dienstweg.

**Reguläres Betreuungsfahrzeug** fährt Einzelaufträge im Einsatzraum.

**Versorgungs-Transporter** ist eine zweite Fahrzeugrolle in Transportergröße mit drei Betriebszuständen, die der Disponent bei Einsatzeröffnung festlegt:

1. **Außer Betrieb** – nicht aktiv im Einsatz.
2. **Mobile Nachschubstelle** – andere EB-Fahrzeuge füllen hier ihre Bestände auf; kann auch stationär als zweite Versorgungsstelle neben der Geschäftsstelle stehen.
3. **Großbestellungs-Modus** – bedient gebündelte Bestellungen an grob gleicher Örtlichkeit.

Im aktiven Betrieb ist der Versorgungs-Transporter für alle Betreuungsfahrzeuge und den Disponenten auf der Karte sichtbar.

**Beispielszenarien:**

- Eine Einsatzkraft an einer Absperrung öffnet die Einsatz-URL, wählt zwei Wasser und einen Kaffee, teilt ihren GPS-Standort. Der Auftrag erscheint beim Disponenten, wird automatisch dem nächsten Fahrzeug mit passender Beladung zugewiesen. Die Einsatzkraft sieht: „Auftrag übernommen, unterwegs."
- Ein Betreuer fährt ohne aktiven Auftrag durch das Einsatzgebiet. Ein neuer Auftrag geht ein – das System erkennt, dass dieses Fahrzeug am nächsten ist und die gewünschten Artikel geladen hat. Der Betreuer wird automatisch dorthin navigiert und bestätigt nach Übergabe per Knopfdruck.
- Der Disponent stellt fest, dass eine Straße offiziell gesperrt ist, EB-Fahrzeuge dort aber durchgelassen werden. Er schaltet die Strecke im System frei. Die Navigation nutzt sie fortan.
- Ein Versorgungs-Transporter steht stationär an einem Knotenpunkt im Großbestellungs-Modus; benachbarte Betreuungsfahrzeuge sehen ihn auf der Karte und können ihre Bestände dort auffüllen, statt an die Geschäftsstelle zurückzufahren.
- Eine GdP-Einsatzkraft nutzt während einer Großlage in Bremen die URL der DPolG-Einsatzbetreuung – ohne Identitätsprüfung. Die Versorgung erfolgt verbandsübergreifend.
- Bei einer besonders sensiblen Lage aktiviert der Disponent die Zugangscode-Funktion. Der Code wird über bestehende Kommunikationskanäle an die berechtigten Einsatzkräfte verteilt. Bestellungen ohne gültigen Code werden vom System abgewiesen.
- Während einer mehrwöchigen Großlage fällt der Server kurz aus. Da EB Digital fortlaufend Backups des Einsatzzustands führt, knüpft das System nach Neustart nahtlos an, ohne Datenverlust.
- Ein Betreuer bekommt mitten im Einsatz eine Reifenpanne und drückt den Hilfe-Knopf in der PWA. Der Disponent sieht die Eigennot-Meldung und koordiniert Ersatz oder Pannenhilfe.

## 4. Erfolgskriterien

- Die beteiligten Akteure – Disponenten, Betreuer, Einsatzkräfte – bewerten EB Digital als spürbare Erleichterung gegenüber der WhatsApp-Lösung.
- Alle Rollen können das System ohne Schulung oder mit minimaler Einweisung bedienen.
- Erste lauffähige Version steht 3–6 Monate nach Implementierungsstart bereit und wird im Testbetrieb des DPolG-Mandanten erprobt.
- Bei mindestens einer realen Großlage wird EB Digital tatsächlich verwendet, nicht nur theoretisch ausgerollt.

## 5. Bewusste Abgrenzung

- **Kein Behörden-IT-Anschluss.** EB Digital ist eine gewerkschaftliche Eigenentwicklung für ehrenamtliche Betreuer. Eine Vernetzung mit polizeilicher oder behördlicher IT ist ausgeschlossen.
- **Keine polizeiliche Einsatzplanung.** Das System bildet kein operatives Lagebild im behördlichen Sinne ab.
- **Keine Einsatzversorgung.** EB Digital unterstützt Einsatzbetreuung – eine optionale, gewerkschaftliche Serviceleistung – nicht die behördlich organisierte Einsatzversorgung. Diese Trennung ist begrifflich und funktional strikt.
- **Keine Klarnamen-Verwaltung von Personen.** Personen werden nicht disponiert, Fahrzeuge werden disponiert. Einsatzkräfte erhalten anonyme Temporär-Sessions; Fahrzeuge tragen sachliche Bezeichnungen ohne Personenbezug.
- **Keine Mitgliedschaftsprüfung der Einsatzkraft.** Wer auf eine Einsatz-URL zugreift, kann bestellen – unabhängig vom Berufsverband. Verbandszugehörigkeit ist kein Auswahlkriterium.
- **Keine Hilfe-Funktion für Einsatzkräfte.** Hilfsersuchen jenseits Verpflegung laufen über den polizeilichen Dienstweg. EB Digital ist kein Notruf-Kanal für Polizeibedienstete.
- **Keine Sichtbarkeit fremder Bestellungen.** Eine Einsatzkraft sieht ausschließlich ihre eigene Bestellung – keine Statistiken, keine anonymen Listen anderer Anfragen.
- **Keine Chat-Funktion mit Einsatzkräften.** Der interne Chat steht nur Disponent und Betreuer offen.
- **Keine native App in Phase 1.** Ausschließlich PWA – keine iOS- oder Android-App-Entwicklung.
- **Keine Mehrsprachigkeit in Phase 1.** Erstrollout ausschließlich auf Deutsch; Architektur muss i18n-Erweiterung erlauben.
- **Keine Selbstdisposition durch Einsatzkräfte.** Stornierung und Umverteilung sind nicht im Funktionsumfang der Einsatzkraft-PWA.
- **Keine vorgegebene Bedarfs-Domäne.** EB Digital macht keine Vorgabe, ob nur Verpflegung oder auch andere Service-Bedarfe (Akkutausch, Sanitärbedarf etc.) bestellbar sind. Der Mandant entscheidet das über seinen Artikelkatalog.

## 6. Harte Randbedingungen

- **Hosting:** Europäischer Server, kein US-Cloud-Anbieter.
- **Multi-Tenancy:** Eine zentrale Plattform-Instanz, mandantenfähig von Anfang an. Initial-Mandant: DPolG (Landesverband). Spätere Erweiterung um GdP-Landesverbände und weitere Berufsverbände vorgesehen. **Mandanten-Trennung gilt ausschließlich für die Anbieterseite** (Administrator-Aktivitäten je Mandant, Disponent, Betreuer, Fahrzeuge, Bestände, Statistiken, mandantenspezifischer Artikelkatalog). Die Bezieherseite (Einsatzkraft) nutzt das System mandantenneutral.
- **Mandanten-Onboarding:** Self-Service-Registrierung kombiniert mit schriftlichem Antrag oder Vertrag (Datenverarbeitungs-Vereinbarung, Nutzungsbedingungen, Haftungsklarheit). Administrator schaltet einen registrierten Mandanten erst nach Vorliegen der schriftlichen Grundlagen frei.
- **Parallele Einsätze:** Pro Mandant sind mehrere parallele Einsätze möglich. Pro Einsatz mindestens ein Disponent, mehrere Disponenten kollaborativ möglich. Ein Disponent kann mehrere Einsätze parallel bearbeiten.
- **Einsatzdauer:** Stunden bis Wochen – das System trägt sowohl kurze Schicht-Einsätze als auch mehrwöchige Großlagen.
- **Resilience:** EB Digital legt fortlaufend Backups des aktuellen Einsatzzustands an, sodass nach Anwendungs- oder Server-Neustart eine nahtlose Fortsetzung ohne Datenverlust möglich ist.
- **Datenschutz:** Privacy by Design – keine Klarnamen im System, anonymisierte Sessions für Einsatzkräfte, Fahrzeugbezeichnungen ohne Personenbezug. Aggregierte Einsatzstatistiken (Anzahl Bestellungen, Fahraufträge, Disponierungsmaßnahmen) bleiben dauerhaft erhalten. Individuelle Bestell- und Standortdaten werden 30 Tage nach Einsatzende automatisch gelöscht.
- **Datenexport:** Mandanten haben jederzeit Zugriff auf eine Export-Funktion ihrer eigenen Daten (Pflicht-Funktion). Damit ist Datenmigration und Plattform-Verlassen technisch in der Hand des Mandanten.
- **Lizenz von EB Digital:** AGPLv3.
- **Technologie-Stack:** Open-Source-Stack bevorzugt; vorhandene Frameworks nutzen statt Eigenentwicklung.
- **Kartendienst:** MapTiler für Kartenmaterial, TomTom für Verkehrsdaten.
- **Routing:** Ausschließlich Straßenwege – Luftlinie ist verboten. Disponent kann gesperrte Straßen für EB-Fahrzeuge manuell freischalten (de-facto-Sonderrechte der Berufsverbands-Fahrzeuge an Absperrungen, eigenverantwortlich genutzt).
- **Offline-Pufferung:** Betreuerseitige App muss Datenverlust bei Funklöchern abfedern; Kartenmaterial muss lokal zwischengespeichert werden.
- **Artikelkatalog-Hierarchie:** Zentraler Basis-Katalog gepflegt durch Administrator, mandantenspezifische Erweiterungen gepflegt durch Disponent. Die Einsatzkraft sieht den Katalog des bedienenden Mandanten.
- **Authentifizierung und Account-Hierarchie:**
  - **Administrator** wird bei Plattform-Initialisierung angelegt; er installiert die Software, betreibt den Server, schaltet Mandanten frei, legt Disponent-Accounts an und übergibt deren Zugangsdaten.
  - **Disponent** und **Betreuer** melden sich per Benutzername und Passwort an. Disponenten-Accounts werden vom Administrator angelegt; Betreuer- und Fahrzeug-Accounts vom Disponenten innerhalb seines Mandanten.
  - **Einsatzkräfte** erhalten anonyme Sessions per einsatzspezifischer URL – ohne Login oder Identitätsprüfung.
  - **Optionale Zugangscode-Funktion:** Pro Einsatz kann der Disponent einen Zugangscode aktivieren (Default: aus). Bei aktiver Funktion müssen Einsatzkräfte vor der Bestellung den Code eingeben. Verteilung des Codes erfolgt außerhalb des Systems über bestehende Kommunikationskanäle der Einsatzkräfte.
- **Spam- und Missbrauchsschutz auf Bezieherseite:** Einsatzspezifische URL (pro Einsatz neu, alte URLs verfallen) als Grundabsicherung; geografische Plausibilitätsprüfung mit Disponenten-Moderation; optional kombinierbar mit der Zugangscode-Funktion.
- **Kommunikationsfunktionen:**
  - Interner Chat zwischen Disponent und Betreuer für operative Koordination.
  - Hilfe-Knopf in der Betreuer-PWA für Eigennot oder Pannen, einseitig zum Disponenten.
  - Keine Kommunikationsfunktionen für Einsatzkräfte.
- **Sprache:** Erstrollout Deutsch; Architektur muss i18n-Erweiterung erlauben.
- **Plattform Mobile:** PWA, keine native App.
- **Budget für externe Dienste:** Bis ~50 €/Monat für aktive Einsatztage – aggressives Tile-Caching und sparsame Routing-Aufrufe sind technisch zwingend.
- **Zeitrahmen:** Erste lauffähige Version in 3–6 Monaten ab Implementierungsstart.

## 7. Weiche Präferenzen

- Wenige, gut integrierte Tools vor vielen Speziallösungen.
- Stabilität vor Aktualität bei Bibliothekswahl.
- Einfache Bedienbarkeit ohne Schulungsaufwand für alle drei operativen Rollen.
- Warenwirtschaft als optionales Modul auf Mandanten-Ebene (Default an, abschaltbar).
- Sicherheits-Features (Zugangscode) als opt-in, nicht als Default – um die niedrigschwellige Bestellbarkeit für Einsatzkräfte als Normalfall zu erhalten.
- Niedrige technische Hürde beim Mandanten-Onboarding bei gleichzeitiger schriftlicher Verbindlichkeit der rechtlichen Rahmenbedingungen.

## 8. Inspirationen und Vorbilder

- **Lieferando / Uber Eats / Glovo:** Referenzrahmen für das Dispatch-Modell – zentrale Auftragsverwaltung, mobile Ausführer, Echtzeit-Statusverfolgung für Besteller. Nicht 1:1 übertragbar, weil bei EB Digital:
  - keine festen Abholpunkte existieren – das Fahrzeug ist gleichzeitig Lager und Auslieferer,
  - Zielorte dynamisch sind und teils ohne feste Adresse beschrieben werden müssen,
  - das Routing behördliche Sperren ignorieren können muss,
  - kein Geld zwischen Anbieter- und Bezieherseite fließt – der Service ist solidarisch ehrenamtlich, die Einsatzkraft als Empfänger ist Angehöriger eines polizeilichen Berufsverbands, nicht zwingend desjenigen, der gerade die Versorgung anbietet.

## 9. Bekannte Risiken und offene Punkte

- **UI-Detailfragen:** Welche Rolle sieht was genau in welcher Ansicht – noch nicht im Detail durchdacht, aber kein strukturelles Risiko. Gehört nicht in die Vision; wird in einer späteren UX-Phase behandelt.
- **Kartenmaterial-Caching:** Konkrete Technik für Offline-Kartenpufferung auf Betreuer-Geräten muss in der Konzeptphase geklärt werden.
- **Fahrzeugbezeichnungs-Schema:** Konvention für Fahrzeugnamen muss vor dem ersten Rollout festgelegt werden.
- **Straßensperr-Override-Technik:** Wie gesperrte Straßen im Routing-System technisch freigeschaltet werden, ist offen.
- **Bündelungs-Trigger:** Bei welchem Schwellenwert oder durch wen (System / Disponent / Versorgungs-Transporter-Crew) eine Bündelung als Großbestellung deklariert wird, ist Konzeptphasen-Detail.
- **Lead-Disponent bei Multi-Disponent-Einsätzen:** Bei mehreren Disponenten an einem Einsatz – sind alle gleichberechtigt oder gibt es einen Lead, der „Einsatz beenden" und „Code aktivieren/deaktivieren" exklusiv darf? Konzeptphasen-Detail.
- **Administrator-Architektur bei Multi-Tenancy:** Ein zentraler Plattform-Administrator für alle Mandanten, oder pro Mandant ein eigener Administrator? Bei Skalierung über DPolG hinaus relevant. In der Anfangsphase trägt ein zentraler Administrator (vermutlich Patrick als Plattform-Betreiber) alle Mandanten.
- **Geografische Plausibilitätsprüfung:** Konkreter Algorithmus zur Erkennung verdächtiger Bestellungen (Distanz zum Einsatzraum, Schwellenwerte) ist offen.
- **Zugangscode-Erzeugung und -Verteilung:** Wie generiert das System den Code (Länge, Zeichenraum, Einmal- oder Wiederverwendung), und wie wird die Verteilung durch den Disponenten unterstützt (Anzeige im Disponenten-UI, Export, QR-Code)? Konzeptphasen-Detail.
- **Resilience-Granularität:** Wie engmaschig die Backups des Einsatzzustands sind (jede Bestellung, jede Statusänderung, periodisch alle X Sekunden) und wie der Wiedereinstieg konkret abläuft, ist Konzeptphasen-Detail. Vision-Anforderung: nahtlose Fortsetzung ohne Datenverlust.
- **Hilfe-Knopf-Semantik:** Konkrete Ausgestaltung der Betreuer-Hilfe-Funktion (Pflichtfeld Beschreibung, automatische Priorisierung, Eskalations-Routing) ist Konzeptphasen-Detail.
- **API-Budget-Disziplin:** Technische Maßnahmen, mit ~50 €/Monat externe Dienste auch bei mehreren parallelen Einsätzen auszukommen, müssen früh in der Architektur verankert werden.
- **Konkrete Großlage als Test-Termin:** Ein realer Anker-Termin im 3–6-Monats-Fenster ist hilfreich, aber noch nicht festgelegt.
- **Betreiber der zentralen Plattform:** Wer betreibt die zentrale Multi-Tenant-Instanz operativ – Patrick persönlich, eine zukünftige neutrale Trägerstruktur, oder ein gewerkschaftlicher Verein? Diese Frage berührt Governance und Haftung und sollte vor Produktivbetrieb geklärt sein.
- **Parallele Mandanten an derselben Großlage:** Wenn mehrere Berufsverbände gleichzeitig in derselben Stadt Einsatzbetreuung anbieten (z. B. DPolG und GdP parallel in Bremen), bekommt die Einsatzkraft potenziell mehrere URLs. Ob das System dafür eine Steuerung vorsieht (z. B. einen Verbund-Modus) oder die Verteilung außerhalb des Systems durch Absprache der Mandanten geregelt wird, ist offen.

## 10. Was diese Vision nicht ersetzt

Dieses Dokument ist Eingang in die Konzeptphase, nicht ihr Ergebnis. Es ersetzt **nicht**:

- die Architekturentscheidung (kommt in `architecture.md`)
- die Stack-Entscheidung (kommt in `project-context.md` und `decisions.md`)
- die Roadmap (kommt in `fahrplan.md`)
- die Constraints in operationalisierter Form (kommt in `project-context.md`)

---

**Überführungs-Status:**

- [x] Vision von Mensch ausgefüllt
- [ ] Konzeptphase abgeschlossen
- [ ] Härtungsphase abgeschlossen
- [ ] Vorlagen-Set initialisiert
- [ ] ADR-001 angelegt: Anpassung des Vorlagen-Sets
- [ ] Datum der Initialisierungs-Abschluss: –

**Nach abgeschlossener Initialisierung:** Diese Datei wird nicht mehr verändert.
Spätere Vision-Erweiterungen oder Pivots werden in einem ADR dokumentiert,
nicht in dieser Datei. Bei substantieller Vision-Änderung: neuer ADR mit Verweis hier.
