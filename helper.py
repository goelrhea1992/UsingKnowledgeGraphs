__author__ = 'akhil'

import json
import sys
import urllib2
import urllib
import re
from collections import defaultdict

def getJSONResults(QueryWords,apiKey):
  """
  create query and retrieve the results
  """

  Query = '%20'.join(QueryWords)

  Url = 'https://www.googleapis.com/freebase/v1/search?query=%27' + Query + '%27&key=' + apiKey

  reques = urllib2.Request(Url)
  response = urllib2.urlopen(reques)
  content = response.read()
  jsonData = json.loads(content)

  return jsonData

def answerQuestion(query, apiKey, mode):
  """
    helper function for the question queries
     
  The function takes the BING results, and formulates the MQL query which in turn fetches the appropriate
   
   results
  """
  
  QueryWords = query.split(' ')
  Quesdata =  getJSONResults(QueryWords, apiKey)
  
  # Types of queries
  OrgQuery = [{
	"/organization/organization_founder/organizations_founded": [{
		"a:name": None,
		"name~=": query
	}],
	"id": None,
	"name": None,
	"type": "/organization/organization_founder"
        }]

  BookQuery = [{"/book/author/works_written": [{
		"a:name": None,
		"name~=": query
	}],
	"id": None,
	"name": None,
	"type": "/book/author"
        }]
  
  
  Results_dict = {}
  Bp = defaultdict(list)
  Auth = defaultdict(list)

  # Check if book or Org and add to appropriate dictionaries
  try:
   DataTerm = Quesdata['result'][0]['mid']
  except:
    print 'No matches found.....Exiting'
    sys.exit()
      
  TopicUrl = 'https://www.googleapis.com/freebase/v1/topic'+str(DataTerm)+'?key=' + apiKey
  request = urllib2.Request(TopicUrl)
  response = urllib2.urlopen(request)
  content = response.read()
  detail = json.loads(content)
  AllCategories = []
  
  for Curr_Categ in detail['property']['/type/object/type']['values']:
    AllCategories.append(Curr_Categ['id'])

#  print AllCategories

  if '/organization/organization' or '/organization/organization_founder' in AllCategories:
    NewQuery = OrgQuery
    params = {
          'query': json.dumps(NewQuery),
          'key': apiKey
    }
    service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
    url = service_url + '?' + urllib.urlencode(params)
    response = json.loads(urllib.urlopen(url).read())

    for result in response['result']:
      Results_dict[result["name"]] = "(as BusinessPerson) created "
      for org in result['/organization/organization_founder/organizations_founded']:
        Results_dict[result["name"]] += '<' + org['a:name'] + '>' + ', '
        Bp[result["name"]].append(org['a:name'])

#      print result['name']

  if '/book/author' or '/book/book' in AllCategories:
    NewQuery = BookQuery
    params = {
          'query': json.dumps(NewQuery),
          'key': apiKey
    }
    service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
    url = service_url + '?' + urllib.urlencode(params)
    response = json.loads(urllib.urlopen(url).read())

    for result in response['result']:
      if result["name"] in Results_dict.keys():
        Results_dict[result["name"]] += "and (as Author) created "
      else:
        Results_dict[result["name"]] = "(as Author) created "
      for book in result['/book/author/works_written']:
        Results_dict[result["name"]] += '<' + book['a:name'] + '>' + ', '

        Auth[result["name"]].append(book['a:name'])
    # print Auth
#    print result['name']

  if mode==1:

      count = 1
      for key in sorted(Results_dict.keys()):
        print str(count) + '. ' + key + ' ' + Results_dict[key][:-2]
        count += 1

      if len(Results_dict.keys())==0:
          print "It seems no one created ["+query+"]!!!"

  elif mode==2:
      print "\t -------------------------------------------------------------------------------------------------- "
      lQuery = 13+len(query)
      numBlanks = 98-lQuery
      if numBlanks%2==0:
          numBlanks2 = numBlanks/2
          numBlanks -= numBlanks2
      else:
          numBlanks2 = numBlanks/2
          numBlanks -= numBlanks2
      print '\t|' + (' '*numBlanks) +'Who Created '+query+'?'+(' '*numBlanks) + '|'
      print "\t -------------------------------------------------------------------------------------------------- "

      if len(Results_dict.keys())!=0:

          maxl = max([len(n) for n in Results_dict.keys()])
          col1 = maxl+2
          col23 = (96 - col1)/2

          # print maxl
          # print Bp['Steve Wozniak']
          for key in sorted(Results_dict.keys()):
              print  '\t| ' + key + ':'+ ' '*(col1-len(key))+'|As ' + ' '*(col23-3)+'| Creation' + ' '*(col23 - 10) +'|'
              print "\t -------------------------------------------------------------------------------------------------- "
              Prefix_1 = ' '*(col1+2) +'|'
              if key in Bp.keys():
                  temp = Bp[key][0]
                  if len(temp)>col23-2:
                      print "\t|" +Prefix_1 +"BusinessPerson" + ' '*(col23-14)+'| ' +temp[0:col23-6]+'...'+' '*(col23 - len(Bp[key][0])-2) + '|'
                  else:
                      print "\t|" +Prefix_1 +"BusinessPerson" + ' '*(col23-14)+'| ' +temp+' '*(col23 - len(Bp[key][0])-2) + '|'

                  for creations in Bp[key][1:]:
                    if len(creations)>col23-2:
                        print "\t|" +Prefix_1 + ' '*(col23)+'| ' +creations[0:col23-6]+'... '+' '*(col23 - len(creations)-2) + '|'

                    else:
                        print "\t|" +Prefix_1 + ' '*(col23)+'| ' +creations+' '*(col23 - len(creations)-2) + '|'


              if key in Auth.keys():
                  temp = Auth[key][0]
                  if len(temp)>col23-2:
                      print "\t|" +Prefix_1 +"Author" + ' '*(col23-6)+'| ' +temp[0:col23-6]+'... '+' '*(col23 - len(Auth[key][0])-2) + '|'

                  else:

                    print "\t|" +Prefix_1 +"Author" + ' '*(col23-6)+'| ' +temp+' '*(col23 - len(Auth[key][0])-2) + '|'

                  for creations in Auth[key][1:]:
                    if len(creations)>col23-2:
                        print "\t|" +Prefix_1 + ' '*(col23)+'| ' +creations[0:col23-6]+'... '+' '*(col23 - len(creations)-2) + '|'

                    else:
                        print "\t|" +Prefix_1 + ' '*(col23)+'| ' +creations+' '*(col23 - len(creations)-2) + '|'
              print "\t -------------------------------------------------------------------------------------------------- "








