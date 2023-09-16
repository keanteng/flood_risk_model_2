import streamlit as st
import pandas as pd
import geopandas as gpd
from PIL import Image
from geopy.geocoders import Nominatim
import leafmap.foliumap as leafmap
import geemap
import math
import ee

st.set_page_config(layout="wide")

# customize the side bar
st.sidebar.title("Resources:")
st.sidebar.info(
    """
    - GitHub repository: [Flood Risk Model](https://github.com/keanteng/flood_risk_model_2)
    - Data sources: [Flood Data](https://www.water.gov.my/)
    """
)

st.sidebar.title("Created By:")
st.sidebar.info(
    """
  Khor Kean Teng | Intern, DGA, JPS, Bank Negara Malaysia | [GitHub](https://github.com/keanteng) | [LinkedIn](https://www.linkedin.com/in/khorkeanteng/)
    """
)

# Customize page title
st.title("🚀Flood Risk Prediction Engine")

st.markdown("""
            ### 🗣️ Chat With Me To Predict Your Flood Risk 
            This is a flood risk prediction service that predicts the flood risk of a location in Malaysia. The result is not 100% accurate and should not be used as a basis for any decision making. 
            The result is only for reference purposes.
            
            The application is designed to look like an interactive chatbot.
            
            **📌Location Cluster Code**
            """)

col1, col2, col3 = st.columns(3)

with col1: 
    st.markdown("""
            | Cluster | States |
            | --- | --- |
            | 8 | Perlis |
            | 0 | Kedah |
            | 0 | Pulau Pinang |
            | 9 | Perak |
            | 2 | Selangor |
            | 11 | Negeri Sembilan |
                """)
    
with col2:
    st.markdown("""
            | Cluster | States |
            | --- | --- |
            | 4 | Terengganu |
            | 12 | Kelantan |
            | 1 | Sabah (Tawau) |
            | 14 | Labuan | 
            | 6 | Sabah 
            | 3 | Sarwak (Kuching) |
                """)
    
with col3:
    st.markdown("""
            | Cluster | States |
            | --- | --- | 
            | 11 | Melaka |
            | 7 | Johor |
            | 5 | Pahang |
            | 10 | Sarawak (Other) |
            | 2 | Kuala Lumpur |
            | 2 | Putrajaya |    
                """)
    
st.markdown("""
            
            """)


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Enter your address of interest and cluster code here:")

if prompt:
    # assign variables
    your_cluster = prompt.split(",")[-1]
    your_address = prompt.split(",")[0]
    your_cluster = int(your_cluster)
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Hi there, your address of interest is: {your_address} and your cluster code is: {your_cluster}"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    
# submitted = st.button("Submit For Prediction")


# your_cluster = st.selectbox("Select your location cluster:", (1,2,3,4,5,6,7,8,9,10,11,12,13,14))


#####################################
# geocoding function
@st.cache_data
def my_geocoder(address):
            try:
                point = geolocator.geocode(address).point
                return pd.Series({'latitude': point.latitude, 'longitude': point.longitude})
            except:
                return pd.Series({'latitude': None, 'longitude': None})

# distance function to historical flood points
def distance_to_nearest_flood_point(data):
    flood_points = pd.read_csv('cleaned/final.csv')
    data = gpd.GeoDataFrame(data, geometry = gpd.points_from_xy(data.longitude, data.latitude), crs = "EPSG:4326").to_crs('EPSG:3857')
    flood_points_data = gpd.GeoDataFrame(flood_points, geometry = gpd.points_from_xy(flood_points.longitude, flood_points.latitude), crs = "EPSG:4326").to_crs('EPSG:3857')
    
    # write a function to compute for the minimum distances from any flood point
    for i in range(0, len(data)):
        distances = flood_points_data.geometry.distance(data.iloc[i].geometry)
        data.loc[i, 'distance'] = distances.min()
        data.loc[i, 'kawasan_banjir'] = flood_points_data.iloc[distances.idxmin()]["kawasan_banjir"]
        data.loc[i, 'latitude_kb'] = flood_points_data.iloc[distances.idxmin()]["latitude"]
        data.loc[i, 'longitude_kb'] = flood_points_data.iloc[distances.idxmin()]["longitude"]
        data.loc[i, 'kedalaman_banjir'] = flood_points_data.iloc[distances.idxmin()]["kedalaman_banjir_max"]

    return data

# distance to the nearest river
def distance_to_river(data):
    rivers = gpd.read_file("data/river_polygon.geojson")
    data = gpd.GeoDataFrame(data, geometry = gpd.points_from_xy(data.longitude, data.latitude), crs = "EPSG:4326").to_crs('EPSG:3857')
    rivers_data = gpd.GeoDataFrame(rivers, geometry = 'geometry', crs = "EPSG:4326").to_crs('EPSG:3857')
    
    # write a function to compute for the minimum distances from any flood point
    for i in range(0, len(data)):
        distances = rivers_data.geometry.distance(data.iloc[i].geometry)
        data.loc[i, 'distance'] = distances.min()

    return data

