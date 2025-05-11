import streamlit as st # type: ignore
import pandas as pd # type: ignore
from mplsoccer import VerticalPitch,Pitch, Sbopen # type: ignore
import matplotlib.pyplot as plt # type: ignore
from utils.data_prep import get_tournament_data,team_of_the_tournament,preprocess_data
from utils.attackstats import most_goals,most_assist,most_successful_dribbles,most_successful_passes
from utils.defensestats import most_blocks,most_clearance,most_interceptions,most_tackels_won
from utils.goalkeepingstats import save_percentage,most_clean_sheets,most_saves
from utils.charts import most_dangerous_attacking_players,plot_shots,passes_assisted_shot,plot_xg_vs_goals,shot_accuracy,plot_possession_share,create_attacker_radar,fouls_and_cards,pressing_zones,duels_won_percent,most_dangerous_defensive_players,create_def_radar,create_gk_radar

# Page configuration
#st.set_page_config(page_title ="Euro 2024 Analysis",layout="wide",initial_sidebar_state = "expanded")



st.title("Euro 2024 Analysis")




euro_df= get_tournament_data(competition_id=55,season_id=282)


@st.cache_data
def get_all_stats(df):
    return {
        "attack": {
            "Most Goals": most_goals(euro_df),
            "Most Assists": most_assist(euro_df),
            "Most Successful Passes": most_successful_passes(euro_df),
            "Most Successful Dribbles": most_successful_dribbles(euro_df)
        },
        "defense": {
            "Most Tackles": most_tackels_won(euro_df),
            "Most Blocks": most_blocks(euro_df),
            "Most Clearance": most_clearance(euro_df),
            "Most Interceptions": most_interceptions(euro_df)
        },
        "goalkeeping_stats":{
            "Most Clean Sheets": most_clean_sheets(euro_df),
            "Most Saves": most_saves(euro_df),
            "Highest Save %": save_percentage(euro_df)
        }
    }


all_stats = get_all_stats(euro_df)
attack_stats= all_stats["attack"]
defense_stats = all_stats["defense"]
goalkeeping_stats = all_stats["goalkeeping_stats"]

#### Getting team Logos

team_logos={
    "Albania": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Albania.png",
    "Austria": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Austria.png",
    "Belgium": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Belgium.png",
    "Croatia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Croatia.png",
    "Czech_Republic": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Czech_Republic.png",
    "Denmark": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Denmark.png",
    "England": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/England.png",
    "France": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/France.png",
    "Georgia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Georgia.png",
    "Germany": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Germany.png",
    "Hungary": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Hungary.png",
    "Italy": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Italy.png",
    "Netherlands": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Netherlands.png",
    "Poland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Poland.png",
    "Portugal": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Portugal.png",
    "Romania": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Romania.png",
    "Scotland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Scotland.png",
    "Serbia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Serbia.png",
    "Slovakia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Slovakia.png",
    "Slovenia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Slovenia.png",
    "Spain": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Spain.png",
    "Switzerland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Switzerland.png" ,
    "Turkey": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Turkey.png" ,
    "Ukraine": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Ukraine.png"
}

@st.cache_data
def best_performers():
    return {
        "Player of the Tournament": {"player": "Rodri","team": "Spain"},
        "Young Player of the Tournamnent": {"player": "Lamine Yamal","team": "Spain" },
        "Golden Glove" : {"player" : "Mike Maignan","team": "France"}
        
    }

expanded_stats = {
    "Player of the Tournament":{ "Minutes played": "521", "Goals": "1", "Assists": "0", "Passes attempted": "439", "Passes completed": "411", "Passing accuracy": "92.84%"},
    "Young Player of the Tournamnent": {"Minutes played": "507", "Goals": "1", "Assists": "4"},
    "Golden Glove" : {"Clean Sheets": "4"}
}


performers = best_performers()

