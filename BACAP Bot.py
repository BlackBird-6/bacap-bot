'''
--== BACAP BOT: RELOADED ==--
Coded By: BlackBird_6 and saladbowls
Last Updated: 2025-01-21

A general-purpose discord bot to assist with playing BlazeandCave's Advancement Pack!
Shows advancement names, rewards, requirements, and much much more!

© 2025. "The BACAP Bot" All rights reserved.
'''

import random
import re

# import
import discord
from discord import app_commands
from discord.ext import commands
import logging
from discord import ui
from discord.ui import Button, View

import gspread

# log
logging.basicConfig(level=logging.INFO)

## BOT STUFF

# start bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    logging.info(f"HELLO I AM WORKING MY NAME IS {bot.user}")

    # sync commands
    try:
        synced_commands = await bot.tree.sync()
        logging.info(f"Synced {len(synced_commands)} commands.\n")
    except Exception as e:
        logging.error("Uh oh! An error occured while syncing application commands:", exc_info=e)

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
'''
    # 65
    if " 65 " in message.content or message.content.endswith(" 65") or message.content.startswith("65 "):
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/632404721537253376/632628242045730819/unknown.png")

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
'''

# DOCUMENTATION STUFF
sorted_doc_names = {
    "BACAP 1.18": "https://docs.google.com/spreadsheets/d/1zlRBAkHZhoMlGBbLIvKGxY4wufVVpAhYko48QH6LDNs/edit?gid=1233183210#gid=1233183210",
    "Advancement Info Legacy": "https://modrinth.com/mod/advancementinfo",
    "Advancement Info Reloaded": "https://modrinth.com/mod/advancements-reloaded",
    "Advancement Legend Rules": "https://docs.google.com/document/d/1WZsGkN7D9piecNOFLRUNL-5GbAX_0Wgb5rxk6Lo1ess/edit?usp=sharing",
    "BACAP Version History": "https://docs.google.com/document/d/1eVlWRDDyhuXMbPpXFNJkk-gYF6NtALNbrI97ARe3-5w/edit?usp=sharing",
    "BACAP Trophy List": "https://docs.google.com/spreadsheets/d/1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI/edit?usp=sharing",
    "Patreon Upcoming Features List": "https://tinyurl.com/y92mxs6r"
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
@app_commands.describe(doc_search="Links you to any official BACAP documentation!")
@app_commands.autocomplete(doc_search=doc_autocomplete)
async def doc(interaction: discord.Interaction, doc_search: str):
    await show_documentation(interaction, doc_search)


@bot.tree.command(name="documentation", description="Links you to any official BACAP documentation")
@app_commands.describe(doc_search="Links you to any official BACAP documentation!")
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
            logging.warning(f"Advancement {parent_name} NOT FOUND!", exc_info = e)

    # for a in advs:
    #     children = a["Children"]
    #     if "and" in children:
    #         print(a["Advancement Name"], children.count("and") + 1, children)


# open sheet if possible
def access_sheet(sheet_key):
    global advs
    global adv_index
    global sorted_adv_names
    global additional_adv_info
    advs = []
    adv_index = {}
    sorted_adv_names = []
    additional_adv_info = {}

    # Open sheet and extract all advancements
    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(sheet_key)
        logging.info(f"Sheet {sheet} was opened successfully")

        for worksheet in sheet.worksheets():
            if worksheet.title == "Introduction" or worksheet.title == "Terralith":
                continue
            records = worksheet.get_all_records(head=1)
            logging.info(f"Fetched {len(records)} records from sheet: {worksheet.title}")

            grab_more_info = False

            # Iterate through advancements
            for row in records:

                # In "Additional Info Mode" append any new descriptions as "Additional Info" to the respective adv
                if grab_more_info == True:

                    if row['Advancement Name'] == "Full requirement notes:" or row['Advancement Name'] == "":
                        continue

                    if row['Advancement Name'] == "Riddle Me This":
                        additional_adv_info[row['Advancement Name']] = "Run /riddlemethis for more information."
                        continue

                    adv_note_names = row['Advancement Name'].split("\n")
                    for name in adv_note_names:
                        additional_adv_info[name] = row['Description'].replace("\n", "")

                    continue

                # After the bulk advancements are done, set info gathering mode to "Additional Info"
                if any(row.values()) == False:
                    grab_more_info = True
                    continue

                row["adv_tab"] = worksheet.title
                advs.append(row)
            logging.info(f"Fetched {len(advs)} advancements from {sheet.title}")

        for i, adv in enumerate(advs):
            name = adv["Advancement Name"]

            if name == "" or name == "(description)":
                continue

            # Set to empty string
            adv['Children'] = ""

            adv_index[name.upper()] = i
            sorted_adv_names.append(name)

        find_children()
        # print(additional_adv_info)

    except Exception as e:
        logging.error(f"An error occured while loading sheet {sheet} :sadcave:", exc_info = e)


# open trophy sheet if possible

def access_trophy_sheet(trophy_sheet_key):
    global trophy_data
    global trophy_index
    trophy_data = []
    trophy_index = {}

    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(trophy_sheet_key)
        logging.info(f"Sheet {sheet} was opened successfully")

        for worksheet in sheet.worksheets():
            records = worksheet.get_all_records(head=1)
            logging.info(f"Fetched {len(records)} records from sheet: {worksheet.title}")

            # Truncate tab (not necessary)
            for trophy in records:
                trophy.pop('Tab')

            for row in records:
                if row['Trophy Name'] != '':
                    trophy_data.append(row)

            for idx, trophy in enumerate(trophy_data):
                trophy_index[trophy['Advancement']] = idx

        logging.info(f"Fetched {len(trophy_data)} sections of trophies from the sheet.")
        # print(f"Trophy Indexes: {trophy_index}")
    except Exception as e:
        logging.error(f"An error occured while loading sheet {sheet} :sadcave:", exc_info = e)


## REFRESH ADVANCEMENT SHEET
@bot.tree.command(name="refresh_advancements", description="Refreshes and reloads all advancements into bot.")
async def refresh(interaction: discord.Interaction):
    # Check if the user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("**You do not have permission to run this command.**", ephemeral=True)
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

    # Declare advancement embed colours
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
            self.show_more_info = False

            if advancement['Advancement Name'] in trophy_index.keys():
                self.add_item(TrophyButton())

        @discord.ui.button(label="More Information", style=discord.ButtonStyle.green)
        async def update_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
            global additional_adv_info
            try:
                # Create the updated embed
                if self.show_more_info == False:
                    n = "\n"

                    # If any of these strings are empty, don't display them under "More Information"
                    actual_reqs = str(advancement['Actual Requirements (if different)'])
                    item_rewards = str(advancement['Item rewards'])
                    xp_rewards = str(advancement['XP Rewards'])
                    trophy = str(advancement['Trophy'])
                    notes = str(advancement['Notes'])

                    # If this advancement has additional information to show, initialize it
                    more_info = ""
                    if advancement['Advancement Name'] in additional_adv_info.keys():
                        more_info = additional_adv_info[advancement['Advancement Name']]

                    # Remove formatting from underscores
                    source = advancement['Source'].replace("_", "\_")

                    # Update embed, hiding any elements which are empty
                    updated_embed = discord.Embed(
                        title="Advancement Found!",
                        description=f"# {advancement['Advancement Name']}{' <HIDDEN>' if advancement['Hidden?'] == 'TRUE' else ''}\n"
                                    f"*__{advancement['Description']}__*\n\n"
                                    f"**Parent**: {advancement['Parent']}\n"
                                    f"**Children**: {advancement['Children']}\n"
                                    f"{'**Actual Requirements**: ' + actual_reqs + n if actual_reqs != '' else ''}"
                                    f"{'**Additional Information**: ' + more_info + n if more_info != '' else ''}"
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
                    self.show_more_info = True
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
                    self.show_more_info = False

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
@app_commands.describe(advancement_search="Display an advancement of your choice!")
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


## TAB COMMAND AUTOCOMPLETE
async def tab_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []

    tabs = {adv["adv_tab"] for adv in advs}
    for tab_name in tabs:
        if len(results) == 25:
            break
        if tab_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=tab_name, value=tab_name))

    for tab_name in tabs:
        if len(results) == 25:
            break
        choice = app_commands.Choice(name=tab_name, value=tab_name)

        if choice not in results:
            if current.lower() in tab_name.lower():
                results.append(choice)
    return results


