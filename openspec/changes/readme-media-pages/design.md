## Context

Sunny 的 README 目前有：世界觀快照、文章列表、儀表板（本地）、Skill 說明。缺少媒體報導/演講/供稿區塊。資料來源是一份 Notion 匯出的 CSV（`專業分享：演講、採訪邀約存檔`），包含 2022-2025 年所有團隊的專業分享紀錄，需篩選 Sunny C 的項目。

現有自動化流程：Substack RSS → `content/raw/` → 萃取 → README + dashboard。媒體報導需要手動匯入但可進入相同萃取流程。

## Goals / Non-Goals

**Goals:**

- README 結構重排，Skill 在最上方
- 建立 `content/media.yaml` 作為媒體報導/演講/供稿的結構化索引
- 從 CSV 篩選 Sunny C 項目匯入 `media.yaml`
- `generate_readme.py` 讀取 `media.yaml` 生成「媒體與分享」區塊
- 可抓取全文的採訪報導存入 `content/raw/` 並跑萃取
- Repo 改 public，啟用 GitHub Pages

**Non-Goals:**

- 媒體報導的自動化收錄（之後再做）
- 演講簡報內容的萃取（等用戶提供文字框架）
- Dashboard 頁面改版

## Decisions

### media.yaml 資料結構

使用 `content/media.yaml` 作為所有媒體項目的單一索引，而非每筆資料一個檔案。結構：

```yaml
- title: 標題
  date: 2025-02-27
  type: interview | talk | writing  # 採訪 | 演講 | 供稿
  publication: 遠見雜誌  # 媒體/場合
  url: https://...  # 外部連結
  speaker: Sunny C  # 分享人（可能是團隊成員）
  has_content: true  # 是否有對應 content/raw/ 檔案
  description: 簡短描述（選填）
```

理由：媒體項目主要是 metadata（標題、日期、連結），不需要像文章一樣每篇一個 markdown 檔案。單一 YAML 檔便於維護和擴充。

### README 區塊順序

```
# Sunny's README
  intro + perpetual beta

## Skill
  think-like-sunny 說明

## 世界觀快照
  6 個主題的最新立場

## 互動式儀表板
  GitHub Pages 連結

## 媒體與分享
### 採訪報導
### 演講與論壇
### 供稿

## 文章
  Substack 文章列表
```

理由：Skill 是對外最有價值的產出，放最上面。媒體報導展現專業背景，放在文章之前。

### 媒體報導全文萃取策略

只萃取有完整網頁全文的採訪報導和供稿。演講只列連結。萃取流程複用現有 `extract.py`，`source_type` 設為 `media` 或 `writing`。

已知可萃取的項目：
- 遠見雜誌：《博恩夜夜秀》幕後功臣
- 經理人雜誌：合約產生器
- INSIDE：GAI 年會爐邊談
- 商業周刊：從害怕被ChatGPT取代（小馮）
- wazaiii 供稿

### GitHub Pages 啟用方式

透過 `gh api` 啟用 GitHub Pages，source 設為 `docs/` 目錄。先改 repo 為 public，再啟用 Pages。

## Risks / Trade-offs

- [CSV 資料品質] 部分欄位有 URL encoding、多重連結用逗號分隔 → 匯入腳本需處理
- [網頁抓取] 部分媒體網站可能有付費牆或反爬蟲 → 抓取失敗的項目只列連結不萃取
- [Repo 公開] 所有內容將公開可見 → 用戶已確認接受
