import streamlit as st
import pandas as pd
import math
import altair as alt
import numpy as np
import pydeck as pdk

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=37.76,
        longitude=-122.4,
        bearing = 0,
        zoom=11,
        pitch=0,
    ),
    layers=[
        # pdk.Layer(
        #     'HexagonLayer',
        #     data=df,
        #     get_position='[lon, lat]',
        #     radius=200,
        #     elevation_scale=4,
        #     elevation_range=[0, 1000],
        #     pickable=True,
        #     extruded=True,
        # ),
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            pickable = True,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))