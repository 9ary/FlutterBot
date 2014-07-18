## -*- coding: utf-8 -*-

def plugin(user, user_nick, channel, message):
    command = ""
    args = ""
    try:
        command = message.split()[0]
        args = " ".join(message.split()[1:])
    except IndexError:
        return ""

    if command == "@eat":
        return "PRIVMSG " + channel + " :ACTION eats " + args + ""
    else:
        return ""

