import time
import timeit
import discord.ext.commands as commands
from discord import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from pytube import YouTube
import os
import s
from discord import FFmpegPCMAudio
import asyncio

bot = commands.Bot(command_prefix='!', intents=Intents.all())
queue = []

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print( '*'*22,bot.user.name,'*'*22)
    print(f'              {len(synced)} commandos carregados')    
    print('*'*51)
    await bot.change_presence(activity=CustomActivity(name="to online 🤖"))

async def changeListeningSong(SongTitle):
    await bot.change_presence(activity=CustomActivity(name="tocando: "+SongTitle))

@bot.tree.command(name="pause",description="pausa a musica")
async def pause(interaction : Interaction):
    voice = utils.get(bot.voice_clients, guild=interaction.guild)
    voice.pause()
    await interaction.response.send_message('⏸️')
    

@bot.tree.command(name="resume",description="retoma a musica")
async def resume(interaction : Interaction):
    voice = utils.get(bot.voice_clients, guild=interaction.guild)
    voice.resume()
    await interaction.response.send_message('▶️')
    

@bot.tree.command(name="stop",description="para a musica")
async def stop(interaction : Interaction):
    voice = utils.get(bot.voice_clients, guild=interaction.guild)
    voice.stop()
    await interaction.response.send_message('⏹️')

@bot.tree.command(name="play",description="toca uma musica")
async def playMusic(interaction : Interaction, pesquisa : str):
    await interaction.response.send_message(f"🔎 procurando: *__{pesquisa}__*")
    procuraBaixaEColocaNaQueue(pesquisa)
    await playnext(interaction)


async def playnext(interaction: Interaction):
    titulo,autor,link,views,duracao,autorImg,thumbnail,filename = queue[0].values()
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    voice = utils.get(bot.voice_clients, guild=interaction.guild)
    songPath = "music/"+filename
    source = FFmpegPCMAudio(songPath)
    try:
        voice.play(source)
    except:
        await interaction.followup.send("já tem uma musica tocando, colocando na queue")
        return
    embed = Embed(
        url=link,
        title=titulo,
        description="autor: " + autor,
        color=0x9933ff,
        timestamp=interaction.created_at
    )
    left = int(time.time()) + int(duracao.split(":")[0])*60 + int(duracao.split(":")[1])
    embed.set_thumbnail(url=autorImg)
    embed.set_image(url=thumbnail)
    embed.add_field(name="Duração: ", value=duracao, inline=True)        
    embed.add_field(name="tempo de musica : ", value=f"<t:{left}:R>", inline=True)
    embed.add_field(name="Views: ", value=views, inline=True)
    embed.set_footer(text="Feito por: musta_01 com ❤️")
    await interaction.followup.send(embed=embed)
    await changeListeningSong(titulo)
    #wait for song to end
    while voice.is_playing():
        await asyncio.sleep(1)
        print("esperando a musica acabar", end="\r")
        print("faltam",left-int(time.time()),"segundos para a musica acabar", end="\r")
    print("", end="\r")
    try:
        queue.pop(0)
        await playnext(interaction)
    except:
        await interaction.response.send_message("acabaram as musicas da queue")

@bot.tree.command(name="die",description="desliga o bot")
async def die(interaction : Interaction):
    if interaction.user.id == s.myid:
        await interaction.response.send_message('desligando o bot, boa noite')
        quit()

@bot.tree.command(name="skip",description="pula para a próxima música na queue")
async def skip(interaction : Interaction):
    voice = utils.get(bot.voice_clients, guild=interaction.guild)
    if voice and voice.is_playing():
        voice.stop()
        await interaction.response.send_message("Música pulada!")
    else:
        await interaction.response.send_message("Não há música tocando no momento.")


@bot.tree.command(name="queue",description="mostra a queue")
async def queueCommand(interaction : Interaction):
    if queue == []:
        await interaction.response.send_message("Não há músicas na queue.")
        return
    embed = Embed(
        title="Queue",
        color=0x9933ff
    )
    for i in range(len(queue)):
        titulo,autor,link,views,duracao,autorImg,thumbnail,filename = queue[i].values()
        embed.add_field(name=f"{i+1} - {titulo}", value=f"autor: {autor}\nduração: {duracao}", inline=True)
    embed.set_footer(text="Feito por: musta_01 com ❤️")
    await interaction.response.send_message(embed=embed)



# ?#############################################{{{{{{{{funcoes}}}}}}}}}}}#####################################################
opcoes = webdriver.ChromeOptions()
opcoes.add_argument("--headless")
opcoes.add_argument("--log-level=3")
opcoes.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

navegador = webdriver.Chrome(options=opcoes)
def procuraBaixaEColocaNaQueue(pesquisa):    
    if not os.path.exists("music"):
        os.makedirs("music")
    pesquisaPronta = pesquisa.replace(" ", "+")
    navegador.get("https://www.youtube.com/results?search_query=" + pesquisaPronta)
    video_element = navegador.find_element('css selector', 'ytd-video-renderer')
    url = video_element.find_element('css selector', 'ytd-thumbnail a').get_attribute('href')
    yt = YouTube(url)
    filename = yt.watch_url.replace("https://youtube.com/watch?v=", "")+".mp3"
    if not os.path.exists("music/"+filename):
        print("baixando a musica agora")
        inicio = timeit.default_timer()
        yt.streams.get_audio_only().download(output_path="music", filename=filename)
        fim = timeit.default_timer()
        print(f"baixei a musica {yt.title} em {fim - inicio} segundos")
        
    else:
        print("ja tinha baixado a musica "+yt.title)
    link = video_element.find_element('css selector', 'ytd-thumbnail a').get_attribute('href')
    autorImg =video_element.find_element('css selector', 'yt-img-shadow img').get_attribute('src')
    titulo = yt.title
    duracao = "{:02d}:{:02d}".format(yt.length // 60, yt.length % 60)
    views = "{:,}".format(yt.views)
    autor = video_element.find_element(By.XPATH ,'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[2]/ytd-channel-name/div/div/yt-formatted-string/a').text
    thumbnail = video_element.find_element(By.XPATH,"/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/ytd-thumbnail/a/yt-image/img").get_attribute('src')
    musica = {
        "titulo":titulo,
        "autor":autor,
        "link":link,
        "views":views,
        "duracao":duracao,
        "autorImg":autorImg,
        "thumbnail":thumbnail,
        "filename":filename
    }
    queue.append(musica)


bot.run(s.token,log_handler=None)