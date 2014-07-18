## -*- coding: utf-8 -*-

def plugin(user, user_nick, channel, message):
    if message.lower() == "test":
        return "PRIVMSG " + channel + " :Test failed"
    else:
        return ""

