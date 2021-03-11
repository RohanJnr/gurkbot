import asyncio
from contextlib import suppress
from datetime import datetime, time, timedelta
from typing import List

from asyncpg import Record
from bot import constants
from bot.converters import OffTopicName
from discord.ext.commands import Bot, Cog, Context, group
from loguru import logger


class OffTopicNames(Cog):
    """Manage off-topic channel names."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.bot.loop.create_task(self.update_ot_channel_name())

    @group(name="offtopicnames", aliases=("otn",), invoke_without_command=True)
    async def off_topic_names(self, ctx: Context) -> None:
        """Commands for managing off-topic-channel names."""
        await ctx.send_help(ctx.command)

    @off_topic_names.command(name="add")
    async def add_ot_name(self, ctx: Context, name: OffTopicName) -> None:
        """Add off topic channel name."""
        async with self.bot.db_pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    "INSERT INTO off_topic_channel_name(channel_name) VALUES($1)", name
                )
        await ctx.send(f"`{name}` has been added!")

    @off_topic_names.command(name="del")
    async def delete_ot_name(self, ctx: Context, name: OffTopicName) -> None:
        """Delete off topic channel name."""
        async with self.bot.db_pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    "DELETE FROM off_topic_channel_name WHERE channel_name=$1", name
                )
        await ctx.send(f"`{name}` has been deleted!")

    async def random_ot_name(self, limit: int = 1) -> List[Record]:
        """Fetch random ot channel name."""
        async with self.bot.db_pool.acquire() as connection:
            async with connection.transaction():
                ot_names = await connection.fetch(
                    "SELECT channel_name FROM off_topic_channel_name ORDER BY random() limit $1",
                    limit,
                )
        return ot_names

    async def update_ot_channel_name(self) -> None:
        """Update ot-channel name everyday at midnight."""
        while not self.bot.is_closed():
            now = datetime.utcnow()
            midnight_datetime = datetime.combine(
                now.date() + timedelta(days=1), time(0)
            )
            till_midnight = int((midnight_datetime - now).total_seconds())
            # await asyncio.sleep(till_midnight)
            logger.info(
                f"Sleeping for {till_midnight} before renaming off topic channel."
            )
            await asyncio.sleep(60)

            guild = self.bot.get_guild(constants.GUILD_ID)
            channel = guild.get_channel(constants.Channels.off_topic)

            channel_name_record = await self.random_ot_name()
            with suppress(IndexError):
                await channel.edit(name=channel_name_record[0]["channel_name"])
                logger.info(
                    f"Channel name changed to {channel_name_record[0]['channel_name']}."
                )


def setup(bot: Bot) -> None:
    """Load cog."""
    bot.add_cog(OffTopicNames(bot))
