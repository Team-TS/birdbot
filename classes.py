class discordServer:
    name = ""
    serverid = ""

    def __init__(self, Name, Id):
        self.name = Name
        self.name = Id

class discordUser:
    name = ""
    nick = ""
    userid = ""
    suffix = ""
    isadmin = 0

    def __init__(self, Name, Nick, Userid, Suffix):
        self.name = Name
        self.nick = Nick
        self.userid = Userid
        self.suffix = Suffix
        self.isadmin = 0

class QuoteCategory:
    name = ""
    quotes = []

    def __init__(self, Name):
        self.name = Name
        self.quotes = []

class Quote:
    content = ""

    def __init__(self, Content):
        self.content = Content
