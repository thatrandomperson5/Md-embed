import discord as discord
from discord import app_commands
import os
from sa import keep_alive
import json as js
import requests
#intents setup so you don't have too
intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)
MY_GUILD = discord.Object(id=1003080614381109298)


class editJson:
    def __init__(self, file):
        self.file = file
        self.json = {}
    def __enter__(self):
        with open(self.file,"r") as p:
            self.json = js.load(p)
        return self
    def __exit__(self, type, value, tb):
        
        with open(self.file, "w") as p:
            js.dump(self.json, p, indent=4)
        del self

intents = discord.Intents().all()
client = discord.Client(intents=intents)
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

client.run(os.getenv('TOKEN'))
#logging in
@client.event
async def on_ready():
    
    print('We have logged in as {0.user}'.format(client))
    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Your info'))
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
    with open("local-copy.json") as ll:
        o = js.load(ll)
    url = 'https://api.jsonbin.io/v3/b/62eb192ee13e6063dc69eb00'
    headers = {
    'Content-Type': 'application/json',
    'X-Master-Key': os.getenv("JSONKEY")
    }
    req = requests.put(url, json=o, headers=headers)
    print(req.text)
class gen(discord.ui.Modal, title='Generate a MD embed for your discord account!'):
    discord.ui.description
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {self.name.value}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        
        
@tree.command()
async def generate(interaction: discord.Interaction):
    """Generate a tag to embed an user profile in markdown."""
    await interaction.response.send_modal(gen())


#running the program
keep_alive()
client.run(os.getenv('TOKEN'))