## TAB COMMAND
@bot.tree.command(name="tab", description="Lists all advancements from an advancement tab")
@app_commands.autocomplete(tab=tab_autocomplete)
@app_commands.describe(tab="The name of the tab you would like to list")
async def tab(interaction: discord.Interaction, tab: str):
    tab = tab.strip()

    # make bot think so it doesnt time out
    await interaction.response.defer(thinking=True)
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
        color = embed_colors[tab]
    except KeyError:
        color = 0xff0000
        logging.warn("Exception when picking color for a tab", exc_info = e)

    # filter out advs by whatever tab they just put in
    filtered_advs = [adv for adv in advs if adv["adv_tab"].lower() == tab.lower()]
    if not filtered_advs:
        embed = discord.Embed(
            title="Error!",
            description=f"The tab {tab} was not found. Please check the tab name and try again.",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    adv_pages = []
    for x in range(0, len(filtered_advs), 7):
        adv_pages.append(filtered_advs[x:x + 7])

    embed = discord.Embed(
        title=f"The {tab} Tab Advancements",
        color=color
    )

    # advancements will be split into pages every 7 advs
    class PageView(View):
        def __init__(self, pages, color):
            super().__init__(timeout=300)  # 5-minute timeout
            self.pages = pages
            self.page = 0
            self.color = color
            self.interaction_user = None

            self.update_button_visibility()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.interaction_user:
                await interaction.response.send_message("You are not allowed to interact with these buttons. L!",
                                                        ephemeral=True)
                return False
            return True

        async def send_page(self, interaction):
            embed = discord.Embed(
                title=f"The {tab} Tab Advancements *(Page {self.page + 1}/{len(self.pages)})*",
                color=self.color,
            )
            for adv in self.pages[self.page]:
                embed.add_field(
                    name=f"**{adv['Advancement Name']}**",
                    value=f"**Description**: {adv['Description']}",
                    inline=False,
                )
            self.update_button_visibility()
            await interaction.response.edit_message(embed=embed, view=self)

        def update_button_visibility(self):
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    if child.label == "⬅️ Previous Page":
                        child.disabled = self.page == 0
                    elif child.label == "Next Page ➡️":
                        child.disabled = self.page == len(self.pages) - 1

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            embed = discord.Embed(
                title="**Pages Timed Out**",
                description="This session has *timed out* due to inactivity. If you need to view the advancements again, please re-run the **/tab** command!",
                color=0xff0000,
            )
            await self.message.edit(embed=embed, view=None)

        @discord.ui.button(label="⬅️ Previous Page", style=discord.ButtonStyle.blurple)
        async def previous_page(self, interaction: discord.Interaction, button: Button):
            if self.page > 0:
                self.page -= 1
                await self.send_page(interaction)

        @discord.ui.button(label="Next Page ➡️", style=discord.ButtonStyle.blurple)
        async def next_page(self, interaction: discord.Interaction, button: Button):
            if self.page < len(self.pages) - 1:
                self.page += 1
                await self.send_page(interaction)

        @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.red)
        async def close(self, interaction: discord.Interaction, button: Button):
            embed = discord.Embed(
                title="**Tab List Closed**",
                description="*To see another tab list, use the `/tab` command!*",
                color=0xff0000,
            )
            await interaction.response.edit_message(embed=embed, view=None)

    view = PageView(adv_pages, color)
    view.interaction_user = interaction.user

    embed = discord.Embed(
        title=f"The {tab} Tab Advancements *(Page 1/{len(adv_pages)})*",
        color=color,
    )
    for adv in adv_pages[0]:
        embed.add_field(
            name=f"**{adv['Advancement Name']}**",
            value=f"{adv['Description']}",
            inline=False,
        )

    view.message = await interaction.followup.send(embed=embed, view=view)


