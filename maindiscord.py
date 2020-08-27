from discord import *
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import time
import random
import json
import threading
import csv
import asyncio

bot = commands.Bot(command_prefix="$",description="Bot discord pour GTALife")
bot.remove_command('help')

token = ""

insultes = []

locas = []

#Ajout de location par la commande, stockage dans le tableau local et dans le fichier csv
def addLoca(email: User,identite,adresse,rue,quoi,datefin: datetime):
    a = {'Email':email,'Identité':identite,'Adresse':adresse,'Rue':rue,'Type':quoi,'Date de fin':datefin}
    locas.append(a)
    storecsv(a)

#Ajout de location par la récupération des données du fichier csv, stockage dans le tableau local seul
def addReader(email: User,identite,adresse,rue,quoi,datefin: datetime):
    a = {'Email':email,'Identité':identite,'Adresse':adresse,'Rue':rue,'Type':quoi,'Date de fin':datefin}
    locas.append(a)

#Suppression de location DANS LE TABLEAU LOCAL SEULEMENT
def delLoca(location: dict):
    for i in range(len(locas)):
        if locas[i]==location:
            del locas[i]
            break

#Renvoie une insulte aléatoire
def rdmins():
    return insultes[random.randrange(len(insultes))]

#Envoi de log de commande avec pseudo, tag, heure et nom de la commande
def gethoro(cxt,cmd):
    horodata = datetime.now()
    strhoro = horodata.strftime("%d-%b-%Y (%H:%M:%S)")
    print(cxt.message.author.name + "#"+cxt.message.author.discriminator+" a utilisé "+cmd+" - "+strhoro)

#Renvoie un entier correspondant à la différence entre 2 dates (en nombre d'heures)
def heurediff(date1: datetime,date2: datetime):
    delta = date2 - date1
    difference = abs(delta).total_seconds() // 3600
    return difference

#Stocke les données du tableau local dans le fichier csv, utilisé lors d'un ajout de location par commande SEULEMENT (sinon doublons)
def storecsv(data: dict):
    columns = ['Email','Identité','Adresse','Rue','Type','Date de fin']
    fichier = "locations.csv"
    try:
        with open(fichier,mode='a') as csvfile:
            appender = csv.writer(csvfile,delimiter='\t')
            appender.writerow([data['Email'],data['Identité'],data['Adresse'],data['Rue'],data['Type'],data['Date de fin']])
            print("Location enregistrée dans locations.csv")
    except IOError:
        print("Erreur entrée/sortie")

#Récupère les données du fichier csv et les stocke dans le tableau local avec l'ajout sans stockage fichier, utiliser une seule fois par start
def getcsv():
    fichier = open('locations.csv','r')
    with fichier:
        reader = csv.DictReader(fichier,delimiter='\t',fieldnames=['Email','Identité','Adresse','Rue','Type','Date de fin'])
        for ligne in reader:
            #print(ligne)
            location = dict(ligne)
            #print("Location enregistrée : "+str(location))
            addReader(int(location['Email']),location['Identité'],location['Adresse'],int(location['Rue']),location['Type'],datetime.strptime(location['Date de fin'],'%Y-%m-%d %H:%M:%S'))

# toString de dict sans la date de fin en 0, date de fin en 1
def joli(data: dict):
    return (data['Identité']+" | "+data['Type']+" au "+str(data['Rue'])+" - "+data['Adresse']),(datetime.strftime(data['Date de fin'],"%d/%m/%Y %H:%M:%S"))

#Renvoie un embed personnalisé avec joli() pour le message de rappel 
def embedcreator(data: dict,temps):
    message=Embed(title="🏡 Oublipataloca 🏡", description=" ", color=0x6d0ce4)
    message.add_field(name="⌛️ Rappel de fin de location ⏳ ", value=("Temps restant : "+str(temps)+"h"), inline=False)
    message.add_field(name="📁 La location en question : 📂", value=joli(data)[0], inline=False)
    message.add_field(name="Date complète de fin de la location : 📍", value=joli(data)[1], inline=False)
    message.add_field(name="Contactez un agent immobilier pour ne pas perdre votre location. 📞", value="➡️ Alan Hazel - 555-90325 ⬅️", inline=False)
    message.add_field(name="Besoin d'autre chose ? 💡", value="Tapez $help ", inline=True)
    message.add_field(name="Un problème avec le logiciel ? Une suggestion ? 🔧", value="Contactez Alan Hazel par mail. 📩", inline=True)
    message.set_footer(text="Bot Discord développé (avec ❤️) en Python par Carbonaraah#6808 pour GTALife")  

    return message

