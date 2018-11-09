import gvars
import Song
import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from Config import Config
import urllib.request
import json

# Load Config file for token
config = Config()
# yapi key
apikey = "AIzaSyAubVJo-rkx0FBDPhEs3yncu0Rb0AmCTsM"

# Client
client = commands.Bot(command_prefix = '!')
#Remove the default help command.
client.remove_command('help')
# Discord token
token = Config.token
#vplayer and voiceclient holders
vplayer = None
voiceclient = None
#initial caller
caller = None
#votes
votelist = []

#searchlist
searchlist = []

#Player stuff
volumechange = 100.0
playqueue = []


# Initialise function
@client.event
async def on_ready():
    asyncio.Task(Autoplay())
    print("Birdbot online!")

@client.event
async def on_message(message):
    if message.author.bot == True:
        return
    elif message.channel.name == 'bot':
        await client.process_commands(message)
    else:
        await client.send_message(message.channel, "Please enter the command again into the bot text channel!")
    return

async def Autoplay():
    global playqueue
    global vplayer
    global voiceclient
    global volumechange
    countdownfired = False
    while True:
        print("Test")
        if voiceclient != None and vplayer != None:
            if voiceclient.is_connected() != False:
                if len(playqueue) >= 1 and vplayer.is_playing() == False:
                    vplayer = await voiceclient.create_ytdl_player(playqueue[0].songlink)
                    vplayer.start()
                    vplayer.volume = volumechange/100
                    await displayembed("Playing")
                    playqueue.pop(0)
                elif len(playqueue) == 0 and vplayer.is_done() == True and countdownfired == False:
                    countdownfired = True
                    x = asyncio.Task(countdown())
                    if x == False:
                        countdownfired = x
        await asyncio.sleep(5)

async def countdown():
    global vplayer
    global voiceclient
    global caller
    time = 0
    while not vplayer.is_playing() and voiceclient.channel != None:
        time = time + 1
        if time == 30:
             await voiceclient.disconnect()
             voiceclient.channel = None
             caller = None
             vplayer.stop()
        await asyncio.sleep(1)
    x = False
    return x

@client.event
async def on_command_error(self, error):
    await client.send_message(client.get_channel(gvars.bot), "Invalid command! Please type !help to see all available commands!")
    return

async def enqueue(ctx):
    global playqueue
    split = ctx.message.content.split(" ")
    link = split[1]
    music = Song.Song(link, ctx.message.channel, ctx.message.author)
    playqueue.append(music)
    return

@client.command(pass_context=True)
async def volume(ctx):
    global volumechange
    global vplayer
    global voiceclient
    split = ctx.message.content.split(" ")
    link = int(split[1])
    if voiceclient == None or voiceclient.is_connected() == False:
        await join.invoke(ctx)
    elif ctx.message.author.voice.voice_channel == voiceclient.channel:
        if link < 0 or link > 200:
            await client.send_message(client.get_channel(gvars.bot), "Volume change value is too high or low, the volume will remain at {0}.!".format(volumechange))
        else:
            volumechange = link
            vplayer.volume = volumechange/100
            await client.send_message(client.get_channel(gvars.bot), "The bot's volume is now at: {0}%!".format(volumechange))
    else:
        await client.send_message(client.get_channel(gvars.bot), "You are not in the bots channel!")
    return


@client.command(pass_context=True)
async def play(ctx):
    global vplayer
    global voiceclient
    global playqueue
    if voiceclient == None or voiceclient.is_connected() == False:
        await join.invoke(ctx)
        await enqueue(ctx)
    elif ctx.message.author.voice.voice_channel == voiceclient.channel:
        await enqueue(ctx)
    else:
        await client.send_message(client.get_channel(gvars.bot), "You are not in the bots channel!")
    return


@client.command(pass_context=True)
async def join(ctx):
    global voiceclient
    global vplayer
    global caller
    if voiceclient == None:
        caller = ctx.message.author
        voiceclient = await client.join_voice_channel(ctx.message.author.voice.voice_channel)
        vplayer = voiceclient.create_stream_player(None)
        vplayer.stop()
    elif voiceclient.is_connected() == False:
        caller = ctx.message.author
        voiceclient = await client.join_voice_channel(ctx.message.author.voice.voice_channel)
    elif str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" and voiceclient.is_connected() == True:
        caller = ctx.message.author
        await voiceclient.move_to(ctx.message.author.voice.voice_channel)
    else:
        await client.send_message(client.get_channel(gvars.bot), "The bot is already in another channel!")
    return

@client.command(pass_context=True)
async def leave(ctx):
    global voiceclient
    global vplayer
    global caller
    if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" or caller == ctx.message.author or ctx == "leave":
        await voiceclient.disconnect()
        voiceclient.channel = None
        caller = None
        vplayer.stop()
    return

@client.command(pass_context=True)
async def skip(ctx):
    await stop.invoke(ctx)
    return

