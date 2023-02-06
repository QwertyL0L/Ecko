import discord
import speech_recognition as sr
from discord.ext import commands
from gtts import gTTS
from discord import FFmpegPCMAudio
import asyncio
from youtube_search import YoutubeSearch
from discord.utils import get
import json, youtube_dl
import random
import re

import operator

def eval_binary_expr(op1, oper, op2):
    op1,op2 = int(op1), int(op2)
    return get_operator_fn(oper)(op1, op2)

def get_operator_fn(op):
    return {
        '+' : operator.add,
        '-' : operator.sub,
        'x' : operator.mul,
        'divided' :operator.__truediv__,
        'Mod' : operator.mod,
        'mod' : operator.mod,
        '^' : operator.xor,
        }[op]

bot = commands.Bot(command_prefix='?',intents=discord.Intents.all())

r = sr.Recognizer()
with sr.Microphone() as source:
    audio = r.listen(source)
text = r.recognize_google(audio, language = 'en-IN', show_all = True )
print(text)

YTDL_OPTIONS = {
    'format':
    'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
	'noplaylist': True,
	'nocheckcertificate': True,
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f"{bot.user.name} is Online!")

@bot.command()
async def transcribe(ctx):
    await ctx.send("Listening...")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        await ctx.send(f'{text}')
    except sr.UnknownValueError:
        pass

@bot.command()
async def copy(ctx):
    await ctx.send("Listening...")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text = r.recognize_google(audio)
        language = 'en'
        myobj = gTTS(text=f'{text}', lang=language, slow=False)
        myobj.save("tts.mp3")
        source = FFmpegPCMAudio('tts.mp3')
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        player = voice.play(source)
        while voice.is_playing(): #Checks if voice is playing
            await asyncio.sleep(1) #While it's playing it sleeps for 1 second
        else:
            await asyncio.sleep(1) #If it's not playing it waits 15 seconds
            while voice.is_playing(): #and checks once again if the bot is not playing
                break #if it's playing it breaks
            else:
                await voice.disconnect() #if not it disconnects

@bot.command()
async def hello(ctx):
    await ctx.send("Listening...")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        if text.lower() == 'hello':
            language = 'en'
            myobj = gTTS(text=f'Hello, {ctx.author.name}', lang=language, slow=False)
            myobj.save("tts.mp3")
            source = FFmpegPCMAudio('tts.mp3')
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            player = voice.play(source)
            while voice.is_playing(): #Checks if voice is playing
                await asyncio.sleep(1) #While it's playing it sleeps for 1 second
            else:
                await asyncio.sleep(1) #If it's not playing it waits 1 second
            while voice.is_playing(): #and checks once again if the bot is not playing
                break #if it's playing it breaks
            else:
                await voice.disconnect() #if not it disconnects
        else:
            await ctx.send("Sorry, I didn't understand what you said")
    except sr.UnknownValueError:
        await ctx.send("Sorry, I didn't understand what you said")

bot.lavalink_nodes = [
    {"host": "lava.link", 
		 "port": 80, 
		 "password": "anything"},
    # Can have multiple nodes here
]