@bot.command()
async def help(cxt):
    gethoro(cxt,"help")
    message=Embed(title="🏡 Oublipataloca 🏡", description="Aide d'utilisation des commandes", color=0x6d0ce4)
    message.add_field(name="⌛️ $meslocas ⏳ ", value="Affiche les locations enregistrées à votre email", inline=False)
    message.add_field(name="📁 $help 📂", value="Affiche ce message", inline=False)
    message.add_field(name="Un problème avec le logiciel ? Une suggestion ? 🔧", value="Contactez Alan Hazel par mail. 📩", inline=False)
    message.set_footer(text="Bot Discord développé (avec ❤️) en Python par Carbonaraah#6808 pour GTALife")
    await cxt.send(embed=message)

#Efface le tableau local SEULEMENT
@bot.command()
async def clear_locas(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"clear_locas")
        locas.clear()
        await cxt.send("Tableau de locations clear")
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#def messagerappel(cxt,cible,location: dict):
#    dmcustom(cxt,cible,)

#Récupère les données du fichier csv avec getcsv()
@bot.command()
async def get_bdd(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"get_bdd")
        getcsv()
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Stocke tout le tableau local dans csv (debug only)
#@bot.command()
#async def stocker(cxt):
#    for location in locas:
#        storecsv(location)

#Envoie un message dans la console quand le bot est prêt à fonctionner
@bot.event
async def on_ready():
    print("Bot lancé correctement")

#Stoppe le bot, pas de restart, prend environ 10 secondes
@bot.command()
async def stop_bot(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"stop_bot")
        await cxt.send("Bot en cours d'arrêt")
        exit()
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Commande de test
@bot.command()
async def test(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"test")
        await cxt.invoke(bot.get_command("dmperso"),cible=323542898505416704)
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Envoie un message privé à l'auteur
#@bot.command()
#async def dm(cxt):
#   gethoro(cxt,"dm")
#   await cxt.author.send("cc mec sa va?")

#Ajoute une location au tableau local et au fichier csv avec addLoca
@bot.command()
async def ajouter(cxt):
    gethoro(cxt,"ajouter")
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        await cxt.send("*Admin vérifié, commande autorisée*")
        
        def check(message):
            return message.author == cxt.message.author and cxt.message.channel == message.channel

        await cxt.send("Entrez l'email")
        msg = await bot.wait_for("message",timeout=20,check=check)
        email = int(msg.content)

        await cxt.send("Entrez l'identité")
        msg = await bot.wait_for("message",timeout=20,check=check)
        identite = msg.content

        await cxt.send("Entrez l'adresse")
        msg = await bot.wait_for("message",timeout=20,check=check)
        adresse = msg.content

        await cxt.send("Entrez le numéro de rue")
        msg = await bot.wait_for("message",timeout=20,check=check)
        rue = int(msg.content)

        await cxt.send("Entrez le type")
        msg = await bot.wait_for("message",timeout=20,check=check)
        quoi = msg.content

        await cxt.send("Entrez la date de fin (format: 13/01/20 13:59:47)")
        msg = await bot.wait_for("message",timeout=20,check=check)
        datefin = datetime.strptime(msg.content,'%d/%m/%y %H:%M:%S')
        ##datefin = datetime.strptime(await bot.wait_for("message",timeout=20,check=check),'%d/%m/%y %H:%M:%S')

        addLoca(email,identite,adresse,rue,quoi,datefin)
        await cxt.send("Location ajoutée avec succès")

    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Supprime une location du tableau local avec delLoca
