import os
import json

import discord

#
# DLBridge settings file example
#    {
#        'target_guilds' : [
#            {
#                'name' : 'server1',
#                'id' : 1234567,
#                'notify_token' : hausjaus862389uehdb8j3d82yehjadh121d
#                'target_channels' : [
#                    {
#                        'name' : 'Information',
#                        'id' : 123123123123
#                    },
#                    {
#                        'name' : 'Announcement',
#                        'id' : 456456456456
#                    }
#                ]
#            },
#            {
#                'name' : 'server2',
#                'id' : 89101112,
#                'notify_token' : ajksnaqi77s9iqgi6wrdbbwj38GAFj7ish7y
#                'target_channels' : [
#                ]
#            }
#        ]
#   }
#

class DLBridgeSettings():
    def __init__(self):
        self.filename = 'dlbridgeconf.json'

        self.settings = {}
        self.settings['target_guilds'] = []

    def register_text_channnel(self, channel : discord.TextChannel) -> bool:
        guild = channel.guild
        for g in self.settings['target_guilds']:
            if g['name'] == guild.name and g['id'] == guild.id:
                    channel_info = {}
                    channel_info['name'] = channel.name
                    channel_info['id'] = channel.id
                    g['target_channels'].append(channel_info)
                    return True            
        return False

    def unregister_text_channel(self, channel : discord.TextChannel) -> bool:
        guild = channel.guild
        for g in self.settings['target_guilds']:
            if g['name'] == guild.name and g['id'] == guild.id:
                channel_info = {}
                channel_info['name'] = channel.name
                channel_info['id'] = channel.id
                g['target_channels'].remove(channel_info)
                return True
        return False
    
    def set_line_notify_token(self, guild : discord.Guild, token : str) -> bool:
        if len(token) <= 0:
            return False

        for g in self.settings['target_guilds']:
            if g['name'] == guild.name and g['id'] == guild.id:
                g['notify_token'] = token
                return True
        return False

    def load(self, guilds : list[discord.Guild]):
        if os.path.exists(self.filename):
            with open(self.filename, mode = 'r') as jsonfile:
                self.settings = json.load(jsonfile)
        else:
            for guild in guilds:
                guild_info = {}
                guild_info['name'] = guild.name
                guild_info['id'] = guild.id
                guild_info['notify_token'] = ""
                guild_info['target_channels'] = []
                self.settings['target_guilds'].append(guild_info)

    def save(self):
        with open(self.filename, mode = 'w') as jsonfile:
            json.dump(self.settings, jsonfile, indent = 4)     
