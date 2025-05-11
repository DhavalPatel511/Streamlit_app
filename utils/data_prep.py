import pandas as pd # type: ignore
from mplsoccer import Sbopen,VerticalPitch # type: ignore
import streamlit as st # type: ignore
import matplotlib.pyplot as plt # type: ignore
import requests # type: ignore
from io import BytesIO

sb = Sbopen()
competitions = sb.competition()
competition_id = 55 ## Euro Cup
season_id = 282 ## 2024 Mens Euro Cup

@st.cache_data
def get_tournament_data(competition_id,season_id):
    matches = sb.match(competition_id = competition_id,season_id = season_id)
    all_events = []
    for match_id in matches['match_id']:
        df_events,df_related, df_freeze, df_tactics = sb.event(match_id)
        df_events['match_id'] = match_id
        all_events.append(df_events)

    df_all_events = pd.concat(all_events,ignore_index= True)
    
    all_lineups=[]
    for match_id in matches['match_id']:
        df_lineup = sb.lineup(match_id)
        all_lineups.append(df_lineup)

    lineups_df = pd.concat(all_lineups,ignore_index= True)

    lineups_df= lineups_df[["player_id","player_nickname"]].drop_duplicates()
    df_all_events = df_all_events.merge(lineups_df,on = 'player_id', how = 'left')

    if 'player_name' in df_all_events.columns:
        df_all_events['player_name'] = df_all_events['player_nickname']
        df_all_events = df_all_events.drop('player_nickname',axis=1)

    return df_all_events


# Load player data
team_tournament = pd.DataFrame({
    "team": ["France","England","Switzerland","France","Spain","Spain","Spain","Spain","Spain","Germany","Spain"],
    "player_name": ["Mike Maignan","Kyle Walker", "Manuel Akanji", "William Saliba","Marc Cucurella", "Rodri", "Dani Olmo", "Fabián Ruiz", "Lamine Yamal", "Jamal Musiala", "Nico Williams"],
    "position": ["Goalkeeper", "Right Back","Right Center Back" , "Left Center Back", "Left Back", "Right Defensive Midfield", "Center Attacking Midfield", "Left Defensive Midfield", "Right Wing", "Center Forward","Left Wing"],
    "position_id": [1,2,3,5,6,9,19,11,22,23,24]
})


team_logos = {
    "England": "https://github.com/DhavalPatel511/Streamlit_app/main/flags/England.png",
    "France": "https://github.com/DhavalPatel511/Streamlit_app/main/flags/France.png",
    "Germany": "https://github.com/DhavalPatel511/Streamlit_app/main/flags/Germany.png",
    "Spain": "https://github.com/DhavalPatel511/Streamlit_app/main/flags/Spain.png",
    "Switzerland": "https://github.com/DhavalPatel511/Streamlit_app/main/flags/Switzerland.png"
}

# Team logos/flags
team_logos = {
    "England": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/England.png",
    "France": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/France.png",
    "Germany": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Germany.png",
    "Spain": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Spain.png",
    "Switzerland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Switzerland.png"
}

@st.cache_data
def load_flag_images(df, logo_dict):
    """Load and cache team flags from GitHub URLs"""
    flag_images = []
    for _, row in df.iterrows():
        team = row['team']
        img_url = logo_dict.get(team, None)
        
        if img_url:
            try:
                response = requests.get(img_url)
                img = plt.imread(BytesIO(response.content))
            except:
                img = None  # Instead of a broken placeholder
        else:
            img = None  # No logo available

        flag_images.append(img)
    
    return flag_images

@st.cache_data
def team_of_the_tournament():
    flag_images = load_flag_images(team_tournament, team_logos)
    formation = '4-2-1-3'
    # Create pitch
    pitch = VerticalPitch(goal_type='box', pitch_color='grass', line_color='white',stripe = True)
    fig, ax = pitch.draw(figsize=(6,8))

    # Add title
    fig.suptitle('TEAM OF THE TOURNAMENT', fontsize=16, fontweight='bold')

    # Add player names with line breaks for better display
    ax_text = pitch.formation(formation, positions=team_tournament.position_id, kind='text',
    text=team_tournament.player_name.str.replace(' ', '\n'),fontweight = 'bold',color = 'Blue',
    va='center', ha='center', fontsize=8, ax=ax,xoffset=-3.5)

    # Add flag images with offset to the left
    ax_images = pitch.formation(formation, positions=team_tournament.position_id, 
    kind='image',image=flag_images,height=3.5,ax=ax,xoffset=-7.5)

    # Add player position markers
    ax_scatter = pitch.formation(formation, positions=team_tournament.position_id, kind='scatter',s=80,
    color='gray', edgecolors='black',linewidth=1,ax=ax)

    return fig

@st.cache_data
def preprocess_data(df):
    not_att_pos = ['Goalkeeper', 'Left Back', 'Right Back', 'Center Back', 'Left Center Back', 'Right Center Back', 'Left Wing Back', 'Right Wing Back']
    att_list = df[~df['position_name'].isin(not_att_pos)]['player_name'].dropna().sort_values().unique()
    def_pos = ['Left Back', 'Right Back', 'Center Back', 'Left Center Back', 'Right Center Back', 'Left Wing Back', 'Right Wing Back']
    def_list = df[df['position_name'].isin(def_pos)]['player_name'].sort_values().unique()
    gk_list = df.loc[df['position_name'] == "Goalkeeper", 'player_name'].sort_values().unique()
    return att_list, def_list, gk_list 

#team_fig = team_of_the_tournament()
#team_fig.show()

# Example 
#df_all_events= get_tournament_data(55,282)

#print(df_all_events.head(5))