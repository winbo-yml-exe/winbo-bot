import random
import json
import os
import glob
from pathlib import Path
import nextcord
from nextcord.ext import commands
import platform
import psutil
from datetime import datetime
import requests

intents = nextcord.Intents.all()
client = commands.Bot(intents=intents)
serverdb = {}
cgcdb = {}
sad_stories = [
    "Winbo found a note in his mailbox: \"I’m sorry I couldn’t stay. Goodbye.\" He never saw his friend again.",
    "Winbo celebrated his birthday alone, his closest friends having forgotten the day entirely.",
    "Winbo sat in the chair that once held his best friend. The empty seat was a constant, painful reminder of his absence.",
    "Winbo found an old letter from a friend that was never read. The words of regret and apology were now lost to time.",
    "Winbo waited for his partner to remember their anniversary, but as the day passed without a word, the silence spoke volumes.",
    "Winbo looked at the last photo taken with his family before they drifted apart. The image was a bittersweet memory of happier times.",
    "Winbo’s phone remained silent, filled with messages from friends he could no longer reach. The emptiness of unreturned calls was deafening."
]
async def getairesponse(question):
    url = 'https://gpt4o-kohl.vercel.app/chat'
    payload = {
        'message': question,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('response', 'noresponse')
    else:
        return f"err-{response.status_code}-{response.text}"
try:
    if not os.path.isfile("serverdb.json"):
        with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
            json.dump(serverdb, sdbfile, indent=2)
            print("Created serverdb.json")
    else:
        with open("serverdb.json", "r", encoding="utf-8") as sdbfile:
            serverdb = json.load(sdbfile)
            print("Loaded serverdb.json")
except:
    pass
try:
    if not os.path.isfile("cgcdb.json"):
        with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
            json.dump(cgcdb, cgcdbfile, indent=2)
            print("Created serverdb.json")
    else:
        with open("serverdb.json", "r", encoding="utf-8") as cgcdbfile:
            cgcdb = json.load(cgcdbfile)
            print("Loaded cgcdb.json")
except:
    pass
try:
    if cgcdb["bans"]:
        cgcdb["bans"] = []
except:
    cgcdb["bans"] = []
with open("owner.txt", "r", encoding="utf-8") as ownerfile:
    owner = str(ownerfile.read().rstrip())
    cgcdb["owner"] = owner
    with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
        json.dump(cgcdb, cgcdbfile, indent=2)
        print("Loaded owner.txt")
with open("staff.txt", "r", encoding="utf-8") as stafffile:
    staff = str(stafffile.read().rstrip()).split(", ")
    cgcdb["staff"] = staff
    with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
        json.dump(cgcdb, cgcdbfile, indent=2)
        print(f"Loaded staff.txt ({staff})")

@client.event
async def on_ready():
    print(f"Logged in as \"{client.user}\"")

@client.event
async def on_message(message):
    if not message.author.bot and not message.content.startswith("/") and not str(message.author.id) in cgcdb["bans"]:
        for server in serverdb:
            await send_message_to_servers(message, server)
async def send_message_to_servers(message, server):
        if str(message.channel.id) == str(serverdb[server]["cgcchannel"]):
            for server in serverdb:
                try:
                    embed = nextcord.Embed(title=f"Message by {message.author}")
                    channel = client.get_channel(int(serverdb[server]["cgcchannel"]))
                    embed.description = message.content
                    if str(message.author.id) == cgcdb["owner"]:
                        embed.set_footer(text=f"{message.author} - Owner - {message.channel.guild.name}")
                    elif str(message.author.id) in cgcdb["staff"]:
                        embed.set_footer(text=f"{message.author} - Staff - {message.channel.guild.name}")
                    else:
                        embed.set_footer(text=f"{message.author} - {message.channel.guild.name}")                        
                    if message.reference:
                        reference = await message.channel.fetch_message(message.reference.message_id)
                        if reference.embeds:
                            embed.add_field(name=f"Original message by {reference.embeds[0].title.split(' ')[-1]}", value=reference.embeds[0].description)
                        else:
                            embed.add_field(name=f"Original message by {reference.author}", value=reference.content)
                    if message.attachments:
                        if message.attachments[-1].filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4')):
                            await message.attachments[-1].save(message.attachments[-1].filename)
                        if message.attachments[-1].filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            attachment = nextcord.File(message.attachments[-1].filename, filename="image.gif")
                            embed.set_image(url="attachment://image.gif")
                            await channel.send(embed=embed, file=attachment)
                        else:
                            attachment = nextcord.File(message.attachments[-1].filename, filename="image.mp4")
                            await channel.send(embed=embed, file=attachment)
                        os.remove(message.attachments[-1].filename)
                    else:
                        await channel.send(embed=embed)
                except Exception as excp:
                    print(excp)
                    pass
            try:
                await message.delete()
            except:
                pass
@client.slash_command(name="ping", description="Replies with pong!")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"Pong 🏓 {client.latency * 1000:.2f}ms")

