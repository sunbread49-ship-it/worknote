"""프로필 3D 시안 (색 조합 08)
  /home/user/bpyenv/bin/python tools/blender_profile.py <out.png> [variant]
  0: '악' 유광 + 빨간 구슬 (흰 바탕)   a: '악어새' 단어 + 빨간 마침표 구슬
  b: 진초록 바탕 + 흰 무광 '악' + 빨간 구슬   c: 진초록 동전 + 흰 '악' 양각 + 딥레드 테두리
"""
import math, sys
from pathlib import Path
import bpy

out = sys.argv[1]
V = sys.argv[2] if len(sys.argv) > 2 else "0"
FONT = str(Path(__file__).resolve().parents[1] / "assets" / "fonts" / "Pretendard-Black.otf")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 800
sc.view_settings.view_transform = "Standard"


def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def mat(name, hexc, metal, rough, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(hexc), 1)
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    return m

GREEN, RED, WHITE = mat("g", "01422B", 0.0, 0.25, 0.8), mat("r", "A3161A", 0.0, 0.15, 1.0), mat("w", "FBFBF9", 0.0, 0.6)
WHITE_GLOSS = mat("wg", "FBFBF9", 0.0, 0.3, 0.6)
GREEN_FLOOR = mat("gf", "01422B", 0.0, 0.7)
GREEN_METAL = mat("gm", "01422B", 0.6, 0.3, 0.5)
bg_hex = "01422B" if V == "b" else "FBFBF9"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(bg_hex), 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6 if V == "b" else 1.0

bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01))
bpy.context.object.data.materials.append(GREEN_FLOOR if V == "b" else WHITE)


def text(body, size, ext, loc, m):
    bpy.ops.object.text_add(location=loc); t = bpy.context.object
    t.data.font = bpy.data.fonts.load(FONT); t.data.body = body; t.data.size = size
    t.data.align_x = "CENTER"; t.data.align_y = "CENTER"; t.data.extrude = ext
    t.data.bevel_depth = min(0.06, ext * 0.25); t.data.bevel_resolution = 4
    t.data.materials.append(m)
    return t


def ball(r, loc):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=64, ring_count=32)
    bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(RED)

cam_loc, lens, tgt = (1.2, -5.2, 11.5), 70, (0.1, -0.1, 0.3)
if V == "0":
    text("악", 5.0, 0.28, (-0.2, 0.2, 0.34), GREEN); ball(0.42, (2.0, -1.45, 0.42))
elif V == "a":
    t = text("악어새", 3.4, 0.24, (-0.35, 0.0, 0.3), GREEN)
    bpy.context.view_layer.update(); hw = t.dimensions.x / 2
    ball(0.3, (-0.35 + hw + 0.45, -0.95, 0.3))
    cam_loc, lens, tgt = (0.3, -2.4, 14.0), 50, (0.0, -0.1, 0.3)
elif V == "b":
    text("악", 5.0, 0.32, (-0.2, 0.2, 0.38), WHITE_GLOSS); ball(0.4, (1.75, -1.3, 0.4))
    lens = 56
elif V == "c":
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=3.3, depth=0.5, location=(0, 0, 0.25))
    coin = bpy.context.object; coin.data.materials.append(mat("rm", "A3161A", 0.0, 0.4, 0.2))
    bpy.ops.object.modifier_add(type="BEVEL"); coin.modifiers["Bevel"].width = 0.08; coin.modifiers["Bevel"].segments = 4
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=2.95, depth=0.12, location=(0, 0, 0.53))
    bpy.context.object.data.materials.append(GREEN_METAL)
    text("악", 3.9, 0.16, (0.0, 0.05, 0.59), WHITE_GLOSS)
    cam_loc, lens, tgt = (0.6, -4.5, 12.0), 58, (0.0, 0.0, 0.4)

bpy.ops.object.light_add(type="AREA", location=(-4, -4, 8)); L = bpy.context.object; L.data.energy = 900; L.data.size = 6
L.rotation_euler = (math.radians(30), math.radians(-25), 0)
bpy.ops.object.light_add(type="AREA", location=(5, -2, 4)); L2 = bpy.context.object; L2.data.energy = 250; L2.data.size = 4
L2.rotation_euler = (math.radians(60), math.radians(50), 0)
bpy.ops.object.camera_add(location=cam_loc); cam = bpy.context.object; sc.camera = cam; cam.data.lens = lens
bpy.ops.object.empty_add(location=tgt); e = bpy.context.object
c = cam.constraints.new("TRACK_TO"); c.target = e; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
