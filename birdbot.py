import gvars
import Song
import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from Config import Config
import urllib.request
import json
import io
import os
import requests
from datetime import datetime

#botVersion
botVersion = "V1.2.4"
#errordump
file = None

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
#countdown bool
countdownbool = False
#timer
timer = 0
#error log
errorloglist = []
#votes
votelist = {}

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
    global vplayer
    global voiceclient
    try:
        if message.author.bot == True:
            return
        elif message.channel.name == 'bot':
            await client.process_commands(message)
        elif message.content.startswith("!"):
            await client.send_message(message.channel, "Please enter the command again into the bot text channel!")
    except Exception as e:
        await write_errors("Exception occured in on_message: {0} at {1}".format(e, str(datetime.now())))
    return

async def Autoplay():
    global playqueue
    global countdownbool
    global vplayer
    global voiceclient
    global volumechange
    global votelist 
    try:
        while True:
            if voiceclient != None and vplayer != None:
                if voiceclient.is_connected() != False:
                    if len(playqueue) >= 1 and vplayer.is_playing() == False:
                        votelist.clear()
                        vplayer = await voiceclient.create_ytdl_player(playqueue[0].songlink, ytdl_options=None, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
                        vplayer.start()
                        vplayer.volume = volumechange/100
                        await displayembed("Playing")
                        playqueue.pop(0)
                    else:
                        if countdownbool == False:
                            countdownbool = True
                            asyncio.Task(countdown())
            await asyncio.sleep(5)
    except Exception as e:
        await write_errors("Exception occured in Autoplay: {0} at {1}".format(e, str(datetime.now())))
        asyncio.Task(Autoplay())
    return

async def countdown():
    global vplayer
    global countdownbool
    global voiceclient
    global caller
    global timer
    try:
        while not vplayer.is_playing() and voiceclient.channel != None:
            timer = timer + 1
            if timer == 30:
                 await voiceclient.disconnect()
                 voiceclient.channel = None
                 caller = None
                 vplayer.stop()
            await asyncio.sleep(1)
        countdownbool = False
        timer = 0
    except Exception as e:
        await write_errors("Exception occured in countdown: {0} at {1}".format(e, str(datetime.now())))
    return

async def write_errors(error):
    try:
        global file
        file = open("BirdBotErrorDump.txt", 'a+')
        file.write("{0} \n".format(error))
        file.close()
    except Exception as e:
        await write_errors("Exception occured in write_errors: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def emptyerrorfile(ctx):
    try:
        if str(discord.utils.get(ctx.message.author.roles, name ='Dev')) == "Dev":
            global file
            file = open("BirdBotErrorDump.txt", 'w')
            file.close()
            await client.send_message(client.get_channel(gvars.bot), "Error file emptied!")
        else:
            await client.send_message(client.get_channel(gvars.bot), "This is a dev only command!")
    except Exception as e:
        await write_errors("Exception occured in emptyerrorfile: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def errorfile(ctx):
    try:
        global file
        if str(discord.utils.get(ctx.message.author.roles, name ='Dev')) == "Dev":
            i = 0
            file = open("BirdBotErrorDump.txt")
            lines = file.read().splitlines()
            file.close()
            if len(lines) > 0:
                for line in lines:
                    await client.send_message(client.get_channel(gvars.bot), "Error line {0}: {1}".format(i,line))
                    i = i + 1
            else:
                await client.send_message(client.get_channel(gvars.bot), "The error file is empty!")
        else:
            await client.send_message(client.get_channel(gvars.bot), "This is a dev only command!")
    except Exception as e:
        await write_errors("Exception occured in errorfile: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def botversion(ctx):
    global botVersion
    try:
        if str(discord.utils.get(ctx.message.author.roles, name ='Dev')) == "Dev":
            await client.send_message(client.get_channel(gvars.bot), botVersion)
    except Exception as e:
        await write_errors("Exception occured in botversion: {0} at {1}".format(e, str(datetime.now())))
    return

@client.event
async def on_command_error(self, error):
    global errorloglist
    try:
        error = error.message.content
        await client.send_message(client.get_channel(gvars.bot), "Invalid command! Please type !help to see all available commands and their conditions for use! This was the command that caused the error: {0}".format(error))
        errorloglist.append(error+" at "+str(datetime.now()))
        if len(errorloglist) >= 20:
            errorloglist.pop(0)
    except Exception as e:
        await write_errors("Exception occured in on_command_error: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def errorlog(ctx):
    global errorloglist
    try:
        if str(discord.utils.get(ctx.message.author.roles, name ='Dev')) == "Dev":
            if len(errorloglist) == 0:
                await client.send_message(client.get_channel(gvars.bot), "No errors to report!")
            else:
                for error in errorloglist:
                    await client.send_message(client.get_channel(gvars.bot), error)
    except Exception as e:
        await write_errors("Exception occured in errorlog: {0} at {1}".format(e, str(datetime.now())))
    return

async def enqueue(ctx):
    global playqueue
    try:
        split = ctx.message.content.split(" ")
        split = split[1]
        split = split.split("&")
        link = split[0]
        music = Song.Song(link, ctx.message.channel, ctx.message.author)
        await displayembed("Enqueue",ctx)
        playqueue.append(music)
    except Exception as e:  
        await write_errors("Exception occured in enqueue: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def volume(ctx):
    global volumechange
    global vplayer
    global voiceclient
    try:
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
                await client.send_message(client.get_channel(gvars.bot), "The bots volume is now at: {0}%!".format(volumechange))
        else:
            await client.send_message(client.get_channel(gvars.bot), "You are not in the bots channel!")
    except Exception as e:
        await write_errors("Exception occured in volume: {0} at {1}".format(e, str(datetime.now())))
    return


@client.command(pass_context=True)
async def play(ctx):
    global vplayer
    global voiceclient
    global playqueue
    try:
        if voiceclient == None or voiceclient.is_connected() == False:
            await join.invoke(ctx)
            await enqueue(ctx)
        elif ctx.message.author.voice.voice_channel == voiceclient.channel:
            await enqueue(ctx)
        else:
            await client.send_message(client.get_channel(gvars.bot), "You are not in the bots channel!")
    except Exception as e:
        await write_errors("Exception occured in play: {0} at {1}".format(e, str(datetime.now())))
    return


@client.command(pass_context=True)
async def join(ctx):
    global voiceclient
    global vplayer
    global caller
    try:
        if voiceclient == None:
            caller = ctx.message.author
            voiceclient = await client.join_voice_channel(ctx.message.author.voice.voice_channel)
            vplayer = voiceclient.create_stream_player(None)
        elif voiceclient.is_connected() == False:
            caller = ctx.message.author
            voiceclient = await client.join_voice_channel(ctx.message.author.voice.voice_channel)
        elif str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" and voiceclient.is_connected() == True:
            caller = ctx.message.author
            await voiceclient.move_to(ctx.message.author.voice.voice_channel)
        else:
            await client.send_message(client.get_channel(gvars.bot), "The bot is already in a channel!")
        vplayer.stop()
    except Exception as e:
        await write_errors("Exception occured in join: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def search(ctx):
    global voiceclient
    global apikey
    global searchlist
    global timer
    try:
        if voiceclient == None:
            await join.invoke(ctx)
        if (len(ctx.message.content) <= 7):
            await client.send_message(client.get_channel(gvars.bot), "No topic for search entered!")
            return
        split = ctx.message.content.split(" ")
        searchContent = split[1:]
        url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=relevance&q={0}&type=video&key={1}'.format(searchContent,apikey)
        responce = requests.get(url, verify=True)
        data = responce.json()
        x = 0
        id = []
        title = []
        while x < 50:
            id.append(data['items'][x]['id']['videoId'])
            title.append(data['items'][x]['snippet']['title'])
            x = x + 1
        a = 0
        while True:
            timer = -40
            await displayembed("Search",ctx,title,a)
            selection = await client.wait_for_message(timeout = 40,author = ctx.message.author)
            if selection.content == "x" or selection.content == "cancel" or selection.content == "Cancel":
                return
            elif selection.content == "+" or selection.content == "next" or selection.content == "Next":
                if a != 40:
                    a = a + 10
                else:
                    await client.send_message(client.get_channel(gvars.bot),"You cannot increase this value any further!")
            elif selection.content == "-" or selection.content == "back" or selection.content == "Back":
                if a != 0:
                    a = a - 10
                else:
                    await client.send_message(client.get_channel(gvars.bot),"You cannot decrease this value any further!")
            else:
                if selection.content.isdigit() == True:
                    selection = int(selection.content)
                    if selection < 1 or selection > 10:
                        await client.send_message(client.get_channel(gvars.bot),"Number is too high/low. Please search again in the bot channel to try again.")
                        return
                    else:
                        selection = selection + a - 1
                        ctx.message.content = "!search https://www.youtube.com/watch?v={0}".format(id[selection])
                        await enqueue(ctx)
                        return
                else:
                    await client.send_message(client.get_channel(gvars.bot),"Incorrect input, please see the bottom of the search function for more info or type !help.")
    except Exception as e:
        await write_errors("Exception occured in search: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def leave(ctx):
    global voiceclient
    global vplayer
    global caller
    try:
        if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" or caller == ctx.message.author or ctx == "leave":
            await voiceclient.disconnect()
            voiceclient.channel = None
            caller = None
            vplayer.stop()
    except Exception as e:
        await write_errors("Exception occured in leave: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def skip(ctx):
    try:
        await stop.invoke(ctx)
    except Exception as e:
        await write_errors("Exception occured in skip: {0} at {1}".format(e, str(datetime.now())))
    return


@client.command(pass_context=True)
async def stop(ctx):
    global vplayer
    global voiceclient
    global votelist
    try:
        # check to see if the bot exists
        if vplayer == None or voiceclient == None or voiceclient.is_connected() == False or vplayer.is_playing() == False:
            await client.send_message(client.get_channel(gvars.bot), "Bot does not exist yet.")
            return
        # breakdown content of message, this is used to change the dialogue from stop to skip.
        message = ctx.message.content
        message = message.replace("!","")
        message = message if message != None else "stop"
        authorindex = ctx.message.author
        if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin":
            await client.send_message(client.get_channel(gvars.bot), "The {0} vote has passed!".format(message))
            votelist.clear()
            vplayer.stop()
        else:
            if ('{0}'.format(authorindex) in votelist) == False:
                votelist['{0}'.format(authorindex)] = ctx.message.author
                if len(votelist) >= round(len(voiceclient.channel.voice_members)/2):
                    # Check the existing list to see if everyone is in the channel who is in the list, if they are not remove them.
                    for name in votelist.copy():
                        if discord.utils.get(voiceclient.channel.voice_members, name = votelist[name]) == None:
                            del votelist[name]
                    if len(votelist) >= round(len(voiceclient.channel.voice_members)/2) or len(voiceclient.channel.voice_members) < 3:
                        await client.send_message(client.get_channel(gvars.bot), "The {0} vote has passed!".format(message))
                        vplayer.stop()
                        votelist.clear()
                        return
                authorindex = str(ctx.message.author).rsplit('#', 1)
                authorindex = authorindex[0]
                await client.send_message(client.get_channel(gvars.bot), "{0} has voted to {2} the music bot, {1} more votes are required for this to pass!".format(authorindex, round(len(voiceclient.channel.voice_members)/2) - len(votelist), message))
            else:
                await client.send_message(client.get_channel(gvars.bot), "You have already voted!")
    except Exception as e:
        await write_errors("Exception occured in stop: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def resume(ctx):
    global voiceclient
    global vplayer
    global caller
    try:
        if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" or caller == ctx.message.author:
            vplayer.resume()
    except Exception as e:
        await write_errors("Exception occured in resume: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def pause(ctx):
    global voiceclient
    global vplayer
    global caller
    try:
        if str(discord.utils.get(ctx.message.author.roles, name ='Admin')) == "Admin" or caller == ctx.message.author:
            vplayer.pause()
    except Exception as e:
        await write_errors("Exception occured in pause: {0} at {1}".format(e, str(datetime.now())))
    return

@client.command(pass_context=True)
async def help(ctx):
    try:
        embed = discord.Embed(
            colour = discord.Colour.orange()
            )
        embed.set_author(name = 'Commands')
        embed.add_field(name = '1: !help', value = 'Provides a list of all available commands.', inline = True)
        embed.add_field(name = '2: !join', value = 'Requests the bot to join the channel you are currently in, Admins are the only ones who can move the bot via this command once it is in a channel.', inline = True)
        embed.add_field(name = '3: !leave', value = 'Requests the bot to leave the channel, Admins are the only ones who can request the bot to leave aside from the initial caller.', inline = True)
        embed.add_field(name = '4: !play "Youtube Link"', value = 'Enqueues a song to be played by the bot, can only be done if you are in the bots channel.', inline = True)
        embed.add_field(name = '5: !stop', value = 'Stops the current song being played by the bot, requires a majority vote or can be instantly passed by an admin.', inline = True)
        embed.add_field(name = '6: !skip', value = 'Skips the current song being played by the bot, requires a majority vote or can be instantly passed by an admin.', inline = True)
        embed.add_field(name = '7: !pause', value = 'Pauses the bot, requires the caller or an admin.', inline = True)
        embed.add_field(name = '8: !resume', value = 'Resumes the bot, requires the caller or an admin', inline = True)
        embed.add_field(name = '9: !search "search parameters"', value = 'Searches Youtube for the top 50 videos matching your parameters (only shows 10 at a time), type the number you want to play. This will timeout after 20 seconds.', inline = True)
        embed.add_field(name = '10: !volume', value = 'Changes the bots volume.', inline = True)
        embed.add_field(name = '11: !errorlog', value = 'Prints off a list containing 20 of the most recent COMMAND errors including the time it occured on the bot, DEV ONLY!', inline = True)
        embed.add_field(name = '12: !botversion', value = 'Shows the current bots version, DEV ONLY!', inline = True)
        embed.add_field(name = '11: !emptyerrorfile', value = 'Emptys the error file containing function exceptions only, DEV ONLY!', inline = True)
        embed.add_field(name = '11: !errorfile', value = 'Prints off any exception errors in the error file, DEV ONLY!', inline = True)
        await client.send_message(ctx.message.author, embed = embed)
    except Exception as e:
        await write_errors("Exception occured in help: {0} at {1}".format(e, str(datetime.now())))
    return


async def displayembed(*args):
    global vplayer
    global playqueue
    try:
        if args[0] == "Search":
            ctx = args[1]
            title = args[2]
            a = args[3]
            embed = discord.Embed(
                colour = discord.Colour.blue()
                )
            embed.set_author(name = 'Search:', icon_url = 'https://cdn1.iconfinder.com/data/icons/hawcons/32/698627-icon-111-search-512.png')
            iter = 0
            while iter < 10:
                embed.add_field(name = 'Video {0}:'.format(iter+1), value = '{0}'.format(title[a+iter]), inline = False)
                iter = iter + 1
            embed.add_field(name = 'Help:', value = "Please enter a number between 1 and 10 with no '!'. To cancel type 'x' or wait 40 seconds, to see the next 10 results type '+', to see the last 10 results type '-'", inline = False)
            await client.send_message(client.get_channel(gvars.bot), embed = embed)
            return
        if args[0] == "Playing":
            songduration = divmod(vplayer.duration,60)
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
        if args[0] == "Enqueue":
            ctx = args[1]
            content = args[1]
            split = content.message.content.split(" ")
            url = split[1]
            title = await nextvideodata(url)
            embed = discord.Embed(
                title = title,
                colour = discord.Colour.blue()
                )
            embed.set_author(name = 'Enqueuing:',icon_url = 'http://www.clker.com/cliparts/j/W/O/s/N/o/windows-media-player-play-button-md.png')
            embed.set_thumbnail(url = "https://img.youtube.com/vi/{0}/default.jpg".format(await youtubeurlsnipper(url)))
            embed.add_field(name = 'Requested by:' , value = content.message.author , inline = True)
            embed.add_field(name = 'Up next:' , value = await nextvideodata(playqueue[1].songlink) if len(playqueue) > 1 else "Nothing.", inline = True)
            await client.send_message(client.get_channel(gvars.bot), embed = embed)
    except Exception as e:
        await write_errors("Exception occured in displayembed: {0} at {1}".format(e, str(datetime.now())))
    return

async def nextvideodata(x):
    global apikey
    try:
        url = x
        id = await youtubeurlsnipper(url)
        data = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/videos?id={0}&key={1}&part=snippet,contentDetails,statistics,status".format(id,apikey))
        title = json.load(data)["items"][0]["snippet"]["title"]
    except Exception as e:
        await write_errors("Exception occured in nextvideodata: {0} at {1}".format(e, str(datetime.now())))
    return title

async def youtubeurlsnipper(x):
    try:
        url = x
        if len(url) > 43:
            url = url[32:43]
        else:
            url = url[32:]
    except Exception as e:
        await write_errors("Exception occured in youtubeurlsnipper: {0} at {1}".format(e, str(datetime.now())))
    return url

@client.event
async def on_member_join(member):
    try:
        await client.send_message(member.server.get_channel(gvars.general), "{0} has joined the server!".format(member.name))
    except Exception as e:
        await write_errors("Exception occured in on_member_join: {0} at {1}".format(e, str(datetime.now())))
    return

@client.event
async def on_voice_state_update(before, after):
    try:
        bchan = before.voice.voice_channel
        achan = after.voice.voice_channel
        if achan == bchan:
            return
        await client.send_message(before.server.get_channel(gvars.voicelog), "{0} has switched from {1} to {2}".format(before.name, bchan, achan))
    except Exception as e:
        await write_errors("Exception occured in on_voice_state_update: {0} at {1}".format(e, str(datetime.now())))
    return


client.run(token)
