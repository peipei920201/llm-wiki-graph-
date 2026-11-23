---
type: log
title: 日誌
---

# 日誌

> 只增不改，新紀錄加在檔案末尾。格式：`## [YYYY-MM-DD] 動作 | 對象`
> 動作：intake、discuss、ingest、query、lint、schema

## [2026-11-23] schema | 初始化
- 建立目錄結構、AGENTS.md、模板、index、log、overview、glossary
- 決議：先討論後入庫、一次精讀一份、繁體中文並保留關鍵英文術語；雙受眾指南（意願人篇／學生篇）

## [2026-11-23] intake | 2 份資料
- 心願探索手冊（臺北市立聯合醫院）：因版權聲明，使用者決定暫不使用，未入庫、未複製進 raw/
- 北慈濟醫細心手工餵食衛教.pdf：改名為 2019-tzuchi-careful-feeding.pdf

## [2026-11-23] ingest | 2019-tzuchi-careful-feeding
- 依使用者「請處理並製作兩版簡報」之指示視為確認入庫（略過獨立的討論報告步驟）；全部頁面 status 為 draft，待審閱
- 新建：[[2019-tzuchi-careful-feeding]]、[[手工餵食]]、[[半流質與全流質]]、[[scn-手工餵食時反覆嗆咳]]；更新 glossary、index
- 匯出簡報：exports/slides/patient-careful-feeding.html、student-careful-feeding.html
- 原檔已移至 raw/ingested/；未產生 raw/converted（PDF 文字可直接讀取）

## [2026-11-23] schema | 新增 exports/slides/
- 新增簡報匯出資料夾與規則（見 AGENTS.md 第 3、4、8 節）

## [2026-11-23] schema | 新增簡報流程 9.6
- 關卡 A、B、C；兩版共用主張池；意願人篇上限 8 頁、學生篇 10 頁；允許放圖；新增 tools/check_slides.py 與模板 outline、slide-spec

## [2026-11-23] query | 以新流程重做 careful-feeding 簡報（階段 0～2）
- 產出 brief、claims（32 條）、outline-patient（7 頁）、outline-student（8 頁），待關卡 A
- 檢查發現 C31、C32 在 wiki 無錨點；已補回 [[手工餵食]]（擺位可因人而異＝原 PDF 明載；餵前中後排列＝【綜合】說明），頁面仍為 draft

## [2026-11-23] query | careful-feeding 簡報階段 3（逐頁內容）
- 產出 spec-patient（7 頁）、spec-student（8 頁）與溯源對照 trace-*.md，待關卡 B
- 檢查：腳本誤判 2 類已修正（版型代號、流程步驟編號）；真實問題 1 項（P5 圖說過長）已改寫
- 新增術語：非語言訊息（nonverbal cues，本專案譯名）；claims C11 補入末期失智憋氣吞嚥一句（wiki 頁面原已載明）

## [2026-11-23] query | careful-feeding 簡報階段 4（套版與驗證），待關卡 C
- 關卡 B 通過；tools/build_slides.py 由 spec 產生 exports/slides/patient-careful-feeding.html（7 頁）、student-careful-feeding.html（8 頁），取代流程前的舊版
- 檢查：文字與 spec 一致、頁尾依據、無外部資源、兩版共同主張數字一致；瀏覽器渲染無橫向溢出、無 JS 錯誤
- 已知：意願人篇 P2、P5 與學生篇 S3（14 列表格）在 1280×720 需捲動；學生篇 S3、S5 在手機寬度需捲動


## [2026-11-23] schema | 「學生篇」更名為「深入學習篇」
- 文字更名：AGENTS.md、模板、index、來源頁、簡報工作檔（brief、claims、outline、spec）與建置／檢查腳本
- 檔名與頁碼編號不變（student、S1～S8、wiki/guides/student/）；先前 log 紀錄保留原稱以維持歷史

## [2026-11-23] schema | 整理上傳 GitHub 版本
- 新增 README.md、.gitignore、raw/SOURCES.md；AGENTS.md 補版本控制說明
- 原始 PDF 因第三方著作權不納入打包；wiki 頁面維持 draft
