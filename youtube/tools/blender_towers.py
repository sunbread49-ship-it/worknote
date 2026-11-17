"""동전 탑 경주 3D (Blender · Cycles CPU) — 여러 탑이 날짜를 따라 오르내림 (EP018: 반도체 vs SOXL 몰빵 vs SOXL 반 + 현금)
  /home/user/bpyenv/bin/python tools/blender_towers.py <data.json> <out_dir> [frames]
  data: {"unit": 50, "towers": [{"mat": "silver|red|green", "x": -2.4}], "rows": [{"date": "2026-06-22", "v": [1000, 1000, 1000]}]}
  줄어들 땐 맨 위 동전이 옆으로 튕겨 떨어짐 · 끝 25프레임은 정지 · 프레임 PNG → 라벨은 coins_compose 류로 합성
"""
import json, math, os, sys
from pathlib import Path
import bpy

D = json.load(open(sys.argv[1]))
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
NF = int(sys.argv[3]) if len(sys.argv) > 3 else 165
ONLY = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]
UNIT, TW, ROWS = D["unit"], D["towers"], D["rows"]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 540


def mat(name, color, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    return m

MATS = {"silver": mat("silver", (0.82, 0.84, 0.88), 1.0, 0.22),
        "red": mat("red", (0.36, 0.009, 0.012), 0.55, 0.28),       # 딥레드 #A3161A (선형)
        "green": mat("green", (0.0, 0.055, 0.024), 0.55, 0.28)}    # 진초록 #01422B (선형)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.5, depth=0.12)
proto = bpy.context.object; proto.hide_render = True; proto.hide_viewport = True
bpy.ops.object.shade_smooth()
TH = 0.13
OBS = []


def coin(x, y, z, m, rot=(0, 0, 0)):
    ob = proto.copy(); ob.data = proto.data.copy(); ob.data.materials.clear(); ob.data.materials.append(m)
    ob.location = (x, y, z); ob.rotation_euler = rot; ob.hide_render = False; ob.hide_viewport = False
    sc.collection.objects.link(ob); OBS.append(ob)

bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.06))
bpy.context.object.data.materials.append(mat("floor", (0.03, 0.032, 0.032), 0.0, 0.3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.008, 0.009, 0.009, 1)
bpy.ops.object.light_add(type="AREA", location=(0, -4, 7)); L = bpy.context.object; L.data.energy = 1500; L.data.size = 5; L.rotation_euler = (math.radians(30), 0, 0)
bpy.ops.object.light_add(type="SPOT", location=(-5, 2, 5)); S = bpy.context.object; S.data.energy = 900; S.rotation_euler = (math.radians(-45), math.radians(-40), 0)
bpy.ops.object.light_add(type="AREA", location=(5, -3, 3)); R = bpy.context.object; R.data.energy = 400; R.data.size = 3; R.rotation_euler = (math.radians(60), math.radians(50), 0)
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 44
bpy.ops.object.empty_add(location=(0, 0, 1.0)); target = bpy.context.object
tc = cam.constraints.new("TRACK_TO"); tc.target = target; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

maxn = max(max(r["v"]) for r in ROWS) / UNIT
hold = 25
prev = None
falls = []   # (tower, level, 시작 프레임)
for fi in range(NF):
    u = min(1.0, fi / (NF - hold))
    pos = u * (len(ROWS) - 1)
    i0 = int(pos); fr = pos - i0
    r0, r1 = ROWS[i0], ROWS[min(i0 + 1, len(ROWS) - 1)]
    ns = [(a + (b - a) * fr) / UNIT for a, b in zip(r0["v"], r1["v"])]
    if u >= 1:
        ns = [round(n) for n in ns]
    if prev is not None:   # 줄어든 만큼 떨어지는 동전 등록
        for t, (a, b) in enumerate(zip(prev, ns)):
            for lv in range(int(b), int(a)):
                falls.append((t, lv, fi))
    prev = ns
    if ONLY and fi not in ONLY:
        continue
    for ob in OBS:
        bpy.data.objects.remove(ob, do_unlink=True)
    OBS.clear()
    for t, (tw, n) in enumerate(zip(TW, ns)):
        x, m = tw["x"], MATS[tw["mat"]]
        full = int(n); part = n - full
        for k in range(full):
            coin(x + 0.03 * math.sin(k * 2.3 + x), 0.02 * math.cos(k * 1.7), 0.06 + k * TH, m, (0, 0, k * 0.4))
        if part > 0.05:
            coin(x, 0, 0.06 + full * TH + (1 - part) * 2.0, m, (0, 0, full * 0.4))
    for t, lv, f0 in falls:   # 떨어진 동전: 12프레임 동안 옆으로 튕겨 바닥으로
        a = fi - f0
        if 0 <= a < 12:
            s = a / 12
            x = TW[t]["x"] + (0.5 + lv % 3 * 0.25) * s * (1 if lv % 2 else -1)
            rx = 2 * math.pi * s   # 한 바퀴 돌고 납작하게 착지
            z = max(0.06 + 0.5 * abs(math.sin(rx)), 0.06 + lv * TH + 0.6 * s - 9.0 * s * s * (0.3 + lv * TH * 0.12))
            coin(x, -0.6 * s, z, MATS[TW[t]["mat"]], (rx, 0, lv * 0.4))
    ang = math.radians(-10 + 8 * u)
    rad = 9.6 - 0.8 * u
    cam.location = (rad * math.sin(ang), -rad * math.cos(ang), 2.4 + maxn * TH * 0.55)
    target.location = (0.1, 0, maxn * TH * 0.45)
    sc.render.filepath = str(out / f"f{fi:04d}.png")
    bpy.ops.render.render(write_still=True)
print("done", NF)