# distance to the nearest town
def distance_to_town(data):
    towns = pd.read_excel('data/malaysia_towns.xlsx')
    data = gpd.GeoDataFrame(data, geometry = gpd.points_from_xy(data.longitude, data.latitude), crs = "EPSG:4326").to_crs('EPSG:3857')
    towns_data = gpd.GeoDataFrame(towns, geometry = gpd.points_from_xy(towns.longitude, towns.latitude), crs = "EPSG:4326").to_crs('EPSG:3857')
    
    # write a function to compute for the minimum distances from any flood point
    for i in range(0, len(data)):
        distances = towns_data.geometry.distance(data.iloc[i].geometry)
        data.loc[i, 'distance'] = distances.min()
        data.loc[i, 'town'] = towns_data.iloc[distances.idxmin()]["town"]
        data.loc[i, 'latitude_tw'] = towns.iloc[distances.idxmin()]["latitude"]
        data.loc[i, 'longitude_tw'] = towns.iloc[distances.idxmin()]["longitude"]

    return data

# earth engine funtionality
@st.cache_data
def ee_authenticate(token_name = 'EARTHENGINE_TOKEN'):
    geemap.ee_initialize(token_name = token_name)
    
# computing elevation
def get_elevation(data):
    DEM = ee.Image("USGS/SRTMGL1_003")
    
    nodes = [data['longitude'][0], data['latitude'][0]]
    points = [ee.Geometry.Point(nodes)]
    feats = [ee.Feature(p, {'name': 'node{}'.format(i)}) for i, p in enumerate(points)]
    fc = ee.FeatureCollection(feats)
    reducer = ee.Reducer.first()
    data = DEM.reduceRegions(fc, reducer.setOutputs(['elevation']), 30)
    elevation = data.getInfo()['features'][0]['properties']['elevation']
    
    return elevation

# computing slope
def get_slope(data):
    DEM = ee.Image("USGS/SRTMGL1_003")
    
    nodes = [data['longitude'][0], data['latitude'][0]]
    points = [ee.Geometry.Point(nodes)]
    feats = [ee.Feature(p, {'name': 'node{}'.format(i)}) for i, p in enumerate(points)]
    fc = ee.FeatureCollection(feats)
    slope = ee.Terrain.slope(DEM)
    reducer = ee.Reducer.first()
    data = slope.reduceRegions(fc, reducer.setOutputs(['slope']), 30)
    slope = data.getInfo()['features'][0]['properties']['slope']
    
    return slope

# computing landcover
def get_landcover(data):
    nodes = [data['longitude'][0], data['latitude'][0]]
    points = [ee.Geometry.Point(nodes)]
    
    landcover = ee.ImageCollection('COPERNICUS/Landcover/100m/Proba-V-C3/Global')
    
    feats = [ee.Feature(p, {'name': 'node{}'.format(i)}) for i, p in enumerate(points)]
    fc = ee.FeatureCollection(feats)
    landcover_at_point = landcover.filterBounds(fc).first()
    reducer = ee.Reducer.first()
    
    data = landcover_at_point.reduceRegions(fc, reducer.setOutputs(['discrete_classification']), 30)
    landcover = data.getInfo()['features'][0]['properties']['discrete_classification']
    
    return landcover

# get landcover description
def get_landcover_description(landcover):
    if landcover == 0:
        return "Unknown"
    elif landcover == 20:
        return "Shurbs"
    elif landcover == 30:
        return "Herbaceous vegetation"
    elif landcover == 40:
        return "Cultivated and managed vegetation/agriculture"
    elif landcover == 50:
        return "Urban / built up"
    elif landcover == 60:
        return "Bare / sparse vegetation"
    elif landcover == 70:
        return "Snow and ice"
    elif landcover == 80:
        return "Permanent Water bodies"
    elif landcover == 90:
        return "Herbaceous wetland"
    elif landcover == 100:
        return "Moss and lichen"
    elif landcover == 111:
        return "Closed forest, evergreen, needle leaf"
    elif landcover == 112:
        return "Closed forest, evergreen, broad leaf"
    elif landcover == 113:
        return "Closed forest, deciduous needle leaf"
    elif landcover == 114:
        return "Closed forest, deciduous broad leaf"
    elif landcover == 115:
        return "Closed forest, mixed"
    elif landcover == 116:
        return "Closed forest, unknown"
    elif landcover == 121:
        return "Open forest, evergreen, needle leaf"
    elif landcover == 122:
        return "Open forest, evergreen, broad leaf"
    elif landcover == 123:
        return "Open forest, deciduous needle leaf"
    elif landcover == 124:
        return "Open forest, deciduous broad leaf"
    elif landcover == 125:
        return "Open forest, mixed"
    elif landcover == 126:
        return "Open forest, unknown"
    elif landcover == 200:
        return "Open sea"
    else:
        return "Nodata"

