import streamlit as st

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
st.title("💡Documentation")

st.markdown("""
        ## Introduction
        
        This project is a continuation of the previous project, [Flood Risk Model 1](https://github.com/keanteng/flood_risk_model) that uses a univariate [logistic regression](https://en.wikipedia.org/wiki/Logistic_regression) approach
        to predict the flood risk of a location. In this project, we will be using a multivariate logistic regression approach to predict the flood risk of a location.
        The flood data is collected from the annual report published by the [Department of Irrigation and Drainage](https://www.water.gov.my/) from 2020-2021. The model is trained on 19,000 labelled random geo-coordinates in Malaysia.
        
        | Flood Annual Report | Link                                                                                         |
        | ------------------- | -------------------------------------------------------------------------------------------- |
        | 2015 Report         | [Link](https://info.water.gov.my/index.php/databank/view_attachment/5486)                    |
        | 2016 Report         | [Link](http://h2o.water.gov.my/man_hp1/Banjir_Tahun1617.pdf)                                 |
        | 2017 Report         | [link](http://h2o.water.gov.my/man_hp1/LBT2017-2018.pdf)                                     |
        | 2018 Report         | [Link](http://h2o.water.gov.my/man_hp1/LBT2018_2019.pdf)                                     |
        | 2019 Report         | [Link](http://h2o.water.gov.my/man_hp1/2019.pdf)                                             |
        | 2020 Report         | [Link](http://h2o.water.gov.my/man_hp1/LBT2020.pdf)                                          |
        | 2021 Report         | [Link](http://h2o.water.gov.my/man_hp1/LAPORAN%20BANJIR%20TAHUN%202021%20FINAL%20e-ISSN.pdf) |
        
        ## Methodology
        
        In this study, we include features such as elevation, slope, land cover, distance to the nearest town, distance to the nearest river and cluster, as follows:
        ```
        target = distance_to_hist_floodsite + 
         altitude + 
         slope + 
         land_cover + 
         town_distance + 
         river_distance + 
         cluster + 
         error_term
        ```
        
        Logistic regression shows great performance in the study with more than 98% accuracy and no sign of overfitting. State of the art-model like `XGBClassifier` is able to achieve a 
        remarkable 100% accuracy.
        
        ## Data Collection
        The labelled random coordinates were generated using `rancoord` a [Python package](https://github.com/hugodscarvalho/rancoord) that is capable of random sampling for geographic coordinates. To create labels for each coordinate, unique flood locations gathered from the 2020-2021 annual report published by the [Department of Irrigation and Drainage](https://www.water.gov.my/) were used to check whether the coordinate fall within 1.5 km radius of all the flood coordinates.

        Furthermore, the nearest distances between the random coordinates and the historical flood points were also computed using the `geopandas` module.

        Features such as altitude, slope and land cover were collected by using [Google Earth Engine](https://developers.google.com/earth-engine/) services. For the land cover or land type, the information is gathered by using the [Copernicus Global Land Cover Layers](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_Landcover_100m_Proba-V-C3_Global).

        For town distances, 62 largest towns from [Wikipedia](https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Malaysia_by_population) were geocoded using [Nominatim](https://nominatim.openstreetmap.org/ui/search.html) and [Opencage](https://opencagedata.com/demo) geocoding services. The minimum distance between these towns and the random locations were computed.

        Moreover, to calculate the nearest river distance from the random coordinates, the waterways shapefile was collected from [HOTOSM Malaysia Waterways](https://data.humdata.org/dataset/hotosm_mys_waterways?). The distance between points (coordinate) and the polygon (waterways shape file) ware computed.

        K-means clustering was used to create 15 clusters class based on the latitude and the longitude of each coordinate.

        As a bonus to this study, [SHAP](https://shap.readthedocs.io/en/latest/index.html) or `SHapley Additive exPlanations` was used to break down a prediction to show the impact of each feature. It was found that the distance to the nearest historical flood site is the most important feature in predicting the flood risk of a location.
            
        ## Limitations
        It was noticed that the logistic regression model prediction depend mainly on the distance to the historical flood point. 
        This caused other feature to have minimal impact on the model. This was due to the assumption that all the flood area of coverage was the same. 
        Further data collection was needed in this area.

        """)