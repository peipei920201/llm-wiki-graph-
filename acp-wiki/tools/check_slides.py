#!/usr/bin/env python3
"""簡報流程的自動檢查。用法：python3 tools/check_slides.py <topic>"""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
work = root / "exports/slides/_work"
LIM = {"cover": 2, "list": 5, "table": 16, "figure": 16, "scenario": 6, "limits": 6}
MARKS = {"原文", "綜合", "待查證", "準則"}
fails = 0

def ok(m): print("ok   " + m)
def fail(m):
    global fails; fails += 1; print("FAIL " + m)

def page(name):
    if name == "AGENTS": return root / "AGENTS.md"
    for p in (root / "wiki").rglob(name + ".md"): return p

def stage0(topic):
    print("== 階段 0：需求定義 ==")
    b = (work / topic / "brief.md").read_text(encoding="utf-8")
    names = re.findall(r"\[\[([^\]]+)\]\]", re.search(r"納入頁面：(.*)", b).group(1))
    idx = (root / "wiki/index.md").read_text(encoding="utf-8")
    for n in names:
        p = page(n)
        if not p: fail(f"找不到頁面 {n}"); continue
        t = p.read_text(encoding="utf-8")
        st = re.search(r"^status:\s*(\S+)", t, re.M)
        ok(f"{n}：status={st.group(1) if st else '?'}，待查證 {t.count('【待查證】')} 處")
        if f"[[{n}]]" not in idx: fail(f"{n} 不在 index")
    m = re.search(r"意願人 (\d+)、學生 (\d+)", b)
    return {"P": int(m.group(1)), "S": int(m.group(2))}

def claims(topic):
    print("== 階段 1：主張池 ==")
    rows = {}
    for line in (work / topic / "claims.md").read_text(encoding="utf-8").splitlines():
        if re.match(r"\|\s*C\d+", line):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if c[0] in rows: fail(f"主張編號重複 {c[0]}")
            rows[c[0]] = dict(zip(["id","text","page","anchor","src","mark","aud","must"], c))
    for cid, r in rows.items():
        if r["mark"] not in MARKS: fail(f"{cid} 標記不合法：{r['mark']}")
        p = page(r["page"])
        if not p: fail(f"{cid} 找不到頁面 {r['page']}"); continue
        if r["anchor"] not in p.read_text(encoding="utf-8"): fail(f"{cid} 錨點不在 {r['page']}：{r['anchor']}")
        if r["mark"] == "待查證" and "P" in r["aud"]: fail(f"{cid} 待查證不得給意願人篇")
    if fails == 0: ok(f"{len(rows)} 條主張皆可在 wiki 或 AGENTS 找到錨點")
    return rows

def outline(path):
    slides, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### ([PS]\d+)\s+(.*)", line)
        if m: cur = {"id": m.group(1), "title": m.group(2)}; slides.append(cur); continue
        m = re.match(r"- (\S+?)[:：]\s*(.*)", line)
        if m and cur is not None: cur[m.group(1)] = m.group(2)
    return slides

def stage2(topic, A, rows, maxn):
    name = {"P": "outline-patient.md", "S": "outline-student.md"}[A]
    print(f"== 階段 2：大綱 {name} ==")
    sl = outline(work / topic / name)
    if len(sl) <= maxn[A]: ok(f"頁數 {len(sl)} ≤ {maxn[A]}")
    else: fail(f"頁數 {len(sl)} 超過上限 {maxn[A]}")
    seen, used = set(), set()
    for s in sl:
        i = s["id"]
        if i in seen: fail(f"{i} 重複")
        seen.add(i)
        if not i.startswith(A): fail(f"{i} 前綴與對象不符")
        lay = s.get("版型", "")
        ids = re.findall(r"C\d+", s.get("主張", ""))
        used.update(ids)
        if lay not in LIM: fail(f"{i} 版型不合法：{lay}"); continue
        if not ids: fail(f"{i} 沒有主張")
        if len(ids) > LIM[lay]: fail(f"{i} 主張 {len(ids)} 條，{lay} 版型上限 {LIM[lay]}")
        if len(s.get("訊息", "")) > 45: fail(f"{i} 訊息過長（應為一句話）")
        for c in ids:
            if c not in rows: fail(f"{i} 引用不存在的 {c}")
            elif A not in rows[c]["aud"]: fail(f"{i} 的 {c} 不屬於此對象")
        g = s.get("圖", "無")
        if lay == "figure" and g == "無": fail(f"{i} 為 figure 版型但沒有圖")
        if g != "無":
            base = set(re.findall(r"C\d+", s.get("圖依據", "")))
            if not base: fail(f"{i} 有圖但沒有圖依據")
            elif not base <= set(ids): fail(f"{i} 圖依據含不在本頁主張內的 {sorted(base - set(ids))}")
        if A == "P" and lay in ("list", "figure") and "互動" not in s: fail(f"{i} 缺互動（想一想／小事／找人）")
    miss = [c for c, r in rows.items() if A in r["aud"] and r["must"] == "是" and c not in used]
    if miss: fail(f"必講主張未落點：{miss}")
    else: ok("必講主張全部有落點")
    if A == "P":
        if sl[0].get("版型") != "cover": fail("第一頁應為封面")
        last = re.findall(r"C\d+", sl[-1].get("主張", ""))
        if not {"C23", "C30"} <= set(last): fail("最後一頁應含 C23、C30（找誰、提醒）")
    else:
        if not any(s.get("版型") == "scenario" for s in sl): fail("深入學習篇缺情境頁")
        sc = [s for s in sl if s.get("版型") == "scenario"]
        if sc and "討論" not in sc[0]: fail("情境頁缺討論題")
        if not any(s.get("版型") == "limits" for s in sl): fail("深入學習篇缺證據與限制頁")
        if "學習目標" not in sl[0]: fail("第一頁缺學習目標")

