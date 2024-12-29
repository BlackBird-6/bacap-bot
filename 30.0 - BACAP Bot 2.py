## THE MAIN FILE FOR THE UHHHH BOT
import random
import re

# import
import discord
from discord import app_commands
from discord.ext import commands
import logging

import gspread

# log
logging.basicConfig(level=logging.INFO)

## BOT STUFF

# start bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"HELLO I AM WORKING MY NAME IS {bot.user}")

    # sync commands
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.\n")
    except Exception as e:
        print("Uh oh! An error occured while syncing application commands:", e)

    # receive sheet info to let bot actually use the api
    # stores into dict
    trophy_sheet_key = "1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI"
    access_trophy_sheet(trophy_sheet_key)

    sheet_key = "1zlRBAkHZhoMlGBbLIvKGxY4wufVVpAhYko48QH6LDNs"
    access_sheet(sheet_key)

@bot.command(name="realisticcave")
async def real(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/1317346365906620459/1319402424070311966/1cavinator.png?")

desc = "Provided below is a link to the official BACAP documentation!\nhttps://docs.google.com/spreadsheets/d/1PcoZGbYr5FWX28_sSEMh9-W_5_qyGbyvptb_9_4te1w/edit"

# Event listener for messages
@bot.event
async def on_message(message):

    # Avoid responding to bot's own messages
    if message.author == bot.user:
        return

    # if message.content == "a":
    #     user = await bot.fetch_user(407695710058971138)
    #     await user.send("I am inside your walls")
    #     await message.channel.send("Nice!")

    # 65
    if " 65 " in message.content or message.content.endswith(" 65") or message.content.startswith("65 "):
        await message.channel.send("https://cdn.discordapp.com/attachments/632404721537253376/632628242045730819/unknown.png")

    # 1 in 10 Nice!
    if message.content == "Nice!" and random.randint(1, 10) == 5:
        await message.channel.send("Nice!")

    # 1 in 1,000 to contribute to #cave-cult
    if message.content == "Cave" and random.randint(1, 1000) == 69:
        await message.channel.send("Cave")

    # 1 in 10,000 BACAP3
    if random.randint(1, 10000) == 69:
        await message.channel.send("Be sure to play BACAP3!")

    # Ensure other commands still work
    await bot.process_commands(message)

# DOCUMENTATION STUFF
sorted_doc_names = {
    "BACAP 1.18": "https://docs.google.com/spreadsheets/d/1zlRBAkHZhoMlGBbLIvKGxY4wufVVpAhYko48QH6LDNs/edit?gid=1233183210#gid=1233183210",
    "Advancement Info Legacy": "https://modrinth.com/mod/advancementinfo",
    "Advancement Info Reloaded": "https://modrinth.com/mod/advancements-reloaded",
    "Advancement Legend Rules": "https://docs.google.com/document/d/1WZsGkN7D9piecNOFLRUNL-5GbAX_0Wgb5rxk6Lo1ess/edit?usp=sharing",
    "BACAP Version History": "https://docs.google.com/document/d/1eVlWRDDyhuXMbPpXFNJkk-gYF6NtALNbrI97ARe3-5w/edit?usp=sharing",
    "BACAP Trophy List": "https://docs.google.com/spreadsheets/d/1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI/edit?usp=sharing",
    "Patreon Upcoming Features List" : "https://tinyurl.com/y92mxs6r"
}

############################ DOCUMENTATION ##############################

async def doc_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in sorted_doc_names:
        if len(results) == 25:
            break
        doc_name = result
        if doc_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=doc_name, value=doc_name))

    for result in sorted_doc_names:
        if len(results) == 25:
            break
        doc_name = result
        choice = app_commands.Choice(name=doc_name, value=doc_name)

        if choice not in results:
            if current.lower() in doc_name.lower():
                results.append(choice)
    return results

async def show_documentation(interaction: discord.Interaction, doc_search: str):
    ephemeral = False
    try:
        embed = discord.Embed(
            title=f"Documentation",
            description=f"The {doc_search} documentation may be found here:\n{sorted_doc_names[doc_search]}"
        )
    except:
        ephemeral = True
        embed = discord.Embed(
            title="Documentation",
            description=f"Perhaps the archives are incomplete. There is no such option named {doc_search}. Please try again with a valid option.",
            color=0xff0000
        )
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@bot.tree.command(name="doc", description="Links you to any official BACAP documentation")
@app_commands.autocomplete(doc_search=doc_autocomplete)
async def doc(interaction: discord.Interaction, doc_search: str):
    await show_documentation(interaction, doc_search)

