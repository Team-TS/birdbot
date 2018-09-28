import logging
from discord import *
import yaml
import gvars
import asyncio
import Song

logging.basicConfig(level=logging.INFO)

# Load Config file for token
with open("config/config.yml", "r") as ymlfile:
	config = yaml.load(ymlfile)

# Client
client = Client()

# Voice
voiceclient = None
vplayer = None
volume = 100.0
playqueue = []

# Discord token
token = config["discord"]["token"]

mprefix = "!"
async def checkplayback():
    global vplayer
    global playqueue
    while True:
        if len(playqueue) > 0 and vplayer and vplayer.is_done():
            await playnext()
        await asyncio.sleep(5)
    
async def enqueue(song : Song.Song):
    global playqueue
    playqueue.append(song)
    return

async def playnext():
    global playqueue
    global vplayer
    global volume
    if not voiceclient:
        return
    song = playqueue.pop(0)
    vplayer = await voiceclient.create_ytdl_player(song.songlink)
    vplayer.start()
    vplayer.volume = volume/100
    return await client.send_message(song.channel, "Now playing: {0} Volume:{1}% requested by {2}".format(vplayer.title,volume,song.user.name))


@client.event
async def on_ready():
    asyncio.Task(checkplayback())
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
    global playqueue
    global voiceclient
    global vplayer

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
        
        music = Song.Song(cargs[0], message.channel, message.author)
        await enqueue(music)
        
        if vplayer and vplayer.is_playing():
            return await client.send_message(message.channel, "Added to the queue.")

        heProtecc = False
        if heProtecc == False:
            heProtecc = True
            await playnext()
            heProtecc = False
            return await client.send_message(message.channel, "Now playing: {0}".format(vplayer.title))

    if command == "stop":
        if not vplayer or not vplayer.is_playing():
            return await client.send_message(message.channel, "I am not playing anything!")

        vplayer.stop()

    if command == "skip":
        if not vplayer or not vplayer.is_playing():
            return await client.send_message(message.channel, "I am not playing anything!")
        try:
            await client.send_message(message.channel, "Skipping song!")
            vplayer.stop()
	           await playnext()
        except Exception as e:
            return await client.send_message("ERROR: SKREK! : {0}".format(e))

 
    if command == "volume":
        if not vplayer:
            return
        try:
            global volume
            volume = float(cargs[0])
            if volume > 200:
                volume = 200.0
            vplayer.volume = volume/100
            await client.send_message(message.channel,"The volume is now: {0}%".format(volume)) 
        except Exception as e:
            return await client.send_message("ERROR: SKREK! : {0}".format(e))

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
    bchan = before.voice.voice_channel
    achan = after.voice.voice_channel

    if achan == bchan:
        return

    return await client.send_message(before.server.get_channel(gvars.voicelog), "{0} has switched from {1} to {2}".format(before.name, bchan, achan))


print(token)
client.run(token)
