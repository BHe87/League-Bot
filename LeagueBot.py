# League Bot by Brandon He
import os
import discord
import json
import datetime
from boto.s3.connection import S3Connection
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

# if running local
# from dotenv import load_dotenv
# load_dotenv()
# discordToken = os.getenv('discord')
# riotAPI = os.getenv('riot')


# if running Heroku
s3 = S3Connection(os.environ['discord'], os.environ['riot'])
discordToken = os.environ['discord']
riotAPI = os.environ['riot']


watcher = LolWatcher(riotAPI)
region = 'na1'

# champion info
champVersions = watcher.data_dragon.versions_for_region(region)['n']['champion']
ddragon = watcher.data_dragon.champions(champVersions)# dict of dict of dict
champions = ddragon['data']# dict of champions -> dict of champ data

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='test', help='see if the bot is running')
async def on_test(context):
	response = 'hello world'

	await context.send(response)


@bot.command(name='summonerInfo', help='display useless summoner info')
async def on_summonerInfo(context, *arguments):
	username = ''
	for x in arguments:
		username += x + ' '
	username = username[:-1]

	rawData = watcher.summoner.by_name(region, username)
	response = json.dumps(rawData, indent=4)

	await context.send(response)
	

@bot.command(name='rank', help='display your rank info')
async def on_rank(context, *arguments):# * operator allows for a variable # of arguments
	username = ''
	for x in arguments:
		username += x + ' '
	username = username[:-1]

	summoner = watcher.summoner.by_name(region, username)

	# returns a list where rawData[0] = flex rank, rawData[1] = solo/duo rank
	rawData = watcher.league.by_summoner(region, summoner['id'])
	
	response = ''
	for queueType in rawData:
		queueType.pop('leagueId')
		queueType.pop('summonerId')
		response += '\n' + json.dumps(queueType, indent=4)

	await context.send(response)


@bot.command(name='championMastery', help='display your top 5 champion mastery')
async def on_championMastery(context, *arguments):
	username = ''
	for x in arguments:
		username += x + ' '
	username = username[:-1]

	summoner = watcher.summoner.by_name(region, username)
	mastery = watcher.champion_mastery.by_summoner(region, summoner['id'])
	sortedMasteryDesc = sorted(mastery, key = lambda i: i['championPoints'], reverse=True)
	top = sortedMasteryDesc[:5]

	response = ''
	for champion in top:
		champId = champion['championId']
		for c in champions:
			cur = champions[c]
			if cur['key'] == str(champId):
				champion['name'] = c

		champion.pop('championId')
		champion.pop('championPointsSinceLastLevel')
		champion.pop('championPointsUntilNextLevel')
		champion.pop('chestGranted')
		champion.pop('tokensEarned')
		champion.pop('summonerId')
		time = champion['lastPlayTime']
		champion['lastPlayTime'] = datetime.datetime.fromtimestamp(float(time)/1000).strftime('%H:%M %m-%d-%Y')
		response += '\n' + json.dumps(champion, indent=4)
	
	await context.send(response)


bot.run(discordToken)
