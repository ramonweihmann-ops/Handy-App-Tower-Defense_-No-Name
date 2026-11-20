# Lava-Asteroid: dunkler Basalt mit glühenden Lavarissen, orangerotes Neon, keine Schrauben
CFG = {"block": (0.16, 0.13, 0.13), "deck": (0.11, 0.09, 0.09), "neon": (1.0, 0.35, 0.05), "neon_strength": 5.0,
       "metal": 0.1, "rough": 0.7, "brushed": False, "block_cracks": (1.0, 0.28, 0.02), "deck_cracks": (1.0, 0.25, 0.02),
       "crack_emit": 3.0, "crack_width": 0.012, "crack_mask": 0.5, "screws": False, "vents": False, "recess": (0.03, 0.02, 0.02),
       "lamp": (1.0, 0.45, 0.08), "ambient": (0.25, 0.08, 0.06), "ambient_strength": 1.0, "sun": 2.2, "sun_color": (1.0, 0.8, 0.7)}
exec(open(os.path.join(KIT_DIR, "streng_kit.py")).read())
