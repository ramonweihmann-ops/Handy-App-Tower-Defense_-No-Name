# Fünkchen „Sternenschuppen“ – Bauanleitung für Blender

## Auftrag und Verbindlichkeit

Baue den vorhandenen Champion Fünkchen anhand von `01_turnaround.png` und `02_details_und_sternenatem.png` zu einem hochwertigen, weiterhin gut lesbaren Comic-Drachen um. Bewahre seine Identität: violetter Körper, türkisfarbener Bauch und Flughäute, zwei helle Hörner, goldenes Halsband mit Stern, vier Beine, zwei Flügel und ein langer Schwanz.

Diese Anleitung ist ein konkreter Bauvorschlag, kein bereits getestetes Modell. Die unten genannten Maße sind Startwerte für einen konsistenten Nachbau, keine aus den Bildern exakt rekonstruierten Messungen. Die Bilder sind gemalte Ansichten und können sich in Details widersprechen; niemals jede Ansicht als separate Anatomie umsetzen.

Priorität bei Widersprüchen: Silhouette der schrägen Vorderansicht → Profil der Seitenansicht → Rückenansicht für Anordnung → Detailblatt für Oberflächen. Die Spielansicht von hinten oben hat bei der Ausarbeitung genauso hohe Priorität wie das Gesicht.

## 1. Bestehendes Modell prüfen und sichern

1. Vorhandenes Fünkchen-Modell, Skelett, Materialien und Animationen in einer Arbeitskopie öffnen. Ausgangsdateien nicht überschreiben.
2. Tatsächliche Achsen, Maßstab, Fußhöhe, Knochennamen, Flügelketten und Maul-/Mündungsanbindung feststellen und dokumentieren. Keine unbekannten Namen erfinden.
3. Bestehende Animationen im unveränderten Zustand abspielen und Referenzbilder sichern. Erst danach Geometrie austauschen oder ergänzen.
4. Wenn möglich das vorhandene Skelett und die bestehenden Aktionen erhalten. Änderungen an Flügelansätzen können Anpassungen der Ruhepose und der Animationen verlangen; neue Ansätze nicht einfach an alte, unpassende Gewichte hängen.

## 2. Proportionen zuerst als einfache Formen festlegen

Für den unabhängigen Entwurfsaufbau: Blender Z nach oben, Figur blickt nach -Y, Breite entlang X. Beim Einpassen in das bestehende Spielmodell dessen Konvention übernehmen, statt es ungeprüft umzudrehen.

Als Arbeitseinheit H = Höhe vom Boden bis zum höchsten Hornpunkt wählen, beispielsweise H = 2 Blender-Einheiten. Alle Werte unten sind Anteile von H. Sie dienen als Ausgangspunkt; anhand der Bildsilhouette gemeinsam nachjustieren.

| Teil | Ausgangsgröße / Lage |
|---|---|
| Kopf ohne Hörner | Breite 0,42 H; Tiefe 0,33 H; Höhe 0,34 H; Mittelpunkt ungefähr Z 0,70 H |
| Schnauze | Breite 0,27 H; Tiefe 0,15 H; Höhe 0,13 H; in Kopf integrieren, nicht als aufgesetzte Kugel belassen |
| Rumpf | Breite 0,29 H; Länge 0,40 H; Höhe 0,29 H; Mittelpunkt ungefähr Z 0,30 H |
| Vorderfüße | Boden Z = 0; links/rechts ungefähr X = ±0,12 H; unter vorderem Rumpf |
| Hinterfüße | X ungefähr ±0,14 H; etwa 0,30 H hinter Vorderfüßen |
| Hals | Kurzer, kräftiger Übergang von Brust zu Kopf; kein dünner Halsstab |
| Schwanz | Freie Länge ab Rumpf ungefähr 0,50–0,60 H; Ansatzdurchmesser etwa 0,12 H |
| Flügel | Halb geöffnet insgesamt etwa 0,85–1,00 H Spannweite; kompakter als ein erwachsener Drache |
| Hörner | Zwei Hörner mit ungefähr 0,16 H Länge, leicht nach außen und hinten gekrümmt |

