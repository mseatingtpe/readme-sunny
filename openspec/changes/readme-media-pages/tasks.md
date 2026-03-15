## 1. Media data index file (media.yaml 資料結構)

- [x] 1.1 建立 `content/media.yaml` media data index file — 從 CSV 篩選 Sunny C 的項目，依照 media.yaml 資料結構規格
- [x] 1.2 補充用戶手動提供的項目（INSIDE GAI 年會爐邊談、wazaiii 音樂劇文章、DDD 年會、子軒臉書後記連結）

## 2. Media content fetching for extraction（媒體報導全文萃取策略）

- [x] 2.1 執行 media content fetching for extraction — 抓取可存取全文的採訪報導，存入 `content/raw/`（遠見、經理人、商業周刊）
- [x] 2.2 抓取 wazaiii 供稿全文，存入 `content/raw/`（無 URL，待用戶提供）
- [x] 2.3 對新增的 `content/raw/` 檔案執行 `extract.py` 萃取世界觀
- [x] 2.4 執行 `generate_dashboard_data.py` 和 `generate_wordcloud.py` 更新儀表板資料

## 3. README structure with Skill prominence（README 區塊順序）

- [x] 3.1 修改 `generate_readme.py` — 實作 README structure with Skill prominence，調整區塊順序：intro → Skill → 世界觀快照 → 互動式儀表板 → 媒體與分享 → 文章
- [x] 3.2 修改 `generate_readme.py` — 新增 README media section generation 功能，從 `media.yaml` 生成三個子區塊表格（採訪報導、演講與論壇、供稿）

## 4. GitHub Pages personal website（GitHub Pages 啟用方式）

- [x] 4.1 將 repo 改為 public visibility，啟用 GitHub Pages personal website（source: docs/）
- [x] 4.2 更新 README 儀表板區塊的 dashboard link — 改為 GitHub Pages URL
- [x] 4.3 執行 `generate_readme.py` 重新生成 README.md
