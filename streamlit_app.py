import streamlit as st
import pandas as pd
import math
import altair as alt
import numpy as np

st.beta_set_page_config(layout="wide")


# Function to remove dollar from price (TBD - move to cleaning later)
def remove_dollar(price):
    return price.replace('$', '').replace(',', '')


# Function to add month to the dataframe
def get_month(date):
    separator = "/"
    if date.__contains__('-'):
        separator = '-'
    month_x = str(date).split(separator)[0]
    return month_x


# Function to add year to the dataframe
def get_year(date):
    separator = "/"
    if date.__contains__('-'):
        separator = '-'
    year = str(date).split(separator)[2]
    return year


@st.cache  # add caching so we load the data only once
def load_data():  # Load the airbnb data acquired from InsideAirbnb.com
    # Server
    # root_path = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/data/"
    # reviews = {'WDC': pd.read_csv(root_path + 'WDC_reviews.csv')}
    # WDC_listings = {'01': pd.read_csv(root_path + '2020/WDC/listings_01.csv'),
    #                 '02': pd.read_csv(root_path + '2020/WDC/listings_02.csv'),
    #                 '03': pd.read_csv(root_path + '2020/WDC/listings_03.csv'),
    #                 '04': pd.read_csv(root_path + '2020/WDC/listings_04.csv'),
    #                 '05': pd.read_csv(root_path + '2020/WDC/listings_05.csv'),
    #                 '06': pd.read_csv(root_path + '2020/WDC/listings_06.csv'),
    #                 '08': pd.read_csv(root_path + '2020/WDC/listings_08.csv'),
    #                 '09': pd.read_csv(root_path + '2020/WDC/listings_09.csv')}

    # Local
    # root_path = "/Users/nur/Documents/Interactive Data Science/a3-data-diggers/data/"
    root_path = "/Users/shravya/Documents/CMU/Interactive_Data_Science/Assignments/3/Code2/data/"
    reviews = {'WDC': pd.read_csv(root_path + 'WDC_reviews.csv')}
    WDC_listings = {'01': pd.read_csv(root_path + '2020/WDC/listings_01.csv'),
                    '02': pd.read_csv(root_path + '2020/WDC/listings_02.csv'),
                    '03': pd.read_csv(root_path + '2020/WDC/listings_03.csv'),
                    '04': pd.read_csv(root_path + '2020/WDC/listings_04.csv'),
                    '05': pd.read_csv(root_path + '2020/WDC/listings_05.csv'),
                    '06': pd.read_csv(root_path + '2020/WDC/listings_06.csv'),
                    '08': pd.read_csv(root_path + '2020/WDC/listings_08.csv'),
                    '09': pd.read_csv(root_path + '2020/WDC/listings_09.csv')}

    # Calculating + appending month and year to the reviews dataframe
    for key in reviews.keys():
        rdf = reviews[key]
        rdf["month"] = rdf.apply(lambda row: get_month(row["date"]), axis=1)
        rdf["year"] = rdf.apply(lambda row: get_year(row["date"]), axis=1)
        reviews[key] = rdf

    # Removing dollar from price, removing nan
    for key in WDC_listings.keys():
        ldf = WDC_listings[key]
        ldf["price"] = ldf["price"].fillna(0)
        ldf["price"] = ldf.apply(lambda row: remove_dollar(row["price"]), axis=1)
        ldf["price"] = pd.to_numeric(ldf["price"])
        WDC_listings[key] = ldf
        ldf['host_neighbourhood'] = ldf['host_neighbourhood'].fillna("other")
        ldf['property_type'] = ldf['property_type'].fillna("other")
        ldf['bedrooms'] = ldf['bedrooms'].fillna(0)

    return reviews, WDC_listings


