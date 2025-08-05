'''
--== BACAP BOT: RELOADED ==--
Coded By: BlackBird_6, saladbowls, and Ktano2o6o8
Last Updated: 2025-08-05
Current Version: v1.3.0

A general-purpose discord bot to assist with playing BlazeandCave's Advancement Pack!
Shows advancement names, rewards, requirements, and much much more!

=== changelog v1.3 ===

v1.3.0
- Added the addon_advancement command, which displays any advancement from any of the BACAP add-ons
   - Currently, the add-ons available are Terralith Version, Nullscape Version, Torture Edition (by Wolfguy2005), Enhanced Discoveries (by ItzSkyReed and _Fedor_F), Incendium Version (by Ktano2o6o8), Complete Collection (by CoolgirlOmega) and Cereal Dedication (by FixingGlobe)
- Added an optional argument "addon" to the /random command that if present, picks a random advancement from that add-on instead
- Updated advancement view to include the advancement ID
- Added overrides for base pack advancement icons with additional components

=== changelog v1.2 ===

v1.2.1
- Fixed a bug related to the "Display Trophy" button still lingering when viewing the actual trophy embed
- Added emojis to advancement embeds and buttons
-- The "More Information" section has been reformatted to be more tidy and clean
- Reworked button timing out logic - buttons now delete themselves when they time out
-- The "Close" button has been removed with this reworked logic
- Added a new thumbnail to /doc and /documentation

- i still cannot believe that it's literally not butter

v1.2.0
- Added capability to read from datapack files
- Updated advancement view to include criteria count
- Updated advancement view to include an image of the adv icon on a frame of that adv's category
- Upgrades, people, upgrades!

=== changelog v1.1 ===

v1.1.5
- Hotfix refresh_advancements command reloading wrong spreadsheet documentation

v1.1.4
- Updated versions command to have new bacap versions
- Updated data to grab from 1.19 documentation
- Updated doc command to use 1.19 documentation

v1.1.3
- Added emojis to display name depending on the category of the advancement

v1.1.2
- Patched in additional adv info again
- Modified trophy button functionality

v1.1.1
- Hotfix for images not loading after being loaded the first time

- Updated versions command to include new version bacap 1.18.2
- Added several thumbnails and pictures for some commands, more will come soon
- Major internal rework of button logic and handling
-- We are currently aware of a bug with the advancement's button logic where it doesn't time out for some reason (FIXED IN v1.2.1)

- Added logging and removed print statements
- Made embeds a bit neater with emojis
- Optimizations here and there

=== changelog v1.0 ===

v1.0r3
- Fixed being able to run any refresh commands if you're an admin on a server with the bot (thank u p1k0chu)

v1.0r2
- Reactive messages disabled due to bot spam/abuse (this is why we can't have nice things)

- i still can't believe it's not butter
=== end of changelog ===


© 2025. "The BACAP Bot" All rights reserved.
'''

# ALL IMPORTS
import random
import re

import discord
from discord import app_commands
from discord.ext import commands
import logging
from discord.ui import Button, View

import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from PIL import Image

import os
import json
import nbtlib
import requests

# image function for preloading images
image_cache = {}
item_cache = {}
adv_image_file = None

# Enable or disable for logging
logging.getLogger().setLevel(logging.INFO)


# Ensure bot is ran from script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# BACAP Bot Reloaded

# Test bot check
test = False
with open("Text/token.txt") as file:
    if(file.read().strip().endswith("P4")):
        test = True
        logging.warning("BACAP Bot initialized in TESTING.")

# Emotes for BACAP Bot Reloaded
emotes = {
    "root": "<:root:1364452913253978175>",
    "task": "<:task:1335313144859328623>",
    "goal": "<:goal:1335313109572648960>",
    "challenge": "<:challenge:1335313097195388979>",
    "super_challenge": "<:super_challenge:1335313134227034163>",
    "milestone": "<:milestone:1335313122268938444>",
    "hidden": "<:hidden:1364451436309516380>",
    "advancement_legend": "<:advancement_legend:1364451408946003978>",
    "realisticcave_advancement_legend": "<:why_hello_there:1399908690378752040>",
    "custom_dark_red": "<:te_dark_red:1399908791713136792>",
    "custom_#8b00e8": "<:te_purple:1399909009405771927>",
    "custom_black": "<:te_black:1399909069472399492>",
    "custom_dark_green": "<:terralithic:1399909122484342815>",
    "": ""  # Add more when necessary
} if not test else { # Emotes for test bot
    "root": "<:root:1399529786283528223>",
    "task": "<:task:1399529800519127052>",
    "goal": "<:goal:1399529815396057088>",
    "challenge": "<:challenge:1399529829472403508>",
    "super_challenge": "<:super_challenge:1399529866948513823>",
    "milestone": "<:milestone:1399529853614686269>",
    "hidden": "<:hidden:1399528697849053344>",
    "advancement_legend": "<:advancement_legend:1399529940151570595>",
    "realisticcave_advancement_legend": "<:why_hello_there:1399529969549574344>",
    "custom_dark_red": "<:te_dark_red:1399529017006227456>",
    "custom_#8b00e8": "<:te_purple:1399528441333940305>",
    "custom_black": "<:te_black:1399528340531970198>",
    "custom_dark_green": "<:terralithic:1399528786864902264>",
    "": "" # Add more when necessary
}

def load_images():
    image_folder = "images/"
    if not os.path.exists(image_folder):
        logging.error(f"WHILE ACCESSING FOLDER {image_folder}, THERE WAS AN ERROR. :sadcave:")
        return
    logging.info(f"THIS MESSAGE INDICATES THAT {image_folder} WAS ACCESSED SUCCESSFULLY")

    for filename in os.listdir(image_folder):
        if filename.lower().endswith(".png"):
            file_path = os.path.join(image_folder, filename)
            image_cache[filename] = file_path
            logging.info(f"Image File Cached: {filename}")

    logging.info(f"ALL IMAGES PRELOADED :cave: {len(image_cache)} images cached.")