@client.command(pass_context=True)
async def stop(ctx):
    global vplayer
    global voiceclient
    global votelist
    message = ctx.message.content
    message = message.replace("!","")
    message = message if message != None else "stop"
    if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin":
        await client.send_message(client.get_channel(gvars.bot), "The {0} vote has passed!".format(message))
        votelist.clear()
        vplayer.stop()
    else:
        if str(discord.utils.get(votelist, name = ctx.message.author)) == None:
            votelist.append(ctx.message.author)
            if len(votelist) >= round(len(voiceclient.channel.voice_members)/2):
                for name in votelist:
                    if str(discord.utils.get(voiceclient.channel.voice_members, name = votelist[name])) != votelist[name]:
                        del votelist[name]
                if len(votelist) >= round(len(voiceclient.channel.voice_members)/2):
                    await client.send_message(client.get_channel(gvars.bot), "The {0} vote has passed!".format(message))
                    vplayer.stop()
                    votelist.clear()
                else:
                    await client.send_message(client.get_channel(gvars.bot), "User: {0} has voted to {2} the music bot, {1} more votes are required for this to pass!".format(ctx.message.author, round(len(voiceclient.channel.voice_members)/2) - len(votelist), message))
        else:
            await client.send_message(client.get_channel(gvars.bot), "You have already voted!")
    return

@client.command(pass_context=True)
async def resume(ctx):
    global voiceclient
    global vplayer
    global caller
    if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" or caller == ctx.message.author:
        vplayer.resume()
    return

@client.command(pass_context=True)
async def pause(ctx):
    global voiceclient
    global vplayer
    global caller
    if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" or caller == ctx.message.author:
        vplayer.pause()
    return

@client.command(pass_context=True)
async def help(ctx):
        embed = discord.Embed(
            colour = discord.Colour.orange()
            )
        embed.set_author(name = 'Commands')
        embed.add_field(name = '1: !help', value = 'Provides a list of all available commands.', inline = True)
        embed.add_field(name = '2: !join', value = 'Requests the bot to join the channel you are currently in, Admins are the only ones who can move the bot via this command once it is in a channel.', inline = True)
        embed.add_field(name = '3: !leave', value = 'Requests the bot to leave the channel, Admins are the only ones who can request the bot to leave aside from the initial caller.', inline = True)
        embed.add_field(name = '4: !play "Youtube Link"', value = 'Enqueues a song to be played by the bo, can only be done if you are in the bots channel.', inline = True)
        embed.add_field(name = '5: !stop', value = 'Stops the current song being played by the bot, requires a majority vote or can be instantly passed by an admin.', inline = True)
        embed.add_field(name = '6: !skip', value = 'Skips the current song being played by the bot, requires a majority vote or can be instantly passed by an admin.', inline = True)
        embed.add_field(name = '7: !pause', value = 'Pauses the bot, requires the caller or an admin.', inline = True)
        embed.add_field(name = '8: !resume', value = 'Resumes the bot, requires the caller or an admin', inline = True)
        await client.send_message(ctx.message.author, embed = embed)
        return


async def displayembed(temp):
    global vplayer
    global playqueue
    #if temp == "Search":
    #    embed = discord.Embed(
    #        title = url,
    #        colour = discord.Colour.blue()
    #        )
    #    embed.set_author(name = 'Added to queue:', avatar_url = author.avatar_url)
    #    embed.set_thumbnail(url = image)
    #    embed.add_field(name = 'Channel:', value = duration, inline = True)
    #    embed.add_field(name = 'Estimated time until playing:', value = durationtillplayed, inline = True)
    #    embed.add_field(name = 'Song duration:', value = duration, inline = False)
    #    embed.add_field(name = 'Position in queue:', value = duration, inline = False)
    #    await client.send_message(client.get_channel(gvars.bot), embed = embed)
    songduration = divmod(vplayer.duration,60)
    if temp == "Playing":
        embed = discord.Embed(
            title = vplayer.title,
            colour = discord.Colour.blue()
            )
        embed.set_author(name = 'Now Playing:',icon_url = 'http://www.clker.com/cliparts/j/W/O/s/N/o/windows-media-player-play-button-md.png')
        embed.set_thumbnail(url = "https://img.youtube.com/vi/{0}/default.jpg".format(await youtubeurlsnipper(vplayer.url)))
        embed.add_field(name = 'Song duration:' , value = '{0}m {1}s'.format(songduration[0],songduration[1]), inline = True)
        embed.add_field(name = 'Volume:' , value = "{0}%".format(vplayer.volume*100) , inline = True)
        embed.add_field(name = 'Requested by:' , value = playqueue[0].user , inline = True)
        embed.add_field(name = 'Up next:' , value = await nextvideodata(playqueue[1].songlink) if len(playqueue) > 1 else "Nothing.", inline = True)
        await client.send_message(client.get_channel(gvars.bot), embed = embed)
    return

async def nextvideodata(x):
    global apikey
    url = x
    id = await youtubeurlsnipper(url)
    data = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/videos?id={0}&key={1}&part=snippet,contentDetails,statistics,status".format(id,apikey))
    title = json.load(data)["items"][0]["snippet"]["title"]
    return title

async def youtubeurlsnipper(x):
    url = x
    if len(url) > 43:
        url = url[32:43]
    else:
        url = url[32:]
    return url

@client.event
async def on_member_join(member):
    try:
        if str(discord.utils.get(member.roles, name ='Regular')) != "Regular":
            role = discord.utils.get(on_member_join.server.roles, name ='Regular')
            await client.add_roles(member, role)
    except Exception as error:
        return print("Error trying to get the 'Regular' server role:'" + error + "'")
    
    await client.send_message(member.server.get_channel(gvars.general), "{0} has joined the server!".format(member.name))

@client.event
async def on_voice_state_update(before, after):
    bchan = before.voice.voice_channel
    achan = after.voice.voice_channel

    if achan == bchan:
        return
    await client.send_message(before.server.get_channel(gvars.voicelog), "{0} has switched from {1} to {2}".format(before.name, bchan, achan))


client.run(token)
