"""비행기 공중 대기 3D (Blender · Cycles CPU) — 지식창고 '수능 듣기평가 35분' 쇼츠
가운데 시험장(학교 건물) 위로 비행기 4대가 높은 하늘(3km 위)에서 원을 그리며 대기 · 지면은 조용한 도시 블록
  /home/user/bpyenv/bin/python tools/blender_holding.py <out_dir> [frames]   (960x620)
"""
import math, os, random, sys
from pathlib import Path
import bpy

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
NF = int(sys.argv[2]) if len(sys.argv) > 2 else 150
ONLY = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 620


def mat(name, color, metal=0.0, rough=0.5, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = emit
    return m

WHITE = mat("w", (0.9, 0.92, 0.95), 0.2, 0.3)
RED = mat("r", (0.9, 0.08, 0.08), 0, 0.4, emit=2.0)
GROUND = mat("g", (0.09, 0.12, 0.1), 0, 0.9)
BLOCK = mat("b", (0.35, 0.37, 0.42), 0, 0.7)
SCHOOL = mat("s", (0.75, 0.55, 0.35), 0, 0.6)
RING = mat("ring", (1.0, 0.8, 0.2), 0, 0.3, emit=3.0)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.55, 0.85, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
bpy.ops.object.light_add(type="SUN", location=(0, 0, 20)); sun = bpy.context.object; sun.data.energy = 3.0; sun.rotation_euler = (math.radians(40), 0, math.radians(30))

bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0)); bpy.context.object.data.materials.append(GROUND)
rnd = random.Random(3)
for i in range(70):   # 도시 블록
    x, y = rnd.uniform(-18, 18), rnd.uniform(-18, 18)
    if abs(x) < 3 and abs(y) < 3:
        continue
    h = rnd.uniform(0.3, 2.2)
    bpy.ops.mesh.primitive_cube_add(location=(x, y, h / 2)); c = bpy.context.object
    c.scale = (rnd.uniform(0.4, 0.9), rnd.uniform(0.4, 0.9), h / 2); c.data.materials.append(BLOCK)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.6)); s = bpy.context.object; s.scale = (2.2, 0.8, 0.6); s.data.materials.append(SCHOOL)
bpy.ops.mesh.primitive_torus_add(major_radius=3.2, minor_radius=0.06, location=(0, 0, 0.05)); bpy.context.object.data.materials.append(RING)

ALT, R = 9.0, 7.0   # 높은 하늘의 대기 원
bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.03, location=(0, 0, ALT)); hr = bpy.context.object
hr.data.materials.append(mat("hr", (1, 1, 1), 0, 0.5, emit=1.5))


def plane():
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.6, rotation=(0, math.radians(90), 0)); parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cube_add(location=(0.05, 0, 0)); wg = bpy.context.object; wg.scale = (0.22, 0.95, 0.03); parts.append(wg)
    bpy.ops.mesh.primitive_cube_add(location=(-0.7, 0, 0.18)); tl = bpy.context.object; tl.scale = (0.12, 0.03, 0.2); parts.append(tl)
    bpy.ops.mesh.primitive_cube_add(location=(-0.7, 0, 0.02)); th = bpy.context.object; th.scale = (0.1, 0.35, 0.02); parts.append(th)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.8, 0, 0)); parts.append(bpy.context.object)
    for p in parts:
        p.data.materials.append(WHITE)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.05, 0.95, 0)); lt = bpy.context.object; lt.data.materials.append(RED); parts.append(lt)
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)   # 동체를 X축으로 눕힌 채 고정
    return bpy.context.object

PLANES = [plane() for _ in range(4)]
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 30
bpy.ops.object.empty_add(location=(0, 0, 4)); tgt = bpy.context.object
c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
for fi in range(NF):
    if ONLY and fi not in ONLY:
        continue
    u = fi / NF
    for k, p in enumerate(PLANES):
        a = 2 * math.pi * (u * 0.9 + k / 4)
        p.location = (R * math.cos(a), R * math.sin(a), ALT + 0.15 * math.sin(a * 2 + k))
        p.rotation_euler = (math.radians(-18), 0, a + math.pi / 2)   # 원을 따라 기울여 선회
    ca = math.radians(-60 + 25 * u)
    cam.location = (19 * math.cos(ca), 19 * math.sin(ca), 7.5 + 2 * u)
    sc.render.filepath = str(out / f"f{fi:04d}.png")
    bpy.ops.render.render(write_still=True)
print("done", NF)
