""" Random useful functions for the bot"""

import discord
from random import choice
from random import randint


""" Listing ID of members and groups """

async def listAllIds(server):
    Sname = server.name
    Smembers = server.members

    rtn = "Listing all members on %s: \n \n" % Sname
    rtn += "Name (Nickname) - ID \n ```"

    for member in Smembers:
        id = str(member.id)
        name = str(member.name)
        nick = str(member.nick)
        rtn += name + " (" + nick + ")" + " - " + id + "\n"

    rtn += "```"

    return rtn

async def listAllGroups(server):
    Sname = server.name
    Sgroups = server.roles

    rtn = "Listing all roles on %s: \n \n" % Sname
    rtn += "Name - ID \n ```"

    for group in Sgroups:
        rtn += group.name + " - " + group.id + "\n"

    rtn += "```"
    return rtn

async def cointoss():
    """Coin toss"""
    result = choice(["Heads", "Tails"])
    return result

async def diceroll(num, sides):
    total = 0
    for dice in range(num):
        total += randint(1, sides)
    return total
