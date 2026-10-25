#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简易 z-buffer 渲染器：用于出预览图（洞洞板背景 + 投影 + 平面着色）"""
import sys, math, numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFilter

LIGHT = np.array([0.45, 0.80, 0.40]); LIGHT /= np.linalg.norm(LIGHT)


def load(path, clip_y=None):
    m = trimesh.load(path)
    V = np.asarray(m.vertices, dtype=np.float64)
    F = np.asarray(m.faces, dtype=np.int64)
    if clip_y is not None:
        V, F = clip_plane(V, F, clip_y)
    return V, F


def clip_plane(V, F, y0):
    """把网格裁剪到 y>=y0"""
    out_tris = []
    for f in F:
        poly = [V[i] for i in f]
        new = []
        for i in range(3):
            a, b = poly[i], poly[(i + 1) % 3]
            da, db = a[1] - y0, b[1] - y0
            if da >= 0:
                new.append(a)
            if (da >= 0) != (db >= 0):
                t = da / (da - db)
                new.append(a + t * (b - a))
        if len(new) >= 3:
            for k in range(1, len(new) - 1):
                out_tris.append([new[0], new[k], new[k + 1]])
    if not out_tris:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
    tris = np.array(out_tris)                      # (n,3,3)
    V2 = tris.reshape(-1, 3)
    F2 = np.arange(len(V2)).reshape(-1, 3)
    return V2, F2


class Cam:
    def __init__(self, target, az, el, dist, fov, W, H):
        self.W, self.H, self.f = W, H, 0.5 * H / math.tan(math.radians(fov) / 2)
        az, el = math.radians(az), math.radians(el)
        d = np.array([math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)])
        self.eye = np.array(target, float) + d * dist
        self.dir = -d
        up = np.array([0, 0, 1.0])
        self.right = np.cross(self.dir, up); self.right /= np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.dir)

    def project(self, P):
        q = P - self.eye
        xc, yc, zc = q @ self.right, q @ self.up, q @ self.dir
        zc = np.maximum(zc, 1e-6)
        return (self.W / 2 + self.f * xc / zc,
                self.H / 2 - self.f * yc / zc, zc)


