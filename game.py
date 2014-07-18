## -*- coding: utf-8 -*-

def plugin(user, user_nick, channel, message):
    if message.lower().find("the game") != -1 or message.lower().find("sorunome") != -1:
        return "PRIVMSG " + channel + " :ACTION lost"
    else:
        return ""

