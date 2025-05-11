import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
from mplsoccer import VerticalPitch,Pitch,Radar,grid # type: ignore
from utils.data_prep import get_tournament_data
import streamlit as st # type: ignore
from utils.attackstats import extract_att_stats
from utils.defensestats import extract_def_stats
from utils.goalkeepingstats import extract_gk_stats



####### Attack charts
@st.cache_data
def plot_shots( df,team_name):
    team_data = df[df['team_name'] == team_name]

    ## Filter shot data
    shots = team_data[team_data["type_name"] == "Shot"]

    #3 separte on target and off target
    shots_on_target = shots[(team_data['outcome_name'] == 'Goal') | (team_data['outcome_name'] == 'Saved')]
    shots_off_target = shots[~((team_data['outcome_name'] == 'Goal') | (team_data['outcome_name'] == 'Saved'))]

    pitch = VerticalPitch(pitch_type ='statsbomb',half = True,corner_arcs=True,spot_scale=0.01,pitch_color = "black")
    fig,ax = pitch.draw(figsize=(10,8))

    ## PLot different shot types
    pitch.scatter(shots_on_target["x"],shots_on_target["y"],color = "green", s = 100, label = "Shots On Target",edgecolors="white",ax= ax)
    pitch.scatter(shots_off_target["x"],shots_off_target["y"],color = "red", s = 100, label = "Shots Off Target",edgecolors="white",ax= ax)

    ## adding shot count text
    pitch.text(80,55, f"Shots On Target: {len(shots_on_target)}",color = "Green",fontsize = 12,ax= ax)
    pitch.text(85,55, f"Shots Off Target: {len(shots_off_target)}",color = "Red",fontsize = 12,ax= ax)
    
    ax.legend(loc="lower right", fontsize=10, facecolor="gray", edgecolor="white", title="Shot Outcomes")
    ax.set_title(f"Shots taken by {team_name}",color = "black",fontsize = 14)

    return fig


@st.cache_data
def passes_assisted_shot(df,team_name):
    df_pass = df.loc[(df.pass_assisted_shot_id.notnull()) & (df.team_name == team_name),['x','y','end_x','end_y','pass_assisted_shot_id']]

    df_shot = (df.loc[(df.type_name == "Shot") & (df.team_name == team_name),['id','outcome_name','shot_statsbomb_xg']].rename({'id':'pass_assisted_shot_id'},axis =1))

    df_pass = df_pass.merge(df_shot,how = 'left').drop('pass_assisted_shot_id',axis = 1)

    mask_goal = df_pass.outcome_name == 'Goal'

    # Setup the pitch
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='black', line_color='white',
                      half=True,corner_arcs=True)
    fig, axs = pitch.draw(figsize=(8,8))

    # Plot the completed passes
    pitch.lines(df_pass[mask_goal].x, df_pass[mask_goal].y, df_pass[mask_goal].end_x, df_pass[mask_goal].end_y,
            lw=8, comet=True, cmap='Blues',
            label='pass leading to shot', ax=axs)

    # Plot the goals
    pitch.scatter(df_pass[mask_goal].end_x, df_pass[mask_goal].end_y, s=250,
              marker='football', edgecolors='black', c='white', zorder=2,
              label='goal', ax=axs)
    # pitch.scatter(df_pass[~mask_goal].end_x, df_pass[~mask_goal].end_y,
    #           edgecolors='white', c='#22312b', s=200, zorder=2,
    #           label='shot', ax=axs)

    # endnote and title
    axs.set_title(f"{team_name}'s passes leading to goals", color='black', fontsize=14,fontweight = 'bold')

    # set legend
    axs.legend(facecolor='gray', edgecolor='white', loc='lower center',fontsize=12)

    return fig


@st.cache_data
def plot_xg_vs_goals(df, team_name):
    # Filter team data for shots
    team_data = df[(df['team_name'] == team_name) & (df['type_name'] == 'Shot')]

    # Group by match and sum xG and actual goals
    match_xg = team_data.groupby('match_id').agg({'shot_statsbomb_xg': 'sum', 'outcome_name': lambda x: (x == 'Goal').sum()}).reset_index()
    match_xg.rename(columns={'shot_statsbomb_xg': 'Total xG', 'outcome_name': 'Actual Goals'}, inplace=True)

    # Plot bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    match_xg.set_index('match_id')[['Total xG', 'Actual Goals']].plot(kind='bar', ax=ax, color=['gray', 'green'])
    ax.set_ylabel("Goals / xG")
    ax.set_title(f"xG vs. Actual Goals - {team_name}")

    return fig

