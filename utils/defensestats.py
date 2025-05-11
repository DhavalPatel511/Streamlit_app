
import matplotlib.pyplot as plt # type: ignore
from mplsoccer import Pitch,Radar,grid # type: ignore
from utils.data_prep import get_tournament_data
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