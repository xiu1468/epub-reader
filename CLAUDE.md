# epub-reader

這是一個個人使用的英文 EPUB 閱讀器 PWA。點書中的英文單字，會先顯示離線英漢解釋，Cambridge Dictionary 則是輔助連結。

- 網站：https://xiu1468.github.io/epub-reader/ （GitHub Pages，從 `main` 分支的根目錄部署）
- 使用者：在 Android 上用 Brave 瀏覽器，把網站「加到主畫面」當 App 用。請用**繁體中文**回覆，回覆要精簡，適合手機閱讀。
- 部署方式：推到 `main` 之後 1～2 分鐘網站就會更新。使用者手上沒有電腦，所以請你直接修改並推送，不要叫他自己上傳檔案。

## 檔案

| 檔案 | 用途 |
|---|---|
| `index.html` | 整個 App 就是這一個檔案（約 1.9 MB）。JSZip 3.10.1 和字形還原程式都直接內嵌在 `<script>` 裡，所以頁面不依賴任何 CDN。 |
| `dict.tsv` | 離線辭典：`word \t phonetic \t translation`，解釋的每一行之間用 ` \| ` 隔開。內容是繁體中文。 |
| `forms.tsv` | 變化形對照原形：`form \t lemma`（例如 `went \t go`）。 |
| `examples.tsv` | 例句：`word \t english \t 繁中翻譯`，約 1.2 萬個常用字各一句，來源 Tatoeba（CC BY 2.0 FR），由 `tools/build_examples.py` 產生。卡片在解釋下方顯示例句（不顯示書中原句；原句仍存進生字本）。 |
| `sw.js` | Service Worker：`index.html` 走 network-first（才會更新），其他檔案走 cache-first，所以可以離線使用。 |
| `manifest.webmanifest`、`icon-*.png` | PWA 安裝用。 |
| `tools/build_dict.py` | 用 ECDICT 重新產生 `dict.tsv` 和 `forms.tsv` 的腳本。 |
| `tools/lemma-entry.js` | 字形還原程式的原始碼（esbuild 打包後內嵌在 `index.html` 裡，全域變數是 `Lem`）。 |

## index.html 的結構

- 第一個 `<script>`：JSZip。第二個：`Lem` 字形還原（從 wink-lemmatizer 打包，約 1.7 MB）。修改 index.html 時，請用針對特定字串的替換（例如 Python 的 `str.replace` 加上 `assert count==1`）。**不要**整份讀進來或整份重寫，因為檔案大部分都是壓縮過的函式庫。
- 主程式在後面的 `<script>`（一個 IIFE），依序有這幾個區塊：
  - 設定：字體大小、深色模式、Cambridge 預設用英漢或英英
  - 書架：IndexedDB 資料庫 `epub-reader`，store 名稱是 `books`，裡面存書的 Blob
  - EPUB 解析：讀 container.xml → OPF → spine，目錄用 nav 或 NCX。每一章用 DOMParser 解析後放進 `#content`。不使用 iframe，所以點擊事件可以直接處理。
  - 點字查詢：用 `caretRangeFromPoint` 找出點到的單字，再用 `<mark class="hl">` 標示
  - 離線辭典：`loadDict()` 載入 `DICT` 和 `FORMS` 兩個 Map；`candidates()` 決定要用哪個字形查詢，優先順序是 forms 對照表 → `Lem` → 原字，最後把辭典裡查得到的字形排到最前面
  - 查詢卡片（`#sheet`）、生字本
- localStorage 的 key：`settings`、`vocab`（陣列，每筆是 `{w, f, d, s, b, t}`）、`pos:<書名>`（`{c: 章節索引, r: 捲動比例}`）、`lastBook`

## 離線辭典

資料來源是 [ECDICT](https://github.com/skywind3000/ECDICT)（MIT 授權）。腳本只保留單一單字，而且要符合以下任一條件：BNC 或 COCA 字頻排名在 60000 以內、有 Collins 星等、屬於 Oxford 3000，或有考試標籤。專業領域的解釋行（以 `[` 開頭）會被拿掉，每個字最多保留 5 行。最後用 OpenCC 的 `s2tw` 轉成繁體。不要用 `s2twp`，因為它會把「運行」改成「執行」之類的詞。

重新產生的步驟：
```
git clone --depth 1 https://github.com/skywind3000/ECDICT.git /tmp/ecdict/src
pip install --break-system-packages opencc-python-reimplemented
cd /tmp/ecdict && python3 /path/to/tools/build_dict.py 60000   # 會在目前資料夾寫出 dict.tsv 和 forms.tsv
```
**`dict.tsv`、`forms.tsv`、`examples.tsv` 或 sw.js 的快取檔案清單有任何變動時，都要把 `sw.js` 裡的 `CACHE` 版本號加一**（例如 `epub-reader-v2` → `v3`），不然已經安裝 App 的使用者會一直用到舊的快取。

例句的重新產生：`npm pack tatoeba-sentence-pairs-in-mandarin-chinese-english` 解開取得 `sentences.json`，再執行 `python3 tools/build_examples.py sentences.json dict.tsv forms.tsv > examples.tsv`。

## Cambridge

Cambridge 只用一般連結，例如 `https://dictionary.cambridge.org/search/direct/?datasetsearch=english-chinese-traditional&q=WORD`，在新分頁開啟。官方 API 需要另外申請，而且條款只允許評估用途；網頁本身也不能被抓取或內嵌，所以不要試著把 Cambridge 的內容放進卡片裡。

## 測試

在 repo 資料夾裡執行 `python3 -m http.server` 啟動本機伺服器（service worker 只在 localhost 或 https 下會註冊），再用 Playwright 搭配 `/usr/bin/google-chrome`，手機尺寸的視窗（390×844）測試：
- 開啟一個小的測試 EPUB（自己用 zipfile 產生：mimetype、META-INF/container.xml、OPF、nav、兩個 xhtml 章節）
- 點單字（用 Range 取得單字中間的座標再點擊），檢查 `#sWord`、`#sDefs`、`#sForms` 的內容
- 用 `context.set_offline(True)` 後重新整理，確認離線也能正常運作
- 推送前截圖檢查卡片的版面

用 `git -c push.negotiate=true push origin HEAD:main` 推送。
