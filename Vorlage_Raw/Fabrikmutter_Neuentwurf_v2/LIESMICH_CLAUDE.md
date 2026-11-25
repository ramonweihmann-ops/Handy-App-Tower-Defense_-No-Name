# Fabrikmutter – vereinfachte Comicfassung

Der Nutzer hat den runderen, weniger kleinteiligen Turnaround freigegeben und die Anpassung des zweiten Bildes sowie die Bereitstellung beider Bilder beauftragt. `01_turnaround.png` ist die verbindliche Form- und Stilvorlage. `02_maul_und_federbot.png` wurde daran angepasst und zeigt Mauldetails und die Ausgabe eines Federbots. Die ältere realistischere Fassung nicht als Detailmaßstab verwenden.

## Nachbau in Blender

- Breiter kompakter Ofenkörper auf zwei kurzen Ketten, keine Beine und keine unabhängig bewegten Greifarme. Zwei kurze dicke Schornsteine, körpernahe Rohre und Kolben. Alles bleibt fest am Körper.
- Große abgerundete Stahlplatten und wenige größere Nieten. Dunkler blaugrauer Stahl, warmes Industriegelb mit schwarzen Warnstreifen, rot-orange Augen und Ofenschlund. Weiche metallische Glanzlichter; keine flächigen Rost-, Kratzer- oder Schweißnahttexturen. Ruß dezent an den Schornsteinen. Details über große lesbare Formen statt Kleinteile vermitteln.
- Gesicht deutlich absetzen: zwei rote Augen unter schweren Brauen, einzelne Stahlzähne, Kieferplatten, Gitter und seitliche Kolben, dahinter ein vertiefter glühender Ofenraum. Kein flacher orangefarbener Aufkleber. Alle Bauteile räumlich sauber verbinden; Gitter und Zähne nicht miteinander verschmelzen.
- Unter dem Maul eine SEPARATE dunkle Bot-Ausgabebucht mit kurzer fest verbundener Rampe. Der Federbot kommt dort heraus, nicht durch das Ofengitter. Die Rampe braucht keine neue Klappanimation.
- Bestehenden Federbot weiterverwenden: silberner Kugelkopf, ein rotes Auge mit Querstrebe, Stahlfeder und gelb-schwarzer runder Fuß. Der Bot im zweiten Bild ist eine Szenenreferenz und darf nicht in das Boss-Mesh eingebacken werden. Öffnung breit und hoch genug für das vorhandene Bot-Modell planen; beim Absetzen Bodenkontakt und Kollisionsfreiheit prüfen. Spawn-Zeitpunkt und Spielwerte erhalten.
- Bestehendes Skelett, Ruhepose, Achsen, Skalierung und Aktionen zuerst im Projekt prüfen. Körper bewegt sich insgesamt: langsames Gleiten/Rollen, leichtes Schwanken und Einfedern. Starre Metallteile nicht stark wie Gummi stauchen; kleine Bewegung über vorhandene Körpersteuerung und verdeckte Übergänge verteilen. Keine zusätzlichen unabhängigen Armbewegungen voraussetzen.
- Beide Referenzen sind generierte Konzeptbilder, keine exakt vermessenen orthografischen Pläne. Bei Abweichungen der Kettenrollen, Zähne oder Nieten zwischen Ansichten ist Bild 1 maßgeblich; eine konsistente Konstruktion festlegen, nicht unterschiedliche Varianten mischen.

## Abnahme

Vorn, Seite und hinten sowie das Absetzen aus der Spielkamera schräg oben vorn prüfen. Die Augen, das Ofenmaul und die separate Ausgabe müssen bei Handygröße unterscheidbar bleiben. Keine schwebenden Teile oder durchdringenden Bots; Ketten und Rampe am Boden. Vorhandenes Geometrie-/Texturbudget beachten, kein neues Budget festgelegt.

Diese Lieferung enthält zwei PNG-Vorlagen, kein fertiges Modell und keinen getesteten Rig. Der tatsächliche Skelettanschluss und der Ablauf müssen in Blender und im Spiel geprüft werden. Ausschließlich eingebaute Bildgenerierung verwendet; keine zusätzlichen kostenpflichtigen Dienste. Spielname bleibt Fabrikmutter, Konzeptname Ofenbrutstätte.
