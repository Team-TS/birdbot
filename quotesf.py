import classes
import sqlstuff
from random import choice

class Friend:
    name = ""
    l_name = ""
    quotes = []
    discordid = ""
    discordsuffix = ""

    def __init__(self, name):
        self.name = name
        self.l_name = name.lower()
        self.quotes = generate_quotes(name)

    def assignDiscord(self, discord, discordsuf):
        self.discordid = discord
        self.discordsuffix = discordsuf

    def addQuotes(self, quote):
        self.quotes.append(quote)
        add_new_quote(self.name, quote)

    async def pickQuote(self):
        return choice(self.quotes)

    def listQuotes(self):
        return self.quotes


def generate_quotes(peep):
    try:
        peepname = peep
        with open("quotes/" + peepname + ".txt", "r") as quotefile:
            quotes = quotefile.read()
            quotes = quotes.split("\n")
            quotes = list(filter(None, quotes))
            return quotes
    except FileNotFoundError:
        print("File not found: " + peepname + ".txt")
        return []

def add_new_quote(peep, quote):
    peep = peep.lower()
    try:
        with open("quotes/" + peep + ".txt", "a") as quotefile:
            quotefile.write(quote + "\n")
    except FileNotFoundError:
        print("File not found")


james = Friend("James")
ben = Friend("Ben")
adam = Friend("Adam")
owen = Friend("Owen")
peter = Friend("Peter")
merlin = Friend("Merlin")
wigster = Friend("Wigster")
scott = Friend("Scott")
marisa = Friend("Marisa")
saxon = Friend("Saxon")
terminator = Friend("Terminator")
rand = Friend("Random")

all_friends = [james, ben, adam, owen, peter, merlin, wigster, scott, marisa, saxon, terminator, rand]

""" New quoting system with database"""

def create_quote_category(categoryname, serverid):
    db = sqlstuff.connect_db()
    with db.cursor() as cursor:
        qry = "SELECT `categoryname` FROM `quote_category`;"
        cursor.execute(qry)
        results = cursor.fetchall()
        if not results:
            qry = "INSERT INTO `quote_category` (`qcid`, `categoryname`, `serverid`) VALUES (NULL, '{0}', '{1}');".format(categoryname, serverid)
            cursor.execute(qry)
            db.commit()
            return 1
        else:
            return 0

def get_quote_categories(serverid):
    db = sqlstuff.connect_db()
    with db.cursor() as cursor:
        qry = "SELECT `categoryname` FROM `quote_category`;"
        cursor.execute(qry)
        results = cursor.fetchall()
        return results

def category_lookup(category, serverid):
    db = sqlstuff.connect_db()
    cat = category.lower()
    qry = "SELECT `qcid` FROM `quote_category` WHERE `categoryname` LIKE %s AND `serverid` LIKE %s;"
    with db.cursor() as cursor:
        cursor.execute(qry, [cat, serverid])
        results = cursor.fetchone()
        if results:
            return results
        else:
            return 0

def add_quote(categoryid, quote):
    quote = str(quote)
    db = sqlstuff.connect_db()
    qry = "INSERT INTO `quotes` (`qid`, `categoryid`, `quote`) VALUES (NULL, %s, %s);"
    with db.cursor() as cursor:
        cursor.execute(qry, [categoryid, quote])
        db.commit()
        return 1

def get_quotes(categoryid):
    db = sqlstuff.connect_db()
    qry = "SELECT `quote` FROM `quotes` WHERE `categoryid`=%s"
    with db.cursor() as cursor:
        cursor.execute(qry, categoryid)
        results = cursor.fetchall()
        return results
