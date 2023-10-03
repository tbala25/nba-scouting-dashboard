###################################################
# Author: Tejas Bala
# Last Modified: Oct 3 2023
###################################################

##################################################
##IMPORTS
##################################################

import streamlit as st
st.set_page_config(layout="wide")

import seaborn as sns
# import mysql.connector
# from utils.mysql_conn import *
from utils.aws_mysql_conn import *
from utils.util_helpers import *

#########################################################
##GET DATA
#######################################################

sql = "SELECT * FROM sr_nba.shot_chart"
shot_df = pd.read_sql(sql, conn)

shot_df['coord_x'] = shot_df['event_coord_y'].astype(int)
shot_df['coord_y'] = [-(x - 1100) if x > 550 else x for x in shot_df['event_coord_x'].astype(int)]
shot_df['coord_x'] = [600 - x if period >=3 else x
                      for x,home,period in zip(shot_df['coord_x'], shot_df['es_team_home'], shot_df['period_number'])]

sql = "SELECT * FROM sr_nba.nba_parsed_game"
game_df = pd.read_sql(sql, conn)
game_df['game_name'] = game_df['game_scheduled'].apply(lambda x: x[:10])
sql = "SELECT * FROM sr_nba.boxscore"
boxscore_df = pd.read_sql(sql, conn)


sql = "SELECT * FROM sr_nba.team_four_factors_rank"
team_ff_df = pd.read_sql(sql, conn)

sql = "SELECT * FROM sr_nba.team_game_four_factors"
team_game_ff_df = pd.read_sql(sql, conn)

#########################################################
#dropdown columns
## TODO add season drop down
########################################################

dd_col1, dd_col2, dd_col3= st.columns(3)

TEAM = 'NBA'
GAME = 'None'
PLAYER = 'None'
SEASON = 'All'
#########################################################
##filters
#########################################################

filtered_df = shot_df.copy()
filtered_boxscore_df = boxscore_df.copy()

filtered_df['game_id'] = filtered_df['game_id'].astype(str)
game_df['game_id'] = game_df['game_id'].astype(str)
filtered_game_df = game_df.merge(filtered_df, how='inner', on='game_id')

team_list = np.insert(sorted(filtered_df['team'].unique()), 0, 'NBA')
team = dd_col1.selectbox('Team', team_list)


if team != TEAM:
    filtered_df = filter_team(filtered_df, team)
    filtered_boxscore_df = filter_team(filtered_boxscore_df, team)
    filtered_game_df = filter_team(filtered_game_df, team)
    team_game_ff_df = filter_team(team_game_ff_df, team)
    TEAM = team

opponents = [" @ " + home_team if away_team==team else " vs " + away_team if home_team==team else "none" for home_team, away_team in zip(filtered_game_df['home_name'], filtered_game_df['away_name'])]
filtered_game_df['opponents'] = opponents
filtered_game_df['game_name'] = filtered_game_df['game_name'] + filtered_game_df['opponents']

game_list = np.insert(sorted(filtered_game_df['game_name'].unique()), 0, 'None')
if TEAM == 'NBA':
    game_list = ['None']
game = dd_col2.selectbox('Game', game_list)

if game != GAME:
    game_id = filtered_game_df[filtered_game_df['game_name'] == game]['game_id'].unique()[0]
    filtered_df = filter_game(filtered_df, game_id)
    filtered_boxscore_df = filter_game(filtered_boxscore_df, game_id)
    filtered_game_df = filter_game(filtered_game_df, game_id)
    team_game_ff_df = filter_game(team_game_ff_df, game_id)

    sql = f"SELECT * FROM sr_nba.parsed_pbp where es_team='{team}' and game_id='{game_id}'"
    filtered_pbp_df = pd.read_sql(sql, conn)
    GAME = game

player_list = np.insert(sorted(filtered_df['player'].unique()),0, 'None')
player = dd_col3.selectbox('Player',player_list)

if player != PLAYER:
    filtered_df = filter_player(filtered_df, player)
    filtered_boxscore_df = filter_player(filtered_boxscore_df, player)
    try:
        filtered_pbp_df = filter_player(filtered_pbp_df, player)
    except:
        pass