def best_performers_section(stats):
    with st.container():
        st.title('Best Players in the Tournament')
        st.write(' Highlighting the standout players of Euro 2024 based on their performers.')

        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]

        for idx, (stat_name, stat_data) in enumerate(stats.items()):
            player = stat_data['player']
            team = stat_data['team']

            team_logo = team_logos.get(team, None)

            with columns[idx]:  
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ddd; 
                        border-radius: 10px; 
                        padding: 12px; 
                        margin: 5px 0;
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        background-color: #fff;">
                        <h4 style="margin: 0; font-size: 22px;">{stat_name}</h4>
                        <p style="margin: 5px 0; font-size: 20px;"><b>{player}</b></p>
                        {f'<img src="{team_logo}" width="40">' if team_logo else ""}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        for idx,(stat_name,_) in enumerate(stats.items()):
            with columns[idx]:
                if stat_name in expanded_stats:
                    with st.expander(f"{stat_name}"):
                        for stat,value in expanded_stats[stat_name].items():
                            st.write(f"{stat}: {value}")

## Display the section
best_performers_section(performers)
st.divider()

def display_stats_section(title, stats):
    with st.container():
        st.markdown(f"## {title}")  # Section title

       


        col1, col2, col3 = st.columns(3)  # Arrange in 3 columns

        for idx, (stat_name, stat_data) in enumerate(stats.items()):
            team = stat_data["team"]
            player = stat_data["player"]
            
            # Determine which value to display based on the stat type
            if "goals_scored" in stat_data:
                value = stat_data["goals_scored"]
                value_label = "Goals"
            elif "assists" in stat_data:
                value = stat_data["assists"]
                value_label = "Assists"
            elif "total_passes" in stat_data:
                value = stat_data["total_passes"]
                value_label = "Passes"
            elif "dribbles" in stat_data:
                value = stat_data["dribbles"]
                value_label = "Dribbles"
            elif "tackles" in stat_data:
                value = stat_data["tackles"]
                value_label = "Tackles"
            elif "blocks" in stat_data:
                value = stat_data["blocks"]
                value_label = "Blocks"
            elif "clearances" in stat_data:
                value = stat_data["clearances"]
                value_label = "Clearances"
            elif "interceptions" in stat_data:
                value = stat_data["interceptions"]
                value_label = "Interceptions"
            elif "clean_sheets" in stat_data:
                value = stat_data["clean_sheets"]
                value_label = "Clean Sheets"
            elif "saves" in stat_data:
                value = stat_data["saves"]
                value_label = "Saves"
            elif "save_percent" in stat_data:
                value = f"{stat_data['save_percent']:.1f}%"
                value_label = "Save %"
            else:
                value = ""
                value_label = ""
            
            # Select team logo if available
            team_logo = team_logos.get(team, None)

            # Assign each stat to a column dynamically
            with [col1, col2, col3][idx % 3]:  
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ddd; 
                        border-radius: 10px; 
                        padding: 12px; 
                        margin: 5px 0;
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        background-color: #fff;">
                        <h4 style="margin: 0; font-size: 16px;">{stat_name}</h4>
                        <p style="margin: 0; font-size: 24px; "><b>{value}</b></p>
                        <p style="margin: 5px 0; font-size: 16px;"><b>{player}</b></p>
                        {f'<img src="{team_logo}" width="50">' if team_logo else ""}
                        <p style="margin: 5px 0; font-size: 14px;">{team}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


#  Display sections with borders
display_stats_section("⚽ Attack Stats", attack_stats)
display_stats_section("🛡️ Defense Stats", defense_stats)
display_stats_section("🧤 Goalkeeping Stats", goalkeeping_stats)

st.divider()

tott = team_of_the_tournament()
with st.container():
    st.pyplot(tott)

st.divider()

att_list, def_list, gk_list = preprocess_data(euro_df)




tab1,tab2,tab3 = st.tabs(["Attacking Analysis","Defensive Analysis","GoalKeeping Analysis"])


