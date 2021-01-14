# League Bot by Brandon He
import os
import discord
import json
import datetime
import sqlite3
import psycopg2
from boto.s3.connection import S3Connection
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

# if running local
# from dotenv import load_dotenv
# load_dotenv()
# discordToken = os.getenv('discord')
# riotAPI = os.getenv('riot')
# databaseURL = os.getenv('db')

# if running Heroku
s3 = S3Connection(os.environ['discord'], os.environ['riot'])
discordToken = os.environ['discord']
riotAPI = os.environ['riot']
databaseURL = os.environ['db']


connection = psycopg2.connect(databaseURL, sslmode='require')
print('connected to database')
cursor = connection.cursor()

table = """CREATE TABLE IF NOT EXISTS players (
		SummonerName varchar(255) PRIMARY KEY,
	 	PrimaryRole varchar(255),
	 	SecondaryRole varchar(255),
	 	Saturday varchar(255),
	 	Sunday varchar(255),
	 	Team int
 	);"""

cursor.execute(table)
connection.commit()

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


@bot.command(name='Caddfull', help='add a player to the clash pool with full info in this format:\
									Summoner Name, Primary Role, Secondary Role, Free on Saturday, Free on Sunday')
async def on_clashAddFull(context, *arguments):
	primary = arguments[-4]
	secondary = arguments[-3]
	sat = arguments[-2]
	sun = arguments[-1]
	username = ''
	for x in arguments[:-4]:
		username += x + ' '
	username = username[:-1]

	print(username, primary, secondary, sat, sun,)

	query = """INSERT INTO players (SummonerName, PrimaryRole, SecondaryRole, Saturday, Sunday, Team)
			VALUES ('{username}', '{primary}', '{secondary}', '{sat}', '{sun}', -1)
			ON CONFLICT (SummonerName) DO UPDATE SET PrimaryRole='{primary}', SecondaryRole='{secondary}', Saturday='{sat}', Sunday='{sun}'
			WHERE players.SummonerName='{username}';"""\
			.format(username=username, primary=primary, secondary=secondary, sat=sat, sun=sat)
	cursor.execute(query)
	row = cursor.fetchone()
	connection.commit()

	title  = 'Added {username} to the Clash pool'.format(username=username)
	description = '%s, Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s' % (row[0], row[1], row[2], row[3], row[4])

	embed = discord.Embed(title=title, description=description)

	await context.send(embed=embed)


@bot.command(name='Cadd', help='add a player to the clash pool')
async def on_clashAdd(context, *arguments):
	username = ''
	for x in arguments:
		username += x + ' '
	username = username[:-1]

	query = """INSERT INTO players(SummonerName, PrimaryRole, SecondaryRole, Saturday, Sunday, Team)
			VALUES('{username}', 'NA', 'NA', 'no', 'no', -1)
			ON CONFLICT DO NOTHING RETURNING *;"""\
			.format(username=username)
	cursor.execute(query)
	row = cursor.fetchone()
	connection.commit()

	title  = "Added '{username}' to the Clash pool".format(username=username)
	description = '%s, Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s' % (row[0], row[1], row[2], row[3], row[4])

	embed = discord.Embed(title=title, description=description)

	await context.send(embed=embed)


@bot.command(name='Cprimary', help='set your primary role')
async def on_clashPrimary(context, *arguments):
	role = arguments[-1]
	username = ''
	for x in arguments[:-1]:
		username += x + ' '
	username = username[:-1]

	query = """UPDATE players SET PrimaryRole = '{role}'
			WHERE SummonerName = '{username}' RETURNING *;"""\
			.format(username=username, role=role)
	cursor.execute(query)
	row = cursor.fetchone()
	connection.commit()

	title  = "Set {username}'s primary role to {role}".format(username=username, role=role)
	description = '%s, Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s' % (row[0], row[1], row[2], row[3], row[4])

	embed = discord.Embed(title=title, description=description)

	await context.send(embed=embed)


@bot.command(name='Csecondary', help='set your secondary role')
async def on_clashSecondary(context, *arguments):
	role = arguments[-1]
	username = ''
	for x in arguments[:-1]:
		username += x + ' '
	username = username[:-1]

	query = """UPDATE players SET SecondaryRole = '{role}'
			WHERE SummonerName = '{username}' RETURNING *;"""\
			.format(username=username, role=role)
	cursor.execute(query)
	row = cursor.fetchone()
	connection.commit()

	title  = "Set {username}'s secondary role to {role}".format(username=username, role=role)
	description = '%s, Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s' % (row[0], row[1], row[2], row[3], row[4])

	embed = discord.Embed(title=title, description=description)

	await context.send(embed=embed)


