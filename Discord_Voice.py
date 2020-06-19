import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import shutil
from os import system


TOKEN = 'NzE0NjY0MTkzNDIwMjk2MTky.Xsx9jw.Pk_IAA0fpPV6P5Q7NxmGB4NjShA'
BOT_PREFIX = '/'

bot = commands.Bot(command_prefix=BOT_PREFIX)

@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")

@bot.command(pass_context=True, aliases=['j', 'joi', 'jo'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)
    await channel.connect()

    await ctx.send(f"Joined {channel}")

@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left the {channel}\n")
        await ctx.send(f"left {channel}")

    else:
        print("Bot was told to leave the voice channel, but was not in one")
        await ctx.send("Dont think I am in a voice channel!")

@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, *url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1

            try:
                first_file = os.listdir(DIR)[0]

            except:
                print("No more queued song(s)\n")
                queues.clear()
                return

            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")

                if song_there:
                    os.remove("song.mp3")

                shutil.move(song_path, main_location)

                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else :
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")


    song_exist = os.path.isfile("song.mp3")

    try: #try to remove, if it throws an error, it is being played currently
        if song_exist:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file") #debug and check purposes
    except PermissionError:
        print("Trying to delete song file, but it is being played.")
        await ctx.send("ERROR: Music is playing")
        return

    Queue_infile = os.path.isdir("./Queue") #check if there is an old queue folder
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")



    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    #youtube download options
    ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': "./song.mp3",
            'postprocessors':
            [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now") #checking and debugging
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' + c_path + '"' + " -s " + url)

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music Paused")
        voice.pause()
        await ctx.send("Music paused")

    else:
        print("Music not playing. Failed Pause.")
        await ctx.send("Music not playing. Failed Pause.")

@bot.command(pass_context=True, aliases=['r', 'res', 're'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed Music")
        voice.resume()
        await ctx.send("Resumed Music")

    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")

@bot.command(pass_context=True, aliases=['s', 'sto', 'st'])
async def stop(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()
    #check queue folder, and look if the folder is empty or not
    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True: #remove if it is not empty
        shutil.rmtree("./Queue")


    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")

    else:
        print("No music playing. Failed to stop")
        await ctx.send("No music playing. Failed to stop.")

queues = {}

@bot.command(pass_context=True, aliases=['q', 'qu', 'que'])
async def queue(ctx, *url: str):
    Queue_infile = os.path.isdir("./Queue")

    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR)) #number of the queue
    q_num += 1
    add_queue = True

    while add_queue:
        if q_num in queues:
            q_num += 1

        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")
    #copied at play function
    ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': queue_path,
            'postprocessors':
            [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    song_search = " ".join(url)
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + song_search)


    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")

@bot.command(pass_context=True, aliases=['n', 'ne', 'nex'])
async def next(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if queue_infile is True: #remove if it is not empty
        shutil.rmtree("./Queue")


    if voice and voice.is_playing():
        print("Playing next Song")
        voice.stop()
        await ctx.send("Next Song")

    else:
        print("No music playing. Failed to play next song")
        await ctx.send("No music playing. Failed to play.")

@bot.command(pass_context=True, aliases=['v', 'vo', 'vol'])
async def volume(ctx, volume: int):

    if ctx.voice_client is None:
        return await ctx.send("Not connected to voice channel")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")


bot.run(TOKEN)