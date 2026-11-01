shader_type canvas_item;
// Gasplanet im Ladebildschirm: helle und dunkle Wolkenbänder, die langsam vorbeiziehen,
// ein roter Sturmwirbel, Schatten zur Seite und ein blauer Lichtsaum am Rand.

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;  // -1..1
	float r = length(p);
	float inner = 0.74;        // Planetenrand innerhalb der Fläche (Rest: Lichtsaum)
	float d = r / inner;
	vec4 outc = vec4(0.0);
	if (d < 1.0) {
		// Kugel: Längengrad aus der Wölbung, damit die Bänder sich zum Rand hin biegen
		float z = sqrt(1.0 - d * d);
		vec2 sp = p / inner;
		float lon = asin(clamp(sp.x / max(0.001, sqrt(1.0 - sp.y * sp.y)), -1.0, 1.0));
		float lat = sp.y;
		float t = TIME * 0.05;
		float w = noise(vec2(lon * 3.0 + t * 6.0, lat * 9.0)) * 0.6;
		float b = sin(lat * 15.0 + w * 2.2 + sin(lon * 2.0 + t * 4.0) * 0.4);
		vec3 light = vec3(0.94, 0.87, 0.74);
		vec3 mid = vec3(0.80, 0.68, 0.50);
		vec3 dark = vec3(0.56, 0.36, 0.25);
		vec3 col = mix(mid, light, smoothstep(-0.2, 0.6, b));
		col = mix(col, dark, smoothstep(0.55, 0.95, -b) * 0.8);
		// roter Sturmwirbel, wandert mit den Bändern
		vec2 sc = vec2(lon - (0.35 - mod(t * 2.0, 2.4)), lat - 0.15);
		float storm = length(sc / vec2(0.32, 0.13));
		col = mix(col, vec3(0.72, 0.27, 0.17), smoothstep(1.0, 0.6, storm));
		col = mix(col, vec3(0.56, 0.18, 0.12), smoothstep(0.55, 0.2, storm));
		col = mix(col, vec3(0.85, 0.44, 0.29), smoothstep(0.18, 0.0, storm) * 0.7);
		// Licht von oben links, dunkle Nachtseite unten rechts
		float lit = clamp(dot(normalize(vec3(sp, z)), normalize(vec3(-0.5, -0.55, 0.65))), 0.0, 1.0);
		col *= 0.25 + 0.85 * lit;
		col += vec3(1.0) * pow(lit, 18.0) * 0.18;
		outc = vec4(col, smoothstep(1.0, 0.985, d));
	}
	// Lichtsaum (Atmosphäre)
	float rim = smoothstep(0.97, 0.75, r) * smoothstep(0.66, 0.75, r);
	vec4 halo = vec4(0.56, 0.77, 1.0, rim * 0.55);
	COLOR = mix(halo, outc, outc.a);
}
