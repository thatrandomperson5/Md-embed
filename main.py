import discord as discord
from discord import app_commands
import os
from sa import keep_alive
import json as js
import requests
import myDiscordExt
import datetime
#intents setup so you don't have too

intents = discord.Intents().all()
MY_GUILD = discord.Object(id=1003080614381109298)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):

        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


client = MyClient(intents=intents)


class editJson:
    def __init__(self, file):
        self.file = file
        self.json = {}

    def __enter__(self):
        with open(self.file, "r") as p:
            self.json = js.load(p)
        return self

    def __exit__(self, type, value, tb):

        with open(self.file, "w") as p:
            js.dump(self.json, p, indent=4)
        del self


async def update(after):
    print("up")
    out = {
        "status": after.raw_status,
        #"act": after.activity,
        "avatar": after.avatar.url
    }
    with editJson("local-copy.json") as e:

        e.json[str(after.id)] = out

        o = e.json

    url = 'https://api.jsonbin.io/v3/b/62eb192ee13e6063dc69eb00'
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': os.getenv("JSONKEY")
    }
    req = requests.put(url, json=o, headers=headers)
    print(req.text)


@client.event
async def on_member_update(before, after: discord.Member):
    await update(after)


@client.event
async def on_member_join(before, after: discord.Member):
    await update(after)


@client.event
async def on_user_update(before, after):
    await update(after)


@client.event
async def on_presence_update(before, after):
    await update(after)


#logging in
@client.event
async def on_ready():

    print('We have logged in as {0.user}'.format(client))

    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name='Your info'))

    with open("local-copy.json") as ll:
        o = js.load(ll)
    url = 'https://api.jsonbin.io/v3/b/62eb192ee13e6063dc69eb00'
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': os.getenv("JSONKEY")
    }
    req = requests.put(url, json=o, headers=headers)
    print(req.text)

class TextInput(discord.ui.Modal):
    def __init__(self, q, pl, oninput, onerror):
        self.oni = oninput
        self.one = onerror
        self.q = discord.ui.TextInput(
        label=q,
        placeholder=pl,
        )
        super().__init__(title=q)
    async def on_submit(self, interaction: discord.Interaction):
        self.oni(interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        self.one(interaction)
class eCreator(discord.ui.View):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(timeout=None)
    @discord.ui.button(label='Set Target', style=discord.ButtonStyle.red)
    async def target(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    @discord.ui.button(label='Set Link', style=discord.ButtonStyle.grey)
    async def link(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if None in self.parent.settings.values():
            await interaction.response.send_message("You need to fill out all the options first!", ephemeral=True)
class msg(myDiscordExt.Message):
    def __init__(self, author: discord.Interaction.user):
        super().__init__()
        self.settings = {
            "Target": None,
            "Link": "https://discord.gg/BrnAvMps",
            "Version": "v1",
            "Advanced": True,
        }
        self.view = eCreator(self)
        self.add_embed(self.starting_embed(author))
        self.eph = True
        
    def starting_embed(self, author: discord.Interaction.user):
        embed=discord.Embed(title="Embed Maker", description="The maker for your embed. Go by step by step clicking on the buttons according to the sections below and answer questions, then we will make I you an embed!\n\n**Dismiss Message To Cancel**", color=0xff79ff, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Target", value="(Click Set Target Button to set)\nThe username of the user you want the embed to be of.", inline=False)
        embed.add_field(name="Link", value="Set what clicking on the embed will send you to (Only works on advanced embeds). \n*Default*: an invite to this discord", inline=False)
        embed.add_field(name="Version", inline=False, value="The style that you want your embed to be. Check out styles with **/styles**.")
        embed.add_field(name="Advanced", inline=False, value="If you want your output to be html or markdown.")
        embed.add_field(name="Your Values:", inline=False, value=self.valueTree(self.settings))
        embed.set_footer(text="Requested By "+str(author), icon_url=author.avatar.url)
        return embed
    def valueTree(self, val):
        out = ""
        for x, y in list(val.items()):
            out += "\n    **" + x + ":** " + str(y)
        return out   

@client.tree.command()
async def generate(interaction: discord.Interaction):
    """Generate a tag to embed an user profile in markdown."""
    themsg = msg(interaction.user)
    await interaction.response.send_message(**themsg())


#running the program
keep_alive()
client.run(os.getenv('TOKEN'))
