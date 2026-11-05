# Tutorial v1 – Ablauf und Gestaltung, noch kein Spielcode

Dieses Paket enthält einen Vorschlag für einen geführten Einstieg über **drei erfolgreiche Kämpfe** und **fünf Lernabschnitte**. Die vorhandenen Spielregeln, Preise, Freischaltungen und Belohnungswerte bleiben maßgeblich. Die sechs neuen Bildschirmbilder sind Gestaltungsvorlagen, keine neuen echten Spiel-Screenshots und keine lauffähige Tutorial-Implementierung.

## Inhalt

- `TUTORIAL_ABLAUF.md`: vollständige Schritttabelle, Geschenk-Vorschläge und Empfehlungen zu Pflicht, Pausen, Niederlagen, Neustarts und erfahrenen Spielern.
- `TUTORIAL_ABLAUF.json`: dieselben 28 Einzelschritte mit den angefragten Feldern `id`, `auslöser`, `bildschirm`, `ziel_element`, `text`, `pflicht`, `erledigt_wenn`, `geschenk`. Ergänzt um Abschnitt, Vorbedingungen und Ausweichverhalten. Zielkennungen sind **semantische Planungsnamen, keine geprüften Nodepfade**.
- Sechs `tutorial_*.png`: je 852 × 1846 Pixel. In Godot Texte, Eingabesperre, Lichtfenster und Knöpfe separat aufbauen; nicht den kompletten Screenshot als Bedienoberfläche verwenden.
- `pip_winken.png`, `pip_zeigen.png`, `pip_freuen.png`: drei separate RGBA-Posen, je 512 × 512.
- `zeigerhand.png`: RGBA, 256 × 256.
- `hinweisblase_rahmen.png`: RGBA, 512 × 256, textfreier Rahmen mit dunkler Innenfläche und transparentem Außenrand.
- `referenzen/`: sieben vorhandene Bildschirm-/Grafikreferenzen samt Herkunftshinweisen. Der Sieg ist aus vorhandenen UI-Exportbausteinen rekonstruiert; keine neu erfundenen Belohnungsmengen.
- `BILDANWEISUNG.txt` und `BILDANWEISUNGEN_VOLLSTAENDIG.json`: kurze Zusammenfassung und tatsächliche Bildanweisungen einschließlich Freistellungskorrekturen.
- `DATEIPRUEFUNG.json`: Auflösungen, Alpha, Vollständigkeit und Übereinstimmung von Markdown-/JSON-Texten.

## Der Kern der Führung

1. Spielen – erster Einsatz.
2. Kampf – Held, Plasma, erster Kernschuss, erste Wellenkarte.
3. Helden – den frei gewählten Starter einmal aufleveln.
4. Upgrades – ein wirklich verfügbares Werft-Modul einmal ausbauen; Munition nur kurz freiwillig zeigen.
5. Basis – ein zulässiges Gebäude bauen oder ausbauen. Lagerhinweis erst bei abholbarem Inhalt, sonst ohne Wartezwang später nachholen.

„Schritt N von 5“ bezeichnet diese fünf Abschnitte, nicht alle 28 Tabellenzeilen. Die Zeilen enthalten auch Navigation und spätere freiwillige Hinweise. So entsteht kein 28-teiliges Startfenster. Im ersten Kampf erscheinen höchstens vier kurze Hinweise; nur Kern, Heldenwahl und Kartenwahl lenken die Eingabe. Luftangriff und Medipack werden später und nur bei sinnvoller vorhandener Nutzung erklärt.

**Pflicht im geführten Modus:** Außerhalb des Zielbereichs sind normale Spielaktionen gesperrt. Pause/Einstellungen und „Ohne Hilfe spielen“ bleiben erreichbar. Freiwillige Hinweise sperren nichts. Kein Tutorial-Schritt verlangt Werbung, einen Shop-Kauf, Echtgeld, eine Premium-Freischaltung oder Multiplayer.

Pip ist der bereits vorhandene Roboter-Held in der Rolle eines Stationshelfers. Sein Auftreten im Tutorial bedeutet **keine Freischaltung als Kampfheld**. Keine neue Stations-KI, kein neuer spielbarer Charakter nötig.

