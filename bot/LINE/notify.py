import aiohttp
import json

from LINE.common import (
    line_get_request,
    line_post_request
)

LINE_NOTIFY_URL        = 'https://notify-api.line.me/api/notify'
LINE_NOTIFY_STATUS_URL = 'https://notify-api.line.me/api/status'

class LINENotifyAPI():
    def __init__(self, token : str) -> None:
        self.notify_token = token

    # LINE Notifyでメッセージを送る
    # API:
    #   POST { LINE_NOTIFY_URL }
    # Param:
    #   must message(String) - メッセージ本文（最大1000文字）
    #   opt  imgThumb(URL) - サムネイル画像（最大240*240, JPEGのみ）
    #   opt  imgFull(URL) - 画像（最大 2048×2048px / JPEG のみ）
    #   opt  image(File) - 画像（PNG/JPEG）
    #                 LINE上の画像サーバーにアップロードされる
    #                 1時間にUPできる量に制限があるので注意
    #   opt  stickerPackageId(Number) - スタンプパッケージ識別子
    #   opt  stickerId(Number) - スタンプ識別子
    #   opt  notificationDisabled(Bool) - trueの場合、送信時にユーザーに通知しない
    #                                デフォルトはfalse
    async def send_notify_msg(self, message : str) -> json:
        data = {
            'message': f'{ message }'
        }
        response = await line_post_request(
            url = LINE_NOTIFY_URL,
            headers = {'Authorization': f'Bearer {self.notify_token}' },
            data = data
        )
        return response.json

    # LINE Notifyの連携状況を取得する
    # API:
    #   GET { LINE_NOTIFY_STATUS_URL }
    # Ret:
    #   targetType - 'USER'  通知先がユーザーである
    #                'GROUP' 通知先がグループである
    #   target     - ユーザー名 or グループ名
    #                取得に失敗した/該当ユーザーがグループを抜けている場合はnull
    async def notify_status(self) -> aiohttp.ClientResponse:
        return line_get_request(
            url = LINE_NOTIFY_STATUS_URL,
            token = self.notify_token
        )
    
    # 1時間に可能なAPI呼び出しの上限回数の取得
    async def apicall_limit(self) -> int:
        response = await self.notify_status()
        return int(response.headers.get('X-RateLimit-Limit'))
    
    # API呼び出しが可能な残り回数の取得
    async def apicall_remaining(self) -> int:
        response = await self.notify_status()
        return int(response.headers.get('X-RateLimit-Remaining'))
    
    # 1時間に可能な画像UPの上限回数の取得
    async def img_upload_limit(self) -> int:
        response = await self.notify_status()
        return int(response.headers.get('X-RateLimit-ImageLimit'))
    
    # 画像UP可能な残り回数の取得
    async def img_upload_remaining(self) -> int:
        response = await self.notify_status()
        return int(response.headers.get('X-RateLimit-ImageRemaining'))
    
    # 回数カウントがリセットされる時刻の取得（UTC epoch seconds ex:1472195604）
    async def count_reset_time(self) -> int:
        response = await self.notify_status()
        utc_epoch = int(response.headers.get('X-RateLimit-Reset'))
        return utc_epoch
