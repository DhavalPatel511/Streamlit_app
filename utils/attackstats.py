import matplotlib.pyplot as plt # type: ignore
from mplsoccer import VerticalPitch,Pitch,Radar,grid # type: ignore
from utils.data_prep import get_tournament_data
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