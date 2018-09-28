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
commandqueue = []
cargs = 0
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
    asyncio.Task(process_commands())
    print("Birdbot online!")

@client.event
async def on_message(message : Message):
    global commandqueue
    if not message.content.startswith(mprefix):
        return
    if message.author.voice.voice_channel == None:
        return
    else:
        commandqueue.append(message)


async def process_commands():
    global commandqueue
    global cargs
    while True:
        if len(commandqueue) > 0:
            split = commandqueue[0].content.split(" ")
            command = split[0]
            command = command[1:]
            cargs = split[1:]
            switch = {
                "join" : join_function,
                "leave" : leave_function,
                "play" : play_function,
                "stop" : stop_function,
                "skip" : skip_function,
                "volume" : volume_function,
                "ping" : ping_function,
                "listchan" : listchan_function,
                "pause" : pause_function,
                "resume" : resume_function
                }
            result = switch.get(command)
            await result()
            commandqueue.pop(0)
        await asyncio.sleep(1)

@client.event
async def join_function():
    global commandqueue
    if commandqueue[0].author.voice.voice_channel:
        await client.send_message(commandqueue[0].channel, "Joining your channel {0}".format(commandqueue[0].author.nick))
        voiceclient = await client.join_voice_channel(commandqueue[0].author.voice.voice_channel)
    else:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel.")

@client.event
async def leave_function():
    global commandqueue
    global voiceclient
    if voiceclient and voiceclient.is_connected():
        await voiceclient.disconnect()
    else:
        client.send_message(commandqueue[0].channel, "I'm not in a channel!")

@client.event
async def play_function():
    global commandqueue
    global voiceclient
    global vplayer
    global cargs
    if not voiceclient or not voiceclient.is_connected():
        voiceclient = await client.join_voice_channel(commandqueue[0].author.voice.voice_channel)
        
    music = Song.Song(cargs[0], commandqueue[0].channel, commandqueue[0].author)
    await enqueue(music)
        
    if vplayer and vplayer.is_playing():
        return await client.send_message(commandqueue[0].channel, "Added to the queue.")
    
    await playnext()
    return await client.send_message(commandqueue[0].channel, "Now playing: {0}".format(vplayer.title))

@client.event
async def stop_function():
    global commandqueue
    global vplayer
    if not vplayer or not vplayer.is_playing():
        return await client.send_message(commandqueue[0].channel, "I am not playing anything!")

    vplayer.stop()

@client.event
async def skip_function():
    global commandqueue
    global vplayer
    if not vplayer or not vplayer.is_playing():
        return await client.send_message(commandqueue[0].channel, "I am not playing anything!")
    try:
        await client.send_message(commandqueue[0].channel, "Skipping song!")
        vplayer.stop()
        await playnext()
    except Exception as e:
        return await client.send_message("ERROR: SKREK! : {0}".format(e))

@client.event
async def volume_function():
    global commandqueue
    global vplayer
    if not vplayer:
        return
    try:
        global volume
        volume = float(cargs[0])
        if volume > 200:
            volume = 200.0
        vplayer.volume = volume/100
        await client.send_message(commandqueue[0].channel,"The volume is now: {0}%".format(volume)) 
    except Exception as e:
        return await client.send_message("ERROR: SKREK! : {0}".format(e))
@client.event
async def ping_function():
    global commandqueue
    if command == "ping":
        return await client.send_message(commandqueue[0].channel, "Pong!")

@client.event
async def listchan_function():
    global commandqueue
    chans = commandqueue[0].server.channels
    channel = ""
    for chan in chans:
        channel += ("{0} - {1}\n".format(chan.name, chan.id))
    return await client.send_message(commandqueue[0].channel, channel)
     
@client.event
async def pause_function():
    global commandqueue
    global vplayer
    vplayer.pause()
    return await client.send_message(commandqueue[0].channel, "Pausing the current song!")
    
@client.event
async def resume_function():
    global commandqueue
    global vplayer
    vplayer.resume()
    return await client.send_message(commandqueue[0].channel, "Resuming the current song!")

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
