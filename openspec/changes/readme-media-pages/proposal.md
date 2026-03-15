## Why

README 目前缺少媒體報導、演講、供稿的區塊，而這些是 Sunny 專業身份的重要面向。同時 Skill 區塊被放在最底部，但它是這個 repo 最具對外價值的產出，應該更顯眼。此外，互動式儀表板目前只能本地開啟，需要透過 GitHub Pages 上線讓外部可存取。

## What Changes

- **README 結構重排**：Skill 區塊移到世界觀快照之前，成為最上方的重點區塊
- **新增「媒體與分享」區塊**：從 CSV 資料篩選 Sunny C 的採訪報導、演講/論壇、供稿，以帶連結的表格呈現
- **媒體報導內容萃取**：可抓取全文的採訪報導和供稿（遠見、經理人、INSIDE、wazaiii 等）下載至 `content/raw/`，跑世界觀萃取流程
- **GitHub Pages 上線**：repo 改為 public，啟用 GitHub Pages（source: docs/），讓儀表板可透過 URL 存取
- **README 的儀表板連結更新**：從 `open docs/index.html` 改為 GitHub Pages URL
- **`generate_readme.py` 更新**：支援新的 README 結構和媒體報導區塊的自動生成

## Capabilities

### New Capabilities

- `media-collection`: 從 CSV 匯入媒體報導/演講/供稿資料，抓取可用全文，建立 `content/raw/` 檔案

### Modified Capabilities

- `personal-site`: 啟用 GitHub Pages，README 結構重排，新增媒體報導區塊

## Impact

- Affected code: `scripts/generate_readme.py`, `docs/index.html`（新增 footer 或 canonical link）
- New files: `content/raw/` 下的媒體報導 markdown 檔案, `content/media.yaml`（媒體資料索引）
- Configuration: GitHub repo visibility（private → public）, GitHub Pages 設定
- Dependencies: 新的媒體報導需跑 `scripts/extract.py` 萃取世界觀
