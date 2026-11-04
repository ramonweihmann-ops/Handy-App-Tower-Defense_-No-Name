class_name WeaponIcons
extends RefCounted
## Kleine Waffensymbole (Heldenauswahl beim Kampfstart), je Waffenart als SVG im Stil des Mockups
## „Kampf · Heldenauswahl beim Start“: graues Metall mit dunkler Kontur, farbige Akzente.
## Raketenwerfer, Frostpistole und Maschinengewehr stammen aus dem Mockup, die übrigen im selben Stil.
## Seitenverhältnis 22 × 18 (wie im Mockup), Ausgabe als Textur in der gewünschten Breite.

const STROKE := "stroke=\"#2a3048\" stroke-width=\"1.2\" stroke-linejoin=\"round\""
const METAL := "#9aa4b8"

static var _cache := {}


static func svg(family: String) -> String:
	var body := ""
	match family:
		"rocket":
			body = "<rect x=\"6\" y=\"2\" width=\"15\" height=\"6\" rx=\"2\" fill=\"#d9443e\" stroke=\"#5a1410\" stroke-width=\"1.2\"/><rect x=\"6\" y=\"9\" width=\"15\" height=\"6\" rx=\"2\" fill=\"#c8393a\" stroke=\"#5a1410\" stroke-width=\"1.2\"/><circle cx=\"5\" cy=\"5\" r=\"3.2\" fill=\"#ef6a5a\" stroke=\"#5a1410\" stroke-width=\"1.2\"/><circle cx=\"5\" cy=\"5\" r=\"1.3\" fill=\"#3a0a08\"/><circle cx=\"5\" cy=\"12\" r=\"3.2\" fill=\"#ef6a5a\" stroke=\"#5a1410\" stroke-width=\"1.2\"/><circle cx=\"5\" cy=\"12\" r=\"1.3\" fill=\"#3a0a08\"/>"
		"cryo":
			body = "<path d=\"M3 4h14l2 2v3H9l-1 7H4l1-7H3z\" fill=\"%s\" %s/><rect x=\"16\" y=\"5\" width=\"5\" height=\"4\" rx=\"1\" fill=\"#6fe8ff\" stroke=\"#1a5a7a\" stroke-width=\"1\"/>" % [METAL, STROKE]
		"mg":
			body = "<path d=\"M1 9l3-3h12l2-2h3v3h1v2h-5l-2 2h-3l-1 5H7l1-5H4z\" fill=\"%s\" %s/><rect x=\"10\" y=\"10\" width=\"2.5\" height=\"5\" rx=\"1\" fill=\"#5a6478\"/>" % [METAL, STROKE]
		"revolver":
			body = "<path d=\"M2 5h15l3 2v2H10l-1 1-1 6H4l1-6-3-1z\" fill=\"%s\" %s/><circle cx=\"11\" cy=\"7.5\" r=\"2.6\" fill=\"#c8a060\" stroke=\"#5a3a10\" stroke-width=\"1\"/>" % [METAL, STROKE]
		"tesla":
			body = "<path d=\"M3 5h12l2 2v2H9l-1 7H4l1-7H3z\" fill=\"%s\" %s/><path d=\"M18 2l-2 4h3l-3 5\" fill=\"none\" stroke=\"#ffe27a\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/>" % [METAL, STROKE]
		"shotgun":
			body = "<path d=\"M1 8h20v3H8l-2 5H2l1-5H1z\" fill=\"%s\" %s/><rect x=\"9\" y=\"5\" width=\"12\" height=\"2.4\" rx=\"1\" fill=\"#7a5a3a\" stroke=\"#3a2410\" stroke-width=\"1\"/>" % [METAL, STROKE]
		"sniper":
			body = "<path d=\"M1 9h21v2H9l-2 5H3l1-5H1z\" fill=\"%s\" %s/><rect x=\"8\" y=\"4\" width=\"8\" height=\"3\" rx=\"1.5\" fill=\"#5a6478\" stroke=\"#2a3048\" stroke-width=\"1\"/><circle cx=\"16.5\" cy=\"5.5\" r=\"1.2\" fill=\"#6fe8ff\"/>" % [METAL, STROKE]
		"flamer":
			body = "<path d=\"M1 8h14v3H8l-2 5H2l1-5H1z\" fill=\"%s\" %s/><path d=\"M15 9.5c2-3 4-2 4-5 2 2 3 4 2 6-1 2-3 2-6-1z\" fill=\"#ff8a2a\" stroke=\"#a83a00\" stroke-width=\"1\" stroke-linejoin=\"round\"/>" % [METAL, STROKE]
		"beam":
			body = "<path d=\"M11 1.5l2.4 5 5.4.6-4 3.7 1.1 5.4L11 13.5l-4.9 2.7 1.1-5.4-4-3.7 5.4-.6z\" fill=\"#ffe27a\" stroke=\"#8a5a00\" stroke-width=\"1.2\" stroke-linejoin=\"round\"/>"
		"drone":
			body = "<path d=\"M4 4h9v4H4z\" fill=\"%s\" %s/><path d=\"M8 8v8M5 11h6M5 14h6\" stroke=\"#5a6478\" stroke-width=\"1.6\" stroke-linecap=\"round\"/><circle cx=\"17\" cy=\"7\" r=\"3\" fill=\"#6fe0e8\" stroke=\"#1a5a6a\" stroke-width=\"1\"/>" % [METAL, STROKE]
		"cannon":
			body = "<rect x=\"6\" y=\"4\" width=\"15\" height=\"7\" rx=\"3\" fill=\"%s\" %s/><circle cx=\"7\" cy=\"12\" r=\"4.5\" fill=\"#7a5a3a\" stroke=\"#3a2410\" stroke-width=\"1.2\"/><circle cx=\"7\" cy=\"12\" r=\"1.5\" fill=\"#3a2410\"/>" % [METAL, STROKE]
		"gravity":
			body = "<path d=\"M3 6a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z\" fill=\"#a88aff\" stroke=\"#3a2470\" stroke-width=\"1.2\"/><path d=\"M15 9h6M17 6l3 3-3 3\" fill=\"none\" stroke=\"#ff9a3d\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/>"
		_:
			return ""
	return "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"22\" height=\"18\" viewBox=\"0 0 22 18\">%s</svg>" % body


## Textur in Breite w (Pixel); null, wenn es für die Waffenart kein Symbol gibt
static func texture(family: String, w: int) -> Texture2D:
	var key := "%s:%d" % [family, w]
	if _cache.has(key):
		return _cache[key]
	var s := svg(family)
	var tex: Texture2D = null
	if s != "":
		var img := Image.new()
		if img.load_svg_from_string(s, float(w) / 22.0) == OK:
			tex = ImageTexture.create_from_image(img)
	_cache[key] = tex
	return tex
