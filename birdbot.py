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

# Initialise function
@client.event
async def on_ready():
    asyncio.Task(checkplayback())
    asyncio.Task(process_commands())
    print("Birdbot online!")

# Async loop functions which control the bot.
async def checkplayback():
    global vplayer
    global playqueue
    global voiceclient
    while True:
        if voiceclient != None and vplayer != None:
            if len(playqueue) > 0 and voiceclient.is_connected() and vplayer.is_done():
                await playnext()
            if len(playqueue) == 0 and voiceclient.is_connected() and not vplayer.is_playing():
                await timeOut()
        await asyncio.sleep(5)

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
    return await client.send_message(song.channel, "Now playing: {0}. Volume: {1}%. requested by {2}.".format(vplayer.title,volume,song.user.name))

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
                    "resume" : resume_function,
                    "help" : help_function,
                    }
            result = switch.get(command, lambda: client.send_message(commandqueue[0].channel, "Invalid command, type !help for a list of commands!"))
            await result()
            commandqueue.pop(0)
        await asyncio.sleep(1)

# Non-client related functions.

async def timeOut():
    global playqueue
    global voiceclient
    time = 0
    while not vplayer.is_playing() and voiceclient.channel != None:
        time = time + 1
        print(time)
        if time == 30:
            await voiceclient.disconnect()
            voiceclient.channel = None
            return
        await asyncio.sleep(1)
    return

async def enqueue(song : Song.Song):
    global playqueue
    playqueue.append(song)
    return

async def join_function():
    global commandqueue
    global voiceclient
    global vplayer
    await client.send_message(commandqueue[0].channel, "Joining your channel {0}".format(commandqueue[0].author))
    if not voiceclient or not vplayer:
        voiceclient = await client.join_voice_channel(commandqueue[0].author.voice.voice_channel)
        vplayer = await voiceclient.create_ytdl_player('https://www.youtube.com/watch?v=cdwal5Kw3Fc')
        vplayer.start()
        return
    elif not voiceclient.is_connected():
        voiceclient = await client.join_voice_channel(commandqueue[0].author.voice.voice_channel)
    elif voiceclient or voiceclient.is_connected():
        await voiceclient.move_to(commandqueue[0].author.voice.voice_channel)
        await vplayer.stop()
        return
    else:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel.")

async def leave_function():
    global commandqueue
    global voiceclient
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel!")
    if voiceclient and voiceclient.is_connected():
        await voiceclient.disconnect()
        voiceclient.channel = None
    else:
        client.send_message(commandqueue[0].channel, "I'm not in a channel!")

async def play_function():
    global commandqueue
    global voiceclient
    global vplayer
    global cargs
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel.")

    if not voiceclient or not voiceclient.is_connected():
        voiceclient = await client.join_voice_channel(commandqueue[0].author.voice.voice_channel)
        
    music = Song.Song(cargs[0], commandqueue[0].channel, commandqueue[0].author)
    await enqueue(music)
        
    if vplayer and vplayer.is_playing():
        return await client.send_message(commandqueue[0].channel, "Added to the queue.")
    
    await playnext()
    return

async def stop_function():
    global commandqueue
    global vplayer
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel!")
    if not vplayer or not vplayer.is_playing():
        return await client.send_message(commandqueue[0].channel, "I am not playing anything!")

    vplayer.stop()

async def skip_function():
    global commandqueue
    global vplayer
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel!")
    if not vplayer or not vplayer.is_playing():
        return await client.send_message(commandqueue[0].channel, "I am not playing anything!")
    try:
        await client.send_message(commandqueue[0].channel, "Skipping song!")
        vplayer.stop()
        await playnext()
    except Exception as e:
        return await client.send_message("ERROR: SKREK! : {0}".format(e))

async def volume_function():
    global commandqueue
    global vplayer
    global voiceclient
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel!")
    if not voiceclient or not voiceclient.is_connected():
        voiceclient = await client.join_voice_channel(commandqueue[0].author.voice.voice_channel)
    try:
        global volume
        volume = float(cargs[0])
        if volume > 200:
            volume = 200.0
        vplayer.volume = volume/100
        await client.send_message(commandqueue[0].channel,"The volume is now: {0}%".format(volume)) 
    except Exception as e:
        return await client.send_message("ERROR: SKREK! : {0}".format(e))

async def ping_function():
    global commandqueue
    return await client.send_message(commandqueue[0].channel, "Pong!")

async def listchan_function():
    global commandqueue
    chans = commandqueue[0].server.channels
    channel = ""
    for chan in chans:
        channel += ("{0} - {1}\n".format(chan.name, chan.id))
    return await client.send_message(commandqueue[0].channel, channel)
     
async def pause_function():
    global commandqueue
    global vplayer
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel!")
    vplayer.pause()
    return await client.send_message(commandqueue[0].channel, "Pausing the current song!")
    
async def resume_function():
    global commandqueue
    global vplayer
    if commandqueue[0].author.voice.voice_channel == None:
        return await client.send_message(commandqueue[0].channel, "You are not in a voice channel!")
    vplayer.resume()
    return await client.send_message(commandqueue[0].channel, "Resuming the current song!")

async def help_function():
    global commandqueue
    await client.send_message(commandqueue[0].channel, "Voice channel commands:\n1: !join\n2: !leave\n3: !play 'insert youtube link'\n4: !stop\n5: !skip\n6: !volume 'insert volume between 0 and 200'\n7: !ping\n8: !listchan\n9: !pause\n10: !resume\n11: !help")
    return await client.send_message(commandqueue[0].channel, "Text channel commands:\n1:!help\n2:!ping\n3:!listchan")
# Client related functions.

@client.event
async def on_message(message : Message):
    global commandqueue
    if not message.content.startswith(mprefix):
        return
    else:
        commandqueue.append(message)

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
