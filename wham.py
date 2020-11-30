"""
Adapted from this example in the docs.
https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
"""

import os
import asyncio

import youtube_dl
import discord
from discord.ext import commands

# Uncomment to suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''

ffmpeg_options = {
    'options': '-vn -ab 32k'
}


def download_video(url):
    """
    Synchronously download the video before starting the bot.
    """

    ytdl_format_options = {
        'format': 'worstaudio',
        'outtmpl': 'videos/%(extractor)s-%(id)s-%(title)s.%(ext)s',
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

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    data = ytdl.extract_info(url, download=True)
    filename = ytdl.prepare_filename(data)
    return filename


class Wham(commands.Cog):
    def __init__(self, bot, filename):
        self.bot = bot
        self.filename = filename

    async def join(self, ctx, channel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    async def stream(self, ctx):
        async def on_video_done(error):
            if error:
                print('Player error: %s' % error)
            else:
                print('Wham completed successfully.')

            await asyncio.sleep(5)
            await ctx.voice_client.disconnect()

        async with ctx.typing():
            player = discord.FFmpegOpusAudio(
                self.filename, bitrate=32, ** ffmpeg_options)
            # player = discord.PCMVolumeTransformer(
            #     discord.FFmpegPCMAudio(self.filename, **ffmpeg_options)
            # )
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
        await self.stream(ctx)
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
        print('ping!')
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


# filename = download_video(os.environ.get('VIDEO'))
bot.add_cog(Wham(
    bot, 'videos/youtube-bwNV7TAWN3M-Wham_-_Last_Christmas_Official_4K_Video.webm'))
bot.run(os.getenv('TOKEN'))
