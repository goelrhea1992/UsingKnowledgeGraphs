import json
import pprint
import urllib
import io
import sys
import time
import datetime
import getpass


def html_table(lol):
	print '<table>'
	for sublist in lol:
		print '  <tr><td>'
		print '    </td><td>'.join(sublist)
		print '  </td></tr>'
		print '</table>'

def drawList(listData):
	for item in listData:
		if type(item)==dict:
			drawDict(item)
		elif type(item)==list:
			drawList(item)
		else:
			print '{0:10} {1:10}'.format('', item)

def drawDict(dictData):
	tab = '\t\t'
	for key, value in dictData.iteritems():

		if type(value)==list:
			drawList(value)
		elif type(value)==dict:
			drawDict(value)
		else:
			print '{0:13} {1:13}'.format(key+':', value)
	print

def drawInfoBox(info, allEntities):
	pprint.pprint(info)
	for key, value in info.iteritems():
		if isinstance(value,basestring):
		    printThis = value.encode('utf8')
		else:
		    printThis = unicode(value).encode('utf8')

		print '|{0:25}\t{1:80}|\n'.format(key+':', printThis),
		print '-'*170
        

	# 	if type(value)==list:
	# 		print '{0:10}'.format(key + ': '),
	# 		drawList(value)
	# 	elif type(value)==dict:
	# 		print '{0:10}'.format(key + ': ')
	# 		drawDict(value)
	# 	else:
	# 		print '{0:10}: {1:10}'.format(key, value)

