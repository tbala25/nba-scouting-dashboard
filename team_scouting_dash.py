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

#########################################################
##filters

filtered_df = shot_df.copy()
filtered_boxscore_df = boxscore_df.copy()

team = st.selectbox(
    'Demo Team',
     np.insert(sorted(filtered_df['es_team'].unique()), 0, 'None'))

#'You selected:', team

if team !='None':
    try:
        st.image('./images/team_logos/' + team + '.png', width=200)
    except:
        st.title(team + ' Scouting Dashboard')

    st.header('Four Factors')

    team_ff_df = team_ff_df[team_ff_df['team']==team]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="OFF eFG%", value=team_ff_df['off_efg%'].values[0])
    col2.metric(label="OFF TOV", value=team_ff_df['off_TOV'].values[0])
    col3.metric(label="OFF REB%", value=team_ff_df['off_reb%'].values[0])
    col4.metric(label="OFF FTR", value=team_ff_df['off_ftr'].values[0])
    col1.metric(label="DEF eFG%", value=team_ff_df['def_efg%'].values[0])
    col2.metric(label="DEF TOV", value=team_ff_df['def_TOV'].values[0])
    col3.metric(label="DEF REB%", value=team_ff_df['def_reb%'].values[0])
    col4.metric(label="DEF FTR", value=team_ff_df['def_ftr'].values[0])

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
        expander = st.sidebar.expander("Show game_id")
        expander.write(game_id)

        team_game_ff_df = team_game_ff_df[(team_game_ff_df['team'] == team) & (team_game_ff_df['game_id'] == game_id)]
        st.header('Four Factors ' + game)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="OFF eFG%", value=team_game_ff_df['off_efg%'].values[0], delta=team_game_ff_df['off_efg%'].values[0] - team_ff_df['off_efg%'].values[0])
        col2.metric(label="OFF TOV", value=team_game_ff_df['off_TOV'].values[0], delta=team_game_ff_df['off_TOV'].values[0] - team_ff_df['off_TOV'].values[0], delta_color="inverse")
        col3.metric(label="OFF REB%", value=team_game_ff_df['off_reb%'].values[0], delta=team_game_ff_df['off_reb%'].values[0] - team_ff_df['off_reb%'].values[0])
        col4.metric(label="OFF FTR", value=team_game_ff_df['off_ftr'].values[0], delta=team_game_ff_df['off_ftr'].values[0] - team_ff_df['off_ftr'].values[0])
        col1.metric(label="DEF eFG%", value=team_game_ff_df['def_efg%'].values[0], delta=team_game_ff_df['def_efg%'].values[0] - team_ff_df['def_efg%'].values[0], delta_color="inverse")
        col2.metric(label="DEF TOV", value=team_game_ff_df['def_TOV'].values[0], delta=team_game_ff_df['def_TOV'].values[0] - team_ff_df['def_TOV'].values[0])
        col3.metric(label="DEF REB%", value=team_game_ff_df['def_reb%'].values[0], delta=team_game_ff_df['def_reb%'].values[0] - team_ff_df['def_reb%'].values[0])
        col4.metric(label="DEF FTR", value=team_game_ff_df['def_ftr'].values[0], delta=team_game_ff_df['def_ftr'].values[0] - team_ff_df['def_ftr'].values[0], delta_color="inverse")


        filtered_df = filtered_df[filtered_df['game_id']==game_id]
        filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['game_id'] == game_id]

    player = st.selectbox(
        'Player',
         np.insert(filtered_df['es_player'].unique(),0, 'None'))
    'You selected:', player

    if player !='None':
        filtered_df = filtered_df[filtered_df['es_player']==player]
        filtered_boxscore_df = filtered_boxscore_df[filtered_boxscore_df['player'] == player]




left_column, right_column = st.columns(2)
#pressed = left_column.button('Boxscore')
#if pressed:
st.header("Boxscore")
st.dataframe(filtered_boxscore_df[['player', 'FGM', 'FGA', '3PM',	'3PA',	'FTM',	'FTA',	'ORB',	'DRB',	'REB',	'AST',	'STL',	'BLK',	'TOV',	'PF',	'PTS']])



expander = st.expander("FAQ")
expander.write("Here you could put in some really, really long explanations...")


#########################################################
# ##DRAW COURT
# from matplotlib.patches import Circle, Rectangle, Arc
#
# def draw_court(ax=None, color='black', lw=2, outer_lines=False):
#     # If an axes object isn't provided to plot onto, just get current one
#     if ax is None:
#         ax = plt.gca()
#
#     # Create the various parts of an NBA basketball court
#
#     # Create the basketball hoop
#     # Diameter of a hoop is 18" so it has a radius of 9", which is a value
#     # 7.5 in our coordinate system
#     hoop = Circle((300, 50), radius=10, linewidth=lw, color=color, fill=False)
#
#     # Create backboard
#     backboard = Rectangle((275, 35), 50, -1, linewidth=lw, color=color)
#
#     # The paint
#     # Create the outer box 0f the paint, width=16ft, height=19ft
#     outer_box = Rectangle((200, 0), 200, 190, linewidth=lw, color=color,
#                           fill=False)
#     # Create the inner box of the paint, widt=12ft, height=19ft
#     inner_box = Rectangle((220, 0), 160, 190, linewidth=lw, color=color,
#                           fill=False)
#
#     # Create free throw top arc
#     top_free_throw = Arc((300, 190), 120, 120, theta1=0, theta2=180,
#                          linewidth=lw, color=color, fill=False)
#     # Create free throw bottom arc
#     bottom_free_throw = Arc((300, 190), 120, 120, theta1=180, theta2=0,
#                             linewidth=lw, color=color, linestyle='dashed')
#     # Restricted Zone, it is an arc with 4ft radius from center of the hoop
#     restricted = Arc((300, 47.5), 80, 80, theta1=0, theta2=180, linewidth=lw,
#                      color=color)
#
#     # Three point line
#     # Create the side 3pt lines, they are 14ft long before they begin to arc
#     corner_three_a = Rectangle((47.5, 0), 0, 150, linewidth=lw,
#                                color=color)
#     corner_three_b = Rectangle((552.5, 0), 0, 150, linewidth=lw, color=color)
#     # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
#     # I just played around with the theta values until they lined up with the
#     # threes
#     three_arc = Arc((300, 47.5), 545, 547.5, theta1=22, theta2=158, linewidth=lw,
#                     color=color)
#
#     # Center Court
#     center_outer_arc = Arc((300, 550), 120, 120, theta1=180, theta2=0,
#                            linewidth=lw, color=color)
#     center_inner_arc = Arc((300, 550), 40, 40, theta1=180, theta2=0,
#                            linewidth=lw, color=color)
#
#     # List of the court elements to be plotted onto the axes
#     court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
#                       bottom_free_throw, restricted, corner_three_a,
#                       corner_three_b, three_arc, center_outer_arc,
#                       center_inner_arc]
#
#     if outer_lines:
#         # Draw the half court line, baseline and side out bound lines
#         outer_lines = Rectangle((0, 0), 600, 550, linewidth=lw,
#                                 color=color, fill=False)
#         court_elements.append(outer_lines)
#
#     # Add the court elements onto the axes
#     for element in court_elements:
#         ax.add_patch(element)
#
#     return ax
# #########################################################


















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

st.pyplot(joint_shot_chart)