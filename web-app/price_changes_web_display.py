import urllib.request

import gender_guesser.detector as gender
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import xmltodict
from mitosheet.streamlit.v1 import spreadsheet
from pandas import json_normalize
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_lottie import st_lottie
import json

st.set_page_config(page_title="FPL Price Changes", layout="wide")

price_change_animation = json.loads("Animation - 1708274690191.json")
st_lottie(price_change_animation, speed=1, height=200, key="initial")

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.2, 1, 0.1)
)

row0_1.title("Predicting your price changes so you don't have to.")


with row0_2:
    add_vertical_space()

row0_2.subheader(
    "This Website displays the results of the full end-to-end pipeline by Tom Ribaroff."
)

row1_spacer1, row1_1, row1_spacer2 = st.columns((0.1, 3.2, 0.1))

with row1_1:
    st.markdown(
        "At 6pm GMT daily, it displays the predicted price changes for players this evening. There is a subscribe function, for you to add your team number and email, that will enable you to receive email notifications of predicted price changes in your team!"
    )
    st.markdown(
        "**To begin, enter your team ID and your email address to recieve notifications.👇"
    )

row2_spacer1, row2_1, row2_spacer2 = st.columns((0.1, 3.2, 0.1))
with row2_1:
    default_username = st.selectbox(
        "Select Tom's team as a default",
        (
            "3402291"
        ),
    )
    st.markdown("**or**")
    user_input = st.text_input(
        "Input your own team ID"
    )
    need_help = st.expander("Need help? 👉")
    with need_help:
        st.markdown(
            "Having trouble finding your team ID? Head to the [FPL website](https://fantasy.premierleague.com/) and click the Points tab. Your team name will be in the of the webpage url. ie https://fantasy.premierleague.com/entry/3402291/event/10"
        )

    if not user_input:
        user_input = f"{default_username}"


@st.cache_data
def get_user_data(user_input):
    base_url = 'https://fantasy.premierleague.com/api/'
    r_all_players_today = requests.get(base_url+'bootstrap-static/').json()
    overall_events_data = pandas.DataFrame(r_all_players_today['events'])
    current_gameweek = numpy.where(overall_events_data.is_current)[0][0] + 1
    r_my_team = requests.get(base_url+'entry/{}/event/{}/picks/'.format(user_input,current_gameweek)).json()
    return r_my_team


user_input = str(user_input)
contents = get_user_data(user_input=user_input)


line1_spacer1, line1_1, line1_spacer2 = st.columns((0.1, 3.2, 0.1))


with line1_1:
    if contents == empty : # TODO write condition of user inputted team name returning nothing
        st.write(
            "Looks like your team name supplied returned no results - please check you supplied the correct 8-digit number"
        )
        st.stop()

    st.header("Searching for team data for team: **{}**".format(user_input))

# TODO change this all to dataframes rather than dictionary searches 

# Get a list of player IDs from team ID supplied 
my_players_ids = list(map(operator.itemgetter('element'), r_my_team['picks']))

# Get list of all player IDs
total_list_of_players_ids = list(map(operator.itemgetter('id'), r_all_players_today['elements']))

# Makes a list of all players that is TRUE if player is in team ID supplied
boolean_list_of_players_in_my_team = [player in my_players_ids for player in total_list_of_players_ids]

# Use boolean list to exact all info about my players this week 
my_players_total = [item for item, condition in zip(r_all_players_today['elements'], boolean_list_of_players_in_my_team) if condition]

# Print all my player's names
# for players in my_players_total:
#     print(players.get('web_name'))

# TODO display dataframe of 15 rows of players names and IDs 

row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.columns(
    (0.1, 1, 0.1, 1, 0.1)
)

#TODO in left column: players predicted to change tonight 
#TODO in right column: players who changed last night 

# df.to_csv("books_read.csv", index=False)