## HELP COMMAND RELATED STUFF

# sorted help dict
sorted_help_commands = {
    "advancement": "Displays an advancement of your choice. Use the `/advancement` command and type what advancement you want to find in the search field.",
    "doc & documentation": "Both commands will link you to any official BACAP documentation of your choice. Use the `/doc` or `/documentation` command and type what documentation you want to find in the search field.",
    "help": "Displays information about all available commands. Use the `/help` command and type what command you need help with in the search field.",
    "random": "Displays a random advancement. Use the `/random` command.",
    "refresh_advancements": "Refreshes and reloads advancement spreadsheet data from Sheets API. You cannot run this command unless you are an **administrator**.",
    "refresh_trophies": "Refreshes and reloads trophy spreadsheet data from Sheets API. You cannot run this command unless you are an **administrator**.",
    "riddlemethis": "Displays steps on how to complete the \"Riddle Me This\" super challenge. Use `/riddlemethis` and type which step you want displayed in the search field.",
    "tab": "Lists all advancements from a tab of your choice. Use the `/tab` command and type what tab you want to list in the search field.",
    "update_world": "Displays information on how to upgrade BACAP to a newer version. Use the `/update_world` command.",
    "versions": "Displays an available BACAP version of your choice. Use the `/versions` command and type what version you want displayed in the search field."
}


