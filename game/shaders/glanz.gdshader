shader_type canvas_item;
// Glanzstreifen wie in den Mockups: ein heller, schräger Streifen läuft über das Symbol
// (nur über die sichtbaren Teile des Bildes), danach kurze Pause.
uniform float dur = 2.6;
uniform float delay = 0.0;
uniform float width = 0.1;
uniform float strength = 0.7;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float ph = fract((TIME + delay) / dur);
	float p = mix(-0.45, 1.65, clamp(ph / 0.6, 0.0, 1.0));
	float d = (UV.x + (1.0 - UV.y) * 0.36) - p;
	float band = ph < 0.6 ? smoothstep(width, 0.0, abs(d)) : 0.0;
	c.rgb = mix(c.rgb, vec3(1.0), band * strength * c.a);
	COLOR = c;
}