Zuerst Kopf, Rumpf, Schnauze, Hals, vier Beine, Schwanz und zwei Flügel als glatte Formen bauen. Noch keine Schuppen, Gravuren oder Sterne. Von vorn, Seite und hinten oben prüfen: großer Kopf, frecher Ausdruck, kurze tragfähige Beine und langer Schwanz müssen bereits ohne Materialien als Fünkchen lesbar sein.

## 3. Körper als zusammenhängende Figur aufbauen

- Rumpf aus einem abgerundeten Volumen; Brust etwas aufrechter, Hüfte kräftig. Hals und Kopf weich anschließen.
- Kopf und Schnauze durch kontrollierte Topologie oder einen sauberen Neuaufbau verbinden. Überlappende Kugeln dürfen im Endmodell keine sichtbaren Nähte bilden.
- Vier Beine mit klaren Gelenkbereichen modellieren; Vorderbeine nicht als menschliche Arme formen. Drei stumpfe Krallen je Fuß als konsistente Modellentscheidung verwenden; die Zeichnungen zeigen durch Perspektive teilweise uneindeutige Zehenzahlen.
- Füße breit genug für das Körpergewicht, alle vier Sohlen in der neutralen Standpose auf gleicher Höhe.
- Schwanz als verjüngte, kontinuierliche Form mit gleichmäßigen Querschnitten aufbauen. In der Ruhepose weich nach hinten führen, keine enge Schlaufe, die beim Animieren kollidiert.
- Nach Formfindung saubere Topologie mit ausreichenden Schleifen an Hals, Beinansätzen und Schwanzansatz herstellen. Ein stark unterteiltes Ausgangsmodell nicht ungeprüft als Spielmodell exportieren.

## 4. Gesicht – entscheidend für die Wiedererkennung

1. Zwei große Augäpfel teilweise in den Kopf einsetzen, mit modellierten oberen und unteren Lidkanten. Keine Augen auf der Oberfläche schweben lassen.
2. Iris mit Türkis am oberen und warmem Gold am unteren Bereich, dunkler Pupille und kleinem Glanzlicht. Iris als Textur oder flache angepasste Fläche, nicht als große Leuchtkugel.
3. Brauen als weiche, kurze Formen an den Kopf anschließen. Ein leicht angehobener Brauenbogen und ein schiefes Lächeln erzeugen Mut und Frechheit; keine aggressive Boss-Mimik.
4. Nasenlöcher als zwei flache Vertiefungen in der breiten Schnauze. Keine tiefen Löcher mit unnötiger Innentopologie.
5. Maulöffnung mit wirklicher dunkler Innenfläche und einem dicken, beweglichen Unterkiefer bauen. Ein aufgemalter schwarzer Strich reicht für die Schusspose nicht.
6. Zwei kleine obere Eckzähne und wenige untere Zähne, abgerundet und hell. Eine einfache breite Zunge im Maul, keine frei flatternde Spitze.
7. Bei geöffnetem Maul die Innenflächen von oben und seitlich kontrollieren. Kein leerer Blick durch den Kopf, kein Halsband im Kiefer und keine Zähne im Oberkiefer.

## 5. Flügel – Geometrie und Bewegungsraum

Die Flügel gehören zum Rücken hinter den Vorderbeinschultern. Im Seitenprofil zwischen Halsbasis und Rumpfmitte ansetzen; nicht an Hals oder Kopf befestigen.

