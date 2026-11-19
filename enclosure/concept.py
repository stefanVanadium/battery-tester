"""Estimated v0.1 3D concept model for battery_tester (shared bench enclosure family).

Run: python concept.py -> out/battery_tester_v0.1.step
"""
import math
from pathlib import Path
from build123d import (
    Align, Axis, BuildPart, BuildSketch, Circle, Compound, Cylinder, extrude,
    Locations, Plane, Polygon, Rectangle, chamfer, export_step, fillet,
)

W, D, H = 185.0, 165.0, 88.0
SLANT_DX = 18.0
HAS_FAN = True


def _bezel_plane():
    ang = math.degrees(math.atan2(SLANT_DX, H - 4.0))
    return Plane(
        origin=(0, SLANT_DX / 2, (H + 4.0) / 2),
        x_dir=(1, 0, 0),
        z_dir=(0, -math.cos(math.radians(ang)), math.sin(math.radians(ang))),
    )


def _add_bnc(parts, fp, x, y, idx):
    with BuildPart() as base_bp:
        with BuildSketch(fp.offset(1.8)):
            with Locations([(x, y)]):
                Rectangle(14.5, 14.5)
        Extr = extrude(amount=3.0)
    with BuildPart() as cyl_bp:
        with BuildSketch(fp.offset(4.8)):
            with Locations([(x, y)]):
                Circle(5.6)
        extrude(amount=14.0)
    with BuildPart() as pin_bp:
        with BuildSketch(fp.offset(18.8)):
            with Locations([(x, y)]):
                Circle(2.2)
        extrude(amount=1.2)
    parts.append((base_bp.part, f"bnc_base_{idx}", (0.22, 0.24, 0.27)))
    parts.append((cyl_bp.part, f"bnc_metal_{idx}", (0.78, 0.80, 0.84)))
    parts.append((pin_bp.part, f"bnc_ins_{idx}", (0.90, 0.90, 0.88)))


def _add_banana(parts, fp, x, y, col, idx, shrouded=False):
    r_out = 7.0 if shrouded else 5.8
    h_out = 14.0 if shrouded else 11.0
    with BuildPart() as j_bp:
        with BuildSketch(fp.offset(1.8)):
            with Locations([(x, y)]):
                Circle(r_out)
        extrude(amount=h_out)
    parts.append((j_bp.part, f"banana_{idx}", col))