# HELP AUTOCOMPLETE
async def help_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in sorted_help_commands:
        if len(results) == 25:
            break
        help_name = result
        if help_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=help_name, value=help_name))

    for result in sorted_help_commands:
        if len(results) == 25:
            break
        help_name = result
        choice = app_commands.Choice(name=help_name, value=help_name)

        if choice not in results:
            if current.lower() in help_name.lower():
                results.append(choice)
    return results


## HELP COMMAND
@bot.tree.command(name="help", description="Displays information about all available commands in this bot.")
@app_commands.autocomplete(help=help_autocomplete)
@app_commands.describe(help="The name of the command you would like information about.")
async def help_command(interaction: discord.Interaction, help: str):
    ephemeral = False
    try:
        embed = discord.Embed(
            title=f"The {help} Command",
            description=f"{sorted_help_commands[help]}",
            color=discord.Color.blurple()
        )
    except:
        ephemeral = True
        embed = discord.Embed(
            title="Help",
            description=f"Perhaps the archives are incomplete. There is no such option named {help}. Please try again with a valid option.",
            color=0xff0000
        )
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


## VERSIONS COMMAND RELATED STUFF

# version dict
version_dict = {
    "BACAP 1.3.1 (for MC 1.12.2)": "http://www.mediafire.com/file/3ipu8sc18xaesi5/BlazeandCave%2527s_Advancements_Pack_1.3.1.zip/file",
    "BACAP 1.5.1 (for MC 1.13.2)": "http://www.mediafire.com/file/w644tcbsy4mw5f4/BlazeandCave%2527s_Advancements_Pack_1.5.1.zip/file",
    "BACAP 1.7.4 (for MC 1.14.4)": "http://www.mediafire.com/file/sfn3dzng8x86flr/BlazeandCave%2527s_Advancements_Pack_1.7.4.zip/file",
    "BACAP 1.9.4 (for MC 1.15.2)": "http://www.mediafire.com/file/m8wh44ucm3bg8pk/BlazeandCave%2527s_Advancements_Pack_1.9.4.zip/file",
    "BACAP 1.10.1 (for MC 1.16 or 1.16.1)": "http://www.mediafire.com/file/3ebqu0fv0sy9e7z/BlazeandCave%2527s_Advancements_Pack_1.10.1.zip/file",
    "BACAP 1.11.5 (for MC 1.16.2-1.16.5)": "https://www.mediafire.com/file/t4ayv8ku84mhbph/BlazeandCave%2527s_Advancements_Pack_1.11.5.zip/file",
    "BACAP 1.12.4 (for MC 1.17 or 1.17.1)": "https://www.mediafire.com/file/qi54buovl5p8xm2/BlazeandCave%2527s_Advancements_Pack_1.12.4.zip/file",
    "BACAP 1.13.3 (for MC 1.18 or 1.18.1)": "https://www.mediafire.com/file/vqzsy0orugf6cvz/BlazeandCave%2527s_Advancements_Pack_1.13.3.zip/file",
    "BACAP 1.13.8 (for MC 1.18.2)": "https://www.mediafire.com/file/6naymjgo70suqp2/BlazeandCave%2527s_Advancements_Pack_1.13.8.zip/file",
    "BACAP 1.14.6 (for MC 1.19)": "https://www.mediafire.com/file/ja8ise0pzt5bmyz/BlazeandCave%2527s_Advancements_Pack_1.14.6.zip/file",
    "BACAP 1.15.3 (for MC 1.19.1-1.19.3)": "https://www.mediafire.com/file/naytadalwfhktz5/BlazeandCave%2527s_Advancements_Pack_1.15.3.zip/file",
    "BACAP 1.15.4 (for MC 1.19.4)": "https://www.mediafire.com/file/gxsymkhhx1h68sg/BlazeandCave%2527s_Advancements_Pack_1.15.4.zip/file",
    "BACAP 1.16.2 (for MC 1.20 or 1.20.1)": "https://www.mediafire.com/file/6mj2x3v6jtikdet/BlazeandCave%2527s_Advancements_Pack_1.16.2.zip/file",
    "BACAP 1.16.3 (for MC 1.20.2)": "https://www.mediafire.com/file/8d9g7ssqw41ccm3/BlazeandCave%2527s_Advancements_Pack_1.16.3.zip/file",
    "BACAP 1.16.7 (for MC 1.20.3 or 1.20.4)": "https://www.mediafire.com/file/xeauvwmf7excv19/BlazeandCave%2527s_Advancements_Pack_1.16.7.zip/file",
    "BACAP 1.16.9 (for MC 1.20.5 or 1.20.6)": "https://www.mediafire.com/file/n0tg28wcwugzpa0/BlazeandCave%2527s_Advancements_Pack_1.16.9.zip/file",
    "BACAP 1.17.2 (for MC 1.21 or 1.21.1)": "https://www.mediafire.com/file/h7y6czxsrp8b8pd/BlazeandCave%2527s_Advancements_Pack_1.17.2.zip/file",
    "BACAP 1.17.3 (for MC 1.21.2 or 1.21.3)": "https://www.mediafire.com/file/vo83prsi0lziwz4/BlazeandCave%2527s_Advancements_Pack_1.17.3.zip/file",
    "latest": "https://www.mediafire.com/file/uy0ayqql8eo6cot/BlazeandCave%2527s_Advancements_Pack_1.18.1.zip/file"
}