## Größen und Positionierung

Alle folgenden Maße sind **logische Punkte auf 390 × 844**. Der PNG-Maßstab ist ungefähr 2,185 Pixel pro Punkt; die exakte Hochauflösung bleibt 852 × 1846. Die endgültige Position immer am wirklichen Control-Rechteck bestimmen, nicht an festen Pixeln eines KI-Bildes.

- Sichere Seitenabstände: mindestens 16 Punkte zu Displayrändern und Aussparungen.
- Hinweisblase normalerweise 342–358 Punkte breit, etwa 104–132 hoch. Kurzer Inhalt: 14–15 Punkte Nunito, Zeilenhöhe 19–21, höchstens zwei Textzeilen. Überschrift optional 18–20 Punkte Fredoka fett.
- Fortschritt: 11–12 Punkte Nunito fett, zum Beispiel „Schritt 2 von 5“. Keine große zusätzliche Fortschrittsleiste über der Kopfzeile.
- Innenabstand: 14–16; Abstand zwischen Fortschritt und Hinweistext: 6; zum Link: 8. Pip seitlich oder oberhalb, niemals über Buchstaben.
- Pip ungefähr 68–84 Punkte hoch; Hand 40–52. Die eigentliche Berührungsfläche des Zielknopfs bleibt mindestens 44 × 44 und wird nicht durch die Figur verkleinert.
- Link „Ohne Hilfe spielen“ mindestens 11–12 Punkte mit gut erreichbarer Trefferfläche. Für Tastatur-/Controller-Fokus und zugängliche Navigation ebenfalls erreichbar lassen.
- Das Zielrechteck rundum um 6–10 Punkte erweitern. 10–14 Punkte Rundung bei rechteckigen Knöpfen; beim Energiekern eine runde Aussparung. Ein dünner Goldring von 1,5–2 Punkten reicht.
- Eine Blase zuerst oberhalb des Ziels platzieren; sonst darunter oder seitlich. Mindestens 12 Punkte Abstand zur aktiven Zielkontur. Bei wenig Platz Pip verkleinern oder weglassen, niemals das Ziel überdecken oder den Text auf unlesbare Größe drücken.
- Auf Level- oder Modulauswahl keine Zeigerhand über alle Karten legen: entweder gemeinsame Auswahlfläche hervorheben oder einen gleichwertigen Beispielbereich markieren. Die freie Auswahl bleibt erhalten.

### Zielbereiche der sechs Entwürfe

Die Werte sind Näherungen zur Gestaltung, **keine fertigen Eingabekoordinaten**:

| Entwurf | Abschnitt / Ziel | Blase ungefähr | Ziel ungefähr |
|---|---|---|---|
| tutorial_01_spielen.png | 1 / Spielen | x 18, y 518, w 354, h 116 | großer Spielen-Knopf über der Navigation, etwa x 68, y 652, w 254, h 58 |
| tutorial_02_kampf_energiekern.png | 2 / bereiter Energiekern | x 18, y 592, w 354, h 112 | mittlerer runder Knopf unten, Mittelpunkt etwa x 195, y 810, Radius 28 |
| tutorial_03_held_aufleveln.png | 3 / Aufleveln | x 18, y 434, w 354, h 116 | grüner vorhandener Aufleveln-Knopf unten; roten X-Knopf ausschließen |
| tutorial_04_tech_werft.png | 4 / Ausbauen | x 18, y 360, w 354, h 116 | grüner Ausbauen-Knopf der echten Detailbox |
| tutorial_05_basis.png | 5 / Bauen oder Ausbauen | x 18, y 150, w 354, h 116 | vorhandener grüner Knopf eines freigeschalteten Gebäudes |
| tutorial_06_abschluss.png | 5 / Abschluss | x 18, y 268, w 354, h 248 | vorhandene Aktion zum Menü; keine erzwungene weitere Partie |