@bot.tree.command(name="documentation", description="Links you to any official BACAP documentation")
@app_commands.autocomplete(doc_search=doc_autocomplete)
async def documentation(interaction: discord.Interaction, doc_search: str):
    await show_documentation(interaction, doc_search)


################### ACTUAL BACAP BOT STUFF #######################

def find_children():

    # Cycle through every advancement (child)
    for i, advancement in enumerate(advs):

        child_name = advancement["Advancement Name"]
        try:

            parent_name = advancement["Parent"]

            if parent_name == "":
                continue

            # Find the ID of the parent and assign it the child's name
            parent_id = adv_index[parent_name.upper()]

            if advs[parent_id]["Children"] != "":
                advs[parent_id]["Children"] = advs[parent_id]["Children"] + " and " + child_name
            else:
                advs[parent_id]["Children"] = child_name

        except Exception as e:
            print(f"WARNING: Advancement {parent_name} NOT FOUND!")
            print(e)

    # for a in advs:
    #     children = a["Children"]
    #     if "and" in children:
    #         print(a["Advancement Name"], children.count("and") + 1, children)

# open sheet if possible
def access_sheet(sheet_key):
    global advs
    global adv_index
    global sorted_adv_names
    advs = []
    adv_index = {}
    sorted_adv_names = []

    # Open sheet and extract all advancements
    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(sheet_key)
        print(f"THIS MESSAGE IS TO INDICATE {sheet} WAS OPENED SUCCESSFULLY")

        for worksheet in sheet.worksheets():
            if worksheet.title == "Introduction" or worksheet.title == "Terralith":
                continue
            records = worksheet.get_all_records(head=1)
            print(f"Fetched {len(records)} records from sheet: {worksheet.title}")

            for row in records:
                if any(row.values()) == False:
                    break
                row["adv_tab"] = worksheet.title
                advs.append(row)
            print(f"Fetched {len(advs)} advancements from {sheet.title}")

        for i, adv in enumerate(advs):
            name = adv["Advancement Name"]

            if name == "" or name == "(description)":
                continue

            # Set to empty string
            adv['Children'] = ""

            adv_index[name.upper()] = i
            sorted_adv_names.append(name)

        find_children()

    except Exception as e:
        print(f"\nWHILE LOADING SPREADSHEET {sheet}, AN ERROR OCCURED :sadcave:\n{e}")

# open trophy sheet if possible

def access_trophy_sheet(trophy_sheet_key):
    global trophy_data
    global trophy_index
    trophy_data = []
    trophy_index = {}

    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(trophy_sheet_key)
        print(f"THIS MESSAGE IS TO INDICATE {sheet} WAS OPENED SUCCESSFULLY")

        for worksheet in sheet.worksheets():
            records = worksheet.get_all_records(head=1)
            print(f"Fetched {len(records)} records from sheet: {worksheet.title}")

            # Truncate tab (not necessary)
            for trophy in records:
                trophy.pop('Tab')

            for row in records:
                if row['Trophy Name'] != '':
                    trophy_data.append(row)

            for idx, trophy in enumerate(trophy_data):
                trophy_index[trophy['Advancement']] = idx

        print(f"Fetched {len(trophy_data)} sections of trophies from the sheet.")
        # print(f"Trophy Data: {trophy_data}")
        print(f"Trophy Indexes: {trophy_index}")
    except Exception as e:
        print(f"\nWHILE LOADING SPREADSHEET {sheet}, AN ERROR OCCURED :sadcave:\n{e}")

## REFRESH ADVANCEMENT SHEET


@bot.tree.command(name="refresh_advancements", description="Refreshes and reloads all advancements into bot.")
async def refresh(interaction: discord.Interaction):
    # Check if the user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("**You do not have permission to run this command.**")
        return

    try:
        # Defer the response to let the bot know it's working on something
        await interaction.response.defer(thinking=True)

        # Reload the advancements from the sheet
        sheet_key = "1zlRBAkHZhoMlGBbLIvKGxY4wufVVpAhYko48QH6LDNs"
        access_sheet(sheet_key)

        # Send a follow-up message after processing
        await interaction.followup.send("*All advancements have been reloaded successfully.*")

    except Exception as e:
        # Send an error message if something went wrong
        await interaction.followup.send(f"*Uh oh! An error occurred while reloading all advancements.*\nError: **{e}**")


