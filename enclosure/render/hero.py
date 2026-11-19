"""Render front and rear isometric concept views side by side -> out/hero_v0.1.png"""
import sys
from pathlib import Path
import matplotlib.image
import numpy as np
import pyvista as pv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import concept  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "out")
out.mkdir(exist_ok=True)
parts = concept.build()

p = pv.Plotter(off_screen=True, window_size=(1800, 1000))
p.enable_anti_aliasing("ssaa")
p.set_background("white")
p.remove_all_lights()
p.add_light(pv.Light(position=(-240, -280, 340), intensity=0.9, light_type="scene light"))
p.add_light(pv.Light(position=(260, -140, 180), intensity=0.45, light_type="scene light"))
p.add_light(pv.Light(position=(0, 360, 220), intensity=0.35, light_type="scene light"))

cx, cy, cz = 0.0, concept.D / 2, concept.H / 2
dx_off = getattr(concept, "HERO_DX", 148.0)
cam_y = getattr(concept, "HERO_CAM_Y", -760.0)
for rot_deg, dx in ((-24.0, -dx_off), (150.0, dx_off)):
    a = np.radians(rot_deg)
    ca, sa = np.cos(a), np.sin(a)
    for shape, label, color in parts:
        verts, tris = shape.tessellate(0.06, 0.28)
        P = np.array([[q.X, q.Y, q.Z] for q in verts])
        T = np.array(tris)
        x, y = P[:, 0], P[:, 1] - cy
        P = np.column_stack([x * ca - y * sa + dx, x * sa + y * ca, P[:, 2]])
        mesh = pv.PolyData(P, np.hstack([np.full((len(T), 1), 3), T]).ravel())
        mesh = mesh.compute_normals(split_vertices=True, feature_angle=35)
        glossy = any(k in label for k in ("tft", "plate", "steel", "barrel", "tip", "bnc"))
        p.add_mesh(mesh, color=tuple(color)[:3], smooth_shading=True, pbr=False,
                   specular=0.9 if glossy else 0.45, specular_power=42 if glossy else 18,
                   ambient=0.22, diffuse=0.8)

p.camera.position = (0.0, cam_y, 315.0)
p.camera.focal_point = (0.0, 0.0, cz)
p.camera.up = (0.0, 0.0, 1.0)
p.camera.view_angle = 28
img = p.screenshot(transparent_background=True, return_img=True)
alpha = img[:, :, 3] > 0
rows, cols = np.where(alpha.any(1))[0], np.where(alpha.any(0))[0]
m = 36
img = img[max(rows[0] - m, 0):rows[-1] + m, max(cols[0] - m, 0):cols[-1] + m]
matplotlib.image.imsave(out / "hero_v0.1.png", img)
print("wrote", out / "hero_v0.1.png")
