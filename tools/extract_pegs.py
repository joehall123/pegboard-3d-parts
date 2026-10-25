"""从参考件 手电钻16mm.3mf 中提取挂销，输出独立 STL + 尺寸剖面。"""
import os, json
import numpy as np
import trimesh

OUT = "/Users/halljoe/Documents/workbuddy/pegboard-phone-holder/pegs"
os.makedirs(OUT, exist_ok=True)

V = np.load("/tmp/mf3/V.npy")
F = np.load("/tmp/mf3/F.npy")
mesh = trimesh.Trimesh(vertices=V, faces=F, process=False)
trimesh.repair.fix_normals(mesh)

print("整体 bbox", mesh.bounds.round(3).tolist(), "| watertight",
      mesh.is_watertight, "| vol", round(mesh.volume, 1), "mm3")

PLATE_Z = -28.452      # 实测板底面
CUT_Z   = -28.60       # 切割面：板面下 0.15mm，避免刮到板料
PEG_Y   = -26.0
XS      = [-64.0, -32.0, 0.0, 32.0, 64.0]

pegs = []
for i, x0 in enumerate(XS):
    box = trimesh.creation.box(extents=(12.0, 14.0, 11.0))
    box.apply_translation([x0, PEG_Y, CUT_Z - 5.5])
    p = trimesh.boolean.intersection([mesh, box], engine="manifold")
    p.apply_translation([-x0, -PEG_Y, -CUT_Z])   # 基面归零，销轴 = -Z
    p.export(os.path.join(OUT, f"peg_{i+1}.stl"))
    lo, hi = p.bounds
    print(f"peg_{i+1}: tris={len(p.faces):5d} watertight={p.is_watertight} "
          f"vol={p.volume:6.1f}  x[{lo[0]:.2f},{hi[0]:.2f}] "
          f"y[{lo[1]:.2f},{hi[1]:.2f}] z[{lo[2]:.2f},{hi[2]:.2f}]")
    pegs.append(p)

# 5 个销排一行导出一个 STL（备件/对位件）
pieces = []
for i, p in enumerate(pegs):
    q = p.copy(); q.apply_translation([i * 9.0 - 18.0, 0, 0]); pieces.append(q)
row = trimesh.util.concatenate(pieces)
row.export(os.path.join(OUT, "pegs_x5.stl"))
print("pegs_x5: tris", len(row.faces), "watertight", row.is_watertight)

# ── 半径剖面（相对真实板面 -28.452）──────────────────────────
p = pegs[2]
rows = []
for d in np.arange(0.05, 8.0, 0.05):
    z = -(d - 0.148)        # 基面已归零 = 板面下 0.148
    sec = p.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        continue
    pts = np.vstack(sec.discrete)
    r = np.linalg.norm(pts[:, :2], axis=1)
    rows.append((round(float(d), 2), round(float(r.max() * 2), 3)))

json.dump(rows, open(os.path.join(OUT, "profile.json"), "w"))
arr = np.array(rows)
print("\n峰值直径 %.3f mm @ 距板面 %.2f mm" % (arr[:, 1].max(), arr[arr[:, 1].argmax(), 0]))
print("销身直径（1.2-3.2mm）平均 %.3f" % arr[(arr[:, 0] >= 1.2) & (arr[:, 0] <= 3.2), 1].mean())
print("末梢最短处 %.3f @ %.2f" % (arr[-1, 1], arr[-1, 0]))
