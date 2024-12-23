# ICP 抽獎系統

## 主要檔案和目錄

- `app/`: 應用程式的主要目錄
  - `routes.py`: 定義了應用程式的路由和處理邏輯
  - `static/`: 靜態資源，如 CSS、JavaScript 和圖片
  - `templates/`: HTML 模板文件
  - `utils/`: 實用工具函數和模組
- `app.py`: 應用程式的入口點
- `requirements.txt`: 列出了專案所需的 Python 套件
- `README.md`: 專案的說明文件

## 安裝和運行

1. **安裝 Python**

   請確保您的系統已安裝 Python（版本 3.6 以上）。

2. **建立虛擬環境**

   使用 `venv` 模組建立虛擬環境：

    ```sh
    python -m venv lotteryenv
    ```

3. **啟動虛擬環境**

    在 Windows：

    ```sh
    lotteryenv\Scripts\activate
    ```

4. **安裝依賴套件**

    使用 pip 安裝 `requirements.txt` 中的依賴套件：

    ```sh
    pip install -r requirements.txt
    ```

5. **運行應用程式**

    執行 `app.py` 啟動應用程式：

    ```sh
    python app.py
    ```

6. **訪問應用程式**

    在瀏覽器中打開 [http://localhost:5000](http://localhost:5000) 查看應用程式。

## 主要功能

- **抽獎功能**: 用於抽取不同組別的獎項
- **獎品管理**: 新增、查看和管理獎品
- **成員管理**: 查看不同組別的成員

## 路由和模板

- `@bp.route('/')`: 主頁面，顯示抽獎系統的入口
- `@bp.route('/googleicp', methods=['GET', 'POST'])`: 用於新增獎品的頁面，對應模板 `add_gift.html`
- `@bp.route('/senior_member')`: 資深同仁頁面，對應模板 `senior_member.html`
- `@bp.route('/junior_member')`: 半年以上成員頁面，對應模板 `junior_member.html`
- `@bp.route('/new_member')`: 新人獎頁面，對應模板 `new_member.html`
- `@bp.route('/gifts?drawing_group=4')`: 獎品頁面，對應模板 `gifts.html`
- `@bp.route('/draw/<int:gift_id>')`: 抽獎頁面，對應模板 `draw.html`

## 靜態資源

- `app/static/css/`: 存放 CSS 文件
- `app/static/js/`: 存放 JavaScript 文件
- `app/static/images/`: 存放圖片資源

## 實用工具

- `app/utils/drawing.py`: 包含抽獎相關的邏輯和函數
- `app/utils/query_sqlite.py`: 包含與 SQLite 資料庫交互的函數
