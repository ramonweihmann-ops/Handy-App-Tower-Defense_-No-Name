shader_type spatial;
// Brücke wie im Mockup „Kampf“: helle Metallplatten mit Fugen, zwei dunkle Fahrspuren,
// türkise Mittellinie, Markierungen am Rand; unterhalb der Mauer dunkler Stationsboden.

uniform float fence_v = 0.804;   // Lage der Mauer in UV.y (0 = hinten am Wurmloch)
uniform float length_m = 46.0;
uniform float width_m = 9.4;
uniform vec3 plate_a : source_color = vec3(0.52, 0.6, 0.78);
uniform vec3 plate_b : source_color = vec3(0.46, 0.54, 0.72);
uniform vec3 dark : source_color = vec3(0.12, 0.13, 0.2);
uniform vec3 teal : source_color = vec3(0.3, 1.0, 0.85);
uniform vec3 pink : source_color = vec3(1.0, 0.45, 0.85);
uniform vec3 floor_col : source_color = vec3(0.16, 0.18, 0.3);

void fragment() {
	float zl = UV.y * length_m;
	float x = (UV.x - 0.5) * width_m;
	vec3 col;
	vec3 emit = vec3(0.0);
	if (UV.y > fence_v) {
		// Boden der Station vor der Mauer
		float zz = (UV.y - fence_v) * length_m;
		col = floor_col * (0.9 + 0.1 * step(0.5, fract(x * 0.5)));
		col = mix(col, dark, smoothstep(0.03, 0.0, abs(fract(zz / 2.0) - 0.5) - 0.47));
	} else {
		float row = floor(zl / 1.6);
		float fr = fract(zl / 1.6);
		col = mod(row, 2.0) < 1.0 ? plate_a : plate_b;
		float seam = smoothstep(0.035, 0.0, fr) + smoothstep(0.965, 1.0, fr);
		col = mix(col, dark, clamp(seam, 0.0, 1.0) * 0.85);
		// zwei dunkle Fahrspuren
		col = mix(col, dark, step(abs(abs(x) - width_m * 0.25), 0.2));
		// Mittellinie: kurze Leuchtstriche auf jeder zweiten Platte
		if (abs(x) < 0.07 && mod(row, 2.0) < 1.0 && abs(fr - 0.5) < 0.22) {
			emit = teal * 2.5;
			col = teal;
		}
		// Querstriche am Rand alle fünf Platten
		if (mod(row, 5.0) == 2.0 && abs(abs(x) - width_m * 0.36) < 0.45 && abs(fr - 0.5) < 0.05) {
			vec3 c = mod(row, 10.0) == 2.0 ? pink : teal;
			emit = c * 2.2;
			col = c;
		}
	}
	ALBEDO = col;
	METALLIC = 0.6;
	ROUGHNESS = 0.32;
	EMISSION = emit;
}
