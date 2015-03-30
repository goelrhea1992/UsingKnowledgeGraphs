import json
import pprint
import urllib
import io
import re
import sys
import time
import datetime
import getpass
from tabulate import tabulate
import textwrap
from textwrap import TextWrapper
import getopt
import helper

priorityWords = ['Organization', 'Name', 'Character']

def getPrintValue(value):
	if isinstance(value,basestring):
		valuePrint = value.encode('utf8')
	else:
		valuePrint = unicode(value).encode('utf8')
	return valuePrint

def drawInfoBox(info, allEntities):
	print
	print
	introString = info['Name']+' ('
	first = True
	for entity in allEntities:
		if first:
			introString = introString + entity
			first = False
		else:
			introString = introString + ', '+entity
	introString = introString + ')'
	wrapper = TextWrapper()
	wrapper.initial_indent = ' '*2
	wrapper.subsequent_indent = ' '*30
	wrapper.dedent = True
	wrapper.width = 150
	print wrapper.fill(introString)
	print wrapper.fill('-'*(len(introString)))
	print
	for key, value in info.iteritems():
		valuePrint = getPrintValue(value)
		valuePrint = valuePrint.decode('utf-8')
		columnString = '{0:25}:  '.format(key)
		if type(value)==unicode:
			print wrapper.fill(columnString+valuePrint)
			print wrapper.fill('-'*(wrapper.width-2))

	for key, value in info.iteritems():
		valuePrint = getPrintValue(value)
		valuePrint = valuePrint.decode('utf-8')
		columnString = '{0:25}:  '.format(key)
		if type(value)==list:
			if all(isinstance(x,unicode) for x in value):
				firstVal = value[0]
				print wrapper.fill(columnString+firstVal)
				wrapper.initial_indent = ' '*30
				print wrapper.fill('\n'.join(value[1:]))
				wrapper.initial_indent = ' '*2
				print wrapper.fill('-'*(wrapper.width-2))

	for key, value in info.iteritems():
		valuePrint = getPrintValue(value)
		valuePrint = valuePrint.decode('utf-8')
		columnString = '{0:25}:  '.format(key)
		if type(value)==list:
			if all(isinstance(x,dict) for x in value):
				table = []
				temp = []

				if key=='Spouses':
					if value:
						first = True
						for item in value:
							if first:
								if item['Location']!=' ':
									print wrapper.fill(columnString+item['Name']+' (' + item['From'] + ' - '+item['To'] + ') @ ' + item['Location'])
								else:
									print wrapper.fill(columnString+item['Name']+' (' + item['From'] + ' - '+item['To'] + ')')
								first = False
							else:
								wrapper.initial_indent = ' '*30
								if item['Location']!=' ':
									print wrapper.fill(item['Name']+' (' + item['From'] + ' - '+item['To'] + ') @ ' + item['Location'])
								else:
									print wrapper.fill(item['Name']+' (' + item['From'] + ' - '+item['To'] + ')')
								wrapper.initial_indent = ' '*2
					print wrapper.fill('-'*(wrapper.width-2))
	
	for key, value in info.iteritems():
		valuePrint = getPrintValue(value)
		valuePrint = valuePrint.decode('utf-8')
		columnString = '{0:25}:  '.format(key)
		if type(value)==list:
			if all(isinstance(x,dict) for x in value):
				table = []
				temp = []
				if key!='Spouses':			
					for item in value:
						b = [getPrintValue(i).strip().decode('utf-8') for i in item.keys()]
						temp = list(set(temp) | set(b))
					foundFT = False
					for word in priorityWords:
						if word in temp:
							temp.remove(word)
							temp.insert(0, word)
					if 'From' in temp:
						temp.remove('From')
						temp.remove('To')
						foundFT = True
					if foundFT:
						temp.append('From/To')
					table.append(temp)
					print temp

					for item in value:
						temp2 = []
						for key2 in temp:
							if key2 in item.keys():
								valuePrint = getPrintValue(item[key2])
								valuePrint = valuePrint.decode('utf-8')
								temp2.append(valuePrint)
							elif key2=='From/To':
								value1 = getPrintValue(item['From'])
								value2 = getPrintValue(item['To'])
								valuePrint = value1 + ' / ' + value2
								valuePrint = valuePrint.decode('utf-8')
								temp2.append(valuePrint)
							else:
								temp2.append(' ')
						table.append(temp2)
					print table
					x = tabulate(table, tablefmt="grid", headers = "firstrow")
					if wrapper.width < len(x.split('\n')[0].encode('utf8')) + 27:
						wrapper.width = len(x.split('\n')[0].encode('utf8')) + 27
					first = True
					for row in x.split('\n'):
						if first:
							print wrapper.fill(columnString+row)
							first = False
						else:
							wrapper.initial_indent = ' '*30
							print wrapper.fill(row)
							wrapper.initial_indent = ' '*2
					print wrapper.fill('-'*(wrapper.width-2))
	print

