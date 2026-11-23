#!/usr/bin/env python3
"""由逐頁內容（spec）套版產生 HTML 簡報，不在 HTML 內改字。用法：python3 tools/build_slides.py <topic>"""
import re, sys, html, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
work = root / "exports/slides/_work"
E = html.escape

def T(t): return re.sub(r"\[\[([^\]]+)\]\]", r"\1", re.sub(r"〔[^〕]*〕", "", t)).strip()

def parse(path):
    slides, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### ([PS]\d+)", line)
        if m: cur = {"id": m.group(1), "f": {}, "b": []}; slides.append(cur); continue
        if cur is None: continue
        if line.startswith("  - "): cur["b"].append(T(line[4:])); continue
        m = re.match(r"- (\S+?)[:：]\s*(.*)", line)
        if m: cur["f"][m.group(1)] = T(m.group(2))
    return slides

BASE = """html,body{height:100%;margin:0}
body{box-sizing:border-box;background:var(--bg);color:var(--ink);font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;display:flex;flex-direction:column;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
.bar{height:6px;background:var(--ac);width:0;transition:width .2s}
main{flex:1;overflow:auto;display:flex}
section{margin:auto;width:100%;max-width:var(--mw);padding:3vh 5vw;box-sizing:border-box;font-size:var(--fs);line-height:1.6}
section[hidden]{display:none}
h1{font-size:calc(var(--fs)*2.4);margin:0 0 .3em;line-height:1.2}
h2{font-size:calc(var(--fs)*1.6);margin:0 0 .5em;line-height:1.3;border-left:8px solid var(--ac);padding-left:.4em}
h3{margin:0 0 .3em;color:var(--ac);font-size:1em}
.sub{color:var(--ac);font-size:1.3em;margin:0 0 .8em}
ul,ol{margin:.3em 0;padding-left:1.4em}li{margin:.3em 0}
.tip{margin-top:1em;padding:.6em 1em;background:var(--tip);color:var(--tipi);border-radius:10px}
.box{background:var(--box);border:1px solid var(--bd);border-left:6px solid var(--ac);padding:.5em 1em;margin:.6em 0;border-radius:6px}
.warn{border-left-color:var(--warn)}.warn b,.badge{color:var(--warn)}
.src{margin-top:1em;font-size:.65em;color:var(--mut)}.cap{font-size:.75em;color:var(--mut)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--box)}
th,td{border:1px solid var(--bd);padding:.35em .6em;text-align:left;vertical-align:top}th{background:var(--hd)}
td.n,th.n{text-align:right;white-space:nowrap}td.k{white-space:nowrap;text-align:center}
.flow,.cmp,.kids{display:flex;flex-wrap:wrap;gap:.6em;align-items:stretch}
.grp,.card,.kid{flex:1 1 200px;border:2px solid var(--ac);border-radius:12px;padding:.5em .8em;background:var(--box)}
.grp ol{list-style:none;margin:0;padding:0}.card p,.kid p{margin:.15em 0}
.node{display:flex;gap:.5em;align-items:flex-start;margin:.25em 0}
.node b{flex:none;width:1.5em;height:1.5em;border-radius:50%;background:var(--ac);color:var(--bg);text-align:center;line-height:1.5em;font-size:.8em}
.ar{align-self:center;color:var(--ac);font-size:1.6em;font-weight:700;text-align:center}
.root{text-align:center;background:var(--ac);color:var(--bg);border-radius:12px;padding:.5em 1em;font-weight:700;margin:0 auto;width:fit-content}
.flow .grp{flex:1 1 0;min-width:170px;font-size:.82em}.flow .ar{font-size:1.2em}.cmp .card{font-size:.88em}
.kids{border-top:3px solid var(--ac);margin-top:.8em;padding-top:.8em}
.map{display:grid;grid-template-columns:1fr auto 1.4fr;gap:.5em .7em;align-items:center}
nav{display:flex;align-items:center;gap:12px;padding:10px 5vw}nav span{margin-left:auto;color:var(--mut)}
button{font:inherit;padding:.45em 1.1em;border-radius:8px;border:2px solid var(--ac);background:transparent;color:var(--ac);cursor:pointer}
button:disabled{opacity:.35;cursor:default}button:focus-visible{outline:3px solid var(--ac);outline-offset:2px}"""

