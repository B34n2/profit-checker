from aiohttp import ClientSession
from discord.ext import commands
from discord import Embed, app_commands, Object, utils
from typing import Optional
from os import getenv

class commandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

# This function is a hybrid command that is only available in the guild with the ID specified in the
# environment variable GUILD_ID
    @commands.hybrid_command()
    @app_commands.guilds(Object(int(getenv('GUILD_ID'))))
    async def profit(self, ctx: commands.Context, txid: str, list_price: Optional[float] = None) -> None:

        opensea = False

        headers_moralis = {
            'X-API-Key': getenv('MORALIS_API_KEY'),
            'accept': 'application/json'
        }

        headers_os = {
            'X-API-KEY': getenv('OS_API_KEY'),
            'accept': 'application/json'
        }

# It's getting the data from the API's.
        async with ClientSession() as session:
            async with session.get(f'https://deep-index.moralis.io/api/v2/transaction/{txid}?chain=eth', headers=headers_moralis) as resp:
                moralis_res = await resp.json()
        if moralis_res == None:
            await ctx.send('**Invalid transaction ID**')

        async with ClientSession() as session:
            async with session.get(f"https://api.opensea.io/api/v1/asset_contract/{moralis_res['logs'][0]['address']}?format=json", headers=headers_os) as resp:
                if resp.status != 500:
                    os_res = await resp.json()
                    opensea = True

        if opensea == True:
            async with ClientSession() as session:
                async with session.get(f'https://api.opensea.io/api/v1/collection/{os_res["collection"]["slug"]}') as resp:
                    os_stats = await resp.json()

        os_contracts = ["0x7f268357a8c2552623316e2562d90e642bb538e5", "0x7be8076f4ea4a4ad08075c2508e481d6c946d12b"]

# It's calculating the transaction fee and the purchase amount.
        purchase_amount = float(int(moralis_res["value"]) / 1000000000000000000)
        transaction_fee = round((int(moralis_res["gas_price"]) * int(moralis_res["receipt_gas_used"])) / pow(10, 18), 4)
        value = float( (int(moralis_res["value"]) / 1000000000000000000) + ((int(moralis_res["gas_price"]) * int(moralis_res["receipt_gas_used"])) / pow(10, 18)))

        newline = '\n'
    
        if moralis_res['to_address'] in os_contracts:
            opensea = True
            platform_fee = int(os_res["collection"]["opensea_seller_fee_basis_points"]) / 100
            floor_price = os_stats["collection"]["stats"]["floor_price"] if os_stats["collection"]["stats"]["floor_price"] != None else float(0)
            royalties = (int(os_res["dev_seller_fee_basis_points"]) / 100) + platform_fee
            derisk_amount = round(value + ((value / 100) * ((int(os_res["dev_seller_fee_basis_points"]) / 100) + platform_fee)), 4)
            profit=round(floor_price - value, 4)
        else:
            opensea = False

# It's creating an embed.
        embed=Embed(title=txid, url=f'https://etherscan.io/tx/{txid}', color=ctx.bot.color).set_author(name='Profit Calculator').add_field(
            name='Details', value=f'{("Floor: " + str(floor_price) + " Ξ") if opensea == True else ""}{(newline + "Purchase Amount: " + str(purchase_amount)) if opensea == True else ""}\nTransaction Fee: {transaction_fee}{(newline + "Royalties: " + str(royalties) + "%") if opensea == True else ""}{(newline + "**Profit: " + str(profit) + " Ξ**") if opensea == True else ""}\nBreakeven Amount: **{derisk_amount if opensea == True else round(value, 4)} Ξ**', inline=True).set_footer(text='Powered by Beanstalk', icon_url=self.bot.user.avatar.url)

        listing = False
        if list_price != None:
            try:
                listing = True
                embed.add_field(name='Profit', value=f'**{round(float(list_price) - (derisk_amount if opensea == True else value), 4)} Ξ**', inline=True)
            except:
                await ctx.send('**List price must be a number, please try again**')
                return

        embed.timestamp = utils.utcnow()
        if opensea == True:
            embed.add_field(name=f'{os_res["collection"]["slug"]} Stats', value=f'Supply: {int(os_stats["collection"]["stats"]["count"])}\nHolders: {os_stats["collection"]["stats"]["num_owners"]}\nVolume Traded: {round(os_stats["collection"]["stats"]["total_volume"], 2)} Ξ\nRoyalties: {int(os_res["collection"]["dev_seller_fee_basis_points"]) / 100}%\nPlatform Fees: {platform_fee}%',inline=False if listing == True else True)
            embed.set_thumbnail(url=os_res['collection']['image_url'])

        await ctx.send(embed=embed)
     
    @commands.Cog.listener()
    async def on_ready(self):
        print('\x1b[6;30;42m' + f'{__name__} Cog - Online' + '\x1b[0m')

async def setup(bot):
    await bot.add_cog(commandsCog(bot)) 