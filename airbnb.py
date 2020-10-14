import streamlit as st
import pandas as pd
import altair as alt

@st.cache
def load_data():
    DC202009 = "http://data.insideairbnb.com/united-states/dc/washington-dc/2020-09-21/visualisations/listings.csv"
    return pd.read_csv(DC202009)

df = load_data()

st.title("An Analysis of COVID's effect on Airbnb Listings")
st.markdown('''
    by Nur Yildirim and Shrayva Bhat \n
    Interactive Data Science Fall 2020 | Assignment 3 | Carnegie Mellon University
    '''
    )

st.header("Abstract")
st.markdown("Lorem ipsum dolor sit")

st.write(df)

st.markdown("This is the dataset from the [InsideAirbnb] (http://insideairbnb.com/get-the-data.html/) website.")

# chart