@client.slash_command(name="sadstory", description="Sends a random (fake) sad story generated by AI.")
async def sadstory(interaction: nextcord.Interaction):
    message = random.choice(sad_stories)
    await interaction.response.send_message(message)

@client.slash_command(name="mute", description="Mutes a user")
async def mute(ctx: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason provided"):
    if ctx.user.guild_permissions.manage_roles:
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role is None:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        if mute_role in member.roles:
            await ctx.send(f"{member.mention} is already muted!")
        else:
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f"Muted {member.mention} for {reason}")
    else:
        await ctx.send("You do not have permission to mute members.")

@client.slash_command(name="unmute", description="Unmutes a user")
async def unmute(ctx: nextcord.Interaction, member: nextcord.Member):
    if ctx.user.guild_permissions.manage_roles:
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.response.send_message(f"Unmuted {member.mention}")
        else:
            await ctx.response.send_message("Member not muted.")
    else:
        await ctx.response.send_message("You do not have permission to unmute members.")

@client.slash_command(name="ban", description="Bans a user")
async def ban(ctx: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason provided"):
    if ctx.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.response.send_message(f"Banned {member.mention} for {reason}")
    else:
        await ctx.response.send_message("You do not have permission to ban members.")

@client.slash_command(name="unban", description="Unbans a user")
async def unban(ctx: nextcord.Interaction, member: nextcord.Member):
    if ctx.user.guild_permissions.ban_members:
        await ctx.guild.unban(member)
        await ctx.response.send_message(f"Unbanned {member.mention}")
    else:
        await ctx.response.send_message("You do not have permission to unban members.")
    
@client.slash_command(name="purge", description="Deletes a number of messages")
async def purge(ctx: nextcord.Interaction, amount: int):
    if ctx.user.guild_permissions.manage_messages:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.response.send_message(f"Deleted {len(deleted) - 1} messages.")
    else:
        await ctx.response.send_message("You do not have permission to manage messages.")

@client.slash_command(name="warn", description="Warns a member")
async def warn(interaction: nextcord.Interaction, member: nextcord.Member, reason: str):
    try:
        if serverdb[str(interaction.guild.id)]:
            try:
                if not serverdb[str(interaction.guild.id)]["warns"]:
                    serverdb[str(interaction.guild.id)]["warns"] = {}
                else:
                    pass
            except:
                serverdb[str(interaction.guild.id)]["warns"] = {}
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["warns"] = {}
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["warns"] = {}
    try:
        if not serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
            serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        else:
            pass
    except:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
    serverdb[str(interaction.guild.id)]["warns"][str(member.id)].append(reason)
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)
    await interaction.send(f"Warned {member.mention} for {reason}")

@client.slash_command(name="warns", description="Checks all warns given to a member")
async def warns(interaction: nextcord.Interaction, member: nextcord.Member):
    try:
        if serverdb[str(interaction.guild.id)]:
            try:
                if not serverdb[str(interaction.guild.id)]["warns"]:
                    serverdb[str(interaction.guild.id)]["warns"] = {}
                else:
                    pass
            except:
                serverdb[str(interaction.guild.id)]["warns"] = {}
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["warns"] = {}
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["warns"] = {}
    try:
        if not serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
            serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        else:
            pass
    except:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
    embed = nextcord.Embed(color=nextcord.Colour.red(), title=f"{member}'s warnings ({len(serverdb[str(interaction.guild.id)]['warns'][str(member.id)])})", description=", ".join(serverdb[str(interaction.guild.id)]['warns'][str(member.id)]))
    await interaction.send(embed=embed)
