import streamlit as st
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
shot_df['coord_x'] = [600 - x if x > 300 and y > 550 else x
                     for x,y in zip(shot_df['event_coord_y'].astype(int),shot_df['event_coord_x'].astype(int))]
shot_df['new_event_action_area'] = [x.replace('right', 'left') if 'right' in x else x.replace('left', 'right') if 'left' in x else x for x in shot_df['event_action_area']]

sql = "SELECT * FROM sr_nba.nba_parsed_game"
game_df = pd.read_sql(sql, conn)
game_df['game_name'] = game_df['game_scheduled'].apply(lambda x: x[:10]) + ' vs. '

sql = "SELECT * FROM sr_nba.boxscore"
boxscore_df = pd.read_sql(sql, conn)


sql = "SELECT * FROM sr_nba.team_four_factors"
team_ff_df = pd.read_sql(sql, conn)

sql = "SELECT * FROM sr_nba.team_game_four_factors"
team_game_ff_df = pd.read_sql(sql, conn)


# st.dataframe(game_df)

#########################################################

col1, col2= st.columns(2)

#########################################################
##filters

filtered_df = shot_df.copy()
filtered_boxscore_df = boxscore_df.copy()

team = col1.selectbox(
    'Demo Team',
     np.insert(sorted(filtered_df['es_team'].unique()), 0, 'None'))

#'You selected:', team

if team == 'None':
    try:
        col1.image('./images/team_logos/NBA.png', width=75)

    except:
        col1.title('NBA Scouting Dashboard')
    pass

else:
    try:
        col1.image('./images/team_logos/' + team + '.png', width=200)

    except:
        col1.title(team + ' Scouting Dashboard')



    col1.header('Four Factors')

    team_ff_df = team_ff_df[team_ff_df['team']==team]

    ff_col1, ff_col2, ff_col3, ff_col4 = st.columns(4)
    ff_col1.metric(label="OFF eFG%", value=format_four_factors(team_ff_df['off_efg%'].values[0],'efg'))
    ff_col2.metric(label="OFF TOV", value=format_four_factors(team_ff_df['off_TOV'].values[0], 'TOV'))
    ff_col3.metric(label="OFF REB%", value=format_four_factors(team_ff_df['off_reb%'].values[0],'REB%'))
    ff_col4.metric(label="OFF FTR", value=format_four_factors(team_ff_df['off_ftr'].values[0], 'ftr'))
    ff_col1.metric(label="DEF eFG%", value=format_four_factors(team_ff_df['def_efg%'].values[0],'efg'))
    ff_col2.metric(label="DEF TOV", value=format_four_factors(team_ff_df['def_TOV'].values[0],'TOV'))
    ff_col3.metric(label="DEF REB%", value=format_four_factors(team_ff_df['def_reb%'].values[0],'REB%'))
    ff_col4.metric(label="DEF FTR", value=format_four_factors(team_ff_df['def_ftr'].values[0],'ftr'))

    #st.dataframe(team_ff_df)

    filtered_df = filtered_df[filtered_df['es_team']==team]
    filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['team']==team]


    filtered_df['game_id'] = filtered_df['game_id'].astype(str)
    game_df['game_id'] = game_df['game_id'].astype(str)
    filtered_game_df = game_df.merge(filtered_df, how='inner', on='game_id')
    opponents = [home_team if away_team==team else away_team if home_team==team else "none" for home_team, away_team in zip(filtered_game_df['home_name'], filtered_game_df['away_name'])]
    filtered_game_df['opponents'] = opponents
    filtered_game_df['game_name'] = filtered_game_df['game_name'] + filtered_game_df['opponents']
    #st.dataframe(filtered_game_df)

    game = st.selectbox(
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


        filtered_df = filtered_df[filtered_df['game_id']==game_id]
        filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['game_id'] == game_id]

    player = st.selectbox(
        'Player',
         np.insert(filtered_df['es_player'].unique(),0, 'None'))
    # 'You selected:', player

    if player !='None':
        filtered_df = filtered_df[filtered_df['es_player']==player]
        filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['player'] == player]


        try:
            st.image('./images/players/' + player.replace(' ','').lower() + '.jpeg', width=100)
            st.sidebar.image('./images/players/' + player.replace(' ','').lower() + '.jpeg', width=100)

        except:
            # col1.subtitle(team + ' Scouting Dashboard')
            pass




left_column, right_column = st.columns(2)
#pressed = left_column.button('Boxscore')
#if pressed:
st.header("Boxscore")
st.dataframe(filtered_boxscore_df[['player', 'FGM', 'FGA', '3PM',	'3PA',	'FTM',	'FTA',	'ORB',	'DRB',	'REB',	'AST',	'STL',	'BLK',	'TOV',	'PF',	'PTS']]
             .dropna(subset=['player'])
             .style.format(precision=0))



##############

# create our jointplot
joint_kws=dict(gridsize=20)
cmap=plt.cm.gist_heat_r

joint_shot_chart = sns.jointplot(filtered_df['coord_x'].astype(int), filtered_df['coord_y'].astype(int),
                                 kind='hex', joint_kws= joint_kws, space=0, color=cmap(.2), cmap=cmap)

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

# st.sidebar.pyplot(joint_shot_chart)
st.pyplot(joint_shot_chart)