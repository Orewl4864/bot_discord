"""
Pour lancer le bot en mode local : 
- lancer l'environnement dans le terminal (.\.venv\Scripts\Activate)
- lancer le bot (python salon.py)
"""

print("5min ecoulées")

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio  # module qui rajoute la notion du temps
import random
from keep_alive import keep_alive

intents = discord.Intents.all()
intents.guilds = True
intents.guild_messages = True
intents.messages = True

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=intents)

async def create_channels(interaction):
    # Crée un embed pour la réponse
    embed = discord.Embed(title="Création de salons", description="Salons créés avec succès!", color=0x00ff00)

    # Liste des catégories à créer
    categories = ["Catégorie 1", "Catégorie 2"]
    
    # Crée les catégories
    for category_name in categories:
        category = await interaction.guild.create_category(category_name)
        embed.add_field(name="Catégorie Créée", value=category_name, inline=False)

        # Liste des salons textuels et vocaux à créer sous cette catégorie
        text_channels = ["général", "annonces", "discussion"]
        voice_channels = ["Salon Vocal 1", "Salon Vocal 2"]

        # Crée les salons textuels sous la catégorie
        for channel_name in text_channels:
            await interaction.guild.create_text_channel(channel_name, category=category)
            embed.add_field(name="Salon Textuel Créé", value=f"{channel_name} dans {category_name}", inline=False)

        # Crée les salons vocaux sous la catégorie
        for channel_name in voice_channels:
            await interaction.guild.create_voice_channel(channel_name, category=category)
            embed.add_field(name="Salon Vocal Créé", value=f"{channel_name} dans {category_name}", inline=False)

    await interaction.response.send_message(embed=embed)  # Utilisez send_message sur l'objet Interaction

@bot.command()
async def create(ctx):
    embed = discord.Embed(title="Setup création de serveur discord", description="Pour créer un serveur discord avec ce BOT utilisez le bouton approprié à votre souhait.")
    embed.add_field(name="Création prédéfinie BASIQUE", value="Cette création comporte :\n- salons sans police d'écriture modifié\n- rôles avec permissions", inline=False)
    buttonBASIQUE = discord.ui.Button(label="Création prédéfinie BASIQUE", style=discord.ButtonStyle.primary)
    buttonPREMIUM = discord.ui.Button(label="Création prédéfinie PREMIUM", style=discord.ButtonStyle.primary)
    buttonPERSO = discord.ui.Button(label="Création personnalisée", style=discord.ButtonStyle.primary)

    async def buttonBASIQUE_callback(interaction):
        await create_channels(interaction)  # Appelle la fonction create_channels
        # Pas besoin d'appeler interaction.response.defer() ici, car nous répondons directement

    buttonBASIQUE.callback = buttonBASIQUE_callback

    view = discord.ui.View()
    view.add_item(buttonBASIQUE)
    view.add_item(buttonPREMIUM)
    view.add_item(buttonPERSO)

    await ctx.send(embed=embed, view=view)

@bot.command()
@commands.has_permissions(manage_channels=True)  # Vérifie que l'utilisateur a la permission de gérer les salons
async def dch(ctx):
    # Envoie un message de confirmation avant de supprimer les salons
    confirmation_message = await ctx.send("Tous les salons vont être supprimés. Veuillez patienter...")

    # Crée une liste des salons à supprimer
    channels_to_delete = ctx.guild.channels

    # Supprime chaque salon
    for channel in channels_to_delete:
        try:
            await channel.delete()
            print(f'Salon supprimé : {channel.name}')
        except Exception as e:
            print(f'Erreur lors de la suppression du salon {channel.name}: {e}')

    # Supprime le message de confirmation une fois tous les salons supprimés
    try:
        await ctx.send("Tous les salons ont été supprimés.")
    except discord.NotFound:
        print("Le canal où le message a été envoyé a été supprimé.\n---------------------------------------------------------")
    await ctx.guild.create_text_channel("général")

@bot.command()
@commands.has_permissions(manage_messages=True)  # Vérifie que l'utilisateur a la permission de gérer les messages
async def clear(ctx, amount: str):
    # Vérifie si le nombre de messages à supprimer est "all"
    if amount.lower() == "all":
        # Envoie un message de confirmation avant de supprimer tous les messages
        confirmation_message = await ctx.send("Suppression de tous les messages dans ce salon. Veuillez patienter...")
        # Supprime tous les messages
        deleted = await ctx.channel.purge(limit=None)  # Supprime tous les messages
        # Envoie un message pour confirmer la suppression
        await ctx.send(f"{len(deleted)} messages ont été supprimés.", delete_after=5)  # Le message sera supprimé après 5 secondes
    else:
        # Vérifie si le nombre de messages à supprimer est valide
        try:
            amount = int(amount)  # Convertit l'argument en entier
            if amount < 1:
                await ctx.send("Veuillez entrer un nombre positif de messages à supprimer.")
                return
            # Envoie un message de confirmation avant de supprimer les messages
            confirmation_message = await ctx.send(f"Suppression de {amount} messages. Veuillez patienter...")
            # Supprime les messages
            deleted = await ctx.channel.purge(limit=amount)
            # Envoie un message pour confirmer la suppression
            await ctx.send(f"{len(deleted)} messages ont été supprimés.", delete_after=5)  # Le message sera supprimé après 5 secondes
        except ValueError:
            await ctx.send("Veuillez entrer un nombre valide ou 'all' pour supprimer tous les messages.")

#######################################################################
#########################       TEST     ##############################
#######################################################################

@bot.command()
@commands.has_permissions(send_messages=True)  # Vérifie que l'utilisateur a la permission d'envoyer des messages
async def srmsg(ctx, amount: int):
    # Liste de mots aléatoires
    words = [
        "chat", "chien", "arbre", "maison", "voiture",
        "ordinateur", "plage", "montagne", "ciel", "fleur",
    ]

    # Vérifie si le nombre de messages à envoyer est valide
    if amount < 1:
        await ctx.send("Veuillez entrer un nombre positif de messages à envoyer.")
        return

    # Envoie le nombre spécifié de messages avec des mots aléatoires
    for _ in range(amount):
        random_word = random.choice(words)  # Choisit un mot aléatoire
        await ctx.send(random_word)  # Envoie le mot aléatoire

    # Envoie un message final pour indiquer que les messages ont été envoyés
    await ctx.send(f"{amount} messages avec des mots aléatoires ont été envoyés.")

#######################################################################
#############################   STATUS     ############################
#######################################################################

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')

@bot.command()
@commands.is_owner()  # Cette ligne permet de restreindre la commande à l'utilisateur qui a lancé le bot
async def shut(ctx):
    deleted = await ctx.channel.purge(limit=1)
    await ctx.send("Le bot va s'éteindre...", delete_after=1.35)
    await asyncio.sleep(1.4)
    await ctx.send("Le bot a été éteint.", delete_after=2.85)
    await asyncio.sleep(3)
    await bot.close()  # Éteindre le bot



keep_alive()
if __name__ == "__main__":
    bot.run(token=token)
