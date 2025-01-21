import sys
import argparse

import os
from os.path import join, dirname
from dotenv import load_dotenv

from dlbridge import DLBridgeBot, DLBridgeMode

# .envファイルに記述されている環境変数を読み込む
load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def main() -> int:
    # コマンドラインパーサーの準備
    parser = argparse.ArgumentParser(
        prog = "DLBridge",
        description = "Discord bot to link Discord and LINE",
        add_help = True,    # -h, --helpをオプションとして追加
        exit_on_error = True
    )
    parser.add_argument(
        '-s', '--setup',
        action = 'store_true',
        help = "Launch the DLBridge in setup mode"
    )

    # コマンドライン引数の解析
    args = parser.parse_args()

    if args.setup:  # 設定専用モードで起動
        mode = DLBridgeMode.SETUP
    else:           # ボットとして起動
        mode = DLBridgeMode.BOT
    
    # ボット起動
    bot = DLBridgeBot(mode = mode, dbot_token = os.environ.get("DBOT_TOKEN"))
    bot.run()   # こいつはブロッキングしてくるので必ず最後に呼ぶこと！

    return 0

if __name__ == '__main__':
    sys.exit(main())
