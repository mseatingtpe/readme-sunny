## Why

建立一個「我的使用說明書」系統，從 Substack 文章、媒體報導、簡報等素材中，自動收集並萃取個人世界觀與思考框架。最終產出一個能代表「我」的用詞與邏輯的 Claude Code Skill，同時讓這個 GitHub repo 作為個人網頁，紀錄訪談、報導與文章。

## What Changes

- 建立內容收集管線：Substack RSS 自動抓取、媒體報導半自動收錄、簡報手動匯入
- 建立萃取框架：每篇內容萃取時間點、主題、立場、張力、連連看、轉變訊號、金句
- 從萃取結果生成「像我一樣思考」的 Claude Code Skill
- 設定 GitHub Pages 作為個人網頁，展示文章、媒體紀錄與世界觀演變
- 自動化更新流程：新內容進來 → 萃取 → 更新 Skill + 網頁

## Capabilities

### New Capabilities

- `content-collection`: 從多個來源（Substack RSS、媒體網站、手動匯入）收集原始內容並儲存
- `worldview-extraction`: 對每篇內容套用萃取框架（立場、張力、連連看、轉變訊號、金句），累積世界觀 profile
- `skill-generation`: 從萃取結果生成並持續更新 Claude Code Skill prompt
- `personal-site`: GitHub Pages 個人網頁，展示文章紀錄、媒體報導與世界觀時間軸

### Modified Capabilities

（無）

## Impact

- 新增資料目錄結構：原始內容、萃取結果、生成的 Skill 檔案
- 新增 GitHub Actions 或自動化腳本處理 RSS 抓取與萃取流程
- 新增 GitHub Pages 設定與靜態網頁模板
- 外部依賴：Substack RSS feed、媒體報導來源網站
