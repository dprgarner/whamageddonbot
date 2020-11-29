"""
Adapted from this example in the docs.
https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
"""

import os
import asyncio

import discord
import youtube_dl

from discord.ext import commands

# Uncomment to suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


YEE = 'https://www.youtube.com/watch?v=q6EoRBvdVPQ'
WHAM = 'https://www.youtube.com/watch?v=-YUH8Xfz-jg'


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, loop=None, stream=False):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Wham(commands.Cog):
    video_url = YEE

    def __init__(self, bot):
        self.bot = bot

    async def join(self, ctx, channel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    async def stream(self, ctx, url):
        async def on_video_done(error):
            if error:
                print('Player error: %s' % error)
            else:
                print('Wham completed successfully.')
            await ctx.voice_client.disconnect()

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    on_video_done(e),
                    self.bot.loop
                )
            )

    @commands.command()
    async def wham(self, ctx, *, channel: discord.VoiceChannel):
        """Whams a voice channel"""

        await self.join(ctx, channel)
        await self.stream(ctx, self.video_url)
        await ctx.send(
            'Whamming "{}". Type `!stop` to stop Whamming.'.format(
                channel)
        )

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong")

    @wham.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description='Wham!'
)


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Wham(bot))
bot.run(os.getenv('TOKEN'))