# with row3_1:
#     st.subheader("Books Read")
#     year_df = pd.DataFrame(df["read_at_year"].dropna().value_counts()).reset_index()
#     year_df.columns = ["Year", "Count"]
#     year_df = year_df.sort_values(by="Year")
#     fig = px.bar(
#         year_df,
#         x="Year",
#         y="Count",
#         title="Books Read by Year",
#         color_discrete_sequence=["#9EE6CF"],
#     )
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
#     st.markdown(
#         "It looks like you've read a grand total of **{} books with {} authors,** with {} being your most read author! That's awesome. Here's what your reading habits look like since you've started using Goodreads.".format(
#             u_books, u_authors, df["book.authors.author.name"].mode()[0]
#         )
#     )


# with row3_2:
#     st.subheader("Book Age")
#     # plots a bar chart of the dataframe df by book.publication year by count in plotly. columns are publication year and count
#     age_df = pd.DataFrame(df["book.publication_year"].value_counts()).reset_index()
#     age_df.columns = ["publication_year", "count"]
#     age_df = age_df.sort_values(by="publication_year")
#     fig = px.bar(
#         age_df,
#         x="publication_year",
#         y="count",
#         title="Books Read by Publication Year",
#         color_discrete_sequence=["#9EE6CF"],
#     )
#     fig.update_xaxes(title_text="Publication Year")
#     fig.update_yaxes(title_text="Count")
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)

#     avg_book_year = str(int(np.mean(pd.to_numeric(df["book.publication_year"]))))
#     row_young = df.sort_values(by="book.publication_year", ascending=False).head(1)
#     youngest_book = row_young["book.title_without_series"].iloc[0]
#     row_old = df.sort_values(by="book.publication_year").head(1)
#     oldest_book = row_old["book.title_without_series"].iloc[0]

#     st.markdown(
#         "Looks like the average publication date is around **{}**, with your oldest book being **{}** and your youngest being **{}**.".format(
#             avg_book_year, oldest_book, youngest_book
#         )
#     )
#     st.markdown(
#         "Note that the publication date on Goodreads is the **last** publication date, so the data is altered for any book that has been republished by a publisher."
#     )

# add_vertical_space()

#TODO subscribe functionality to recieve email notification when model predicts for price changes

# row4_space1, row4_1, row4_space2, row4_2, row4_space3 = st.columns(
#     (0.1, 1, 0.1, 1, 0.1)
# )

# with row4_1:
#     st.subheader("How Do You Rate Your Reads?")
#     rating_df = pd.DataFrame(
#         pd.to_numeric(
#             df[df["rating"].isin(["1", "2", "3", "4", "5"])]["rating"]
#         ).value_counts(normalize=True)
#     ).reset_index()
#     # add a barplot of rating_df by index and rating in plotly, y label is percentage, x label is rating
#     rating_df.columns = ["rating", "percentage"]
#     fig = px.bar(
#         rating_df,
#         x="rating",
#         y="percentage",
#         title="Percentage of Books by Rating",
#         color_discrete_sequence=["#9EE6CF"],
#     )
#     fig.update_xaxes(title_text="Rating")
#     fig.update_yaxes(title_text="Percentage")
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
#     df["rating_diff"] = pd.to_numeric(df["book.average_rating"]) - pd.to_numeric(
#         df[df["rating"].isin(["1", "2", "3", "4", "5"])]["rating"]
#     )

#     difference = np.mean(df["rating_diff"].dropna())
#     row_diff = df[abs(df["rating_diff"]) == abs(df["rating_diff"]).max()]
#     title_diff = row_diff["book.title_without_series"].iloc[0]
#     rating_diff = row_diff["rating"].iloc[0]
#     pop_rating_diff = row_diff["book.average_rating"].iloc[0]

#     if difference > 0:
#         st.markdown(
#             "It looks like on average you rate books **lower** than the average Goodreads user, **by about {} points**. You differed from the crowd most on the book {} where you rated the book {} stars while the general readership rated the book {}".format(
#                 abs(round(difference, 3)), title_diff, rating_diff, pop_rating_diff
#             )
#         )
#     else:
#         st.markdown(
#             "It looks like on average you rate books **higher** than the average Goodreads user, **by about {} points**. You differed from the crowd most on the book {} where you rated the book {} stars while the general readership rated the book {}".format(
#                 abs(round(difference, 3)), title_diff, rating_diff, pop_rating_diff
#             )
#         )