@bot.command()
async def supprimer(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        await cxt.send("*Admin vérifié, commande autorisée*")
        gethoro(cxt,"supprimer")
        def check(message):
            return message.author == cxt.message.author and cxt.message.channel == message.channel

        await cxt.send("Entrez l'email")
        msg = await bot.wait_for("message",timeout=20,check=check)
        email = int(msg.content)

        locasdemail = []

        for j in range(len(locas)):
            if(locas[j]['Email']==email):
                locasdemail.append(locas[j])
        
        await cxt.send("Voici les locations pour l'email entré :")
        res = ""
        for k in range(len(locasdemail)):
            res = res + str(k) + ". " + str(locasdemail[k]) + "\n"
        await cxt.send(res)

        await cxt.send("Entrez le numéro de la location à supprimer")
        msg = await bot.wait_for("message",timeout=20,check=check)
        num = int(msg.content)

        delLoca(locasdemail[num])
        await cxt.send("Location supprimée avec succès")

    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Envoie une insulte aléatoire à la cible @taggée avec rdmins()
@bot.command()
async def attaque(cxt,cible: Member):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"attaque")
        await cxt.send(rdmins()+" "+cible.mention)
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Envoie un message privé prédéfini à l'id entré
@bot.command()
async def dmperso(cxt,cible):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"dmperso")
        user = bot.get_user(int(cible))
        if user is not None:
            await user.send("```Oublipataloca: PLUS JAMAIS T'OUBLIE TU M'ENTENDS```")
        else:
            await cxt.send("Utilisateur introuvable ou mp bloqués")
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Envoie un message privé à l'id entré avec le message entré (non utilisable par un utilisateur, utilisé dans allrappel())
@bot.command()
async def dmcustom(cxt,cible,message):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"dmcustom")
        user = bot.get_user(int(cible))
        if user is not None:
            await user.send(embed=message)
        else:
            await cxt.send("Utilisateur introuvable ou mp bloqués")
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Vérifie toutes les locations dans le tableau local et envoie un message de rappel (joli(),embedcreator(),dmcustom()) si il reste moins de 48h
@bot.command()
async def allrappel(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"allrappel")
        mtn = datetime.now()
        for i in range(len(locas)):
            temps = heurediff(mtn,locas[i]['Date de fin'])
            if temps<=48 and temps>0:
                print("Rappel envoyé pour "+str(locas[i]))
                msg_rappel = embedcreator(locas[i],temps)
                await cxt.invoke(bot.get_command('dmcustom'),cible=int(locas[i]['Email']),message=msg_rappel)
            else:
                pass
        await cxt.send("Rappels effectués !")
        await asyncio.sleep(57600)
        await cxt.invoke(bot.get_command('allrappel'))
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Commence l'appel automatique à allrappel() (n'utiliser qu'une seule fois par start)
#@bot.command()
#async def start_rappel(cxt):
#    gethoro(cxt,"start_rappel")
#    launch_rappel(cxt)

#@bot.command()
#async def launch_rappel(cxt):
#    t1 = threading.Timer(5,allrappel)
#    t1.daemon=True
#    t1.start()
#    #await cxt.invoke(bot.get_command('allrappel'))
    
#Affiche toutes les locations dans la console (debug only)
@bot.command()
async def afftout(cxt):
    if(cxt.message.author.id==323542898505416704 or cxt.message.author.id==736297202657394720):
        gethoro(cxt,"afftout")
        print(locas)
    else:
        await cxt.send("*Admin non vérifié, commande interdite*")

#Envoie toutes les locations enregistrées au nom de l'utilisateur de la commande
@bot.command()
async def meslocas(cxt):
    gethoro(cxt,"meslocas")
    email = cxt.message.author.id

    locasdemail = []

    for i in range(len(locas)):
        if(locas[i]['Email']==email):
            locasdemail.append(locas[i])
    
    await cxt.send("Voici les locations pour l'email entré :")
    res = ""
    for k in range(len(locasdemail)):
        res = res + str(k) + ". " + joli(locasdemail[k])[0]+" , date de fin : "+joli(locasdemail[k])[1] + "\n"
    if res!="":
        await cxt.send(res)
    else:
        await cxt.send("Pas de location à cette adresse email")

#Lance le bot, pas toucher
bot.run(token)