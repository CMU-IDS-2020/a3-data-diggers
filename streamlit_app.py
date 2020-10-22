import streamlit as st
import pandas as pd
import math
import altair as alt
import numpy as np
import pydeck as pdk

st.beta_set_page_config(layout="wide")


# Function to remove dollar from price (TBD - move to cleaning later)
def remove_dollar(price):
    return price.replace('$', '').replace(',', '')


# Function to add month to the dataframe
def get_month(date):
    separator = "/"
    if date.__contains__('-'):
        separator = '-'
    month_x = str(date).split(separator)[1]
    return month_x


# Function to add year to the dataframe
def get_year(date):
    separator = "/"
    if date.__contains__('-'):
        separator = '-'
    year = str(date).split(separator)[0]
    return year


def get_coordinates(lat, lon):
    coordinates_list = list()
    coordinates_list.append(lat)
    coordinates_list.append(lon)
    return coordinates_list


@st.cache  # add caching so we load the data only once
def load_data():  # Load the airbnb data acquired from InsideAirbnb.com
    # Server
    root_path = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/data/"
    reviews = {'NYC': pd.read_csv(root_path + 'NYC_reviews.csv')}
    NYC_listings = {'01': pd.read_csv(root_path + '2020/NYC/listings_01.csv'),
                    '02': pd.read_csv(root_path + '2020/NYC/listings_02.csv'),
                    '03': pd.read_csv(root_path + '2020/NYC/listings_03.csv'),
                    '04': pd.read_csv(root_path + '2020/NYC/listings_04.csv'),
                    '05': pd.read_csv(root_path + '2020/NYC/listings_05.csv'),
                    '06': pd.read_csv(root_path + '2020/NYC/listings_06.csv'),
                    '07': pd.read_csv(root_path + '2020/NYC/listings_07.csv'),
                    '08': pd.read_csv(root_path + '2020/NYC/listings_08.csv'),
                    '09': pd.read_csv(root_path + '2020/NYC/listings_09.csv')}

    # Local
    # root_path = "/Users/nur/Documents/Interactive Data Science/a3-data-diggers/data/"
    # root_path = "/Users/shravya/Documents/CMU/Interactive_Data_Science/Assignments/3/Code2/data/"
    # reviews = {'NYC': pd.read_csv(root_path + 'NYC_reviews.csv')}
    # NYC_listings = {'01': pd.read_csv(root_path + '2020/NYC/listings_01.csv'),
    #                 '02': pd.read_csv(root_path + '2020/NYC/listings_02.csv'),
    #                 '03': pd.read_csv(root_path + '2020/NYC/listings_03.csv'),
    #                 '04': pd.read_csv(root_path + '2020/NYC/listings_04.csv'),
    #                 '05': pd.read_csv(root_path + '2020/NYC/listings_05.csv'),
    #                 '06': pd.read_csv(root_path + '2020/NYC/listings_06.csv'),
    #                 '07': pd.read_csv(root_path + '2020/NYC/listings_07.csv'),
    #                 '08': pd.read_csv(root_path + '2020/NYC/listings_08.csv'),
    #                 '09': pd.read_csv(root_path + '2020/NYC/listings_09.csv')}

    map_data = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/data/2020/NYC/listings_09.csv"

    # Calculating + appending month and year to the reviews dataframe
    for key in reviews.keys():
        rdf = reviews[key]
        rdf["Month"] = rdf.apply(lambda row: get_month(row["date"]), axis=1)
        rdf["year"] = rdf.apply(lambda row: get_year(row["date"]), axis=1)
        reviews[key] = rdf

    # Removing dollar from price, removing nan
    for key in NYC_listings.keys():
        ldf = NYC_listings[key]
        ldf["price"] = ldf["price"].fillna(0)
        ldf["price"] = ldf.apply(lambda row: remove_dollar(row["price"]), axis=1)
        ldf["price"] = pd.to_numeric(ldf["price"])
        ldf['neighbourhood_group_cleansed'] = ldf['neighbourhood_group_cleansed'].fillna("other")
        ldf['room_type'] = ldf['room_type'].fillna("other")
        ldf['bedrooms'] = ldf['bedrooms'].fillna(0)
        NYC_listings[key] = ldf

    # Load in the Covid-19 data
    covid_data = {'09': pd.read_csv(root_path + '2020/COVID/covid_data_cleaned_09.csv')}

    return reviews, NYC_listings, covid_data, map_data


