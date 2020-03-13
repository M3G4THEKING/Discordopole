import discord
import asyncio

from discord.ext import tasks, commands
from datetime import datetime, date

from discordopole import get_area
from util.mondetails import details
import util.queries as queries

class Boards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board_loop.start()

    @tasks.loop(seconds=2.0)   
    async def board_loop(self):      
        for board in self.bot.boards['raids']:
            try:
                channel = await self.bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(board["message_id"])
                area = get_area(board["area"])
                text = ""
                raids = await queries.get_active_raids(self.bot.config, area[0], board["levels"], board["timezone"], board['ex'])
                if not raids:
                    text = self.bot.locale["empty_board"]
                else:
                    length = 0
                    for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form in raids:
                        end = datetime.fromtimestamp(end).strftime(self.bot.locale['time_format_hm'])
                        if len(name) >= 30:
                            name = name[0:27] + "..."
                        ex_emote = ""
                        if ex == 1:
                            ex_emote = f"{self.bot.custom_emotes['ex_pass']} "
                        form_letter = ""
                        if str(mon_id) in self.bot.forms:
                            if str(form) in self.bot.forms[str(mon_id)]:
                                form_letter = f"{self.bot.forms[str(mon_id)][str(form)][0]} "
                        
                        if not mon_id is None and mon_id > 0:
                            mon_name = details.id(mon_id, self.bot.config['language'])
                            if move_1 > self.bot.max_moves_in_list:
                                move_1 = "?"
                            else:
                                move_1 = self.bot.moves[str(move_1)]["name"]
                            if move_2 > self.bot.max_moves_in_list:
                                move_2 = "?"
                            else:
                                move_2 = self.bot.moves[str(move_2)]["name"]

                            entry = f"{ex_emote}**{name}**: {self.bot.locale['until']} {end}\n**{mon_name}** {form_letter}- *{move_1} / {move_2}*\n\n"
                            if length + len(entry) >= 2048:
                                break
                            else:
                                text = text + entry
                                length = length + len(entry)
                        
                embed = discord.Embed(title=board['title'], description=text, timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:              
                print(err)
                print("Error while updating Raid Board. Skipping it.")
                await asyncio.sleep(5)
            
        for board in self.bot.boards['eggs']:
            try:
                channel = await self.bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(board["message_id"])
                area = get_area(board["area"])
                text = ""
                raids = await queries.get_active_raids(self.bot.config, area[0], board["levels"], board["timezone"], board['ex'])
                if not raids:
                    text = self.bot.locale["empty_board"]
                else:
                    length = 0
                    for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form in raids:
                        start = datetime.fromtimestamp(start).strftime(self.bot.locale['time_format_hm'])
                        end = datetime.fromtimestamp(end).strftime(self.bot.locale['time_format_hm'])
                        if len(name) >= 30:
                            name = name[0:27] + "..."
                        ex_emote = ""
                        if ex == 1:
                            ex_emote = f"{self.bot.custom_emotes['ex_pass']} "
                        if mon_id is None or mon_id == 0:
                            egg_emote = self.bot.custom_emotes[f"raid_egg_{level}"]
                            entry = f"{egg_emote} {ex_emote}**{name}**: {start}  –  {end}\n"
                            if length + len(entry) >= 2048:
                                break
                            else:
                                text = text + entry
                                length = length + len(entry)
                    
                embed = discord.Embed(title=board['title'], description=text, timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:
                print(err)
                print("Error while updating Egg Board. Skipping it.")
                await asyncio.sleep(5)
        
        for board in self.bot.boards['stats']:
            try:
                channel = await self.bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(board["message_id"])
                area = get_area(board["area"])
                text = ""

                if "mon_active" in board['type']:
                    mon_active = await queries.statboard_mon_active(self.bot.config, area[0])
                    if not "mon_today" in board['type']:
                        text = f"{text}{self.bot.custom_emotes['pokeball']} **{mon_active[0][0]:,}** {self.bot.locale['active_pokemon']}\n\n"

                if "mon_today" in board['type']:
                    mon_today = await queries.statboard_mon_today(self.bot.config, area[0])
                    if "mon_active" in board['type']:
                        text = f"{text}{self.bot.custom_emotes['pokeball']} **{mon_active[0][0]:,}** {self.bot.locale['active_pokemon']} | **{mon_today[0][0]:,}** {self.bot.locale['today']}\n\n"
                    else:
                        text = f"{text}{self.bot.custom_emotes['pokeball']} **{mon_today[0][0]:,}** {self.bot.locale['pokemon_seen_today']}\n\n"
                
                if "gym_amount" in board['type']:
                    gym_amount = await queries.statboard_gym_amount(self.bot.config, area[0])
                    text = f"{text}{self.bot.custom_emotes['gym_white']} **{gym_amount[0][0]:,}** {self.bot.locale['total_gyms']}\n"

                if "raid_active" in board['type']:
                    raid_active = await queries.statboard_raid_active(self.bot.config, area[0])
                    if not "egg_active" in board['type']:
                        text = f"{text}{self.bot.custom_emotes['raid']} **{raid_active[0][0]:,}** {self.bot.locale['active_raids']}\n"

                if "egg_active" in board['type']:
                    egg_active = await queries.statboard_egg_active(self.bot.config, area[0])
                    if "raid_active" in board['type']:
                        text = f"{text}{self.bot.custom_emotes['raid']} **{raid_active[0][0]:,}** {self.bot.locale['active_raids']} | **{egg_active[0][0]:,}** {self.bot.locale['eggs']}\n"
                    else:
                        text = f"{text}{self.bot.custom_emotes['raid_egg_1']} **{egg_active[0][0]:,}** {self.bot.locale['active_eggs']}\n"
                
                if "gym_teams" in board['type']:
                    gym_teams = await queries.statboard_gym_teams(self.bot.config, area[0])
                    text = f"{text}{self.bot.custom_emotes['gym_blue']}**{gym_teams[0][1]}**{self.bot.custom_emotes['blank']}{self.bot.custom_emotes['gym_red']}**{gym_teams[0][2]}**{self.bot.custom_emotes['blank']}{self.bot.custom_emotes['gym_yellow']}**{gym_teams[0][3]}**\n"

                if "stop_amount" in board['type']:
                    stop_amount = await queries.statboard_stop_amount(self.bot.config, area[0])
                    text = f"{text}\n{self.bot.custom_emotes['pokestop']} **{stop_amount[0][0]:,}** {self.bot.locale['total_stops']}\n"

                if "quest_active" in board['type']:
                    quest_active = await queries.statboard_quest_active(self.bot.config, area[0])
                    text = f"{text}🔎 **{quest_active[0][0]:,}** {self.bot.locale['quests']}"
                    if "stop_amount" in board['type']:
                        quest_ratio = int(round((quest_active[0][0] / stop_amount[0][0] * 100), 0))
                        text = f"{text} ({quest_ratio}%)"
                    text = text + "\n"

                if "grunt_active" in board['type']:
                    grunt_active = await queries.statboard_grunt_active(self.bot.config, area[0])
                    if not "leader_active" in board['type']:
                        text = f"{text}{self.bot.custom_emotes['grunt_female']} **{grunt_active[0][0]:,}** {self.bot.locale['active_grunts']}"

                if "leader_active" in board['type']:
                    leader_active = await queries.statboard_leader_active(self.bot.config, area[0])
                    if "grunt_active" in board['type']:
                        text = f"{text}{self.bot.custom_emotes['grunt_female']} **{grunt_active[0][0]:,}** {self.bot.locale['grunts']} | {self.bot.custom_emotes['cliff']} **{leader_active[0][0]:,}** {self.bot.locale['leaders']}"
                    else:
                        text = f"{text}{self.bot.custom_emotes['cliff']} **{leader_active[0][0]:,}** {self.bot.locale['leaders']}"

                    
                embed = discord.Embed(title=board['title'], description=text.replace(",", self.bot.locale['decimal_comma']), timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:
                print(err)
                print("Error while updating Stat Board. Skipping it.")
                await asyncio.sleep(5)

    @board_loop.before_loop
    async def before_boards(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Boards(bot))