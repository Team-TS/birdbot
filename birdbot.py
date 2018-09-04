# Dependancies

import discord
import yaml
import classes
import chatfunc
import quotesf
import sqlstuff

with open("config/config.yml", "r") as ymlfile:
	config = yaml.load(ymlfile)

prefix = "\U0001F426"
usergroupid = "410109275986460672"
admingroupid = "387024327654113280"
admins = []

client = discord.Client()


# When the bot starts
@client.event
async def on_ready():
	reload_admins()
	print("Birdbot online.")


# Commands
@client.event
async def on_message(message):
	outmsg = "Error"
	explode = message.content.split(" ")

	"""Random"""

	if explode[0] == prefix + "coin":
		outmsg = await chatfunc.cointoss()
		return await client.send_message(message.channel, outmsg)

	if explode[0] == prefix + "ping":
		outmsg = "Pong!"
		return await client.send_message(message.channel, outmsg)

	if explode[0] == prefix + "dice":
		if len(explode) > 1:
			dice = explode[1].split("d")
			if len(dice) != 2:
				return await client.send_message(message.channel, outmsg)
			numdice = int(dice[0])
			sides = int(dice[1])
			rtn = await chatfunc.diceroll(numdice, sides)
			outmsg = rtn
			return await client.send_message(message.channel, outmsg)

	"""cance"""

	if explode[0] == prefix + "reacc":
		if message.author == client.user:
			return
		if not check_admin_perms(message.author):
			return

		num = 1

		if len(explode) >= 2:
			reacc = explode[1]
		if len(explode) >= 3:
			num = int(explode[2])

		for msg in reversed(client.messages):
			if msg.channel == message.channel and msg != message and num > 0:
				await client.add_reaction(msg, reacc)
				num = num - 1

		await client.delete_message(message)
		return

	"""Help"""

	if explode[0] == prefix + "help":
		outmsg = """**Commands**
Prefix all comamnds with :bird:
```
help - Displays help for commands.
quote <name> - Picks a random quote by <name>.
addquote <name> <quote> - Add a quote for the listed <name>.
listquotes <name> - Lists current quotes in the library for <name>.
coin - Tosses a standard coin.
dice <input> - Throws dice. Input format is 2d6. Example: :bird:dice 3d12```"""
		return await client.send_message(message.channel, outmsg)

	"""Admin related"""

	if explode[0] == prefix + "listid":
		if check_admin_perms(message.author):
			outmsg = await chatfunc.listAllIds(message.server)
			return await client.send_message(message.channel, outmsg)

	if explode[0] == prefix + "listroles":
		if check_admin_perms(message.author):
			outmsg = await chatfunc.listAllGroups(message.server)
			return await client.send_message(message.channel, outmsg)

	if explode[0] == prefix + "addmin":
		if not check_admin_perms(message.author):
			outmsg = "Permissions error: You are not authorised to use: addmin"
			return await client.send_message(message.channel, outmsg)
		else:
			if explode[1]:
				if message.mentions:
					for user in message.mentions:
						if await sqlstuff.db_add_admin(user.id, user.name, user.discriminator, message.server.id):
							outmsg = "New botmin added '{0}'.".format(user.name)
							reload_admins()
						else:
							outmsg = "User '{0}' is already a botmin.".format(user.name)
						await client.send_message(message.channel, outmsg)

	if explode[0] == prefix + "delmin":
		if not check_admin_perms(message.author):
			outmsg = "Permissions error: You are not authorised to use: delmin"
			return await client.send_message(message.channel, outmsg)
		else:
			if explode[1]:
				if message.mentions:
					for user in message.mentions:
						if await sqlstuff.db_del_admin(user.id):
							outmsg = "Deleted admin: '{0}'".format(user.name)
							reload_admins()
							await client.send_message(message.channel, outmsg)
						else:
							outmsg = "User '{0}' not deleted. Not found in table.".format(user.name)
							await client.send_message(message.channel, outmsg)

	if explode[0] == prefix + "printadmins":
		print(admins)
		outmsg = "Admin IDs \n"
		for admin in admins:
			outmsg += admin + "\n"
		return await client.send_message(message.channel, outmsg)

"""Permissions"""


def check_perms(author):
	usergroups = author.roles
	for role in usergroups:
		if role.id == usergroupid:
			return 1
	return 0


def check_admin_perms(author):
	for admin in admins:
		if author.id == admin:
			return 1
	return 0


def reload_admins():
	global admins
	admins = sqlstuff.load_admins()
	print("Admins reloaded.")
	return


client.run(config["discord"]["token"])
