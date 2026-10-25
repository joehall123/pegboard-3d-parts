// =============================================================================
//  洞洞板手机收纳架 · 4 槽  (Pegboard Phone Caddy)
//  孔板: 孔径 6mm / 孔中心距 16mm (6mm 孔 + 10mm 边距 = 16mm 标准洞洞板)
//  摆放: 手机像书一样立进槽里, 屏幕朝左右, 背板靠住板面
//  挂销: 6 个圆柱销 (3 排 × 2), 几何抄自「手电钻16mm」参考件 ——
//        销身 Ø5.50 等径 + 卡环 Ø5.99 @ 距板面 3.95 + 球头收尾,
//        轴长 8.01, 过孔自锁 (实测剖面见 pegs/profile_chart.png)
//  充电: 每个槽底部开一个过线窗, 数据线从下方穿上来插手机
//  打印: 拓竹 A1 —— 本文件坐标即为打印坐标, 免支撑
//  坐标: X 宽度 / Y 离墙深度(挂销朝 -Y) / Z 高度(= 打印 Z)
// =============================================================================

/* [孔板规格] */
pitch      = 16.0;   // 孔中心距
hole_d     = 6.0;    // 孔径
board_t    = 5.0;    // 洞洞板厚度 (仅用于核对卡环与板厚关系)

/* [挂销 —— 实测自「手电钻16mm」参考件] */
peg_d      = 5.50;   // 销身直径 (实测 Ø5.50 等径 1.0~5.5mm)
rib_d      = 6.20;   // 卡环最大直径 (参考件实测 Ø5.99, 见下方说明)
rib_pos    = 3.95;   // 卡环峰到板面距离 (实测)
peg_len    = 8.01;   // 销总长 (含球头, 实测)
peg_rows   = [80, 48, 16];   // 三排挂销高度 (间距须为 16 的整数倍)
// 注: 参考件卡环 Ø5.99 ≈ 孔径 6.00, 属于"零过盈"——靠销身 5.50→5.59 的
//     微锥与孔壁摩擦止退。FDM 打印孔径常偏小 0.1~0.2, 这里给到 Ø6.20 作为
//     补偿; 若装不进, 按 0.1 递减; 若太松, 按 0.1 递增 (上限 6.4)。

/* [主体] */
slots      = 4;      // 卡槽数量
slot_w     = 13.5;   // 槽宽 (手机含壳 8~12mm 通用)
fin_t      = 2.4;    // 隔板厚度
depth      = 88.0;   // 总深度 (需 > 手机宽度, iPhone 约 72, 带壳 76)
back_h     = 100.0;  // 背板高度
back_t     = 5.0;    // 背板厚度
floor_z    = 6.0;    // 槽底离打印面高度
bot_flat   = 76.0;   // 底面平直段 (= 打印平台接触面)
lip_w      = 4.0;    // 前挡唇宽度
lip_h      = 12.0;   // 前挡唇高出槽底
fin_rise   = 8.0;    // 隔板前端高出挡唇顶面

/* [充电口] */
charge_on  = true;   // 槽底过线窗
charge_d   = 14.0;   // 过线窗深度 (从背板内表面往前)

/* [预览] */
show_holder = true;
show_phone  = false;
$fn         = 64;

// ---------------------------------------------------------------- 派生
w        = slots * slot_w + (slots + 1) * fin_t;
lip_top  = floor_z + lip_h;
lip_back = depth - lip_w;
fin_top  = lip_top + fin_rise;

// ---------------------------------------------------------------- 底座 2D
base_pts = [
    [0, 0],
    [bot_flat, 0],
    [depth, depth - bot_flat],      // 45° 让位倒角 (自支撑)
    [depth, lip_top],
    [lip_back, lip_top],
    [lip_back, floor_z],
    [0, floor_z]
];

function bez(p0, p1, p2, p3, t) =
    let (u = 1 - t)
    [ u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
      u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1] ];

// ---------------------------------------------------------------- 隔板 2D
fin_pts =
    concat(
        [[0, 0], [0, back_h - 5]],
        [ for (i = [0:12]) let (a = 180 + i * 7.5)            // 后上 R5
            [5 + 5 * cos(a), back_h - 5 + 5 * sin(a)] ],
        [ for (i = [1:26]) bez([5, back_h], [0.28 * depth, back_h - 2],
                              [0.80 * depth, fin_top + 26], [depth, fin_top], i / 26) ],
        [[depth, fin_top], [depth, depth - bot_flat], [bot_flat, 0]]
    );

module base2d() {
    offset(r = -1.6) offset(r = 1.6) polygon(base_pts);
}

module fin2d() {
    offset(r = -1.2) offset(r = 1.2) polygon(fin_pts);
}

// (Y,Z) 平面轮廓沿 X 拉伸
module extrude_yz(h) {
    multmatrix([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = h) children();
}

// ---------------------------------------------------------------- 挂销
// 圆柱销: Ø5.5 销身 + 球头顶端 + 一道卡环 (过孔时挤压, 起止退作用)
module peg() {
    R   = peg_d / 2;
    Rr  = rib_d / 2;
    rotate([90, 0, 0]) {                      // +Z -> -Y
        cylinder(h = peg_len - R, r = R);
        translate([0, 0, peg_len - R]) sphere(r = R, $fn = 32);
        // 卡环: 环形凸筋 (截面圆 r=0.5, 中心半径让外缘正好到 rib_d/2)
        translate([0, 0, rib_pos])
            rotate_extrude($fn = 48)
                translate([Rr - 0.55, 0]) circle(r = 0.55, $fn = 20);
    }
}

// ---------------------------------------------------------------- 主体
module body() {
    extrude_yz(w) square([back_t, back_h]);                   // 背板
    extrude_yz(w) base2d();                                   // 底座 + 前挡唇
    for (i = [0:slots])
        translate([i * (fin_t + slot_w), 0, 0]) extrude_yz(fin_t) fin2d();
}

module holder() {
    difference() {
        body();
        // 每个槽底的过线窗 (贯通底座, 侧壁就是隔板内表面)
        if (charge_on)
            for (i = [0:slots - 1])
                translate([i * (fin_t + slot_w) + fin_t, back_t, -2])
                    cube([slot_w, charge_d, floor_z + 6]);
    }
    // 6 个挂销
    for (r = peg_rows)
        for (sx = [-1, 1])
            translate([w / 2 + sx * pitch / 2, 0, r]) peg();
}

// ---------------------------------------------------------------- 预览用
module rbox(s, r) {
    minkowski() {
        cube([s[0] - 2 * r, s[1] - 2 * r, s[2] - 2 * r]);
        sphere(r = r, $fn = 20);
    }
}
module phone() {
    translate([-5.5, 5.4, floor_z]) rbox([11, 76, 158], 4);
}

if (show_holder) translate([-w / 2, 0, 0]) holder();
if (show_phone)
    for (i = [0:slots - 1])
        translate([-w / 2 + fin_t + i * (fin_t + slot_w) + slot_w / 2, 0, 0]) phone();