THEMES = {
 "P": ("陪家人好好吃一餐｜細心手工餵食（意願人篇）", "--mw:980px;--fs:clamp(18px,2.4vw,28px);--bg:#EEF5F2;--ink:#1D3B36;--ac:#2F7F6F;--tip:#FFF3C4;--tipi:#5A4500;--mut:#4F6B66;--box:#fff;--bd:#BBD3CC;--hd:#DCEBE6;--warn:#8A3B12",
       "--bg:#12201D;--ink:#E6F2EE;--ac:#6FC5B2;--tip:#3A3216;--tipi:#F6E7A8;--mut:#A9C4BD;--box:#1B2D29;--bd:#2E4742;--hd:#22373A;--warn:#F2B38D"),
 "S": ("手工餵食與質地調整飲食（深入學習篇）", "--mw:1100px;--fs:clamp(15px,1.8vw,21px);--bg:#F4F6FB;--ink:#17233B;--ac:#2F55A4;--tip:#E8EEFB;--tipi:#17233B;--mut:#4A5A78;--box:#fff;--bd:#C9D3E8;--hd:#E3E9F6;--warn:#8A3B12",
       "--bg:#10172A;--ink:#E4EAF8;--ac:#8EACF0;--tip:#1D2842;--tipi:#E4EAF8;--mut:#A2B1D1;--box:#172036;--bd:#33415F;--hd:#1D2842;--warn:#F2B38D"),
}
JS = """const S=[...document.querySelectorAll('section')],B=document.getElementById('b'),C=document.getElementById('c'),P=document.getElementById('p'),N=document.getElementById('n');let i=0;
function go(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((e,k)=>e.hidden=k!==i);B.style.width=(i+1)/S.length*100+'%';C.textContent=(i+1)+' / '+S.length;P.disabled=i==0;N.disabled=i==S.length-1}
P.onclick=()=>go(i-1);N.onclick=()=>go(i+1);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(i+1)}else if(['ArrowLeft','PageUp'].includes(e.key))go(i-1)});
go(0)"""
REC = re.compile(r"(.+?)(?:（([^）]*)）)?：(\d+) 大卡、蛋白質 (\d+) g、脂肪 (\d+) g、碳水 (\d+) g、纖維 (\d+) g、鈉 (\d+) mg、鈣 (\d+) mg")

