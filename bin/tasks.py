from datetime import datetime

import discord
from discord.ext import commands, tasks

from bin.config import conf
from bin.database import DataBase
from bin.reddit import reddit


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.db_conn
        self.channel_id = conf.get('discord', 'channel_id')
        self.keyword_task.start()

    @tasks.loop()
    async def keyword_task(self):
        await self.bot.wait_until_ready()

        subreddit = await reddit.subreddit("matthewsplaypalace")  # dankmemes+memes+okbuddyretard
        async for submission in subreddit.stream.submissions():
            keywords = DataBase.get_keywords()
            matching = [s for s in keywords if submission.title.lower() in s[0].lower()]
            if matching:
                await self.send_notification(submission, matching[0])

    async def send_notification(self, submission, matching):
        await submission.author.load()
        channel = await self.bot.fetch_channel(self.channel_id)
        embed = discord.Embed(color=0xEE7E38, url=f"https://reddit.com{submission.permalink}")
        embed.title = submission.title
        embed.set_author(name=submission.author, icon_url=submission.author.icon_img)
        if not submission.is_self:
            embed.set_image(url=submission.url)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f"👍 {submission.score} | 💬 {submission.num_comments}")

        await channel.send(f"<@{matching[1]}> your keyword was mentioned in r/{submission.subreddit}!", embed=embed)


def setup(bot):
    bot.add_cog(Tasks(bot))