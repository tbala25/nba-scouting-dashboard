"""
NBA Data Pipeline
Author: Tejas Bala
"""
import logging
from icecream import ic
#ic.configureOutput(includeContext=True)

ic.disable()

import datetime
from dateutil import tz

import os
import json
import requests
import time
import boto3

import sys
sys.path.insert(0, '../utils')
from mysql_conn import *
import slack_hooks

#########################################
##AWS Boto Connections
#########################################

aws_key = os.getenv('aws_access_key_id')
aws_secret = os.getenv('aws_secret_access_key')
aws_bucket = os.getenv('aws_bucket')

s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)


#########################################
## Helper Functions
#########################################

def convert_utc_est(date_string):
    """Convert string time from UTC to EST
    Parameters:
        date_string: string date in the format: "2021-03-31T02:00:00+00:00"
    """
    from__utc_zone = tz.gettz('UTC')
    to_est_zone = tz.gettz('America/New_York')

    utc = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S+00:00')
    # Tell the datetime object that it's in UTC time zone since datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from__utc_zone)
    # Convert time zone
    eastern = utc.astimezone(to_est_zone)
    eastern_string = eastern.strftime('%Y-%m-%dT%H:%M:%S')
    return(eastern_string)


def find(element, json):
    """Find element from nested dictionary
    Parameters:
        element: string path to element with keys separated by '.' ('games.home.alias')
        json: dictionary to query
    """
    keys = element.split('.')
    rv = json
    for key in keys:
        rv = rv[key]
    return rv

def replace_dict_val(d):
    """Replace None from dictionary
    Parameters:
        d: dictionary
    """
    for k,v in d.items():
        if v is None:
            d[k] = 0
        elif type(v) is list:
            for item in v:
                if type(item) is dict:
                    item = replace_dict_val(item)
        elif type(v) is dict:
            v = replace_dict_val(v)
    return d



##############################################
## 
##############################################

def get_endpoint(keys, ENDPOINT_MAP, api_key):
    """Get SPORTRADAR endpoint URL"""
    uri_base = ENDPOINT_MAP['uri_base']
    return os.path.join(uri_base, *map(str, keys)).replace("\\","/") + f'?api_key={api_key}'


def get_data(endpoint, params, ENDPOINT_MAP, api_key):
    """Get raw data from SPORTRADAR endpoint"""
    uri = ic(get_endpoint(ENDPOINT_MAP[endpoint]['fn_get_keys'](**params), ENDPOINT_MAP, api_key))
    result = ic(requests.get(uri))
    if result.status_code != 200:
        time.sleep(1)
        result = ic(requests.get(uri))
    data = json.loads(result.text)
    result.close()
    return data


def insert_data(endpoint, raw_data, params, ENDPOINT_MAP):
    """Insert raw data into table"""

    s3_dir = ENDPOINT_MAP[endpoint]['s3_dir']
    file_replace = ENDPOINT_MAP[endpoint]['file_replace']

    row_id = params['row_id']

    if file_replace:
        s3.delete_object(Bucket='sportradar-nba-pipeline', Key=s3_dir+str(row_id)+'.json')
    
    raw_data_na_replaced = replace_dict_val(raw_data)
    s3.put_object(Bucket='sportradar-nba-pipeline', Key=s3_dir+str(row_id)+'.json',Body=(bytes(json.dumps(raw_data_na_replaced).encode('UTF-8'))))


def extract_and_load(endpoint, params, ENDPOINT_MAP, api_key, raw_data_key=None, reporting_keys = None, load=True):
    """Extract raw data from the specified endpoint and load into S3"""
    #endpoint_type = ENDPOINT_MAP[endpoint]['endpoint_type']
    raw_data = ic(get_data(endpoint, params, ENDPOINT_MAP, api_key))
    
    if raw_data_key is not None:
        if raw_data[raw_data_key] == [] or raw_data[raw_data_key] is None or len(raw_data[raw_data_key]) == 0:
          load = False

    if load:
        reporting_message = ''
        if reporting_keys is not None:
            for rk in reporting_keys:
                if rk == 'scheduled':
                    converted_time = convert_utc_est(find(rk, raw_data))
                    appending = converted_time[:10]
                else:
                    appending = find(rk, raw_data)

                reporting_message += f'{appending}/'

        if raw_data_key is None:
            ic(insert_data(endpoint, raw_data, params, ENDPOINT_MAP))
        else:
            ic(insert_data(endpoint, raw_data[f'{raw_data_key}'], params, ENDPOINT_MAP))

        if endpoint == 'pbp':
            parse_pbp(raw_data)

        return reporting_message

    else:
        return raw_data


