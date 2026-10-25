"""生成「插销1号 · 弯钩销」设计图（主视图 + 俯视图 + 等轴测 + 尺寸表 + 技术要求）"""
import math, sys, json
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/Users/halljoe/Documents/workbuddy/pegboard-phone-holder")
import render_lib as R

D    = "/Users/halljoe/Documents/workbuddy/pegboard-phone-holder"
OUT  = D + "/pegs"
FONT = "/System/Library/Fonts/PingFang.ttc"
def f(sz):
    try:    return ImageFont.truetype(FONT, sz)
    except: return ImageFont.load_default()

# ── 实测尺寸（手电钻16mm.3mf 后排弯钩逐层切片）───────────────
d, stem, Rb, arm = 5.00, 3.11, 2.90, 4.60
r      = d / 2
ballc  = Rb + arm            # 7.50
d_arm  = stem + Rb           # 6.01
W      = Rb + arm + d        # 12.50
H      = stem + Rb + r       # 8.51

INK, DIM, GRAY, FAINT = (26, 26, 30), (28, 92, 168), (122, 122, 130), (208, 210, 214)
SW, SH = 1800, 1210
img = Image.new("RGB", (SW, SH), (252, 252, 250))
dr  = ImageDraw.Draw(img)
dr.rectangle([24, 24, SW - 24, SH - 24], outline=INK, width=3)
dr.rectangle([40, 40, SW - 40, SH - 40], outline=INK, width=1)

S  = 40.0
OX, OY = 430.0, 150.0
P = lambda my, mz: (OX + S * my, OY - S * mz)

def arrow(tip, ang, col=DIM, s=9):
    a = math.radians(ang)
    for da in (26, -26):
        b = a + math.radians(da)
        dr.line([tip, (tip[0] + s * math.cos(b), tip[1] + s * math.sin(b))], fill=col, width=2)

def dimh(x1, x2, y, text, ext=None, col=DIM):
    dr.line([(x1, y), (x2, y)], fill=col, width=2)
    arrow((x1, y), 0, col); arrow((x2, y), 180, col)
    for x, y0 in (ext or []):
        dr.line([(x, y0), (x, y + (-6 if y0 < y else 6))], fill=col, width=1)
    tw = dr.textlength(text, font=f(22))
    dr.text(((x1 + x2) / 2 - tw / 2, y - 31), text, font=f(22), fill=col)

def dimv(y1, y2, x, text, ext=None, col=DIM):
    dr.line([(x, y1), (x, y2)], fill=col, width=2)
    arrow((x, y1), -90, col); arrow((x, y2), 90, col)
    for y, x0 in (ext or []):
        dr.line([(x0, y), (x + (-6 if x0 < x else 6), y)], fill=col, width=1)
    tw = dr.textlength(text, font=f(22))
    tim = Image.new("RGBA", (int(tw) + 8, 30), (0, 0, 0, 0))
    ImageDraw.Draw(tim).text((4, 0), text, font=f(22), fill=col)
    tim = tim.rotate(90, expand=True)
    img.paste(tim, (int(x - 15), int((y1 + y2) / 2 - tim.height / 2)), tim)

def leader(p, tp, text, tail=64, col=DIM, head=True):
    dr.line([p, tp], fill=col, width=2)
    if tail:
        dr.line([tp, (tp[0] + tail, tp[1])], fill=col, width=2)
    if head:
        ang = math.degrees(math.atan2(p[1] - tp[1], p[0] - tp[0]))
        arrow(p, ang + 180, col, 10)
    dr.text((tp[0] + 7, tp[1] - 29), text, font=f(22), fill=col)

def dash(p0, p1, col=(158, 158, 168), w=1):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    L = np.linalg.norm(p1 - p0)
    if L < 1: return
    u = (p1 - p0) / L; t = 0.0
    while t < L:
        e = min(t + 13, L)
        dr.line([tuple(p0 + u * t), tuple(p0 + u * e)], fill=col, width=w)
        t = e + 6

def cap(x, y, text, sz=24, col=(72, 74, 82)):
    tw = dr.textlength(text, font=f(sz))
    dr.text((x - tw / 2, y), text, font=f(sz), fill=col)

# ══════════════════════════════ 主视图 ══════════════════════════
out = [P(-r, 0), P(r, 0), P(r, -stem)]
cx, cz = P(Rb, -stem)
for a in np.linspace(180, 270, 20):          # 内圆角 R0.40
    th = math.radians(a)
    out.append((cx + (Rb - r) * S * math.cos(th), cz - (Rb - r) * S * math.sin(th)))
out.append(P(Rb, -(d_arm - r)))
out.append(P(ballc, -(d_arm - r)))
bx, bz = P(ballc, -d_arm)
for a in np.linspace(-90, 90, 32):           # 臂端球头
    th = math.radians(a)
    out.append((bx + r * S * math.cos(th), bz + r * S * math.sin(th)))
