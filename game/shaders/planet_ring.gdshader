shader_type spatial;
// Ring eines Planeten aus vielen feinen Bändern
render_mode blend_mix, cull_disabled;
uniform vec4 col : source_color = vec4(0.85, 0.8, 0.7, 1.0);
float h(float x) { return fract(sin(x * 91.7) * 43758.5453); }
void fragment() {
	vec2 uv = UV * 2.0 - 1.0;
	float r = length(uv);
	float band = h(floor(r * 60.0)) * 0.6 + 0.4;
	float a = smoothstep(0.55, 0.6, r) * (1.0 - smoothstep(0.95, 1.0, r)) * band;
	ALBEDO = col.rgb * band;
	ALPHA = a * 0.9;
	ROUGHNESS = 0.8;
}
