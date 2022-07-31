import discord
from discord import app_commands
import os
from sa import keep_alive, getc
#intents setup so you don't have too
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
getc(client)
tree = app_commands.CommandTree(client)
MY_GUILD = discord.Object(id=1003080614381109298)
#logging in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    keep_alive()
    tree.copy_global_to(guild=MY_GUILD)
    await tree.sync(guild=MY_GUILD)
class gen(discord.ui.Modal, title='Generate'):
    name = discord.ui.TextInput(
        label='Name',
        placeholder='Your name here...',
    )
    
    feedback = discord.ui.TextInput(
        label='What do you think of this new feature?',
        style=discord.TextStyle.long,
        placeholder='Type your feedback here...',
        required=False,
        max_length=300,
    )
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {self.name.value}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        
        
@tree.command()
async def generate(interaction: discord.Interaction):
    """Generate a tag to embed an user profile in markdown."""
    await interaction.response.send_modal(gen())

#running the program
client.run(os.getenv('TOKEN'))