def build():
    parts = []
    pts = [(0.0, 4.0), (D, 4.0), (D, H), (SLANT_DX, H)]
    with BuildPart() as body_bp:
        with BuildSketch(Plane.YZ):
            Polygon(*pts, align=None)
        extrude(amount=W / 2, both=True)
        fillet(body_bp.edges().filter_by(Axis.X), radius=3.5)
        chamfer(body_bp.edges().filter_by(Axis.Z), length=1.5)
    parts.append((body_bp.part, "body", (0.19, 0.21, 0.24)))

    fp = _bezel_plane()
    with BuildPart() as bezel_bp:
        with BuildSketch(fp):
            Rectangle(170.0, 74.0)
        extrude(amount=1.8)
    parts.append((bezel_bp.part, "bezel", (0.26, 0.29, 0.34)))

    with BuildPart() as feet_bp:
        with Locations([(-W/2+16, 20, 0), (W/2-16, 20, 0), (-W/2+16, D-18, 0), (W/2-16, D-18, 0)]):
            Cylinder(radius=8.0, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append((feet_bp.part, "feet", (0.08, 0.08, 0.09)))

    # Shared 3.5" 480x320 IPS TFT
    with BuildPart() as glass_bp:
        with BuildSketch(fp.offset(1.8)):
            with Locations([(-33.0, 6.5)]):
                Rectangle(85.0, 55.5)
        extrude(amount=1.5)
    with BuildPart() as lcd_bp:
        with BuildSketch(fp.offset(3.35)):
            with Locations([(-33.0, 6.5)]):
                Rectangle(73.4, 49.0)
        extrude(amount=0.4)
    parts.append((glass_bp.part, "tft_glass", (0.06, 0.07, 0.09)))
    parts.append((lcd_bp.part, "tft_active", (0.10, 0.28, 0.32)))

    for idx, (kx, ky) in enumerate([(34.0, 18.0), (64.0, 18.0)]):
        with BuildPart() as kb:
            with BuildSketch(fp.offset(1.8)):
                with Locations([(kx, ky)]):
                    Circle(9.5)
            extrude(amount=14.0)
            chamfer(kb.edges().sort_by(Axis.Z)[-1:], length=1.2)
        parts.append((kb.part, f"knob_{idx}", (0.76, 0.79, 0.83)))
    for idx, (kx, ky) in enumerate([(26.0, -3.0), (43.0, -3.0), (60.0, -3.0), (26.0, -15.0), (43.0, -15.0), (60.0, -15.0)]):
        col = (0.20, 0.65, 0.38) if idx == 5 else (0.38, 0.42, 0.47)
        with BuildPart() as key_bp:
            with BuildSketch(fp.offset(1.8)):
                with Locations([(kx, ky)]):
                    Rectangle(11.0, 7.0)
            extrude(amount=3.5)
        parts.append((key_bp.part, f"key_{idx}", col))
    # 4x Kelvin banana + XT60 + JST-XH 7P
    for idx, (jx, jc) in enumerate([(-62.0, (0.82, 0.16, 0.16)), (-42.95, (0.85, 0.68, 0.14)), (-23.9, (0.16, 0.45, 0.82)), (-4.85, (0.12, 0.12, 0.14))]):
        _add_banana(parts, fp, jx, -28.0, jc, idx)
    with BuildPart() as xt_bp:
        with BuildSketch(fp.offset(1.8)):
            with Locations([(22.0, -28.0)]):
                Rectangle(16.0, 9.0)
        extrude(amount=9.0)
    with BuildPart() as bal_bp:
        with BuildSketch(fp.offset(1.8)):
            with Locations([(52.0, -28.0)]):
                Rectangle(20.0, 7.0)
        extrude(amount=7.0)
    parts.append((xt_bp.part, "xt60", (0.92, 0.74, 0.12)))
    parts.append((bal_bp.part, "jst_xh", (0.90, 0.90, 0.88)))

    # Rear panel: IEC C14, PE lug, optional fan, isolated USB-C
    rp = Plane(origin=(0, D, H / 2 + 2), x_dir=(-1, 0, 0), z_dir=(0, 1, 0))
    with BuildPart() as iec_bp:
        with BuildSketch(rp):
            with Locations([(-56.0, -10.0)]):
                Rectangle(30.0, 22.0)
        extrude(amount=4.0)
    parts.append((iec_bp.part, "rear_iec", (0.10, 0.11, 0.13)))

    with BuildPart() as pe_bp:
        with BuildSketch(rp):
            with Locations([(-56.0, 14.0)]):
                Circle(4.5)
        extrude(amount=8.0)
    parts.append((pe_bp.part, "rear_pe", (0.85, 0.70, 0.20)))

    with BuildPart() as rusb_bp:
        with BuildSketch(rp):
            with Locations([(56.0, -12.0)]):
                Rectangle(10.0, 4.2)
        extrude(amount=2.5)
    parts.append((rusb_bp.part, "rear_usbc", (0.72, 0.75, 0.78)))

    if HAS_FAN:
        with BuildPart() as fan_bp:
            with BuildSketch(rp):
                with Locations([(8.0, 0.0)]):
                    Circle(26.0)
            extrude(amount=2.0)
        parts.append((fan_bp.part, "rear_fan", (0.13, 0.14, 0.16)))

    return parts


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "out"
    out_dir.mkdir(exist_ok=True)
    parts = build()
    comp = Compound(children=[p[0] for p in parts])
    export_step(comp, str(out_dir / "battery_tester_v0.1.step"))
    print("Exported", out_dir / "battery_tester_v0.1.step")
