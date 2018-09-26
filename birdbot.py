import logging
from discord import *
import yaml
import gvars

logging.basicConfig(level=logging.INFO)

# Load Config file for token
with open("config/config.yml", "r") as ymlfile:
	config = yaml.load(ymlfile)

# Client
client = Client()

# Voice
voiceclient = None
vplayer = None

# Discord token
token = config["discord"]["token"]

mprefix = "£"

@client.event
async def on_ready():
    print("Birdbot online!")

@client.event
async def on_message(message : Message):
    if not message.content.startswith(mprefix):
        return
    
    split = message.content.split(" ")
    command = split[0]
    command = command[1:]
    cargs = split[1:]

    if command == "ping":
        return await client.send_message(message.channel, "Pong!")

    # VOICE STUFF

    global voiceclient

    if command == "join":
        if message.author.voice.voice_channel:
            await client.send_message(message.channel, "Joining your channel {0}".format(message.author.nick))
            voiceclient = await client.join_voice_channel(message.author.voice.voice_channel)
        else:
            return await client.send_message(message.channel, "You are not in a voice channel.")
            
    if command == "leave":
        if voiceclient and voiceclient.is_connected():
            await voiceclient.disconnect()
        else:
            client.send_message(message.channel, "I'm not in a channel!")

    if command == "play":
        if not voiceclient or not voiceclient.is_connected():
            voiceclient = await client.join_voice_channel(message.author.voice.voice_channel)
        
        music = cargs[0]

        vplayer = await voiceclient.create_ytdl_player(music)
        vplayer.start()

        return await client.send_message(message.channel, "Now playing: {0}".format(vplayer.title))

    # Utilities

    if command == "listchan":
        chans = message.server.channels
        channel = ""
        for chan in chans:
            channel += ("{0} - {1}\n".format(chan.name, chan.id))
        return await client.send_message(message.channel, channel)
        

@client.event
async def on_member_join(member : Member):
    return await client.send_message(member.server.get_channel(gvars.general), "{0} has joined the server!".format(member.name))

@client.event
async def on_voice_state_update(before, after):
    print("on_voice_state_update called")
    bchan = before.voice.voice_channel
    achan = after.voice.voice_channel

    if achan == bchan:
        print("Same, returning")
        return

    return await client.send_message(before.server.get_channel(gvars.voicelog), "{0} has switched from {1} to {2}".format(before.name, bchan, achan))

client.run(token)