def parse_pbp(raw_data):

    events_parsed_arr = []
    game_parsed_arr = []

    game_id = raw_data.get('id')
    game_attendance = raw_data.get('attendance')
    game_scheduled = raw_data.get('scheduled')
    home_name = raw_data.get('home').get('name')
    home_alias = raw_data.get('home').get('alias')
    home_id = raw_data.get('home').get('id')
    home_reference = raw_data.get('home').get('reference')
    away_name = raw_data.get('away').get('name')
    away_alias = raw_data.get('away').get('alias')
    away_id = raw_data.get('away').get('name')
    away_reference = raw_data.get('away').get('name')

    periods = raw_data.get('periods')
    try:
        periods_num = len(periods)
    except:
        periods_num = 0

    game_scheduled_est = convert_utc_est(game_scheduled)

    game_parsed_arr.append(
        [
            game_id,
            game_attendance,
            game_scheduled_est,
            home_name,
            home_alias,
            home_id,
            home_reference,
            away_name,
            away_alias,
            away_id,
            away_reference,
            periods_num
        ]
    )

    # games
    delete_statement = f"""DELETE FROM nba_parsed_game where game_id = '{game_id}'"""
    cur.execute(delete_statement)
    conn.commit()

    query = """INSERT INTO nba_parsed_game VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"""
    for row in game_parsed_arr:
        row_0 = [str(s).replace("'", "") for s in row]
        filled_query = (query % tuple(row_0)).replace("'None'", "NULL")
        cur.execute(filled_query)
    conn.commit()

    # delete pre existing dup pbp
    delete_statement = f"""DELETE FROM parsed_pbp where game_id = '{game_id}'"""
    cur.execute(delete_statement)
    conn.commit()

    if periods is not None:
        for period in periods:
            
            period_number = period.get('number')
            period_events = period.get('events')

            if period_events is not None:

                for event in period_events:

                    event_id = event.get('id')
                    event_clock = event.get('clock_decimal')
                    event_description = event.get('description')
                    event_wall_clock = event.get('wall_clock')
                    event_type = event.get('event_type')
                    event_qualifiers = event.get('qualifiers')
                    event_attribution = event.get('attribution')                        

                    event_location = event.get('location')

                    if event_location is not None:
                        event_coord_x = event_location.get('coord_x')
                        event_coord_y = event_location.get('coord_y')
                        event_action_area = event_location.get('action_area')
                    else:
                        event_coord_x = None
                        event_coord_y = None
                        event_action_area = None

                    event_on_court = event.get('on_court')
                    #print(event_on_court)

                    if event_on_court is not None:
                        home_on_court_players = [player.get('full_name') for player in event_on_court.get('home').get('players')]
                        away_on_court_players = [player.get('full_name') for player in event_on_court.get('away').get('players')]
                    else:
                        home_on_court_players = None
                        away_on_court_players = None

                    event_statistics = event.get('statistics')

                    if event_statistics is  None:
                        es_player = None 
                        es_team = None 
                        non_es_team  = None
                        es_type = None 
                        es_made = None
                        es_shot_type = None
                        es_shot_type_desc = None
                        es_points = None
                        es_shot_distance = None
                        es_rebound_type = None
                        es_free_throw_type = None

                        events_parsed_arr.append(
                        [
                            game_id,
                            home_alias,
                            home_name,
                            away_alias,
                            away_name,
                            period_number,
                            event_id,
                            event_clock,
                            event_description,
                            event_wall_clock,
                            event_type,
                            event_qualifiers,
                            event_coord_x,
                            event_coord_y,
                            event_action_area,
                            home_on_court_players,
                            away_on_court_players,
                            es_player,
                            es_team,
                            non_es_team,
                            es_type,
                            es_made,
                            es_shot_type,
                            es_shot_type_desc,
                            es_points,
                            es_shot_distance,
                            es_rebound_type,
                            es_free_throw_type
                        ]
                        )
                    else:
                        for es in event_statistics:
                            try:
                                es_player = es.get('player').get('full_name')
                            except:
                                es_player = None

                            es_team = es.get('team').get('name')
                            if es_team == home_name:
                                non_es_team = away_name
                            else:
                                non_es_team = home_name
                            es_type = es.get('type') 
                            es_made = es.get('made')
                            es_shot_type = es.get('shot_type')
                            es_shot_type_desc = es.get('shot_type_desc')
                            es_points = es.get('points')
                            es_shot_distance = es.get('shot_distance')
                            es_rebound_type = es.get('rebound_type')
                            es_free_throw_type = es.get('free_throw_type')
                    
                            events_parsed_arr.append(
                                [
                                    game_id,
                                    home_alias,
                                    home_name,
                                    away_alias,
                                    away_name,
                                    period_number,
                                    event_id,
                                    event_clock,
                                    event_description,
                                    event_wall_clock,
                                    event_type,
                                    event_qualifiers,
                                    event_coord_x,
                                    event_coord_y,
                                    event_action_area,
                                    home_on_court_players,
                                    away_on_court_players,
                                    es_player,
                                    es_team,
                                    non_es_team,
                                    es_type,
                                    es_made,
                                    es_shot_type,
                                    es_shot_type_desc,
                                    es_points,
                                    es_shot_distance,
                                    es_rebound_type,
                                    es_free_throw_type
                                ]
                            )

        query = """INSERT INTO parsed_pbp VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"""
        for row in events_parsed_arr:
            row_0 = [str(s).replace("'", "") for s in row]
            filled_query = (query % tuple(row_0)).replace("'None'", "NULL")
            cur.execute(filled_query)
        conn.commit()