- Pro Seite eine kräftige Flügelwurzel, einen gebogenen Hauptarm und zwei bis drei klare Membranfelder bauen. Die Wurzel liegt links/rechts neben dem Rückenkamm.
- Zwischen Wurzel, Hals und Schulter einen sichtbaren Freiraum vorsehen. Als Arbeitsziel mindestens etwa 0,02 H Abstand anlegen, aber die tatsächliche Kollisionsfreiheit in allen Bewegungen prüfen.
- Membran als zusammenhängende Fläche mit geringer echter Dicke modellieren. Ein dünner Volumenkörper vermeidet eine von hinten unsichtbare Fläche; bei einseitigem Material zusätzlich dessen Rückseitendarstellung prüfen.
- Rippen bilden große, runde Hauptformen. Feine Adern kommen in die Textur oder Normalenkarte, nicht als dünne separate Drähte.
- Flügel beim Schießen aufrichten und seitlich führen; die gesamte Schlagbahn muss außerhalb von Kopf, Hörnern, Hals und Rückenkamm liegen. Den Kamm gegebenenfalls im Wurzelbereich niedriger ausformen.
- Ruhepose, oberer Anschlag, unterer Anschlag und Zwischenstellungen prüfen. Nicht nur die beiden Endpositionen betrachten.

## 6. Welche Details wirklich modelliert werden

| Detail | Umsetzung | Grund |
|---|---|---|
| Kopf, Maul, Beine, Schwanz, Flügelarme | Echte Geometrie | Bestimmen Silhouette und Bewegung |
| Große Rückenplatten und seitliche Kopfplatten | Wenige echte, abgerundete Formen | Von hinten und oben wichtig |
| Bauchschilde | Etwa 6–8 große flache Segmente mit weichen Übergängen | Klar lesbar, geringe Teilzahl |
| Hörner, Krallen | Echte kompakte Geometrie | Sichtbare Kontur |
| Halsband und Sternfassung | Echte Geometrie | Wiedererkennungsmerkmal |
| Kleine Schuppenreihen | Normalenkarte und zurückhaltende Farb-/Rauheitsvariation | Hunderte Einzelobjekte vermeiden |
| Kleine Hornrillen | Normalenkarte; nur wenige große Rillen bei Bedarf modellieren | Kontur bleibt ruhig |
| Flügelnebel, feine Adern, Sternpunkte | Texturen | Keine schwebenden Objekte nötig |
| Licht im Stern, in Kehle und Schwanzspitze | Emissionsmaske auf fester Oberfläche | Kontrollierbar und günstig |

### Schuppen praktisch herstellen

Eine einzige abgerundete, tropfenförmige Schuppe als Detailvorlage modellieren. Auf einem separaten Detailmodell versetzte Reihen an Wangen, Hinterkopf, Flanken und Beinen anordnen; Größen nach Körperbereich variieren und die Reihen der Körperrichtung folgen lassen. Dieses Detailmodell wird nur zum Backen verwendet und nicht mit exportiert.

Auf dem Spielmodell UV-Flächen ohne starke Streckung anlegen. Die Details des hoch aufgelösten Modells auf eine Tangenten-Normalenkarte backen; Projektionsabstand und Hülle so einstellen, dass keine benachbarten Körperteile in die Textur geraten. Normalenkarte als Nicht-Farbdaten behandeln und über einen Normalen-Knoten auswerten; die tatsächliche Orientierung nach GLB-Import prüfen.

Die Farbkarte bekommt nur leichte Helligkeitsunterschiede zwischen Schuppen, keine schwarzen Umrandungen jeder Schuppe. Auf Stirn und Schnauze größere ruhige Flächen lassen. Bei kleiner Darstellung müssen die Schuppen weich zusammenlaufen statt zu flimmern.

## 7. Rücken, Kamm und Schwanz

Etwa 7–10 größere niedrige Platten vom Hinterkopf über den Rücken bis zum Schwanz verteilen; die Anzahl an die finale Körperlänge anpassen. Am Hinterkopf zusätzlich wenige breite seitliche Platten wie in der Vorlage, keine Vielzahl langer Spitzen.

Platten überlappen leicht und sitzen an der Haut. Für die Verformung jede Platte überwiegend dem nächstgelegenen Körper- oder Schwanzsegment zuordnen; an Übergängen nur gezielt weich gewichten. Keine harte Platte über mehrere stark gegeneinander drehende Gelenke spannen.