out.append(P(Rb, -(d_arm + r)))
for a in np.linspace(270, 180, 32):          # 外圆弧 R5.40
    th = math.radians(a)
    out.append((cx + (Rb + r) * S * math.cos(th), cz - (Rb + r) * S * math.sin(th)))

mask = Image.new("L", (SW, SH), 0)
ImageDraw.Draw(mask).polygon(out, fill=255)
img.paste(Image.new("RGB", (SW, SH), (233, 235, 239)), (0, 0), mask)
dr = ImageDraw.Draw(img)
dr.line(out + [out[0]], fill=INK, width=3, joint="curve")

# 中心线
dash((OX, OY - 118), (OX, OY + S * (d_arm + r) + 22))
dash((OX - 104, OY + S * d_arm), (980, OY + S * d_arm))
# 板面基准线（延伸到右侧尺寸区）
dr.line([(268, OY), (1064, OY)], fill=(64, 142, 208), width=3)
dr.text((174, OY - 13), "板面", font=f(21), fill=(40, 120, 190))

# 尺寸
dimv(OY, OY + S * stem, 262, "3.11", ext=[(OY, 330), (OY + S * stem, 330)])
dimv(OY, OY + S * d_arm, 992, "6.01", ext=[(OY, 976), (OY + S * d_arm, 976)])
dimv(OY, OY + S * H, 1058, "8.51", ext=[(OY, 992), (OY + S * H, P(ballc, 0)[0])])
dimh(OX, P(ballc, 0)[0], OY - 90, "7.50",
     ext=[(OX, OY - 6), (P(ballc, 0)[0], OY + S * (d_arm - r) - 4)])
dimh(P(Rb, 0)[0], P(ballc, 0)[0], OY + S * (d_arm - r) - 26, "4.60",
     ext=[(P(Rb, 0)[0], OY + S * (d_arm - r) - 24), (P(ballc, 0)[0], OY + S * (d_arm - r) - 4)])
dimh(P(-r, 0)[0], P(W - r, 0)[0], OY + S * H + 50, "12.50",
     ext=[(P(-r, 0)[0], OY + S * H + 4), (P(W - r, 0)[0], OY + S * H + 4)])

# 半径引注（全部引到形体外侧）
leader((546 - 153, 274 + 153), (238, 404), "R2.90  弯头", 0)
leader((546 + 11.3, 274 + 11.3), (644, 194), "R0.40  内圆角", 0)
cap(OX + S * (ballc - r) / 2 - 20, OY + S * H + 84, "主视图  1:1")

# ══════════════════════════════ 俯视图 ══════════════════════════
ty = 712.0
xc_l, xc_r = OX, P(ballc, 0)[0]             # 430 / 730
xl, xr = xc_l - r * S, xc_r + r * S         # 330 / 830
top = [(xc_l, ty - r * S)]
top += [(xc_r, ty - r * S)]                                   # 上沿
for a in np.linspace(-90, 90, 30):                            # 右端球头
    th = math.radians(a)
    top.append((xc_r + r * S * math.cos(th), ty + r * S * math.sin(th)))
top += [(xc_l, ty + r * S)]                                   # 下沿
for a in np.linspace(90, 270, 30):                            # 左端直柱截面
    th = math.radians(a)
    top.append((xc_l + r * S * math.cos(th), ty + r * S * math.sin(th)))
mask2 = Image.new("L", (SW, SH), 0)
ImageDraw.Draw(mask2).polygon(top, fill=255)
img.paste(Image.new("RGB", (SW, SH), (233, 235, 239)), (0, 0), mask2)
dr = ImageDraw.Draw(img)
dr.line(top + [top[0]], fill=INK, width=3, joint="curve")
dash((xl - 56, ty), (xr + 56, ty))
dash((xl, ty - r * S - 34), (xl, ty + r * S + 28))
dimv(ty - r * S, ty + r * S, xl - 86, "Ø5.00", ext=[(ty - r * S, xl), (ty + r * S, xl)])
cap((xl + xr) / 2, ty + r * S + 34, "俯视图  1:1")

# ══════════════════════════════ 等轴测 ══════════════════════════
m = trimesh.load(D + "/插销1号_弯钩销.stl")
V = np.asarray(m.vertices, float); F = np.asarray(m.faces, np.int64)
V = V - np.array([0, 0, r])
V = np.stack([-V[:, 2], V[:, 1], V[:, 0]], axis=1)   # → 绘图姿态
V = V - np.array([0, W / 2 - r, -H / 2])
cam = R.Cam([0, 0, 0], az=34, el=24, dist=46, fov=27, W=600, H=470)
iso = R.render([(V, F, (0.70, 0.77, 0.88))], cam, bg_img=None, shadow=False, auto_flip=False)
iso_img = Image.fromarray((np.clip(iso, 0, 1) * 255).astype(np.uint8))
img.paste(iso_img, (1130, 78))
dr = ImageDraw.Draw(img)
dr.rectangle([1130, 78, 1130 + iso_img.width, 78 + iso_img.height], outline=FAINT, width=2)
cap(1130 + iso_img.width / 2, 78 + iso_img.height + 10, "等轴测", 22)

