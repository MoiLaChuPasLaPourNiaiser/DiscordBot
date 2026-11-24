import discord
from discord import app_commands
import FonctionBot
from datetime import date, timedelta
import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

###########################
#       todo 
#   Cacher les token
############################

ROLE_CRIMINELLE = 1502087351692951672
ROLE_VIP = 1502087758993162362
ROLE_PLEBE = 1328240294432604170
ROLE_LHOMME = 1328239520285593611
ROLE_FORCES = 1328241100225511456
ROLE_GAUGAUBOT = 1499597878258307207
ROLE_DRAFTBOT = 1328243007115497534
MY_GUILD = discord.Object(id=1328237921362509844)
PRICE_CRIMINELLE = 100
PRICE_VIP = 1500
POINTS_QUOTIDIENS = 10

is_live        = False
twitch_token   = None
intents = discord.Intents.default()
discord_token = os.getenv("DISCORD_TOKEN")
twitch_id = os.getenv("TWITCH_ID")
twitch_secret = os.getenv("TWITCH_SECRET")


async def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id":     twitch_id,
        "client_secret": twitch_secret,
        "grant_type":    "client_credentials",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            data = await resp.json()
            return data["access_token"]
        
async def check_twitch_live():
    global twitch_token

    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID":     twitch_id,
        "Authorization": f"Bearer {twitch_token}",
    }
    params = {"user_login": "gaugaulive"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status == 401:
                twitch_token = await get_twitch_token()
                return await check_twitch_live()
            data = await resp.json()
            streams = data.get("data", [])
            return streams[0] if streams else None
        
async def twitch_monitor():
    global is_live, twitch_token

    await bot.wait_until_ready()
    twitch_token = await get_twitch_token()
    channel = bot.get_channel(1496951300988997642)

    print(f"✅ Surveillance de gaugaulive démarrée.")

    while not bot.is_closed():
        stream = await check_twitch_live()

        if stream and not is_live:
            is_live = True
            game    = stream.get("game_name", "Jeu inconnu")
            title   = stream.get("title", "Sans titre")
            url     = "https://twitch.tv/gaugaulive"

            embed = discord.Embed(
                title       = "🔴 le big big goat est en live ! 🔴",
                description = f"**{title}**\n🎮 {game}",
                url         = url,
                color       = discord.Color.red(),
            )
            embed.set_thumbnail(url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_gaugaulive-320x180.jpg")
            embed.add_field(name="👀 Regarder", value=f"[Clique ici]({url})", inline=False)

            await channel.send("@everyone", embed=embed)
            print(f"🔴 Live détecté : {title}")

        elif not stream and is_live:
            # ⚫ Fin du live
            is_live = False
            await channel.send(f"⚫ l'absolut goat vient de terminer son live. Vous êtes tristes et c'est normal, mais n'ayez crainte, il reviendra.. ⚫")
            print("⚫ Live terminé.")

        await asyncio.sleep(60)

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        self.loop.create_task(twitch_monitor())

        if not os.path.exists("synced.txt"):
            await self.tree.sync(guild=MY_GUILD)
            open("synced.txt", "w").close()
            print("Commandes synchronisées !")
        else:
            print("Sync ignoré.")

bot = MyBot()

# La commande salut
# @bot.tree.command(name="salut", description="Dit bonjour")
# async def salut(interaction: discord.Interaction):
#     await interaction.response.send_message("Wasup blud")

#Commande pour ajouter un certain nombre de point
# @bot.tree.command(name="add_point", description="Add 1 point")
# async def addpoint(interaction: discord.Interaction):
#     FonctionBot.addPoints(interaction.user.name, 1)
#     await interaction.response.send_message("1 point ajouté !")

# Commande pour voir son nombre de points
@bot.tree.command(name="see_points", description="See your points")
async def seepoints(interaction: discord.Interaction):
    info = FonctionBot.getNameAndPoints(interaction.user.name)
    if(info["name"] == "None") :
        await interaction.response.send_message(info["name"] + " a 0 point.")
    else : 
        await interaction.response.send_message("Tu as " + str(info["points"]) + " points !")

# Commande pour voir le store
@bot.tree.command(name="store", description="See the store")
async def store(interaction: discord.Interaction):
    await interaction.response.send_message("MAGASIN\n------------------------------\nTIMEOUT QUELQU'UN (CRIMINELLE) : " + str(PRICE_CRIMINELLE) + " POINTS\n\nPRENDRE/RETIRER UN VIP : " + str(PRICE_VIP) + " POINTS\n------------------------------")

# Commande pour acheter un item du store
@bot.tree.command(name="buy", description="Buy someting from the store")
async def buy(interaction: discord.Interaction, item: str, pseudo: str = None):
    members = interaction.guild.members
    names = [member.name for member in members]
    if(item == "criminelle"):
        if(FonctionBot.verifyPrice(PRICE_CRIMINELLE, interaction.user.name)):
            if(FonctionBot.verifyPseudo(pseudo, names)):
                for i in members:
                    if (i.name == pseudo):
                        if((interaction.guild.get_role(ROLE_VIP) in i.roles) or (interaction.guild.get_role(ROLE_FORCES) in i.roles)
                        or (interaction.guild.get_role(ROLE_LHOMME) in i.roles) or (interaction.guild.get_role(ROLE_GAUGAUBOT) in i.roles)
                        or (interaction.guild.get_role(ROLE_DRAFTBOT) in i.roles)):
                            await interaction.response.send_message("Vous ne pouvez pas désigner un VIP, les forces spéciales, GauGau lui-même et les bots en tant que criminelle !")
                        elif (interaction.guild.get_role(ROLE_CRIMINELLE) in i.roles):
                            await interaction.response.send_message(i.name + " est déjà un criminelle.")
                        else:
                            FonctionBot.pay(interaction.user.name, PRICE_CRIMINELLE)
                            FonctionBot.addCriminelle(pseudo)
                            await i.remove_roles(interaction.guild.get_role(ROLE_PLEBE))
                            await i.add_roles(interaction.guild.get_role(ROLE_CRIMINELLE))
                        break
                await interaction.response.send_message(interaction.user.name + " vient de désigner " + pseudo + " comme criminelle !")
            else:
                await interaction.response.send_message("Le pseudo est invalide.")
        else:
            await interaction.response.send_message("Yark té ben trop pauvre... Il te faut " + str(PRICE_CRIMINELLE) + " points.")
    elif(item == "vip"):
        if(FonctionBot.verifyPrice(PRICE_VIP, interaction.user.name)):
            member = interaction.guild.get_member(interaction.user.id)
            if(interaction.guild.get_role(ROLE_VIP) in member.roles):
                if(pseudo != None):
                    if(FonctionBot.verifyPseudo(pseudo, names)):
                        for i in members:
                            if (i.name == pseudo):
                                if(interaction.guild.get_role(ROLE_VIP) in i.roles):
                                    FonctionBot.pay(i.name, PRICE_VIP)
                                    await i.remove_roles(interaction.guild.get_role(ROLE_VIP))
                                    await interaction.response.send_message(pseudo + " a perdu son VIP !")
                                else:
                                    await interaction.response.send_message("L'utilisateur spécifié n'a pas de VIP.")
                    else:
                        await interaction.response.send_message("Le pseudo spécifié est invalide.")
                else:
                    await interaction.response.send_message("Tu fais déjà partie de la noblesse !")
                    await interaction.response.send_message("Si tu veux retirer le VIP d'un autre utilisateur, spécifies le pseudo de l'utilisateur en question dans la commande '/buy vip [pseudo]'.")
            else:
                FonctionBot.pay(interaction.user.name, PRICE_VIP)
                await member.add_roles(interaction.guild.get_role(ROLE_VIP))
                await interaction.response.send_message(interaction.user.name + " vient de recevoir un VIP !")
        else:
            await interaction.response.send_message("Yark té ben trop pauvre... Il te faut " + str(PRICE_VIP) + " points.")
    else:
        await interaction.response.send_message("L'item est invalide, voici quoi écrire pour les choix :\nCRIMINELLE : criminelle pseudo\nVIP : vip")

# Commande pour se libérer de la criminalité
@bot.tree.command(name="free", description="Free yourself from criminality")
async def free(interaction: discord.Interaction):
    result = FonctionBot.removeCriminelle(interaction.user.name)
    if(result == timedelta(minutes=0)):
        await interaction.user.remove_roles(interaction.guild.get_role(ROLE_CRIMINELLE))
        await interaction.user.add_roles(interaction.guild.get_role(ROLE_PLEBE))
        await interaction.response.send_message(interaction.user.name + " EST ENFIN (ou pas) LIIIIIBREEEE !")
    elif(result == timedelta(minutes=-1)):
        await interaction.response.send_message("Tu es déjà une libre personne...")
    else:
        await interaction.response.send_message("Tu auras la permission de te libérer seulement dans " + str(result) + " minutes.")

@bot.tree.command(name="help", description="Voir les commandes et leur fonctionnement")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("COMMANDES :\nsee_points : voir le nombre de points que tu possède\nstore : voir les items dans le store\nbuy [item] [pseudo:optionnel] : acheter un item dans le shop ; certains items requièrent le pseudo d'un autre utilisateur\nfree : permet de se libérer du rôle de criminelle après 30 minutes de son obtention")

# Event qui s'active à chaque message envoyé
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    else :
        # Récompense quotidienne
        user = FonctionBot.getNameAndPoints(message.author.name)
        if(user["name"] != "None") :
            if(user["lastMessageDate"] < date.today()):
                FonctionBot.addPoints(message.author.name, POINTS_QUOTIDIENS)
        else :
            FonctionBot.addPoints(message.author.name, POINTS_QUOTIDIENS)

bot.run(discord_token)