def doStuff(query, apiKey):
	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
			'query': query,
			'key': apiKey
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	foundSomething = False
	countMid = 0
	for result in response['result']:
		countMid = countMid + 1
		thisMid = result['mid']
		topic_url = 'https://www.googleapis.com/freebase/v1/topic' + thisMid
		params = {
				'key': apiKey
		}
		url2 = topic_url + '?' + urllib.urlencode(params)
		response2 = json.loads(urllib.urlopen(url2).read())
		allEntities = getEntities(response2)
		info = {}
		if allEntities:
			for entityFound in allEntities:
				getInfo(entityFound, response2, result, info)
		if info:
			foundSomething = True
			break
		else:
			if countMid%5==0:
				print str(countMid)+' Search API result entries were considered. None of them of a supported type.'
				if countMid==20:
					print 'No related information about query ['+query+'] was found!'
					break
	if foundSomething:
		drawInfoBox(info, allEntities)

def getEntities(response):
	allProperites = response['property']
	allEntities = []
	for key in allProperites.keys():
		thisKey = str(key)
		if thisKey.startswith('/people/person'):
			allEntities.append('Person')
		if thisKey.startswith('/book/author'):
			allEntities.append('Author')
		if thisKey.startswith('/film/actor') or thisKey.startswith('/tv/tv_actor'):
			allEntities.append('Actor')
		if thisKey.startswith('/organization/organization_founder') or thisKey.startswith('/business/board_member'):
			allEntities.append('BusinessPerson')
		if thisKey.startswith('/sports/sports_league'):
			allEntities.append('League')
		if thisKey.startswith('/sports/sports_team') or thisKey.startswith('/sports/professional_sports_team'):
			allEntities.append('SportsTeam')		
	return list(set(allEntities))

def getDOB(propertyJson):
	return propertyJson['values'][0]['text']

def getPOB(propertyJson):
	return propertyJson['values'][0]['text']

def getSlogan(propertyJson):
	return propertyJson['values'][0]['text']

def getOfficialWebsite(propertyJson):
	return propertyJson['values'][0]['text']

def getSport(propertyJson):
	return propertyJson['values'][0]['text']

def getArena(propertyJson):
	return propertyJson['values'][0]['text']

def getFoundedYear(propertyJson):
	return propertyJson['values'][0]['text']

def getSiblings(propertyJson):
	allSiblings = []
	for item in propertyJson['values']:
		if '/people/sibling_relationship/sibling' in item['property'].keys():
			if item['property']['/people/sibling_relationship/sibling']['values']:
				allSiblings.append(item['property']['/people/sibling_relationship/sibling']['values'][0]['text'])
	return allSiblings

def getSpouses(propertyJson):
	allSpouses = []
	neededArgs = ['Name', 'From', 'To', 'Location']
	for item in propertyJson['values']:
		temp = {}
		if '/people/marriage/spouse' in item['property'].keys():
			if item['property']['/people/marriage/spouse']['values']:
				temp['Name'] = item['property']['/people/marriage/spouse']['values'][0]['text']
		if '/people/marriage/from' in item['property'].keys():
			if item['property']['/people/marriage/from']['values']:
				temp['From'] = item['property']['/people/marriage/from']['values'][0]['text']
		if '/people/marriage/to' in item['property'].keys():
			if item['property']['/people/marriage/to']['values']:
				temp['To'] = item['property']['/people/marriage/to']['values'][0]['text']
		if 'From' in temp.keys() and 'To' not in temp.keys():
			temp['To'] = 'now'
		if '/people/marriage/location_of_ceremony' in item['property'].keys():
			if item['property']['/people/marriage/location_of_ceremony']['values']:
				temp['Location'] = item['property']['/people/marriage/location_of_ceremony']['values'][0]['text']
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allSpouses.append(temp)
	return allSpouses

def getBooksAbout(propertyJson):
	allBooksAbout = []
	for item in propertyJson['values']:
		allBooksAbout.append(item['text'])
	return allBooksAbout

