import os
from os.path import join, dirname
from dotenv import load_dotenv

# .envファイルに記述されている環境変数を読み込む
load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DBOT_TOKEN = os.environ.get("DBOT_TOKEN")
LINENOTIFY_TOKEN = os.environ.get("LINENOTIFY_TOKEN")