TAG = re.compile(r"〔([^〕]*C\d+[^〕]*)〕")
NEEDTAG = {"圖說", "圖註", "補充", "待查證"}

def strip(s): return TAG.sub("", s)
def norm(s): return re.sub(r"\s+", "", s)

def spec(path):
    slides, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### ([PS]\d+)", line)
        if m: cur = {"id": m.group(1), "lines": [], "版型": ""}; slides.append(cur); continue
        if cur is None: continue
        m = re.match(r"- 版型[:：]\s*(\S+)", line)
        if m: cur["版型"] = m.group(1)
        cur["lines"].append(line)
    return slides

def stage3(topic, A, rows):
    nm = {"P": "patient", "S": "student"}[A]
    print(f"== 階段 3：逐頁內容 spec-{nm}.md ==")
    ol = {s["id"]: s for s in outline(work / topic / f"outline-{nm}.md")}
    sp = spec(work / topic / f"spec-{nm}.md")
    trace = ["| 頁 | 內容 | 主張 | 錨點 | 標記 |", "|---|---|---|---|---|"]
    if [s["id"] for s in sp] != list(ol): fail("頁序與大綱不一致")
    alltext = []
    for s in sp:
        i = s["id"]; o = ol.get(i)
        if not o: fail(f"{i} 不在大綱"); continue
        if s["版型"] != o.get("版型"): fail(f"{i} 版型與大綱不同")
        cited = set(); text = []
        for line in s["lines"]:
            sub = line.startswith("  - ")
            m = re.match(r"- (\S+?)[:：]", line)
            key = m.group(1) if m else None
            body = line.strip()[2:] if line.strip().startswith("- ") else line.strip()
            tags = [c for t in TAG.findall(line) for c in re.findall(r"C\d+", t)]
            cited.update(tags)
            if key not in ("標題", "版型", "頁尾依據"): text.append(strip(body))
            if (sub and not tags) or (key in NEEDTAG and not tags):
                fail(f"{i} 缺主張編號：{strip(body)[:24]}")
            if tags:
                for c in tags:
                    if c not in rows: fail(f"{i} 引用不存在的 {c}")
                pages = norm("".join(page(rows[c]["page"]).read_text(encoding="utf-8") for c in tags if c in rows and page(rows[c]["page"])))
                for n in re.findall(r"\d+(?:\.\d+)?", re.sub(r"^\d+\s+", "", strip(body))):
                    if n not in pages: fail(f"{i} 數字 {n} 不在所引主張的頁面：{strip(body)[:24]}")
                for c in tags:
                    if c in rows: trace.append(f"| {i} | {strip(body).strip()[:60]} | {c} | {rows[c]['anchor'][:30]} | {rows[c]['mark']} |")
                if A == "P" and sub or key in ("圖說", "圖註"):
                    pass
            if A == "P" and (sub or key in ("圖說", "圖註")):
                for seg in re.split(r"[。！？]", strip(body)):
                    if len(seg) > 32: fail(f"{i} 句子過長（{len(seg)} 字）：{seg[:20]}")
        extra = cited - set(re.findall(r"C\d+", o.get("主張", "")))
        if extra: fail(f"{i} 引用大綱外的主張 {sorted(extra)}")
        lost = set(re.findall(r"C\d+", o.get("主張", ""))) - cited
        if lost: fail(f"{i} 大綱主張未使用 {sorted(lost)}")
        t = "\n".join(text); alltext.append(t)
        if A == "P":
            for b in ["你應該", "一定要", "必須", "務必", "口腔", "非語言", "均質", "擺位", "維持生命治療", "臨床"]:
                if b in t: fail(f"{i} 意願人篇不宜出現「{b}」")
            for term, ex in {"增稠劑": "變濃稠", "半流質": "鹹粥", "全流質": "濃湯"}.items():
                if term in t and ex not in t: fail(f"{i}「{term}」未在同頁白話說明")
            if re.search(r"[A-Za-z]{3,}", t): fail(f"{i} 意願人篇出現英文")
        else:
            if s["版型"] == "scenario" and "虛構" not in t: fail(f"{i} 情境頁缺虛構標示")
            if s["版型"] == "limits":
                for line in s["lines"]:
                    if re.search(r"C2[89]", line) and "【待查證】" not in line: fail(f"{i} 待查證項目未標示")
    if A == "S":
        full = "\n".join(alltext)
        for term, en in {"手工餵食": "Careful hand feeding", "半流質": "semi-liquid", "全流質": "full liquid", "增稠劑": "thickener", "非語言訊息": "nonverbal"}.items():
            k = full.find(term)
            if k >= 0 and en.lower() not in full[k:k + len(term) + 40].lower(): fail(f"首次出現「{term}」未附英文 {en}")
    (work / topic / f"trace-{nm}.md").write_text(f"# 溯源對照（{nm}）\n\n" + "\n".join(trace) + "\n", encoding="utf-8")
    ok(f"{len(sp)} 頁；溯源對照已輸出 trace-{nm}.md（{len(trace) - 2} 列）")

