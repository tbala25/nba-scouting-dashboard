from icecream import ic
import logging

from dotenv import load_dotenv
load_dotenv()

from endpoint_maps import *
import sys
sys.path.insert(0, '../utils')
from pipeline_master import *
import os

ic.disable()

#########################################

if __name__ == '__main__':

    ##DAILY NBA LOAD LOGIC

    ##################################
    #####    GET CURRENT DATE    #####
    ##################################

    #Changelog finishes update at 4am UTC for day prior (ex. for 7/17 changes log is open from 4am 7/17 to 3:59am 7/18)
    #we want to get changelog from "yesterday" if running after 4am UTC ~= 11pm CT

    for day in range(-30,-1):
        try:
            now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=day)
            #now = datetime.date(2022, 6, 10)

            slack_msg = f""":white_check_mark: Sportradar NBA (Daily) Import Success for {now.month}/{now.day}/{now.year}!\n*****"""

            api_key = os.getenv('SPORTRADAR_NBA_API_KEY')
            ENDPOINT_MAP = NBA_ENDPOINT_MAP
            #print(ENDPOINT_MAP)

            ##################################
            #####      GET CHANGELOG     #####
            ##################################
            changelog_players, changelog_games, slack_msg = ic(get_changelog(slack_msg, now, ENDPOINT_MAP, api_key))

            ##################################
            #####       GET PLAYERS      #####
            ##################################
            # if changelog_players is not None:

            #     slack_msg = ic(get_players(slack_msg, now, changelog_players, ENDPOINT_MAP, api_key))

            ##################################
            #####       GET GAMES        #####
            ##################################
            if changelog_games is not None:
                slack_msg = ic(get_games(slack_msg, now, changelog_games, ENDPOINT_MAP, api_key))

            logging.info("COMPLETE")
            print(slack_msg)
            slack_hooks.send_to_nba_pipeline(slack_msg)

            ##################################
            #####      GET SCHEDULE      #####
            ##################################
            # if changelog_schedule is not None:
            #     #get the whole schedule table again
            #     logging.info(f"Requesting Schedule update")

            #     slack_msg = get_schedule(slack_msg, now, season, ENDPOINT_MAP, api_key)

        except Exception as e:
            print(e)
            #logging.exception()
            slack_hooks.send_to_nba_pipeline(f":rotating_light: Error in Sportradar import: \n`{e}`")