def get_changelog(slack_msg, date, ENDPOINT_MAP, api_key):
    """ Get Changelog from Sportradar"""

    changelog = extract_and_load(
        endpoint='changes',
        params={'year': f'{date.year}', 'month':f'{date.month}', 'day': f'{date.day}'},
        ENDPOINT_MAP = ENDPOINT_MAP,
        api_key = api_key,
        load=False
    )

    changelog_players = changelog.get('players')
    changelog_games = changelog.get('results')

    return changelog_players, changelog_games, slack_msg


def get_games(slack_msg, date, changelog_games, ENDPOINT_MAP, api_key):
    """ Get games boxscore, summary, pbp from Sportradar
    Parameters:
        slack_msg: Slack msg to iteratively build
        date: Defines today's date or historical
    """

    games_list_text = ''
    for game in changelog_games:

        try:
            game_id = game['id']
        except Exception as e:
            slack_hooks.send_to_nba_pipeline(f":rotating_light: Error in Sportradar import: \n No Game ID\n `{e}`")
            pass
        try:
            last_modified = game['last_modified']
        except Exception as e:
            slack_hooks.send_to_nba_pipeline(f":rotating_light: Error in Sportradar import: \n No last_modified for game: `{game_id}`\n `{e}`")
            last_modified = date                

        logging.info(f"Requesting Play by Play for {game_id}")
        try:
            slack_reporting_msg = extract_and_load(
                endpoint='pbp',
                #raw_data_key='periods',
                reporting_keys=['scheduled', 'away.alias', 'home.alias'],
                params={'row_id': game_id, 'last_modified': last_modified},
                ENDPOINT_MAP = ENDPOINT_MAP,
                api_key = api_key,
                load=True
            )
        except:
            slack_reporting_msg = extract_and_load(
                endpoint='pbp',
                #raw_data_key='periods',
                reporting_keys=['scheduled', 'away.name', 'home.name'],
                params={'row_id': game_id, 'last_modified': last_modified},
                ENDPOINT_MAP = ENDPOINT_MAP,
                api_key = api_key,
                load=True
            )

        games_list_text += f"""{slack_reporting_msg}\n"""

    games_updated_text = f"Updated PBP game count: {len(changelog_games)}"
    slack_msg += f"""\n{games_updated_text} \n{games_list_text}\n*****"""

    return slack_msg