@client.slash_command(name="askai", description="Ask GPT-4o a question (uses steeldev's API)")
async def askai(interaction: nextcord.Interaction, prompt: str):
    await interaction.response.defer()
    response = await getairesponse(prompt)
    if response.split("-")[0] == "err":
        splitresponse = response.split("-")
        embed = nextcord.Embed(color=nextcord.Color.red(), title="An error occurred")
        embed.add_field(name=f"Response code:{splitresponse[1]}")
        embed.add_field(name=f"Response: {splitresponse[2]}")
        embed.set_footer(text="DM either \"winbo_the_dev\" or \"tolino0\" about this.")
        await interaction.send(embed=embed)
    elif response == "noresponse":
        embed = nextcord.Embed(color=nextcord.Color.red(), title="An error occurred", description="No response by the API.")
        embed.set_footer(text="DM either \"winbo_the_dev\" or \"tolino0\" about this.")
        await interaction.send(embed=embed)
    else:
        await interaction.send(f"GPT-4o's response: {response}")

@client.slash_command(name="unwarn", description="Removes a warn from a member")
async def unwarn(interaction: nextcord.Interaction, member: nextcord.Member, warningreason: str):
    try:
        if serverdb[str(interaction.guild.id)]:
            try:
                if not serverdb[str(interaction.guild.id)]["warns"]:
                    serverdb[str(interaction.guild.id)]["warns"] = {}
                else:
                    pass
            except:
                serverdb[str(interaction.guild.id)]["warns"] = {}
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["warns"] = {}
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["warns"] = {}
    try:
        if not serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
            serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        else:
            pass
    except:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
    if warningreason in serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)].remove(warningreason)
        with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
            json.dump(serverdb, sdbfile, indent=2)
        embed = nextcord.Embed(color=nextcord.Colour.green(), title=f"Removed a warning from {member}", description=f"Removed the warning '{warningreason}' from '{member}'.")
        await interaction.send(embed=embed)
    else:
        embed = nextcord.Embed(color=nextcord.Colour.red(), title="Couldn't find such a warning", description=f"Couldn't find '{warningreason}' in {member}'s warnings.")
        await interaction.send(embed=embed)

@client.slash_command(name="clearwarns", description="Clears all warns given to a member")
async def clearwarns(interaction: nextcord.Interaction, member: nextcord.Member):
    try:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        await interaction.send(f"Cleant all warnings for {member.mention}")
    except:
        await interaction.send(f"{member.mention} has no warnings")
@client.slash_command()
async def cgc(interaction: nextcord.Interaction):
    pass

@cgc.subcommand(description="Set the current channel for Cross-Guild chatting.")
async def set(interaction: nextcord.Interaction):
    try:
        if serverdb[str(interaction.guild.id)]:
            serverdb[str(interaction.guild.id)]["cgcchannel"] = str(interaction.channel.id)
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["cgcchannel"] = str(interaction.channel.id)
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["cgcchannel"] = str(interaction.channel.id)
    serverdb[str(interaction.guild.id)]["cgcchannel"] = str(interaction.channel.id)
    await interaction.send("Set channel for CGC-chatting successfully!")
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)

@cgc.subcommand(description="Unset the current channel for Cross-Guild chatting.")
async def unset(interaction: nextcord.Interaction):
    try:
        serverdb[str(interaction.guild.id)]["cgcchannel"] = "None"
    except:
        pass
    await interaction.send("Unset channel for CGC-chatting successfully!")
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)

@cgc.subcommand(description="Ban a user from Cross-Guild chatting using this bot")
async def ban(interaction: nextcord.Interaction, member: nextcord.Member):
    if str(interaction.user.id) in cgcdb["staff"] or str(interaction.user.id) == cgcdb["owner"]:
        try:
            if cgcdb:
                try:
                    if not cgcdb["bans"]:
                        cgcdb["bans"] = []
                    else:
                        pass
                except:
                    cgcdb["bans"] = []
        except:
            pass
        cgcdb["bans"].append(str(member.id))
        with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
            json.dump(cgcdb, cgcdbfile, indent=2)
        await interaction.send(f"Banned {member}")
@cgc.subcommand(description="Unban a user from Cross-Guild chatting using this bot")
async def unban(interaction: nextcord.Interaction, member: nextcord.Member):
    if str(interaction.user.id) in cgcdb["staff"] or str(interaction.user.id) == cgcdb["owner"]:
        try:
            cgcdb["bans"].remove(str(member.id))
            with open("cgcdb.json", "w", encoding="utf-8") as cgcdbfile:
                json.dump(cgcdb, cgcdbfile, indent=2)
            await interaction.send(f"Unbanned {member}.")
        except:
            await interaction.send(f"{member} is not banned.")

client.run("TOKEN_GOES_HERE")