def getBooksWritten(propertyJson):
	allBooksWritten = []
	for item in propertyJson['values']:
		allBooksWritten.append(item['text'])
	return allBooksWritten

def getInfluenced(propertyJson):
	allInfluenced = []
	for item in propertyJson['values']:
		allInfluenced.append(item['text'])
	return allInfluenced

def getFilms(propertyJson):
	allFilms = []
	neededArgs = ['Character', 'Film']
	for item in propertyJson['values']:
		temp = {}
		if '/film/performance/character' in item['property'].keys():
			if item['property']['/film/performance/character']['values']:
				temp['Character'] = item['property']['/film/performance/character']['values'][0]['text']
		if '/film/performance/film' in item['property'].keys():
			if item['property']['/film/performance/film']['values']:
				temp['Film'] = item['property']['/film/performance/film']['values'][0]['text']
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allFilms.append(temp)
	return allFilms

def getLeagues(propertyJson):
	allLeagues = []
	for item in propertyJson['values']:
		temp = {}
		if '/sports/sports_league_participation/league' in item['property'].keys():
			if item['property']['/sports/sports_league_participation/league']['values']:
				allLeagues.append(item['property']['/sports/sports_league_participation/league']['values'][0]['text'])
	return allLeagues

def getTVSeries(propertyJson):
	allTVSeries = []
	neededArgs = ['Character', 'TV Series']
	for item in propertyJson['values']:
		temp = {}
		if '/tv/regular_tv_appearance/character' in item['property'].keys():
			if item['property']['/tv/regular_tv_appearance/character']['values']:
				temp['Character'] = item['property']['/tv/regular_tv_appearance/character']['values'][0]['text']
		if '/tv/regular_tv_appearance/series' in item['property'].keys():
			if item['property']['/tv/regular_tv_appearance/series']['values']:
				temp['TV Series'] = item['property']['/tv/regular_tv_appearance/series']['values'][0]['text']
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allTVSeries.append(temp)
	return allTVSeries

def getBoardMember(propertyJson):
	allBoardMember = []
	neededArgs = ['Organization', 'Role', 'Title', 'From', 'To']
	for item in propertyJson['values']:
		temp = {}
		if '/organization/organization_board_membership/organization' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/organization']['values']:
				temp['Organization'] = item['property']['/organization/organization_board_membership/organization']['values'][0]['text']
		
		if '/organization/organization_board_membership/role' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/role']['values']:
				temp['Role'] = item['property']['/organization/organization_board_membership/role']['values'][0]['text']

		if '/organization/organization_board_membership/title' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/title']['values']:
				temp['Title'] = item['property']['/organization/organization_board_membership/title']['values'][0]['text']

		if '/organization/organization_board_membership/from' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/from']['values']:
				temp['From'] = item['property']['/organization/organization_board_membership/from']['values'][0]['text']

		if '/organization/organization_board_membership/to' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/to']['values']:
				temp['To'] = item['property']['/organization/organization_board_membership/to']['values'][0]['text']
		if 'From' in temp.keys() and 'To' not in temp.keys():
			temp['To'] = 'now'
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allBoardMember.append(temp)
	return allBoardMember

def getFounded(propertyJson):
	allFounded = []
	for item in propertyJson['values']:
		allFounded.append(item['text'])
	return allFounded

def getLocation(propertyJson):
	allLocations = []
	for item in propertyJson['values']:
		allLocations.append(item['text'])
	return allLocations

def getLeadership(propertyJson):
	allLeadership = []
	neededArgs = ['Organization', 'Role', 'Title', 'From', 'To']
	for item in propertyJson['values']:
		temp = {}
		if '/organization/leadership/organization' in item['property'].keys():
			if item['property']['/organization/leadership/organization']['values']:
				temp['Organization'] = item['property']['/organization/leadership/organization']['values'][0]['text']

		if '/organization/leadership/role' in item['property'].keys():
			if item['property']['/organization/leadership/role']['values']:
				temp['Role'] = item['property']['/organization/leadership/role']['values'][0]['text']

		if '/organization/leadership/title' in item['property'].keys():
			if item['property']['/organization/leadership/title']['values']:
				temp['Title'] = item['property']['/organization/leadership/title']['values'][0]['text']	

		if '/organization/leadership/from' in item['property'].keys():
			if item['property']['/organization/leadership/from']['values']:
				temp['From'] = item['property']['/organization/leadership/from']['values'][0]['text']		

		if '/organization/leadership/to' in item['property'].keys():
			if item['property']['/organization/leadership/to']['values']:
				temp['To'] = item['property']['/organization/leadership/to']['values'][0]['text']
		if 'From' in temp.keys() and 'To' not in temp.keys():
			temp['To'] = 'now'
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allLeadership.append(temp)
	return allLeadership

