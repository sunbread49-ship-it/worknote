"""동전 탑 3D 애니메이션 (Blender · Cycles CPU) — EP017: 그냥 지수 vs 커버드콜(원금 탑 + 옆에 쌓이는 분배금 더미)
  /home/user/bpyenv/bin/python tools/blender_coins.py <data.json> <out_dir> [frames]
  data: [{date, idx, cc, div}] (만 원) · 동전 1개 = 50만 원 · 프레임 PNG → 2D 라벨은 따로 합성
"""
import json, math, sys
from pathlib import Path
import bpy

data = json.load(open(sys.argv[1]))
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
NF = int(sys.argv[3]) if len(sys.argv) > 3 else 165
UNIT = 50.0
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 960, 540, 100
sc.render.film_transparent = False


def mat(name, color, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    return m

SILVER = mat("silver", (0.82, 0.84, 0.88), 1.0, 0.22)
GOLD = mat("gold", (1.0, 0.72, 0.22), 1.0, 0.2)
RED = mat("red", (0.85, 0.18, 0.18), 0.6, 0.3)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.5, depth=0.12)
proto = bpy.context.object; proto.name = "coinproto"
bpy.ops.object.shade_smooth()
proto.hide_render = True; proto.hide_viewport = True
TH = 0.13
COINS = {}


def coin(key, x, y, z, m, rot=0.0):
    ob = proto.copy(); ob.data = proto.data.copy(); ob.data.materials.clear(); ob.data.materials.append(m)
    ob.location = (x, y, z); ob.rotation_euler = (0, 0, rot); ob.hide_render = False; ob.hide_viewport = False
    sc.collection.objects.link(ob); COINS[key] = ob
    return ob

# 바닥 · 배경 · 조명
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.06))
bpy.context.object.data.materials.append(mat("floor", (0.05, 0.055, 0.07), 0.0, 0.3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.014, 0.024, 1)
bpy.ops.object.light_add(type="AREA", location=(0, -4, 7)); L = bpy.context.object; L.data.energy = 1400; L.data.size = 5; L.rotation_euler = (math.radians(30), 0, 0)
bpy.ops.object.light_add(type="SPOT", location=(-5, 2, 5)); S = bpy.context.object; S.data.energy = 900; S.rotation_euler = (math.radians(-45), math.radians(-40), 0)
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 42
bpy.ops.object.empty_add(location=(0.2, 0, 1.0)); target = bpy.context.object
tc = cam.constraints.new("TRACK_TO"); tc.target = target; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
import os
ONLY = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]

maxn = max(max(r["idx"], r["cc"]) for r in data) / UNIT
XL, XR, XD = -1.6, 0.9, 2.3
months = len(data)
hold = 25
for fi in range(NF):
    if ONLY and fi not in ONLY:
        continue
    u = min(1.0, fi / (NF - hold))
    pos = u * (months - 1)
    i0 = int(pos); fr = pos - i0
    r0, r1 = data[i0], data[min(i0 + 1, months - 1)]
    lerp = lambda k: r0[k] + (r1[k] - r0[k]) * fr
    n_idx, n_cc, n_div = lerp("idx") / UNIT, lerp("cc") / UNIT, lerp("div") / UNIT
    if u >= 1:   # 끝: 떠 있는 동전 없이 정리
        n_idx, n_cc, n_div = round(n_idx), round(n_cc), round(n_div)
    for ob in list(COINS.values()):
        bpy.data.objects.remove(ob, do_unlink=True)
    COINS.clear()
    for side, x, n, m in (("L", XL, n_idx, SILVER), ("R", XR, n_cc, SILVER), ("D", XD, n_div, GOLD)):
        full = int(n); part = n - full
        for k in range(full):
            jit = 0.03 * math.sin(k * 2.3 + x)
            coin(f"{side}{k}", x + jit, 0.02 * math.cos(k * 1.7), 0.06 + k * TH, m, rot=k * 0.4)
        if part > 0.05:   # 떨어지는 중인 동전 (위에서 내려와 쌓임)
            drop = (1 - part) * 2.5
            coin(f"{side}p", x, 0, 0.06 + full * TH + drop, m, rot=full * 0.4)
    # 카메라: 천천히 돌며 다가감
    ang = math.radians(-12 + 10 * u)
    rad = 11.5 - 0.8 * u
    cz = 2.0 + maxn * TH * 0.5
    cam.location = (0.2 + rad * math.sin(ang), -rad * math.cos(ang), cz + 1.0)
    target.location = (0.3, 0, maxn * TH * 0.48)
    sc.render.filepath = str(out / f"f{fi:04d}.png")
    bpy.ops.render.render(write_still=True)
print("done", NF)
