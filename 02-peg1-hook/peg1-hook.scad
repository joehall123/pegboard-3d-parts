// =============================================================================
//  插销 1 号 · 弯钩销  (J-Hook Peg)
//  尺寸 100% 实测自参考件「手电钻16mm.3mf」后排 5 个弯钩
//  —— 不是拟合，是逐层切片量出来的
//
//  命名对照:
//    插销 1 号 = 本件（Ø5.00 直柱 3.11 + R2.90 急弯 + 短臂 4.60 + Ø5 球头）
//    插销 2 号 = 直插销（Ø5.50 销身 + Ø5.99 卡环@3.95 + 球头，总长 8.01）
//
//  坐标: 板面 = z0 平面（零件上表面），钩体向 -Z 伸出
//        直柱轴线 = Y 轴（x=0, y=0），短臂向 +Y 弯出
//  实测: 总深 8.51 / 总宽 12.50 / 理论体积 273.5 mm³（参考件实测 269.0 + 切割余量）
// =============================================================================

/* [核心尺寸 · 实测] */
d       = 5.00;    // 管径（实测 x 向恒为 Ø5.00）
stem    = 3.11;    // 直柱段长：板面 → 弯头切点
R       = 2.90;    // 弯头中心线半径（内圆角 = R - d/2 = 0.40）
arm     = 4.60;    // 短臂直段：弯头切点 → 臂端球心
ball    = true;    // 臂端球头（实测为半球收尾）

/* [派生] */
r   = d / 2;
d_arm = stem + R;          // 板面 → 短臂轴线 = 6.00
tip = R + arm + r;         // 短臂尽头到直柱轴线的距离 = 10.00

/* [姿态] */
orient = "print";   // "print" 平躺 / "draw" 立起(板面朝上)
$fn = 96;

module hook_raw() {
    // 1) 直柱（顶面贴板面，平端）
    translate([0, 0, -stem]) cylinder(h = stem, r = r, center = false);

    // 2) 90° 急弯：环轴沿 X，弧在 YZ 平面内
    //    扫掠 0°→90° 后绕 Y 轴立起，圆心落在 (y=R, z=-stem)
    translate([0, R, -stem])
        rotate([-90, 0, 0])
            rotate([0, 90, 0])
                rotate_extrude(angle = 90, $fn = $fn)
                    translate([R, 0]) circle(r = r, $fn = $fn);

    // 3) 短臂
    translate([0, R, -stem - R])
        rotate([-90, 0, 0])
            cylinder(h = arm, r = r, center = false);

    // 4) 臂端球头
    if (ball)
        translate([0, R + arm, -stem - R]) sphere(r = r, $fn = $fn);
}

module part() {
    if (orient == "print") {
        // 把钩子平放到平台：弯钩平面 YZ → 平台平面 XY，管轴厚度方向转成 +Z
        translate([0, 0, r]) rotate([0, 90, 0]) hook_raw();
    } else {
        hook_raw();
    }
}

part();

echo(str("板面→短臂轴线 = ", d_arm, " mm"));
echo(str("总深 = ", stem + R + r, " mm"));
echo(str("总宽 = ", R + arm + d, " mm"));
echo(str("短臂上表面距板面 = ", d_arm - r, " mm  ← 可用板厚上限"));
