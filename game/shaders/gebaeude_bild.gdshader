shader_type canvas_item;
// Gebäudebild im Rahmen des Gebäudefensters: wie im Mockup breiter als der Rahmen, mittig,
// mit abgerundeten Ecken beschnitten; noch nicht gebaut: grau und halb durchsichtig.
uniform vec2 box = vec2(210.0, 170.0);
uniform vec2 img = vec2(220.0, 187.0);
uniform float radius = 16.0;
uniform float grey = 0.0;
uniform float alpha = 1.0;

void fragment() {
	vec2 p = UV * box;
	vec2 t = (p - (box - img) * 0.5) / img;
	vec4 c = texture(TEXTURE, clamp(t, vec2(0.0), vec2(1.0)));
	if (t.x < 0.0 || t.y < 0.0 || t.x > 1.0 || t.y > 1.0) {
		c.a = 0.0;
	}
	vec2 q = abs(p - box * 0.5) - (box * 0.5 - vec2(radius));
	float d = length(max(q, vec2(0.0))) - radius;
	c.a *= clamp(0.5 - d, 0.0, 1.0);
	float l = dot(c.rgb, vec3(0.3, 0.59, 0.11));
	c.rgb = mix(c.rgb, vec3(l), grey);
	c.a *= alpha;
	COLOR = c;
}
