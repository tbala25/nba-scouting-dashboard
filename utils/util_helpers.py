from matplotlib.patches import Circle, Rectangle, Arc
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial.distance import cdist
import numpy as np
import datetime


def get_data(sql, conn):
    return pd.read_sql(sql, conn)

def get_season(date_string):
    date = datetime.datetime.strptime(date_string[:10], '%Y-%M-%d')
    if int(date.month) >= 8:
        season = int(date.year)
    else:
        season = int(date.year) -1
    return season

def format_four_factors(value, metric):
    # if metric in ['TOV', 'REB%']:
    #     return f"{value * 100:.1f}%"
    # else:
    #     return f"{value:.3}"
    return f"{value * 100:.1f}%"


def get_game_four_factors_ranks(team, team_game_ff_df,  team_ff_df):
    # receiving team_game_ff_df after it has been filtered

    # remove team_ff_df team
    team_ff_df = team_ff_df[(team_ff_df['team'] != team)]

    #add game team ff
    game_ff_df = pd.concat([team_ff_df,team_game_ff_df], axis = 0)
    game_ff_df['off_efg_rank'] = game_ff_df['off_efg%'].rank(ascending=False, method='dense')
    game_ff_df['off_tov_rank'] = game_ff_df['off_TOV'].rank(ascending=True, method='dense')
    game_ff_df['off_reb_rank'] = game_ff_df['off_reb%'].rank(ascending=False, method='dense')
    game_ff_df['off_ftr_rank'] = game_ff_df['off_ftr'].rank(ascending=False, method='dense')

    game_ff_df['def_efg_rank'] = game_ff_df['def_efg%'].rank(ascending=True, method='dense')
    game_ff_df['def_tov_rank'] = game_ff_df['def_TOV'].rank(ascending=False, method='dense')
    game_ff_df['def_reb_rank'] = game_ff_df['def_reb%'].rank(ascending=False, method='dense')
    game_ff_df['def_ftr_rank'] = game_ff_df['def_ftr'].rank(ascending=True, method='dense')



    return game_ff_df


def filter_team(input_df, team):
    try:
        filtered_df = input_df[input_df['es_team'] == team]
        return filtered_df
    except:
        filtered_df = input_df[input_df['team'] == team]
        return filtered_df

def filter_game(input_df, game_id):
    filtered_df = input_df[input_df['game_id'] == game_id]
    return filtered_df

def filter_player(input_df, player):
    filtered_df = input_df[input_df['team'] == player]
    return filtered_df


def calculate_shot_variability(shot_chart_df):

    made = shot_chart_df[shot_chart_df['es_made'] == 'True']

    shot_locs = shot_chart_df[['coord_x', 'coord_y']].values.tolist()
    made_shot_locs = made[['coord_x', 'coord_y']].values.tolist()

    distances = cdist(shot_locs, shot_locs)
    made_distances = cdist(made_shot_locs, made_shot_locs)

    shot_avg_dist = []
    made_shot_avg_dist = []

    for shot_dist_to_all in distances:
        shot_avg_dist.append(np.mean(shot_dist_to_all))

    for shot_dist_to_all in made_distances:
        made_shot_avg_dist.append(np.mean(shot_dist_to_all))

    return np.mean(made_shot_avg_dist).round(1), np.mean(shot_avg_dist).round(1)

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((300, 50), radius=10, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((275, 35), 50, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((200, 0), 200, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((220, 0), 160, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((300, 190), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((300, 190), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((300, 47.5), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((47.5, 0), 0, 150, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((552.5, 0), 0, 150, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((300, 47.5), 545, 547.5, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((300, 550), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((300, 550), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((0, 0), 600, 550, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax
#########################################################