if team == 'NBA':
    try:
        st.image('./images/team_logos/NBA.png', width=150)

    except:
        st.title('NBA Scouting Dashboard')
    pass

else:
    try:
        st.image('./images/team_logos/' + team + '.png', width=200)
    except:
        st.title(team + ' Scouting Dashboard')


    col1, col2 = st.columns(2)
    col1.header('Four Factors')
    rank = col1.radio('Percentages or Rank ', options=['Percentages (Raw)', 'Rank (vs. League)'])
    team_ff_df_orig = team_ff_df.copy()
    team_ff_df = team_ff_df[team_ff_df['team']==team]
    ff_col1, ff_col2, ff_col3, ff_col4 = st.columns(4)
    if rank =='Percentages (Raw)':
        ff_col1.metric(label="OFF eFG%", value=format_four_factors(team_ff_df['off_efg%'].values[0],'efg'))
        ff_col2.metric(label="OFF TOV", value=format_four_factors(team_ff_df['off_TOV'].values[0], 'TOV'))
        ff_col3.metric(label="OFF REB%", value=format_four_factors(team_ff_df['off_reb%'].values[0],'REB%'))
        ff_col4.metric(label="OFF FTR", value=format_four_factors(team_ff_df['off_ftr'].values[0], 'ftr'))
        ff_col1.metric(label="DEF eFG%", value=format_four_factors(team_ff_df['def_efg%'].values[0],'efg'))
        ff_col2.metric(label="DEF TOV", value=format_four_factors(team_ff_df['def_TOV'].values[0],'TOV'))
        ff_col3.metric(label="DEF REB%", value=format_four_factors(team_ff_df['def_reb%'].values[0],'REB%'))
        ff_col4.metric(label="DEF FTR", value=format_four_factors(team_ff_df['def_ftr'].values[0],'ftr'))
    elif rank == 'Rank (vs. League)':
        ff_col1.metric(label="OFF eFG% Rank", value=int(team_ff_df['off_efg_rank'].values[0]))
        ff_col2.metric(label="OFF TOV Rank", value=int(team_ff_df['off_tov_rank'].values[0]))
        ff_col3.metric(label="OFF REB% Rank", value=int(team_ff_df['off_reb_rank'].values[0]))
        ff_col4.metric(label="OFF FTR Rank", value=int(team_ff_df['off_ftr_rank'].values[0]))
        ff_col1.metric(label="DEF eFG% Rank", value=int(team_ff_df['def_efg_rank'].values[0]))
        ff_col2.metric(label="DEF TOV Rank", value=int(team_ff_df['def_tov_rank'].values[0]))
        ff_col3.metric(label="DEF REB% Rank", value=int(team_ff_df['def_reb_rank'].values[0]))
        ff_col4.metric(label="DEF FTR Rank", value=int(team_ff_df['def_ftr_rank'].values[0]))
    else:
        pass


    filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['team']==team]

    if game !='None':

        st.header('Four Factors ' + game)
        col1, col2, col3, col4 = st.columns(4)
        if rank == 'Percentages (Raw)':
            col1.metric(label="OFF eFG%", value=format_four_factors(team_game_ff_df['off_efg%'].values[0],'efg'),
                        delta=format_four_factors(team_game_ff_df['off_efg%'].values[0] - team_ff_df['off_efg%'].values[0],'efg'))
            col2.metric(label="OFF TOV", value=format_four_factors(team_game_ff_df['off_TOV'].values[0],'TOV'),
                        delta=format_four_factors(team_game_ff_df['off_TOV'].values[0] - team_ff_df['off_TOV'].values[0],'TOV'), delta_color="inverse")
            col3.metric(label="OFF REB%", value=format_four_factors(team_game_ff_df['off_reb%'].values[0],'REB%'),
                        delta=format_four_factors(team_game_ff_df['off_reb%'].values[0] - team_ff_df['off_reb%'].values[0],'REB%'))
            col4.metric(label="OFF FTR", value=format_four_factors(team_game_ff_df['off_ftr'].values[0],'ftr'),
                        delta=format_four_factors(team_game_ff_df['off_ftr'].values[0] - team_ff_df['off_ftr'].values[0],'ftr'))
            col1.metric(label="DEF eFG%", value=format_four_factors(team_game_ff_df['def_efg%'].values[0],'efg'),
                        delta=format_four_factors(team_game_ff_df['def_efg%'].values[0] - team_ff_df['def_efg%'].values[0],'efg'), delta_color="inverse")
            col2.metric(label="DEF TOV", value=format_four_factors(team_game_ff_df['def_TOV'].values[0],'TOV'),
                        delta=format_four_factors(team_game_ff_df['def_TOV'].values[0] - team_ff_df['def_TOV'].values[0],'TOV'))
            col3.metric(label="DEF REB%", value=format_four_factors(team_game_ff_df['def_reb%'].values[0],'REB%'),
                        delta=format_four_factors(team_game_ff_df['def_reb%'].values[0] - team_ff_df['def_reb%'].values[0],'REB%'))
            col4.metric(label="DEF FTR", value=format_four_factors(team_game_ff_df['def_ftr'].values[0],'ftr'),
                        delta=format_four_factors(team_game_ff_df['def_ftr'].values[0] - team_ff_df['def_ftr'].values[0],'ftr'), delta_color="inverse")
        elif rank == 'Rank (vs. League)':
            game_ranks = get_game_four_factors_ranks(team, team_game_ff_df, team_ff_df_orig)
            game_ranks = game_ranks[game_ranks['team'] == team]
            col1.metric(label="OFF eFG% Rank", value=int(game_ranks['off_efg_rank'].values[0]),
                        delta= int(team_ff_df['off_efg_rank'].values[0] - game_ranks['off_efg_rank'].values[0] ))

            col2.metric(label="OFF TOV Rank", value=int(game_ranks['off_tov_rank'].values[0]),
                        delta=int(team_ff_df['off_tov_rank'].values[0] - game_ranks['off_tov_rank'].values[0]))

            col3.metric(label="OFF REB% Rank", value=int(game_ranks['off_reb_rank'].values[0]),
                        delta=int(team_ff_df['off_reb_rank'].values[0] - game_ranks['off_reb_rank'].values[0]))

            col4.metric(label="OFF FTR Rank", value=int(game_ranks['off_ftr_rank'].values[0]),
                        delta=int(team_ff_df['off_ftr_rank'].values[0] - game_ranks['off_ftr_rank'].values[0]))

            col1.metric(label="DEF eFG% Rank", value=int(game_ranks['def_efg_rank'].values[0]),
                        delta=int(team_ff_df['def_efg_rank'].values[0] - game_ranks['def_efg_rank'].values[0]))

            col2.metric(label="DEF TOV Rank", value=int(game_ranks['def_tov_rank'].values[0]),
                        delta=int(team_ff_df['def_tov_rank'].values[0] - game_ranks['def_tov_rank'].values[0]))

            col3.metric(label="DEF REB% Rank", value=int(game_ranks['def_reb_rank'].values[0]),
                        delta=int(team_ff_df['def_reb_rank'].values[0] - game_ranks['def_reb_rank'].values[0]))

            col4.metric(label="DEF FTR Rank", value=int(game_ranks['def_ftr_rank'].values[0]),
                        delta=int(team_ff_df['def_ftr_rank'].values[0] - game_ranks['def_ftr_rank'].values[0]))

    if player !='None':

        try:
            st.image('./images/players/' + player.replace(' ','').lower() + '.jpeg', width=150)

        except:
            pass

        st.header(player + ' ' + game)
        box_1, box_2, box_3, box_4, box_5, box_6 = st.columns(6)
        b_1, b_2, b_3, b_4, b_5, b_6, b_7, b_8, b_9, b_10, b_11, b_12 = st.columns(12)

        box_1.metric(label="PTS", value=int(filtered_boxscore_df['PTS'].values[0]))
        box_2.metric(label="AST", value=int(filtered_boxscore_df['AST'].values[0]))
        box_3.metric(label="REB", value=int(filtered_boxscore_df['REB'].values[0]))
        box_4.metric(label="BLK", value=int(filtered_boxscore_df['BLK'].values[0]))
        box_5.metric(label="STL", value=int(filtered_boxscore_df['STL'].values[0]))
        box_6.metric(label="TOV", value=int(filtered_boxscore_df['TOV'].values[0]))

        box_1.metric(label="FGM/FGA",
                     value=str(int(filtered_boxscore_df['FGM'].values[0]))+'/'+str(int(filtered_boxscore_df['FGA'].values[0])))
        box_2.metric(label="3PM/3PA",
                     value=str(int(filtered_boxscore_df['3PM'].values[0]))+'/'+str(int(filtered_boxscore_df['3PA'].values[0])))
        box_3.metric(label="FTM/FTA",
                     value=str(int(filtered_boxscore_df['FTM'].values[0]))+'/'+str(int(filtered_boxscore_df['FTA'].values[0])))

        box_4.metric(label="ORB",
                     value=int(filtered_boxscore_df['ORB'].values[0]))
        box_5.metric(label="DRB",
                   value=int(filtered_boxscore_df['DRB'].values[0]))

        box_6.metric(label="PF",
                   value=int(filtered_boxscore_df['PF'].values[0]))

        ##SHOT VARIABILITY
        shot_vars = calculate_shot_variability(filtered_df)
        st.info("SHOT VAR is the calculated distance between shots." \
                + " Capped representing only made shots and uncapped representing all shots attempted." \
                + " Hypothesis is that a large deficit between Capped/Uncapped call for further exploration")
        box_1.metric("SHOT VAR (Capped)", shot_vars[0])
        box_2.metric("SHOT VAR (Uncapped)", shot_vars[1])

        #####
        filtered_df = filtered_df.reset_index(drop=True)
        toggle_shot_df = st.radio("Toggle Shot Chart Data Table & Row Selector", ["Show", "Hide"])
        if toggle_shot_df == "Show":
            st.dataframe(filtered_df.style.format(precision=0), height=1000)

            shot_list = list(filtered_df.index.values)
            shot_list.insert(0, 'None')

            shot = st.selectbox(
                'Play ID', shot_list)

            if shot != "None":
                filtered_df = filtered_df.loc[shot, :]