if __name__ == "__main__":
    reviews_dictionary, NYC_listings_dictionary, covid, map_1 = load_data()

    month_number_mapping = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May",
                            "06": "June", "07": "July", "08": "August", "09": "September", "10": "October",
                            "11": "November", "12": "December"}

    # city to listings dictionary mapping
    city_listings_mapping = {"New York City": NYC_listings_dictionary}
    # neighbourhood_mapping TBD
    city_neighbourhood_mapping = {"New York City": ['All', 'Brooklyn', 'Manhattan', 'Queens',
                                                    'Bronx', 'Staten Island']}
    room_types = ['All', 'Entire home/apt', 'Private room', 'Shared room', 'Hotel room']
    # years = ["2015", "2016", "2017", "2018", "2019", "2020"]
    rental_size = ["All", "Studio", "1", "2", "3", "4", "5+"]

    # DISPLAY STARTS HERE
    st.title("To List or Not To List: A COVID-19 Edition")
    st.markdown('''
        by Nur Yildirim and Shravya Bhat \n
        Interactive Data Science Fall 2020 | Assignment 3 | Carnegie Mellon University
        '''
                )

    # Select City
    cities = ["New York City"]
    city = st.sidebar.selectbox("City", cities)

    # Get unique neighbourhoods
    unique_neighbourhoods = city_neighbourhood_mapping[city]
    neighbourhood = st.sidebar.selectbox("Borough", unique_neighbourhoods)

    # Select room type
    type_room = st.sidebar.selectbox("Room Type", room_types)

    # Select rental size
    size_rental = st.sidebar.select_slider("Rental Size", rental_size)
    size_rental_internal = None
    if size_rental != 'All':
        size_rental_internal = 0 if size_rental == 'Studio' else int(size_rental.replace('+', ''))

    # Select price range
    min_price = st.sidebar.slider("Minimum Price", 0, 10000, 0, 500, format="$%d")
    max_price = st.sidebar.slider("Maximum Price", 0, 10000, 10000, 500, format="$%d")

    # Get the filtered dataframe based on the above criteria
    listings_dict = city_listings_mapping[city]

    filtered_listings = {}
    for month_no in listings_dict.keys():
        df = listings_dict[month_no]
        df_filter = df
        if neighbourhood != 'All':
            df_filter = df[(df["neighbourhood_group_cleansed"] == neighbourhood)]
        if type_room != 'All':
            df_filter = df_filter[(df_filter["room_type"] == type_room)]
        if size_rental_internal is not None:
            df_filter = df_filter[(df["bedrooms"] == size_rental_internal)]
        df_filter = df_filter[(df["price"] <= max_price) & (df["price"] >= min_price)]
        filtered_listings[month_no] = df_filter

    # Combine all filtered listings into one dataframe
    all_filtered_listings = pd.concat([filtered_listings['01'], filtered_listings['02'], filtered_listings['03'],
                                       filtered_listings['04'], filtered_listings['05'], filtered_listings['06'],
                                       filtered_listings['07'], filtered_listings['08'],
                                       filtered_listings['09']], ignore_index=True)
    all_filtered_listings.drop_duplicates(subset=['id'], inplace=True, keep='last')
    # Get total number of filtered listings
    total_filtered_listings = len(all_filtered_listings.axes[0])
    st.write("Number of listings: " + str(total_filtered_listings))

    filtered_covid = covid['09']
    if neighbourhood != 'All':
        filtered_covid = covid['09'][(covid['09']['BOROUGH_GROUP'] == neighbourhood)]

    # Showing map with listings by month
    # st.map(all_filtered_listings)
    # all_filtered_listings.dropna(subset=['latitude', 'longitude'])
    # all_filtered_listings['latitude'] = pd.to_numeric(all_filtered_listings['latitude'])
    # all_filtered_listings['longitude'] = pd.to_numeric(all_filtered_listings['longitude'])
    month = st.select_slider("Months in 2020", ['01', '02', '03', '04', '05', '06', '07', '08', '09'])
    dataset_map = filtered_listings[month]
    dataset_map.dropna(subset=['latitude', 'longitude'])
    # dataset_map['latitude'] = pd.to_numeric(dataset_map['latitude'])
    # dataset_map['longitude'] = pd.to_numeric(dataset_map['longitude'])
    if month == '09':
        left_column, right_column = st.beta_columns(2)
        left_column.write("Listings")
        left_column.map(dataset_map)
        right_column.write("Current Covid Stats")
        covid_map_data = filtered_covid
        right_column.map(covid_map_data)
    else:
        st.map(dataset_map)

    # st.pydeck_chart(pdk.Deck(
    #     map_style='mapbox://styles/mapbox/light-v9',
    #     layers=[
    #         pdk.Layer(
    #             'HexagonLayer',
    #             data=dataset_map,
    #             get_position='[longitude, latitude]',
    #             radius=200,
    #             elevation_scale=4,
    #             elevation_range=[0, 1000],
    #             pickable=True,
    #             extruded=True,
    #         ),
    #         pdk.Layer(
    #             'ScatterplotLayer',
    #             data=dataset_map,
    #             get_position='[longitude, latitude]',
    #             get_color='[200, 30, 0, 160]',
    #             get_radius=200,
    #         ),
    #     ],
    # ))

    column1, column2, column3 = st.beta_columns(3)

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

    graphing_dict = {"Month": month, "Median price": median_price, "Number of listings": number_of_listings}
    graphing_df = pd.DataFrame.from_dict(graphing_dict)

    # View 2
    view2 = alt.Chart(graphing_df).mark_line().encode(
            x='Month',
            y='Median price'
        ).properties(
            width=300, height=400
        ).interactive()

    # View 3
    # Get unique listing IDs from all_filtered_listings
    listing_id_list = all_filtered_listings['id'].tolist()
    reviews_city = reviews_dictionary['NYC']
    df_reviews_year = reviews_city[(reviews_city["year"] == '2020')]
    df_reviews_year = df_reviews_year[(df_reviews_year["listing_id"].isin(listing_id_list))]
    reviews_chart = pd.DataFrame(df_reviews_year.groupby(['Month'])['Month'].count())
    reviews_chart.columns = ['Number of Guests']
    reviews_chart.reset_index(inplace=True)
    view3 = alt.Chart(reviews_chart).mark_line().encode(
         x='Month',
         y='Number of Guests'
    ).properties(
         width=300, height=400
    ).interactive()

    # View 4
    view4 = alt.Chart(graphing_df).mark_line().encode(
        x='Month',
        y='Number of listings'
    ).properties(
        width=300, height=400
    ).interactive()

    if st.checkbox('See how the filtered listings have changed over the past year:'):
        column1.write(view2)
        column2.write(view3)
        column3.write(view4)