# VERSION AUTOCOMPLETE
async def version_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in version_dict:
        if len(results) == 25:
            break
        version_name = result
        if version_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=version_name, value=version_name))

    for result in version_dict:
        if len(results) == 25:
            break
        version_name = result
        choice = app_commands.Choice(name=version_name, value=version_name)

        if choice not in results:
            if current.lower() in version_name.lower():
                results.append(choice)
    return results


## VERSION COMMAND
@bot.tree.command(name="versions", description="Displays older versions of BACAP and the compatible Minecraft version.")
@app_commands.autocomplete(version=version_autocomplete)
@app_commands.describe(version="The name of the BACAP version you want to display.")
async def help_command(interaction: discord.Interaction, version: str):
    ephemeral = False
    try:
        embed = discord.Embed(
            title=f"**{version}**",
            description=f"*Version {version}'s download can be found here:*\n{version_dict[version]}",
            color=discord.Color.brand_green()
        )
    except:
        ephemeral = True
        embed = discord.Embed(
            title="Help",
            description=f"Perhaps the archives are incomplete. There are no versions matching {version}. Please try again with a valid option.",
            color=0xff0000
        )
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


## UPDATE COMMAND
@bot.tree.command(name="update_world",
                  description="Displays a prompt on how to update your world when a new BACAP version releases.")