##############

# create our jointplot
joint_kws=dict(gridsize=40)
cmap=plt.cm.gist_heat_r

joint_shot_chart = sns.jointplot(filtered_df['coord_x'].astype(int), filtered_df['coord_y'].astype(int),
                                 kind='hex', joint_kws= joint_kws, space=0, color=cmap(.2), cmap=cmap)
# joint_shot_chart = plt.hexbin(filtered_df['coord_x'].astype(int), filtered_df['coord_y'].astype(int), gridsize = 50, cmap ='Greens')
joint_shot_chart.fig.set_size_inches(8,6)
ax = joint_shot_chart.ax_joint
draw_court(ax, outer_lines=True)

# Adjust the axis limits and orientation of the plot in order
# to plot half court, with the hoop by the top of the plot
ax.set_xlim(0,600)
ax.set_ylim(550,0)

# Get rid of axis labels and tick marks
ax.set_xlabel('')
ax.set_ylabel('')
ax.tick_params(labelbottom='off', labelleft='off')

# st.pyplot(joint_shot_chart)

left_column, right_column = st.columns(2)
st.markdown('#')
st.pyplot(joint_shot_chart)

#DEBUGGING BOXSCOER + PBP

# try:
#     boxscore_pressed = st.button('Boxscore')
#     pbp_pressed = st.button("Play by Play")
#
#     if boxscore_pressed:
#         right_column.dataframe(filtered_boxscore_df[
#                                    ['player', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'REB', 'AST',
#                                     'STL', 'BLK', 'TOV', 'PF', 'PTS']]
#                                .dropna(subset=['player'])
#                                .style.format(precision=0),
#                                height=1000)
#     if pbp_pressed:
#         right_column.dataframe(filtered_pbp_df[['period_number', 'event_clock', 'es_team', 'es_player', 'es_type',
#                                                 'event_action_area', 'event_description']]
#                                .style.format(precision=0),
#                                height=1000)
# except:
#     pass


