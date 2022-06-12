import os
import sys
import time
import socket
import random
import secrets
import discord
import asyncio
import tempfile
from datetime import date
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands
from collections import OrderedDict

from argofamiglia import ArgoFamiglia
from utils import *

# Test:
# DISCORD_TOKEN = ""

# Real one:
DISCORD_TOKEN = "Insert Discord Bot Token here"
PASSWORD = "MyP4ssw0rd$48312"
USERNAME = "argoTest12345"
SCHOOL_CODE = "278912"


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class DiscordBot:
    def __init__(self, school, username, password):
        self.client = commands.Bot(command_prefix='!')
        self.my_server = None
        self.comunicazioni_channel = None
        self.compiti_channel = None
        # Test:
        # self.server_id = 1234567890234567890
        # self.comunicazioni_channel_id = 1234567890234567890
        # self.compiti_channel_id = 1234567890234567890

        # Real one:
        self.server_id = 1234567890234567890
        self.compiti_channel_id = 1234567890234567890
        self.comunicazioni_channel_id = 1234567890234567890
        
        self.__school = school
        self.__username = username
        self.__password = password

        self.session = ArgoFamiglia(school, username, password)
        if self.session.online:
            self.comunicazioni = self.getBachecaData(self.session.argoRequest("bachecanuova"))
            self.promemoria = self.getPromemoriaData(noDate=True)
        else:
            print("invalid credentials")
            sys.exit(1)

    async def sendCompiti(self, ctx, args):
        special = None
        folder_name = None # Solo per immagine
        toImage = False
        day = None
        days = OrderedDict({
            "lunedì": 0,
            "martedì": 1,
            "mercoledì": 2,
            "giovedì": 3, 
            "venerdì": 4, 
        })
        
        dkeys = list(days.keys())
        sml = {"lun": dkeys[0], "mar": dkeys[1], "mer": dkeys[2], "gio": dkeys[3], "ven": dkeys[4]}

        if args:
            day = args[0].lower()

        if args and args[-1].lower() == "i":
            toImage = True
            args = list(args)
            args.pop(-1)

        if not args:
            date = datetime.fromtimestamp(time.time() + 86400).strftime("%Y-%m-%d")
            special = "domani"
        elif day == "oggi":
            date = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
            special = "oggi"
        elif day == "domani":
            date = datetime.fromtimestamp(time.time() + 86400).strftime("%Y-%m-%d")
            special = "domani"
        elif day == "dopodomani":
            date = datetime.fromtimestamp(time.time() + 172800).strftime("%Y-%m-%d")
            special = "dopodomani"
        elif day and (day in days or day in sml):
            if day in sml:
                day = sml[day]
            offset = days[day]
            date = next_weekday(datetime.now(), offset).strftime("%Y-%m-%d")
            special = f"il prossimo {day}"
        else:
            date = ' '.join(args)

        if toImage: # Directory con un nome random, molto inutile, meglio lasciarla così
            TMP_DIR = tempfile.gettempdir()
            folder_name = f"{TMP_DIR}/{hex(int(str(self.server_id) + str(random.randint(0, 65537)) + str(self.compiti_channel_id)))[2:]}"
            os.mkdir(folder_name)

        compiti = self.getCompiti(date, special, toImage, folder_name)
        if len(compiti) == 3:
            if compiti[0]:
                await ctx.send(compiti[1], file=discord.File(open(f"{folder_name}/{compiti[2]}.png", "rb"), filename=f"{compiti[2]}.png"))
                return
        else:
            if compiti == "INVALID_DATE":
                compiti = "Inserisci una data valida."

            await ctx.send(compiti)

    async def sendPromemoria(self, ctx, args):
        await ctx.send(self.getPromemoria())

    def getCompiti(self, data, special, toImage, temp_dir=None):
        compiti = self.session.argoRequest("compiti")
    
        date = dict()
        for x in compiti.keys(): # Inserisce in una dict i compiti
            if type(compiti[x]) == list:
                for compito in compiti[x]:
                    if compito["datCompiti"] not in date:
                        date[compito["datCompiti"]] = []
                    date[compito["datCompiti"]].append(compito)
        
        data_format = "%d-%m-%Y"
        tmp_data = data.replace("/", "-").replace("\\", "-").replace(" ", "-")
        tmp_data = tmp_data.replace(".", "-").replace(",", "-").replace("_", "-")

        if len(tmp_data) != 8 and len(tmp_data) != 10:
            return "INVALID_DATE"

        if len(tmp_data) == 8:
            data_format = "%d-%m-%y"

        if tmp_data in date:
            compiti = date[tmp_data]
        else: # Si potrebbe migliorare
            try:
                compiti = date[datetime.strptime(tmp_data, data_format).strftime("%Y-%m-%d")]
            except (ValueError, KeyError):
                try:
                    compiti = date[datetime.strptime(tmp_data, "%y-%m-%d").strftime("%Y-%m-%d")]
                except (ValueError, KeyError):
                    compiti = []

        if not compiti:
            if not special:
                return f"❗ Non ci sono compiti per il {tmp_data}. ❗"

            else:
                return f"❗ Non ci sono compiti per {special}. ❗"

        if not special:
            msgCompiti = f"❗ **COMPITI PER IL {tmp_data}** ❗\n\n"
        else:
            msgCompiti = f"❗ **COMPITI PER {special.upper()}** ❗\n\n"

        if toImage:
            fin = f"compiti-{secrets.token_hex(8)}"
            fout = f"output-{fin}"
            if compiti2IMG(fin, fout, compiti, temp_dir):
                return True, msgCompiti, fout
            
        for compito in compiti:
            msgCompiti += f"📕 {compito['desMateria']} 📕\n{compito['desCompiti']}\n\n"
        
        return msgCompiti

    def getPromemoriaData(self, noDate=False):
        data = self.session.argoRequest("promemoria")["dati"]
        promemoria = []
        tstamp = time.mktime(time.strptime(datetime.now().strftime("%Y-%m-%d"), '%Y-%m-%d'))
        for prom in data:
            if not noDate:
                if time.mktime(time.strptime(prom["datGiorno"], '%Y-%m-%d')) < tstamp:
                    continue
            promemoria.append(prom)
        return promemoria

    def getPromemoria(self):
        promemoria = self.getPromemoriaData()
            
        if not promemoria:
            return f"❗Nessun promemoria presente❗"

        msgPromemoria = ""
        for prom in promemoria:
            msgPromemoria += f"🎟️ **{prom['desMittente']} - {datetime.strptime(prom['datGiorno'],'%Y-%m-%d').strftime('%d/%m/%Y')}** 🎟️\n{prom['desAnnotazioni']}\n\n"
        
        return msgPromemoria
        
    def getBachecaData(self, bacheca):
        try:
            comunicazioni = dict()
            for comunicazione in bacheca["dati"]: # Lista
                files = []
                links = []
                for allegato in comunicazione["allegati"]:
                    files.append(allegato["desFile"])
                    links.append(self.session.getUrl(allegato["prgAllegato"], allegato["prgMessaggio"]))
                comunicazioni[comunicazione["desMessaggio"]] = {"files": files, "links": links}

            return comunicazioni
        except Exception as e:
            return self.comunicazioni

    @tasks.loop(hours=1)
    async def resetSessionTask(self):
        self.session = ArgoFamiglia(self.__school, self.__username, self.__password)
        now = datetime.now()
        if now.hour == 14 and (now.weekday()+1)%7 <= 4:
            while not self.my_server or not self.comunicazioni_channel:
                await asyncio.sleep(1)
            await self.sendCompiti(self.compiti_channel, [])

    @tasks.loop(minutes=2)
    async def argoPromemoriaTask(self):
        while not self.my_server or not self.comunicazioni_channel:
            await asyncio.sleep(1)

        temp_promemoria = self.getPromemoriaData(noDate=True)
        if self.promemoria != temp_promemoria:
            for x in temp_promemoria:
                if x not in self.promemoria:
                    try:
                        promemoria = x
                    except Exception as e:
                        print(e)
                    
                    try:
                        description = f"**❗Nuovo promemoria❗**\n@everyone\n 🎟️ **{promemoria['desMittente']} - {datetime.strptime(promemoria['datGiorno'],'%Y-%m-%d').strftime('%d/%m/%Y')}** 🎟️\n{promemoria['desAnnotazioni']}\n\n"
                        await self.comunicazioni_channel.send(description)
                    except Exception as e:
                        print(f"???{e}???")
                    
                    self.promemoria = temp_promemoria
                    break
                    

    @tasks.loop(minutes=2)
    async def argoComunicazioniTask(self):
        while not self.my_server or not self.comunicazioni_channel:
            await asyncio.sleep(1)

        temp_comunicazioni = self.getBachecaData(self.session.argoRequest("bachecanuova"))
        if self.comunicazioni != temp_comunicazioni: # Vuol dire che è presente una nuova comunicazione
            for x in temp_comunicazioni.keys():
                if x not in self.comunicazioni.keys():
                    try:
                        annuncio = temp_comunicazioni[x]
                        title = x
                    except Exception as e:
                        print(e)
                    try:
                        links = annuncio.pop("links")
                        folder = tempfile.gettempdir()
                        
                        embed = discord.Embed()
                        desc = ""
                        
                        files_to_read = []
                        files_to_send = []

                        for x in range(len(links)):
                            files_to_read.append(url2File(links[x], annuncio["files"][x], folder))
                        
                        for filename in files_to_read:
                            with open(filename, "rb") as f:
                                files_to_send.append(discord.File(f, filename=filename.split("/")[-1]))

                        if not links:
                            raise IndexError
                        description = f"🔑**{title}**\n📁Allegati i files📁:\n{desc}"
                        await self.comunicazioni_channel.send(f"**❗Nuova comunicazione❗**\n@everyone\n{description}", files=files_to_send)
                    except (IndexError, KeyError):
                        await self.comunicazioni_channel.send(f"**❗Nuova comunicazione❗**\n@everyone\n🔑**{title}**\n")
                    except TypeError as e:
                        print(e)
                    self.comunicazioni = temp_comunicazioni
                    break

    async def argoCompitiTask(self):
        pass # Da implementare

    def main(self):
        @self.client.command(pass_context=True)
        async def compiti(ctx, *args):
            await self.sendCompiti(ctx, args)

        @self.client.command(pass_context=True)
        async def promemoria(ctx, *args):
            await self.sendPromemoria(ctx, args)


        # @self.client.command(pass_context=True)
        # async def test(ctx, *args):
        #     await ctx.send(self.getPromemoria())
        
        @self.client.event
        async def on_ready():
            print(f"Bot started at {date.today()}")
            clearDir()

            if not self.my_server: # Abbandona i server se diversi da quello indicato
                self.my_server = self.client.get_guild(self.server_id)
            if not self.comunicazioni_channel:
                self.comunicazioni_channel = self.client.get_channel(self.comunicazioni_channel_id)
                self.compiti_channel = self.client.get_channel(self.compiti_channel_id)
            for server in self.client.guilds:
                if server != self.my_server:
                   await server.leave()

        @self.client.event
        async def on_server_join(server):
            if not self.my_server or not self.comunicazioni_channel: # Abbandona il server se è diverso da quello indicato
                self.my_server = self.client.get_guild(self.server_id)
                self.comunicazioni_channel = self.client.get_channel(self.comunicazioni_channel_id)
                self.compiti_channel = self.client.get_channel(self.compiti_channel_id)
            if server != self.my_server:
                await server.leave()

        self.argoComunicazioniTask.start()
        self.argoPromemoriaTask.start()
        self.resetSessionTask.start()
        asyncio.run(self.client.run(DISCORD_TOKEN))
    

def internet_connection(): # Controlla la connessione ad Internet
    for host in ["1.1.1.1","8.8.8.8"]:
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 53))
            return True
        except socket.error:
            pass
    else:
        return False 

while not internet_connection():
    print("No internet connection...")
    time.sleep(1)

print("Establishing the internet connection...")
obj = DiscordBot(SCHOOL_CODE, USERNAME, PASSWORD)
obj.main()
