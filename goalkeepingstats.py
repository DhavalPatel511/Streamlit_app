from backend_analysis import get_tournament_data
import streamlit as st # type: ignore
from mplsoccer import Radar,grid # type: ignore
import pandas as pd # type: ignore

@st.cache_data
def most_saves(df):

    saves = df[(df['type_name'] == 'Goal Keeper') & (df['sub_type_name'] == 'Shot Saved')]
    saves_cnt = saves.groupby(['team_name','player_name']).size().reset_index(name='Saves')

    if saves_cnt.empty:
        return {"team": None, "player": None, "Saves" : 0}

    most_saves_player = saves_cnt.loc[saves_cnt['Saves'].idxmax()]

    return {"team":  most_saves_player['team_name'], "player": most_saves_player['player_name'], "saves" : int(most_saves_player['Saves'])}

@st.cache_data
def save_percentage(df):
    
    # Filter for saves
    saves = df[(df['type_name'] == 'Goal Keeper') & (df['sub_type_name'] == 'Shot Saved')]
    saves_cnt = saves.groupby(['team_name', 'player_name']).size().reset_index(name='Saves')

    # Filter for shots faced
    shots_faced = df[(df['type_name'] == 'Goal Keeper') & (df['sub_type_name'] == 'Shot Faced')]
    shots_faced_cnt = shots_faced.groupby(['team_name', 'player_name']).size().reset_index(name='Shots Faced')

    # Merge saves and shots faced
    save_percentage_df = saves_cnt.merge(shots_faced_cnt, on=['team_name', 'player_name'], how="inner")

    # **Check if DataFrame is empty before calculations**
    if save_percentage_df.empty:
        return {"team": None, "player": None, "Save Percent": 0.00}

    # **Filter out cases where 'Shots Faced' == 0**
    save_percentage_df = save_percentage_df[save_percentage_df['Shots Faced'] > 0]

    # **Check again after filtering**
    if save_percentage_df.empty:
        return {"team": None, "player": None, "Save Percent": 0.00}

    # **Calculate Save Percentage Correctly**
    save_percentage_df['Save_Percent'] = round((save_percentage_df['Saves'] / save_percentage_df['Shots Faced']) * 100, 2)

    # **Get Goalkeeper with the Best Save Percentage**
    if save_percentage_df['Save_Percent'].empty:
        return {"team": None, "player": None, "Save Percent": 0.00}

    top_save_percent = save_percentage_df.loc[save_percentage_df['Save_Percent'].idxmax()]

    return {"team": top_save_percent['team_name'],"player": top_save_percent['player_name'],"save_percent": float(top_save_percent['Save_Percent'])}

@st.cache_data
def most_clean_sheets(df):
    
    df = df[df['period'] < 5]
    goalkeepers = df[df['position_name'] == "Goalkeeper"] [['match_id','player_name','team_name']]
    goals = df[(df['type_name'] == 'Shot') & (df['outcome_name'] == "Goal")]

    clean_sheets = goalkeepers.groupby(['player_name','team_name','match_id']).first().reset_index()
    clean_sheets = clean_sheets[~clean_sheets['match_id'].isin(goals['match_id'])]

    clean_sheet_cnt = clean_sheets.groupby(['team_name','player_name']).size().reset_index(name="Clean_Sheets")

    if clean_sheet_cnt.empty:
        return {"message": "No clean sheets were recorded in this tournament."}
    
    top_clean_sheet_gk = clean_sheet_cnt.loc[clean_sheet_cnt['Clean_Sheets'].idxmax()]


    return {"team": top_clean_sheet_gk['team_name'],"player": top_clean_sheet_gk['player_name'],"clean_sheets":int(top_clean_sheet_gk['Clean_Sheets'])}

