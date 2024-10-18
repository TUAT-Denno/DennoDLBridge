from rich import print as rich_print

class _CommandHelp:
    def __init__(self, name : str, usage : str, description : str):
        self.name  = name
        self.usage = usage
        self.description  = description

_cmds_help = [
    _CommandHelp('chtree', 'chtree GUILD_ID',
                 'Display a tree structure of channels that exist in the specified guild'),
    _CommandHelp('lg', 'lg',
                 'Display a list of guilds where the DLBridge is installed'),
    _CommandHelp('lch', 'lch GUILD_ID',
                 'Display a list of registered channels'),
    _CommandHelp('regch', 'regch GUILD_ID CHANNEL_ID',
                 'Register the channel'),
    _CommandHelp('unregch', 'unregch GUILD_ID CHANNEL_ID',
                 'Unregister the channel'),
    _CommandHelp('settoken', 'settoken GUILD_ID token',
                 'Register the LINE Notify token for the specified guild'),
    _CommandHelp('help', 'help [COMMAND]',
                 'Display help'),
    _CommandHelp('quit', 'quit',
                 'Quit this bot')
]

_cmdlist = ''
for _ch in _cmds_help:
    _cmdlist += "{0:10} - {1}\n".format(_ch.name, _ch.description)

# セットアップコマンドの一覧を出力する
# "help"の実体
def display_setup_cmd_list():
    print(_cmdlist.replace('\n', '\n'))

# 指定されたコマンドのヘルプを出力する
# "help [COMMAND]"の実体
def display_setup_cmd_help(cmd : str):
    for h in _cmds_help:
        if h.name == cmd:
            print("Usage: {0}\n{1}"
                    .format(h.usage, h.description)
                    .replace('\n', '\n'))
            return
    rich_print("[red]Unknown command. Type 'help' for a list of available commands.[/red]")
