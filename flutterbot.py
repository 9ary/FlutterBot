#!/usr/bin/env python3
## -*- coding: utf-8 -*-

import socket
import sys
import importlib
import json
import re

config_file = sys.argv[1]
config = json.loads(open(config_file).read())
modules = {}
for plugin in list(config["plugins_loaded"].keys()):
    modules.update({plugin: importlib.import_module(plugin)})

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((config["server"], config["port"]))
sys.stdout.write(irc.recv(4096).decode())
if config["passw"] != "":
    irc.send(("PASS " + config["passw"] + "\n").encode())
irc.send(("NICK " + config["nick"] + "\n").encode())
irc.send(("USER " + config["nick"] + " 0 * :" + config["nick"] + "\n").encode())

def mkconfig():
    open(config_file, "w").write(json.dumps(config, sort_keys = True, indent = 4))

def send(channel, message):
    raw("PRIVMSG " + channel + " :" + message)

def raw(cmd):
    if cmd != "":
        irc.send((cmd + "\n").encode())

def sys_message(channel, message):
    print(str(channel) + ": " + message)
    if channel != None:
        send(channel, message)

def plugin_load(plugin, channels, channel = None):
    if not plugin in list(config["plugins_loaded"].keys()):
        try:
            config["plugins_loaded"].update({plugin: channels})
            modules.update({plugin: importlib.import_module(plugin)})
        except Exception as error:
            sys_message(channel, "Couldn't load " + plugin + " (" + str(type(error)) + ")")
        else:
            sys_message(channel, "Successfully loaded " + plugin)
            mkconfig()
    else:
        sys_message(channel, "Plugin " + plugin + " already loaded")

def plugin_unload(plugin, channel = None):
    if plugin in list(config["plugins_loaded"].keys()):
        del config["plugins_loaded"][plugin]
        del modules[plugin]
        sys_message(channel, "Unloaded " + plugin)
        mkconfig()
    else:
        sys_message(channel, "Plugin " + plugin + " not loaded")

def plugin_activate(plugin, channel):
    if plugin in list(config["plugins_loaded"].keys()):
        if not channel in config["plugins_loaded"][plugin]:
            config["plugins_loaded"][plugin] += [channel]
            sys_message(channel, "Activated " + plugin)
            mkconfig()
        else:
            sys_message(channel, "Plugin " + plugin + " already activated")
    else:
        sys_message(channel, "Plugin " + plugin + " not loaded")

def plugin_deactivate(plugin, channel):
    if plugin in list(config["plugins_loaded"].keys()):
        if channel in config["plugins_loaded"][plugin]:
            for i in range(len(config["plugins_loaded"][plugin])):
                if config["plugins_loaded"][plugin][i] == channel:
                    del config["plugins_loaded"][plugin][i]
            sys_message(channel, "Deactivated " + plugin)
            mkconfig()
        else:
            sys_message(channel, "Plugin " + plugin + " not activated")
    else:
        sys_message(channel, "Plugin " + plugin + " not loaded")

def main():
    while True:
        data = irc.recv(4096).decode()
        sys.stdout.write(data)

        if data.find("PING") != -1:
            raw("PONG " + data.split()[1])

        if data.find(":Welcome to") != -1:
            for channel in config["channels_autojoin"]:
                raw("JOIN " + channel)

        msg_type = ""
        try:
            msg_type = data.split()[1]
        except IndexError:
            pass

        if msg_type == "PRIVMSG":
            user = data.split()[0][1:]
            user_nick = ""
            channel = data.split()[2]
            message = (":".join(data.split(":")[2:]))[:-2]

            if user == "OmnomIRC!OmnomIRC@23.82.187.93":
                extract = r"^.{3}\((O|#|C)\).<((\w+ *)+)> (.*)"
                user_nick = re.sub(extract, r"\2", message)
                message = re.sub(extract, r"\4", message)
            else:
                user_nick = user.split("!")[0]

            if channel == config["nick"]:
                channel = user_nick

            if not channel in config["channels_autojoin"] and channel.find("#") != -1:
                config["channels_autojoin"] += [channel]
                mkconfig()

            for plugin in list(config["plugins_loaded"].keys()):
                if channel in config["plugins_loaded"][plugin]:
                    try:
                        raw(importlib.reload(modules[plugin]).plugin(user, user_nick, channel, message))
                    except Exception as error:
                        sys_message(channel, plugin + ": " + str(type(error)))

            if user in config["admins"]:
                try:
                    command = message.split()[0].lower()

                    if command == ">load":
                        plugin_load(message.split()[1], [], channel)

                    if command == ">unload":
                        plugin_unload(message.split()[1], channel)

                    if command == ">activate":
                        plugin_activate(message.split()[1], channel)

                    if command == ">deactivate":
                        plugin_deactivate(message.split()[1], channel)

                    if command == ">list":
                        try:
                            plugin = message.split()[1]
                            try:
                                sys_message(channel, plugin + " is activated in: " + str(config["plugins_loaded"][plugin]))
                            except KeyError:
                                sys_message(channel, "Plugin " + plugin + " not loaded")
                        except IndexError:
                            sys_message(channel, "Loaded plugins: " + str(list(config["plugins_loaded"].keys())))

                    if command == ">raw":
                        raw(" ".join(message.split()[1:]))

                except IndexError:
                    pass

main()

