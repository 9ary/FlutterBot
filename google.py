## -*- coding: utf-8 -*-

import json, urllib.parse, urllib.request

def plugin(user, user_nick, channel, message):
    command = ""
    args = ""
    try:
        command = message.split()[0]
        args = " ".join(message.split()[1:])
    except IndexError:
        return ""

    if command in ["@google", "@youtube", "@omnimaga", "@xkcd", "@tiplanet", "@wikipedia", "@kiwidepia", "@bulbapedia"]:
        site = ""
        if command == "@google":
            site = "Google"
        elif command == "@youtube":
            args = "site:youtube.com " + args
            site = "YouTube"
        elif command == "@omnimaga":
            args = "site:omnimaga.org " + args
            site = "Omnimaga"
        elif command == "@xkcd":
            args = "site:xkcd.com " + args
            site = "xkcd"
        elif command == "@tiplanet":
            args = "site:tiplanet.org " + args
            site = "TI-Planet"
        elif command == "@wikipedia" or command == "@kiwidepia":
            args = "site:en.wikipedia.org " + args
            site = "Wikipedia"
        elif command == "@bulbapedia":
            args = "site:bulbapedia.bulbagarden.net " + args
            site = "Bulbapedia"

        query = urllib.parse.urlencode({"q": args})
        url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&num=0&pws=0&hl=en&" + query
        prefix = "PRIVMSG " + channel + " :[\0032" + site + "\003] "
        try:
            response = json.loads((urllib.request.urlopen(url).read()).decode())["responseData"]["results"][0]
            return prefix + response["titleNoFormatting"] + " - " + response["unescapedUrl"]
        except IndexError:
            return prefix + "\002ERROR:\002 No results found"
    else:
        return ""