def getCoaches(propertyJson):
	allCoaches = []
	neededArgs = ['Name', 'Position', 'From', 'To']
	for item in propertyJson['values']:
		temp = {}
		if '/sports/sports_team_coach_tenure/coach' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/coach']['values']:
				temp['Name'] = item['property']['/sports/sports_team_coach_tenure/coach']['values'][0]['text']

		if '/sports/sports_team_coach_tenure/position' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/position']['values']:
				temp['Position'] = item['property']['/sports/sports_team_coach_tenure/position']['values'][0]['text']

		if '/sports/sports_team_coach_tenure/from' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/from']['values']:
				temp['From'] = item['property']['/sports/sports_team_coach_tenure/from']['values'][0]['text']		

		if '/sports/sports_team_coach_tenure/to' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/to']['values']:
				temp['To'] = item['property']['/sports/sports_team_coach_tenure/to']['values'][0]['text']

		if 'From' in temp.keys() and 'To' not in temp.keys():
			temp['To'] = 'now'
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allCoaches.append(temp)
	return allCoaches

def getRoster(propertyJson):
	allRoster = []
	neededArgs = ['Name', 'Position', 'Number', 'From', 'To']
	for item in propertyJson['values']:
		temp = {}
		if '/sports/sports_team_roster/player' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/player']['values']:
				temp['Name'] = item['property']['/sports/sports_team_roster/player']['values'][0]['text']

		if '/sports/sports_team_roster/position' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/position']['values']:
				temp['Position'] = item['property']['/sports/sports_team_roster/position']['values'][0]['text']
		
		if '/sports/sports_team_roster/number' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/number']['values']:
				temp['Number'] = item['property']['/sports/sports_team_roster/number']['values'][0]['text']

		if '/sports/sports_team_roster/from' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/from']['values']:
				temp['From'] = item['property']['/sports/sports_team_roster/from']['values'][0]['text']		

		if '/sports/sports_team_roster/to' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/to']['values']:
				temp['To'] = item['property']['/sports/sports_team_roster/to']['values'][0]['text']

		if 'From' in temp.keys() and 'To' not in temp.keys():
			temp['To'] = 'now'
		for arg in neededArgs:
			if arg not in temp.keys():
				temp[arg] = ' '
		allRoster.append(temp)
	return allRoster

def getChampionship(propertyJson):
	allChampionship = []
	for item in propertyJson['values']:
		allChampionship.append(item['text'])
	return allChampionship

def getTeams(propertyJson):
	allTeams = []
	for item in propertyJson['values']:
		if '/sports/sports_league_participation/team' in item['property'].keys():
			if item['property']['/sports/sports_league_participation/team']['values']:
				allTeams.append(item['property']['/sports/sports_league_participation/team']['values'][0]['text'])
	return allTeams