Die gezeigten Profil-/Stufen-/Preisstände stammen aus vorhandenen Entwurfsreferenzen und sind **keine Anfänger-Balancingvorgaben**. Insbesondere zeigt der Heldenentwurf Brocken exemplarisch zum vorhandenen Preis 650. Die im alten Beispiel fehlenden Karten werden zur Darstellung einer möglichen Übungsgutschrift auf den bereits vorhandenen Bedarf 20/20 ergänzt. Das ist **nur ein Geschenk-Vorschlag für das Bild**, keine neue feste Kartenmenge und kein Freischalten Brockens gegen die Wahl des Spielers. Im Spiel immer den tatsächlichen gewählten Starter, echten Kartenbedarf und echten Preis verwenden.

Die Basisübersicht mit 30 Gebäuden ist eine Grafikreferenz. Der Tutorial-Entwurf verwendet nur einen nahen Ausschnitt. Anfänger erhalten dadurch keine 30 fertigen Gebäude. Gebäude-Freischaltungen weiterhin aus dem Spiel lesen.

## Ebenen und Eingaben

Von hinten nach vorn: vorhandener Bildschirm → Abdunklung mit ausgespartem Ziel → dünner Zielrand → Hand → Pip → Hinweisblase/Text/Link. Diese Elemente als eigene Controls beziehungsweise Zeichenebenen aufbauen.

Die Abdunklung ist eine gleichmäßige Fläche, **kein gemalter Bühnen-Lichtkegel**. Das transparente Lichtfenster muss am echten Ziel-Control ausgerichtet sein. Nach Layoutänderung, Rotation oder Skalierung neu positionieren. Bei freiwilligen Tipps darf die Maske keine Spieltipps verschlucken. Bei Pflichtschritten nur die echte Zielaktion und sichere Auswege freigeben.

Das Bild einer Hand empfängt selbst keine Eingaben. Ihr ausgestreckter Finger zeigt auf das Ziel; die Hand sitzt vollständig außerhalb des wichtigen Knopfinhalts. Die PNG zeigt nach links oben; bei Bedarf als Ganzes drehen. Den tatsächlichen Fingerpunkt visuell kalibrieren, nicht die Bildmitte auf den Knopf legen. Bei einem unteren Energiekern die Hand seitlich oder rechts oberhalb platzieren, damit sie nicht unten aus dem Bild ragt.

Nach dem Zielklick erst dann fortsetzen, wenn die echte Spielaktion bestätigt ist: Kernschuss ausgelöst, Heldenstufe erhöht, Karte angewendet oder Lagerertrag gebucht. Ein bloßes Tap-Geräusch reicht nicht. Keine zweite Aktion auslösen, wenn ein Schritt nach App-Neustart bereits erledigt ist.

## Farbwerte

| Element | Farbe |
|---|---|
| Hinweisfläche | `#231747` |
| obere weiche Lichtkante | `#44306F` |
| Goldrand, Zielring, Fortschritt | `#FFD56A` |
| Hinweistext | `#FFF4D8` |
| kleiner Link / Nebenangabe | `#D9D2F0` |
| cyanfarbener Akzent | `#52E7FF` |
| Abdunklung | `#0B071C`, normalerweise 60 % Deckkraft, bei Bedarf 65 % |
| normaler vorhandener grüner Knopf | vorhandener Spielstil, ungefähr `#A0F568` → `#4BC62D` |
| Abschluss-Haken | `#78E65B` |

Schrift nicht in den PNG-Rahmen einbrennen: Fredoka und Nunito als echte Schriften im Spiel verwenden. Die Bildentwürfe bilden Typografie nur gestalterisch ab.

## Textfreier Rahmen und PNGs

Der Rahmen hat eine dunkle, gefüllte Innenfläche; nur der Außenbereich ist transparent. Als Neun-Flächen-Rahmen verwenden. Ausgangswert für Randaufteilung: 48 Pixel pro Seite; sichtbarer Inhalt mit etwa 16 logischen Punkten Innenabstand. Außenpadding der Textur beträgt mindestens 16 Pixel. Den transparenten Außenrand nicht als Textinnenabstand zählen. Ecken beim Strecken erhalten; die Mitte darf horizontal und vertikal gestreckt werden. Falls die Engine aus der PNG zusätzliche Randschatten erzeugt, keinen zweiten schweren Schatten hinzufügen.

