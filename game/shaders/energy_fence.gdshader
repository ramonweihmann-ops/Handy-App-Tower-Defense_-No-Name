shader_type spatial;
// Energiezaun der Station: leuchtende Linien, laufende Abtastwelle, Aufblitzen bei Treffern.
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, shadows_disabled;

uniform vec3 col : source_color = vec3(0.2, 0.75, 1.0);
uniform float hit = 0.0;
uniform float health = 1.0;

void fragment() {
	float vertical = smoothstep(0.92, 1.0, sin(UV.x * 70.0) * 0.5 + 0.5) * 0.35;
	float scan = smoothstep(0.08, 0.0, abs(fract(UV.y - TIME * 0.6) - 0.5) - 0.0) * 0.25;
	float hex = smoothstep(0.9, 1.0, sin(UV.x * 40.0 + sin(UV.y * 12.0) * 2.0) * sin(UV.y * 18.0)) * 0.3;
	float top = smoothstep(0.08, 0.0, abs(UV.y - 0.04)) * 1.2;
	float bottom = smoothstep(0.3, 1.0, UV.y) * 0.6;
	vec3 c = mix(vec3(1.0, 0.25, 0.2), col, clamp(health * 1.4, 0.0, 1.0));
	float a = 0.12 + vertical + scan + hex + top + bottom + hit * 0.8;
	ALBEDO = c * a + vec3(1.0) * hit * 0.3;
	ALPHA = clamp(a, 0.0, 1.0) * 0.8;
}
