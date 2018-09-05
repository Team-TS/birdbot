# Dependancies

import discord
import yaml
import classes
import chatfunc
import sqlstuff
import commands

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
	print("Birdbot online.")


# Commands
@client.event
async def on_message(message):
	outmsg = "Error"
	explode = message.content.split(" ")
	keyword = ""
	args = []

	if explode[0][0] != prefix:
		return
	
	print(explode)
	if len(explode) >= 1:
		keyword = explode[0][1:]
	if len(explode) >= 2:
		args = explode[1:]

	print(keyword)
	

	"""New object based command system"""

	if keyword == "output":
		command = commands.OutputText(explode[1:])
		output = await command.fire()
		return await client.send_message(message.channel, output)

	if keyword == "dice":
		if not args:
			return await client.send_message(message.channel, outmsg)
		
		dice = args[0]
		num = int(dice[0])
		value = int(dice[2:])
		command = commands.RollDice(num, value)
		output = await command.fire()
		return await client.send_message(message.channel, output)

	

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
coin - Tosses a standard coin.
dice <input> - Throws dice. Input format is 2d6. Example: :bird:dice 3d12```"""
		return await client.send_message(message.channel, outmsg)

client.run(config["discord"]["token"])