Alle freigestellten Dateien sind RGBA mit geradem Alpha und sRGB. Keine schwarze Fläche aus einer Vorschau als Hintergrund übernehmen. Die Rohbilder wurden nur technisch zugeschnitten, auf die Zielgröße skaliert und transparent gepolstert. Keine kostenpflichtige Zusatzsoftware oder neue 3D-Produktion.

## Kleine Animationen – Vorschlag für später

- Einblenden: Hinweis und Maske über 0,18–0,22 Sekunden weich einblenden. Die Spiellogik nicht von dieser Dekoration abhängig machen.
- Hand: etwa alle 1,1 Sekunden zwischen 100 und 106 % skalieren, Bewegung maximal 3 Punkte. Pulsursprung an der Fingerspitze, damit der Finger nicht vom Ziel weg springt. Kein hektisches Wackeln.
- Zielrand: dezente Deckkraftänderung zwischen etwa 70 und 100 %, keine schnellen Blitze. Die eigentliche Aussparung bleibt stabil.
- Pip: im Normalfall stillstehendes PNG. Beim ersten Auftreten einmal klein einblenden, nicht ununterbrochen hüpfen. Posenwechsel nur beim jeweiligen Lernmoment.
- Abschluss: ein ruhiger Haken und kurzer Goldakzent etwa 0,5 Sekunden; keine lange Partikelflut über Buttons. Vorhandene Beute feiern, optionalen Bonus ohne Freigabe nicht auszahlen oder versprechen.
- Bei reduzierter Bewegung Hand, Pip und Ring statisch anzeigen. Text und Funktion bleiben vollständig erhalten.

Diese Zeiten sind **Gestaltungsvorschläge**, keine neuen Kampf-Ladezeiten oder Spielwerte.

## Unterbrechungen und Fehlerfälle

Fortschritt nach bestätigten Handlungen merken. Bei App-Neustart Spielstand und offenen Schritt gemeinsam abgleichen. Geschenke nur einmal pro Profil und Einmalschlüssel; keine erneute Auszahlung, nur weil ein Hinweis erneut erscheint. Reguläre Siegbeute wird vom bestehenden System gebucht und nie durch den Tutorial-Dialog nochmals vergeben.

Gibt es kein zulässiges Ziel, Overlay ausblenden und die Sperre aufheben. Bei Maximalstufe, gesperrtem Modul, laufendem Bauauftrag oder leerem Lager eine passende bestehende Alternative wählen beziehungsweise den Hinweis vertagen. Kein unsichtbarer Kaufknopf, keine Paywall und keine neue Sofortbau-/Sofortproduktionsfunktion als Voraussetzung.

Ein zusätzlicher Abschlussbonus und Probe-Booster sind nur **Vorschläge**. Ohne Freigabe dürfen Screenshots oder Texte keine entsprechende neue Inventarbuchung auslösen. Das Tutorial ist auch ohne Bonus und ohne Booster-Verbrauch abschließbar.

## Prüfung und Herkunft

Die Quellen des externen Designvergleichs stehen im Ablaufplan als Links auf offiziellen Supercell- und King-Support. Daraus wurden nur allgemeine Empfehlungen abgeleitet; keine fremden Spielfiguren oder Grafiken kopiert.

Neue Grafiken ausschließlich mit der eingebauten Bildgenerierung im bestehenden Konto erstellt. Keine weiteren kostenpflichtigen Dienste, keine Meshy-Credits. Nutzung im Rahmen der Kontobedingungen; keine Zusicherung rechtlicher Exklusivität von KI-Motiven. Vorhandene Spielgrafiken und UI-Exportbausteine stammen aus diesem Projekt.

**Noch kein Godot-Spieltest und keine Programmierung des Tutorials.** Nach Freigabe: auf 390 × 844 und Geräten mit Aussparung testen, korrekte Zielausrichtung und Eingabefreigabe prüfen, freie Starterwahl, Preis-Fehlbeträge, Neustart nach jeder Aktion, Niederlage, MAX-Fälle, leeres Lager und „Ohne Hilfe spielen“ durchgehen.
