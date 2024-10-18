import sys
import argparse

import envvar
from dlbridge import DLBridgeBot, DLBridgeMode

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
    discord_bot_token = envvar.DBOT_TOKEN
    bot = DLBridgeBot(mode = mode, dbot_token = discord_bot_token)
    bot.run()   # こいつはブロッキングしてくるので必ず最後に呼ぶこと！

    return 0

if __name__ == '__main__':
    sys.exit(main())
