"""
LINE Bot Flask 應用程式
Echo Bot - 鸚鵡機器人
"""

import os
import sys
import yaml
from datetime import datetime

from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent


def load_config():
    """載入配置文件"""
    config_path = os.environ.get('LINEBOT_CONFIG_PATH', 'default.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f'[error]: Failed to load config file: {e}')
        sys.exit(1)


def validate_environment():
    """驗證必要的環境變數"""
    try:
        os.environ["LINE_CHANNEL_SECRET"]
        os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    except KeyError:
        print('[error]: LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN environment variables are required')
        sys.exit(1)


# 驗證環境變數
validate_environment()

# 載入配置
config = load_config()

# 建立 Flask 應用
app = Flask(__name__)

# 初始化 LINE Bot
handler = WebhookHandler(channel_secret=os.environ["LINE_CHANNEL_SECRET"])
configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])


@app.route('/')
def health_check():
    """
    健康檢查路由
    顯示服務狀態和配置資訊
    """
    bot_info = config.get('bot', {})
    server_info = config.get('server', {})
    line_info = config.get('line', {})

    response = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "bot": {
            "name": bot_info.get('name', 'LINE Bot'),
            "version": bot_info.get('version', '1.0.0'),
            "description": bot_info.get('description', '')
        },
        "server": {
            "host": server_info.get('host', '0.0.0.0'),
            "port": server_info.get('port', 8000)
        },
        "endpoints": {
            "health": "/",
            "webhook": line_info.get('webhook_path', '/callback')
        },
        "environment": {
            "channel_secret_configured": bool(os.environ.get("LINE_CHANNEL_SECRET")),
            "access_token_configured": bool(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
        }
    }

    return jsonify(response)


@app.route("/callback", methods=['POST'])
def callback():
    """
    LINE Webhook 回調端點
    接收來自 LINE 平台的事件
    """
    # 取得 X-Line-Signature header
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        app.logger.warning("Missing X-Line-Signature header")
        abort(400)

    # 取得請求內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        app.logger.error(f"Error handling webhook: {e}")
        abort(500)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """
    處理文字訊息事件
    Echo Bot - 回應相同的訊息內容
    """
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            # Echo 回使用者傳送的訊息
            reply_text = event.message.text

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
            app.logger.info(f"Replied to user with: {reply_text}")

    except Exception as e:
        app.logger.error(f"Error replying to message: {e}")


if __name__ == "__main__":
    # 如果直接執行此文件，使用配置文件中的設定啟動
    server_config = config.get('server', {})
    app.run(
        host=server_config.get('host', '0.0.0.0'),
        port=server_config.get('port', 8000),
        debug=server_config.get('debug', False)
    )