import html as _h
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_slides as BS
N = lambda t: re.sub(r"[\W_]+", "", t)

def stage4(topic, A):
    nm = {"P": "patient", "S": "student"}[A]
    print(f"== 階段 4：簡報 {nm}-{topic}.html ==")
    path = root / "exports/slides" / f"{nm}-{topic}.html"
    if not path.exists(): fail("HTML 不存在"); return
    h = path.read_text(encoding="utf-8")
    for need in ['name="viewport"', "prefers-color-scheme", "ArrowRight", 'id="p"', 'id="n"']:
        if need not in h: fail(f"缺少 {need}")
    if re.search(r"https?://|<script[^>]+src=|<link ", h): fail("含外部資源")
    secs = dict(re.findall(r'<section data-id="([PS]\d+)"[^>]*>(.*?)</section>', h, re.S))
    sp = BS.parse(work / topic / f"spec-{nm}.md")
    if list(secs) != [x["id"] for x in sp]: fail("頁序與逐頁內容不一致")
    miss = 0
    for x in sp:
        sec = N(_h.unescape(re.sub(r"<[^>]+>", "", secs.get(x["id"], ""))))
        f = x["f"]
        items = [f[k] for k in ("標題", "副標", "互動", "圖說", "圖註", "備註", "待查證", "標示", "延伸閱讀") if k in f]
        items += f.get("學習目標", "").split("；") if "學習目標" in f else []
        items += [q for q in re.split(r"(?:^|\s)\d\s", f.get("討論", "")) if q]
        for t in x["b"]:
            m = BS.REC.match(t)
            if m:
                items += [m.group(1)] + [g for g in m.groups()[1:] if g]
            else: items += t.split("：") if "：" in t else [t]
        for t in items:
            if N(t) and N(t) not in sec: miss += 1; fail(f"{x['id']} HTML 缺少 spec 文字：{t[:24]}")
        if "依據：" not in secs.get(x["id"], "") or any(N(n) not in sec for n in re.findall(r"[^、]+", f.get("頁尾依據", ""))): fail(f"{x['id']} 缺頁尾依據")
    if not miss: ok(f"{len(sp)} 頁文字與 spec 一致，皆有頁尾依據；無外部資源，含淺深色與鍵盤換頁")

def cross():
    print("== 階段 4：兩版一致性 ==")
    def nums(nm):
        d = {}
        for x in BS.parse(work / topic / f"spec-{nm}.md"):
            raw = [l for l in (work / topic / f"spec-{nm}.md").read_text(encoding="utf-8").split("### ")[1:] if l.startswith(x["id"])][0]
            for line in raw.splitlines():
                tg = {c for t in TAG.findall(line) for c in re.findall(r"C\d+", t)}
                if len(tg) == 1 and line.startswith("  - "):
                    d.setdefault(next(iter(tg)), set()).update(re.findall(r"\d+(?:\.\d+)?", re.sub(r"^\s*- \d+\s+", "", strip(line))))
        return d
    p, st = nums("patient"), nums("student")
    bad = [c for c in p if c in st and not p[c] <= st[c]]
    if bad: fail(f"兩版數字不一致：{bad}")
    else: ok(f"兩版共同主張 {len([c for c in p if c in st])} 條，意願人篇的數字皆見於深入學習篇")

if __name__ == "__main__":
    topic = sys.argv[1]
    maxn = stage0(topic)
    rows = claims(topic)
    for A in ("P", "S"): stage2(topic, A, rows, maxn)
    for A in ("P", "S"): stage3(topic, A, rows)
    for A in ("P", "S"): stage4(topic, A)
    cross()
    print(f"\n結果：{'全部通過' if fails == 0 else str(fails) + ' 項未通過'}")
    sys.exit(1 if fails else 0)
