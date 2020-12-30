# League Bot by Brandon He
import os
import discord
from boto.s3.connection import S3Connection
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

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


@bot.command(name='summonerInfo')
async def on_summonerInfo(context):
	response = watcher.summoner.by_name(region, 'BHe')
	await context.send(response)
	

@bot.command(name='rank')
async def on_rank(context):
	summoner = watcher.summoner.by_name(region, 'BHe')
	response = watcher.league.by_summoner(region, summoner['id'])
	await context.send(response)


bot.run(discordToken)
