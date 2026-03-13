## 1. 內容儲存結構與收集

- [x] 1.1 建立內容目錄結構（content directory structure）：`content/raw/`、`content/extractions/`
- [x] 1.2 依「內容儲存格式：Markdown + YAML frontmatter」決策，定義 frontmatter schema 與範例檔
- [x] 1.3 撰寫 Substack RSS 抓取腳本，實作 collect content from Substack RSS 功能
- [x] 1.4 實作重複偵測邏輯（article already collected 情境），避免重複抓取已存在的文章
- [x] 1.5 建立手動匯入範本，支援 store media coverage records 與 store presentation content

## 2. 萃取框架實作

- [x] 2.1 依「萃取框架：七維度固定結構」決策，定義 extraction output format 的 YAML schema
- [x] 2.2 撰寫 Claude API 萃取腳本，實作 extract worldview snapshot from content 功能
- [x] 2.3 處理無轉變訊號的情境（shift signal 為 null）
- [x] 2.4 實作 worldview timeline：建立累積式 worldview-profile.yaml 並在每次萃取後更新

## 3. Skill 生成

- [x] 3.1 依「Skill 結構：分層 prompt 檔案」決策，設計 Skill 的三層結構（core identity / topic stances / recent dynamics）
- [x] 3.2 撰寫 generate Claude Code Skill from extractions 的生成腳本
- [x] 3.3 實作 Skill reflects author voice 的 prompt 設計，捕捉用詞風格與推理習慣
- [x] 3.4 實作 Skill token budget 限制（4000 tokens 上限與自動精簡邏輯）

## 4. 自動化流程

- [x] 4.1 依「自動化方式：GitHub Actions + Claude API」決策，建立 workflow 每日排程抓取 RSS，實作 extraction triggered automatically
- [x] 4.2 串接完整管線：RSS 收集 → 萃取 → 更新 worldview profile → Skill auto-updated after extraction
- [ ] 4.3 設定 GitHub Secrets 存放 Claude API key
- [x] 4.4 加入手動觸發（workflow_dispatch）作為備援

## 5. 個人網頁（GitHub Pages）

- [x] 5.1 依「個人網頁：GitHub Pages + Jekyll/靜態生成」決策，設定 GitHub Pages personal website
- [x] 5.2 建立 content listing page，依時間倒序顯示所有收集的內容
- [x] 5.3 建立 media coverage section，按年份分組顯示媒體報導
- [x] 5.4 建立 worldview evolution display 頁面，視覺化信念在各主題上的時間演變

## 6. 初始內容匯入

- [x] 6.1 匯入既有 Substack 文章（~20 篇）至 `content/raw/`
- [x] 6.2 對所有既有文章執行萃取，產生 extraction 檔案
- [x] 6.3 從萃取結果生成第一版 Skill，由使用者手動校正
