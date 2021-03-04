import requests
import argparse
import sys
from time import sleep

class colors:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  WHITE = '\033[37m'
  UNDERLINE = '\033[4m'

def print_to_stdout(*a):  
    print(*a, file = sys.stdout) 

api_key_auth = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
riot_url = "https://esports-api.lolesports.com/persisted/gw"
headers = { "x-api-key": api_key_auth }
base_params = { "hl": "pt-BR" }

def get_live_events():
  sufix = "/getLive"
  response = get_response(sufix)
  events = response["data"]["schedule"]["events"]
  current_events = soon_events(events)
  print_live_events(current_events)
  return 1

def get_scheduled_events():
  sufix = "/getSchedule"
  response = get_response(sufix)
  events = response["data"]["schedule"]["events"]
  current_events = soon_events(events)
  print_live_events(current_events)
  return 1

def print_live_events(events):
  for event in events:
    print_to_stdout(f"\nLeague: {event['league']['name']}")
    print_to_stdout(f"{colors.RED}{event['match']['teams'][0]['name']} X {event['match']['teams'][1]['name']}{colors.ENDC}")
    if 'id' in event.keys():
      print_to_stdout(f"EventID: {colors.GREEN}{event['id']}{colors.ENDC}, state: {event['state']}")
    else:
      print_to_stdout(f"startTime: {event['startTime']}, state: {event['state']}")

def get_event_games(event_id):
  sufix = "/getEventDetails"
  extra_params = { "id": event_id }
  response = get_response(sufix, extra_params)
  match_info = response["data"]["event"]["match"] 
  teams = match_info["teams"]
  print_to_stdout(f"{colors.RED}{teams[0]['name']} X {teams[1]['name']}{colors.ENDC}")
  print_event_games(match_info["games"])
  return 1

def print_event_games(games):
  for game in games:
    game_color = colors.WHITE
    if game['state'] == 'inProgress':
      game_color = colors.GREEN
    print_to_stdout(f"{game_color}game_number: {game['number']}, game_ID: {game['id']}, state: {game['state']}{colors.ENDC}")

def watch_game(game_id):
  sufix = f"/window/{game_id}"
  response = get_response(sufix)
  not_started = True
  while not_started:
    if response.ok:
      not_started = False
    else:
      print_to_stdout("Game didnt start yet. trying again in a few seconds")
      sleep(10)
      response = get_response(sufix)

  patch_version = response["gameMetadata"]["patchVersion"]
  blue_team_info = { "participants": get_team_participants(response['gameMetadata']["blueTeamMetadata"], patch_version),
                     "team_name": get_team_name(response['gameMetadata']["blueTeamMetadata"])}
  red_team_info = { "participants": get_team_participants(response['gameMetadata']["redTeamMetadata"], patch_version),
                    "team_name": get_team_name(response['gameMetadata']["redTeamMetadata"])}
  teams = { "red": red_team_info, "blue": blue_team_info}

  game_state = "in_game"
  while game_state != "finished":
    sleep(3)
    sys.stdout.flush()
    game_info = get_game_info(game_id)
    print_game_info(game_info, teams)
    game_state = game_info["gameState"]
  print_to_stdout(f"{colors.RED}GAME ENDED{colors.ENDC}")
  return 1

def get_team_participants(teamData, patch_version):
  participants = teamData['participantMetadata']
  participants_dict = {}
  for participant in participants:
    participants_dict[participant['participantId']] = { "name": participant['summonerName'],
                                                        "champion": get_champ_name(participant['championID'], patch_version),
                                                        "role": participant['role'] }
  return participants_dict

def get_champ_name(champ_id, patch_version):
  response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{patch_version}/data/pt_BR/champion.json")
  champion_list = response.json()['data']
  for champion in champion_list:
    if champ_id == champion['key']:
      return champion['name']

def get_team_name(teamData):
  team_id = teamData['esportsTeamId']
  sufix = "/getTeams"
  params = { "id": team_id }
  response = get_response(sufix, params)
  team_info = response.json()["data"]["teams"][0]
  return team_info["name"]

def get_game_info(game_id):
  sufix = f"/window/{game_id}"
  response = get_response(sufix)
  return response.json()['frames']

def print_game_info(game_info, teams):
  print_to_stdout(f"{colors.BLUE}{teams['blue']['team_name']}{colors.ENDC}")
  print_team_info(game_info["blueTeam"], teams['blue']['participants'])
  print_to_stdout(f"{colors.RED}{teams['red']['team_name']}{colors.ENDC}")
  print_team_info(game_info["redTeam"], teams['red']['participants'])

def print_team_info(team_info, team_participants):
  for key in team_info.keys():
    if key == 'participants':
      print_participants_info(team_info['participants'], team_participants)
    else:
      print_to_stdout(f"  {key}: {team_info[key]}")
      print_to_stdout(f"  {colors.YELLOW}========================================================={colors.ENDC}")

def print_participants_info(participants_info, team_participants):
  for participant in participants_info:
    for key in participant.keys():
      if key == 'participantId':
        for extra_participant_info_keys in team_participants[participant['key']].keys():
          print_to_stdout(f"  {extra_participant_info_keys}: {participant[extra_participant_info_keys]}")  
      else:
        print_to_stdout(f"    {key}: {participant[key]}")

def soon_events(events):
  selected = []
  for event in events:
    if (event['state'] != 'completed' and event['type'] == 'match'):
      selected += [event]

  return selected

def get_response(sufix, data={}):
  url = riot_url + sufix
  params = { **base_params, **data }
  response = requests.get(url, headers=headers, params=params)
  if not response.ok:
    raise RuntimeError(f"Error when trying to request {url} with headers: {headers} and params: {params}")
  return response.json()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--scheduled", action="store_true", dest="get_scheduled_events", help="Get current scheduled esports events")
  parser.add_argument("-l", "--live", action="store_true", dest="get_live_events", help="Get current live esports events")
  parser.add_argument("-e", "--event", default="InvalidEventID", dest="get_event_games", help="Get event games given an event id")
  parser.add_argument("-g", "--game", default="InvalidGameID", dest="watch_game", help="Get game info repeatedly given game id")

  args = parser.parse_args()
  args = args.__dict__
  retcode = 1
  if args["get_live_events"]:
    retcode = get_live_events()
  elif args["get_scheduled_events"]:
    retcode = get_scheduled_events()
  elif args["get_event_games"]:
    retcode = get_event_games(args["get_event_games"])
  elif args["watch_game"]:
    retcode = watch_game(args["watch_game"])
  
  sys.exit(retcode)