@bot.command(name='CSat', help='set your availability to clash on Saturday')
async def on_clashSaturday(context, *arguments):
	free = arguments[-1]
	username = ''
	for x in arguments[:-1]:
		username += x + ' '
	username = username[:-1]

	query = """UPDATE players SET Saturday = '{free}' 
			WHERE SummonerName = '{username}' RETURNING *;"""\
			.format(username=username, free=free)
	cursor.execute(query)
	row = cursor.fetchone()
	connection.commit()

	title  = "Set {username}'s Saturday availability to {free}".format(username=username, free=free)
	description = '%s, Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s' % (row[0], row[1], row[2], row[3], row[4])

	embed = discord.Embed(title=title, description=description)

	await context.send(embed=embed)


@bot.command(name='CSun', help='set your availability to clash on Sunday')
async def on_clashSaturday(context, *arguments):
	free = arguments[-1]
	username = ''
	for x in arguments[:-1]:
		username += x + ' '
	username = username[:-1]

	query = """UPDATE players SET Sunday = '{free}'
			WHERE SummonerName = '{username}' RETURNING *;"""\
			.format(username=username, free=free)
	cursor.execute(query)
	row = cursor.fetchone()
	connection.commit()

	title  = "Set {username}'s Sunday availability to {free}".format(username=username, free=free)
	description = '%s, Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s' % (row[0], row[1], row[2], row[3], row[4])

	embed = discord.Embed(title=title, description=description)

	await context.send(embed=embed)


@bot.command(name='Cplayers', help='displays all players in the clash pool')
async def on_clashPlayers(context):
	query = """SELECT * FROM players;"""
	cursor.execute(query)
	players = cursor.fetchall()

	embed = discord.Embed(title='All Players', description='')

	for row in players:
		info = "Primary: %s, Secondary: %s, Saturday: %s, Sunday: %s" % (row[1], row[2], row[3], row[4])
		embed.add_field(name=row[0], value=info, inline=False)

	await context.send(embed=embed)


@bot.command(name='Cremove', help='removes a player from the clash pool')
async def on_clashRemove(context, *arguments):
	username = ''
	for x in arguments:
		username += x + ' '
	username = username[:-1]

	query = """DELETE FROM players WHERE SummonerName = '{username}';"""\
			.format(username=username)
	cursor.execute(query)
	connection.commit()

	title = "Removed '{username}' from the clash pool".format(username=username)
	embed = discord.Embed(title=title, description='')

	await context.send(embed=embed)


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
async def on_rank(context, *arguments):
	mode = arguments[-1]
	username = ''
	for x in arguments[:-1]:
		username += x + ' '

	summoner = watcher.summoner.by_name(region, username)

	# returns a list where rawData[0] = flex rank, rawData[1] = solo/duo rank
	rawData = watcher.league.by_summoner(region, summoner['id'])
	
	embed = discord.Embed(title='Current ' + mode + ' Rank: ', description='')

	if mode == 'solo':
		try:
			rawData = rawData[1]
		except IndexError:
			await context.send(username + ' is not ranked in this queue')
	elif mode == 'flex':
		try:
			rawData = rawData[0]
		except IndexError:
			await context.send(username + ' is not ranked in this queue')
	else:
		await context.send('something went wrong')
		
	rawData.pop('queueType')
	rawData.pop('leagueId')
	rawData.pop('summonerId')
	wins = rawData['wins']
	losses = rawData['losses']
	rawData['winrate'] = str(100 * (float)(wins/(wins+losses))) + '%'

	keys = ''
	for key in rawData.keys():
		keys += '\n' + key

	values = ''
	for value in rawData.values():
		values += '\n' + str(value)

	embed.add_field(name='_', value=keys)
	embed.add_field(name='_', value=values)
	embed.set_author(name=username, icon_url='')

	await context.send(embed=embed)


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

	embed = discord.Embed(title='Champion Mastery: ', description='')

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
		keys = ''
		for key in champion.keys():
			keys += '\n' + key

		values = ''
		for value in champion.values():
			values += '\n' + str(value)

		embed.add_field(name='_', value=keys)
		embed.add_field(name='_', value=values)

	embed.set_author(name=username, icon_url='')

	await context.send(embed=embed)


@bot.command(name='test', help='see if the bot is running')
async def on_test(context):
	response = 'hello world'

	await context.send(response)


bot.run(discordToken)
