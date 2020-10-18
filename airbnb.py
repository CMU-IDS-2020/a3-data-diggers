import streamlit as st
import pandas as pd
import math
import altair as alt


# Function to remove dollar from price (TBD - move to cleaning later)
def remove_dollar(price):
    return price.replace('$', '').replace(',', '')


# Function to add month to the dataframe
def get_month(date):
    separator = "/"
    if date.__contains__('-'):
        separator = '-'
    month = str(date).split(separator)[1]
    return month


# Function to add year to the dataframe
def get_year(date):
    separator = "/"
    if date.__contains__('-'):
        separator = '-'
    year = str(date).split(separator)[0]
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

    # city to listings dictionary mapping
    city_listings_mapping = {"Washington DC": WDC_listings_dictionary}

    # neighbourhood_mapping TBD
    city_neighbourhood_mapping = {"Washington DC": ['Shaw', 'Capitol Hill', 'Columbia Heights'],
                                  "Austin, Texas": ['N1', 'N2']}

    property_types = ['Townhouse', 'House', 'Other', 'Apartment', 'Guest suite', 'Loft', 'Bed and breakfast',
                      'Barn', 'Condominium', 'Bungalow', 'Guesthouse', 'Serviced apartment', 'Boat', 'Hostel',
                      'Tiny house', 'Boutique hotel', 'Resort', 'Aparthotel', 'Villa', 'Cottage', 'Camper/RV', 'Hotel']

    years = ["2015", "2016", "2017", "2018", "2019", "2020"]

    rental_size = ["Studio", "1", "2", "3", "4", "5+"]

    # DISPLAY STARTS HERE
    st.title("To List or Not To List: A COVID-19 Edition")
    st.markdown('''
        by Nur Yildirim and Shravya Bhat \n
        Interactive Data Science Fall 2020 | Assignment 3 | Carnegie Mellon University
        '''
                )
    st.header("Search Criteria")

    # Select City
    cities = ["Washington DC", "Austin, Texas"]
    city = st.selectbox("City", cities)

    # Get unique neighbourhoods
    unique_neighbourhoods = city_neighbourhood_mapping[city]
    neighbourhood = st.selectbox("Neighbourhood", unique_neighbourhoods)

    # Select property type
    type_property = st.selectbox("Property Type", property_types)

    # Select year
    selected_year = st.selectbox("Year", years, index=5)

    # Select rental size
    size_rental = st.select_slider("Rental Size", rental_size)
    size_rental_internal = 0 if size_rental == 'Studio' else int(size_rental.replace('+', ''))
    st.write(size_rental_internal)

    # Select price range
    min_price = st.slider("Minimum Property Price", 0, 10000, 50, 50, format="$%d")
    max_price = st.slider("Maximum Property Price", 0, 10000, 200, 50, format="$%d")

    # Get the filtered dataframe based on the above criteria
    listings_dict = city_listings_mapping[city]

    filtered_listings = {}
    for month_no in listings_dict.keys():
        df = listings_dict[month_no]

        # host_neighbourhood to be changed to neighbourhood later
        df_filter = df[(df["host_neighbourhood"] == neighbourhood)
                       & (df["property_type"] == type_property)
                       & (df["bedrooms"] == size_rental_internal)
                       & (df["price"] <= max_price) & (df["price"] >= min_price)]

        st.write(df_filter)

        filtered_listings[month_no] = df_filter

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

    st.write("The dataframe shown below consists of aggregate statistics from the filtered dataframes above:")
    st.write(graphing_df)

    one_listing_data = []
    selected_listing_id = st.text_input("Please enter the listing ID you want details for", 93551)
    for fl in filtered_listings.keys():
        fl_df_1 = filtered_listings[fl]
        st.write(fl_df_1[(fl_df_1["id"] == int(selected_listing_id))])


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