if __name__ == "__main__":
    reviews_dictionary, WDC_listings_dictionary = load_data()

    month_number_mapping = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May",
                            "06": "June", "07": "July", "08": "August", "09": "September", "10": "October",
                            "11": "November", "12": "December"}

    # city to listings dictionary mapping
    city_listings_mapping = {"Washington DC": WDC_listings_dictionary}
    # neighbourhood_mapping TBD
    city_neighbourhood_mapping = {"Washington DC": ['All', 'Shaw', 'Capitol Hill', 'Columbia Heights',
                                                    'U Street Corridor']}
    room_types = ['All', 'Entire home/apt', 'Private room', 'Shared room', 'Hotel room']
    years = ["2015", "2016", "2017", "2018", "2019", "2020"]
    rental_size = ["All", "Studio", "1", "2", "3", "4", "5+"]

    # DISPLAY STARTS HERE
    st.title("To List or Not To List: A COVID-19 Edition")
    st.markdown('''
        by Nur Yildirim and Shravya Bhat \n
        Interactive Data Science Fall 2020 | Assignment 3 | Carnegie Mellon University
        '''
                )

    # Select City
    cities = ["Washington DC"]
    city = st.sidebar.selectbox("City", cities)

    # Get unique neighbourhoods
    unique_neighbourhoods = city_neighbourhood_mapping[city]
    neighbourhood = st.sidebar.selectbox("Neighbourhood", unique_neighbourhoods)

    # Select room type
    type_room = st.sidebar.selectbox("Room Type", room_types)

    # Select year
    selected_year = st.sidebar.selectbox("Year", years, index=5)

    # Select rental size
    size_rental = st.sidebar.select_slider("Rental Size", rental_size)
    size_rental_internal = None
    if size_rental != 'All':
        size_rental_internal = 0 if size_rental == 'Studio' else int(size_rental.replace('+', ''))

    # Select price range
    min_price = st.sidebar.slider("Minimum Property Price", 0, 10000, 0, 500, format="$%d")
    max_price = st.sidebar.slider("Maximum Property Price", 0, 10000, 10000, 500, format="$%d")

    # Get the filtered dataframe based on the above criteria
    listings_dict = city_listings_mapping[city]

    filtered_listings = {}
    for month_no in listings_dict.keys():
        df = listings_dict[month_no]
        # host_neighbourhood to be changed to neighbourhood later
        df_filter = df
        if neighbourhood != 'All':
            df_filter = df[(df["host_neighbourhood"] == neighbourhood)]
        if type_room != 'All':
            df_filter = df_filter[(df_filter["room_type"] == type_room)]
        if size_rental_internal is not None:
            df_filter = df_filter[(df["bedrooms"] == size_rental_internal)]
        df_filter = df_filter[(df["price"] <= max_price) & (df["price"] >= min_price)]
        filtered_listings[month_no] = df_filter

    # Combine all filtered listings into one dataframe
    all_filtered_listings = pd.concat([filtered_listings['02'], filtered_listings['03'],
                                       filtered_listings['04'], filtered_listings['05'],
                                       filtered_listings['06'], filtered_listings['08'],
                                       filtered_listings['09']], ignore_index=True)
    all_filtered_listings.drop_duplicates(subset=['id'], inplace=True, keep='last')
    # Get total number of filtered listings
    total_filtered_listings = len(all_filtered_listings.axes[0])
    st.write("Number of listings: " + str(total_filtered_listings))
    # Showing map with all the filtered listings
    st.map(all_filtered_listings)

    # Get median price, no_of reviews
    median_price = []
    number_of_listings = []
    month = []
    for fl in filtered_listings.keys():
        fl_df = filtered_listings[fl]
        month.append(fl)
        fl_median = fl_df['price'].median()

        if math.isnan(fl_median):
            fl_median = 0
        median_price.append(fl_median)
        # median_price becomes nan when the dataframe is empty
        fl_listings = len(fl_df.axes[0])
        number_of_listings.append(fl_listings)

    graphing_dict = {"month": month, "median price": median_price, "number of listings": number_of_listings}
    graphing_df = pd.DataFrame.from_dict(graphing_dict)

    # View 2
    view2 = alt.Chart(graphing_df).mark_line().encode(
            x='month',
            y='median price'
        ).properties(
            width=600, height=400
        ).interactive()

    st.write(view2)

    # View 3
    # Get unique listing IDs from all_filtered_listings
    listing_id_list = all_filtered_listings['id'].tolist()
    reviews_city = reviews_dictionary['WDC']
    df_reviews_year = reviews_city[(reviews_city["year"] == '20')]
    df_reviews_year = df_reviews_year[(df_reviews_year["listing_id"].isin(listing_id_list))]
    reviews_chart = pd.DataFrame(df_reviews_year.groupby(['month'])['month'].count())
    reviews_chart.columns = ['count']
    reviews_chart.reset_index(inplace=True)
    view3 = alt.Chart(reviews_chart).mark_line().encode(
         x='month',
         y='count'
    ).properties(
         width=600, height=400
    ).interactive()

    st.write(view3)

    # View 4
    view4 = alt.Chart(graphing_df).mark_line().encode(
        x='month',
        y='number of listings'
    ).properties(
        width=600, height=400
    ).interactive()

    st.write(view4)

    one_listing_data = []
    selected_listing_id = st.text_input("Please enter the listing ID you want details for", 93551)
    for fl in filtered_listings.keys():
        fl_df_1 = filtered_listings[fl]



    # # OLD: chart
    #
    # # Monthly trends in terms of number of reviews (Could be changed to slider input)
    # user_input_year = st.text_input("Please enter a year to view monthly trends for that year", "2020")
    # # Get subset of the dataframe for user_input_year
    # df_reviews_year = df_reviews[(df_reviews["year"] == user_input_year)]
    #
    # chart1_data = pd.DataFrame(df_reviews_year.groupby(['month'])['month'].count())
    # chart1_data.columns = ['count']
    # chart1_data.reset_index(inplace=True)
    #
    # reviewsPlot = alt.Chart(chart1_data).mark_line().encode(
    #     x='month',
    #     y='count'
    # ).properties(
    #     width=600, height=400
    # ).interactive()
    #
    # st.write(reviewsPlot)
    #
    # st.write("We can observe a clear decline from February to April, which was around the time when the pandemic"
    #          " was at it's peak. The drastic dip shows just how much of an effect COVID-19 had on the number of"
    #          " people staying in an Airbnb. \n If we look at previous years, there is an increase in reviews during"
    #          " February, March and April, indicating that it is a time people usually travel. The curves of 2017, "
    #          " 2018, and 2019 look similar, as do 2014 - 2016. Every couple of years, the curve changes slightly, "
    #          " but 2020 is drastically different. \n Let's look at the data from 2020 in more detail.")
    #