@st.cache_data
def plot_possession_share(df, team_name):
    # Filter data for the selected team
    team_data = df[df['team_name'] == team_name]

    # Define pitch thirds (StatsBomb pitch range: x from 0 to 120)
    defensive_third = team_data[team_data['x'] < 40]
    middle_third = team_data[(team_data['x'] >= 40) & (team_data['x'] <= 80)]
    attacking_third = team_data[team_data['x'] > 80]

    # Count passes in each third
    possession_counts = [len(defensive_third), len(middle_third), len(attacking_third)]
    labels = ['Defensive Third', 'Middle Third', 'Attacking Third']
    colors = ['blue', 'orange', 'red']

    # Plot pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(possession_counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.set_title(f'Possession Share by Pitch Zone - {team_name}')
    
    return fig

@st.cache_data
def shot_accuracy(df,team_name):
    team_data = df[df['team_name'] == team_name]

    total_shots = team_data[team_data['type_name'] == 'Shot'].shape[0]
    shots_on_target = team_data[(team_data['type_name'] == 'Shot') & (( team_data['outcome_name'] == 'Goal') | (team_data['outcome_name'] == 'Saved'))].shape[0]

    missed_shots = total_shots - shots_on_target
    shot_accuracy = round((shots_on_target / total_shots) * 100,2) if total_shots > 0 else 0

    # Pie Chart
    fig,ax = plt.subplots(figsize=(6, 6))
    ax.pie([shots_on_target,missed_shots],labels = ["on Taget","Missed"],autopct="%1.1f%%", colors = ["green","red"])
    ax.set_title(f"Shot Accuracy {team_name}")

    return fig

@st.cache_data
def most_dangerous_attacking_players(df,team_name):
    team_data = df[df['team_name'] == team_name]

    ##Count_goals
    goals = team_data[(team_data['type_name'] == 'Shot') & (team_data['outcome_name'] =='Goal')]
    goals_cnt = goals.groupby('player_name').size().reset_index(name = "Goals")

    ## Count assists
    assists = team_data[(team_data['type_name'] == 'Pass') & (team_data['pass_goal_assist'] == True)]
    assists_cnt = assists.groupby('player_name').size().reset_index(name="Assists")

    ## Mergeing goals and assists
    goal_involvements = goals_cnt.merge(assists_cnt,on= 'player_name',how= 'outer').fillna(0)
    goal_involvements['Total Involvements'] = goal_involvements["Goals"] + goal_involvements["Assists"]
    goal_involvements = goal_involvements.sort_values("Total Involvements",ascending = False).head(5)

    ##plotting figure
    fig,ax = plt.subplots(figsize=(10,8))
    ax.bar(goal_involvements['player_name'],goal_involvements["Total Involvements"],color = 'blue')
    ax.set_title("Most Dangerous Players ( Goals + Assists)")
    ax.set_xlabel("Player")
    ax.set_ylabel("Total Goal Involvements")
    ax.set_xticklabels(goal_involvements['player_name'],rotation = 45,ha="right")

    return fig


@st.cache_data
def create_attacker_radar(df, player1_name, player2_name):
    """Create radar chart comparing two attacking players using mplsoccer"""
    # Extract player stats
    player1_stats = extract_att_stats(df, player1_name)
    player2_stats = extract_att_stats(df, player2_name)
    
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


####### Defense charts

@st.cache_data
def fouls_and_cards(df,team_name):
    team_data = df[df['team_name'] == team_name]

    fouls = team_data[team_data["type_name"] == "Foul Committed"].groupby("player_name").size().reset_index(name = "Fouls")
    yellow_fouls = team_data[(team_data["foul_committed_card_name"] == "Yellow Card") | (team_data["foul_committed_card_name"] == "Second Yellow")]
    yellow_fouls_cnt = yellow_fouls.groupby("player_name").size().reset_index(name = "Yellow_fouls")
    yellow_behaviour= team_data[team_data["bad_behaviour_card_name"] == "Yellow Card"]
    yellow_behaviour_cnts = yellow_behaviour.groupby("player_name").size().reset_index(name ="Yellow_behaviour")
    
    yellows = yellow_fouls_cnt.merge(yellow_behaviour_cnts,on = "player_name",how = "outer").fillna(0)
    yellows["total_yellow_cards"] = yellows["Yellow_fouls"] + yellows["Yellow_behaviour"]

    red_fouls = team_data[team_data["foul_committed_card_name"] == "Red Card"]
    red_fouls_cnt = red_fouls.groupby("player_name").size().reset_index(name = "Red_fouls")
    red_behaviour= team_data[team_data["bad_behaviour_card_name"] == "Red Card"]
    red_behaviour_cnts = red_behaviour.groupby("player_name").size().reset_index(name ="Red_behaviour")

    reds = red_fouls_cnt.merge(red_behaviour_cnts,on = "player_name",how = "outer").fillna(0)
    reds["total_red_cards"] = reds["Red_fouls"] + reds["Red_behaviour"]


    foul_stats = fouls.merge(yellows, on="player_name", how="outer").merge(reds, on="player_name", how="outer").fillna(0)
    foul_stats = foul_stats[["player_name","Fouls","total_yellow_cards","total_red_cards"]]
    foul_stats = foul_stats.sort_values(by=["Fouls","total_yellow_cards","total_red_cards"],ascending = False ).head(5)
    colors = ["orange","yellow","red"]

    fig, ax = plt.subplots(figsize=(10,8))
    foul_stats.plot(x="player_name", kind="bar", stacked=False, ax=ax,color = colors,edgecolor="black")
    ax.set_title("Fouls & Cards")
    ax.set_ylabel("Count")
    ax.set_xlabel("Player")

    ax.set_xticklabels(foul_stats['player_name'],rotation = 45,ha="right")

    ax.legend(["Fouls","total_yellow_cards","total_red_cards"], loc = "upper right", title = "Type")

    return fig