# with row4_2:
#     st.subheader("How do Goodreads Users Rate Your Reads?")
#     df["book.average_rating"] = pd.to_numeric(df["book.average_rating"])
#     fig = px.histogram(
#         df,
#         x="book.average_rating",
#         title="Goodreads User Ratings",
#         color_discrete_sequence=["#9EE6CF"],

#     )
#     fig.update_xaxes(title_text="Average Rating")
#     fig.update_yaxes(title_text="Count")
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
#     st.markdown(
#         "Here is the distribution of average rating by other Goodreads users for the books that you've read. Note that this is a distribution of averages, which explains the lack of extreme values!"
#     )

# add_vertical_space()
# row5_space1, row5_1, row5_space2, row5_2, row5_space3 = st.columns(
#     (0.1, 1, 0.1, 1, 0.1)
# )

# with row5_1:
#     st.subheader("Book Length Distribution")
#     df['book.num_pages'] = pd.to_numeric(df['book.num_pages'])
#     fig = px.histogram(
#         df,
#         x="book.num_pages",
#         title="Book Length Distribution",
#         color_discrete_sequence=["#9EE6CF"],
#     )
#     fig.update_xaxes(title_text="Number of Pages")
#     fig.update_yaxes(title_text="Count")
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)

#     book_len_avg = round(np.mean(pd.to_numeric(df["book.num_pages"].dropna())))
#     book_len_max = pd.to_numeric(df["book.num_pages"]).max()
#     row_long = df[pd.to_numeric(df["book.num_pages"]) == book_len_max]
#     longest_book = row_long["book.title_without_series"].iloc[0]

#     st.markdown(
#         "Your average book length is **{} pages**, and your longest book read is **{} at {} pages!**.".format(
#             book_len_avg, longest_book, int(book_len_max)
#         )
#     )


# with row5_2:
#     st.subheader("How Quickly Do You Read?")
#     df["read_at"] = pd.to_datetime(df["read_at"], errors="coerce")
#     df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
#     valid_dates_df = df.dropna(subset=["read_at", "started_at"])
#     valid_dates_df["days_to_complete"] = (
#         valid_dates_df["read_at"] - valid_dates_df["started_at"]
#     ).dt.days
#     fig = px.histogram(
#         valid_dates_df,
#         x="days_to_complete",
#         title="Days to Complete Distribution",
#         color_discrete_sequence=["#9EE6CF"],
#     )
#     fig.update_xaxes(title_text="Number of Days")
#     fig.update_yaxes(title_text="Count")
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
#     days_to_complete = pd.to_numeric(valid_dates_df["days_to_complete"].dropna())
#     time_len_avg = 0
#     if len(days_to_complete):
#         time_len_avg = round(np.mean(days_to_complete))
#     st.markdown(
#         "On average, it takes you **{} days** between you putting on Goodreads that you're reading a title, and you getting through it! Now let's move on to a gender breakdown of your authors.".format(
#             time_len_avg
#         )
#     )

# add_vertical_space()
# row6_space1, row6_1, row6_space2, row6_2, row6_space3 = st.columns(
#     (0.1, 1, 0.1, 1, 0.1)
# )

# with row6_1:
#     st.subheader("Gender Breakdown")
#     # gender algo
#     d = gender.Detector()
#     new = df["book.authors.author.name"].str.split(" ", n=1, expand=True)
#     df["first_name"] = new[0]
#     df["author_gender"] = df["first_name"].apply(d.get_gender)
#     df.loc[df["author_gender"] == "mostly_male", "author_gender"] = "male"
#     df.loc[df["author_gender"] == "mostly_female", "author_gender"] = "female"

