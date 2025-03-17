
import matplotlib.pyplot as plt # type: ignore
from mplsoccer import Pitch,Radar,grid # type: ignore
from backend_analysis import get_tournament_data
import streamlit as st # type: ignore



@st.cache_data
def most_interceptions(df):

    interceptions = df[(df['type_name'] == 'Pass') & (df['sub_type_name'] == 'Interception')]
    interception_cnt = interceptions.groupby(['team_name','player_name']).size().reset_index(name='Interception')

    if interception_cnt.empty:
        return {"team": None, "player": None, "interceptions" : 0}

    most_interceptions_player = interception_cnt.loc[interception_cnt['Interception'].idxmax()]

    return {"team":  most_interceptions_player['team_name'], "player": most_interceptions_player['player_name'], "interceptions" : int(most_interceptions_player['Interception'])}

@st.cache_data
def most_blocks(df):

    blocks = df[df['type_name'] == 'Block']
    blocks_cnt = blocks.groupby(['team_name','player_name']).size().reset_index(name='Block')

    if blocks_cnt.empty:
        return {"team": None, "player": None, "blocks" : 0}

    most_blocks_player = blocks_cnt.loc[blocks_cnt['Block'].idxmax()]

    return {"team":  most_blocks_player['team_name'], "player": most_blocks_player['player_name'], "blocks" : int(most_blocks_player['Block'])}

@st.cache_data
def most_clearance(df):

    clearances = df[df['type_name'] == 'Clearance']
    clearances_cnt = clearances.groupby(['team_name','player_name']).size().reset_index(name='Clearrance')

    if clearances_cnt.empty:
        return {"team": None, "player": None, "clearances" : 0}

    most_clearances_player = clearances_cnt.loc[clearances_cnt['Clearrance'].idxmax()]

    return {"team":  most_clearances_player['team_name'], "player": most_clearances_player['player_name'], "clearances" : int(most_clearances_player['Clearrance'])}

@st.cache_data
def most_tackels_won(df):

    tackles = df[(df['sub_type_name'] == "Tackle") & ((df['outcome_name'] == 'Won') | (df['outcome_name'] == 'Success In Play')  | (df['outcome_name'] == 'Success Out')) ]
    tackles_cnt = tackles.groupby(['team_name','player_name']).size().reset_index(name='Tackles')

    if tackles_cnt.empty:
        return {"team": None, "player": None, "tackles" : 0}

    most_tackles_player = tackles_cnt.loc[tackles_cnt['Tackles'].idxmax()]

    return {"team":  most_tackles_player['team_name'], "player": most_tackles_player['player_name'], "tackles" : int(most_tackles_player['Tackles'])}


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
def extract_def_stats(df,player):
    player_df = df[df['player_name'] == player]

    tackles_attempted = len(player_df[player_df['type_name'] == "Duel"])
    tackles_won = len(player_df[(player_df['type_name'] == "Duel") & (player_df['outcome_name'].isna())])
    tackle_success = round(tackles_won / tackles_attempted * 100,2) if tackles_attempted> 0 else 0 

    interceptions = len(player_df[player_df['type_name'] == "Interception"])
    clearances = len(player_df[player_df['type_name'] == "Clearance"])
    blocks = len(player_df[player_df['type_name'] == "Block"])
    ball_recoveries = len(player_df[player_df['type_name'] == "Ball Recovery"])

    aerials_duels = len(player_df[(player_df['type_name'] == "Duel") & (player_df['aerial_won'].notna())])
    aerial_wins = len(player_df[(player_df['type_name'] == "Duel") & (player_df['aerial_won'] == True)])
    aerial_success = round(aerial_wins / aerials_duels * 100,2) if aerials_duels > 0 else 0 

    total_passes = len(player_df[(player_df['type_name'] == "Pass")])
    successful_passes = len(player_df[(player_df['type_name'] == "Pass") & (player_df['outcome_name'].isna())])
    pass_accuracy = round(successful_passes / total_passes * 100,2) if total_passes > 0 else 0

    def_stats = {
        "Tackles Won": tackles_won,
        "Tackles Success (%)": tackle_success,
        "Interceptions": interceptions,
        "Clearances": clearances,
        "Blocks": blocks,
        "Ball Recovery": ball_recoveries,
        "Aerial Success (%)": aerial_success,
        "Pass Accuracy (%)": pass_accuracy
    }

    return def_stats

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

# euro_df = get_tournament_data(55,282)
# defs = extract_def_stats(euro_df,"Kyle Walker")
# print(defs)
# fig1 = fouls_and_cards(euro_df,"Germany")
# plt.show()
#f = most_fouls(euro_df)
# t = most_tackels_won(euro_df)
# c = most_clearance(euro_df)
# b = most_blocks(euro_df)
# i = most_interceptions(euro_df)

# print(f)
# print(t)
# print(c)
# print(b)
# print(i)