Die türkise Schwanzspitze ist eine kleine fest angewachsene rautenförmige Endschuppe mit weichen Kanten. Sie ist nicht transparent und benötigt weder Partikel noch einen großen Leuchthof. Der Schwanz bleibt bis zur Spitze eine klar durchgehende Form.

## 8. Halsband und Sternenkern

- Breiter goldener Reif mit Innenabstand zum Hals und abgerundeten Kanten. Keine freihängende Kette.
- Stern als kompakter fünfzackiger Körper, weich abgestumpfte Spitzen, goldene Fassung und innen wenige geschliffene türkis-goldene Facetten. Keine komplexe Edelstein-Innengeometrie.
- Sternfassung fest mittig vor der Kehle beziehungsweise oberen Brust anbringen. Beim Öffnen des Mauls muss sie unterhalb des Unterkiefers bleiben.
- Gravur des Reifs nur als schwache Normalen-/Farbstruktur, nicht als viele winzige Metallteile.
- Der Sternenkern sitzt im Bereich der unteren Kehle hinter einer festen hellen Schuppe. Er kann beim Schuss heller werden; kein sichtbares Loch durch den Körper.

## 9. Materialien und Texturen

Startpalette, anschließend anhand der Referenzen unter neutralem Licht abstimmen:

| Material | Farbstart | Oberfläche |
|---|---|---|
| Haut | Violett #8042C8, helle Flächen #AE6DEB | Nichtmetallisch, Rauheit etwa 0,35–0,50 |
| Bauch | Türkis #8ADDD3, Schatten #4CA9AC | Nichtmetallisch, Rauheit etwa 0,40 |
| Flügelmembran | Türkis #50D2DC mit Violett #7357C8 | Nichtmetallisch, kein Glas |
| Hörner/Krallen | Elfenbein #FFF0C5 bis warmes Beige #C99A57 | Rauheit etwa 0,35–0,45 |
| Halsband | Warmgold #E5AD32 | Metallisch, Rauheit etwa 0,25–0,35 |
| Stern/Schwanzspitze | Helles Türkis #7FEDE5 mit Goldakzent | Undurchsichtig, sparsame Emission |

Keine Studioreflexe aus dem Bild fest in die Farbtextur malen. Formschatten kommen aus Geometrie und Beleuchtung; geringe gebackene Kontaktverschattung ist erlaubt, darf aber die beweglichen Gelenke nicht verschmutzen.

Kosmische Sternpunkte sparsam und größer anlegen, vor allem auf Flügelmembranen und wenigen Schuppen. Kein vollflächiges Rauschen. Der helle Kern bleibt sichtbar, auch wenn Bloom ausgeschaltet ist. Emissionsstärken sind abhängig von Belichtung und Spieleinstellungen und müssen im Spiel abgestimmt werden.

Blender-spezifische prozedurale Materialien vor dem GLB-Export auf unterstützte Texturen backen. Materialvorschau allein beweist nicht, dass das Ergebnis nach dem Export gleich aussieht.

## 10. Detail- und Leistungsbudget

Zunächst ein Arbeitsziel von etwa 12.000–18.000 Dreiecken für das sichtbare Spielmodell ansetzen; kein bestehendes strengeres Projektlimit überschreiten. Die genaue Obergrenze mit den vorhandenen Champion-Modellen abgleichen.

Verteilung als Orientierung: Körper/Beine/Schwanz etwa 35 %, Kopf/Maul/Augen etwa 30 %, Flügel etwa 20 %, Kamm/Hörner/Schmuck etwa 15 %. Nur dort mehr Geometrie einsetzen, wo sich die Silhouette oder eine Gelenkverformung sichtbar verbessert.

Eine gemeinsame Texturbelegung bevorzugen. Bei Bedarf in 2K arbeiten und eine 1K-Spielversion vergleichen; endgültige Auflösung nach Projektvorgaben wählen. Möglichst wenige Materialien verwenden und nicht jeder Schuppe ein eigenes Material geben. Anzahl der Dreiecke und Texturgrößen nach angewandten Modifikatoren beziehungsweise am exportierten Modell prüfen.