#     author_gender_df = pd.DataFrame(
#         df["author_gender"].value_counts(normalize=True)
#     ).reset_index()
#     # plot bar plot of gender by percentage in plotly
#     author_gender_df.columns = ["Gender", "Percentage"]
#     fig = px.bar(
#         author_gender_df,
#         x="Gender",
#         y="Percentage",
#         title="Percentage of Books by Gender",
#         color_discrete_sequence=["#9EE6CF"],
#     )
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
#     st.markdown(
#         "To get the gender breakdown of the books you have read, this next bit takes the first name of the authors and uses that to predict their gender. These algorithms are far from perfect, and tend to miss non-Western/non-English genders often so take this graph with a grain of salt."
#     )
#     st.markdown(
#         "Note: the package I'm using for this prediction outputs 'andy', which stands for androgenous, whenever multiple genders are nearly equally likely (at some threshold of confidence). It is not, sadly, a prediction of a new gender called andy."
#     )

# with row6_2:
#     st.subheader("Gender Distribution Over Time")
#     year_author_df = pd.DataFrame(
#         df.groupby(["read_at_year"])["author_gender"].value_counts(normalize=True)
#     )
#     year_author_df.columns = ["Percentage"]
#     year_author_df.reset_index(inplace=True)
#     year_author_df = year_author_df[year_author_df["read_at_year"] != ""]
#     year_author_df["read_at_year"] = pd.to_datetime(year_author_df["read_at_year"])
#     # plot line plot in plotly of year_author_df with x axis as read_at_year, y axis is percentage, color is author gender
#     fig = px.line(
#         year_author_df,
#         x="read_at_year",
#         y="Percentage",
#         color="author_gender",
#         title="Percent of Books by Gender Over Time",
#     )
#     fig.update_xaxes(title_text="Year Read")
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)
#     st.markdown(
#         "Here you can see the gender distribution over time to see how your reading habits may have changed."
#     )
#     st.markdown(
#         "Want to read more books written by women? [Here](https://www.penguin.co.uk/articles/2019/mar/best-books-by-female-authors.html) is a great list from Penguin that should be a good start (I'm trying to do better at this myself!)."
#     )

# add_vertical_space()
# row7_spacer1, row7_1, row7_spacer2 = st.columns((0.1, 3.2, 0.1))

# with row7_1:
#     st.header("**Book List Recommendation for {}**".format(user_name))
#     reco_df = pd.read_csv("recommendations_df.csv")
#     unique_list_books = df["book.title"].unique()
#     reco_df["did_user_read"] = reco_df["goodreads_title"].isin(unique_list_books)
#     most_in_common = (
#         pd.DataFrame(reco_df.groupby("recommender_name").sum())
#         .reset_index()
#         .sort_values(by="did_user_read", ascending=False)
#         .iloc[0][0]
#     )
#     avg_in_common = (
#         pd.DataFrame(reco_df.groupby("recommender_name").mean())
#         .reset_index()
#         .sort_values(by="did_user_read", ascending=False)
#         .iloc[0][0]
#     )
#     most_recommended = reco_df[reco_df["recommender_name"] == most_in_common][
#         "recommender"
#     ].iloc[0]
#     avg_recommended = reco_df[reco_df["recommender_name"] == avg_in_common][
#         "recommender"
#     ].iloc[0]

#     def get_link(recommended):
#         if "-" not in recommended:
#             link = "https://bookschatter.com/books/" + recommended
#         elif "-" in recommended:
#             link = "https://www.mostrecommendedbooks.com/" + recommended + "-books"
#         return link

#     st.markdown(
#         "For one last bit of analysis, we scraped a few hundred book lists from famous thinkers in technology, media, and government (everyone from Barack and Michelle Obama to Keith Rabois and Naval Ravikant). We took your list of books read and tried to recommend one of their lists to book through based on information we gleaned from your list"
#     )
#     st.markdown(
#         "You read the most books in common with **{}**, and your book list is the most similar on average to **{}**. Find their book lists [here]({}) and [here]({}) respectively.".format(
#             most_in_common,
#             avg_in_common,
#             get_link(most_recommended),
#             get_link(avg_recommended),
#         )
#     )


#     st.markdown("***")
#     st.markdown(
#         "Thanks for going through this mini-analysis with me! I'd love feedback on this, so if you want to reach out you can find me on [twitter](https://twitter.com/tylerjrichards) or my [website](http://www.tylerjrichards.com/)."
#     )


