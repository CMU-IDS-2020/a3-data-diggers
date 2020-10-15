import streamlit as st
import pandas as pd
import altair as alt


@st.cache
def load_data():
    DC202009 = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/listings.csv"
    reviews = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/reviews.csv"

    df_reviews = pd.read_csv(reviews)
    # Calculating + appending month and year to the reviews dataframe
    df_reviews["month"] = df_reviews.apply(lambda row: getMonth(row["date"]), axis=1)
    df_reviews["year"] = df_reviews.apply(lambda row: getYear(row["date"]), axis=1)
    return pd.read_csv(DC202009), df_reviews


# Function to add month to the dataframe
def getMonth(date):
    month = str(date).split('-')[1]
    return month


# Function to add year to the dataframe
def getYear(date):
    year = str(date).split('-')[0]
    return year


if __name__ == "__main__":
    df, df_reviews = load_data()

    st.title("An Analysis of COVID's effect on Airbnb Listings")
    st.markdown('''
        by Nur Yildirim and Shravya Bhat \n
        Interactive Data Science Fall 2020 | Assignment 3 | Carnegie Mellon University
        '''
                )
    st.header("Abstract")
    st.markdown("Lorem ipsum dolor sit")
    st.write(df)
    st.markdown("This is the dataset from the [InsideAirbnb] (http://insideairbnb.com/get-the-data.html/) website.")

    # chart

    # Monthly trends in terms of number of reviews (Could be changed to slider input)
    user_input_year = st.text_input("Please enter a year to view monthly trends for that year", "2020")
    # Get subset of the dataframe for user_input_year
    df_reviews_year = df_reviews[(df_reviews["year"] == user_input_year)]

    chart1_data = pd.DataFrame(df_reviews_year.groupby(['month'])['month'].count())
    chart1_data.columns = ['count']
    chart1_data.reset_index(inplace=True)

    st.write(alt.Chart(chart1_data).mark_line().encode(
        x='month',
        y='count'
    ))

    st.write("We can observe a clear decline from February to April, which was around the time when the pandemic"
             " was at it's peak. The drastic dip shows just how much of an effect COVID-19 had on the number of"
             " people staying in an Airbnb. \n If we look at previous years, there is an increase in reviews during"
             " February, March and April, indicating that it is a time people usually travel. The curves of 2017, "
             " 2018, and 2019 look similar, as do 2014 - 2016. Every couple of years, the curve changes slightly, "
             " but 2020 is drastically different. \n Let's look at the data from 2020 in more detail.")