### Attacking Analysis
with tab1:
    selected_team = st.selectbox("Select a team",euro_df['team_name'].sort_values().unique(),index = 0,key ="att_team")
    st.subheader(f"{selected_team} - Attacking Analysis")
    st.write("Dive into key attacking metrics such asd progressive passes, shot accuracy, goal contributions, and xG analysis")
    

    col1,col2 = st.columns(2)


    top_attacking_players = most_dangerous_attacking_players(euro_df,selected_team)
    xg_vs_goals_fig = plot_xg_vs_goals(euro_df,selected_team)
    shots_fig = plot_shots(euro_df,selected_team)
    pass_fig = passes_assisted_shot(euro_df,selected_team)
    poss_fig = plot_possession_share(euro_df,selected_team)
    shot_acc_fig = shot_accuracy(euro_df,selected_team)

    with col1:
        st.markdown('### Top Goal Contributors')
        st.pyplot(top_attacking_players)
        st.markdown("### xG vs. Actual Goals")
        st.pyplot(xg_vs_goals_fig)
        st.markdown("### Shot Accuracy")
        st.pyplot(shot_acc_fig)

    with col2:
        st.markdown("### Team Shot Map ")
        st.pyplot(shots_fig)
        st.markdown("### Key Passes Leading to Goals")
        st.pyplot(pass_fig)
        st.markdown("### Team Possesion Share")
        st.pyplot(poss_fig)

    
    with st.container():
        st.divider()
        player1 = st.selectbox("Select a first player",att_list,index = 0)
        player2_options = [player for player in att_list if player != player1]
        player2 = st.selectbox("Select a second player",player2_options,index = 0)
        player_data = euro_df[euro_df['player_name'].isin([player1, player2])]
        att_radar = create_attacker_radar(player_data,player1,player2)
        st.markdown('### Defensive Performance Comparison (Radar Chart)')
        st.pyplot(att_radar)

    
### Defensive Analysis
with tab2:
    selected_team = st.selectbox("Select a team",euro_df['team_name'].sort_values().unique(),index = 0,key ="def_team")
    st.subheader(f"{selected_team} - Defensive Analysis")
    st.write("Understanding key defensive metrics like tackles,interceptions,clearances and goalkeeper performance.")
    

    col1,col2 = st.columns(2)


    cards_fig = fouls_and_cards(euro_df,selected_team)
    pressing_fig = pressing_zones(euro_df,selected_team)
    duels_fig = duels_won_percent(euro_df,selected_team)
    defensive_player = most_dangerous_defensive_players(euro_df,selected_team)

    with col1:
        st.markdown('### Top Defensive Players')
        st.pyplot(defensive_player)
        st.markdown("### Fouls and Cards")
        st.pyplot(cards_fig)

    with col2:
        st.markdown('### Duels Won (Aerial & Ground)')
        st.pyplot(duels_fig)
        st.markdown("### Presssing Zones")
        st.pyplot(pressing_fig)


    with st.container():
        st.divider()
        player1 = st.selectbox("Select a first player",def_list,index = 0)
        player2_options = [player for player in def_list if player != player1]
        player2 = st.selectbox("Select a second player",player2_options,index = 0)
        player_data = euro_df[euro_df['player_name'].isin([player1, player2])]
        def_radar = create_def_radar(player_data,player1,player2)
        st.markdown('### Player Performance Comparison (Radar Chart)')
        st.pyplot(def_radar)



### GoalKeeping Analysis
with tab3:
    st.subheader("Comparing Goal Keepers performaces in the tournament")
    st.write("Analyzing the performance of goalkeepers based on key metrics like save, clean sheets, and save percentage.")

    with st.container():
        st.divider()
        player1 = st.selectbox("Select a first player",gk_list,index = 0)
        player2_options = [player for player in gk_list if player != player1]
        player2 = st.selectbox("Select a second player",player2_options,index = 0)
        player_data = euro_df[euro_df['player_name'].isin([player1, player2])]
        gk_radar = create_gk_radar(player_data,player1,player2)
        st.markdown('### Goalkeeper Performance Comparison (Radar Chart)')
        st.pyplot(gk_radar)
