## Context

這是一個全新的 repo（sunny-readme），目標是建立一個「個人使用說明書」系統。資料來源以 Substack 電子報為主（~20 篇），輔以媒體報導與 Canva 簡報。使用者已有固定的半年度信念列表（「相信的事情列表」），這是世界觀演變的天然錨點。

目前 repo 只有 OpenSpec 設定，沒有任何應用程式碼。

## Goals / Non-Goals

**Goals:**

- 建立可擴充的內容收集與儲存結構
- 定義萃取框架，從原始內容中提取世界觀快照
- 產出可用的 Claude Code Skill 檔案
- 用 GitHub Pages 呈現個人紀錄網頁
- 自動化：新內容進來後能自動觸發萃取與更新

**Non-Goals:**

- 不做即時爬蟲或複雜的 NLP pipeline
- 不建立自訂的 LLM fine-tuning
- 不處理 Canva 簡報的自動匯入（維持手動）
- 不做使用者認證或多人系統

## Decisions

### 內容儲存格式：Markdown + YAML frontmatter

每篇原始內容存為 Markdown 檔案，metadata 用 YAML frontmatter 記錄。

理由：GitHub Pages 原生支援、人類可讀、Git 版本控制天然追蹤演變。

替代方案：JSON / SQLite — 對單人系統過重，且不利於直接在 GitHub 上閱讀。

### 萃取框架：七維度固定結構

每篇內容萃取七個維度：時間點、主題、立場、張力、連連看、轉變訊號、金句。萃取結果存為獨立的 YAML 檔案，與原始內容分離。

理由：與使用者討論後確認的框架，貼合其寫作特徵（跨領域串連、矛盾中找平衡）。

替代方案：自由格式萃取 — 難以跨時間比對，不利於自動化生成 Skill。

### 自動化方式：GitHub Actions + Claude API

用 GitHub Actions 監聽 RSS feed（定時排程），新文章進來後呼叫 Claude API 執行萃取，結果 commit 回 repo。Skill 檔案在每次萃取後重新生成。

理由：不需要額外伺服器，完全在 GitHub 生態系內完成。

替代方案：本地 cron job — 需要一台持續運行的機器；Zapier/Make — 增加外部依賴且成本較高。

### 個人網頁：GitHub Pages + Jekyll/靜態生成

使用 GitHub Pages 搭配靜態網站生成器，直接從 repo 中的 Markdown 檔案生成網頁。

理由：零成本、與 repo 同步、支援自訂域名。

替代方案：Vercel + Next.js — 對靜態內容來說過重。

### Skill 結構：分層 prompt 檔案

Skill 由三層組成：核心身份（不常變）、主題立場（半年更新）、最近動態（每次萃取更新）。

理由：避免每次更新都重寫整個 Skill，也反映世界觀有不同時間尺度的演變。

## Risks / Trade-offs

- [萃取品質不穩定] → 前幾篇手動校正萃取結果，建立 few-shot examples 給 Claude API 參考
- [RSS 抓取可能遺漏或延遲] → GitHub Actions 排程每日檢查，加上手動觸發作為備援
- [Skill prompt 過長] → 設定 token 預算上限，超過時自動精簡舊的動態層
- [GitHub Actions 的 Claude API 費用] → 每篇萃取約一次 API call，成本極低（每月幾篇文章）
