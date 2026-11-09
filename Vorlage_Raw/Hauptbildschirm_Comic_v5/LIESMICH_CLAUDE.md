# Hauptbildschirm v5 – korrigierter Planetenring

`hauptbildschirm_aktuell_v5.png`: 852 × 1846 Pixel, PNG/RGB. Der hintere obere Ringbogen verschwindet nun hinter der Planetenkugel. Der vordere untere Bogen verläuft vor der Kugel. Farben, Lage und Stil orientieren sich am gelieferten aktuellen Bildschirm.

Die eingebaute Bildgenerierung hat nur den Planeten-Ausschnitt neu gezeichnet. Für die Lieferung wurde ausschließlich der örtlich begrenzte Planeten- und Ringbereich eingesetzt. Die UI-Silhouetten und die Schrift wurden separat aus den Originalpixeln geschützt. Kopfleiste, Boss, Pfad, Angebote links, Spielen-Knopf, Reiterleiste und alle Pixel außerhalb der örtlichen Bearbeitungsmaske sind pixelgleich zum gelieferten Original. Die Knöpfe rechts und ihre Schrift bleiben durch die Schutzmaske original. Innerhalb des Planeten-/Ringbereichs wurden auch Wolkenbänder und Ringglanz neu gezeichnet; dort ist das Bild absichtlich nicht pixelgleich.

Die Differenzprüfung bestätigt: außerhalb der Bearbeitungsmaske null geänderte Pixel; innerhalb der UI-Schutzmaske null geänderte Pixel. Kein gesamtes Neurendern des Bildschirms. Der Vergleich `vergleich_ring.png` zeigt vorher und nachher nebeneinander. Die Prüf- und Maskendateien liegen zusätzlich im Ordner für die Nachvollziehbarkeit.

Nur Bilddateien, keine Spielcodeänderungen. Keine weiteren kostenpflichtigen Dienste verwendet.