# get landcover label
def get_landcover_label(landcover):
    if landcover == 50:
        return 1
    elif landcover == 112:
        return 2
    elif landcover == 200:
        return 3
    elif landcover == 40:
        return 4
    elif landcover == 126:
        return 5
    elif landcover == 122:
        return 6
    elif landcover == 116:
        return 7
    elif landcover == 80:
        return 8
    elif landcover == 30:
        return 9
    elif landcover == 90:
        return 10
    elif landcover == 20:
        return 11
    elif landcover == 60:
        return 12
    elif landcover == 111:
        return 13
    else:
        return 1 # for no matching all assume as built up

#####################################
# computation output

if prompt:
    your_cluster = prompt.split(",")[-1]
    your_address = prompt.split(",")[0]
    your_cluster = int(your_cluster)
    
    with st.spinner("Computing ... Please Wait ..."):
        ee_authenticate(token_name="EARTHENGINE_TOKEN")
        
        data = pd.DataFrame({'Location': [your_address],})
        geolocator = Nominatim(user_agent="u2004763@siswa.um.edu.my")
        data[['latitude', 'longitude']] = data.apply(lambda x: my_geocoder(x['Location']), axis=1)
        
        if data['latitude'][0] == None:
            with st.chat_message("assistant"):
                st.error("Please enter a new address. The address you entered is not valid.")
        else:
            data = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))
            data.crs = {'init': 'epsg:4326'}
            
            # getting the variables
            dist_to_hist = distance_to_nearest_flood_point(data)
            dist_to_river = distance_to_river(data) 
            dist_to_town = distance_to_town(data)
            location_elevation = get_elevation(data) 
            location_slope = get_slope(data)
            location_landcover = get_landcover(data)
            
            scale_dist_to_hist = (dist_to_hist['distance'][0]- 2683.402344024774)/3513.597864
            scale_dist_to_river = (dist_to_river['distance'][0] - 2022.250156510475)/2076.7445583475537
            scale_dist_to_town = (dist_to_town['distance'][0] - 16447.459432970976)/12995.05773734854
            scale_location_elevation = (location_elevation - 56.8942191283293)/ 38.0
            scale_location_slope = (location_slope - 5.435003841785432)/5.896303206682205
            
            landcover_label = get_landcover_label(location_landcover)
            landcover_description = get_landcover_description(location_landcover)
            
            # computing the flood risk
            flood_risk_x = -3.04993633e+01 * scale_dist_to_hist + -8.08219098e-02 * scale_location_elevation + -4.23774005e-02 * scale_location_slope + -1.96876083e-01 * scale_dist_to_river + -2.85777681e-02 * landcover_label + -3.96249614e-02 * scale_dist_to_town + -2.54932137e-02 * your_cluster + -13.29790589
            flood_risk = 1/(1 + math.exp(flood_risk_x))
            
            with st.chat_message("assistant"):
                st.write("Hi there, the flood risk for your location is: ", flood_risk)
                st.write("According to Earth Engine, you location elevation is ", location_elevation, "meters. The slope is ", location_slope, "degrees. I notice that your location is ", landcover_description, "area.")
                st.write("From you location, the distance to the nearest flood point is ", dist_to_hist['distance'][0], "meters. The distance to the nearest river is ", dist_to_river['distance'][0], "meters. The distance to the nearest town is ", dist_to_town['distance'][0], "meters.")
            
                if flood_risk < 0.5:
                    st.markdown("Your location is at a low risk of flooding.")
                else:
                    st.markdown("Your location is at a high risk of flooding. Please be careful and take precautions.")
            
                # tranforming data
                df1 = dist_to_hist[['kawasan_banjir', 'latitude_kb', 'longitude_kb']]
                df2 = dist_to_town[['town', 'latitude_tw', 'longitude_tw']]
                df1.columns = ['Location', 'latitude', 'longitude']
                df2.columns = ['Location', 'latitude', 'longitude']
                data = pd.concat([data, df1])
                data = pd.concat([data, df2])
                data['Remarks'] = ['Your Location', 'Nearest Flood Point', 'Nearest Town']
                
                # plot the map
                with st.expander("Further Analysis", expanded=True):
                    m = leafmap.Map(center=[3, 101], zoom=6, google_map="HYBRID")
                    regions = 'data/river_polygon.geojson'
                    m.add_geojson(regions, layer_name="Waterways")
                    m.add_points_from_xy(
                        data, 
                        x="longitude", 
                        y="latitude",
                        icon_names=['gear', 'map', 'leaf', 'globe'],
                    )
                    m.to_streamlit(height = 700)