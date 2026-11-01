class_name MockFonts
## Schriften der Mockups: Fredoka (Überschriften, Zahlen) und Nunito (Fließtext), beide SIL Open
## Font License (fonts/OFL-*.txt). Liefert die passende Datei zum Gewicht, auf Wunsch mit
## Buchstabenabstand.

const HAVE := {"fredoka": [500, 600, 700], "nunito": [600, 700, 800]}

static var _files := {}
static var _vars := {}


static func font(family: String, weight: int, spacing := 0) -> Font:
	var fam := "fredoka" if family.to_lower().begins_with("fredoka") else "nunito"
	var best: int = HAVE[fam][0]
	for w in HAVE[fam]:
		if absi(int(w) - weight) < absi(best - weight):
			best = w
	var key := "%s-%d" % [fam, best]
	if not _files.has(key):
		var f: FontFile = load("res://fonts/%s.woff2" % key)
		_files[key] = f
	if spacing == 0:
		return _files[key]
	var vk := "%s/%d" % [key, spacing]
	if not _vars.has(vk):
		var fv := FontVariation.new()
		fv.base_font = _files[key]
		fv.spacing_glyph = spacing
		_vars[vk] = fv
	return _vars[vk]


## CSS-Farbe „rgb(…)“ / „rgba(…)“ lesen
static func color(css: String) -> Color:
	var re := RegEx.create_from_string("rgba?\\(([^)]*)\\)")
	var m := re.search(css)
	if m == null:
		return Color.WHITE
	var p := m.get_string(1).split(",")
	var a := 1.0 if p.size() < 4 else float(p[3])
	return Color(float(p[0]) / 255.0, float(p[1]) / 255.0, float(p[2]) / 255.0, a)


## CSS-Textschatten in eine Liste [Farbe, Versatz, Unschärfe] zerlegen
static func shadows(css: String) -> Array:
	var out := []
	if css == "" or css == "none":
		return out
	var re := RegEx.create_from_string("(rgba?\\([^)]*\\))\\s+(-?[\\d.]+)px\\s+(-?[\\d.]+)px\\s+(-?[\\d.]+)px")
	for m in re.search_all(css):
		out.append([color(m.get_string(1)), Vector2(float(m.get_string(2)), float(m.get_string(3))), float(m.get_string(4))])
	return out
