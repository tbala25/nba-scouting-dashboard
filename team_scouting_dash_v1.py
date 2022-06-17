import streamlit as st
st.set_page_config(layout="wide")
import numpy as np
import pandas as pd

# import requests
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# import mysql.connector
from utils.mysql_conn import *
from utils.util_helpers import *

#########################################################
##GET DATA
sql = "SELECT * FROM sr_nba.shot_chart"
shot_df = pd.read_sql(sql, conn)

shot_df['coord_x'] = shot_df['event_coord_y'].astype(int)
shot_df['coord_y'] = [-(x - 1100) if x > 550 else x for x in shot_df['event_coord_x'].astype(int)]
shot_df['coord_x'] = [600 - x if period >=3 else x
                      for x,home,period in zip(shot_df['coord_x'], shot_df['es_team_home'], shot_df['period_number'])]
# shot_df['coord_x'] = [600 - x if x <= 300 and y <= 550 else x
#                      for x,y in zip(shot_df['event_coord_y'].astype(int),shot_df['event_coord_x'].astype(int))]
# shot_df['new_event_action_area'] = [x.replace('right', 'left') if 'right' in x and q >=3 and t == 0 else x.replace('left', 'right') if 'left' in x and q >= 3 and t == 0 else x for x,q,t in zip(shot_df['event_action_area'], shot_df['period_number'], shot_df['es_team_home'])]
# shot_df['new_event_action_area'] = [x.replace('right', 'left') if 'right' in x and q <=2 and t == 1 else x.replace('left', 'right') if 'left' in x and q <= 2 and t == 1 else x for x,q,t in zip(shot_df['event_action_area'], shot_df['period_number'], shot_df['es_team_home'])]

sql = "SELECT * FROM sr_nba.nba_parsed_game"
game_df = pd.read_sql(sql, conn)
game_df['game_name'] = game_df['game_scheduled'].apply(lambda x: x[:10])
sql = "SELECT * FROM sr_nba.boxscore"
boxscore_df = pd.read_sql(sql, conn)

# sql = "SELECT * FROM sr_nba.nba_parsed_game"
# pbp_df = pd.read_sql(sql, conn)


sql = "SELECT * FROM sr_nba.team_four_factors_rank"
team_ff_df = pd.read_sql(sql, conn)

sql = "SELECT * FROM sr_nba.team_game_four_factors"
team_game_ff_df = pd.read_sql(sql, conn)

#########################################################
#dropdown columns
## TODO add season drop down
dd_col1, dd_col2, dd_col3= st.columns(3)

#########################################################
##filters

filtered_df = shot_df.copy()
filtered_boxscore_df = boxscore_df.copy()

team = dd_col1.selectbox(
    'Team',
     np.insert(sorted(filtered_df['es_team'].unique()), 0, 'NBA'))