# ══════════════════════════════ 尺寸表 ══════════════════════════
TX, TY = 1090, 586
rows = [("管径",            "Ø5.00",  "x 向恒等，实测"),
        ("直柱段长",         "3.11",   "板面 → 弯头切点"),
        ("弯头中心线半径 R",   "2.90",   "扫掠 90°"),
        ("弯头内圆角",        "0.40",   "R − d/2"),
        ("板面 → 短臂轴线",   "6.01",   "= 3.11 + 2.90"),
        ("短臂直段",         "4.60",   "弯头切点 → 球心"),
        ("臂端球心距轴线",     "7.50",   "= 2.90 + 4.60"),
        ("总深",            "8.51",   "板面 → 最低点"),
        ("总宽",            "12.50",  "= 2.90 + 4.60 + 5.00"),
        ("短臂上表面距板面",   "3.51",   "可用板厚上限"),
        ("头部包络 R+d",     "7.90",   "＞孔径 6.00"),
        ("理论体积",         "273.5",  "mm³ · 实测件 269.0")]
cw = [262, 116, 264]
RH, HH = 27, 32
TB = TY + HH + RH * len(rows)
dr.rectangle([TX, TY, TX + sum(cw), TB], outline=INK, width=2)
dr.rectangle([TX, TY, TX + sum(cw), TY + HH], fill=(238, 240, 244), outline=INK, width=2)
for i, t in enumerate(["项目", "数值", "说明"]):
    dr.text((TX + 10 + sum(cw[:i]), TY + 4), t, font=f(20), fill=INK)
for i, row in enumerate(rows):
    y = TY + HH + RH * i
    if i: dr.line([(TX, y), (TX + sum(cw), y)], fill=FAINT, width=1)
    for j, c in enumerate(row):
        dr.text((TX + 10 + sum(cw[:j]), y + 3), c, font=f(18), fill=(58, 60, 68))
for x in [TX + cw[0], TX + cw[0] + cw[1]]:
    dr.line([(x, TY), (x, TB)], fill=INK, width=1)
dr.text((TX + 10, TB + 8), "单位：mm（体积 mm³）  ·  1:1 按实测输出", font=f(17), fill=GRAY)

# ══════════════════════════════ 技术要求 ══════════════════════════
NX, NY = 96, 890
dr.text((NX, NY - 42), "技术要求", font=f(25), fill=INK)
notes = [
    "1. 材质 PLA / PETG，填充 100%（弯头根部受弯，别用低填充），外壁 4 道。",
    "2. 打印姿态：弯钩平面平躺于平台（SCAD 中 orient=\"print\"），全程免支撑；",
    "    底面为线接触，务必开 5mm brim。层高 0.12–0.16，弯头段降速至 60%。",
    "3. 弯头内圆角仅 R0.40，是全件最弱处；若首件断裂，把 R 由 2.90 放大到 3.30",
    "    （内圆角 R0.80，总深不变，短臂相应缩短 0.40）。",
    "4. 安装：头部包络 R+d = 7.90 ＞ 孔径 6.00，不能像插销 2 号那样直插；须从板",
    "    边缘或将某个孔扩成长槽滑入，钩臂落到板背面后下拉自锁。",
    "5. 适配板厚：短臂上表面距板面仅 3.51，故洞洞板厚度须 ≤ 3.2mm（留 0.3 余量）。",
    "6. 与插销 2 号成组：2 号过孔卡环定位、1 号钩住背面防前翻，建议 2 号 4 件 + 1 号 2 件。",
]
for i, t in enumerate(notes):
    dr.text((NX, NY + i * 30), t, font=f(18.5), fill=(58, 60, 68))

# ══════════════════════════════ 标题栏 ══════════════════════════
BX, BY, BW, BH = 1090, 972, 642, 172
dr.rectangle([BX, BY, BX + BW, BY + BH], outline=INK, width=2)
dr.line([(BX, BY + 54), (BX + BW, BY + 54)], fill=INK, width=2)
dr.text((BX + 16, BY + 10), "插销 1 号 · 弯钩销", font=f(29), fill=INK)
dr.text((BX + 16, BY + 60), "J-Hook Peg   /   PEG-01", font=f(18), fill=GRAY)
dr.line([(BX, BY + 90), (BX + BW, BY + 90)], fill=FAINT, width=1)
xx = BX + 16
for k, v in [("比例", "1:1"), ("数量", "2 件"), ("材质", "PLA/PETG"), ("日期", "2026-10-25"), ("版本", "A")]:
    dr.text((xx, BY + 100), k, font=f(16), fill=GRAY)
    dr.text((xx, BY + 120), v, font=f(20), fill=INK)
    xx += 124
dr.text((BX + 16, BY + 148), "数据来源：手电钻16mm.3mf 后排弯钩，逐层切片实测（偏差 ≤ 0.06mm）",
        font=f(16), fill=(96, 98, 106))

img.save(OUT + "/插销1号_设计图.png")
print("saved", OUT + "/插销1号_设计图.png", img.size)
