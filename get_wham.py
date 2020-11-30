"""
Adapted from this example in the docs.
https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
"""

import os
import asyncio

import youtube_dl

# Uncomment to suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''

# VIDEO = 'https://www.youtube.com/watch?v=q6EoRBvdVPQ'  # Yee
VIDEO = 'https://www.youtube.com/watch?v=-YUH8Xfz-jg'  # Wham! lyrics

ffmpeg_options = {
    'options': '-vn'
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


filename = download_video(VIDEO)
print(filename)
