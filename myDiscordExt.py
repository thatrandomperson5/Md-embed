import discord
class Message:
    def __init__(self):
        self.message: str = ""
        self.embeds: list = []
        self.files: list = []
        self.eph: bool = False
        self.view: discord.View = None
    def add_embed(self, embed: discord.Embed):
        self.embeds.append(embed)
    def add_file(self, file: discord.File):
        self.files.append(file)
    def __call__(self):
        out =  {
            
            "content":self.message,
            "embeds": self.embeds,
            "files": self.files,
            "ephemeral": self.eph,
        }
        if self.view:
            out["view"] = self.view
        return out