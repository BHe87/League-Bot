# League Bot by Brandon He
import os
import discord
import json
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


    # "id": "ZdQ0DDubuMSlf01Jsb7pwa90N4wIuWiU0qRSLg2oy7W5UuY",
    # "accountId": "FzkJaZd8rI8nIjimVR26dMF47ZDFelaC9zENN6VjdTUsZDA",
    # "puuid": "SWjCRqZ8cUHfHMnS4gonCU9xocBFh5cNcJTej5MokKA_tqsJUxTrR8csvNKL5nCfAtx9E9jiePn-KQ",
    # "name": "BHe",
    # "profileIconId": 4693,
    # "revisionDate": 1609204798000,
    # "summonerLevel": 144
@bot.command(name='summonerInfo', help='display useless summoner info')
async def on_summonerInfo(context, username):
	rawData = watcher.summoner.by_name(region, username)
	response = json.dumps(rawData, indent=4)

	await context.send(response)
	

@bot.command(name='rank', help='display your rank info')
async def on_rank(context, username):
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
async def on_championMastery(context, username):
	summoner = watcher.summoner.by_name(region, username)
	mastery = watcher.champion_mastery.by_summoner(region, summoner['id'])
	sortedMasteryDesc = sorted(mastery, key = lambda i: i['championPoints'], reverse=True)
	top = sortedMasteryDesc[:5]

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

	response = json.dumps(top, indent=4)
	
	await context.send(response)


bot.run(discordToken)
