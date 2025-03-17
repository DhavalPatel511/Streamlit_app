import matplotlib.pyplot as plt # type: ignore
from mplsoccer import VerticalPitch,Pitch,Radar,grid # type: ignore
from backend_analysis import get_tournament_data
import streamlit as st # type: ignore



@st.cache_data
def most_goals(df):
    
    df_goals = df.groupby(['team_name','player_name'])['outcome_name'].apply(lambda x: (x=='Goal').sum()).reset_index(name='Goals_scored')
    highest_scorer = df_goals.loc[df_goals["Goals_scored"].idxmax()]

    return {"team": highest_scorer['team_name'],"player":highest_scorer['player_name'], "goals_scored": highest_scorer['Goals_scored']}

@st.cache_data
def most_assist(df):
    
    assists = df[(df['type_name'] == 'Pass') & (df['pass_goal_assist'] == True)]
    assists_cnt = assists.groupby(['team_name','player_name']).size().reset_index(name="Assists")

    if assists_cnt.empty:
        return {"team": None, "player": None, "assists": 0}

    most_assist_player = assists_cnt.loc[assists_cnt["Assists"].idxmax()]

    return {"team": most_assist_player['team_name'],"player": most_assist_player['player_name'], "assists": int(most_assist_player['Assists'])}

@st.cache_data
def most_successful_passes(df):

    successful_passes = df[(df['type_name'] == 'Pass') & (df['outcome_name'].isna())]
    pass_cnt = successful_passes.groupby(['team_name','player_name']).size().reset_index(name="Successful_passes")

    most_successful_pass_player = pass_cnt.loc[pass_cnt["Successful_passes"].idxmax()]

    return {"team":most_successful_pass_player['team_name'],"player":most_successful_pass_player['player_name'],"total_passes": int(most_successful_pass_player['Successful_passes'])}

@st.cache_data
def most_successful_dribbles(df):

    dribbles = df[(df['type_name'] == 'Dribble') & (df['outcome_name'] == 'Complete')]
    dribbles_cnt = dribbles.groupby(['team_name','player_name']).size().reset_index(name="Dribbles")

    if dribbles_cnt.empty:
        return {"team": None, "player": None, "dribbles": 0}

    most_dribbles_player = dribbles_cnt.loc[dribbles_cnt["Dribbles"].idxmax()]

    return {"team": most_dribbles_player['team_name'],"player": most_dribbles_player['player_name'], "dribbles": int(most_dribbles_player['Dribbles'])}


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
def highlight_key_passer(df,team_name):
    team_data = df[(df['type_name'] == "Pass") & (df['team_name'] == team_name)].copy()
    team_data["progressive"] = ((team_data["end_x"] - team_data["x"]) > 0.35 * team_data["x"]) & ((team_data["x"] > 60) | (team_data["end_x"] > 60) & (team_data["end_x"] > 80))

    progessive_passes = team_data[team_data["progressive"]]

    top_passers = progessive_passes.groupby("player_name").size().reset_index(name="progressive_passes")
    top_passers = top_passers.sort_values("progressive_passes",ascending = False).head(3)

    top_passer_names = top_passers['player_name'].tolist()
    top_pass_data = progessive_passes[progessive_passes["player_name"].isin(top_passer_names)]

    pitch = Pitch(pitch_color="black",line_color="white")
    fig,ax = pitch.draw(figsize=(10,8))

    colors =["yellow","cyan","lime"]

    for i,player in enumerate(top_passer_names):
        player_passes = top_pass_data[top_pass_data["player_name"] == player]
        pitch.arrows(player_passes["x"],player_passes["y"],player_passes["end_x"],player_passes["end_y"],ax=ax,
                     color = colors[i],width =2,alpha=0.7,label=f"{player} ({len(player_passes)})")
        

    ax.set_title(f"{team_name} - Key Passess In Opponents's Half",color = "black",fontsize = 14)
    ax.legend(loc="upper left",fontsize = 10,facecolor="gray",edgecolor ="white",title = "Top Playmakers")

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
def extract_att_stats(df,player):
    player_df = df[df['player_name'] == player]

    shots = len(player_df[player_df['type_name'] == 'Shot'])
    goals = len(player_df[(player_df['type_name'] == 'Shot') & (player_df['outcome_name'] == "Goal")])
    xg_total = round(player_df[player_df['type_name'] == 'Shot']['shot_statsbomb_xg'].sum(),2)
    xg_per_shot = xg_total / shots if shots > 0 else 0
    shot_on_target = len(player_df[(player_df['type_name'] == "Shot") & (player_df['outcome_name'] == "Goal") | (player_df['outcome_name'] == "Saved")])
    shot_accuracy = round(shot_on_target / shots * 100,2) if shots > 0 else 0 

    assists = len(player_df[(player_df['type_name'] == "Pass") & (player_df['pass_goal_assist'] == True)])
    crosses = len(player_df[(player_df['type_name'] == "Pass") & (player_df['pass_cross'] == True)])
    successful_crosses = len(player_df[(player_df['type_name'] == "Pass") & (player_df['pass_cross'] == True) & (player_df['outcome_name'].isna())])
    cross_accuracy = round(successful_crosses / crosses * 100,2) if crosses > 0 else 0

    dribbles_attempted = len(player_df[player_df['type_name'] == "Dribble"])
    dribbles_completed = len(player_df[(player_df['type_name'] == "Dribble") & (player_df['outcome_name'] == 'Complete')])
    dribble_success = round(dribbles_completed / dribbles_attempted * 100,2) if  dribbles_attempted > 0 else 0

    total_passes = len(player_df[(player_df['type_name'] == "Pass")])
    successful_passes = len(player_df[(player_df['type_name'] == "Pass") & (player_df['outcome_name'].isna())])
    pass_accuracy = round(successful_passes / total_passes * 100,2) if total_passes > 0 else 0

    att_stats = {
        "Goals": goals,
        "xG Total": xg_total,
        "Shot Accuracy (%)": shot_accuracy,
        "Assists": assists,
        "Cross Accuracy (%)": cross_accuracy,
        "Dribble Success (%)": dribble_success,
        "Shots": shots,
        "Pass Accuracy (%)": pass_accuracy
    }

    return att_stats

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

# euro_df = get_tournament_data(55,282)
# ss = extract_att_stats(euro_df,"Jamal Musiala")
# print(ss)
# pas = passes_assisted_shot(euro_df,"England")
# pas.show() 
# g = most_goals(euro_df)
# a = most_assist(euro_df)
# sp = most_successful_passes(euro_df)
# sd = most_successful_dribbles(euro_df)

# print(g)
# print(a)
# print(sp)
# print(sd)