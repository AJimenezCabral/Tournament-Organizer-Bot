from typing import List, Optional
import discord
from discord.app_commands.models import _to_locale_dict
from discord.components import SelectOption
from discord.ui import Select, View
from discord.ext import commands
import typing


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents = intents)

bot = commands.Bot(command_prefix = '!', intents = intents)

bot.remove_command("help")


Participants = []
max_size = {'size': 0, 'counter': 1}

@bot.group(invoke_without_command = True)
async def help(ctx):
    em = discord.Embed(title = "Help", description = "Use !help <command> for extended information")

    em.add_field(name = "Tournament Commands", value = "create, join, leave, entries, clear, winner")
    em.add_field(name = "Test Command", value = "bottles")

    await ctx.send(embed = em)


class MySelect(Select):  #Subclassing the "Select" class for the tournament winner drop down menu
    def __init__(self) -> None:
        super().__init__(
                placeholder = f"Choose a winner for {Participants[0]}:",
                min_values = 1,         #This is where you set the settings for the drop down menu: Placeholder is text to show while nothing is selected
                max_values = 1,         #min/max values affect how many options you need to/can have selected
                )
    async def callback(self, interaction):      #Callback functions trigger when an option is selected
        Select.disabled = True          #disables the drop down menu
        await interaction.response.send_message(f'The winner of {Participants[0]} is: {Participants[max_size["counter"] - 1].mention}!')        #Sends message when option is selected
        Participants.clear()
        max_size['size'] = 0
        max_size['counter'] = 1     #Resets values of tournament to 0

    
 
@bot.event
async def on_ready():
   print(f'We have logged in as {bot.user}')



@bot.command()
async def bottles(ctx, amount: typing.Optional[int] = 99, *, liquid = "beer"):
    await ctx.send(f'{amount} bottles of {liquid} on the wall!')

@bot.command()
async def create(ctx, size: typing.Optional[int] = 6, *, name = "King of the hill tournament"): #Initializes tournament by setting the maximum size of the tournament as well as the name of the tournament. Has defaults
    if (Participants != []):
        await ctx.send('There is a tournament already in play! Please either use !clear or !winner to clear or declare a winner and end the ongoing tournament')
    else:
        await ctx.send(f'Created the tournament "{name}" with a maximum size of {size} players')
        max_size['size'] = size + 1
        Participants.append(name)
    
@bot.command()
async def leave(ctx):
    if (Participants == []):
        await ctx.send('There is no ongoing tournament for you to leave!')
    elif (ctx.author in Participants):
        Participants.remove(ctx.author)
        await ctx.send('You have been removed from the ongoing tournament.')
    else:
        await ctx.send("You're not in the ongoing tournament!")

@bot.command()
async def join(ctx):
    if (len(Participants) >= max_size['size']):    # checks if maximum capacity for tournament has been reached
        await ctx.send(f'Maximum number of participants has been reached')

    elif (ctx.author in Participants):   #checks if user already registered
        await ctx.send(f'You have already registered for this tournament!')

    else:   #adds user to the list of participants and tags user to let them know and for easy bookkeeping
        await ctx.send(f'{ctx.author.mention} has been added to {Participants[0]}')
        Participants.append(ctx.author) #This appends a type member to the list. This means you can do all kinds of shit with each item on the list such as tag them or get their username
        if (max_size['size'] - len(Participants) > 1):
            await ctx.send(f'There are ' + str(max_size['size'] - len(Participants)) + ' spots left')
        else:
            await ctx.send(f'There is 1 spot left')
 
@bot.command()
async def entries(ctx):
    if len(Participants) < 1:
        await ctx.send('There is no tournament happening!')
    elif len(Participants) < 2:     #Cases for if the tournament doesn't really exist
        await ctx.send(f'There are no participants in {Participants[0]}!')
    else:
        await ctx.send(f'There are {len(Participants) - 1} entries. They are: ' + "".join(x.display_name for x in Participants[1:]))     #Creates list with users currently in the tournament and tags them.

@bot.command()
async def clear(ctx): #Command to clear the current tournament; Resets values of list and max size to 0
    Participants.clear()
    max_size['size'] = 0
    max_size['counter'] = 1
    await ctx.send(f'Tournament has been cleared')

@bot.command()
async def winner(ctx):
    if len(Participants) < 1:
        await ctx.send("There is no tournament!")
    elif len(Participants) < 3:       #Cases for if there aren't enough participants or the tournament doesn't exist       
        await ctx.send(f"Not enough participants in {Participants[0]}")
    else:
        select = MySelect()
        while (max_size['counter'] < len(Participants)):
            select.append_option(discord.SelectOption(label = Participants[max_size['counter']].display_name, description = f"Choose {Participants[max_size['counter']].display_name} as the winner!"))
            max_size['counter'] += 1
        view = View()
        view.add_item(select)
        await ctx.send(view = view)
    #await ctx.send("uhh?>?",view = SelectView())
#should make a command to declare a winner and clear the current tournament
#I want this to be a drop down menu

#############Help Commands below this################

 
@help.command()
async def create(ctx):
    
    em = discord.Embed(title = "create", description = "Creates a tournament", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!tournament [size] [name]")
    em.add_field(name = "**Information**", value = "Defaults to a max of 6 players and a name of 'King of the hill tournament' if no information is given")

    await ctx.send(embed = em)

@help.command()
async def leave(ctx):
    
    em = discord.Embed(title = "leave", description = "Removes the user from the ongoing tournament", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!leave")
    em.add_field(name = "**Information**", value = "Doesn't remove the user if there is no ongoing tournament at the moment")

    await ctx.send(embed = em)


@help.command()
async def join(ctx):
    
    em = discord.Embed(title = "join", description = "Adds the user to the ongoing tournament", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!join")
    em.add_field(name = "**Information**", value = "Doesn't add user if:\n1. Tournament is full\n2. User is already in the tournament\n3. Tournament doesn't exist")

    await ctx.send(embed = em)

@help.command()
async def entries(ctx):
    
    em = discord.Embed(title = "entries", description = "Returns a list of users currently in the ongoing tournament and how many total entries there are", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!entries")
    em.add_field(name = "**Information**", value = "Doesn't return a list of users if:\n1. Tournament doesn't exist\n2. Tournament doesn't have any entries")

    await ctx.send(embed = em)
 
@help.command()
async def clear(ctx):
    
    em = discord.Embed(title = "clear", description = "Clears the ongoing tournament of all information", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!clear")
    em.add_field(name = "**Information**", value = "Empties the ongoing tournament of all information. This command can be used at any time")

    await ctx.send(embed = em) 
 
@help.command()
async def winner(ctx):
    
    em = discord.Embed(title = "winner", description = "Allows the user to declare a winner and clears the current tournament", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!winner")
    em.add_field(name = "**Information**", value = "Creates a drop down menu to select the winner of the current tournament. This command can't be used if:\n1. There is no tournament\n2. There are less than 2 entries")

    await ctx.send(embed = em)   

@help.command()
async def bottles(ctx):
    
    em = discord.Embed(title = "bottles", description = "Tells you how many bottles are on the wall!", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = "!bottles [amount] [liquid]")
    em.add_field(name = "**Information**", value = "If the amount of bottles or the liquid isn't specified then they default to 99 and beer respectively")

    await ctx.send(embed = em)


f = open("Bot Token.txt", "r")
bot.run(f.read())
