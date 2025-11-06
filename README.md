# LINE Bot Echo 鸚鵡機器人

一個簡單的 LINE Bot 鸚鵡機器人模板，當使用者發送訊息時，機器人會回應相同的內容。適合初學者學習 LINE 聊天機器人開發。

## 功能特色

- 簡單的 Echo Bot 功能（鸚鵡機器人）
- 支援 YAML 配置文件
- 完整的環境變數驗證和防呆機制
- 健康檢查端點（`/`）
- LINE Webhook 回調端點（`/callback`）
- 清晰的專案結構

## 專案結構

```
linebot-flask-app/
├── src/                    # 原始碼目錄
│   ├── main.py            # Flask 應用程式主檔案
│   └── requirements.txt   # Python 依賴套件
├── default.yaml           # 預設配置文件
├── .env.example           # 環境變數範例文件
├── run.py                 # 應用程式啟動入口
├── docker-compose.yml     # Docker Compose 配置
└── README.md              # 專案說明文件
```

## 環境需求

- Python 3.8 或以上版本
- LINE Developers 帳號
- ngrok（用於本地開發測試）

## 安裝步驟

### 1. 複製專案

```bash
git clone <your-repo-url>
cd linebot-flask-app
```

### 2. 安裝依賴套件

```bash
pip install -r src/requirements.txt
```

### 3. 建立 LINE Bot

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 登入並建立一個新的 Provider（如果還沒有的話）
3. 建立一個新的 Messaging API Channel
4. 在 Channel 設定中取得以下資訊：
   - **Channel Secret**：在「Basic settings」頁面
   - **Channel Access Token**：在「Messaging API」頁面，點擊「Issue」按鈕產生

### 4. 設定環境變數

複製 `.env.example` 為 `.env`：

```bash
cp .env.example .env
```

編輯 `.env` 文件，填入你的 LINE Bot 資訊：

```bash
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
```

然後載入環境變數：

```bash
# Linux/macOS
export $(cat .env | xargs)

# 或者直接 export
export LINE_CHANNEL_SECRET=your_channel_secret
export LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
```

### 5. 自訂配置（選用）

如果需要自訂配置，可以修改 `default.yaml` 或建立新的配置文件：

```yaml
# custom.yaml
bot:
  name: "我的機器人"
  version: "2.0.0"
  description: "客製化的 LINE Bot"

server:
  host: "0.0.0.0"
  port: 8080
  debug: false
```

## 使用方式

### 啟動服務

使用預設配置啟動：

```bash
python run.py
```

使用自訂配置啟動：

```bash
python run.py --config custom.yaml
```

啟動成功後，你會看到類似以下的輸出：

```
==================================================
  LINE Bot 啟動檢查
==================================================
[✓] 成功載入配置文件: default.yaml

[檢查配置文件]
[✓] bot.name: 鸚鵡機器人
[✓] bot.version: 1.0.0
...

[檢查環境變數]
[✓] LINE_CHANNEL_SECRET: **********abcd
[✓] LINE_CHANNEL_ACCESS_TOKEN: **********xyz

[✓] 所有檢查通過！準備啟動服務...

==================================================
  鸚鵡機器人 v1.0.0
==================================================
伺服器位址: http://0.0.0.0:8000
Webhook 路徑: /callback
健康檢查: http://0.0.0.0:8000/
==================================================
```

### 使用 ngrok 暴露本地服務

在本地開發時，需要使用 ngrok 將本地服務暴露到公開網路，讓 LINE 平台能夠發送 webhook 事件。

#### 安裝 ngrok

1. 前往 [ngrok 官網](https://ngrok.com/) 註冊帳號
2. 下載並安裝 ngrok
3. 設定 authtoken：
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

#### 啟動 ngrok

在另一個終端視窗中執行：

```bash
ngrok http 8000
```

你會看到類似以下的輸出：

```
ngrok by @inconshreveable

Session Status                online
Account                       your_account (Plan: Free)
Version                       3.0.0
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abcd1234.ngrok.io -> http://localhost:8000
```

複製 `Forwarding` 中的 HTTPS URL（例如：`https://abcd1234.ngrok.io`）

### 設定 LINE Webhook URL

1. 回到 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇你的 Channel
3. 前往「Messaging API」頁面
4. 在「Webhook settings」中：
   - 設定 Webhook URL：`https://abcd1234.ngrok.io/callback`
   - 點擊「Verify」按鈕驗證 URL
   - 啟用「Use webhook」

### 測試機器人

1. 在 LINE Developers Console 的「Messaging API」頁面，使用手機掃描 QR Code 加入機器人好友
2. 發送訊息給機器人
3. 機器人應該會回應相同的訊息

## API 端點

### GET `/`

健康檢查端點，返回服務狀態和配置資訊。

**回應範例：**

```json
{
  "status": "ok",
  "timestamp": "2025-11-06T10:30:00.123456",
  "bot": {
    "name": "鸚鵡機器人",
    "version": "1.0.0",
    "description": "一個簡單的 LINE Echo Bot"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "endpoints": {
    "health": "/",
    "webhook": "/callback"
  },
  "environment": {
    "channel_secret_configured": true,
    "access_token_configured": true
  }
}
```

### POST `/callback`

LINE Webhook 回調端點，接收來自 LINE 平台的事件。

## 開發建議

### 防呆機制

本專案內建完整的防呆機制：

1. **配置文件驗證**：啟動前會檢查配置文件是否存在及格式是否正確
2. **環境變數檢查**：確保必要的環境變數已設定
3. **欄位完整性檢查**：驗證配置文件中的必要欄位

### 擴充功能

如需擴充機器人功能，可以在 `src/main.py` 中新增更多的 message handler：

```python
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    # 你的邏輯
    pass

# 處理貼圖訊息
@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    # 處理貼圖
    pass
```

### 使用 Docker

專案包含 `docker-compose.yml`，可以使用 Docker 運行：

```bash
docker-compose up
```

## 常見問題

### Q: 為什麼機器人沒有回應？

1. 檢查環境變數是否正確設定
2. 確認 ngrok 正在運行且 URL 正確
3. 檢查 LINE Webhook URL 是否設定正確
4. 查看服務日誌是否有錯誤訊息

### Q: Webhook 驗證失敗

1. 確認 ngrok URL 包含 HTTPS
2. 檢查防火牆設定
3. 確認服務正在運行

### Q: 環境變數設定後仍然顯示未設定

確保使用 `export` 命令載入環境變數，或重新啟動終端視窗。

## 技術棧

- **Flask 3.0.1**：Web 框架
- **line-bot-sdk 3.10.1**：LINE Bot SDK
- **PyYAML 6.0.1**：YAML 配置文件解析
- **gunicorn 21.2.0**：WSGI HTTP 伺服器（生產環境）

## 授權

MIT License

## 參考資源

- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [line-bot-sdk-python](https://github.com/line/line-bot-sdk-python)
- [Flask 官方文件](https://flask.palletsprojects.com/)
- [ngrok 官方文件](https://ngrok.com/docs)