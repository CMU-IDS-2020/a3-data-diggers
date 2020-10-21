import streamlit as st
import pandas as pd
import math
import altair as alt
import numpy as np
import pydeck as pdk

SCATTERPLOT_LAYER_DATA = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart-stations.json"
df = pd.read_json(SCATTERPLOT_LAYER_DATA)

# SCATTERPLOT_LAYER_DATA = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-data-diggers/master/data/2020/NYC/listings_01.csv"
# df = pd.read_csv(SCATTERPLOT_LAYER_DATA)

# Use pandas to calculate additional data
df["exits_radius"] = df["exits"].apply(lambda exits_count: math.sqrt(exits_count))

SCREEN_GRID_LAYER_DATA = (
    "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf-bike-parking.json"  # noqa
)
df_grid = pd.read_json(SCREEN_GRID_LAYER_DATA)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=37.7749295,
        longitude=-122.4,
        bearing = 0,
        zoom=11,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScreenGridLayer',
            data=df_grid,
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
            get_position='COORDINATES',
            get_weight="SPACES",
            # get_position='[lon, lat]',
            # radius=200,
            # elevation_scale=4,
            # elevation_range=[0, 1000],
            # pickable=True,
            # extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            pickable = True,
            opacity = 0.8,
            filled=True,
            radius_scale=1,
            radius_min_pixels=1,
            radius_max_pixels=100,
            get_position="coordinates",
            get_radius="exits_radius",
            # get_fill_color=[200, 30, 0, 160],
            get_fill_color=[32, 111, 178, 160],
        ),
    ],
))

# Define a layer to display on a map
layer = pdk.Layer(
    "ScreenGridLayer",
    df,
    pickable=False,
    opacity=0.8,
    cell_size_pixels=50,
    color_range=[
        [0, 25, 0, 25],
        [0, 85, 0, 85],
        [0, 127, 0, 127],
        [0, 170, 0, 170],
        [0, 190, 0, 190],
        [0, 255, 0, 255],
    ],
    get_position="COORDINATES",
    get_weight="SPACES",
)