## REFRESH TROPHY SHEET
@bot.tree.command(name="refresh_trophies", description="Refreshes and reloads all trophies into bot.")
async def refresh(interaction: discord.Interaction):
    # Check if the user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("**You do not have permission to run this command.**")
        return

    try:
        # Defer the response to let the bot know it's working on something
        await interaction.response.defer(thinking=True)

        # Reload the advancements from the sheet
        trophy_sheet_key = "1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI"
        access_trophy_sheet(trophy_sheet_key)

        # Send a follow-up message after processing
        await interaction.followup.send("*All trophies have been reloaded successfully.*")

    except Exception as e:
        # Send an error message if something went wrong
        await interaction.followup.send(f"*Uh oh! An error occurred while reloading all trophies.*\nError: **{e}**")


# # menacing bot status loop
# bot_statuses = cycle([":realisiticcave:", "You're a clown!", "Use /advancement", "saladbowls is a loser"])
#
# @tasks.loop(seconds=600)
# async def status_loop():
#     await bot.change_presence(activity=discord.Game(next(bot_statuses)))
#
#
# @bot.event
# async def on_ready():
#     print(f"HELLO I AM WORKING MY NAME IS {bot.user}")
#     status_loop.start()

# ADVANCEMENT AUTOCOMPLETE
async def autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in sorted_adv_names:
        if len(results) == 25:
            break
        adv_name = result
        if adv_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=adv_name, value=adv_name))

    for result in sorted_adv_names:
        if len(results) == 25:
            break
        adv_name = result
        choice = app_commands.Choice(name=adv_name, value=adv_name)

        if choice not in results:
            if current.lower() in adv_name.lower():
                results.append(choice)
    return results

