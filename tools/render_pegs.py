"""挂销预览：5 销排布图 + 单销侧视标注图 + 直径剖面曲线"""
import math, json, sys
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/Users/halljoe/Documents/workbuddy/pegboard-phone-holder")
import render_lib as R

D = "/Users/halljoe/Documents/workbuddy/pegboard-phone-holder"
OUT = D + "/pegs"
FONT = "/System/Library/Fonts/PingFang.ttc"
def f(sz):
    try:    return ImageFont.truetype(FONT, sz)
    except: return ImageFont.load_default()

COL = (0.99, 1.00, 1.00)

# ── 1. 五个挂销并排站立 ─────────────────────────────────────
m = trimesh.load(OUT + "/pegs_x5.stl")
V = np.asarray(m.vertices, float); F = np.asarray(m.faces, np.int64)
V = V * np.array([1, -1, -1])            # 销轴 -Z → +Z（尖端朝上）
V[:, 2] -= V[:, 2].min()
cam = R.Cam([0, 0, 4.6], az=12, el=19, dist=54, fov=32, W=980, H=520)
img = R.render([(V, F, COL)], cam, bg_img=None, shadow=True, auto_flip=False)
R.save(img, OUT + "/peg_row.png", ss=1)

# ── 2. 单销侧视：轴 → 屏幕水平（注意本渲染器屏幕右方 = -X）──
p = trimesh.load(OUT + "/peg_3.stl")
P = np.asarray(p.vertices, float); Fp = np.asarray(p.faces, np.int64)
U = -P[:, 2]                     # u = 距基面距离，0..7.86
LEN = float(U.max())
PPMM = 58.0                      # 像素/mm
Vp = np.stack([LEN / 2 + P[:, 2], P[:, 1], -P[:, 0]], axis=1)  # det=+1   # 基面在左，尖端在右
DIST = 240.0
foc = DIST * PPMM
W_, H_ = 1240, 820
fov = math.degrees(2 * math.atan(0.5 * H_ / foc))
cam2 = R.Cam([0, 0, 0], az=0, el=1.5, dist=DIST, fov=fov, W=W_, H=H_)
img2 = R.render([(Vp, Fp, COL)], cam2, bg_img=None, shadow=False, auto_flip=False)
base = Image.fromarray((np.clip(img2, 0, 1) * 255).astype(np.uint8))
dr = ImageDraw.Draw(base)

def px(u, z=0.0):
    """u=距基面距离, z=截面高度 → 像素"""
    sx, sy, _ = cam2.project(np.array([[LEN / 2 - u, 0.0, z]], float))
    return float(sx[0]), float(sy[0])

GRAY, ORANGE, BLUE = (58, 60, 68), (200, 112, 8), (42, 100, 186)
Y0 = H_ / 2.0

# 总长尺寸线
A, B = px(0, 4.55), px(LEN, 4.55)
dr.line([A, B], fill=GRAY, width=2)
for q in (A, B):
    dr.line([(q[0], q[1] - 12), (q[0], q[1] + 12)], fill=GRAY, width=3)
dr.text(((A[0] + B[0]) / 2 - 44, A[1] - 46), f"{LEN:.2f} mm", font=f(24), fill=GRAY)

# 板面竖线
pt, pb = px(0, 3.5), px(0, -3.9)
dr.line([pt, pb], fill=BLUE, width=3)
dr.text((pt[0] - 78, Y0 + 4), "板面", font=f(20), fill=BLUE)

# 三条引线（全部向下引出，避免互相压字）
def callout(u, ztop, dx, label, sub, color, zlab=None):
    a = px(u, ztop)
    yb = Y0 + 3.35 * PPMM + 44
    dr.line([a, (a[0] + dx, yb)], fill=color, width=2)
    tx = a[0] + dx - (len(label) * 11)
    dr.text((tx, yb + 8), label, font=f(21), fill=color)
    if sub:
        dr.text((tx + 6, yb + 38), sub, font=f(17), fill=color)

callout(1.75, -3.20, -46, "销身", "Ø5.50 等径", GRAY)
callout(3.95, -3.24, 0, "卡环", "Ø5.99", ORANGE)
callout(7.05, -2.80, 56, "球头收尾", "Ø5.16 → Ø1.49", GRAY)

