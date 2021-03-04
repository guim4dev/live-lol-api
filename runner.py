import requests
import argparse
import sys

class colors:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
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
  current_events = only_in_progress(events)
  print_live_events(current_events)
  return 1

def print_live_events(events):
  for event in events:
    print_to_stdout(f"League: {event['league']['name']}")
    print_to_stdout(f"{colors.RED}{event['match']['teams'][0]['name']} X {event['match']['teams'][1]['name']}{colors.ENDC}")
    print_to_stdout(f"EventID: {colors.GREEN}{event['id']}{colors.ENDC}, state: {event['state']}")

def get_event_games(event_id):
  sufix = "/getEventDetails"
  extra_params = { "id": event_id }
  response = get_response(sufix, extra_params)
  match_info = response["data"]["event"]["match"] 
  teams = match_info["teams"]
  print_to_stdout(f"{teams[0]['name']} X {teams[1]['name']}")
  games = match_info["games"]
  print_to_stdout(games)
  return 1

def watch_game(game_id):
  return 1

def only_in_progress(events):
  selected = []
  for event in events:
    if (event["state"] == "inProgress"):
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
  parser.add_argument("-gle", "--getliveevents", action="store_true", dest="get_live_events", help="Get current live esports events")
  parser.add_argument("-geg", "--geteventgames", default="InvalidEventID", dest="get_event_games", help="Get event games given an event id")
  parser.add_argument("-wg", "--watchgame", default="InvalidGameID", dest="watch_game", help="Get game info given game id")

  args = parser.parse_args()
  args = args.__dict__
  retcode = 1
  if args["get_live_events"]:
    retcode = get_live_events()
  elif args["get_event_games"]:
    retcode = get_event_games(args["get_event_games"])
  elif args["watch_game"]:
    retcode = watch_game(args["watch_game"])
  
  sys.exit(retcode)