# improved button logic handling
def button_logic(user: discord.User, pages, color, tab, advancement=None, paginated=True):
    class PageView(View):
        def __init__ (self):
            super().__init__(timeout=300)
            self.pages = pages
            self.page = 0
            self.color = color
            self.interaction_user = user
            self.show_more_info = False
            self.message = None
            self.paginated = paginated

            if paginated:
                self.previous_page = Button(label="⬅️ Previous Page", style=discord.ButtonStyle.blurple, custom_id="prev_page")
                self.next_page = Button(label="Next Page ➡️", style=discord.ButtonStyle.blurple, custom_id="next_page")
                self.previous_page.callback = self.previous_page_callback
                self.next_page.callback = self.next_page_callback
                self.add_item(self.previous_page)
                self.add_item(self.next_page)

            if not paginated and advancement:
                self.more_info_button = Button(label="ℹ️ More Information", style=discord.ButtonStyle.green, custom_id="more_info_" + str(id(self)))
                self.more_info_button.callback = self.more_info_callback
                self.add_item(self.more_info_button)

            if advancement and advancement['Advancement Name'] in trophy_index.keys():
                self.trophy_button = Button(label="🏆 Display Trophy", style=discord.ButtonStyle.blurple, custom_id="trophy" + str(id(self)))

                self.trophy_button.callback = self.trophy_callback
                self.add_item(self.trophy_button)

                # self.add_item(self.TrophyButton(advancement, color))

            #    def __init__(self, advancement, color):
            #         super().__init__(label="Display Trophy", style=discord.ButtonStyle.blurple)
            #         self.advancement = advancement
            #         self.color = color

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.interaction_user:
                await interaction.response.send_message("❌ This is not your interaction. *Please run your own command!*",ephemeral=True)
                return False
            return True

        async def send_page(self, interaction):
            embed = discord.Embed(
                title=f"The {tab} Tab Advancements *(Page {self.page + 1}/{len(self.pages)})*",
                color=self.color
            )
            for adv in self.pages[self.page]:
                embed.add_field(
                    name=f"**{adv['Advancement Name']}**",
                    value=f"**Description:** {adv['Description']}",
                    inline=False
                )
            self.message = interaction.message
            await interaction.response.edit_message(embed=embed,view=self)

        async def on_timeout(self):
            if self.message:
                for item in self.children:
                    item.disabled = True
                await self.message.edit(view=None)

        async def previous_page_callback(self, interaction: discord.Interaction):
            if self.page > 0:
                self.page -= 1
                await self.send_page(interaction)

        async def next_page_callback(self, interaction: discord.Interaction):
            if self.page < len(self.pages) - 1:
                self.page += 1
                await self.send_page(interaction)


        async def more_info_callback(self, interaction: discord.Interaction):
            try:
                if not self.show_more_info:

                    # If this advancement has additional information to show, initialize it
                    more_info = ""
                    if advancement['Advancement Name'] in additional_adv_info.keys():
                        more_info = additional_adv_info[advancement['Advancement Name']]

                    source_reformatted = advancement.get('Source', '').replace('_', '\\_')
                    extra_info = "\n"
                    extra_info += f"**📃   Actual Requirements**: {advancement.get('Actual Requirements (if different)', '')}\n" if advancement.get('Actual Requirements (if different)') else "\n"
                    extra_info += f"**🔢   Criteria Count**: {advancement.get('Criteria Count', '')}\n" if advancement.get('Criteria Count') else ""
                    extra_info += "\n"
                    extra_info += f"**🏅   Item Rewards**: {advancement.get('Item rewards', '')}\n" if advancement.get('Item rewards') else "**🏅   Item Rewards**: N/A\n"
                    extra_info += f"**✨   XP Rewards**: {advancement.get('XP Rewards', '')}\n" if advancement.get('XP Rewards') else "**✨   XP Rewards**: N/A\n"
                    extra_info += f"**🏆   Trophy**: {advancement.get('Trophy', '')}\n" if advancement.get('Trophy') else ""
                    extra_info += "\n"
                    extra_info += f"**🆔   Advancement ID**: {advancement.get('Advancement Id', '')}\n" if advancement.get('Advancement Id') else ""
                    extra_info += f"**📝   Source**: {source_reformatted}\n" if advancement.get('Source') else ""
                    extra_info += f"**🔧   Version Added**: {advancement.get('Version added', '')}\n" if advancement.get('Version added') else ""
                    extra_info += f"\n**ℹ️   Additional Information**: {more_info}\n" if more_info != '' else ''

                    updated_embed = embed_advancement(advancement, extra_info, color)

                    self.more_info_button.label = "🚫 Less Information"
                    self.more_info_button.style = discord.ButtonStyle.red
                    self.show_more_info = True
                else:
                    updated_embed = embed_advancement(advancement, "", color)
                    self.more_info_button.label = "ℹ️ More Information"
                    self.more_info_button.style = discord.ButtonStyle.green
                    self.show_more_info = False

                    if advancement['Advancement Name'] in trophy_index.keys():
                        if self.trophy_button not in self.children:
                            self.add_item(self.trophy_button)                    

                if adv_image_file.filename:
                    updated_embed.set_thumbnail(url=f"attachment://{adv_image_file.filename}")

                await interaction.response.edit_message(embed=updated_embed, view=self)
            except Exception as e:
                await interaction.response.send_message(content=f"An error occurred: {e}", ephemeral=True)


        async def trophy_callback(self, interaction: discord.Interaction):
            try:
                self.more_info_button.label = "⬅️ Back to Advancement"
                self.more_info_button.style = discord.ButtonStyle.red
                self.show_more_info = True

                trophy = trophy_data[trophy_index[advancement['Advancement Name']]]

                # Format | into line breaks in lore
                lore = re.sub(r"\s*\|\s*", "\n", trophy['Lore'])

                # Remove discord formatting from underscores
                credit = trophy['Credit'].replace("_", "\_")

                updated_embed = discord.Embed(
                    title="",
                    description=f"# {trophy['Trophy Name']}\n"
                                f"*{lore}*\n\n"
                                f"({trophy['Item Type']})\n\n"
                                f"🔢   **Version**: {trophy['Version']}\n"
                                f"📝   **Credit**: {credit}\n"
                                f"\n*Obtained from __{advancement['Advancement Name']}__.*",
                    color=self.color
                )

                if adv_image_file.filename:
                    updated_embed.set_thumbnail(url=f"attachment://{adv_image_file.filename}")
                self.remove_item(self.trophy_button)

                await interaction.response.edit_message(embed=updated_embed, view=self)
            except Exception as e:
                await interaction.response.send_message(content=f"An error occurred: {e}", ephemeral=True)

    return PageView()

logging.basicConfig(level=logging.INFO)

## BOT STUFF

# start bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    logging.info(f"HELLO I AM WORKING MY NAME IS {bot.user}")
    load_images() # image preload

    try:
        synced_commands = await bot.tree.sync() # command sync
        logging.info(f"Synced {len(synced_commands)} commands.\n")
    except Exception as e:
        logging.error("Uh oh! An error occured while syncing application commands:", e)

    # receive sheet info to let bot actually use the api
    # stores into dict
    trophy_sheet_key = "1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI"
    access_trophy_sheet(trophy_sheet_key)

    access_sheet(BACAP_DOC_KEY)

    access_BACAP_datapack()

    access_BACAP_addons()

    build_adv_icons()

    logging.info("BACAP Bot loaded and ready for use!")
    
    