@bot.command()
async def play(ctx):

	# is command author in voice channel
    if not ctx.message.author.voice:
        await ctx.send('You must join a voice channel to play music.')
        return
	
	# get user voice channel id
    channel = ctx.message.author.voice.channel

    r = sr.Recognizer()
    with sr.Microphone() as source, youtube_dl.YoutubeDL(YTDL_OPTIONS) as ydl:
        print('Hearing the voice')
        await ctx.send("Say the name of the song you want to hear!")
        r.adjust_for_ambient_noise(source, duration=0.2)
        try:
            audio = r.listen(source)
            text = r.recognize_google(audio, language='en')
            results = YoutubeSearch(text, max_results=1).to_json()

            # Save search results to json
            f = open("data.json", "w")
            f.write(results)
            f.close()

			# command is correct
            print('Got the voice command')
            await ctx.send("I have received your input!")

            # Decode result to json format
            results = json.loads(results)
            final_result = "https://youtu.be" + results['videos'][0][
                'url_suffix']

		    # connect to voice channel
            voice_client = await channel.connect()

			# download youtube file
            file = ydl.extract_info(final_result, download=False)

			# Final: Play music on voice channel
            voice_client.play(discord.FFmpegPCMAudio(str(file['url']), **FFMPEG_OPTIONS))
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)

            print('Music playing successfully')
            await ctx.send(f"Now Playing **{results['videos'][0]['title']}**")

            while voice_client.is_playing():
                await asyncio.sleep(1)
            else:
                bot.voice_clients.disconnect()
        except Exception as e:
            print(e)
            print("Voice command cancelled or bot error")
            await ctx.send("Sorry, I didn't understand what you said")

@bot.command()
async def stop(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send('Bot left')
    else:
        await ctx.send("I'm not in a voice channel, use the play command to make me join")

@bot.command()
async def pause(ctx):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text = r.recognize_google(audio)
        await ctx.send("Listening...")
        if text == 'pause':
            server = ctx.message.guild
            voice_channel = server.voice_client
            voice_channel.pause()

@bot.command()
async def resume(ctx):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text = r.recognize_google(audio)
        await ctx.send("Listening...")
        if text == 'resume':
            server = ctx.message.guild
            voice_channel = server.voice_client
            voice_channel.resume()

@bot.command()
async def repeat(ctx):
        if not ctx.voice_client.is_playing:
            return await ctx.send('Nothing is being played at the moment.')
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        text = r.recognize_google(audio)
        await ctx.send("Listening...")
        if text == 'repeat':
            ctx.voice_client.loop = not ctx.voice_client.loop
        await ctx.send('Loop Mode On')

@bot.command()
async def calc(ctx):
    await ctx.send("Say what you want to calculate, example: 1 plus 1")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text=r.recognize_google(audio)
    await ctx.send(eval_binary_expr(*(text.split())))

@bot.command()
async def iq(ctx):
    await ctx.send("Listening...")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text = r.recognize_google(audio)
        if text == "what's my IQ":
            language = 'en'
            myobj = gTTS(text=f'Your IQ Is {random.randrange(101)}', lang=language, slow=False)
            myobj.save("tts.mp3")
            source = FFmpegPCMAudio('tts.mp3')
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            player = voice.play(source)
            while voice.is_playing(): #Checks if voice is playing
                await asyncio.sleep(1) #While it's playing it sleeps for 1 second
            else:
                await asyncio.sleep(1) #If it's not playing it waits 15 seconds
            while voice.is_playing(): #and checks once again if the bot is not playing
                break #if it's playing it breaks
            else:
                await voice.disconnect() #if not it disconnects

@bot.command()
async def tts(ctx, *, text: str):
    language = 'en'
    myobj = gTTS(text=f'{text}', lang=language, slow=False)
    myobj.save("tts.mp3")
    source = FFmpegPCMAudio('tts.mp3')
    channel = ctx.message.author.voice.channel
    voice = await channel.connect()
    player = voice.play(source)
    await ctx.reply("playing audio...")
    while voice.is_playing(): #Checks if voice is playing
        await asyncio.sleep(1) #While it's playing it sleeps for 1 second
    else:
        await asyncio.sleep(1) #If it's not playing it waits 15 seconds
    while voice.is_playing(): #and checks once again if the bot is not playing
        break #if it's playing it breaks
    else:
        await voice.disconnect() #if not it disconnects

@bot.event
async def on_command_error(ctx, error):
     if isinstance(error, commands.CommandNotFound): 
         await ctx.reply("Invalid Command. Type **?help** to see all commands")

bot.run('MTA0NDA2NDgwMjUyNTQyOTg0MA.GZrMGZ.lQkI08Cper-1NKOXLhkCttFOu2babbwx2HEJxg')