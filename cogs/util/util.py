import base64
import json
import math
import platform
import sys
from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

import cpuinfo
import discord
import pip._vendor.requests
import psutil
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Shows the avatar of a user")
    @app_commands.describe(member="The member whose avatar you want to view")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        embed = discord.Embed(title="Download Avatar",
                              url=member.avatar, color=0x00EFDB,)
        embed.set_author(name=member.name + "`s avatar",
                         url="https://discord.com/users/" + str(member.id), icon_url=member.avatar,)
        embed.set_image(url=member.avatar)
        embed.set_footer(
            text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="base64decode", description="Decodes a Base64 string")
    @app_commands.describe(text="What is your encoded text?")
    async def base64decode(self, interaction: discord.Interaction, text: str):
        decoded = base64.b64decode(text).decode("utf-8", "ignore")
        embed = discord.Embed(
            title="Your decoded text:\n ||" + str(decoded) + "||", color=0x00D9FF)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="base64_encode", description="Base64 encodes a string")
    @app_commands.describe(text="What is the text you want to encode?")
    async def base64_encode(self, interaction: discord.Interaction, *, text: str):
        string_bytes = text.encode("ascii")

        base64_bytes = base64.b64encode(string_bytes)
        base64_string = base64_bytes.decode("ascii")

        embed = discord.Embed(
            title="Your encoded text:\n ||" + str(base64_string) + "||", color=0x00D9FF)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # I was bored...
    @app_commands.command(name="yt", description="Direct-Download for your YT video")
    @app_commands.describe(url="Which YT video do you want to download?")
    async def yt(self, interaction: discord.Interaction, url: str):
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            if "https://youtu.be/" in url:
                url.replace("https://youtu.be/",
                            "https://www.youtube.com/watch?v=")

            vgm_url = "https://8downloader.com/download?v=" + url
            html_text = requests.get(vgm_url).text
            soup = BeautifulSoup(html_text, "html.parser")
            download = soup.find("a", href=True, text="Download")["href"]

            link = "http://tinyurl.com/api-create.php?url=" + str(download)
            short_url = requests.get(link).text

            embed = discord.Embed(
                title="Click here to download your Video", url=short_url, color=0xFF0000)
            embed.set_author(name="Your download link is ready")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Invalid URL detected")

    @app_commands.command(name="userinfo", description="Shows information about a user")
    @app_commands.describe(member="About which member do you want to get infos?")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user

        user_created_at = member.created_at.strftime("%b %d, %Y %I:%M %p")
        joined_at = member.joined_at.strftime("%b %d, %Y %I:%M %p")

        embed = discord.Embed(color=member.color)
        embed.set_thumbnail(url=member.avatar)
        embed.set_author(name=f"{member.name}'s Info", icon_url=member.avatar)
        embed.add_field(
            name="Tag", value=f"```{member.name}#{member.discriminator}```", inline=False)
        embed.add_field(name="ID", value=f"```{member.id}```", inline=False)
        embed.add_field(name="Creation",
                        value=f"```{user_created_at}```", inline=False)
        embed.add_field(
            name="Avatar", value=f"[Click here]({member.avatar})", inline=False)
        embed.add_field(name="Joined", value=f"{joined_at}", inline=True)
        embed.add_field(name="Nickname", value=f"{member.nick}", inline=True)
        embed.add_field(name="Highest Role",
                        value=f"{member.top_role.mention}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="ping", description="Pong")
    async def ping(self, interaction: discord.Interaction):

        # Calculate the ping in milliseconds
        ping_ms = round(self.bot.latency * 1000)

        if ping_ms <= 50:
            color = 0x44FF44
        elif ping_ms <= 100:
            color = 0xFFD000
        elif ping_ms <= 200:
            color = 0xFF6600
        else:
            color = 0x990000

        embed = discord.Embed(
            title="PING", description=f"Pong! The ping is **{ping_ms}** milliseconds!", color=color,)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fact", description="Shows you a useless fact")
    @app_commands.describe(language="In which language should your useless fact be shown?")
    async def fact(self, interaction: discord.Interaction, language: Literal["English", "German"] = "English"):
        try:
            language_codes = {"English": "en", "German": "de"}
            code = language_codes.get(language)
            if not code:
                await interaction.response.send_message("Sorry, that language is not supported.", ephemeral=True)
                return

            url = f"https://uselessfacts.jsph.pl/random.json?language={code}"
            factembed = discord.Embed(timestamp=datetime.now(), color=discord.Color.dark_red(
            )).set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

            try:
                response = requests.get(url)
                if response.status_code != 200:
                    factembed.add_field(name="Error Code:",
                                        value=response.status_code)
                    await interaction.response.send_message(embed=factembed, ephemeral=True)
                    return

                data = response.json()
                fact = data["text"]
                factembed.add_field(name="Useless Fact:", value=fact)
                await interaction.response.send_message(embed=factembed, ephemeral=True)
            except requests.exceptions.RequestException as e:
                factembed.add_field(name="Error:", value=str(e))
                await interaction.response.send_message(embed=factembed, ephemeral=True)
            except ValueError:
                factembed.add_field(
                    name="Error:", value="Failed to parse response as JSON.")
                await interaction.response.send_message(embed=factembed, ephemeral=True)
        except Exception as e:
            print(e)

    @app_commands.command(name="short", description="Short a url")
    @app_commands.describe(shortner="Which shortner service do you want to use?")
    async def short(self, interaction: discord.Interaction, url: str, shortner: Literal["anditv.it", "tinyurl", "is.gd", "urlz (only ascii)"] = "tinyurl",):
        shortener_urls = {
            "anditv.it": "https://anditv.it/short/api/",
            "tinyurl": "http://tinyurl.com/api-create.php",
            "is.gd": "http://is.gd/api.php",
            "urlz": "https://urlz.fr/api_new.php",
        }

        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            await interaction.response.send_message("Invalid URL detected. Please enter a valid URL.")
            return

        try:
            shortener_url = shortener_urls[shortner]
            payload = {"url": url}
            response = requests.post(shortener_url, data=payload)

            if response.status_code == 400:
                raise ValueError("Invalid URL")
            elif response.status_code == 401:
                raise ValueError("Unauthorized")
            elif response.status_code != 200:
                raise ValueError(
                    f"Unexpected HTTP status code: {response.status_code}")

        except Exception as e:
            print("Error while shortening URL: %s", e)
            embed = discord.Embed(title="An unexpected error occurred",
                                  imestamp=datetime.now(), color=discord.Color.dark_red(),)
            embed.set_footer(text=interaction.guild.name,
                             icon_url=interaction.guild.icon.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="botinfo", description="Shows information about the bot.")
    async def botinfo(self, interaction: discord.Interaction):
        name = self.bot.user
        id = self.bot.user.id
        python_version = platform.python_version()
        os_version = platform.system()
        cpu_name = cpuinfo.get_cpu_info()['brand_raw']
        ram_usage = psutil.virtual_memory().percent

        info = f"Bot-Name: {name} ({id}) \nPython: {python_version}\nOS: {os_version}\nCPU: {cpu_name}\nRAM: {ram_usage} %"

        embed = discord.Embed(color=0x00D9FF)
        embed.add_field(name="Bot Info", value=f"```{info}```", inline=False)
        embed.set_footer(text=interaction.user.name,
                         icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='discordstatus', description="Shows you the discord server status")
    async def discordstatus(self, interaction: discord.Interaction):
        try:
            response = requests.get(
                "https://discordstatus.com/api/v2/summary.json")
            data = json.loads(response.text)
            if response.status_code != 200:
                raise ValueError(
                    f"Unexpected HTTP status code: {response.status_code}")
            components = [{'name': component["name"], 'value': component["status"].capitalize(
            ), 'inline': True} for component in data["components"]]

            embed = discord.Embed(title=data["status"]["description"],
                                  description=f"[Discord Status](https://discordstatus.com/)\n **Current Incident:**\n {data['status']['indicator']}",
                                  color=0x00D9FF,
                                  timestamp=datetime.now())
            embed.set_thumbnail(
                url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png")
            for component in components:
                embed.add_field(
                    name=component["name"], value=component["value"], inline=component["inline"])
            await interaction.response.send_message(embed=embed)
        except ValueError as e:
            embed = discord.Embed(
                title="Error while retrieving discord status",
                description=str(e),
                color=discord.Color.dark_red(),
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message("Error: " + str(e))


async def setup(bot):
    await bot.add_cog(Util(bot))