@st.cache_data
def extract_gk_stats(df,player):
    gk_events = df.query("player_name ==@player and type_name == 'Goal Keeper'")
    shots_faced = len(gk_events.query("sub_type_name == 'Shot Faced'"))
    saves = len(gk_events.query("sub_type_name == 'Shot Saved'"))
    goals_conceded = saves = len(gk_events.query(" sub_type_name == 'Goal Conceded' "))
    crosses_claimed = saves = len(gk_events.query(" outcome_name == 'Claim'"))

    save_percent = round(saves / shots_faced * 100,2) if shots_faced > 0 else 0

    player_df = df[df['player_name'] == player]
    total_passes = len(player_df[(player_df['type_name'] == 'Pass') & (player_df['position_name'] == "Goalkeeper")])
    successful_passes = len(player_df[(player_df['type_name'] == 'Pass') &(player_df['outcome_name'].isna()) &  (player_df['position_name'] == "Goalkeeper")])
    pass_accuracy = round(successful_passes / total_passes * 100,2) if total_passes > 0 else 0

    long_passes = len(player_df[(player_df['type_name'] == 'Pass') & (player_df['pass_length'] > 35.0) &  (player_df['position_name'] == "Goalkeeper")])
    successful_long_passes = len(player_df[(player_df['type_name'] == 'Pass') &(player_df['pass_length'] > 35.0) & (player_df['outcome_name'].isna()) & (player_df['position_name'] == "Goalkeeper")])
    long_pass_accuracy = round(successful_long_passes / long_passes * 100,2) if long_passes > 0 else 0

    gk_stats = {
        "Save Percentage (%)": save_percent,
        "Goals Conceded": -goals_conceded,
        "Saves": saves,
        "Pass Accuracy (%)": pass_accuracy,
        "Long Passs Accuracy (%)": long_pass_accuracy,
        "Cross Claimed": crosses_claimed,
        "Total Passes": total_passes
    }

    return gk_stats

@st.cache_data
def create_gk_radar(df, player1_name, player2_name):
    """Create radar chart comparing two attacking players using mplsoccer"""
    # Extract player stats
    player1_stats = extract_gk_stats(df, player1_name)
    player2_stats = extract_gk_stats(df, player2_name)
    
    # Parameters for attackers
    params = list(player1_stats.keys())
    player1_values = [player1_stats[param] for param in params]
    player2_values = [player2_stats[param] for param in params]
    
    # Normalize values to 0-1 range
    normalized_player1_values = []
    normalized_player2_values = []
    
    for param, value1, value2 in zip(params, player1_values, player2_values):
        if "%" in param:  # Percentage-based parameters
            normalized_player1_values.append(value1 / 100)
            normalized_player2_values.append(value2 / 100)
        elif param == "Goals Conceded":  # Negative parameter (lower is better)
            max_val = max(value1, value2)
            normalized_player1_values.append(1 - (value1 / max_val if max_val > 0 else 0))
            normalized_player2_values.append(1 - (value2 / max_val if max_val > 0 else 0))
        else:  # Numeric parameters
            max_val = max(value1, value2)
            normalized_player1_values.append(value1 / max_val if max_val > 0 else 0)
            normalized_player2_values.append(value2 / max_val if max_val > 0 else 0)

    
    # Create radar chart
    radar = Radar(params, [0] * len(params), [1]* len(params), num_rings=4, ring_width=1, center_circle_radius=1)
    
    # Create figure and axis
    fig, axs = grid(figheight=6, grid_height=0.915, title_height=0.06, title_space=0.01, grid_key='radar', axis=False)
    
    
    # Plot radar
    radar.setup_axis(ax=axs['radar']) 
    radar.draw_circles(ax=axs['radar'], facecolor="#e9e9e9", edgecolor="#c9c9c9")
    radar_poly, radar_poly2, vertices1, vertices2 = radar.draw_radar_compare(normalized_player1_values, normalized_player2_values, ax=axs['radar'],
                                                            kwargs_radar={'facecolor': '#1a78cf', 'alpha': 0.6},
                                                            kwargs_compare={'facecolor': '#66d8ba', 'alpha': 0.6})
    
    # Add title
    axs['title'].text(0.01, 0.65, player1_name, fontsize=20, color='#1a78cf', ha='left', va='center')
    axs['title'].text(0.99, 0.65, player2_name, fontsize=20, ha='right', va='center', color='#66d8ba')
    
    # Draw parameter and range labels
    radar.draw_range_labels(ax=axs['radar'], fontsize=8)
    radar.draw_param_labels(ax=axs['radar'], fontsize=12)
    
    return fig






# euro_df = get_tournament_data(55,282)
# a = most_clean_sheets(euro_df)
# print(a)
# gkstats = extract_gk_stats(euro_df,"Angus Gunn")
# cs = most_clean_sheets(euro_df)
# sp = save_percentage(euro_df)
# s = most_saves(euro_df)
#print(gkstats)
# print(cs)
# print(sp)
# print(s)