## -*- coding: utf-8 -*-

def plugin(user, user_nick, channel, message):
    return "PRIVMSG " + channel + " :" + message

