import discord
from discord.ext import commands
from belphegor import utils
from belphegor.utils import token, config
import asyncio
import aiohttp
import psutil
import os
import time
from motor import motor_asyncio

#==================================================================================================================================================

class BelphegorContext(commands.Context):
    async def confirm(self):
        await self.message.add_reaction("\u2705")

    async def deny(self):
        await self.message.add_reaction("\u274c")

#==================================================================================================================================================

class Belphegor(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.process = psutil.Process(os.getpid())
        self.cpu_count = psutil.cpu_count()
        self.process.cpu_percent(None)
        self.start_time = utils.now_time()
        self.loop.create_task(self.load())
        self.block_users = []
        self.mongo_client = motor_asyncio.AsyncIOMotorClient()
        self.db = self.mongo_client.belphydb

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=BelphegorContext)
        await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot:
            return
        elif self.block_users:
            if message.author.id in self.block_users:
                return
        await self.process_commands(message)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await asyncio.sleep(5)
        await self.change_presence(game=discord.Game(name='with Chronos-senpai'))

    async def close(self):
        await super().close()
        await self.session.close()

    async def load(self):
        await self.wait_until_ready()
        with open("extensions.txt", encoding="utf-8") as file:
            extensions = file.read().strip().splitlines()
        for extension in extensions:
            try:
                self.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(f"Failed loading {extension}: {e}")
                return await self.logout()
        print("Done")

#==================================================================================================================================================

if __name__ == "__main__":
    belphegor = Belphegor(command_prefix=commands.when_mentioned_or("!!", ">>", "b>"), owner_id=config.OWNER_ID)
    belphegor.run(token.TOKEN)
