#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把预览图内嵌成一页式 HTML 说明书"""
import base64, pathlib

D = pathlib.Path(__file__).parent


def b64(name):
    return "data:image/png;base64," + base64.b64encode((D / name).read_bytes()).decode()


IMG = {
    "hero": b64("final_1.png"),
    "front": b64("final_2.png"),
    "side": b64("final_3.png"),
    "peg": b64("peg_detail.png"),
    "win": b64("final_5.png"),
}

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>洞洞板手机收纳架 · 4 槽</title>
<style>
  :root {{
    --ink:#1c1e21; --mid:#5a6270; --line:#e3e6ea; --bg:#f6f7f8;
    --accent:#0f766e; --card:#ffffff;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--bg); color:var(--ink);
    font:15px/1.75 -apple-system,"PingFang SC","Helvetica Neue",Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
  }}
  .wrap {{ max-width:980px; margin:0 auto; padding:44px 28px 72px; }}
  header {{ display:flex; align-items:flex-end; justify-content:space-between;
           gap:24px; border-bottom:1px solid var(--line); padding-bottom:20px; }}
  h1 {{ font-size:27px; letter-spacing:-.3px; margin:0 0 6px; }}
  .sub {{ color:var(--mid); font-size:13.5px; }}
  .badge {{ display:inline-block; font-size:12px; padding:3px 10px; border-radius:20px;
            background:#e7f3f1; color:#0b5f58; border:1px solid #cfe6e2; margin-left:8px; }}
  h2 {{ font-size:17px; margin:40px 0 14px; letter-spacing:-.2px;
        display:flex; align-items:center; gap:9px; }}
  h2::before {{ content:""; width:3px; height:16px; background:var(--accent); border-radius:2px; }}
  figure {{ margin:0; }}
  .hero {{ border-radius:14px; overflow:hidden; background:#fff; border:1px solid var(--line); }}
  .hero img {{ width:100%; display:block; }}
  .cap {{ color:var(--mid); font-size:12.5px; padding:9px 14px; border-top:1px solid var(--line); }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px; }}
  .grid .cell {{ background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
  .grid img {{ width:100%; display:block; }}
  table {{ width:100%; border-collapse:collapse; background:var(--card);
           border:1px solid var(--line); border-radius:12px; overflow:hidden; font-size:14px; }}
  th, td {{ padding:10px 14px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ background:#fafbfc; font-weight:600; color:#37404d; white-space:nowrap; width:180px; }}
  tr:last-child td, tr:last-child th {{ border-bottom:none; }}
  td b {{ color:var(--accent); font-weight:600; }}
  code {{ background:#eef1f4; padding:1px 6px; border-radius:5px; font-size:13px;
          font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
  @media (max-width:760px) {{ .cols,.grid {{ grid-template-columns:1fr; }} th {{ width:auto; }} }}
  ol {{ margin:0; padding-left:20px; }} ol li {{ margin-bottom:7px; }}
  .note {{ background:#fffdf3; border:1px solid #f0e6c8; border-radius:12px;
           padding:14px 18px; font-size:13.5px; color:#5d5330; }}
  .note b {{ color:#8a6d1f; }}
  footer {{ margin-top:48px; padding-top:16px; border-top:1px solid var(--line);
            color:#9aa2ad; font-size:12.5px; }}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div>
      <h1>洞洞板手机收纳架<span class="badge">4 槽</span></h1>
      <div class="sub">Ø6 孔 / 16 mm 孔距 · 6 个卡环圆柱挂销 · 槽底带充电过线窗 · 拓竹 A1 免支撑</div>
    </div>
    <div class="sub" style="text-align:right">66 × 88 × 100 mm<br>PLA · 约 85 g</div>
  </header>

  <figure class="hero" style="margin-top:26px">
    <img src="{IMG['hero']}" alt="整体效果">
    <div class="cap">手机像书一样立进槽里，屏幕朝左右，背面靠住背板</div>
  </figure>

  <h2>结构与细节</h2>
  <div class="grid">
    <div class="cell"><img src="{IMG['front']}" alt="正面 3/4"><div class="cap">正面 3/4：四槽，隔板 2.4 mm，前挡唇 4 mm 厚</div></div>
    <div class="cell"><img src="{IMG['side']}" alt="侧面"><div class="cap">侧面：背高 100，前挡唇高 18，底部 45° 让位</div></div>
    <div class="cell"><img src="{IMG['peg']}" alt="挂销"><div class="cap"><b>6 个挂销 · 3 排 × 2</b>：Ø5.5 销身 + Ø6.0 卡环 + 球头，长 8，排距 32</div></div>
    <div class="cell"><img src="{IMG['win']}" alt="过线窗"><div class="cap"><b>槽底过线窗</b>：每槽 13.5 × 14 mm 贯通，往后透出洞洞板</div></div>
  </div>

  <h2>关键尺寸</h2>
  <table>
    <tr><th>外形</th><td>宽 66 × 深 88 × 高 100 mm（不含挂销；含销总深 96）</td></tr>
    <tr><th>卡槽</th><td>4 槽 / 槽宽 <b>13.5 mm</b> / 隔板 2.4 mm / 槽内可用深 79 mm</td></tr>
    <tr><th>充电过线窗</th><td>每槽 13.5 × 14 mm，贯通槽底，开在靠背侧</td></tr>
    <tr><th>挂销</th><td><b>6 个（3 排 × 2）</b>；Ø5.5 销身 + Ø6.0 卡环 + 球头顶端；总长 8，卡环距板面 3.7；排高 80 / 48 / 16，列距 16</td></tr>
    <tr><th>最小壁厚</th><td>2.4 mm（= 6 圈 0.4 线宽）</td></tr>
    <tr><th>实体体积</th><td>123.9 cm³，水密单一实体；床面接触 42.6 cm²；超 45° 悬垂 1.5%</td></tr>
    <tr><th>适配手机</th><td>含壳厚度 ≤ 12 mm、宽度 ≤ 79 mm 完全落入槽内；更宽会搭在挡唇上微后仰</td></tr>
  </table>

  <h2>打印设定</h2>
  <div class="cols">
    <table>
      <tr><th>喷嘴 / 层高</th><td>0.4 / 0.20 mm</td></tr>
      <tr><th>墙层数</th><td>4</td></tr>
      <tr><th>顶 / 底实心层</th><td>5 / 4</td></tr>
      <tr><th>填充</th><td>15% Gyroid</td></tr>
      <tr><th>支撑</th><td><b>不需要</b></td></tr>
      <tr><th>摆放</th><td>直接导入，不要旋转</td></tr>
    </table>
    <table>
      <tr><th>耗材</th><td>PLA，约 80–95 g</td></tr>
      <tr><th>时间</th><td>4–5 h（0.2 层高）</td></tr>
      <tr><th>底面接触</th><td>42.6 cm²，免 brim</td></tr>
      <tr><th>打印方向</th><td>站立打印，背板在后侧竖直生长</td></tr>
      <tr><th>挂销</th><td>水平圆柱，靠层间自支撑（同参考件做法）</td></tr>
      <tr><th>材料替换</th><td>PETG 更韧，收缩率调 0.3%</td></tr>
    </table>
  </div>

  <h2>安装</h2>
  <ol>
    <li>在洞洞板上找 <b>3 排 × 2 列</b>的孔：每排相邻两孔（16 mm），排间隔一个孔（32 mm）。</li>
    <li>对准后整块直推压入，感觉到卡环过孔即可（手掌推，别用锤子）。拆卸时握住两侧平拉。</li>
    <li>数据线从架子下方穿进槽底过线窗，插头落在手机底边位置，再把手机立进槽里。</li>
  </ol>

  <h2>想改尺寸</h2>
  <table>
    <tr><th>减一个槽</th><td><code>slots</code> 4 → 3，外形自动变窄</td></tr>
    <tr><th>放厚壳手机</th><td><code>slot_w</code> 13.5 → 15</td></tr>
    <tr><th>卡环偏紧 / 偏松</th><td><code>rib_d</code> 6.0 → 5.8 / 6.2</td></tr>
    <tr><th>不要充电窗</th><td><code>charge_on</code> true → false</td></tr>
    <tr><th>过线窗要深一点</th><td><code>charge_d</code> 14 → 18</td></tr>
    <tr><th>挂销只要两排</th><td><code>peg_rows</code> [80,48,16] → [60,28]</td></tr>
  </table>
  <p class="sub" style="margin-top:10px">改完 OpenSCAD 里 F6 渲染 → Export STL。参数都带中文注释，单位 mm。</p>

  <h2>两点要留意</h2>
  <div class="note">
    <b>① 卡环是压配的。</b>Ø6.0 卡环 = 孔径，靠塑料微量挤压产生止退；装的时候对准直推，不要斜着撬。
    板厚 3 mm 以下时卡环会落在板背面之外，变成普通销（还能挂，但没止退）。<br>
    <b>② 深度。</b>槽深按 76 mm 宽的手机设计，整件离墙 88 mm。嫌厚可以改 <code>depth</code>，代价是手机底部露在槽外。
  </div>

  <footer>pegboard_phone_holder.scad / .stl · 模型坐标即打印坐标 · Ø6 孔 / 16 mm 孔距洞洞板 · 挂销尺寸参考「手电钻16mm」</footer>
</div>
</body>
</html>
"""

(D / "打印说明.html").write_text(HTML, encoding="utf-8")
print("ok", len(HTML) // 1024, "KB")