@st.cache_data
def pressing_zones(df,team_name):
    team_data = df[df['team_name'] == team_name]

    recoveries = team_data[team_data["type_name"] == "Ball Recovery"]

    high_press = recoveries[recoveries['x'] > 80.00]
    low_block = recoveries[recoveries['x'] <= 30.00]

    pitch = Pitch(pitch_type ='statsbomb',pitch_color="black",line_color='white')
    fig,ax = pitch.draw(figsize=(10,8))

    ax.scatter(high_press["x"],high_press["y"],color = "red",alpha=0.6,label= "High Press Recoveries")
    ax.scatter(low_block["x"],low_block["y"],color = "blue",alpha=0.6,label= "Low Block Recoveries")

    ax.text(10,75,f"Low Blocks: {len(low_block)}",color = "blue",fontsize = 10)
    ax.text(90,75,f"High Press: {len(high_press)}",color = "red",fontsize = 10)

    ax.legend(loc = "lower center",fontsize =10,facecolor = "gray",edgecolor="white",title="Ball Recoveries")

    return fig

@st.cache_data
def duels_won_percent(df,team_name):
    team_data = df[df['team_name'] == team_name]

    total_duels = team_data[team_data['type_name'] == "Duel"].shape[0]

    aerial_lost = team_data[(team_data['type_name'] == 'Duel') & (team_data['sub_type_name'] == "Aerial Lost")].shape[0]
    ground_lost = team_data[(team_data['type_name'] == 'Duel') & (team_data['sub_type_name'] == "Tackle") & ((team_data['outcome_name'] == "Lost Out") | (team_data['outcome_name'] == "Lost In Play"))].shape[0]
    total_lost = aerial_lost + ground_lost 

    total_won = total_duels - total_lost
    duel_win_percent = round((total_won / total_duels)* 100,2) if total_duels > 0 else 0

    fig,ax = plt.subplots(figsize=(6, 6))
    ax.pie([total_won,total_lost], labels = ["Duels Won","Duels Lost"],autopct = "%1.1f%%", colors = ["green","red"])
    ax.set_title(f"Duel Won Percent {team_name} ")

    return fig

@st.cache_data
def most_dangerous_defensive_players(df,team_name):
    team_data = df[df['team_name'] == team_name]

    ## Interceptions count
    interceptions = team_data[(team_data['type_name'] == 'Pass') & (team_data['sub_type_name'] == 'Interception')]
    interception_cnt = interceptions.groupby('player_name').size().reset_index(name='Interception')

    ## Blocks assists
    blocks = team_data[team_data['type_name'] == 'Block']
    blocks_cnt = blocks.groupby('player_name').size().reset_index(name='Block')

    ## Tackles count
    tackles = team_data[(team_data['sub_type_name'] == "Tackle") & ((team_data['outcome_name'] == 'Won') | (team_data['outcome_name'] == 'Success In Play')  | (team_data['outcome_name'] == 'Success Out')) ]
    tackles_cnt = tackles.groupby('player_name').size().reset_index(name='Tackles')

    ## Mergeing goals and assists
    defensive_involvements = tackles_cnt.merge(interception_cnt.merge(blocks_cnt,on= 'player_name',how= 'outer'),on = 'player_name',how = 'outer').fillna(0)
    defensive_involvements['Defensive Contribution'] = defensive_involvements["Interception"] + defensive_involvements["Block"] + defensive_involvements["Tackles"]
    defensive_involvements = defensive_involvements.sort_values("Defensive Contribution",ascending = False).head(5)

    ##plotting figure
    fig,ax = plt.subplots(figsize=(10,8))
    ax.bar(defensive_involvements['player_name'],defensive_involvements["Defensive Contribution"],color = 'blue')
    ax.set_title("Defensive Threat ( Blocks + Tackles + Interceptions)")
    ax.set_xlabel("Player")
    ax.set_ylabel("Defensive Contribution")
    ax.set_xticklabels(defensive_involvements['player_name'],rotation = 45,ha="right")

    return fig

@st.cache_data
def create_def_radar(df, player1_name, player2_name):
    """Create radar chart comparing two attacking players using mplsoccer"""
    # Extract player stats
    player1_stats = extract_def_stats(df, player1_name)
    player2_stats = extract_def_stats(df, player2_name)
    
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

####### GoalKeeping charts

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