def doStuff(query, api_key):
	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
	        'query': query,
	        'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	# pprint.pprint(response)
	foundSomething = False
	countMid = 0
	for result in response['result']:
		countMid = countMid + 1
		thisMid = result['mid']
		topic_url = 'https://www.googleapis.com/freebase/v1/topic' + thisMid
		params = {
	        	'key': api_key
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
	return allEntities

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
		if 'from' in temp.keys() and 'to' not in temp.keys():
			temp['to'] = 'now'
		if '/people/marriage/location_of_ceremony' in item['property'].keys():
			if item['property']['/people/marriage/location_of_ceremony']['values']:
				temp['Location'] = item['property']['/people/marriage/location_of_ceremony']['values'][0]['text']
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
	for item in propertyJson['values']:
		temp = {}
		if '/film/performance/character' in item['property'].keys():
			if item['property']['/film/performance/character']['values']:
				temp['Character'] = item['property']['/film/performance/character']['values'][0]['text']
		if '/film/performance/film' in item['property'].keys():
			if item['property']['/film/performance/film']['values']:
				temp['Film'] = item['property']['/film/performance/film']['values'][0]['text']
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
	for item in propertyJson['values']:
		temp = {}
		if '/tv/regular_tv_appearance/character' in item['property'].keys():
			if item['property']['/tv/regular_tv_appearance/character']['values']:
				temp['Character'] = item['property']['/tv/regular_tv_appearance/character']['values'][0]['text']
		if '/tv/regular_tv_appearance/series' in item['property'].keys():
			if item['property']['/tv/regular_tv_appearance/series']['values']:
				temp['TV Series'] = item['property']['/tv/regular_tv_appearance/series']['values'][0]['text']
		allTVSeries.append(temp)
	return allTVSeries

def getBoardMember(propertyJson):
	allBoardMember = []
	for item in propertyJson['values']:
		temp = {}
		if '/organization/organization_board_membership/organization' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/organization']['values']:
				temp['organization'] = item['property']['/organization/organization_board_membership/organization']['values'][0]['text']
		
		if '/organization/organization_board_membership/role' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/role']['values']:
				temp['role'] = item['property']['/organization/organization_board_membership/role']['values'][0]['text']

		if '/organization/organization_board_membership/title' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/title']['values']:
				temp['title'] = item['property']['/organization/organization_board_membership/title']['values'][0]['text']

		if '/organization/organization_board_membership/from' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/from']['values']:
				temp['from'] = item['property']['/organization/organization_board_membership/from']['values'][0]['text']

		if '/organization/organization_board_membership/to' in item['property'].keys():
			if item['property']['/organization/organization_board_membership/to']['values']:
				temp['to'] = item['property']['/organization/organization_board_membership/to']['values'][0]['text']
		if 'from' in temp.keys() and 'to' not in temp.keys():
			temp['to'] = 'now'
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
	for item in propertyJson['values']:
		temp = {}
		if '/organization/leadership/organization' in item['property'].keys():
			if item['property']['/organization/leadership/organization']['values']:
				temp['organization'] = item['property']['/organization/leadership/organization']['values'][0]['text']

		if '/organization/leadership/role' in item['property'].keys():
			if item['property']['/organization/leadership/role']['values']:
				temp['role'] = item['property']['/organization/leadership/role']['values'][0]['text']

		if '/organization/leadership/title' in item['property'].keys():
			if item['property']['/organization/leadership/title']['values']:
				temp['title'] = item['property']['/organization/leadership/title']['values'][0]['text']	

		if '/organization/leadership/from' in item['property'].keys():
			if item['property']['/organization/leadership/from']['values']:
				temp['from'] = item['property']['/organization/leadership/from']['values'][0]['text']		

		if '/organization/leadership/to' in item['property'].keys():
			if item['property']['/organization/leadership/to']['values']:
				temp['to'] = item['property']['/organization/leadership/to']['values'][0]['text']
		if 'from' in temp.keys() and 'to' not in temp.keys():
			temp['to'] = 'now'
		allLeadership.append(temp)
	return allLeadership

def getCoaches(propertyJson):
	allCoaches = []
	for item in propertyJson['values']:
		temp = {}
		if '/sports/sports_team_coach_tenure/coach' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/coach']['values']:
				temp['name'] = item['property']['/sports/sports_team_coach_tenure/coach']['values'][0]['text']

		if '/sports/sports_team_coach_tenure/position' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/position']['values']:
				temp['position'] = item['property']['/sports/sports_team_coach_tenure/position']['values'][0]['text']

		if '/sports/sports_team_coach_tenure/from' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/from']['values']:
				temp['from'] = item['property']['/sports/sports_team_coach_tenure/from']['values'][0]['text']		

		if '/sports/sports_team_coach_tenure/to' in item['property'].keys():
			if item['property']['/sports/sports_team_coach_tenure/to']['values']:
				temp['to'] = item['property']['/sports/sports_team_coach_tenure/to']['values'][0]['text']

		if 'from' in temp.keys() and 'to' not in temp.keys():
			temp['to'] = 'now'

		allCoaches.append(temp)
	return allCoaches

def getRoster(propertyJson):
	allRoster = []
	for item in propertyJson['values']:
		temp = {}
		if '/sports/sports_team_roster/player' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/player']['values']:
				temp['name'] = item['property']['/sports/sports_team_roster/player']['values'][0]['text']

		if '/sports/sports_team_roster/position' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/position']['values']:
				temp['position'] = item['property']['/sports/sports_team_roster/position']['values'][0]['text']
		
		if '/sports/sports_team_roster/number' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/number']['values']:
				temp['number'] = item['property']['/sports/sports_team_roster/number']['values'][0]['text']

		if '/sports/sports_team_roster/from' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/from']['values']:
				temp['from'] = item['property']['/sports/sports_team_roster/from']['values'][0]['text']		

		if '/sports/sports_team_roster/to' in item['property'].keys():
			if item['property']['/sports/sports_team_roster/to']['values']:
				temp['to'] = item['property']['/sports/sports_team_roster/to']['values'][0]['text']

		if 'from' in temp.keys() and 'to' not in temp.keys():
			temp['to'] = 'now'
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
	python InfoBox.py [API_Key] -q [query] 
	python InfoBox.py [API_Key] -f [file of queries]
	python InfoBox.py [API_Key]

	"""
def interactiveInfoBox(api_key):
	print 'Welcome to infoxbox creator using Freebase knowledge graph.'
	print 'Feel curious? Start exploring...'
	print

	while True:
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
		print '['+st+']',
		query = raw_input(getpass.getuser()+'@fb_ibox> ')
		doStuff(query, api_key)

if __name__ == "__main__":

	print len(sys.argv)
	for item in sys.argv:
		print item

	if len(sys.argv)!=2 and len(sys.argv)!=4: # Expect exactly one argument: the api_key
		usage()
		sys.exit(2)	
	else:
		api_key =  sys.argv[1].strip('\'')
		if len(sys.argv)==2:
			interactiveInfoBox(api_key)
		elif sys.argv[2]=='-q':
			query = sys.argv[3].strip('\'')
			doStuff(query, api_key)
		elif sys.argv[2]=='-f':
			f = open(sys.argv[3].strip('\''))
			while f:
				query = f.readline()
				if query:
					doStuff(query, api_key)
				else:
					sys.exit(2)

			

	