def render(meshes, cam, bg_img=None, shadow=True, auto_flip=True):
    W, H = cam.W, cam.H
    if bg_img is None:
        bg = np.ones((H, W, 3)) * np.array([0.97, 0.97, 0.97])
        grad = np.linspace(0.0, 0.06, H)[:, None, None]
        bg -= grad
    else:
        bg = bg_img.astype(np.float64)
    img = bg.copy()
    zb = np.full((H, W), np.inf)

    # ---- 阴影（投影到 y=0 平面，先算 mask 再一次性叠加） ----
    if shadow:
        mask = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(mask)
        for V, F, col in meshes:
            P = V.copy()
            t = P[:, 1] / LIGHT[1]
            P[:, 0] -= t * LIGHT[0]; P[:, 1] = 0.0; P[:, 2] -= t * LIGHT[2]
            sx, sy, zc = cam.project(P)
            for f in F:
                if zc[f].min() <= 0:
                    continue
                dr.polygon([(sx[i], sy[i]) for i in f], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2.2))
        mk = np.asarray(mask, dtype=np.float64)[..., None] / 255.0
        img = img * (1 - 0.26 * mk) + np.array([0.42, 0.42, 0.45]) * 0.26 * mk

    # ---- 实体 ----
    for V, F, col in meshes:
        sx, sy, zc = cam.project(V)
        tri = V[F]                                   # (n,3,3)
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1); ln[ln < 1e-12] = 1
        n = n / ln[:, None]
        # 双面法向朝向相机
        cen = tri.mean(axis=1)
        if auto_flip and np.sum(np.einsum("ij,ij->i", n, cen - cam.eye)) < 0:
            n = -n
        diff = np.clip(n @ LIGHT, 0, 1)
        sky = 0.5 + 0.5 * n[:, 2]
        base = np.array(col)
        shade = (0.37 + 0.58 * diff + 0.09 * sky)[:, None]
        fc = np.clip(base[None, :] * shade, 0, 1)
        spec = (np.clip(n @ (LIGHT * 0 + np.array([0, 0, 1.0])), 0, 1) ** 40)[:, None] * 0.05
        fc = np.clip(fc + spec, 0, 1)

        for k, f in enumerate(F):
            x0, x1 = int(np.floor(min(sx[f]))) - 1, int(np.ceil(max(sx[f]))) + 1
            y0, y1 = int(np.floor(min(sy[f]))) - 1, int(np.ceil(max(sy[f]))) + 1
            x0, x1 = max(x0, 0), min(x1, W - 1); y0, y1 = max(y0, 0), min(y1, H - 1)
            if x0 > x1 or y0 > y1:
                continue
            (ax, ay), (bx, by), (cx_, cy_) = [(sx[i], sy[i]) for i in f]
            xs = np.arange(x0, x1 + 1) + 0.5
            ys = np.arange(y0, y1 + 1) + 0.5
            X, Y = np.meshgrid(xs, ys)
            d = (by - cy_) * (ax - cx_) + (cx_ - bx) * (ay - cy_)
            if abs(d) < 1e-9:
                continue
            l1 = ((by - cy_) * (X - cx_) + (cx_ - bx) * (Y - cy_)) / d
            l2 = ((cy_ - ay) * (X - cx_) + (ax - cx_) * (Y - cy_)) / d
            l3 = 1 - l1 - l2
            m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not m.any():
                continue
            z = l1 * zc[f[0]] + l2 * zc[f[1]] + l3 * zc[f[2]]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            upd = m & (z < sub)
            sub[upd] = z[upd]
            img[y0:y1 + 1, x0:x1 + 1][upd] = fc[k]
    return img


def pegboard_bg(cam, pitch=16.0, hole_r=3.0, ext=420.0, base=(0.90, 0.90, 0.88)):
    """洞洞板墙面：平面 + 预先画的孔（在 y=0 平面）"""
    W, H = cam.W, cam.H
    img = np.ones((H, W, 3))
    P = np.array([[-ext, 0, -ext], [ext, 0, -ext], [ext, 0, ext], [-ext, 0, ext]], float)
    sx, sy, _ = cam.project(P)
    img[:] = np.array(base)
    mask = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(mask)
    dr.polygon([(sx[i], sy[i]) for i in range(4)], fill=255)
    mk = np.asarray(mask, dtype=np.float64)[..., None] / 255.0
    img = np.ones((H, W, 3)) * (1 - mk) + np.array(base) * mk
    # 孔
    holes = []
    n = 14
    for ix in range(-26, 27):
        for iz in range(-14, 30):
            cx, cz = ix * pitch + 8, iz * pitch
            if abs(cx) > ext or abs(cz) > ext:
                continue
            pts = np.array([[cx + hole_r * math.cos(2 * math.pi * i / n), 0.0,
                             cz + hole_r * math.sin(2 * math.pi * i / n)] for i in range(n)])
            hsx, hsy, hz = cam.project(pts)
            if hz.min() <= 1:
                continue
            if (hsx.max() - hsx.min()) < 3.0 or (hsy.max() - hsy.min()) < 2.2:
                continue
            holes.append(list(zip(hsx, hsy)))
    hd = ImageDraw.Draw(mask)
    hd.polygon([(sx[i], sy[i]) for i in range(4)], fill=0)
    for h in holes:
        hd.polygon(h, fill=255)
    mk = np.asarray(mask, dtype=np.float64)[..., None] / 255.0
    img = img * (1 - mk) + np.array([0.32, 0.32, 0.34]) * mk
    return img


def save(img, path, ss=2):
    a = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    if ss > 1:
        a = a.resize((a.width // ss, a.height // ss), Image.LANCZOS)
    a.save(path)
    print("saved", path, a.size)