@bot.command(name="realisticcave")
async def real(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/1317346365906620459/1319402424070311966/1cavinator.png?")


desc = "Provided below is a link to the official BACAP documentation!\nhttps://docs.google.com/spreadsheets/d/1PcoZGbYr5FWX28_sSEMh9-W_5_qyGbyvptb_9_4te1w/edit"


# Event listener for messages
'''
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
############################ DOCUMENTATION ##############################

BACAP_DOC_KEY = '14-69HHvKP54OsHQZm1zoWSZ36bMPHp6hQSgfp2Xu1nY'
sorted_doc_names = {
    "BACAP 1.19": f"https://docs.google.com/spreadsheets/d/{BACAP_DOC_KEY}/edit?usp=sharing",
    "Advancement Info Legacy": "https://modrinth.com/mod/advancementinfo",
    "Advancement Info Reloaded": "https://modrinth.com/mod/advancements-reloaded",
    "Advancement Legend Rules": "https://docs.google.com/document/d/1WZsGkN7D9piecNOFLRUNL-5GbAX_0Wgb5rxk6Lo1ess/edit?usp=sharing",
    "BACAP Version History": "https://docs.google.com/document/d/1eVlWRDDyhuXMbPpXFNJkk-gYF6NtALNbrI97ARe3-5w/edit?usp=sharing",
    "BACAP Trophy List": "https://docs.google.com/spreadsheets/d/1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI/edit?usp=sharing",
    "Patreon Upcoming Features List": "https://tinyurl.com/y92mxs6r"
}

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
    image_name = "docs.png"
    try:
        if doc_search in ["Advancement Info Reloaded", "Advancement Info Legacy"]:
            embed = discord.Embed(
                title="Documentation",
                description=f"The {doc_search} download link may be found here:\n{sorted_doc_names[doc_search]}"
            )
            image_name = "docs.png"
            if image_name in image_cache:
                file_path = image_cache[image_name]
                file = discord.File(file_path, filename=image_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")
            else:
                embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
                logging.warning(f"{interaction.user} ({interaction.user.id})'s /doc command success failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

        else:
            embed = discord.Embed(
                title=f"Documentation",
                description=f"The {doc_search} documentation may be found here:\n{sorted_doc_names[doc_search]}"
            )
            image_name = "docs.png"
            if image_name in image_cache:
                file_path = image_cache[image_name]
                file = discord.File(file_path, filename=image_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")
            else:
                embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
                logging.warning(f"{interaction.user} ({interaction.user.id})'s /doc command success failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

    except:
        ephemeral = True
        image_name = "command_failed.png"
        embed = discord.Embed(
            title="Documentation",
            description=f"Perhaps the archives are incomplete. There is no such option named {doc_search}. Please try again with a valid option.",
            color=0xff0000
        )
        image_name = "command_failed.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /doc command failure failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

    await interaction.response.send_message(embed=embed, ephemeral=ephemeral, file=file)


@bot.tree.command(name="doc", description="Links you to any official BACAP documentation")
@app_commands.describe(doc_search="Links you to any official BACAP documentation!")
@app_commands.autocomplete(doc_search=doc_autocomplete)
async def doc(interaction: discord.Interaction, doc_search: str):
    logging.info(f"/doc command was ran by {interaction.user} ({interaction.user.id}) Input: {doc_search}")
    await show_documentation(interaction, doc_search)


@bot.tree.command(name="documentation", description="Links you to any official BACAP documentation")
@app_commands.describe(doc_search="Links you to any official BACAP documentation!")
@app_commands.autocomplete(doc_search=doc_autocomplete)
async def documentation(interaction: discord.Interaction, doc_search: str):
    logging.info(f"/documentation command was ran by {interaction.user} ({interaction.user.id}) Input: {doc_search}")
    await show_documentation(interaction, doc_search)


################### ACTUAL BACAP BOT STUFF #######################

def find_children():
    # Cycle through every advancement (child)
    for i, advancement in enumerate(advs):
        child_name = advancement["Advancement Name"]

        try:
            # Safeguard: Initialize parent_name with a default value
            parent_name = advancement.get("Parent", "")

            # Skip if the parent_name is empty
            if not parent_name:
                continue

            # Find the ID of the parent and assign it the child's name
            parent_id = adv_index[parent_name.upper()]

            if advs[parent_id]["Children"] != "":
                advs[parent_id]["Children"] = advs[parent_id]["Children"] + ", " + child_name
            else:
                advs[parent_id]["Children"] = child_name

        except Exception as e:
            logging.warning(f"WARNING: Advancement {parent_name} NOT FOUND!")
            logging.warning(e)

    # for a in advs:
    #     children = a["Children"]
    #     if "and" in children:
    #         print(a["Advancement Name"], children.count("and") + 1, children)

# GET COLOR FROM CELLS
def get_category_from_color_or_so_help_me_god(rgb):
    colors = {
        (243, 243, 243): "root",
        (147, 196, 125): "task",
        (109, 158, 235): "goal",
        (194, 123, 160): "challenge",
        (224, 102, 102): "super_challenge",
        (213, 166, 189): "hidden",
        (255, 217, 102): "milestone",
        (246, 178, 107): "advancement_legend",
    }
    if rgb not in colors:
        logging.warning(f"Color combination {rgb} not found in color dictionary.")

    return colors.get(rgb, "task")

def get_cell_color(background_color):
    red = round(background_color.get("red", 1) * 255, 0)
    green = round(background_color.get("green", 1) * 255, 0)
    blue = round(background_color.get("blue", 1) * 255, 0)
    return (red, green, blue)

def assign_cell_colors(sheet_key):
    try:
        # Authenticate with Google Sheets API
        creds = Credentials.from_service_account_file("Text/google_auth.json")
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        logging.info("Starting to assign cell colors to advancements.")

        # Group advancements by their worksheet
        advancements_by_worksheet = {}
        for adv in advs:
            worksheet_title = adv["adv_tab"]
            if worksheet_title not in advancements_by_worksheet:
                advancements_by_worksheet[worksheet_title] = []
            advancements_by_worksheet[worksheet_title].append(adv)

        # Process each worksheet
        for worksheet_title, worksheet_advs in advancements_by_worksheet.items():
            logging.info(f"Processing worksheet: {worksheet_title}")

            # Fetch cell formatting data for column A
            range_name = f"'{worksheet_title}'!A2:A"
            formatting = sheet.get(
                spreadsheetId=sheet_key,
                ranges=range_name,
                fields="sheets(data(rowData(values(effectiveFormat(backgroundColor)))))"
            ).execute()

            # Extract row data
            row_data = formatting["sheets"][0]["data"][0].get("rowData", [])
            row_colors = []

            for row in row_data:
                background_color = row.get("values", [{}])[0].get("effectiveFormat", {}).get("backgroundColor", {})
                cell_color = get_cell_color(background_color)
                row_colors.append(cell_color)

            # Assign colors to advancements
            for i, adv in enumerate(worksheet_advs):
                if i < len(row_colors):

                    index = adv_index[adv['Advancement Name'].upper()]
                    advs[index]['Category'] = get_category_from_color_or_so_help_me_god(row_colors[i])


                    # logging.info(f"Assigned color {row_colors[i]} to advancement '{adv['Advancement Name']}'")
                else:
                    adv["Cell Color"] = None
                    logging.warning(f"No color data found for advancement '{adv['Advancement Name']}' in worksheet '{worksheet_title}'")
            # print(worksheet_advs)

        logging.info("Finished assigning cell colors to advancements.")

    except Exception as e:
        logging.error(f"An error occurred while assigning cell colors: {e}")

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
        logging.info(f"THIS MESSAGE IS TO INDICATE {sheet} WAS OPENED SUCCESSFULLY")


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

                # The loop will only get down here if it's reading a valid advancement (due to continues)
                row["adv_tab"] = worksheet.title

                # Add each advancement row into the advs list
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
        # Assign cell colors to advancements

        # Get backgrounds
        assign_cell_colors(sheet_key)

    except Exception as e:
        logging.error(f"\nWHILE LOADING SPREADSHEET {sheet}, AN ERROR OCCURED :sadcave:\n{e}")


# open trophy sheet if possible
def access_trophy_sheet(trophy_sheet_key):
    global trophy_data
    global trophy_index
    trophy_data = []
    trophy_index = {}

    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(trophy_sheet_key)
        logging.info(f"THIS MESSAGE IS TO INDICATE {sheet} WAS OPENED SUCCESSFULLY")

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
        logging.error(f"\nWHILE LOADING SPREADSHEET {sheet}, AN ERROR OCCURED :sadcave:\n{e}")

def access_BACAP_datapack():
    global advs
    global adv_namespace

    # Remember to update this
    adv_directories = ["./packs/BlazeandCaves Advancements Pack 1.19/data/blazeandcave/advancement",
                       "./packs/BlazeandCaves Advancements Pack 1.19/data/minecraft/advancement"]
    adv_paths = []
    adv_namespace = []

    for directory in adv_directories:
        for root, dirs, files in os.walk(directory, topdown=True):
            for file in files:
                adv_path = os.path.join(root, file).replace('\\', '/')
                if adv_path.split('data/',1)[1] not in adv_namespace:
                    adv_paths.append(adv_path)
                    adv_namespace.append(adv_path.split('data/',1)[1])

    adv_paths = [adv for adv in adv_paths if '/technical' not in adv]

    for adv_path in adv_paths:
        with open(adv_path, encoding='utf-8') as adv_file:
            datapack_adv = json.load(adv_file)

            try:
                title = datapack_adv["display"]["title"]["translate"]
                if "extra" in datapack_adv["display"]["title"].keys() and title != "Riddle Me This":
                    for extra in datapack_adv["display"]["title"]["extra"]:
                        title += extra["translate" if "translate" in extra.keys() else "text"]
                
                if title == "Feeding the §mDucks§r Chickens": # Hardcode this weird guy
                    title = "Feeding the Ducks Chickens"

                # Merge into advs dictionary if adv exists
                if title.upper() not in adv_index:
                    logging.warning(f"Bad title: {title}")
                else:

                    adv = advs[adv_index[title.upper()]]

                    adv["Icon"] = datapack_adv["display"]["icon"]["id"].replace("minecraft:", "minecraft_")

                    # LIST OF EXCEPTIONS
                    blacklist = {
                        'ALL AROUND THE WORLD' : 'custom/all_around_the_world', 
                        'CHROMATIC ARMORY': 'custom/chromatic_armory', 
                        'COORDINATED FLAIR': 'custom/coordinated_flair',
                        'I AM RAVAGER, HEAR ME ROAR!': 
                        'custom/ominous_shield', 
                        'JUSTICE': 'custom/leaping_arrow', 
                        'NERDS NEVER DIE': 'custom/technoblade_head', 
                        'RIOT SHIELD': 'custom/riot_shield', 
                        'SHADY DEALS': 'custom/invisibility_potion', 
                        'THE SHIELDING': 'custom/vindicator_shield', 
                        'WHAT\'S UP, DOC?': 'custom/dinnerbone_head', 
                        'YOU ARE THE PILLAGER': 'custom/pillager_head', 
                        'BATTLE OF THE BANDS': 'custom/ominous_banner', 
                        'COLORFUL CAVALRY': 'custom/colorful_cavalry', 
                        'FASHION STATEMENT': 'custom/fashion_statement', 
                        'HEAVY DUTY CARAVAN': 'custom/strength_potion', 
                        'PAW PATROL': 'custom/paw_patrol', 
                        'SHOE SHED': 'custom/shoe_shed', 
                        'ADVANCEMENT LEGEND': 'custom/cavinator1_head', 
                        'CAPTAIN AMERICA': 'custom/captain_america', 
                        'DIVE BOMB': 'custom/dive_bomb', 
                        'KUNG FU PANDA!': 'custom/kung_fu_chestplate', 
                        'BIOLOGICAL WARFARE': 'custom/lingering_harming', 
                        'DRAGON VS WITHER: THE PRE-SEQUEL': 'custom/wither_head', 
                        'OVERWARDEN': 'custom/warden_head', 
                        'POTION MASTER': 'custom/splash_healing', 
                        'THE PERFECT RUN': 'custom/perfect_run', 
                        'THE WORLD IS ENDING': 'custom/wither_head', 
                        'OH BABY A TRIPLE!': 'custom/harming_arrow', 
                        'DIMENSION PENETRATION': 'custom/turtle_master_arrow', 
                        'DIVER\'S DOZEN': 'custom/harming_arrow', 
                        'DRAGON SHIELD': 'custom/dragon_shield', 
                        'ROCKETMAN': 'custom/rocketman', 
                        'SHOULDN\'T MY SHIELD LEVITATE TOO?': 'custom/shulker_shield', 
                        'SOME BREAKTHROUGH': 'custom/broken_elytra', 
                        'THE ACTUAL END': 'custom/enderman_head', 
                        'THE BEGINNING': 'custom/wither_head', 
                        'VOID WALKER': 'custom/void_walkers', 
                        'CERTIFIED SPUD CHOMPER': 'custom/mega_spud', 
                        'AWW MAN!': 'custom/captainsparklez_head', 
                        'BLAST SHIELD': 'custom/blast_shield', 
                        'BONE-TO-PARTY': 'custom/wither_head', 
                        'FAMILY REUNION': 'custom/pigman_head', 
                        'OH NO GUYS I\'M O O Z I N G': 'custom/slime_head', 
                        'POISON DART': 'custom/poison_arrow', 
                        'POULTRY BOY': 'custom/poultry_man', 
                        'RICOCHET SWOOP': 'custom/phantom_shield', 
                        'TASTE OF YOUR OWN MEDICINE': 'custom/splash_poison', 
                        'TRIDENTED SHIELD': 'custom/tridented_shield', 
                        'FIRE BLAST SHIELD': 'custom/ghast_shield', 
                        'HUNG, DRAWN AND BARTERED': 'custom/splash_fire_resistance', 
                        'LEGEND OF HELL CHICKEN RIDERS': 'custom/poultry_man', 
                        'THE NETHER\'S SHIELD': 'custom/blaze_shield', 
                        'DEATH BY MAGIC': 'custom/splash_harming', 
                        'FINAL SHOUT': 'custom/splash_wind_charge', 
                        'FURIOUS AMMUNITION': 'custom/regeneration_arrow', 
                        'GAS!': 'custom/lingering_harming', 
                        'IMBUED PROJECTILES': 'custom/swiftness_arrow', 
                        'MAD SCIENTIST': 'custom/villager_head', 
                        'NOXIOUS FUMES': 'custom/lingering_poison', 
                        'POTIONS': 'custom/uncraftable_potion', 
                        'STRING SHOT': 'custom/weaving_arrow', 
                        'BLACK BELT NINJA': 'custom/void_chestplate', 
                        'LAPS IN THE POOL': 'custom/slightly_different_dive_bomb', 
                        'LIGHTNING MCPIG': 'custom/pig_head', 
                        'MORE FOR ME': 'custom/healing_potion', 
                        'SNEAKY SNITCH': 'custom/void_walkers', 
                        'ARTILLERY': 'custom/charged_crossbow', 
                        'EXPLOSIVE FIRE': 'custom/firework_crossbow', 
                        'FLYING COLORS': 'custom/red_shield', 
                        'LOSER!': 'custom/loser', 
                        'MASTER SHIELDSMAN': 'custom/black_shield', 
                        'MY EYES!': 'custom/my_eyes', 
                        'PYROTECHNIC': 'custom/pyrotechnic', 
                        'WHEN PIGS FINALLY FLY': 'custom/pig_head', 
                        'CAREFUL RESTORATION': 'custom/pot', 
                        'CRAFTING A NEW LOOK': 'custom/crafting_a_new_look', 
                        "I'VE GOT A BAD FEELING ABOUT THIS": 'custom/ominous_banner', 
                        'LIGHT AS A RABBIT': 'custom/light_boots', 
                        'WHOS\'S THE PILLAGER NOW?': 'custom/pillager_head', 
                        'NOT TODAY, THANK YOU': 'custom/bone_shield'
                    }

                    if title.upper() in blacklist:
                        adv["Icon"] = blacklist[title.upper()]

                    # Set a default non-null value of False
                    adv["Enchanted"] = False

                    # Check if the item is enchanted
                    if "components" in datapack_adv["display"]["icon"]:
                        if "minecraft:enchantment_glint_override" in datapack_adv["display"]["icon"]["components"]:
                            adv["Enchanted"] = True
                            
                    # For advs which group some of their criteria together
                    if "requirements" in datapack_adv:
                        adv["Criteria Count"] = len(datapack_adv["requirements"])
                    else:
                        adv["Criteria Count"] = len(datapack_adv["criteria"])
                    
                    # Gets the advancement id from the file path
                    adv["Advancement Id"] = adv_path.split('data/',1)[1].replace('/advancement/',':').replace('.json','')

            except Exception as e:
                logging.warning(f"Error parsing {adv_path} with error {e}")
                continue

def truncate_to_namespace(id: str):
    return id.split(':')[1].replace('/','_')

# The great add-on reader
def access_BACAP_addons():
    global addon_advs
    global addon_adv_index
    global sorted_addon_adv_names
    global addon_list
    global adv_namespace
    global addon_adv_namespace
    global tier_mapper
    global tab_mapper
    global add_base_pack_note
    global addon_children_list
    addon_advs = {}
    addon_adv_index = {}
    sorted_addon_adv_names = {}

    tier_mapper = {
        ('#CCCCCC','task'): 'root',
        ('#CCCCCC','challenge'): 'root',
        ('green','task'): 'task',
        ('#75E1FF','goal'): 'goal',
        ('dark_purple','challenge'): 'challenge',
        ('#FF2A2A','challenge'): 'super_challenge',
        ('light_purple','task'): 'hidden',
        ('light_purple','challenge'): 'hidden',
        ('yellow','goal'): 'milestone',
        ('gold','challenge'): 'realisticcave_advancement_legend'
    }
    tab_mapper = {
        'bacap': "B&C Advancements",
        'mining': 'Mining',
        'building': 'Building',
        'farming': 'Farming',
        'animal': "Animals",
        'monsters': 'Monsters',
        'weaponry': 'Weaponry',
        'biomes': 'Biomes',
        'adventure': 'Adventure',
        'redstone': 'Redstone',
        'enchanting': 'Enchanting',
        'statistics': 'Statistics',
        'nether': 'Nether',
        'potion': 'Potions',
        'end': 'End',
        'challenges': 'Super Challenges'
    }

    # Loads language file
    lang_url = 'https://raw.githubusercontent.com/misode/mcmeta/refs/heads/assets/assets/minecraft/lang/en_us.json'
    response = requests.get(lang_url)
    lang = response.json()
    
    addon_list = os.listdir('./packs/addons')
    logging.info(f'Processing addons {', '.join(addon_list)}')

    for addon in addon_list:

        addon_advs[addon] = []
        addon_adv_paths = []
        addon_adv_namespace = []
        addon_children_list = []
        
        try:
            # Checks pack.mcmeta for pack overrides and sorts them by minimum pack format if they exist
            with open(f'./packs/addons/{addon}/pack.mcmeta','r',encoding='utf-8') as mcmeta:
                mcmeta_json = json.load(mcmeta)
            
            if mcmeta_json.get('overlays'):

                overlays_json = mcmeta_json['overlays']['entries']
                overlays = []

                for overlay in overlays_json:
                    pack_formats = overlay['formats']
                    if isinstance(pack_formats, int):
                        pack_format = pack_formats
                    elif isinstance(pack_formats, list):
                        pack_format = pack_formats[0]
                    elif isinstance(pack_formats, dict):
                        pack_format = pack_formats['min_inclusive']
                    else:
                        logging.warning(f'Invalid pack format in addon {addon}: {pack_formats}')
                        continue

                    directory = overlay['directory']
                    overlays.append((pack_format, directory))

                overlays = sorted(overlays, reverse=True)

                # If overlays exist opens and sorts through them first before the main directory
                for pack_format, directory in overlays:

                    for root, dirs, files in os.walk(f'./packs/addons/{addon}/{directory}'):
                        for file in files:
                            path = os.path.join(root,file).replace('\\','/').replace('/advancements/','/advancement/')
                            namespace = path.split('data/',1)[1]
                            if '.json' in path and '/advancement/' in path and (namespace not in adv_namespace):
                                addon_adv_paths.append(path)
                                adv_namespace.append(namespace)
                                addon_adv_namespace.append(namespace)
            else:
                overlays = []

            # Now iterates through the main directory
            for root, dirs, files in os.walk(f'./packs/addons/{addon}/data'):
                for file in files:
                    path = os.path.join(root,file).replace('\\','/').replace('/advancements/','/advancement/')
                    namespace = path.split('data/',1)[1]
                    if '.json' in path and '/advancement/' in path and namespace not in adv_namespace or namespace == 'minecraft/advancement/husbandry/obtain_netherite_hoe.json':
                        addon_adv_paths.append(path)
                        adv_namespace.append(namespace)
                        addon_adv_namespace.append(namespace)
        except Exception as e:
            logging.warning(f'Failed to load addon {addon}: {e}')
            continue

        # Iterates through the advancements in the path list
        for addon_adv_path in addon_adv_paths:
            try:
                adv_dict = {}

                with open(addon_adv_path, 'r',encoding='utf-8') as adv_file:
                    adv = dict(json.load(adv_file))

                # Halts when trying to look through technical advancements
                if not (adv.get('display') and adv.get('rewards')):
                    continue

                # Title

                title_data = adv['display']['title']

                if isinstance(title_data, dict):
                    title = title_data['translate' if title_data.get('translate') else 'text']
                    if title_data.get('extra'):
                        for extra in title_data['extra']:
                            title += extra['translate' if extra.get('translate') else 'text']
                else:
                    title = title_data

                title = title.strip()
                adv_dict['Advancement Name'] = title

                # Set to empty string
                adv_dict['Children'] = ''

                # Id

                adv_id = addon_adv_path.split('data/',1)[1].replace('/advancement/',':').replace('.json','')
                adv_dict['Advancement Id'] = adv_id

                # Category

                frame = adv['display'].get('frame','task')

                if isinstance(adv['display']['description'], dict) and adv['display']['description'].get('color'):
                    adv_color = adv['display']['description']['color']
                elif frame == 'challenge':
                    adv_color = 'dark_purple'
                else:
                    adv_color = 'green'
                
                if (adv_color,frame) in tier_mapper.keys():
                    category = tier_mapper[(adv_color,frame)]
                else:
                    category = f"custom;{adv_color};{frame}"

                adv_dict['Category'] = category

                # Description

                description_data = adv['display']['description']

                if isinstance(description_data, dict):
                    description = description_data['translate' if description_data.get('translate') else 'text']
                    if description_data.get('extra') and title not in []:
                        for extra in description_data['extra']:
                            if extra['translate' if extra.get('translate') else 'text'] != '\n\n' or title in []:
                                description += extra['translate' if extra.get('translate') else 'text']
                            else:
                                break
                else:
                    description = description_data
                
                description = description.strip()
                adv_dict['Description'] = description

                # Icon (and Enchanted)

                icon_data = adv['display']['icon']
                icon = icon_data['id']

                enchanted = bool(icon_data.get('components',{}).get('minecraft:enchantment_glint_override', False))

                adv_dict['Icon'] = ('minecraft_' if not icon.startswith('minecraft:') else '') + icon.replace('minecraft:','minecraft_')
                adv_dict['Enchanted'] = enchanted

                # Criteria Count

                criteria_count = len(adv['requirements' if adv.get('requirements') else 'criteria'])
                adv_dict['Criteria Count'] = criteria_count

                # Tab

                tab = tab_mapper[find_tab(adv['parent'], addon, overlays)]
                adv_dict['adv_tab'] = tab

                # Parent

                if adv.get('parent'):
                    add_base_pack_note = False
                    parent_adv_id = adv['parent']
                    parent = find_parent(parent_adv_id, title, addon, overlays)
                else:
                    parent = ''

                # You are a big cheater!
                parent = 'Statistics **(from Statistics tab)**' if parent.startswith('You are a big cheater!') else parent

                adv_dict['Parent'] = parent

                # Gets item reward xp and trophy functions from reward file

                reward_function = adv['rewards']['function']
                reward_path = namespace_to_dir(reward_function, addon, overlays, 'function')

                with open(reward_path,'r',encoding='utf-8') as reward_file:
                    reward_found = False
                    xp_found = False
                    trophy_found = False
                    for line in reward_file:
                        if line.startswith('execute if score reward') and not reward_found:
                            rewards_function = namespace_to_dir(line.split()[-1], addon, overlays, 'function')
                            reward_found = True
                        elif line.startswith('execute if score exp') and not xp_found:
                            xp_function = namespace_to_dir(line.split()[-1], addon, overlays, 'function')
                            xp_found = True
                        elif line.startswith('execute if score trophy') and not trophy_found:
                            trophy_function = namespace_to_dir(line.split()[-1], addon, overlays, 'function')
                            trophy_found = True

                # Item Rewards
                
                if reward_found and os.path.exists(rewards_function):
                    with open(rewards_function,'r',encoding='utf-8') as reward_file:
                        reward_list = []
                        reward_commands = [command for command in reward_file.readlines() if command.startswith('tellraw ')]

                        for reward_command in reward_commands:
                            if reward_command.startswith('tellraw @s ['):
                                reward_data = nbtlib.parse_nbt(reward_command[reward_command.rindex(' [')+1:])
                                reward_text = reward_data[0]['text'][2:]

                                for extra in reward_data[1:]:
                                    if extra.get('translate') in lang:
                                        reward_text += lang[extra['translate']]
                                    elif extra.get('fallback'):
                                        reward_text += extra['fallback']
                                    else:
                                        reward_text += extra['translate' if extra.get('translate') else 'text']
                            else:
                                reward_data = nbtlib.parse_nbt(reward_command[reward_command.rindex(' {')+1:])
                                reward_text = reward_data['text'][2:]

                                for extra in reward_data["extra"]:
                                    if extra.get('translate') in lang:
                                        reward_text += lang[extra["translate"]]
                                    elif extra.get('fallback'):
                                        reward_text += extra['fallback']
                                    else:
                                        reward_text += extra['translate' if extra.get('translate') else 'text']
                            
                            reward_list.append(reward_text)

                        reward = ', '.join(reward_list)
                else:
                    reward = ''
                
                adv_dict['Item rewards'] = reward

                # XP Rewards

                if xp_found and os.path.exists(xp_function):
                    with open(xp_function,'r',encoding='utf-8') as xp_reward_file:
                        xp_command = xp_reward_file.readline()
                        if xp_command.startswith('xp'):
                            xp_reward = int(xp_command.split()[-1])
                        else:
                            xp_reward = ""
                else:
                    xp_reward = ""

                adv_dict['XP Rewards'] = xp_reward

                # Trophy

                if trophy_found and os.path.exists(trophy_function):
                    with open(trophy_function,'r',encoding='utf-8') as trophy_reward_file:
                        trophy_file_lines = [command.replace('\\','') for command in trophy_reward_file.readlines()]
                        for command in trophy_file_lines:
                            if command.startswith('tellraw'):
                                try:
                                    trophy_nbt = nbtlib.parse_nbt(command[command.find('{'):])
                                    trophy = trophy_nbt['extra'][0]['translate']
                                    break
                                except:
                                    trophy_nbt = nbtlib.parse_nbt(command[command.find('['):])
                                    trophy = trophy_nbt[1]['translate']
                                    break
                        else:
                            trophy = ''
                else:
                    trophy = ''

                adv_dict['Trophy'] = trophy

                adv_dict['Add-on'] = addon

                addon_advs[addon].append(adv_dict)
            except Exception as e:
                logging.warning(f'Failed to load advancement {addon_adv_path.split('data/',1)[1].replace('/advancement/',':').replace('.json','')} in addon {addon}: {e}')

        # Creates index and finds children after loop is finished
        addon_adv_index[addon] = {}
        sorted_addon_adv_names[addon] = []

        for i, advancement in enumerate(addon_advs[addon]):
            addon_adv_index[addon][advancement['Advancement Name'].upper()] = i
            sorted_addon_adv_names[addon].append(advancement['Advancement Name'])

            children_list = []
            for parent, children in addon_children_list:
                if parent == advancement['Advancement Name']:
                    children_list.append(children)

            addon_advs[addon][i]['Children'] = ', '.join(children_list)

        logging.info(f'Loaded {len(addon_advs[addon])} advancements from addon {addon}')


def namespace_to_dir(function: str, addon: str, overlays: str, mode: str = 'advancement'):
    function = function.split(':')

    if overlays:

        for pack_format, directory in overlays:
            if os.path.exists(f'./packs/addons/{addon}/{directory}/data/{function[0]}/{mode}/{function[1]}.{'mcfunction' if mode == 'function' else 'json'}'):
                return f'./packs/addons/{addon}/{directory}/data/{function[0]}/{mode}/{function[1]}.{'mcfunction' if mode == 'function' else 'json'}'
        else:
            return f'./packs/addons/{addon}/data/{function[0]}/{mode}/{function[1]}.{'mcfunction' if mode == 'function' else 'json'}'
        
    else:
        return f'./packs/addons/{addon}/data/{function[0]}/{mode}/{function[1]}.{'mcfunction' if mode == 'function' else 'json'}'
    
def find_tab(adv_id: str, addon: str, overlays: str):
            # Vanilla root cases
            if adv_id == 'minecraft:husbandry/root':
                return('animal')
            #  If id follows the format of <namespace>:<existing tab>/<advancement> return tab
            elif re.split(r':|/', adv_id)[1] in tab_mapper.keys():
                return re.split(r':|/', adv_id)[1]
            else:
                # If id already exists in either of the dictionaries return tab of that advancement
                for parent_adv in addon_advs[addon]:
                    if parent_adv.get('Advancement Id') == adv_id:
                        return next((key for key, value in tab_mapper.items() if value == parent_adv.get('adv_tab')), None)
                else:
                    for parent_adv in advs:
                        if parent_adv.get('Advancement Id') == adv_id:
                            return next((key for key, value in tab_mapper.items() if value == parent_adv.get('adv_tab')), None)
                    else:
                        # If all else fails result to recurring function but with parent advancement instead
                        try:
                            with open(namespace_to_dir(adv_id, addon, overlays),'r',encoding='utf-8') as f:
                                parent_data = json.load(f)
                        except FileNotFoundError:
                            with open(namespace_to_dir(adv_id, addon, overlays).replace(f'addons/{addon}','Blazeandcaves Advancements Pack 1.19'),'r',encoding='utf-8') as f:
                                parent_data = json.load(f)
                        return find_tab(parent_data['parent'], addon, overlays) 
                    
def find_parent(parent_adv_id: str, title: str, addon: str, overlays: str):
            add_base_pack_note = False

            split_parent_adv_id = parent_adv_id.split(':')

            if f'{split_parent_adv_id[0]}/advancement/{split_parent_adv_id[1]}.json' in adv_namespace and f'{split_parent_adv_id[0]}/advancement/{split_parent_adv_id[1]}.json' not in addon_adv_namespace and parent_adv_id != 'minecraft:husbandry/obtain_netherite_hoe':
                parent_adv_path = f'./packs/Blazeandcaves Advancements Pack 1.19/data/{split_parent_adv_id[0]}/advancement/{split_parent_adv_id[1]}.json'
                add_base_pack_note = True
            else:
                parent_adv_path = namespace_to_dir(parent_adv_id, addon, overlays)

            with open(parent_adv_path,'r',encoding='utf-8') as parent_adv_file:
                parent_adv = json.load(parent_adv_file)
            
            if parent_adv.get('display'):
                parent_title_data = parent_adv['display']['title']
                if isinstance(parent_title_data, dict):
                    parent = parent_title_data['translate' if parent_title_data.get('translate') else 'text']
                    if parent_title_data.get('extra'):
                        for extra in parent_title_data['extra']:
                            parent += extra['translate' if extra.get('translate') else 'text']
                else:
                    parent = parent_title_data

                parent = parent.strip()

                if add_base_pack_note:
                    for adv_dict in advs:
                        if adv_dict['Advancement Name'] == parent:
                            parent += f' **(from {adv_dict['adv_tab']} tab)**'
                            break                   
                else:
                    global addon_children_list
                    addon_children_list.append((parent, title))
                return parent
            else:
                parent_adv_parent = parent_adv['parent']
                return find_parent(parent_adv_parent, title, addon, overlays)

def build_adv_icons():
    text_colors = {
        'black': (0, 0, 0),
        'dark_blue': (0, 0, 170),
        'dark_green': (0, 170, 0),
        'dark_aqua': (0, 170, 170),
        'dark_red': (170, 0, 0),
        'dark_purple': (170, 0, 170),
        'gold': (255, 170, 0),
        'gray': (170, 170, 170),
        'dark_gray': (85, 85, 85),
        'blue': (85, 85, 255),
        'green': (85, 255, 85),
        'aqua': (85, 255, 255),
        'red': (255, 85, 85),
        'light_purple': (255, 85, 255),
        'yellow': (255, 255, 85),
        'white': (255, 255, 255)
    }
    
    # Set up the 50% opacity enchantment glint
    glint = Image.open("images/glint.png").convert("RGBA")
    glint_half_strength = glint.copy()
    glint_data = glint_half_strength.load()
    for x in range(glint_half_strength.width):
        for y in range(glint_half_strength.height):
            r, g, b, a = glint_data[x, y]
            glint_data[x, y] = (r, g, b, int(a/2)) # Halve alpha value

    # Make add-on image paths
    for addon in addon_list:
        if not os.path.exists(f"images/bacap/addons/{addon}"):
            os.makedirs(f"images/bacap/addons/{addon}", exist_ok=True)

    for adv in advs + [addon_adv for addon_list in addon_advs.values() for addon_adv in addon_list]:

        item_name = adv['Icon']
        frame_name = adv['Category']

        if not os.path.exists(f"images/bacap"):
            os.mkdir(f"images/bacap")

        # Load images for the frame and item
        try:
            if frame_name.startswith('custom;'):
                # Custom frame maker
                frame_color, frame_shape = frame_name.split(';')[1:]
                if os.path.exists(f"images/frames/custom/{frame_color}_{frame_shape}.png"):
                    frame = Image.open(f"images/frames/custom/{frame_color}_{frame_shape}.png").convert('RGBA')
                else:
                    if frame_color in text_colors.keys():
                        frame_color = text_colors[frame_color]
                    elif frame_color.startswith('#'):
                        frame_color = (int(frame_color[1:3], 16), int(frame_color[3:5], 16), int(frame_color[5:7], 16))
                    else:
                        logging.warning(f'Invalid color {frame_color} found in advancement {adv['Advancement Name']}, defaulting to #FFFFFF')
                        frame_color = '#FFFFFF'

                    frame = Image.open(f"images/frames/{frame_shape}_raw.png").convert("RGBA")
                    frame_data = frame.load()
                    for x in range(frame.width):
                        for y in range(frame.height):
                            r, g, b, a = frame_data[x, y]
                            frame_data[x, y] = (r*frame_color[0]//255, g*frame_color[1]//255, b*frame_color[2]//255, a)
                    frame.save(f"images/frames/custom/{'_'.join(frame_name.split(';')[1:])}.png")
            else:
                frame = Image.open(f"images/frames/{frame_name}.png").convert("RGBA")
            item = Image.open(f"images/mc_textures/{item_name}.png").convert("RGBA")
        except Exception as e:
            logging.warning(f"File could not be found for advancement {adv['Advancement Id']}, with error {e}")

        try:
            # Make enchanted version
            if adv["Enchanted"]:
                ench_item = item.copy()
                ench_item.alpha_composite(glint_half_strength,(0,0),(0,0))

                img_pixels = []
                for r, g, b, a in ench_item.getdata():
                    if a < 255:
                        img_pixels.append((r, g, b, 0))
                    else:
                        img_pixels.append((r, g, b, 255))

                ench_item = Image.new("RGBA", (64, 64))
                ench_item.putdata(img_pixels)

                # Enchanted item and normal item take the exact same set of pixels so no new copy is necessary
                new_frame = frame.copy()
                new_frame.paste(item, (20, 20), item) # Paste the original item first to eliminate transparency bugs
                new_frame.paste(ench_item, (20, 20), ench_item)
            
            # Make normal version
            else:
                new_frame = frame.copy()
                new_frame.paste(item, (20, 20), item)

            # Saves image    
            if adv.get('Add-on'): # Base pack advs have this while add-on advs don't
                new_frame.save(f"images/bacap/addons/{adv['Add-on']}/{truncate_to_namespace(adv['Advancement Id'])}.png")
            else:
                new_frame.save(f"images/bacap/{truncate_to_namespace(adv['Advancement Id'])}.png")

        except Exception as e:
            logging.warning(f"{adv} could not be built, giving error {e}")

    logging.info(f"{len(advs + [addon_adv for addon_list in addon_advs.values() for addon_adv in addon_list])} advancement icons built!")

# refresh admin fix
you_have_rights = {407695710058971138, 131972834695184385, 360894618734428160, 558916591950102538}


## REFRESH ADVANCEMENT SHEET
@bot.tree.command(name="refresh_advancements", description="Refreshes and reloads all advancements into bot.")
async def refresh(interaction: discord.Interaction):
    logging.info(f"/refresh_advancements command was ran by {interaction.user} ({interaction.user.id})")

    if interaction.user.id not in you_have_rights:
        await interaction.response.send_message("**You do not have permission to run this command.**", ephemeral=True)
        return
    try:
        # Defer the response to let the bot know it's working on something
        await interaction.response.defer(thinking=True)

        # Reload the advancements from the sheet
        access_sheet(BACAP_DOC_KEY)

        # Send a follow-up message after processing
        await interaction.followup.send("*All advancements have been reloaded successfully.*")

    except Exception as e:
        # Send an error message if something went wrong
        await interaction.followup.send(f"*Uh oh! An error occurred while reloading all advancements.*\nError: **{e}**")


## REFRESH TROPHY SHEET
@bot.tree.command(name="refresh_trophies", description="Refreshes and reloads all trophies into bot.")
async def refresh(interaction: discord.Interaction):
    logging.info(f"/refresh_trophies command was ran by {interaction.user} ({interaction.user.id})")

    if interaction.user.id not in you_have_rights:
        await interaction.response.send_message("**You do not have permission to run this command.**",ephemeral=True)
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

def embed_advancement(advancement, extra_info, color):
    if emotes.get(advancement.get('Category','goal')):
        adv_emote = emotes.get(advancement.get('Category','goal'))
    elif advancement.get('Category').startswith('custom;'):
        adv_emote = emotes.get(f"custom_{advancement.get('Category').split(';')[1]}")
    else:
        adv_emote = '🛃'
    

    # Parent/Children field will not be shown in embed if it does not exist
    # Making the description conditional prevents Parent/Children lines that are empty still
    # showing on embed
    desc = f"# {adv_emote} {advancement['Advancement Name']} {adv_emote}\n"
    desc += f"**(from {advancement['Add-on']})**\n" if advancement.get('Add-on') else ""
    desc += f"*__{advancement['Description']}__*\n\n"

    desc += f"📈   **Parent**: {advancement.get('Parent', '')}\n" if advancement.get('Parent', '') else "📈   **Parent**: N/A\n"
    desc += f"📉   **Children**: {advancement.get('Children', '')}\n" if advancement.get('Children', '') else "📉   **Children**: N/A\n"

    desc += f"{extra_info}"
    desc += f"\n*Part of the __{advancement['adv_tab']}__ tab.*"

    return discord.Embed(
        title="Advancement Found!",
        description=desc,
        color=color
    )

async def generate_adv_embed(interaction: discord.Interaction, advancement: str):
    global adv_image_file
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

    embed = embed_advancement(advancement, "", color)

    image_name = f"{truncate_to_namespace(advancement['Advancement Id'])}.png"
    file_path = f"images/bacap/{image_name}" if not advancement.get('Add-on') else f"images/bacap/addons/{advancement['Add-on']}/{image_name}"

    if os.path.exists(file_path):
        adv_image_file = discord.File(file_path, filename=image_name)
        embed.set_thumbnail(url=f"attachment://{adv_image_file.filename}")
    else:
        adv_image_file = None
        embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
        logging.warning(f"{interaction.user} ({interaction.user.id})'s /help command failed to display image. IMAGE FILE: {image_name}")
    
    view = button_logic(interaction.user, pages=[], color=color, tab=advancement["adv_tab"], advancement=advancement, paginated=False)
    await interaction.response.send_message(embed=embed, view=view, file=adv_image_file)
    
    view.message = await interaction.original_response()

## GET ADVANCEMENT COMMAND
@bot.tree.command(name="advancement", description="Display an advancement of your choice")
@app_commands.autocomplete(advancement_search=autocomplete)
@app_commands.describe(advancement_search="Display an advancement of your choice!")
async def get_advancement(interaction: discord.Interaction, advancement_search: str):
    logging.info(f"/advancement command was ran by {interaction.user} ({interaction.user.id}) Input: {advancement_search}")
    try:
        index = adv_index[advancement_search.upper()]
        advancement = advs[index]
        await generate_adv_embed(interaction, advancement)

    except Exception as e:
        embed = discord.Embed(
            title="Advancement Not Found!",
            description=f"*The advancement **{advancement_search}** could not be found. Please try again. {e}*",
            color=0xff0000
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

## ADDON ADVANCEMENT AUTOCOMPLETES
async def addon_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in addon_list:
        if len(results) == 25:
            break
        addon_name = result
        if addon_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=addon_name, value=addon_name))

    for result in addon_list:
        if len(results) == 25:
            break
        addon_name = result
        choice = app_commands.Choice(name=addon_name, value=addon_name)

        if choice not in results:
            if current.lower() in addon_name.lower():
                results.append(choice)
    return results

async def addon_adv_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    selected_addon = interaction.namespace.addon
    if selected_addon in addon_list:
        results = []
        for result in sorted_addon_adv_names[selected_addon]:
            if len(results) == 25:
                break
            adv_name = result
            if adv_name.lower().startswith(current.lower()):
                results.append(app_commands.Choice(name=adv_name, value=adv_name))

        for result in sorted_addon_adv_names[selected_addon]:
            if len(results) == 25:
                break
            adv_name = result
            choice = app_commands.Choice(name=adv_name, value=adv_name)

            if choice not in results:
                if current.lower() in adv_name.lower():
                    results.append(choice)
    else:
        results = []
    return results

## GET ADD-ON ADVANCEMENT COMMAND
@bot.tree.command(name="addon_advancement", description="Display an advancement of your choice, from a BACAP add-on of your choice")
@app_commands.autocomplete(addon=addon_autocomplete)
@app_commands.autocomplete(advancement_search=addon_adv_autocomplete)
@app_commands.describe(addon="The add-on you want to display an advancement from", advancement_search="Display an advancement of your choice!")
async def get_addon_advancement(interaction: discord.Interaction, addon: str, advancement_search: str):
    logging.info(f"/addon_advancement command was ran by {interaction.user} ({interaction.user.id}) Input: {addon}, {advancement_search}")
    try:
        if addon in addon_list:
            if advancement_search in sorted_addon_adv_names[addon]:
                index = addon_adv_index[addon][advancement_search.upper()]
                advancement = addon_advs[addon][index]
                await generate_adv_embed(interaction, advancement)
            else:
                embed = discord.Embed(
                    title="Advancement Not Found!",
                    description=f"*The advancement **{advancement_search}** could not be found in add-on **{addon}**. Please try again.",
                    color=0xff0000
                )

                await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            embed = discord.Embed(
                title="Add-on Not Found!",
                description=f"*The add-on **{addon}** could not be found. Please try again.",
                color=0xff0000
            )

            await interaction.response.send_message(embed=embed,ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="Advancement Not Found!",
            description=f"*An unexpected error was encountered. Please try again. {e}",
            color=0xff0000
        )

        await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command(name="random", description="Displays a random advancement (supports add-ons)")
@app_commands.autocomplete(addon=addon_autocomplete)
@app_commands.describe(addon="Add-on to pick a random advancement from (leave blank to pick from the regular pack)")
async def random_advancement(interaction: discord.Interaction, addon: str | None):
    logging.info(f"/random command was ran by {interaction.user} ({interaction.user.id}) Input: {addon}")
    try:
        if addon == None:
            random_adv = advs[random.randrange(0, len(advs))]
            await generate_adv_embed(interaction, random_adv)
        elif addon in addon_list:
            random_adv = addon_advs[addon][random.randrange(0, len(addon_advs[addon]))]
            await generate_adv_embed(interaction, random_adv)
        else:
            embed = discord.Embed(
                title="Add-on Not Found!",
                description=f"*The add-on **{addon}** could not be found. Please try again.",
                color=0xff0000
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
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
    logging.info(f"/tab command was ran by {interaction.user} ({interaction.user.id}) Input {tab}")
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
    except Exception as e:
        color = 0xff0000
        logging.warning(e)

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
    view = button_logic(interaction.user, adv_pages, color, tab)

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
    "addon_advancement": "Display an advancement of your choice, from a BACAP add-on of your choice. Use the `/addon_advancement` command and type what add-on you want to find an advancement from, along with the advancement you want to find in the search field.",
    "doc & documentation": "Both commands will link you to any official BACAP documentation of your choice. Use the `/doc` or `/documentation` command and type what documentation you want to find in the search field.",
    "random": "Displays a random advancement (supports add-ons). Use the `/random` command and type the add-on you want to pick an advancement from, or leave it blank to pick from the regular pack.",
    "refresh_advancements": "Refreshes and reloads advancement spreadsheet data from Sheets API. You cannot run this command unless you are an **bot developer**.",
    "refresh_trophies": "Refreshes and reloads trophy spreadsheet data from Sheets API. You cannot run this command unless you are an **bot developer**.",
    "riddlemethis": "Displays steps on how to complete the \"Riddle Me This\" super challenge. Use `/riddlemethis` and type which step you want displayed in the search field.",
    "tab": "Lists all advancements from a tab of your choice. Use the `/tab` command and type what tab you want to list in the search field.",
    "update_world": "Displays information on how to upgrade BACAP to a newer version. Use the `/update_world` command.",
    "versions": "Displays an available BACAP version of your choice. Use the `/versions` command and type what version you want displayed in the search field."
}


# HELP AUTOCOMPLETE
async def help_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    results = []
    for result in dict(sorted({**sorted_help_commands, 'help': ''}.items())):
        if len(results) == 25:
            break
        help_name = result
        if help_name.lower().startswith(current.lower()):
            results.append(app_commands.Choice(name=help_name, value=help_name))

    for result in dict(sorted({**sorted_help_commands, 'help': ''}.items())):
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
    logging.info(f"/help command was ran by {interaction.user} ({interaction.user.id}) Input {help}")
    pictures = {
        "advancement": "help_command_advancement.png",
        "addon_advancement": "help_command_advancement.png",
        "doc & documentation": "help_command_doc.png",
        "help": "help_command_help.png",
        "random": "help_command_random.png",
        "refresh_advancements": "help_command_refresh_advancements.png",
        "refresh_trophies": "help_command_refresh_trophies.png",
        "riddlemethis": "help_command_riddle.png",
        "tab": "help_command_tab.png",
        "versions": "help_command_versions.png",
        "update_world": "help_command_update_world.png"
        }

    try:
        ephemeral = False
        embed = discord.Embed(
            title=f"The {help} Command",
            description=f"{sorted_help_commands[help]}",
            color=discord.Color.blurple()
        )

        image_name = pictures[help]
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            file = None
            embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /help command failed to display image. IMAGE FILE: {image_name}")

    except:
        ephemeral = True
        embed = discord.Embed(
            title="❌ Error!",
            description=f"Perhaps the archives are incomplete. There is no such option named *{help}*. Please try again with a valid option.",
            color=0xff0000
        )

        if help.lower() == 'help':
            searge_says = [
                'Yolo',
                f'/advancement revoke {interaction.user.display_name} only discord:understand_commands',
                'relay your query to the crew*http://e.gv/LiveInstant-Chat',
                f'/deop {interaction.user.display_name}',
                'Scoreboard deleted, commands blocked',
                'Contact helpdesk for help',
                f'/execute if entity @p[name={interaction.user.display_name},tag=noob]',
                '/trigger warning',
                'Oh my god, it\'s full of stats',
                f'/kill @p[name=!{bot.user.display_name}]',
                'Have you tried turning it off and on again?',
                'Sorry, no help today'
            ]
            embed.description = random.choice(searge_says)

        image_name = "command_failed.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            file = None
            embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /help command denied failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

    await interaction.response.send_message(embed=embed, ephemeral=ephemeral, file=file)


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
    "BACAP 1.18.1 (for MC 1.21.4)": "https://www.mediafire.com/file/uy0ayqql8eo6cot/BlazeandCave%2527s_Advancements_Pack_1.18.1.zip/file",
    "BACAP 1.18.2 (for MC 1.21.5)": "https://www.mediafire.com/file/h4zolq1ykgxum01/BlazeandCave%2527s_Advancements_Pack_1.18.2.zip/file",
    "BACAP 1.18.3 (for MC 1.21.5)": "https://www.mediafire.com/file/vyljk8r2vd1jjlm/BlazeandCave%2527s_Advancements_Pack_1.18.3.zip/file",
    "BACAP 1.19 (for MC 1.21.6)": "https://www.mediafire.com/file/kjihn47u1txundg/BlazeandCave%2527s_Advancements_Pack_1.19.zip/file",
    "BACAP 1.19.1 (for MC 1.21.7 or 1.21.8)": "https://www.mediafire.com/file/op98gugusyx3d9j/BlazeandCave%2527s_Advancements_Pack_1.19.1.zip/file"
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
async def version_command(interaction: discord.Interaction, version: str):
    logging.info(f"/versions command was ran by {interaction.user} ({interaction.user.id}) Input: {version}")

    try:
        ephemeral = False
        embed = discord.Embed(
            title=f"**{version}**",
            description=f"*⬇️ Version **{version}**'s download can be found here:*\n{version_dict[version]}",
            color=discord.Color.brand_green()
        )

        image_name = "versions.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            file = None
            embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /versions command failed to display image. IMAGE FILE: {image_name}")

    except:
        ephemeral = True
        embed = discord.Embed(
            title="❌ Error!",
            description=f"Perhaps the archives are incomplete. There are no versions matching *{version}*. Please try again with a valid option.",
            color=0xff0000
        )

        image_name = "command_failed.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            file = None
            embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /versions command denied failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

    await interaction.response.send_message(embed=embed,ephemeral=ephemeral, file=file)


## UPDATE COMMAND
@bot.tree.command(name="update_world", description="Displays a prompt on how to update your world when a new BACAP version releases.")
async def update_world_command(interaction: discord.Interaction):
    logging.info(f"/update_world command was ran by {interaction.user} ({interaction.user.id})")

    try:
        ephemeral = False
        image_name = "update_world.png"
        embed = discord.Embed(
            title="⬆️ Updating BACAP to a Newer Version",
            description="1️⃣ Leave your world for upmost safety and do not rejoin during the process. *If you are updating BACAP on a server, we recommend you plan for downtime.*\n"
                        "2️⃣ Make a backup of your world in case you screw up. *If the world is hosted on a server, save it either on the server's FTP or your computer.*\n"
                        "3️⃣ Delete the old datapacks **COMPLETELY** from your world.\n"
                        "4️⃣ Copy and paste in the new updated datapacks.\n"
                        "5️⃣ Go into your world.\n"
                        "6️⃣ If you **screwed up**, go to your backup, make a backup of your backup, then repeat __steps 3-6__ on the backup.",
            color=discord.Color.dark_blue()
        )

        image_name = "update_world.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /update_world command success failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

    except Exception as e:
        logging.error(f"{interaction.user} ({interaction.user.id})'s /update_world command produced ERROR: {e}")

        ephemeral = True
        embed = discord.Embed(
            title="❌ Error!",
            description=f"**Uh oh! An unknown error has occured!** *Please copy the error and report it to your server administrator.*\n**Error:** {e}",
            color=0xff0000
        )

        image_name = "command_failed.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            embed.add_field(name="❌ Image Error!",value="Image was not loaded properly!",inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /update_world command failure failed to display image. IMAGE FILE: {image_name} | URL: attachment://{file.filename}")

    await interaction.response.send_message(embed=embed, ephemeral=ephemeral, file=file)


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


## RIDDLE ME THIS COMMAND
@bot.tree.command(name="riddlemethis", description="Displays the solutions to each step in the \"Riddle Me This\" challenge.")
@app_commands.autocomplete(riddle=riddle_autocomplete)
@app_commands.describe(riddle="Which step you would like to display")
async def riddle_command(interaction: discord.Interaction, riddle: str):
    logging.info(f"/riddlemethis command was ran by {interaction.user} ({interaction.user.id}) Input: {riddle}")

    try:
        if riddle.lower() == "list all steps":
            steps = "\n".join(
                [f"**{key}:** {value}" for key, value in riddle_me_this_batman.items() if key != "List All Steps"])
            embed = discord.Embed(
                title="📜 Riddle Me This: All Steps",
                description=f"{steps}",
                color=discord.Color.dark_gold()
            )

            image_name = "riddlemethisbatman.png"
            if image_name in image_cache:
                file_path = image_cache[image_name]
                file = discord.File(file_path, filename=image_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")
            else:
                file = None
                embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
                logging.warning(f"{interaction.user} ({interaction.user.id})'s /riddlemethis command failed to display image. IMAGE FILE: {image_name}")

        else:
            step = riddle_me_this_batman.get(riddle)

            if step is None:
                embed = discord.Embed(
                    title="❌ Error!",
                    description=f"There is no such step as *{riddle}*. Please try again with a valid option.",
                    color=0xff0000,
                )

                image_name = "command_failed.png"
                if image_name in image_cache:
                    file_path = image_cache[image_name]
                    file = discord.File(file_path, filename=image_name)
                    embed.set_thumbnail(url=f"attachment://{file.filename}")
                else:
                    file = None
                    embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
                    logging.warning(f"{interaction.user} ({interaction.user.id})'s /riddlemethis command failed to display image. IMAGE FILE: {image_name}")

                await interaction.response.send_message(embed=embed, ephemeral=True, file=file)
                return

            embed = discord.Embed(
                title=f"📜 Riddle Me This: {riddle}",
                description=f"{step}",
                color=discord.Color.gold()
            )

            image_name = "riddlemethisbatman.png"
            if image_name in image_cache:
                file_path = image_cache[image_name]
                file = discord.File(file_path, filename=image_name)
                embed.set_thumbnail(url=f"attachment://{file.filename}")
            else:
                file = None
                embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
                logging.warning(f"{interaction.user} ({interaction.user.id})'s /riddlemethis command failed to display image. IMAGE FILE: {image_name}")

        await interaction.response.send_message(embed=embed, ephemeral=False, file=file)

    except Exception as e:
        logging.error(f"{interaction.user} ({interaction.user.id})'s /riddlemethis command with input: \"{riddle}\" produced ERROR: {e}")

        embed = discord.Embed(
            title="❌ Error!",
            description=f"**Uh oh! An unknown error has occurred!** *Please copy the error and report it to your server administrator.*\n**Error:** {e}",
            color=0xff0000
        )

        image_name = "command_failed.png"
        if image_name in image_cache:
            file_path = image_cache[image_name]
            file = discord.File(file_path, filename=image_name)
            embed.set_thumbnail(url=f"attachment://{file.filename}")
        else:
            file = None
            embed.add_field(name="❌ Image Error!", value="Image was not loaded properly!", inline=False)
            logging.warning(f"{interaction.user} ({interaction.user.id})'s /riddlemethis command failed to display image. IMAGE FILE: {image_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True, file=file)

# get token and RUN
with open("Text/token.txt") as file:
    token = file.read().strip()

bot.run(token)

# END

# ONE THOUSAND FOUR HUNDRED NINETY SEVEN


# ONE THOUSAND FIVE HUNDRED

# TWO THOUSAND ONE HUNDRED NINETY FOUR