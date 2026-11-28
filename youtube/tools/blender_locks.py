"""번호 자물쇠 3D (Blender · Cycles CPU) — 지식창고 '비밀번호' 쇼츠
왼쪽: 짧은 비밀번호(4칸) → 금방 맞춰져 고리가 '딸깍' 열림 / 오른쪽: 긴 비밀번호(12칸) → 끝까지 돌기만 함
  /home/user/bpyenv/bin/python tools/blender_locks.py <out_dir> [frames]   (세로 540x960)
"""
import math, os, random, sys
from pathlib import Path
import bpy

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
NF = int(sys.argv[2]) if len(sys.argv) > 2 else 120
ONLY = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 20; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 620   # 쇼츠 위쪽(멘트 자리 위)에 넣는 가로형


def mat(name, color, metal, rough, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = emit
    return m

BRASS = mat("brass", (0.95, 0.68, 0.28), 1.0, 0.25)
STEEL = mat("steel", (0.8, 0.82, 0.86), 1.0, 0.18)
DARK = mat("dark", (0.05, 0.05, 0.06), 0.3, 0.4)
WHITE = mat("white", (0.95, 0.95, 0.95), 0.0, 0.3, emit=0.6)
GREEN = mat("green", (0.1, 0.9, 0.35), 0.0, 0.3, emit=4.0)
RED = mat("red", (0.95, 0.15, 0.15), 0.0, 0.3, emit=3.0)

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -2.6))
bpy.context.object.data.materials.append(mat("floor", (0.03, 0.035, 0.05), 0.0, 0.25))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.012, 0.02, 1)
bpy.ops.object.light_add(type="AREA", location=(0, -6, 6)); L = bpy.context.object; L.data.energy = 1600; L.data.size = 6; L.rotation_euler = (math.radians(45), 0, 0)
bpy.ops.object.light_add(type="SPOT", location=(4, -3, 5)); S = bpy.context.object; S.data.energy = 700; S.rotation_euler = (math.radians(40), math.radians(30), 0)
bpy.ops.object.camera_add(location=(0, -13.5, 0.6), rotation=(math.radians(88), 0, 0)); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 58


def lock(cx, cz, n, scale):
    """세로로 선 자물쇠: 몸통 + 고리 + n칸 번호 링(가로축 회전) + 칸마다 숫자"""
    parts = {}
    bw = 1.9 * scale
    bh = (0.42 * n + 0.6) * scale
    bpy.ops.mesh.primitive_cube_add(location=(cx, 0, cz)); body = bpy.context.object
    body.scale = (bw / 2, 0.55 * scale, bh / 2); body.data.materials.append(BRASS)
    bpy.ops.object.modifier_add(type="BEVEL"); body.modifiers["Bevel"].width = 0.08 * scale; body.modifiers["Bevel"].segments = 3
    bpy.ops.mesh.primitive_torus_add(major_radius=0.62 * scale, minor_radius=0.12 * scale, location=(cx, 0, cz + bh / 2 + 0.1 * scale),
                                     rotation=(math.radians(90), 0, 0))
    sh = bpy.context.object; sh.data.materials.append(STEEL); parts["shackle"] = sh; parts["sh_z"] = sh.location.z
    rings, digits = [], []
    for i in range(n):
        z = cz + bh / 2 - 0.5 * scale - i * 0.42 * scale
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.24 * scale, depth=bw * 0.62, location=(cx, -0.58 * scale, z),
                                            rotation=(0, math.radians(90), 0))
        r = bpy.context.object; r.data.materials.append(DARK); r.rotation_mode = "ZYX"; rings.append(r)   # Z(자기 축) 먼저 돌고 → Y로 눕힘
        bpy.ops.object.text_add(location=(cx - 0.12 * scale, -0.83 * scale, z - 0.13 * scale), rotation=(math.radians(90), 0, 0))
        tx = bpy.context.object; tx.data.size = 0.36 * scale; tx.data.body = "0"; tx.data.materials.append(WHITE); digits.append(tx)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12 * scale, location=(cx + bw * 0.38, -0.6 * scale, cz - bh / 2 + 0.25 * scale))
    lamp = bpy.context.object; lamp.data.materials.append(RED); parts["lamp"] = lamp
    parts.update(rings=rings, digits=digits, n=n)
    return parts

A = lock(-1.75, 0.6, 4, 0.95)
B = lock(1.75, 0.0, 12, 0.62)
CODE = "0513"
OPEN_AT = int(NF * 0.32)
rnd = random.Random(7)
for fi in range(NF):
    if ONLY and fi not in ONLY:
        continue
    for P, opens in ((A, True), (B, False)):
        done = opens and fi >= OPEN_AT
        for i, (r, tx) in enumerate(zip(P["rings"], P["digits"])):
            if done:
                r.rotation_euler[2] = 0
                tx.data.body = CODE[i]
            else:
                r.rotation_euler[2] = fi * (1.3 + 0.17 * i)   # 링 자기 축(가로)으로 회전
                tx.data.body = str(rnd.randint(0, 9))
        if opens:
            k = max(0.0, min(1.0, (fi - OPEN_AT) / 6))
            P["shackle"].location.z = P["sh_z"] + 0.55 * k
            P["shackle"].rotation_euler[2] = math.radians(35) * k
            P["lamp"].data.materials[0] = GREEN if done else RED
    cam.location = (0.25 * math.sin(fi / NF * 2), -15.0 + 1.2 * fi / NF, 1.0)
    sc.render.filepath = str(out / f"f{fi:04d}.png")
    bpy.ops.render.render(write_still=True)
print("done", NF)
