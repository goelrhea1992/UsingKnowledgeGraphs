# UsingKnowledgeGraphs

Akhil Lohchab (al3372)
----------------------
Rhea Goel     (rg2936)
----------------------

Files Submitted
---------------
	- run.sh
		Script to run the complete program as per the reference implementation
	- InfoBox.py
		Python script that executes both parts Infobox Creation, and Question Answering
	- helper.py
		Python script containing helper functions for Question Answering part
	- Transcript files
		- Part1_transcript
			Contains output for Infobox Creation queries
		- Part2_transcript
			Contains output for Question answering queries
	- Tabulate package
		Module used for infobox creation

Run Instructions
----------------
The complete program can be executed in one of the following ways:

	./run.sh -key <Freebase API key> -q <query> -t <infobox|question>
	./run.sh -key <Freebase API key> -f <file of queries> -t <infobox|question>
	./run.sh -key <Freebase API key>

Internal Design
---------------
- Part 1: Infobox Creation
---------------------------
	- All relevant entity types for the query are identified
	- For each entity type, the corresponding properties of interest are extracted 
	- Using the following mapping from Freebase properties to the entity properties of interest


   	| Type of Entity   |  Property of Interest          |  Freebase Property                                        |
	--------------------------------------------------------------------------------------------------------------
	| Person           | Name                           | /type/object/name                                        |
	|                  | Birthday                       | /people/person/date_of_birth                             |
	|                  | Place of Birth                 | /people/person/place_of_birth                            |
	|                  | Siblings                       | /people/person/sibling_s                                 |
	|                  | Spouses                        | /people/person/spouse_s                                  |
	|                  | Description                    | /common/topic/description                                |
	--------------------------------------------------------------------------------------------------------------
	| Author           | Books(Title)                   | /book/author/works_written                               |
	|                  | Book About the Author(Title)   | /book/book_subject/works                                 |
	|                  | Influenced                     | /influence/influence_node/influenced                     |
	|                  | Influenced by                  |                                                           |
	 -------------------------------------------------------------------------------------------------------------
	| Actor            | FilmsParticipated (Film)       | /film/performance/film                                   |
	|                  |                   (Name)       | /type/object/name                                        |
	|                  |                   (Character)  | /film/performance/character                              |
	 -------------------------------------------------------------------------------------------------------------
	| BusinessPerson   | Leadership  (From)             | /organization/leadership/from                            |
	|                  |             (To)               | /organization/leadership/to                              | 
	|                  |             (Organization)     | /organization/leadership/organization                    |
	|                  |             (Role)             | /organization/leadership/role                            |
	|                  |             (Title)            | /organization/leadership/title                           |
	|                  | BoardMember (From)             | /organization/organization_board_membership/from         |
	|                  |             (To)               | /organization/organization_board_membership/to           |
	|                  |             (Organization)     | /organization/organization_board_membership/organization |
	|                  |             (Role)             | /organization/organization_board_membership/role         |
	|                  |             (Title)            | /organization/organization_board_membership/title        |
	|                  | Founded     (OrganizationName) | /organization/organization_founder/organizations_founded |
	 --------------------------------------------------------------------------------------------------------------
	| League           | Name                           | /type/object/name                                        |
	|                  | Championship                   | /sports/sports_league/championship                       |
	|                  | Sport                          | /sports/sports_league/sport                              |
	|                  | Slogan                         | /organization/organization/slogan                        |
	|                  | OfficialWebsite                | /common/topic/official_website                           |
	|                  | Description                    | /common/topic/description                                |
	|                  | Teams                          | /sports/sports_league/teams                              |
	 --------------------------------------------------------------------------------------------------------------
	| SportsTeam       | Name                           | /type/object/name                                        |
	|                  | Description                    | /common/topic/description                                |
	|                  | Sport                          | /sports/sports_team/sport                                |
	|                  | Arena                          | /sports/sports_team/arena_stadium                        |
	|                  | Championships                  | /sports/sports_team/championships                        |
	|                  | Coaches       (Name)           | /sports/sports_team_coach_tenure/coach                   |
	|                  |               (Position)       | /sports/sports_team_coach_tenure/position                |
	|                  |               (From)           | /sports/sports_team_coach_tenure/from                    |
	|                  |               (To)             | /sports/sports_team_coach_tenure/to                      |
	|                  | Founded                        | /sports/sports_team/founded                              |
	|                  | Leagues                        | /sports/sports_team/league                               |
	|                  | Locations                      | /sports/sports_team/location                             |
	|                  | PlayersRoster (Name)           | /sports/sports_team_roster/player                        |
	|                  |               (Position)       | /sports/sports_team_roster/position                      |
	|                  |               (Number)         | /sports/sports_team_roster/number                        |
	|                  |               (From)           | /sports/sports_team_roster/from                          |
	|                  |               (To)             | /sports/sports_team_roster/to                            |
	 -------------------------------------------------------------------------------------------------------------

- Part 2: Question Answering
----------------------------------
This section answers questions of the form of 'Who created X?' where X could either be the name of a book or an organization (as specified in the problem statement). The author/founder of the subject in question was obtained by using the Freebase MQL read API where the following specific fields were used:

/organization/organization_founder/organization_founded for type BusinessPerson
/book/author/works_written for type Author

The output is then sorted alphabetically on the name of author/businessperson.

The main function responsible for this section is answerQuestion() in the helper class which can in two separate 
modes - one for standalone queries and one for the interactive mode which produces the results in a box just like the reference implementation.

Transcripts:
--------------
The transcripts are located in the following folders and include the corresponding files:

Part1_transcripts:
- billGates		: for ‘Bill Gates’
- RobertDowneyJr	: for ‘Robert Downey Jr.’
- Jackson		: for ‘Jackson’
- NFL			: for ‘NFL’
- NBA			: for ’NBA’
- NYKnicks		: for ‘NY Knicks’
- MiamiHeat		: for ‘MiamiHeat’


Part2_transcripts:
- Google.txt         : for 'Who Created Google'
- LoTR.txt           : for 'Who Created Lord of The Rings'
- Microsoft.rtf      : for 'Who Created Microsoft'
- romeoAndJuliet.txt : for 'Who Created Romeo And Juliet'
- box.txt            : for results of the above 4 questions in a box format.


Freebase API Key
----------------
AIzaSyDUcGzUl-GpF5IhwP3M7GZ_5ERBr-1NUIQ




