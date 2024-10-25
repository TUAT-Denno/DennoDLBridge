import discord
from discord.ext import commands

from rich import print as rich_print

from dlbridge import DLBridgeBot
from LINE.notify import LINENotifyAPI

class Discord2LINECog(commands.Cog):
    def __init__(self, bot : DLBridgeBot):
        print("Discord2LINECog is loaded!!")
        self.bot = bot

    # LINEにぶん投げるメッセージを生成する
    def _generate_notify_message(self, message : discord.Message) -> str:
        notify_msg = "\n"
        
        # まず、送信元のチャンネルと送信者を載せる
        notify_msg += (
            f"From: {message.author.display_name}\n"
            f"At: {message.channel.name}@{message.guild.name}\n"
        )

        # 次に本文の処理
        # えっ、Markdown？ 知らない子ですね...
        msg_content = message.clean_content or ""
        if msg_content != "":
            notify_msg += (
                f"Message:\n{msg_content}\n"
            )

        notify_msg += "\n"

        # 添付ファイルがあった場合は、何件あるかを載せる
        # Notifyは文字以外にJPEG/PNG画像だけ送ることができるらしい
        # 気が向いたら実装します
        attachment_num = len(message.attachments)
        if attachment_num > 0:
            notify_msg += (
                f"添付ファイルが{attachment_num}件あります\n"
                f"一番下のURLを開けばDiscordのメッセージを開けるから見てね\n\n"
            )
        
        # 投票が含まれていたら、そのことを載せる
        if message.poll:
            notify_msg += (
                f"投票が作成されました\n"
                f"一番下のURLを開いて、投票しましょう！\n"
                f"テーマ：{message.poll.question.text}\n\n"
            )

        # 最後にDiscordのメッセージを開くためのURLを貼る
        notify_msg += (f"URL: {message.jump_url}")

        return notify_msg

    # このコグの準備が整ったときに呼ばれるイベント関数
    @commands.Cog.listener(name = "on_ready")
    async def on_ready(self):
        print("Discord2LINE is ready!")

    # メッセージが投稿されたときに呼ばれるイベント関数
    @commands.Cog.listener(name = "on_message")
    async def on_message(self, message : discord.Message):
        # ボットからのメッセージは無視
        if message.author.bot is True:
           return

        if(message.type != discord.MessageType.default and
           message.type != discord.MessageType.reply):
            return

        for g in self.bot.settings.settings['target_guilds']:
            if message.guild.name == g['name'] and message.guild.id == g['id']:
                # LINE Notifyのトークンが設定されていなければ終了
                notify_token = g['notify_token']
                if len(notify_token) <= 0:
                    rich_print(
                        f"[yellow]Warning: LINE Notify token for {message.guild.name} (ID: {message.guild.id}) is not set.[/yellow]\n"
                        f"[yellow]Restart this application in setup mode and use the 'settoken' command to set the token.[/yellow]"
                    )
                    return
                target_channels = g['target_channels']
                line_notify_api = LINENotifyAPI(token = notify_token)
                break

        # 対象ギルドからのメッセージで無ければ終了
        if not bool('line_notify_api' in locals()):
            return

        # テキストチャンネルからのメッセージか
        if(message.channel.type == discord.ChannelType.text and
           message.channel.type == discord.ChannelType.news):
            # 送信元のチャンネルがエロい/グロい
            if message.channel.nsfw is True:
                return
            channel = message.channel
        # 公開スレッドからのメッセージ
        # elif message.channel.type == discord.ChannelType.public_thread:
        #     channel = message.channel.parent    # スレッドが所属しているチャンネルを取得
        else:
            return

        # 対象チャンネルからのメッセージであればLINEへ投げる
        for ch in target_channels:
            if channel.name == ch['name'] and channel.id == ch['id']:
                msg = self._generate_notify_message(message)
                await line_notify_api.send_notify_msg(msg.replace('\n', '\n'))
                break

    # スレッドが作成されたときに呼ばれるイベント関数
    @commands.Cog.listener(name = "on_thread_create")
    async def on_thread_create(self, thread : discord.Thread):
        # 公開スレッドでなければ無視
        if thread.type != discord.ChannelType.public_thread:
            return

        # 対象ギルド上のものか
        for g in self.bot.settings.settings['target_guilds']:
            if thread.guild.name == g['name'] and thread.guild.id == g['id']:
                # LINE Notifyのトークンが設定されていなければ終了
                notify_token = g['notify_token']
                if len(notify_token) <= 0:
                    rich_print(
                        f"[yellow]Warning: LINE Notify token for {thread.guild.name} (ID: {thread.guild.id}) is not set.[/yellow]\n"
                        f"[yellow]Restart this application in setup mode and use the 'settoken' command to set the token.[/yellow]"
                    )
                    return
                target_channels = g['target_channels']
                line_notify_api = LINENotifyAPI(token = notify_token)
                break

        # 対象ギルドからのメッセージで無ければ終了
        if not bool('line_notify_api' in locals()):
            return

        # 対象チャンネル上のものだったら、LINEに作成されたことを通知する
        for ch in target_channels:
            if thread.parent.name == ch['name'] and thread.parent.id == ch['id']:
                msg = (
                    f"\n「{thread.parent.name}」にスレッドが作成されました！\n"
                    f"Title: {thread.name}\n"
                    f"URL: {thread.jump_url}"
                )
                await line_notify_api.send_notify_msg(msg.replace('\n', '\n'))
                break

# Pycordがこのモジュールを読み込むために必要
def setup(bot : DLBridgeBot):
    bot.add_cog(Discord2LINECog(bot))