## 11. Skelett und Schussbewegung

Bestehende Bewegungsstruktur verwenden. Vorhandene Gewichte können als Ausgangspunkt übertragen werden, müssen an vier Beinen, Hals, Kiefer, Flügelwurzeln und Schwanz aber manuell geprüft werden.

- Vier Beine bleiben vier getrennte tragende Gliedmaßen. Keine zusätzlichen Arme.
- Sternmedaillon und Halsband überwiegend an den passenden Hals-/Brustbereich binden, ohne starkes Gummiverhalten.
- Beim Schuss kurzer Impuls aus Brust und Hals, Maul öffnen, Flügel kontrolliert aufstellen. Füße bleiben belastet; kein Sprung, sofern die bestehende Aktion keinen vorsieht.
- Atemursprung innen zwischen den geöffneten Kiefern platzieren und vorhandene Mündungsanbindung korrekt übernehmen. Der Strahl darf weder aus dem Halsband noch aus dem Nasenrücken kommen.
- Der gemalte Sternenatem auf Bild 2 ist eine Effektillustration, keine mit dem Körper zu exportierende feste Geometrie. Den bestehenden freigegebenen Spieleffekt separat anbinden; diese Modellüberarbeitung ersetzt dessen Ablauf nicht ungefragt.

## 12. Kontrollpunkte und Freigabeschritte

### A – Formprüfung vor Details

Vier Ansichten und Spielkamera von hinten oben als neutral graues Modell rendern. Erst weiterarbeiten, wenn Kopfgröße, vier Beine, Flügelansätze, Bauch und Schwanz zur Vorlage passen. Fehlende Ähnlichkeit nicht durch mehr Glanz oder Schuppen kaschieren.

### B – Materialprüfung

Farbige Ansichten unter weichem Studiolicht und anschließend unter der tatsächlichen Spielbeleuchtung erstellen. Violett, Türkis und Gold müssen klar getrennt bleiben. Einen Vergleich bei 60 und 120 Pixel Figurenhöhe ansehen; für die endgültige Beurteilung zusätzlich die tatsächliche Spielgröße verwenden.

### C – Bewegungsprüfung

Eine vollständige Schleife der vorhandenen Stand-, Lauf- und Schussbewegungen prüfen, soweit diese vorhanden sind. Flügel, Kopf, Kamm, Halsband, Kiefer und Schwanz auf Durchdringungen kontrollieren. Problemstellen mit Standbild dokumentieren und korrigieren, nicht nur günstige Kamerawinkel zeigen.

### D – Exportprüfung

Exportiertes GLB in einer frischen Szene und anschließend in Godot laden. Materialien, Normalen, Texturen, Animationen, Maßstab, Fußhöhe und Atemursprung überprüfen. Eine funktionierende Blender-Szene ist noch kein geprüfter Spieleinbau.

## 13. Empfohlene Übergabe

- Bearbeitbare `.blend` mit eingebundenen oder sauber beigefügten Texturen.
- Spielmodell `.glb` mit den vereinbarten vorhandenen Aktionen.
- Vorschauen vorn, schräg vorn, Seite, hinten und hinten oben.
- Kurze Schussvorschau, in der die freie Flügelbewegung sichtbar ist.
- Kurzer Bericht: Dreiecke, Texturauflösungen, Materialzahl, übernommenes/geändertes Skelett, vorhandene Aktionen und verbleibende Abweichungen.

## Priorität bei knapper Zeit

Zuerst Silhouette, Gesicht, Flügelansätze und Rückansicht sauber bauen. Danach große Bauch-/Rückenplatten und Sternschmuck ergänzen. Kleine Schuppen, Adern und Gravuren zuletzt als Texturdetails hinzufügen; diese dürfen vereinfacht werden, ohne Fünkchens Charakter oder Beweglichkeit zu opfern.
