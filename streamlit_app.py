import pandas as pd
import leafmap
import streamlit as st

st.set_page_config(layout="wide")

data = pd.read_csv('Cleaned/final.csv')
data = data.loc[data.year == 2020]

with st.expander("Source Code (Click to Expand)"):
    with st.echo():

        m = leafmap.Map(center=[4, 108], zoom=5)

        # m.add_geojson(regions, layer_name="Malaysia")
        m.add_points_from_xy(
            data,
            x="longitude",
            y="latitude",
            icon_names=['gear', 'map', 'leaf', 'globe'],
        )


m.to_streamlit(height=700)

