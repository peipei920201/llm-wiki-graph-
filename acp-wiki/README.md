# 預立醫療照護諮商（ACP）衛教 LLM Wiki

參考 Karpathy 的 LLM Wiki 做法，由 LLM Agent 持續維護的繁體中文衛教知識庫。資料以「先討論、後入庫」逐份精讀，再整理成兩種受眾的衛教內容：

- **意願人篇**：給有意願做 ACP 的一般民眾，必要重點、階段性引導、白話用詞。
- **深入學習篇**：給醫護、社工等相關科系學生，內容完整，附情境與討論。

> **狀態：草稿。** 目前只收錄 1 份來源，所有頁面為 `draft`，尚未經專業人員審閱。內容僅供衛教與教學，不構成個別化醫療、法律或諮商意見。

## 目錄

```
AGENTS.md          # schema：給 Agent 的規則（先讀這份）
raw/               # 原始資料層（不可修改）；來源清單見 raw/SOURCES.md
wiki/              # Agent 維護層：index、log、overview、glossary、sources、concepts、laws、scenarios…
templates/         # 各類頁面與簡報模板
tools/             # build_slides.py（套版）、check_slides.py（檢查）
exports/slides/    # 由 wiki 生成的 HTML 簡報；_work/ 為簡報流程的工作檔
```

## 簡報成品

- `exports/slides/patient-careful-feeding.html`：意願人篇（7 頁）
- `exports/slides/student-careful-feeding.html`：深入學習篇（8 頁）

直接用瀏覽器開啟，← → 換頁。檔名中的 `student` 為程式代號，對外名稱為「深入學習篇」。

## 日常使用

1. 把新資料放進 `raw/inbox/`，請 Agent「處理 inbox」。
2. Agent 逐份精讀並討論重點，你確認後才入庫。
3. 想問問題直接問；想健檢請 Agent 做 lint。

詳見 `AGENTS.md` 第 9 節。

## 簡報流程（階段與關卡）

需求定義 → 選材（主張池）→ 大綱（關卡 A）→ 逐頁內容（關卡 B）→ 套版與驗證（關卡 C）。規則見 `AGENTS.md` 9.6。

```
python3 tools/build_slides.py careful-feeding   # 由逐頁內容產生 HTML
python3 tools/check_slides.py careful-feeding   # 檢查（階段 0～4）
```

只需 Python 3 標準函式庫；瀏覽器渲染檢查為選用（需 Playwright）。

## 著作權與資料來源

wiki 內容整理自第三方衛教資料，皆為摘要與改寫並標註出處，著作權屬原機構；原始 PDF 不在此版本庫。對外發布前請確認授權。本專案尚未指定授權條款。

## 在 Obsidian 中瀏覽

用 Obsidian 開啟此資料夾即可，內部連結為 `[[wikilink]]` 格式。
