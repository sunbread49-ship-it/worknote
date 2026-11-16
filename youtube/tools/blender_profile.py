"""프로필 시안 4 — 3D '악' 글자 (진초록 유광) + 딥레드 구슬, 흰 바탕
  /home/user/bpyenv/bin/python tools/blender_profile.py <out.png>
"""
import math, sys
from pathlib import Path
import bpy

out = sys.argv[1]
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
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("FBFBF9"), 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01)); bpy.context.object.data.materials.append(WHITE)
bpy.ops.object.text_add(location=(0, 0, 0)); t = bpy.context.object
t.data.font = bpy.data.fonts.load(FONT); t.data.body = "악"; t.data.size = 5.0
t.data.align_x = "CENTER"; t.data.align_y = "CENTER"; t.data.extrude = 0.28; t.data.bevel_depth = 0.06; t.data.bevel_resolution = 4
t.location = (-0.2, 0.2, 0.34); t.data.materials.append(GREEN)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(2.0, -1.45, 0.42), segments=64, ring_count=32)
bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(RED)

bpy.ops.object.light_add(type="AREA", location=(-4, -4, 8)); L = bpy.context.object; L.data.energy = 900; L.data.size = 6
L.rotation_euler = (math.radians(30), math.radians(-25), 0)
bpy.ops.object.light_add(type="AREA", location=(5, -2, 4)); L2 = bpy.context.object; L2.data.energy = 250; L2.data.size = 4
L2.rotation_euler = (math.radians(60), math.radians(50), 0)
bpy.ops.object.camera_add(location=(1.2, -5.2, 11.5)); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 70
bpy.ops.object.empty_add(location=(0.1, -0.1, 0.3)); tgt = bpy.context.object
c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