def getInfo(entityFound, response, result, info):
	allProperites = response['property']
	if 'name' not in info.keys():
		info['Name'] = allProperites['/type/object/name']['values'][0]['text']

	if entityFound == 'Person':
		for thisProperty in allProperites.keys():
			if thisProperty.startswith('/people/person/date_of_birth'):
				info['Date of Birth'] = getDOB(allProperites[thisProperty])
			if thisProperty.startswith('/people/person/place_of_birth'):
				info['Place of Birth'] = getPOB(allProperites[thisProperty])
			if thisProperty.startswith('/people/person/sibling_s'):
				info['Siblings'] = getSiblings(allProperites[thisProperty])
			if thisProperty.startswith('/people/person/spouse_s'):
				info['Spouses'] = getSpouses(allProperites[thisProperty])

	elif entityFound == 'Author':
		for thisProperty in allProperites.keys():
			if thisProperty.startswith('/book/book_subject/works'):
				info['Books About'] = getBooksAbout(allProperites[thisProperty])
			if thisProperty.startswith('/book/author/works_written'):
				info['Books Written'] = getBooksWritten(allProperites[thisProperty])
			if thisProperty.startswith('/influence/influence_node/influenced'):
				info['Influenced'] = getInfluenced(allProperites[thisProperty])

	elif entityFound == 'Actor':
		for thisProperty in allProperites.keys():
			if thisProperty.startswith('/film/actor/film'):
				info['Films Participated'] = getFilms(allProperites[thisProperty])
			if thisProperty.startswith('/tv/tv_actor/starring_roles'):
				info['TV Series Participated'] = getTVSeries(allProperites[thisProperty])

	elif entityFound == 'BusinessPerson':
		for thisProperty in allProperites.keys():
			if thisProperty.startswith('/business/board_member/organization_board_memberships'):
				info['Board Member'] = getBoardMember(allProperites[thisProperty])
			if thisProperty.startswith('/organization/organization_founder/organizations_founded'):
				info['Founded'] = getFounded(allProperites[thisProperty])
			if thisProperty.startswith('/business/board_member/leader_of'):
				info['Leadership'] = getLeadership(allProperites[thisProperty])

	elif entityFound == 'League':
		for thisProperty in allProperites.keys():
			if thisProperty.startswith('/sports/sports_league/sport'):
				info['Sport'] = getSport(allProperites[thisProperty])
			if thisProperty.startswith('/common/topic/official_website'):
				info['Official Website'] = getOfficialWebsite(allProperites[thisProperty])
			if thisProperty.startswith('/organization/organization/slogan'):
				info['Slogan'] = getSlogan(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_league/championship'):
				info['Championship'] = getChampionship(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_league/teams'):
				info['Teams'] = getTeams(allProperites[thisProperty])
			

	elif entityFound == 'SportsTeam':
		for thisProperty in allProperites.keys():
			if thisProperty.startswith('/sports/sports_team/location'):
				info['Location'] = getLocation(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_team/sport'):
				info['Sport'] = getSport(allProperites[thisProperty])	
			if thisProperty.startswith('/sports/sports_team/coaches'):
				info['Coaches'] = getCoaches(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_team/arena_stadium'):
				info['Arena'] = getArena(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_team/league'):
				info['Leagues'] = getLeagues(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_team/founded'):
				info['Founded'] = getFoundedYear(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_team/championships'):
				info['Championships'] = getChampionship(allProperites[thisProperty])
			if thisProperty.startswith('/sports/sports_team/roster'):
				info['Player Roster'] = getRoster(allProperites[thisProperty])
	
	if '/common/topic/description' in allProperites.keys():
		if allProperites['/common/topic/description']['values']:
			info['Description'] = allProperites['/common/topic/description']['values'][0]['value']

def usage():
	print """ Usage:
	python InfoBox.py [apiKey] -q [query] 
	python InfoBox.py [apiKey] -f [file of queries]
	python InfoBox.py [apiKey]

	"""

def printHelp():
    print "HELP!"

def interactiveInfoBox(apiKey):
	print 'Welcome to infoxbox creator using Freebase knowledge graph.'
	print 'Feel curious? Start exploring...'
	print

	while True:
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
		print '['+st+']',
		query = raw_input(getpass.getuser()+'@fb_ibox> ')

		pattern = 'Who created ([\w\s.-]+)\?*'
		match = re.search(pattern, query, re.IGNORECASE)
		if match:
			query = match.group(1)
			helper.answerQuestion(query, apiKey)
		else:
			doStuff(query, apiKey)

if __name__ == "__main__":

	if len(sys.argv)!=3 and len(sys.argv)!=7: # Expect exactly one argument: the apiKey
		usage()
		sys.exit(2)	
	else:
		try:
			opts, arguments = getopt.getopt(sys.argv[1:],"f:hq:t:",["key="])
		except getopt.GetoptError:
			printHelp()
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				printHelp()
				sys.exit()
			elif opt == '-f':
				queryFile = arg.strip('\'')
			elif opt == '-q':
				query = arg
			elif opt == '-t':
				task = arg
			elif opt == "--key":
				apiKey = arg

		if len(sys.argv)==3:
			interactiveInfoBox(apiKey)

		elif sys.argv[3]=='-q':
			if task=='infobox':
				doStuff(query, apiKey)
			else:
				print 'Question: ' + query
				pattern = 'Who created ([\w\s.-]+)\?*'
				match = re.search(pattern, query, re.IGNORECASE)
				if match:
					query = match.group(1)
					helper.answerQuestion(query, apiKey)

		elif sys.argv[3]=='-f':
			f = open(queryFile)
			while f:
				query = f.readline()
				if query:
					if task=='infobox':
						doStuff(query, apiKey)
					else:
						print 'Question: ' + query
						pattern = 'Who created ([\w\s.-]+)\?*'
						match = re.search(pattern, query, re.IGNORECASE)
						if match:
							query = match.group(1)
							helper.answerQuestion(query, apiKey)
				else:
					sys.exit(2)


			

	

