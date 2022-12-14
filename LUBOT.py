import base64
import nextcord
from nextcord.utils import get # esse get é muito bom!!!
from nextcord import Interaction, SlashOption , ChannelType
from nextcord.ext import commands
from nextcord.abc import GuildChannel
import time
from PIL import Image # pip install pillow
#todo pillow não ta sendo usado mas eu quero colocar um comando que manda foto de gatinho que eu me lembre precisa disso mas não precisa instalar agora
from craiyon import Craiyon # pip install -U craiyon.py    (reclama q usa .py mas funciona)
#makes images from a prompt, but is kinda dumb and slow AI image generation 
from io import BytesIO # faz parte da função de criar imagem, n tenho a certeza do que faz pq copiei de alguem no youtube
#import wavelink  <------ não rolou #todo usar yt-dl
import sys
import random
import priv as p # priv is a file with the token and other stuff such as serverID, channelID, userID, etc


bot = commands.Bot(command_prefix = '!',intents=nextcord.Intents.all())
client = nextcord.Client()

#################################
@bot.event
async def on_ready():
    
    print("="*50)
    print(bot.user ,' ta rodando')
    print('serverID: ', p.serverID)
    print('Bot id: ', bot.user.id)
    print("="*50)
    activity = nextcord.Game(name="Tá on👍")
    await bot.change_presence(status=nextcord.Status.online, activity=activity)
#################################
@bot.slash_command( name="play" ,description="Play a song", guild_ids=[p.serverID])

async def play(
    #TODO **fazer tocar musica**, tentar com o yt-dl  
    interaction: Interaction,
    channel: GuildChannel = SlashOption(channel_types=[ChannelType.voice],
    description="Voice Channel to Join"),
    search: str = SlashOption(description="Song Name")
    ):
    await channel.connect()
    embed = nextcord.Embed(
        title="Tocando 🎵 "+search+" 🎶 no canal 🔈"+channel.name,
        description=str(interaction.user.name)+" pediu para tocar \n https://www.youtube.com/watch?v=XzcJ4p0R6NY",
        #TODO trocar por link do search do youtube
        color=random.randint(0, 0xFFFFFF)
    )
    await interaction.send(embed=embed)


#################################
@bot.slash_command(name="move" ,description="move o usuario para o canal escolhido", guild_ids=[p.serverID])
async def move(member: nextcord.Member,vc : nextcord.VoiceChannel):
    await member.move_to(vc)

      
#TODO permissoes para mover o usuario apenas para administradores
#* mas tem q estudar mais a documentação do nextcord pra fazer isso
################## joão bugado #####################
#* meu amigo joão usa discord no celular que frequentemente para de funcionar.
#* quando ele sai e volta do canal de voz magicamente volta a funcionar normalmente
@bot.slash_command(name="mover2", description="usuario predestinado vai e volta", guild_ids=[p.serverID])
async def mover(ctx, canal_atual:nextcord.VoiceChannel):
    member: nextcord.Member = get(ctx.guild.members, id=p.mover2userid)#trocar por id do usuario
    pingPongChannel = get(ctx.guild.channels, name="geral2")#trocar por nome de um canal
    await member.move_to(pingPongChannel)
    await member.move_to(canal_atual)
################## joão bugado #####################
######################################################
@bot.slash_command(name="dalle" ,description="generate a image ia and shit", guild_ids=[p.serverID])
async def dalle(ctx: commands.Context,*,prompt: str):
    ETA = int(time.time()+60)
    msg = await ctx.send(f"Generating... it will takes a while  ETA: <t:{ETA}:R>")
    generator = Craiyon()
    result = generator.generate(prompt)
    images = result.images
    for i in images:
        image = BytesIO(base64.decodebytes(i.encode("utf-8")))
        return await msg.edit(f"generated by DALLE-mini \n {prompt}",file=nextcord.File(image,"image.png"))
######################################################
#################### EMBED TEST ####################
@bot.slash_command(name='oi2', description="da um oi com embed", guild_ids=[p.serverID])
async def oi2(interaction: Interaction):

    embed = nextcord.Embed(
        title="Oi por embed",
        description=" OI "+str(interaction.user.name),
        color=nextcord.Color.green()
    )
    await interaction.send(embed=embed)
#################### EMBED TEST ####################
 ##################################
@bot.slash_command(name='oi', description="da um oi", guild_ids=[p.serverID])
async def oi(interaction : Interaction):
    await interaction.response.send_message(f"OI {interaction.user.name}!!")
##################################
@bot.slash_command(name='ping', description="joga ping pong", guild_ids=[p.serverID])
async def pingPong(interaction : Interaction):
    await interaction.response.send_message("pong")
##################################
#* usado principalmente para fins de desenvolvimento mas pode ser util
#todo permissão criador ou dev para usar comando
@bot.slash_command(name="kill",description="stops python script", guild_ids=[p.serverID])
async def kill(interaction:Interaction):
    await interaction.response.send_message("killing...")
    await sys.exit()

###leave## perfeito
@bot.slash_command(name="leave",description="kicks the bot", guild_ids=[p.serverID])
async def leave(ctx):
    voice = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)
    await ctx.send('saindo de '+str(voice.channel))
    await voice.disconnect()







#runs the bot
bot.run(p.TOKEN)
print("[-]="*45)