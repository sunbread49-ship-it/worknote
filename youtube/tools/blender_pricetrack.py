"""주가 롤러코스터 3D (Blender · Cycles CPU) — 실제 주가 곡선을 3D 레일로 만들고 카메라가 그 위를 달린다 (EP019 펄어비스)
  /home/user/bpyenv/bin/python tools/blender_pricetrack.py <data.json> <out_dir> [frames]
  data: {"prices": [..일별 종가..], "flags": [{"i": 인덱스, "color": "green|red", "h": 높이}], "ymin": 0}
  레일 = 진초록 리본 + 흰 가장자리 · 깃발 = 기둥 + 천 · 카메라는 레일을 따라 조금 뒤 · 위에서 앞을 본다 (끝 30프레임은 옆으로 빠져 전체 조망)
"""
import json, math, os, sys
from pathlib import Path
import bpy

D = json.load(open(sys.argv[1]))
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
NF = int(sys.argv[3]) if len(sys.argv) > 3 else 180
ONLY = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]
P = D["prices"]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.view_settings.view_transform = "Standard"


def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, hexc, metal=0.0, rough=0.4, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(hexc), 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(hexc), 1); b.inputs["Emission Strength"].default_value = emit
    return m

GREEN, RED, WHITE, POLE = mat("g", "01422B", 0.2, 0.3), mat("r", "A3161A", 0, 0.4, 0.6), mat("w", "FBFBF9", 0, 0.5, 0.4), mat("p", "D0D4D2", 0.8, 0.3)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (*lin("1A1F1E"), 1)
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -0.05)); bpy.context.object.data.materials.append(mat("floor", "0E1211", 0, 0.9))
bpy.ops.object.light_add(type="SUN", location=(0, 0, 30)); sun = bpy.context.object; sun.data.energy = 3.2; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
bpy.ops.object.light_add(type="AREA", location=(0, -20, 15)); fill = bpy.context.object; fill.data.energy = 3000; fill.data.size = 30

# 일별 잡음을 줄여 부드러운 레일: 5일 이동평균 → 3일마다 한 점 → 사이를 4등분 보간 (캣멀-롬)
sm = [sum(P[max(0, i - 2):i + 3]) / len(P[max(0, i - 2):i + 3]) for i in range(len(P))]
key = sm[::3] + ([sm[-1]] if (len(sm) - 1) % 3 else [])
FL = {fl["i"] // 3: fl for fl in D.get("flags", [])}


def cr(p0, p1, p2, p3, t):
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)

P = []
for k in range(len(key) - 1):
    a, b, c_, d = key[max(0, k - 1)], key[k], key[k + 1], key[min(len(key) - 1, k + 2)]
    for j in range(4):
        P.append(cr(a, b, c_, d, j / 4))
P.append(key[-1])
for fl in D.get("flags", []):
    fl["i"] = min(len(P) - 1, (fl["i"] // 3) * 4)
n = len(P)
LEN = 160.0
lo, hi = D.get("ymin", min(P) * 0.9), max(P)
X = [LEN * i / (n - 1) for i in range(n)]
Z = [1.0 + 12.0 * (p - lo) / (hi - lo) for p in P]


def ribbon(z_off, half, m, name, thick=0.18):
    """레일: 곡선을 따라 폭 half*2 판 + 두께 (세로로 깎인 기둥 없이 떠 있는 리본)"""
    me = bpy.data.meshes.new(name)
    vs, fs = [], []
    for i in range(n):
        for dy in (-half, half):
            vs.append((X[i], dy, Z[i] + z_off)); vs.append((X[i], dy, Z[i] + z_off - thick))
    for i in range(n - 1):
        a = i * 4; b = a + 4
        fs += [(a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1), (a, a + 1, b + 1, b), (a + 2, b + 2, b + 3, a + 3)]
    me.from_pydata(vs, [], fs); me.update()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); ob.data.materials.append(m)
    return ob

ribbon(0.0, 1.0, GREEN, "rail")
for side in (-1, 1):   # 양쪽 흰 난간 (가는 띠)
    o = ribbon(0.12, 0.06, WHITE, f"edge{side}", 0.12); o.location.y = side * 0.97
for i in range(0, n, 8):   # 받침 기둥 (가늘게)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=Z[i], location=(X[i], 0, Z[i] / 2))
    bpy.context.object.data.materials.append(POLE)
for fl in D.get("flags", []):   # 깃발
    i, m = fl["i"], (GREEN if fl["color"] == "green" else RED)
    h = fl.get("h", 4.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=h, location=(X[i], -1.3, Z[i] + h / 2)); bpy.context.object.data.materials.append(POLE)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(X[i] + 0.9, -1.3, Z[i] + h - 0.6), rotation=(math.radians(90), 0, 0))
    f = bpy.context.object; f.scale = (1.8, 1.1, 1); f.data.materials.append(m)

bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 30
bpy.ops.object.empty_add(); tgt = bpy.context.object
c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"


def at(u):
    x = u * (n - 1); i = min(int(x), n - 2); fr = x - i
    return X[i] + (X[i + 1] - X[i]) * fr, Z[i] + (Z[i + 1] - Z[i]) * fr

RIDE = NF - 40
for fi in range(NF):
    if ONLY and fi not in ONLY:
        continue
    if fi < RIDE:   # 레일 위를 달림 (조금 뒤 · 위에서 앞을 봄)
        u = fi / (RIDE - 1)
        x, z = at(u)
        xa, za = at(min(1.0, u + 0.08))
        cam.location = (x - 10.0, -7.5, z + 5.0)
        tgt.location = (xa, 0, za + 0.5)
    else:   # 옆으로 빠져 전체 조망
        k = (fi - RIDE) / 39
        k = k * k * (3 - 2 * k)
        x, z = at(1.0)
        cam.location = (x - 10.0 + (LEN / 2 - x + 10.0) * k, -7.5 - 72 * k, z + 5.0 + 13 * k)
        tgt.location = (X[-1] + (LEN / 2 - X[-1]) * k, 0, z + 0.5 + (6 - z) * k)
    sc.render.filepath = str(out / f"f{fi:04d}.png")
    bpy.ops.render.render(write_still=True)
print("done", NF)