async def update_world_command(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="Updating BACAP to a Newer Version",
            description="*1. Make a backup of you world for safety if you screw anything up.*\n"
                        "*2. Leave your world for more safety and don't go in during the process.*\n"
                        "*3. Delete the old datapacks **COMPLETELY** from your world.*\n"
                        "*4. Copy and paste in the new updated datapacks.*\n"
                        "*5. Go into your world.*\n"
                        "*6. If you **screwed up**, go to your backup, make a backup of your backup, then repeat __steps 2-6__ on the backup.*",
            color=discord.Color.dark_blue()
        )
    except Exception as e:
        embed = discord.Embed(
            title="Error!",
            description=f"Uh oh! An error occured while trying to display information! Error: {e}",
            color=0xff0000
        )

    await interaction.response.send_message(embed=embed, ephemeral=False)


## RIDDLE ME THIS DICT
riddle_me_this_batman = {
    "Full Riddle": "The first is to smith a compass that vanishes\n"
              "The second is to slay a corpse that fishes\n"
              "The third is to ride an upside-down mount a lot\n"
              "The fourth is to put a pot in a pot and a pot on a pot\n"
              "The fifth is to be invisible yet be visible everywhere\n"
              "The sixth is to return the product of a fowl in mid-air\n"
              "The seventh is to allow a child to commit the act of stealing\n"
              "The eighth is to smite a Wither with splash healing\n"
              "The ninth is to be a pirate; parrot, spyglass, map, and boat\n"
              "The tenth, if you can achieve it, you will be the G.O.A.T.",
    "Step 1": "||Put Curse of Vanishing on a compass||",
    "Step 2": "||Slay either a Drowned with a fishing rod or a Zombie Villager of fisherman profession||",
    "Step 3": "||Ride a mob named “Dinnerbone” or “Grumm” for 1km without dismounting||",
    "Step 4": "||Place a decorated or flower pot inside a decorated pot, and a decorated or flower pot on top of a decorated pot||",
    "Step 5": "||Have the Invisibility and Glowing effects at the same time||",
    "Step 6": "||Throw an egg at a chicken that is currently in mid-air||",
    "Step 7": "||Give a baby Piglin a gold ingot||",
    "Step 8": "||Kill a Wither with a splash healing potion||",
    "Step 9": "||Use a spyglass while you have a parrot on your shoulder, a map in your other hand, and are riding a boat||",
    "Step 10": "||Place 1000 Warped Buttons (note: It does not start counting until you have completed the ninth line)||",
    "List All Steps": ""
}

## RIDDLE ME THIS AUTOCOMPLETE
async def riddle_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in riddle_me_this_batman:
        if len(results) == 25:
            break
        riddle_name = result
        if riddle_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=riddle_name, value=riddle_name))

    for result in riddle_me_this_batman:
        if len(results) == 25:
            break
        riddle_name = result
        choice = app_commands.Choice(name=riddle_name, value=riddle_name)

        if choice not in results:
            if current.lower() in riddle_name.lower():
                results.append(choice)
    return results


## RIDDLE ME THIS HELP COMMAND
@bot.tree.command(name="riddlemethis",
                  description="Displays the solutions to each step in the \"Riddle Me This\" challenge.")
@app_commands.autocomplete(riddle=riddle_autocomplete)
@app_commands.describe(riddle="Which step you would like to display")
async def riddle_command(interaction: discord.Interaction, riddle: str):
    try:
        if riddle.lower() == "list all steps":
            steps = "\n".join(
                [f"**{key}:** {value}" for key, value in riddle_me_this_batman.items() if key != "List All Steps"])
            embed = discord.Embed(
                title="Riddle Me This: All Steps",
                description=f"{steps}",
                color=discord.Color.dark_gold()
            )
        else:
            try:
                step = riddle_me_this_batman.get(riddle)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"There is no such step as {riddle}. Please try again with a valid option.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed)
            embed = discord.Embed(
                title=f"Riddle Me This: {riddle}",
                description=f"{step}",
                color=discord.Color.gold()
            )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error!",
            description=f"Uh oh! An unknown error has occured! Error: {e}",
            color=0xff0000
        )


# get token and RUN
with open("Text/token.txt") as file:
    token = file.read()

bot.run(token)

# END

# 1000
