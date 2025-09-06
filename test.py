import discord
from discord.ext import commands
import logging, requests
import urllib.request, json
import time, datetime


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

TOKEN = "MTM5Nzk4OTEwMDE3NDQ0MjUwNw.GVBLbn.4yCGH3Sb888DZiiDmPawVx6nRX0gjeE9QSnEL8"


#print("Getting steam games info. . .")
#with urllib.request.urlopen("https://api.steampowered.com/ISteamApps/GetAppList/v2/") as url:
#    games = json.load(url)

listOfRoles = []
favoriteGames = []
favoriteID = []
f = open('OPTIONS.txt', 'r')
for line in f:
    l = line[:-1].split(';')
    match l[0]:
        case 'favoriteGames':
            for n in l[1::]:
                favoriteGames.append(n)
            print(favoriteGames)

        case 'favoriteID':
            for n in l[1::]:
                favoriteID.append(int(n))
            print(favoriteID)

        case 'listOfRoles':
            for n in l[1::]:
                listOfRoles.append(n)
            print(listOfRoles)
f.close()


def updateFile():
    f = open("OPTIONS.txt", 'w')
    s = 'favoriteGames'
    for n in favoriteGames:
        s += ';' + n
    f.write(s + '\n')
    s = 'favoriteID'
    for n in favoriteID:
        s += ';' + str(n)
    f.write(s + '\n')
    s = 'listOfRoles'
    for n in listOfRoles:
        s += ';' + n
    f.write(s)
    f.close()
    #print('works')


class BotClient(discord.Client):
    async def on_message(self, message):
        if message.author == self.user:
            return
        member = message.author
        print("LOG: " + str(member) + "\ttext: " + str(message.content) + "\t time: " + str(datetime))
        text = message.content.lower().split()
        if message.content.lower()[0] == '/':
            if len(text) == 1:
                print("Error 1")
                await message.channel.send("Мяу?")
            else:
                print(f"Command: {text[0]}; Data: {text[1]}, user: {str(member)}")


        if message.content.lower() == 'test':
            await message.channel.send("Мяу")


        if '/update' == text[0]:
            #print(text)
            link = ""
            if '/id/' in text[1]:
                link = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=68EDAC16A2FD3691EA2FED4A25772C62&vanityurl=" + text[1].split('/')[-2]
                with urllib.request.urlopen(link) as url:
                    data = json.load(url)
                    #print(data['response']['steamid'])
                    link = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=68EDAC16A2FD3691EA2FED4A25772C62&steamid=" + data['response']['steamid'] + "&format=json/include_appinfo"

            elif 'https' in text[1]:
                link = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=68EDAC16A2FD3691EA2FED4A25772C62&steamid=" + text[1][36:-1] + "&format=json/include_appinfo"

            else:
                link = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=68EDAC16A2FD3691EA2FED4A25772C62&steamid=" + text[1] + "&format=json/include_appinfo"
            print(link)
            listGamesUser = []
            try:
                with urllib.request.urlopen(link) as url:
                    data = json.load(url)
                    #print(data)
                    #print(data['response']['games'])
                    for n in data['response']['games']:
                        if n['appid'] in favoriteID:
                            listGamesUser.append(favoriteGames[favoriteID.index(n['appid'])])


            except:
                print("Error: GET STEAM INFO")
                await message.channel.send("Error: GET STEAM INFO")


            member = message.author
            print("Start giving roles to " + str(member) + "\nmember's games: ")
            print(listGamesUser)
            print(f"{str(member)} roles list: ")
            print(member.roles)
            for roleName in listGamesUser:
                if roleName not in listOfRoles:
                    await member.guild.create_role(name=roleName)
                    listOfRoles.append(roleName)
                    updateFile()

                role = discord.utils.get(message.guild.roles, name=roleName)

                try:
                    print("Adding roles...")
                    if role not in member.roles:
                        #await member.guild.create_role(name=roleName, hoist=True)
                        #await message.chanel.guild.add_roles(roleName)
                        await member.add_roles(role)
                        await message.channel.send("Role added")
                except:
                    print("Error: give role")
                    #await member.remove_roles(role)
                    await message.channel.send("Can't give role")
                """
                test = message.author
                role = discord.utils.get(message.guild.roles, name=i)
                if role in test.roles:
                    await message.channel.send("you already have a role")
                else:
                    await test.guild.create_role(name=i, hoist=True)
                    await test.add_roles(role)
                    await message.channel.send("Role added")
                    await message.chanel.guild.add_roles(i)
                """

            #print(listGamesUser)
            #print("!!!___!!!")

            #role_id = 1234567890  # Замени на ID нужной роли
            #role = message.channel.guild.get_role(role_id)


            """
            if role:
                await message.channel.guild.create_role(name=role_name, hoist=True)
                await message.channel.author.add_roles(role)
                await message.channel.send(f"Роль {role.name} успешно выдана!")
            else:
                print("Error: give role")
                await message.channel.send("Error give role")
            """


def main():
    client = BotClient(intents=intents)
    client.run(TOKEN)


if __name__ == '__main__':
    main()

#http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=68EDAC16A2FD3691EA2FED4A25772C62&vanityurl=userVanityUrlName