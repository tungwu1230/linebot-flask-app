#!/usr/bin/env python3
"""
LINE Bot 啟動程式
提供配置驗證和防呆機制
"""

import os
import sys
import argparse
import yaml
from pathlib import Path


def load_config(config_path):
    """載入 YAML 配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"[✓] 成功載入配置文件: {config_path}")
        return config
    except FileNotFoundError:
        print(f"[✗] 錯誤: 找不到配置文件 '{config_path}'")
        print(f"    請確認文件是否存在，或使用 --config 參數指定配置文件")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[✗] 錯誤: 配置文件格式錯誤")
        print(f"    {e}")
        sys.exit(1)


def validate_config(config):
    """驗證配置文件的必要欄位"""
    print("\n[檢查配置文件]")

    required_fields = [
        ('bot', 'name'),
        ('bot', 'version'),
        ('server', 'host'),
        ('server', 'port'),
        ('line', 'webhook_path')
    ]

    all_valid = True
    for fields in required_fields:
        current = config
        valid = True
        for field in fields:
            if field not in current:
                print(f"[✗] 缺少必要欄位: {'.'.join(fields)}")
                all_valid = False
                valid = False
                break
            current = current[field]
        if valid:
            print(f"[✓] {'.'.join(fields)}: {current}")

    return all_valid


def validate_env():
    """驗證必要的環境變數"""
    print("\n[檢查環境變數]")

    required_env_vars = [
        "LINE_CHANNEL_SECRET",
        "LINE_CHANNEL_ACCESS_TOKEN"
    ]

    missing_vars = []
    for var in required_env_vars:
        if var in os.environ and os.environ[var]:
            print(f"[✓] {var}: {'*' * 10}{os.environ[var][-4:]}")
        else:
            print(f"[✗] {var}: 未設定")
            missing_vars.append(var)

    if missing_vars:
        print("\n[錯誤] 缺少必要的環境變數！")
        print("\n請設定以下環境變數：")
        for var in missing_vars:
            print(f"  export {var}=your_{var.lower()}")
        print("\n或建立 .env 文件並使用 python-dotenv 載入")
        return False

    return True


def display_startup_info(config):
    """顯示啟動資訊"""
    bot_name = config.get('bot', {}).get('name', 'Unknown')
    bot_version = config.get('bot', {}).get('version', 'Unknown')
    host = config.get('server', {}).get('host', '0.0.0.0')
    port = config.get('server', {}).get('port', 8000)
    webhook_path = config.get('line', {}).get('webhook_path', '/callback')

    print("\n" + "=" * 50)
    print(f"  {bot_name} v{bot_version}")
    print("=" * 50)
    print(f"伺服器位址: http://{host}:{port}")
    print(f"Webhook 路徑: {webhook_path}")
    print(f"健康檢查: http://{host}:{port}/")
    print("=" * 50)
    print("\n[提示] 使用 Ctrl+C 停止服務\n")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='LINE Bot 啟動程式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python run.py                    # 使用預設配置文件 (default.yaml)
  python run.py --config my.yaml   # 使用自訂配置文件
        """
    )

    parser.add_argument(
        '--config',
        default='default.yaml',
        help='指定配置文件路徑 (預設: default.yaml)'
    )

    args = parser.parse_args()

    print("=" * 50)
    print("  LINE Bot 啟動檢查")
    print("=" * 50)

    # 1. 載入配置文件
    config = load_config(args.config)

    # 2. 驗證配置文件
    if not validate_config(config):
        print("\n[✗] 配置文件驗證失敗！請檢查配置文件內容")
        sys.exit(1)

    # 3. 驗證環境變數
    if not validate_env():
        sys.exit(1)

    print("\n[✓] 所有檢查通過！準備啟動服務...\n")

    # 4. 顯示啟動資訊
    display_startup_info(config)

    # 5. 設定配置文件路徑到環境變數，讓 Flask app 可以讀取
    os.environ['LINEBOT_CONFIG_PATH'] = args.config

    # 6. 啟動 Flask 應用
    try:
        from src.main import app

        host = config.get('server', {}).get('host', '0.0.0.0')
        port = config.get('server', {}).get('port', 8000)
        debug = config.get('server', {}).get('debug', False)

        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n[✓] 服務已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n[✗] 啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