async def embed_advancement(interaction: discord.Interaction, advancement: str):
    # advancements[i]:
    # "Advancement Name"
    # "Description"
    # "Parent"
    # "Actual Requirements (if different)"
    # "Hidden?"
    # "Item rewards"
    # "XP Rewards"
    # "Trophy"
    # "Source"
    # "Version added"
    # "Notes"
    # "adv_tab"

    embed_colors = {
        "B&C Advancements": 0xccac66,
        "Farming": 0xccac66,
        "Mining": 0xb7b7b7,
        "Building": 0xf9cb9c,
        "Animals": 0xb6d7a8,
        "Monsters": 0x93af90,
        "Weaponry": 0x999999,
        "Redstone": 0x999999,
        "Biomes": 0xf3f3f3,
        "Adventure": 0xfff2cc,
        "Enchanting": 0x000000,
        "Statistics": 0xe69138,
        "Nether": 0xe06666,
        "Potions": 0xffd966,
        "End": 0xfff2cc,
        "Super Challenges": 0x666666
    }
    try:
        color = embed_colors[advancement["adv_tab"]]
    except Exception as e:
        color = 0xffffff

    # Note that this also appears below and must be changed twice
    embed = discord.Embed(
        title="Advancement Found!",
        description=f"# {advancement['Advancement Name']}{' <HIDDEN>' if advancement['Hidden?'] == 'TRUE' else ''}\n"
                    f"*__{advancement['Description']}__*\n\n"
                    f"**Parent**: {advancement['Parent']}\n"
                    f"**Children**: {advancement['Children']}\n"
                    f"\n*Part of the __{advancement['adv_tab']}__ tab.*",
        color=color

    )

    # Images?
    # image_url = "https://static.planetminecraft.com/files/resource_media/screenshot/17877618-thumbnail.png"  # Replace with your actual image URL
    # embed.set_image(url=image_url)

    class TrophyButton(discord.ui.Button):
        def __init__(self, label="Display Trophy", style=discord.ButtonStyle.blurple):
            super().__init__(label=label, style=style)

        async def callback(self, interaction: discord.Interaction):
            try:

                # {'Advancement': 'Mining Milestone',
                # 'Item Type': 'Iron Pickaxe',
                # 'CMD': 131,
                # 'Trophy Name': "Miner's Trophy",
                # 'Lore': "Don't mine at night!",
                # 'Version': 1.11, 'Notes': '',
                # 'Credit': 'Fiery_Crystal'}

                trophy = trophy_data[trophy_index[advancement['Advancement Name']]]

                # Format | into line breaks in lore
                lore = re.sub("\s*\|\s*", "\n", trophy['Lore'])

                # Remove formatting from underscores
                credit = trophy['Credit'].replace("_", "\_")

                updated_embed = discord.Embed(
                    title="",
                    description=f"# {trophy['Trophy Name']}\n"
                                f"*{lore}*\n\n"
                                f"({trophy['Item Type']})\n\n"
                                f"**Version**: {trophy['Version']}\n"
                                f"**Credit**: {credit}\n"
                                f"\n*Obtained from __{advancement['Advancement Name']}__.*",
                    color=color
                )
                await interaction.response.edit_message(embed=updated_embed)
            except Exception as e:
                await interaction.response.send_message(content=f"An error occurred: {e}", ephemeral=True)

    class MyView(discord.ui.View):

        def __init__(self, timeout=300):  # Extend timeout to 5 minutes
            super().__init__(timeout=timeout)
            self.more_info = False

            if advancement['Advancement Name'] in trophy_index.keys():
                self.add_item(TrophyButton())

        @discord.ui.button(label="More Information", style=discord.ButtonStyle.green)
        async def update_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                # Create the updated embed
                if self.more_info == False:
                    n = "\n"

                    # If any of these strings are empty, don't display them under "More Information"
                    actual_reqs = str(advancement['Actual Requirements (if different)'])
                    item_rewards = str(advancement['Item rewards'])
                    xp_rewards = str(advancement['XP Rewards'])
                    trophy = str(advancement['Trophy'])
                    notes = str(advancement['Notes'])

                    # Remove formatting from underscores
                    source = advancement['Source'].replace("_", "\_")

                    updated_embed = discord.Embed(
                        title="Advancement Found!",
                        description=f"# {advancement['Advancement Name']}{' <HIDDEN>' if advancement['Hidden?'] == 'TRUE' else ''}\n"
                                    f"*__{advancement['Description']}__*\n\n"
                                    f"**Parent**: {advancement['Parent']}\n"
                                    f"**Children**: {advancement['Children']}\n"
                                    f"{'**Actual Requirements**: ' + actual_reqs + n if actual_reqs != '' else ''}"
                                    f"{'**Item rewards**: ' + item_rewards + n if item_rewards != '' else ''}"
                                    f"{'**XP Rewards**: ' + xp_rewards + n if xp_rewards != '' else ''}"
                                    f"{'**Trophy**: ' + trophy + n if trophy != '' else ''}"
                                    f"**Source**: {source}\n"
                                    f"**Version added**: {advancement['Version added']}\n"
                                    f"{'**Notes**: ' + notes + n if notes != '' else ''}"
                                    f"\n*Part of the __{advancement['adv_tab']}__ tab.*",
                        color=color
                    )
                    button.label = "Less Information"
                    button.style = discord.ButtonStyle.red
                    self.more_info = True
                else:
                    updated_embed = discord.Embed(
                        title="Advancement Found!",
                        description=f"# {advancement['Advancement Name']}{' <HIDDEN>' if advancement['Hidden?'] == 'TRUE' else ''}\n"
                                    f"*__{advancement['Description']}__*\n\n"
                                    f"**Parent**: {advancement['Parent']}\n"
                                    f"**Children**: {advancement['Children']}\n"
                                    f"\n*Part of the __{advancement['adv_tab']}__ tab.*",
                        color=color
                    )
                    button.label = "More Information"
                    button.style = discord.ButtonStyle.green
                    self.more_info = False

                # Edit the original message
                await interaction.response.edit_message(embed=updated_embed, view=self)
            except Exception as e:
                # Handle exceptions properly
                await interaction.response.edit_message(f"An error occurred: {e}", ephemeral=True)

    view = MyView()
    await interaction.response.send_message(embed=embed, view=view)

## GET ADVANCEMENT COMMAND
@bot.tree.command(name="advancement", description="Display an advancement of your choice")
@app_commands.autocomplete(advancement_search=autocomplete)
async def get_advancement(interaction: discord.Interaction, advancement_search: str):

    try:
        index = adv_index[advancement_search.upper()]
        advancement = advs[index]
        await embed_advancement(interaction, advancement)

    except Exception as e:

        embed = discord.Embed(
            title="Advancement Not Found!",
            description=f"*The advancement **{advancement_search}** could not be found. Please try again. {e}*",
            color=0xff0000
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="random", description="Displays a random advancement")
async def random_advancement(interaction: discord.Interaction):
    try:
        random_adv = advs[random.randrange(0, len(advs))]
        await embed_advancement(interaction, random_adv)
    except Exception as e:
        embed = discord.Embed(
            title="Advancement Not Found!",
            description=f"An unexpected error was encountered. Please try again. {e}*",
            color=0xff0000
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

# get token and RUN
with open("Text/token.txt") as file:
    token = file.read()

bot.run(token)