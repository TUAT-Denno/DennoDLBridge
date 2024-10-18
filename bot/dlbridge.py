from enum import Enum
import traceback

from rich import print as rich_print
from rich.tree import Tree

import aioconsole
import discord

import command_help as help
from bot_settings import DLBridgeSettings

class DLBridgeMode(Enum):
    BOT   = 1
    SETUP = 2

class DLBridgeBot(discord.AutoShardedBot):
    def __init__(self, dbot_token : str, mode : DLBridgeMode = DLBridgeMode.BOT):
        self.mode = mode
        self.discord_bot_token = dbot_token
        self.settings = DLBridgeSettings()

        # Botが利用するイベントの設定
        # DLBridgeはpresences, members以外に関連した全てのイベントを受け取ることができる
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents = intents)

        print("Starting bot...")

    async def on_ready(self):
        # Botの設定の読み込み
        print("Loading settings...")
        self.settings.load(self.guilds)

        # presenceの設定
        await self._update_presence()

        # ヘッダの出力・処理の開始
        print(f"Hello! I'm {self.user.name}!! My ID is {self.user.id}.")
        if self.mode is DLBridgeMode.BOT:
            rich_print("I'm running in [green]BOT[/green] mode.")
            self._load_cogs()
        elif self.mode is DLBridgeMode.SETUP:
            rich_print(("I'm running in [blue]SETUP[/blue] mode.\n"
                       "Type 'help' for a list of available commands.\n"
                       "Type 'help name' to find out more about the function 'name'.")
                       .replace('\n', '\n'))
            self.loop.create_task(self._setup_task())

    # Bot実行に必要なモジュール（cogsフォルダの中にあるもの）を読み込む
    def _load_cogs(self):
        # store=Trueとすると、ロードエラー時にクリティカルになる
        ret = self.load_extensions(
            "cogs.discord_to_line",
            store = True
        )

    # チャンネルの一覧を木構造で出力する
    # "chtree"コマンドの実体
    def _display_text_channels_tree(self, guild_id : int):
        guild = self.get_guild(guild_id)
        if guild == None:
            rich_print(f'[red]The guild (ID: {guild_id}) not found[/red]')
            return

        for category in guild.categories:
            tree_root = Tree(category.name)
            for textch in category.text_channels:
                tree_root.add(f'{textch.name} (ID: {textch.id})')
            rich_print(tree_root)

    # DLBridgeがインストールされているギルドの一覧を出力する
    # "lg"コマンドの実体
    def _list_guilds(self):
        for i in range(len(self.guilds)):
            guild = self.guilds[i]
            print(f'{guild.name} (ID: {guild.id})')

    # 登録済みのチャンネルの一覧を出力する
    # "lch"コマンドの実体
    def _list_registered_text_channels(self, guild_id : int):
        guild = self.get_guild(guild_id)
        if guild == None:
            rich_print(f'[red]The guild (ID: {guild_id}) not found[/red]')
            return

        for g in self.settings.settings['target_guilds']:
            if g['name'] == guild.name and g['id'] == guild.id:
                print(f'List of registered text channels on {guild.name}:')
                if len(g['target_channels']) > 0:
                    for ch in g['target_channels']:
                        name = ch['name']
                        id = ch['id']
                        print(f'{name} (ID: {id})')
                else:
                    print("None")
                break
    
    # 指定されたチャンネルを連携対象にする
    # "regch"コマンドの実体
    def _register_text_channel(self, guild_id : int, channel_id : int):
        guild = self.get_guild(guild_id)
        if guild == None:
            rich_print(f'[red]The guild (ID: {guild_id}) not found[/red]')
            return
        
        for category in guild.categories:
            for ch in category.text_channels:
                if ch.id == channel_id:
                    if not self.settings.register_text_channnel(ch):
                        rich_print('[red]Cannot register the text channel[/red]')
                    print(f'Registered the \'{ch.name}\'')
                    return
        rich_print(f'[red]The channel (ID: {channel_id}) not found[/red]')

    # 指定されたチャンネルを連携対象から外す
    # "unregch"コマンドの実体 
    def _unregister_text_channel(self, guild_id : int, channel_id : int):
        guild = self.get_guild(guild_id)
        if guild == None:
            rich_print(f"[red]The guild (ID: {guild_id}) not found[/red]")
            return
        
        for category in guild.categories:
            for ch in category.text_channels:
                if ch.id == channel_id:
                    if not self.settings.unregister_text_channel(ch):
                        rich_print('[red]Cannot unregister the text channel[/red]')
                    print(f'Unregistered the \'{ch.name}\'')
                    return
        rich_print(f'[red]The channel (ID: {channel_id}) not found[/red]')

    # 指定したギルドにLINE Notifyのトークンを紐づける
    # "settoken"コマンドの実体
    def _set_notify_token(self, guild_id : int, token : str):
        guild = self.get_guild(guild_id)
        if guild == None:
            rich_print(f'[red]The guild (ID: {guild_id}) not found[/red]')
            return

        if not self.settings.set_line_notify_token(guild = guild, token = token):
            return rich_print(f'[red]Cannot register the notify token. Maybe it is invalid.[/red]')
        print(f"Registered the LINE notify token for '{guild.name}'")

    async def _setup_task(self):
        await self.wait_until_ready()

        while not self.is_closed():
            # ユーザーによるコマンド入力の取得
            try:
                line =  await aioconsole.ainput(prompt = ">> ")
            except EOFError:
                continue

            args = line.split()
            args[0].lower()     # 入力されたコマンド文字列を小文字に変換する
            if not args:
                continue

            if args[0] == 'lg':
                self._list_guilds()
            elif args[0] == 'lch':
                if len(args) < 2:
                    rich_print('[red]Guild ID not specified[/red]')
                    continue
                try:
                    id = int(args[1])
                except ValueError:
                    rich_print(f'[red]This ID cannot be converted to integer. Is this really an integer?[/red]')
                    continue
                self._list_registered_text_channels(id)
            elif args[0] == 'chtree':
                if len(args) < 2:
                    rich_print('[red]Guild ID not specified[/red]')
                    continue
                try:
                    id = int(args[1])
                except ValueError:
                    rich_print(f'[red]This ID cannot be converted to integer. Is this really an integer?[/red]')
                    continue
                self._display_text_channels_tree(id)
            elif args[0] == 'regch':
                if len(args) < 3:
                    rich_print('[red]Guild and channel ID not specified[/red]')
                    continue
                try:
                    guild_id = int(args[1])
                    channel_id = int(args[2])
                except ValueError:
                    rich_print(f'[red]These IDs cannot be converted to integer. Are these really integers?[/red]')
                    continue
                self._register_text_channel(guild_id, channel_id)
            elif args[0] == 'unregch':
                if len(args) < 3:
                    rich_print('[red]Guild and channel ID not specified[/red]')
                    continue
                try:
                    guild_id = int(args[1])
                    channel_id = int(args[2])
                except ValueError:
                    rich_print(f'[red]These IDs cannot be converted to integer. Are these really integers?[/red]')
                    continue
                self._unregister_text_channel(guild_id, channel_id)
            elif args[0] == 'settoken':
                if len(args) < 3:
                    rich_print('[red]Guild ID and notify token not specified[/red]')
                    continue
                try:
                    guild_id = int(args[1])
                except ValueError:
                    rich_print(f'[red]This ID cannot be converted to integer. Is this really an integer?[/red]')
                    continue
                self._set_notify_token(guild_id, args[2])
            elif args[0] == 'quit':
                if self.mode == DLBridgeMode.SETUP:
                    print("Save settings...")
                    self.settings.save()
                print("Good bye")
                await self.close()
                break
            elif args[0] == 'help':
                if len(args) < 2:
                    help.display_setup_cmd_list()
                else:
                    help.display_setup_cmd_help(args[1])
            else:
                rich_print("[red]Unknown command. Type 'help' for a list of available commands.[/red]")

    async def _update_presence(self):
        if self.mode == DLBridgeMode.BOT:
            await self.change_presence(
                activity = discord.Game(name = '電脳ちゃんダッシュ!!')
            )
        elif self.mode == DLBridgeMode.SETUP:
            await self.change_presence(
                activity = discord.Game(name = 'ボットの設定')
            )

    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.discord_bot_token))
        except discord.LoginFailure:
            rich_print("[red]Cannot log in to Discord. Maybe there is something wrong with the bot token...[/red]")
        except discord.HTTPException as e:
            traceback.print_exc()
        except KeyboardInterrupt:
            if self.mode is DLBridgeMode.SETUP:
                print("Save settings...")
                self.settings.save()
            print("Good bye")
            self.loop.run_until_complete(self.close())
        except:
            traceback.print_exc()
        finally:
            self.loop.close()