# 卡环处水平虚线，标出凸起


dr.text((36, 22), "参考件挂销 · 侧视尺寸（单件 1:1 可独立打印）", font=f(27), fill=(34, 34, 34))
dr.text((36, 62), "5 件几何完全一致 · 每件体积 173.3 mm³ · 水密实体 · 轴长 8.01mm（含根部圆角）",
        font=f(18), fill=(112, 112, 120))
base.save(OUT + "/peg_profile.png")
print("saved peg_profile.png", base.size)

# ── 3. 直径-距板面 曲线 ─────────────────────────────────────
rows = json.load(open(OUT + "/profile.json"))
a = np.array(rows); d, dia = a[:, 0], a[:, 1]
CW, CH = 1150, 620
ML, MR, MT, MB = 100, 60, 78, 82
cv = Image.new("RGB", (CW, CH), (250, 250, 248)); dv = ImageDraw.Draw(cv)
xmax, ymax = 8.4, 7.2
X = lambda v: ML + (v / xmax) * (CW - ML - MR)
Y = lambda v: CH - MB - (v / ymax) * (CH - MT - MB)
for g in np.arange(0, 8.5, 1.0):
    dv.line([(X(g), Y(0)), (X(g), Y(ymax))], fill=(230, 230, 226), width=1)
    dv.text((X(g) - 6, CH - MB + 14), f"{g:.0f}", font=f(18), fill=(125, 125, 125))
for g in np.arange(0, 7.5, 1.0):
    dv.line([(ML, Y(g)), (X(xmax), Y(g))], fill=(230, 230, 226), width=1)
    dv.text((ML - 50, Y(g) - 11), f"{g:.0f}", font=f(18), fill=(125, 125, 125))
dv.line([(ML, Y(0)), (X(xmax), Y(0))], fill=(95, 95, 95), width=2)
dv.line([(ML, Y(0)), (ML, Y(ymax))], fill=(95, 95, 95), width=2)
dv.line([(ML, Y(6.0)), (X(xmax), Y(6.0))], fill=(140, 195, 145), width=2)
dv.text((X(6.45), Y(6.0) - 28), "洞洞板孔径 6.00", font=f(19), fill=(46, 140, 58))
dv.line([(X(u_), Y(v_)) for u_, v_ in zip(d, dia)], fill=(45, 95, 195), width=5, joint="curve")
sel = (d >= 3.3) & (d <= 4.7)
dd, vv = d[sel][dia[sel].argmax()], dia[sel].max()
dv.ellipse([X(dd) - 8, Y(vv) - 8, X(dd) + 8, Y(vv) + 8], fill=(228, 122, 18))
dv.line([(X(dd), Y(vv)), (X(dd) - 40, Y(vv) + 66)], fill=(196, 108, 8), width=2)
dv.text((X(dd) - 262, Y(vv) + 22), f"卡环峰 Ø{vv:.2f}", font=f(21), fill=(196, 108, 8))
dv.text((X(dd) - 262, Y(vv) + 50), f"距板面 {dd:.2f} mm", font=f(18), fill=(196, 108, 8))
dv.text((X(dd) - 262, Y(vv) + 74), "比销身单边凸出 0.25", font=f(17), fill=(196, 108, 8))
dv.text((112, 20), "参考件挂销 · 直径随距板面的变化", font=f(27), fill=(34, 34, 34))
dv.text((CW // 2 - 54, CH - 44), "距板面 (mm)", font=f(20), fill=(95, 95, 95))
dv.text((ML - 92, MT + 4), "直径(mm)", font=f(19), fill=(95, 95, 95))
dv.text((X(1.15), Y(3.3)), "销身 Ø5.50 等径", font=f(18), fill=(80, 82, 95))
dv.text((X(5.35), Y(3.5)), "收腰 Ø5.16", font=f(18), fill=(80, 82, 95))
dv.text((X(6.45), Y(1.5)), "球头 Ø5.16→1.49", font=f(18), fill=(80, 82, 95))
dv.text((X(0.20), Y(6.95)), "根部圆角 Ø6.46", font=f(17), fill=(80, 82, 95))
cv.save(OUT + "/profile_chart.png")
print("saved profile_chart.png", cv.size)
