# Neue Gegner für Level 51–150 – aktuelle Übergabe

Stand 09.11.2026. Alle zehn neuen Planeten sind mit jeweils vier Gegner-Entwürfen zusammengestellt, insgesamt 40. Die Dschungelgruppe ist unverändert aus der ersten Runde übernommen; die weiteren neun Gruppen verwenden die weniger knuffige Formensprache. Für Planet 15 ist ausschließlich die neue, vom Nutzer freigegebene Effektfassung maßgeblich.

## Einstieg für Claude

- `alle_gegner.png`: alle 40 Entwürfe, Planeten 06–15.
- `alle_36_monster_aktuell.png`: die neun zuletzt bearbeiteten Gruppen, Planeten 07–15.
- `pruefseite_01.png` bis `pruefseite_04.png`: größere Ansichten.
- `planet_06_uebersicht.png` bis `planet_15_uebersicht.png`: je eine Gruppe, stets leicht, mittel, stark, Boss von links nach rechts.
- `schwarzes_loch_effekte_freigegeben.png`: unverändertes freigegebenes Bild der letzten Welt.
- `MONSTER_KATALOG.json`: eindeutige IDs, Namen, Planeten und Stärken. Diese IDs sind Übergabebezeichner; vorhandene IDs im Spiel nicht ohne Zuordnung ersetzen.

## Produktionsstand – bitte beachten

Diese Lieferung stellt die Entwürfe bereit. Sie enthält für die Planeten 07–15 noch keine einzelnen freigestellten 1024-Pixel-Produktionsvorlagen, keine neuen GLB-Modelle, keine Skelette und keine Bewegungen. Bestehende funktionierende Modelle und Animationen im Spiel beibehalten. Die vier vorhandenen Dschungel-Einzelvorlagen liegen weiterhin eine Ordnerebene höher unter `06_leicht.png`, `06_mittel.png`, `06_stark.png`, `06_boss.png`.

Gruppenblätter nicht direkt in Meshy hochladen und nicht als Laufanimationen oder kampffertige Modelle behandeln. Vor einer 3D-Produktion pro Gegner eine separate Vorlage mit transparentem Hintergrund, 1024 × 1024 Pixeln und etwa zehn Prozent Rand erstellen: eine Figur, keine Beschriftung, keine Bodenplatte, keine Effekte; humanoide Figuren in offener A-Pose. Es wurden keine Meshy-Credits ausgegeben oder neue 3D-Kosten freigegeben.

Die Anatomie ist auf den Konzeptblättern noch nicht für 3D freigegeben: Bei einigen Krabblern sind nur vier der vorgesehenen sechs Beine sichtbar. Insbesondere Ozean-Krabbenpanzer (sechs Laufbeine plus zwei Scheren), Schraubenkrabbler, Pilzpanzer und Sternenpanzer benötigen eindeutig getrennte Beine in der Einzelvorlage. Hände, Flügelansätze und Fangarme bei der Modellproduktion erneut prüfen. Die Übersicht darf nicht als automatische Anatomieprüfung gelten.

## Letzte Welt – Effekte getrennt vom Körper

Schattenkugel: schmale Aura und leuchtende Panzerfugen. Leerenflügler: cyanfarbene Flügelkanten und kurze Energieabströmung. Sternenpanzer: strahlender Sternenkern und kurze elektrische Verbindungen. Schlundwächter: Brust-Gravitationskern mit Akkretionsring, Halo hinter dem Oberkörper sowie Energie um Unterarme und Fäuste. Die Intensität steigt von leicht bis Boss.

Für Godot sind dies Gestaltungsvorschläge für separate Effekt-Ebenen beziehungsweise Materialien, noch keine fertigen Effekt-Dateien. Panzerfugen gegebenenfalls als Emission am Material, Auren und Bögen als getrennte Effektobjekte, den Brustkernring als separates Teil am Brustanker umsetzen. Funken und Bruchstücke nicht mit dem Körper verschmelzen oder als Knochen auffassen. Effekte bei kleiner Kampfgröße auf Lesbarkeit und Handy-Leistung abstimmen. Keine neuen Angriffe, Werte oder Spielregeln aus dem Bild ableiten.

Die anderen Planeten, frühere Fassungen und bestehender Spielcode wurden für diese Übergabe nicht ersetzt. Ausschließlich eingebaute Bildgenerierung verwendet; Zusammenstellung und Beschriftung aus vorhandenen Bildern. Prompts und Dateiprüfsummen liegen bei.