#'You selected:', team

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



    filtered_df = filtered_df[filtered_df['es_team']==team]
    filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['team']==team]
    # filtered_pbp_df = filtered_pbp_df[filtered_pbp_df['team']==team]

    filtered_df['game_id'] = filtered_df['game_id'].astype(str)
    game_df['game_id'] = game_df['game_id'].astype(str)
    filtered_game_df = game_df.merge(filtered_df, how='inner', on='game_id')
    opponents = [" @ " + home_team if away_team==team else " vs " + away_team if home_team==team else "none" for home_team, away_team in zip(filtered_game_df['home_name'], filtered_game_df['away_name'])]
    filtered_game_df['opponents'] = opponents
    filtered_game_df['game_name'] = filtered_game_df['game_name'] + filtered_game_df['opponents']
    #st.dataframe(filtered_game_df)

    game = dd_col2.selectbox(
        'Game',
         np.insert(sorted(filtered_game_df['game_name'].unique()), 0, 'None'))

    #'Game selected:', game
    if game !='None':

        game_id = filtered_game_df[filtered_game_df['game_name'] == game]['game_id'].unique()[0]
        # expander = st.sidebar.expander("Show game_id")
        # expander.write(game_id)

        team_game_ff_df = team_game_ff_df[(team_game_ff_df['team'] == team) & (team_game_ff_df['game_id'] == game_id)]
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
            # st.dataframe(game_ranks)
            # st.dataframe(team_ff_df)
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

            # col1.metric(label="DEF eFG%", value=format_four_factors(team_game_ff_df['def_efg%'].values[0], 'efg'),
            #             delta=format_four_factors(
            #                 team_game_ff_df['def_efg%'].values[0] - team_ff_df['def_efg%'].values[0], 'efg'),
            #             delta_color="inverse")
            # col2.metric(label="DEF TOV", value=format_four_factors(team_game_ff_df['def_TOV'].values[0], 'TOV'),
            #             delta=format_four_factors(
            #                 team_game_ff_df['def_TOV'].values[0] - team_ff_df['def_TOV'].values[0], 'TOV'))
            # col3.metric(label="DEF REB%", value=format_four_factors(team_game_ff_df['def_reb%'].values[0], 'REB%'),
            #             delta=format_four_factors(
            #                 team_game_ff_df['def_reb%'].values[0] - team_ff_df['def_reb%'].values[0], 'REB%'))
            # col4.metric(label="DEF FTR", value=format_four_factors(team_game_ff_df['def_ftr'].values[0], 'ftr'),
            #             delta=format_four_factors(
            #                 team_game_ff_df['def_ftr'].values[0] - team_ff_df['def_ftr'].values[0], 'ftr'),
            #             delta_color="inverse")

        filtered_df = filtered_df[filtered_df['game_id']==game_id]
        filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['game_id'] == game_id]
        sql = f"SELECT * FROM sr_nba.parsed_pbp where es_team='{team}' and game_id='{game_id}'"
        pbp_df = pd.read_sql(sql, conn)
        filtered_pbp_df = pbp_df.copy()

    # pp_col1, pp_col2 = st.columns([3,1])
    player = dd_col3.selectbox(
        'Player',
         np.insert(filtered_df['es_player'].unique(),0, 'None'))
    # 'You selected:', player

    if player !='None':
        filtered_df = filtered_df[filtered_df['es_player']==player]
        filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['player'] == player]
        filtered_pbp_df = filtered_pbp_df[filtered_pbp_df['es_player']==player]


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


        #####
        filtered_df = filtered_df.reset_index(drop=True)
        st.dataframe(filtered_df.style.format(precision=0),height=1000)

        shot = st.selectbox(
            'Play ID', filtered_df.index.values)

        if shot != "None":
            filtered_df = filtered_df.loc[shot,:]


##############

# create our jointplot
joint_kws=dict(gridsize=40)
cmap=plt.cm.gist_heat_r

joint_shot_chart = sns.jointplot(filtered_df['coord_x'].astype(int), filtered_df['coord_y'].astype(int),
                                 kind='hex', joint_kws= joint_kws, space=0, color=cmap(.2), cmap=cmap)
# joint_shot_chart = plt.hexbin(filtered_df['coord_x'].astype(int), filtered_df['coord_y'].astype(int), gridsize = 50, cmap ='Greens')
joint_shot_chart.fig.set_size_inches(12,11)
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

try:
    boxscore_pressed = st.button('Boxscore')
    pbp_pressed = st.button("Play by Play")

    if boxscore_pressed:
        right_column.dataframe(filtered_boxscore_df[
                                   ['player', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'ORB', 'DRB', 'REB', 'AST',
                                    'STL', 'BLK', 'TOV', 'PF', 'PTS']]
                               .dropna(subset=['player'])
                               .style.format(precision=0),
                               height=1000)
    if pbp_pressed:
        right_column.dataframe(filtered_pbp_df[['period_number', 'event_clock', 'es_team', 'es_player', 'es_type',
                                                'event_action_area', 'event_description']]
                               .style.format(precision=0),
                               height=1000)
except:
    pass


