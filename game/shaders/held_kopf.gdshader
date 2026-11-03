shader_type canvas_item;
// Heldenbild als Porträt in einer kleinen Box: Gesicht mittig und groß, Hut und Haare dürfen oben
// über den Rand und werden dort abgeschnitten (wie in den Mockups). face = Augenmitte (x, y) und
// Gesichtsbreite, alles als Anteil am Bild; Ausschnitt: Gesicht face_frac der Boxbreite, Augen auf eye_y.
uniform vec2 box = vec2(80.0, 88.0);
uniform vec2 img = vec2(286.0, 418.0);
uniform vec3 face = vec3(0.5, 0.28, 0.38);
uniform float face_frac = 0.62;
uniform float eye_y = 0.40;
uniform float radius = 6.0;
uniform float grey = 0.0;
uniform float bright = 1.0;

void fragment() {
	float w = face_frac * box.x / face.z;
	vec2 sz = vec2(w, w * img.y / img.x);
	vec2 lt = vec2(box.x * 0.5 - face.x * sz.x, eye_y * box.y - face.y * sz.y);
	vec2 p = UV * box;
	vec2 t = (p - lt) / sz;
	vec4 c = texture(TEXTURE, clamp(t, vec2(0.0), vec2(1.0)));
	if (t.x < 0.0 || t.y < 0.0 || t.x > 1.0 || t.y > 1.0) {
		c.a = 0.0;
	}
	vec2 q = abs(p - box * 0.5) - (box * 0.5 - vec2(radius));
	c.a *= clamp(0.5 - (length(max(q, vec2(0.0))) - radius), 0.0, 1.0);
	float l = dot(c.rgb, vec3(0.3, 0.59, 0.11));
	c.rgb = mix(c.rgb, vec3(l), grey) * bright;
	COLOR = c;
}