map_data = (
    # "https://raw.githubusercontent.com/uber-common/"
    # "deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"
    # "https://github.com/CMU-IDS-2020/a3-data-diggers/blob/master/data/2020/NYC/listings_09.csv"
    # 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv'
    "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/data/2020/NYC/listings_09.csv"
)


st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=40.7128,
        longitude=-74.0060,
        bearing = 0,
        zoom=11,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScreenGridLayer',
            data=map_data,
            pickable = False,
            opacity = 0.8,
            cell_size_pixels=50,
            color_range=[
                # [0, 25, 0, 25],
                # [0, 85, 0, 85],
                # [0, 127, 0, 127],
                # [0, 170, 0, 170],
                # [0, 190, 0, 190],
                # [0, 255, 0, 255],
                [252, 171, 143, 25],
                [252, 138, 107, 85],
                [249, 105, 76, 127],
                [239, 70, 52, 170],
                [217, 40, 36, 190],
                [187, 22, 26, 255],
            ],
            get_position='[longitude, latitude]',
            get_weight=2,
            # get_position='[lon, lat]',
            # radius=200,
            # elevation_scale=4,
            # elevation_range=[0, 1000],
            # pickable=True,
            # extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=map_data,
            pickable = True,
            opacity = 0.8,
            filled=True,
            radius_scale=0.8,
            # radius_min_pixels=1,
            # radius_max_pixels=100,
            # get_position="coordinates",
            get_position='[longitude, latitude]',
            get_radius=20,
            # get_fill_color=[200, 30, 0, 160],
            get_fill_color=[32, 111, 178, 160],
        ),
    ],
    tooltip={
        "html": "<b>name:</b> {name}"
        "<br/> <b>Neighbourhood:</b> {neighbourhood_cleansed}"
        " <br/> <b>Room Type:</b> {room_type} "
        "<br/> <b>Price:</b> {price}"
        "<br/> <b>Number of reviews last 3 months:</b> {number_of_reviews_ltm}"
        "<br/> <b>Number of reviews last month:</b> {number_of_reviews_l30d}",
        # "style": {"color": "white"},
    },
))