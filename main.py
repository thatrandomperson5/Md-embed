import discord as discord
from discord import app_commands
import os
from sa import keep_alive
import json as js
import requests
import myDiscordExt
import datetime
import re
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


#@client.event
#async def on_member_update(before, after: discord.Member):
    #await update(after)


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
    def __init__(self, q, pl, oninput, onerror, **kwargs):
        super().__init__(title=q)
        self.oni = oninput
        self.one = onerror
        self.kwargs = kwargs
        self.q = discord.ui.TextInput(
        label=q,
        placeholder=pl,
        )
        self.add_item(self.q)
        
    async def on_submit(self, interaction: discord.Interaction):
        await self.oni(interaction,self.q.value,**self.kwargs)

    #async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        #await self.one(interaction)
        #print(error)
class eCreator(discord.ui.View):
    def __init__(self, parent):
        self.parent: msg = parent
        super().__init__(timeout=None)
    @discord.ui.button(label='Set Target', style=discord.ButtonStyle.red)
    async def target(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TextInput("Set Target:", 
                                                        "target username and hash go here, example: example#9999",
                                                        self.ontargetset,
                                                        self.onfail,
                                                        
                                                       ))
    async def ontargetset(self, interaction: discord.Interaction,ans):
        match = re.search(r"^(.+)(#)([\d][\d][\d][\d])$", ans, flags=re.UNICODE)
        if not match:
            await interaction.response.send_message("Invalid target", ephemeral=True)
        else: 
            self.parent.settings["Target"] = ans
            await interaction.response.edit_message(embed=self.parent.starting_embed(self.parent.author))
            await interaction.followup.send("Target Set.", ephemeral=True)
            
    async def onfail(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Oops, something went wrong!", ephemeral=True)
    @discord.ui.button(label='Set Link', style=discord.ButtonStyle.grey)
    async def link(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TextInput("Set Link:", 
                                                        "URL here...",
                                                        self.onlinkset,
                                                        self.onfail,
                                                        
                                                       ))
    async def onlinkset(self, interaction: discord.Interaction, ans):
        match = re.search(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", ans)
        if not match:
            await interaction.response.send_message("Invalid URL", ephemeral=True)
        else: 
            self.parent.settings["Link"] = ans
            await interaction.response.edit_message(embed=self.parent.starting_embed(self.parent.author))
            await interaction.followup.send("Link Set.", ephemeral=True)
    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if None in self.parent.settings.values():
            await interaction.response.send_message("You need to fill out all the options first!", ephemeral=True)
        else:
            await interaction.response.edit_message(view=None, embed=self.makeEndEmbed())
    def makeEndEmbed(self):
        settings = self.parent.settings
        if settings["Advanced"]: a = ", Advanced"
        else: a = ""
        o = self.createEndData(settings)
        embed=discord.Embed(title="Embed Created!", description="Your {v}{a} embed!".format(v=settings["Version"],a=a), color=0xc10ae6)
        embed.add_field(name="Output", value="```{gen}```".format(gen=o[0]), inline=False)
        embed.add_field(name="Example", value="```{exm}```".format(exm=o[1]), inline=True)
        return embed
    def createEndData(self, settings):
        url1 = settings["Link"]
        splarget = settings["Target"].split("#")
        url2 = f"https://md-embed-site.dragonhunter1.repl.co/api/{settings['Version']}?tg={'#'.join(splarget[:-1])}&hash={splarget[-1]}"
        if settings["Advanced"]:
            out = "html\n<a href='{href}'><img height='40' alt='discord-profile' src='{src}'></a>\n".format(href=url1, src=url2)
            exm = "md\n# Some markdown\n\n<a href='{href}'><img height='40' alt='discord-profile' src='{src}'></a>\n\n## Some other markdown\n".format(href=url1, src=url2)
        else:
            out= "md\n![Discord Profile]({src})\n".format(src=url2)
            exm = "md\n# Some markdown\n![Discord Profile]({src})\n## Some other markdown\n".format(src=url2)
        return [out, exm]
    @discord.ui.select(placeholder="Version...", options=[
        discord.SelectOption(label='v1', description='Version 1 style', emoji='1️⃣'),
        discord.SelectOption(label='v2', description='Version 2 style', emoji='2️⃣'),
    ])
    async def version(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.parent.settings["Version"] = select.values[0]
        await interaction.response.edit_message(embed=self.parent.starting_embed(self.parent.author))
        await interaction.followup.send("Version Set.", ephemeral=True)
    @discord.ui.select(placeholder="Advanced?", options=[
        discord.SelectOption(label='True', description='Advanced style (Compact, linked, html)', emoji='✔️'),
        discord.SelectOption(label="False", description='Normal style (Large, link does not work, markdown)', emoji='❌'),
    ])
    async def adv(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.parent.settings["Advanced"] = eval(select.values[0])
        await interaction.response.edit_message(embed=self.parent.starting_embed(self.parent.author))
        await interaction.followup.send("Advanced? Set.", ephemeral=True)  
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
        self.author = author
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
            out += "\n    •**" + x + ":** " + str(y)
        return out   

@client.tree.command()
async def generate(interaction: discord.Interaction):
    """Generate a tag to embed an user profile in markdown."""
    themsg = msg(interaction.user)
    await interaction.response.send_message(**themsg())


#running the program
keep_alive()
client.run(os.getenv('TOKEN'))
