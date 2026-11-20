# Schrottwelt: rostige Platten mit vielen Nieten, Kupferrohr, orangefarbene Lampen
CFG = {"block": (0.46, 0.28, 0.16), "deck": (0.32, 0.2, 0.12), "neon": (1.0, 0.55, 0.15), "neon_strength": 3.0, "metal": 0.6, "rough": 0.55,
       "screw": (0.55, 0.4, 0.28), "recess": (0.05, 0.03, 0.02), "lamp": (1.0, 0.6, 0.15), "edge_neon": False, "props": ["pipe"],
       "ambient": (0.18, 0.1, 0.06), "ambient_strength": 1.0, "sun": 2.8, "sun_color": (1.0, 0.88, 0.75)}
exec(open(os.path.join(KIT_DIR, "streng_kit.py")).read())
