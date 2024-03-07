import urllib.request

import numpy as np
import pandas as pd
# import plotly.express as px
import requests
import streamlit as st
# import xmltodict
# from mitosheet.streamlit.v1 import spreadsheet
from pandas import json_normalize
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_lottie import st_lottie
import json
import os

from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from datetime import date

animation_filename = "Animation - 1708274690191.json"

with open(animation_filename, "r") as file:
    price_change_animation = json.load(file)

st_lottie(price_change_animation, speed=1, height=200, key="initial")

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.2, 1, 0.1)
)

row0_1.title("Predicting your FPL price changes so you don't have to.")


with row0_2:
    add_vertical_space()

row0_2.subheader(
    "This Website displays the results of the full end-to-end pipeline by Tom Ribaroff."
)

row1_spacer1, row1_1, row1_spacer2 = st.columns((0.1, 3.2, 0.1))

with row1_1:
    st.subheader(
        "Predictions made using a LightGBM model trained on past overnight price changes"
    )


row1_5_space1, row1_5_1, row1_5_space2,= st.columns(
    (1, 1.6, 1)
)

with row1_5_1:
    st.write("--------------------------------")
    st.title("Players Predicted to Change Tonight ~1:00GMT:")
    # Dummy Data
    st.table(
        pd.DataFrame.from_dict(
        {"player_id": ["17", "56476"], 
        "web_name": ["Saka", "Watkins"],
        "predicted_price_change": ["increase", "decrease"]
            }
            ))
    
    # pull real predictions from today using FastAPI 

    # today = date.today()

    # # URL for the FastAPI endpoint with today's date
    # url = f"https://your-fastapi-app-url/get_prediction/{today}" #TODO change your-fastapi-app-url to correct public URL (a google run url) or IP address where your FastAPI app is accessible

    # you will need to filter batch prediction results 
    # df[df.predicted_price_change != 0] 

    # # Make a request to the FastAPI endpoint
    # response = requests.get(url)

    # # Check the response and display the result
    # if response.status_code == 200:
    #     prediction_result = response.json()["prediction"]
    #     st.success(f"Prediction for {today}: {prediction_result}")
    # else:
    #     st.error(f"Error: {response.text}")

    st.title("Model Predictions Updated Daily ~6pm GMT")
    st.write("--------------------------------")

@st.cache_data
def get_user_data(user_input):
    base_url = 'https://fantasy.premierleague.com/api/'
    r_all_players_today = requests.get(base_url+'bootstrap-static/').json()
    overall_events_data = pd.DataFrame(r_all_players_today['events'])
    current_gameweek = np.where(overall_events_data.is_current)[0][0] + 1
    r_my_team = requests.get(base_url+'entry/{}/event/{}/picks/'.format(user_input,current_gameweek)).json()
    return r_all_players_today, r_my_team
    

st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')

row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.columns(
    (0.1, 1, 0.1, 1, 0.1)
)

st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')

with row3_1:


    st.title("Let's have a look at the players in your team this week:")
    default_username = st.selectbox(
        "Select Tom's team as a default",
        [
            "3402291"
        ],
    )
    st.markdown("**or**")
    user_input = st.text_input(
        "or Input your own team ID"
    )
    need_help = st.expander("Need help finding your team-id? 👉")
    with need_help:
        st.markdown(
            "Having trouble finding your team ID? Head to the [FPL website](https://fantasy.premierleague.com/) and click the Points tab. Your team name will be in the of the webpage url. ie https://fantasy.premierleague.com/entry/3402291/event/10"
        )

    if not user_input:
        user_input = f"{default_username}"



    user_input = str(user_input)
    contents, team = get_user_data(user_input=user_input)

    if team == {'detail': 'Not found.'} :
        st.write(
            "Looks like your team name supplied returned no results - please check you supplied the correct number"
        )
        st.stop()

    st.write("Searching for team data for team: **{}**".format(user_input))

    # Get a list of player IDs from team ID supplied 
    players_this_week = pd.DataFrame(team['picks'])

    # Get list of all player IDs
    overall_events_data = pd.DataFrame(contents['events'])
    todays_player_data = pd.DataFrame(contents['elements'])
    total_players = contents['total_players']

    # Get a list of player names using your team player's IDs
    player_names = todays_player_data[[value in players_this_week.element.values for value in todays_player_data.id]]['web_name']

    # Display the names in a nice way
    st.table(player_names)

with row3_2:
    st.title("Players Who Changed Last Night:")

    # Dummy Data 
    st.table(
        pd.DataFrame.from_dict(
        {"player_id": ["506", "576"], 
         "web_name": ["Haaland", "Gordon"]
              }
              ))
    
    # pull real price changes from yesterday using FastAPI

    # URL for the FastAPI endpoint to get yesterday's results
    # url = "https://your-fastapi-app-url/get_yesterday_results"  # Replace with the actual URL

    # # Make a request to the FastAPI endpoint
    # response = requests.get(url)

    # # Check the response and display the results
    # if response.status_code == 200:
    #     result_data = response.json()["players_predicted_to_change_price"]

    #     # Display the results using a DataFrame or any other appropriate method
    #     if result_data:
    #         df = pd.DataFrame(result_data)
    #         st.dataframe(df)
    #     else:
    #         st.warning("No results found for yesterday.")
    # else:
    #     st.error(f"Error: {response.text}")

    
row2_spacer1, row2_1, row2_spacer2 = st.columns((2, 3.2, 2))
with row2_1:
    st.write("----------------------------")
    st.subheader("Add your team number and email")
    st.title("↓")
    st.subheader("Subscribe for Email Notifications")
    st.title("↓")
    st.subheader("Receive email notifications of predicted price changes in your team!")
    st.write("----------------------------")
    
st.title("Would you like to subscribe to recieve email updates when we predict a price change in your team?:")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "fpl-price-change-subscription-firebase-admin.json"

# Check if Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase app
    cred = credentials.Certificate("fpl-price-change-subscription-firebase-admin.json")
    firebase_admin.initialize_app(cred)
# Initialize Firestore
db = firestore.Client()

# Streamlit code
email = st.text_input("Enter your email:")
team_id = st.text_input("Enter your team ID:")

if st.button("Subscribe"):
    # Save email and team_id to Firestore
    doc_ref = db.collection("subscribers").add({
        "email": email,
        "team_id": team_id
    })
    st.success("Subscribed successfully!")