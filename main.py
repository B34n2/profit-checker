from discord import Intents, Status, Game, Activity, ActivityType, Object
from discord.ext.commands import Bot

from os import getenv, system, name
from dotenv import load_dotenv

load_dotenv()
clearConsole = lambda: system('cls' if name in ('nt', 'dos') else 'clear')
clearConsole()

intents = Intents.default()
intents.guilds = True 
intents.members = True

bot=Bot(command_prefix='!', intents=intents, status=Status.idle, activity=Game(name="Booting"))   

bot.color = int(getenv('EMBED_COLOR'), 16)

@bot.event
async def on_ready():
    name_=bot.user.name
    print('\x1b[0;30;44m' + f'Logged in as {name_}' + '\x1b[0m' + '\n    ----------')
    print('\x1b[6;30;42m' + 'Bot - Online' + '\x1b[0m' + '\n')
    await bot.change_presence(status=Status.online, activity=Activity(type=ActivityType.watching, name="profits"))

    await bot.wait_until_ready()
    await bot.tree.sync(guild=Object(id=(int(getenv('GUILD_ID')))))

# It loads the cogs.commandsCog extension using the setup_hook event
@bot.event
async def setup_hook():
    initial_extensions = ['cogs.commandsCog']
    if __name__ == '__main__':
       for extension in initial_extensions:
            await bot.load_extension(extension)

bot.run(getenv('BOT_TOKEN'))
