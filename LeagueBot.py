# League Bot by Brandon He
import os
import discord
import json
from boto.s3.connection import S3Connection
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

#if running local
# from dotenv import load_dotenv
# load_dotenv()
# discordToken = os.getenv('discord')
# riotAPI = os.getenv('riot')

# global variables

s3 = S3Connection(os.environ['discord'], os.environ['riot'])

discordToken = os.environ['discord']
riotAPI = os.environ['riot']

watcher = LolWatcher(riotAPI)
region = 'na1'

# check league's latest version
latest = watcher.data_dragon.versions_for_region(region)['n']['champion']

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='test', help='see if the bot is running')
async def on_test(context):
	response = 'hello world'
	await context.send(response)


@bot.command(name='summonerInfo', help='display your summoner info')
async def on_summonerInfo(context, username):
	rawData = watcher.summoner.by_name(region, username)
	response = json.dumps(rawData, indent=4)
	await context.send(response)
	

@bot.command(name='rank', help='display your rank info')
async def on_rank(context, username):
	summoner = watcher.summoner.by_name(region, username)

	# returns a list where rawData[0] = flex rank, rawData[1] = solo/duo rank
	rawData = watcher.league.by_summoner(region, summoner['id'])
	
	flex = rawData[0]
	flex.pop('leagueId')
	flex.pop('summonerId')

	solo = rawData[1]
	solo.pop('leagueId')
	solo.pop('summonerId')

	prettyFlex = json.dumps(flex, indent=4)
	prettySolo = json.dumps(solo, indent=4)

	response = prettyFlex + '\n' + prettySolo
	await context.send(response)


bot.run(discordToken)
