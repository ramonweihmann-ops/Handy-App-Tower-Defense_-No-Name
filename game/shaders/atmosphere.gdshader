shader_type spatial;
// Leuchtender Rand eines Planeten (Atmosphäre)
render_mode blend_add, unshaded, cull_back;
uniform vec4 col : source_color = vec4(0.4, 0.7, 1.0, 1.0);
uniform float power = 3.0;
void fragment() {
	float f = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), power);
	ALBEDO = col.rgb * f * 1.6;
	ALPHA = f;
}