def render(s):
    f, b, i = s["f"], s["b"], s["id"]
    lay = f["版型"]
    ul = lambda xs: "<ul>" + "".join("<li>%s</li>" % E(x) for x in xs) + "</ul>"
    cap = lambda k: '<p class="cap">%s</p>' % E(f[k]) if k in f else ""
    sr = lambda k: '<p class="sr">%s</p>' % E(f[k]) if k in f else ""
    lab = lambda x: x.split("：", 1)
    if lay == "cover":
        o = "<h1>%s</h1><p class=\"sub\">%s</p>" % (E(f["標題"]), E(f.get("副標", "")))
        if "學習目標" in f:
            o += '<div class="box"><b>學習目標</b><ol>' + "".join("<li>%s</li>" % E(x) for x in f["學習目標"].split("；")) + "</ol></div>"
        o += ul(b)
    else:
        o = "<h2>%s</h2>" % E(f["標題"])
        if i == "P2":
            nodes = {int(re.match(r"(\d+)\s", x).group(1)): re.sub(r"^\d+\s+", "", x) for x in b}
            gs = []
            for m in re.finditer(r"(餵[前中後])（(\d+)(?:～(\d+))?）", f["分組"]):
                a = int(m.group(2)); z = int(m.group(3) or a)
                gs.append('<div class="grp"><h3>%s</h3><ol>%s</ol></div>' % (m.group(1), "".join('<li class="node"><b>%d</b><span>%s</span></li>' % (n, E(nodes[n])) for n in range(a, z + 1))))
            o += '<div class="flow">' + '<div class="ar">→</div>'.join(gs) + "</div>" + cap("圖註")
        elif i == "P5":
            cs = re.findall(r"「(半流質|全流質)」(像[^，]+)，([^，]+)，(適合[^。]+)。", f["圖說"])
            cards = ['<div class="card"><h3>%s</h3><p>%s</p><p>%s</p><p>%s</p></div>' % tuple(map(E, c)) for c in cs]
            o += ul(b) + '<div class="cmp">' + '<div class="ar">→</div>'.join(cards) + "</div>" + sr("圖說")
        elif i == "S2":
            kids = "".join('<div class="kid"><h3>%s</h3><p>%s</p></div>' % tuple(map(E, lab(x))) for x in b)
            o += '<div class="root">手工餵食（Careful hand feeding）</div><div class="kids">' + kids + "</div>" + cap("圖註")
        elif i == "S3":
            o += '<div class="tw"><table><tr><th>編號</th><th>內容</th></tr>' + "".join('<tr><td class="k">%s</td><td>%s</td></tr>' % (E(x[0]), E(x[1:].strip())) for x in b) + "</table></div>"
        elif i == "S4":
            c = lab(b[2]); br = []
            for d, w in ((b[0], b[3]), (b[1], b[4])):
                l, dd = lab(d); ww = lab(w)[1]
                br.append('<div class="card"><h3>%s</h3><p>%s</p><p>%s</p></div>' % (E(l), E(dd), E(ww)))
            o += '<div class="card"><h3>%s</h3><p>%s</p></div><div class="ar">↓</div><div class="cmp">%s</div>' % (E(c[0]), E(c[1]), "".join(br)) + sr("圖說")
        elif i == "S5":
            rows, rest = [], []
            for x in b:
                m = REC.match(x)
                if m:
                    g = m.groups()
                    name = E(g[0]) + ("<br><small>%s</small>" % E(g[1]) if g[1] else "")
                    rows.append("<tr><td>%s</td>%s</tr>" % (name, "".join('<td class="n">%s</td>' % v for v in g[2:])))
                else: rest.append(x)
            hd = "".join('<th class="n">%s</th>' % h for h in ["熱量(大卡)", "蛋白質(g)", "脂肪(g)", "碳水(g)", "纖維(g)", "鈉(mg)", "鈣(mg)"])
            o += ul(rest) + '<div class="tw"><table><tr><th>範例食譜</th>' + hd + "</tr>" + "".join(rows) + "</table></div>" + cap("備註")
        elif i == "S6":
            qs = [q for q in re.split(r"(?:^|\s)\d\s", f["討論"]) if q]
            o += '<p class="badge"><b>%s</b></p><div class="box">%s</div><b>討論問題</b><ol>%s</ol>' % (E(f["標示"]), ul(b), "".join("<li>%s</li>" % E(q) for q in qs))
        elif i == "S7":
            rows = [x.split(" → ", 1) for x in b[:4]]
            o += '<div class="map">' + "".join('<div class="card">%s</div><div class="ar">→</div><div class="card">%s</div>' % (E(l), E(r)) for l, r in rows) + "</div>"
            o += '<div class="box">%s</div><div class="box warn">%s</div>' % (E(b[4]), E(f["待查證"])) + sr("圖說")
        elif i == "S8":
            o += "<ul>" + "".join("<li>%s</li>" % ("<b class=\"badge\">%s</b>%s" % ("【待查證】", E(x.replace("【待查證】", ""))) if "【待查證】" in x else E(x)) for x in b) + "</ul>"
            o += '<div class="box"><b>延伸閱讀</b>　%s</div>' % E(f["延伸閱讀"])
        else:
            o += ul(b)
    if "互動" in f:
        k, _, v = f["互動"].partition("｜")
        o += '<div class="tip"><b>%s</b>：%s</div>' % (E(k), E(v))
    o += '<p class="src">依據：%s</p>' % E(f.get("頁尾依據", ""))
    return o

def build(topic, A):
    nm = {"P": "patient", "S": "student"}[A]
    sl = parse(work / topic / f"spec-{nm}.md")
    title, light, dark = THEMES[A]
    secs = "".join('<section data-id="%s"%s>%s</section>' % (s["id"], "" if n == 0 else " hidden", render(s)) for n, s in enumerate(sl))
    page = ('<!DOCTYPE html>\n<html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f"<title>{E(title)}</title><style>:root{{{light};color-scheme:light dark}}"
            f"@media(prefers-color-scheme:dark){{:root{{{dark}}}}}\n{BASE}</style></head><body>"
            f'<div class="bar" id="b"></div><main>{secs}</main>'
            '<nav><button id="p">上一頁</button><button id="n">下一頁</button><span id="c"></span></nav>'
            f"<script>{JS}</script></body></html>\n")
    out = root / "exports/slides" / f"{nm}-{topic}.html"
    out.write_text(page, encoding="utf-8")
    print(f"built {out.relative_to(root)}（{len(sl)} 頁，{len(page.encode('utf-8')) // 1024} KB）")

if __name__ == "__main__":
    for A in ("P", "S"): build(sys.argv[1], A)
