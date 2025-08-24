import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from PIL import Image
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import base64
from io import BytesIO
#from zipfile import ZipFile
from datetime import datetime
import io
import json
#import sys

#version = sys.version
#version_info = "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

#st.write(version)
#st.write("version info is",version_info)

# === Page Configuration ===
bp_refresh_date = "12-Jun-25"
st.set_page_config(page_title="Website Interactions", page_icon = Image.open("Titan Logo.png"), layout='wide', initial_sidebar_state = 'expanded', menu_items={'About': f"Website Interactions. \n\nThis platform displays Business Profile metrics of GMB (Consumer Interaction with our stores listed in Google Maps). This platform is refreshed in the backend every month. \n\nLast refreshed on {bp_refresh_date}."})


#--- {version} & {version_info}

# === Text Formatting ===
css = """
<style>
@keyframes shine {
  0% { background-position: -500%; }
  100% { background-position: 500%; }
}

.center-title {
    text-align: center;
    font-size: 50px;
    margin-top: 0px;
}

.center-header {
    text-align: center;
    font-size: 24px;
    margin-top: 0px;
}

.left-header {
    text-align: left;
    font-size: 24px;
    margin-top: 0px;
    font-style: italic; /* This will italicize the text */
    text-decoration: underline; /* This will underline the text */
}

.left-header-2 {
    text-align: left;
    font-size: 20px;
    margin-top: 0px;
    font-style: italic; /* This will italicize the text */
    text-decoration: underline; /* This will underline the text */
}

.left-content {
    text-align: left;
    font-size: 18px;
    margin-top: 0px;
    font-weight: normal;
   /*color: #FF3E05;*/
    text-decoration: underline;
    font-style: italic;
}

.left-content-2 {
    text-align: left;
    font-size: 15px;
    margin-top: 0px;
    font-weight: normal;
    font-style: italic;
}

.center-content {
    text-align: center;
    font-size: 18px;
    margin-top: 0px;
    font-weight: normal;
}

.rainbow-text {
    background: linear-gradient(90deg,violet,indigo,blue,green, yellow, orange, red);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    color: transparent;
    animation: shine 15s linear infinite;
    /*text-shadow: 0 0 10px rgba(255, 255, 255, 0.6);*/
}

.container {
    display: flex;
}
   
.logo-text {
    font-size:50px !important;
    font-weight:700 !important;
    padding-top: 75px !important;
}

.logo-img {
    float:left;
    width:63px;
    height:63px;
    margin-right:10px;
}

.sticky-left-header {
    position: fixed; /* Fixed position */
    top: 20px; /* Align to the top */
    width: 100%; /* Header width is full container width */
    background-color: #0E1117; /* Background color */
    z-index: 1000; /* Ensures the header is always on top */
    text-align: left;
    font-size: 24px;
    font-style: italic;
    color: white;
    /*text-decoration: underline;*/
    padding: 75px 0; /* Add some padding */
}

.sticky-left-subheader {
    position: fixed; /* Fixed position */
    top: 150px; /* Align to the top */
    width: 100%; /* Header width is full container width */
    background-color: #0E1117; /* Background color */
    z-index: 1000; /* Ensures the header is always on top */
    text-align: left;
    font-size: 24px;
    font-style: italic;
    color: #FFBD36; /* #477DEA(blue)*/
    /*text-decoration: underline;*/
    padding: 0px 0; /* Add some padding */
}


.content {
    margin-top: 0px; /* Add top margin to content equal to header height */
}

.keyword-box-green {
    display: inline-block;
    background-color: #81c784;
    border-radius: 20px;
    padding: 5px 10px;
    margin: 2px;
    font-size: 16px;
    color: white;
}

.keyword-box-red {
    display: inline-block;
    background-color: #FF735D;
    border-radius: 20px;
    padding: 5px 10px;
    margin: 2px;
    font-size: 16px;
    color: white;
}

</style>
"""
#Display the custom CSS
st.markdown(css, unsafe_allow_html=True)

# === User Defined Functions ===

# Function to convert dataframe to Excel and return a download link
def get_table_download_link(df):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"GMB_Metrics_{current_time}.xlsx"
    
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}">⬇️Download GMB Metrics</a>'
    return href

#Function to convert img to base64
def img_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

#Custom mapping for quarters
def get_custom_quarter(month):
    if month in [4, 5, 6]:
        return 'Q1'
    elif month in [7, 8, 9]:
        return 'Q2'
    elif month in [10, 11, 12]:
        return 'Q3'
    elif month in [1, 2, 3]:
        return 'Q4'

#Function to determine the financial year
def get_financial_year(date):
    year = date.year
    month = date.month
    if month in [1, 2, 3]:  # Jan, Feb, Mar
        return f"{str(year-1)[-2:]}-{str(year)[-2:]}"
    else:  # Apr to Dec
        return f"{str(year)[-2:]}-{str(year+1)[-2:]}"
    
# === Mapping of stores & competitors ===
store_list = ["Mia-Dubai BurJuman (XDJ)",
              "Mia-Al Wahda Mall (XAW)",
              "Tanishq Jewellers-Gold Souk (XDG)",
              "Tanishq-Abu Dhabi (XAH)",
              "Tanishq-Al Barsha (XDB)",
              "Tanishq-Al Fahidi (XDF)",
              "Tanishq-Karama Centre (XDK)",
              "Tanishq-Meena Bazar (XDM)",
              "Tanishq-Silicon Central (XDS)",
              "Tanishq-Sharjah Central (XSL)",
              "Tanishq-Doha Lulu (XQD)",
              "Tanishq-Doha Festival City (XQF)",
              "Tanishq-Oman Avenue Mall (XOM)",
              "Tanishq-Taj Dubai (XDT)",
              "Tanishq-Rolla Sharjah (XSR)",
              "Tanishq Jewellers-UW Mall Al Mankhool (XDX)",
              "Tanishq Chicago-Illinois (XCG)",
              "Tanishq Frisco-Texas (XTD)",
              "Tanishq Houston-Texas (XTH)",
              "Tanishq New Jersey-New Jersey (XNJ)",
              "Tanishq Redmond-Seattle (XWS)",
              "Tanishq Atlanta-Georgia (XAC)",
             "Tanishq Santa Clara-California (XBA)"] 

country_to_catchment = {"Select a Country":[],
                        "GCC":["Mia-Dubai BurJuman (XDJ)",
                              "Mia-Al Wahda Mall (XAW)",
                              "Tanishq Jewellers-Gold Souk (XDG)",
                              "Tanishq-Abu Dhabi (XAH)",
                              "Tanishq-Al Barsha (XDB)",
                              "Tanishq-Al Fahidi (XDF)",
                              "Tanishq-Karama Centre (XDK)",
                              "Tanishq-Meena Bazar (XDM)",
                              "Tanishq-Silicon Central (XDS)",
                              "Tanishq-Sharjah Central (XSL)",
                              "Tanishq-Doha Lulu (XQD)",
                              "Tanishq-Doha Festival City (XQF)",
                              "Tanishq-Oman Avenue Mall (XOM)",
                              "Tanishq-Taj Dubai (XDT)",
                              "Tanishq-Rolla Sharjah (XSR)",
                              "Tanishq Jewellers-UW Mall Al Mankhool (XDX)"],
                        "USA":["Tanishq Chicago-Illinois (XCG)",
                              "Tanishq Frisco-Texas (XTD)",
                              "Tanishq Houston-Texas (XTH)",
                              "Tanishq New Jersey-New Jersey (XNJ)",
                              "Tanishq Redmond-Seattle (XWS)",
                              "Tanishq Atlanta-Georgia (XAC)",
                             "Tanishq Santa Clara-California (XBA)"]}

#List of countries
countries = list(country_to_catchment.keys())


mapping_dict = {
                "Mia-Al Wahda Mall (XAW)" :  'Mia by Tanishq - Al Wahda Mall',
                "Mia-Dubai BurJuman (XDJ) " :  'Mia by Tanishq - BurJuman, Dubai',
                "Tanishq Atlanta-Georgia (XAC)" :  "Tanishq Jewellers - Atlanta",
                "Tanishq Chicago-Illinois (XCG) " :  "Tanishq Jewellers - Chicago",
                "Tanishq Frisco-Texas (XTD) " :  "Tanishq Jewelers - Dallas",
                "Tanishq Houston-Texas (XTH) " :  "Tanishq Jewelers - Houston",
                "Tanishq Jewellers-Gold Souk (XDG)" :  "Tanishq Jewelers - Gold Souk",
                "Tanishq New Jersey-New Jersey (XNJ) " :  "Tanishq Jewelers - New Jersey",
                "Tanishq Redmond-Seattle (XWS)" :  "Tanishq Jewelers - Redmond Seattle",
                "Tanishq-Abu Dhabi (XAH) " :  'Tanishq Jewellers - Hamdan Bin Mohammed Street',
                "Tanishq-Al Barsha (XDB) " :  'Tanishq Jewellers - Al Barsha',
                "Tanishq-Al Fahidi (XDF) " :  'Tanishq Jewellers - Al Fahidi , Bur Dubai',
                "Tanishq-Doha Festival City (XQF) " :  'Tanishq Jewellery - Doha Festival City',
                "Tanishq-Doha Lulu (XQD) " :  'Tanishq Jewellery - Doha Lulu, D Ring Rd',
                "Tanishq-Karama Centre (XDK) " :  'Tanishq Jewellers - Al Karama',
                "Tanishq-Meena Bazar (XDM) " :  'Tanishq Jewellers - Meena Bazar',
                "Tanishq-Oman Avenue Mall (XOM) " :  'Tanishq - Oman Avenue Mall',
                "Tanishq-Sharjah Central (XSL) " :  'Tanishq Jewellery - Sharjah Central',
                "Tanishq-Silicon Central (XDS) " :  'Tanishq Jewellers - Silicon Central',
                "Tanishq-Taj Dubai (XDT) " :  "Tanishq Jewellers - Taj Dubai",
                "Tanishq-Rolla Sharjah (XSR)" : "Tanishq Jewellery- Rolla, Sharjah",
                "Tanishq Santa Clara-California (XBA)" : "Tanishq Jewellers - Santa Clara",
                "Tanishq Jewellers-UW Mall Al Mankhool (XDX)" : "Tanishq Jewellers-Al Mankhool UW Mall"
                }

# === Front End UI coding ===
# Title - Display image and text
st.markdown(f"""
            <div class="container">
            <img class="logo-img" src="data:image/png;base64,{img_to_base64(Image.open("GMB.png"))}">
            <h1 style="color: #4AB4FF;">Customer Web Interaction Metrics </h1>
            </div>""", unsafe_allow_html=True)


#Create radio buttons in the sidebar
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        #Create a dropdown to select a country
        selected_country = st.selectbox(":blue[Select a country]", countries, index=0)
    with col2:
        #Check if a country has been selected
        if selected_country != "Select a country":
            catchment_areas = country_to_catchment[selected_country]
            #Create a second drop-down select box for the user to choose a catchment area
            selected_catchment = st.selectbox(":blue[Select a Store]", catchment_areas, index=0)
    with col1:
        #define types
        type_dis = ['Q on Q','M on M']
        #create a drop down to select type
        #selected_type = st.select_slider(':blue[Select type]', options = type_dis)
        selected_type = st.radio(':blue[Select type]', options = type_dis)

    with col2:
        #define years
        financial_years = ["22-23","23-24","24-25", "25-26"]        
        #create a drop down to select type
        selected_year = st.selectbox(':blue[Select financial year]',financial_years, index=0)
        
        # if selected_type == 'Q on Q':
        #     #define years
        #     financial_years = ["22-23","23-24","24-25"]        
        #     #create a drop down to select type
        #     selected_year = st.selectbox(':blue[Select financial year]',financial_years, index=0)
        # elif selected_type == 'M on M':
        #     #define years
        #     regular_years = ["2022","2023","2024"]        
        #     #create a drop down to select type
        #     selected_year = st.selectbox(':blue[Select year]',regular_years, index=0)
            
    submit_button = st.button("Display",key="submit_button",help="Click to Display")

# === Back end working code ===

#Reading data
gpmetric_df = pd.read_excel('gmb_web_interactions/output/output_usa_uae.xlsx')

gpmetric_df['date'] = pd.to_datetime(gpmetric_df['date'], errors='coerce')

#Further data preparation to get year, month, quarter & financial year 
gpmetric_df['year'] = gpmetric_df['date'].dt.year
gpmetric_df['month'] = gpmetric_df['date'].dt.strftime('%b')
gpmetric_df['quarter'] = gpmetric_df['date'].dt.month.apply(get_custom_quarter)

#Apply the function to create the financial year column
gpmetric_df['fy'] = gpmetric_df['date'].apply(get_financial_year)
#combine quarter & fy
gpmetric_df['quarter_fy'] = gpmetric_df['quarter'].astype(str) + ' (' + gpmetric_df['fy'] + ')'
#combine month & year
gpmetric_df['month_year'] = gpmetric_df['month'].astype(str) + ' (' + gpmetric_df['year'].astype(str) + ')'
#check
#st.dataframe(catchment_filtered_df)

if selected_country == "GCC":
    #Filter out the country
    country_filtered_df = gpmetric_df[gpmetric_df['country'] == "GCC"]
    #check
    #st.dataframe(country_filtered_df)

    #Filter out the store    
    if selected_catchment == "Tanishq-Abu Dhabi (XAH)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq Jewellers-Gold Souk (XDG)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Gold Souk"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Mia-Al Wahda Mall (XAW)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Mia by Tanishq - Al Wahda Mall"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Silicon Central (XDS)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Silicon Central"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Al Barsha (XDB)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Al Barsha"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Al Fahidi (XDF)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Karama Centre (XDK)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Al Karama"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Meena Bazar (XDM)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Meena Bazar"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Sharjah Central (XSL)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellery - Sharjah Central"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Doha Lulu (XQD)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellery - Doha Lulu, D Ring Rd"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Mia-Dubai BurJuman (XDJ)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Mia by Tanishq - BurJuman, Dubai"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Doha Festival City (XQF)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellery - Doha Festival City"]
        #check
        #st.dataframe(catchment_filtered_df)
        
    elif selected_catchment == "Tanishq-Oman Avenue Mall (XOM)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq - Oman Avenue Mall"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Taj Dubai (XDT)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Taj Dubai"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq-Rolla Sharjah (XSR)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellery- Rolla, Sharjah"]
        #check
        #st.dataframe(catchment_filtered_df)        
        
    elif selected_catchment == "Tanishq Jewellers-UW Mall Al Mankhool (XDX)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] ==  "Tanishq Jewellers-Al Mankhool UW Mall"]
        #check
        #st.dataframe(catchment_filtered_df)        
    else:
        pass
    
    #Filter for year/ fy based on selected_type
    if selected_year == "22-23":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "22-23"]
        #check
        #st.dataframe(year_filtered_df)
    elif selected_year == "23-24":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "23-24"]
        #check
        #st.dataframe(year_filtered_df)
        #st.write(year_filtered_df.columns)
    elif selected_year == "24-25":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "24-25"]
        #check
        #st.dataframe(year_filtered_df)
    elif selected_year == "25-26":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "25-26"]
        #check
        #st.dataframe(year_filtered_df)

    # if selected_type == 'Q on Q':
    #     if selected_year == "22-23":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "22-23"]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "23-24":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "23-24"]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "24-25":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "24-25"]
    #         #check
    #         #st.dataframe(year_filtered_df)
    # elif selected_type == 'M on M':
    #     if selected_year == "2022":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['year'] == 2022]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "2023":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['year'] == 2023]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "2024":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['year'] == 2024]
    #         #check
    #         #st.dataframe(year_filtered_df)

        
        
    #Filter data based on metrics
    #Filter the DataFrame for bpi parameter tags & types
    filtered_df_bpi = year_filtered_df[year_filtered_df['parameter_tag'].isin(['bpi-call_button', 'bpi-directions_button', 'bpi-website_button'])]
    #Filter the DataFrame for gm parameter tags & types
    filtered_df_gm = year_filtered_df[year_filtered_df['parameter_tag'].isin(['gm-mobile_views', 'gm-desktop_views'])]        
    #Filter the DataFrame for gs parameter tags & types        
    filtered_df_gs = year_filtered_df[year_filtered_df['parameter_tag'].isin(['gs-mobile_views', 'gs-desktop_views'])]
    #check
    #st.dataframe(filtered_df_gs)

    #Data Preparation for chart creation based on selected type
    if selected_type == "Q on Q":

        #Group by quarter and bpi_parameter_tag and sum the count for datafrmae 
        grouped_df_bpi_a = filtered_df_bpi.groupby(['quarter','quarter_fy', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for chart
        grouped_df_bpi = filtered_df_bpi.groupby(['quarter', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_bpi = [col for col in grouped_df_bpi_a.columns if col != 'quarter']
        #Display the dataframe without the 'quarter' column
        #check
        #st.dataframe(grouped_df_bpi_a[columns_to_display_bpi])
        #st.dataframe(grouped_df_bpi_a)

        #Group by quarter and bpi_parameter_tag and sum the count for datafrmae 
        grouped_df_gm_a = filtered_df_gm.groupby(['quarter','quarter_fy', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count
        grouped_df_gm = filtered_df_gm.groupby(['quarter', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gm = [col for col in grouped_df_gm_a.columns if col != 'quarter']
        #Display the dataframe without the 'quarter' column
        #check
        #st.dataframe(grouped_df_gm_a[columns_to_display_gm])
        #st.dataframe(grouped_df_gm_a)

        #Group by quarter and bpi_parameter_tag and sum the count for datafrmae 
        grouped_df_gs_a = filtered_df_gs.groupby(['quarter','quarter_fy', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count
        grouped_df_gs = filtered_df_gs.groupby(['quarter', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gs = [col for col in grouped_df_gs_a.columns if col != 'quarter']
        #Display the dataframe without the 'quarter' column
        #check
        #st.dataframe(grouped_df_gs_a[columns_to_display_gs])
        #st.dataframe(grouped_df_gs_a)
        
    elif selected_type ==  "M on M":
        #Group by quarter and bpi_parameter_tag and sum the count for dataframe
        grouped_df_bpi_a = filtered_df_bpi.groupby(['month','month_year', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for graph
        grouped_df_bpi = filtered_df_bpi.groupby(['month', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_bpi = [col for col in grouped_df_bpi_a.columns if col != 'month']
        #Display the dataframe without the 'month' column
        #check
        #st.dataframe(grouped_df_bpi_a[columns_to_display_bpi])
        #st.dataframe(grouped_df_bpi_a)

        #Group by quarter and bpi_parameter_tag and sum the count for dataframe
        grouped_df_gm_a = filtered_df_gm.groupby(['month','month_year', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for graph
        grouped_df_gm = filtered_df_gm.groupby(['month', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gm = [col for col in grouped_df_gm_a.columns if col != 'month']
        #Display the dataframe without the 'month' column
        #check
        #st.dataframe(grouped_df_gm_a[columns_to_display_gm])
        #st.dataframe(grouped_df_gm_a)

        #Group by quarter and bpi_parameter_tag and sum the count for dataframe
        grouped_df_gs_a = filtered_df_gs.groupby(['month','month_year', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for graph
        grouped_df_gs = filtered_df_gs.groupby(['month', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gs = [col for col in grouped_df_gs_a.columns if col != 'month']
        #Display the dataframe without the 'month' column
        #check
        #st.dataframe(grouped_df_gs_a[columns_to_display_gs])
        #st.dataframe(grouped_df_gs_a)
        
        # Define the order of months
        month_order = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec','Jan', 'Feb', 'Mar']

        #Convert the month column to a categorical type with the specified order
        grouped_df_gm['month'] = pd.Categorical(grouped_df_gm['month'], categories=month_order, ordered=True)
        grouped_df_gs['month'] = pd.Categorical(grouped_df_gs['month'], categories=month_order, ordered=True)
        grouped_df_bpi['month'] = pd.Categorical(grouped_df_bpi['month'], categories=month_order, ordered=True)
        grouped_df_gm_a['month'] = pd.Categorical(grouped_df_gm_a['month'], categories=month_order, ordered=True)
        grouped_df_gs_a['month'] = pd.Categorical(grouped_df_gs_a['month'], categories=month_order, ordered=True)
        grouped_df_bpi_a['month'] = pd.Categorical(grouped_df_bpi_a['month'], categories=month_order, ordered=True)

        #Sort the dataframe by the month column
        grouped_df_gm = grouped_df_gm.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gm[columns_to_display_gm])
        grouped_df_gs = grouped_df_gs.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gs[columns_to_display_gs])
        grouped_df_bpi = grouped_df_bpi.sort_values('month').reset_index(drop=True)    
        #check
        #st.dataframe(grouped_df_bpi[columns_to_display_bpi])

        #Sort the dataframe by the month column
        grouped_df_gm_a = grouped_df_gm_a.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gm[columns_to_display_gm])
        grouped_df_gs_a = grouped_df_gs_a.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gs[columns_to_display_gs])
        grouped_df_bpi_a = grouped_df_bpi_a.sort_values('month').reset_index(drop=True)    
        #check
        #st.dataframe(grouped_df_bpi[columns_to_display_bpi])


elif selected_country == "USA":
    #Filter out the country
    country_filtered_df = gpmetric_df[gpmetric_df['country'] == "USA"]
    #check
    #st.dataframe(country_filtered_df)

    #Filter out the store    
    if selected_catchment == "Tanishq Chicago-Illinois (XCG)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Chicago"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq Frisco-Texas (XTD)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Dallas"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq Houston-Texas (XTH)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Houston"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq New Jersey-New Jersey (XNJ)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - New Jersey"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq Redmond-Seattle (XWS)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Redmond Seattle"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq Atlanta-Georgia (XAC)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Atlanta"]
        #check
        #st.dataframe(catchment_filtered_df)
    elif selected_catchment == "Tanishq Santa Clara-California (XBA)":
        catchment_filtered_df = country_filtered_df[country_filtered_df['store'] == "Tanishq Jewellers - Santa Clara"]
        #check
        #st.dataframe(catchment_filtered_df)
    else:
        pass
    
    #Filter for year/ fy based on selected_type
    if selected_year == "22-23":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "22-23"]
        #check
        #st.dataframe(year_filtered_df)
    elif selected_year == "23-24":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "23-24"]
        #check
        #st.dataframe(year_filtered_df)
    elif selected_year == "24-25":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "24-25"]
        #check
        #st.dataframe(year_filtered_df)
    elif selected_year == "25-26":
        year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "25-26"]
        #check
        #st.dataframe(year_filtered_df)

    # if selected_type == 'Q on Q':
    #     if selected_year == "22-23":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "22-23"]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "23-24":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "23-24"]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "24-25":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['fy'] == "24-25"]
    #         #check
    #         #st.dataframe(year_filtered_df)
    # elif selected_type == 'M on M':
    #     if selected_year == "2022":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['year'] == 2022]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "2023":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['year'] == 2023]
    #         #check
    #         #st.dataframe(year_filtered_df)
    #     elif selected_year == "2024":
    #         year_filtered_df = catchment_filtered_df[catchment_filtered_df['year'] == 2024]
    #         #check
    #         #st.dataframe(year_filtered_df)

        
        
    #Filter data based on metrics
    #Filter the DataFrame for bpi parameter tags & types
    filtered_df_bpi = year_filtered_df[year_filtered_df['parameter_tag'].isin(['bpi-call_button', 'bpi-directions_button', 'bpi-website_button'])]
    #Filter the DataFrame for gm parameter tags & types
    filtered_df_gm = year_filtered_df[year_filtered_df['parameter_tag'].isin(['gm-mobile_views', 'gm-desktop_views'])]        
    #Filter the DataFrame for gs parameter tags & types        
    filtered_df_gs = year_filtered_df[year_filtered_df['parameter_tag'].isin(['gs-mobile_views', 'gs-desktop_views'])]

    #Data Preparation for chart creation based on selected type
    if selected_type == "Q on Q":
        #Group by quarter and bpi_parameter_tag and sum the count for datafrmae 
        grouped_df_bpi_a = filtered_df_bpi.groupby(['quarter','quarter_fy', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for chart
        grouped_df_bpi = filtered_df_bpi.groupby(['quarter', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_bpi = [col for col in grouped_df_bpi_a.columns if col != 'quarter']
        #Display the dataframe without the 'quarter' column
        #check
        #st.dataframe(grouped_df_bpi_a[columns_to_display_bpi])
        #st.dataframe(grouped_df_bpi_a)

        #Group by quarter and bpi_parameter_tag and sum the count for datafrmae 
        grouped_df_gm_a = filtered_df_gm.groupby(['quarter','quarter_fy', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count
        grouped_df_gm = filtered_df_gm.groupby(['quarter', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gm = [col for col in grouped_df_gm_a.columns if col != 'quarter']
        #Display the dataframe without the 'quarter' column
        #check
        #st.dataframe(grouped_df_gm_a[columns_to_display_gm])
        #st.dataframe(grouped_df_gm_a)

        #Group by quarter and bpi_parameter_tag and sum the count for datafrmae 
        grouped_df_gs_a = filtered_df_gs.groupby(['quarter','quarter_fy', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count
        grouped_df_gs = filtered_df_gs.groupby(['quarter', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gs = [col for col in grouped_df_gs_a.columns if col != 'quarter']
        #Display the dataframe without the 'quarter' column
        #check
        #st.dataframe(grouped_df_gs_a[columns_to_display_gs])
        #st.dataframe(grouped_df_gs_a)
        
    elif selected_type ==  "M on M":
        #Group by quarter and bpi_parameter_tag and sum the count for dataframe
        grouped_df_bpi_a = filtered_df_bpi.groupby(['month','month_year', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for graph
        grouped_df_bpi = filtered_df_bpi.groupby(['month', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_bpi = [col for col in grouped_df_bpi_a.columns if col != 'month']
        #Display the dataframe without the 'month' column
        #check
        #st.dataframe(grouped_df_bpi_a[columns_to_display_bpi])
        #st.dataframe(grouped_df_bpi_a)

        #Group by quarter and bpi_parameter_tag and sum the count for dataframe
        grouped_df_gm_a = filtered_df_gm.groupby(['month','month_year', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for graph
        grouped_df_gm = filtered_df_gm.groupby(['month', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gm = [col for col in grouped_df_gm_a.columns if col != 'month']
        #Display the dataframe without the 'month' column
        #check
        #st.dataframe(grouped_df_gm_a[columns_to_display_gm])
        #st.dataframe(grouped_df_gm_a)

        #Group by quarter and bpi_parameter_tag and sum the count for dataframe
        grouped_df_gs_a = filtered_df_gs.groupby(['month','month_year', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Group by quarter and bpi_parameter_tag and sum the count for graph
        grouped_df_gs = filtered_df_gs.groupby(['month', 'parameter_tag'])['count'].sum().unstack().reset_index()
        #Select only the columns you want to display (excluding 'month')
        columns_to_display_gs = [col for col in grouped_df_gs_a.columns if col != 'month']
        #Display the dataframe without the 'month' column
        #check
        #st.dataframe(grouped_df_gs_a[columns_to_display_gs])
        #st.dataframe(grouped_df_gs_a)
        
        # Define the order of months
        month_order = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec','Jan', 'Feb', 'Mar']

        #Convert the month column to a categorical type with the specified order
        grouped_df_gm['month'] = pd.Categorical(grouped_df_gm['month'], categories=month_order, ordered=True)
        grouped_df_gs['month'] = pd.Categorical(grouped_df_gs['month'], categories=month_order, ordered=True)
        grouped_df_bpi['month'] = pd.Categorical(grouped_df_bpi['month'], categories=month_order, ordered=True)
        grouped_df_gm_a['month'] = pd.Categorical(grouped_df_gm_a['month'], categories=month_order, ordered=True)
        grouped_df_gs_a['month'] = pd.Categorical(grouped_df_gs_a['month'], categories=month_order, ordered=True)
        grouped_df_bpi_a['month'] = pd.Categorical(grouped_df_bpi_a['month'], categories=month_order, ordered=True)

        #Sort the dataframe by the month column
        grouped_df_gm = grouped_df_gm.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gm[columns_to_display_gm])
        grouped_df_gs = grouped_df_gs.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gs[columns_to_display_gs])
        grouped_df_bpi = grouped_df_bpi.sort_values('month').reset_index(drop=True)    
        #check
        #st.dataframe(grouped_df_bpi[columns_to_display_bpi])

        #Sort the dataframe by the month column
        grouped_df_gm_a = grouped_df_gm_a.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gm[columns_to_display_gm])
        grouped_df_gs_a = grouped_df_gs_a.sort_values('month').reset_index(drop=True)
        #check
        #st.dataframe(grouped_df_gs[columns_to_display_gs])
        grouped_df_bpi_a = grouped_df_bpi_a.sort_values('month').reset_index(drop=True)    
        #check
        #st.dataframe(grouped_df_bpi[columns_to_display_bpi])
        
        
        
# === Front end working code ===
#Data conversion to charts based on type selected    
if submit_button:
    if selected_catchment == "Tanishq New Jersey-New Jersey (XNJ)":
        display_store = "Tanishq Jewellers - New Jersey"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq Houston-Texas (XTH)":
        display_store = "Tanishq Jewellers - Houston"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)                
    elif selected_catchment == "Tanishq Frisco-Texas (XTD)":
        display_store = "Tanishq Jewellers - Dallas"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)                
    elif selected_catchment == "Tanishq Chicago-Illinois (XCG)":
        display_store = "Tanishq Jewelers - Chicago"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq Redmond-Seattle (XWS)":
        display_store = "Tanishq Jewelers - Redmond Seattle"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq Atlanta-Georgia (XAC)":
        display_store = "Tanishq Jewelers - Atlanta"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)    
    elif selected_catchment == "Tanishq-Taj Dubai (XDT)":
        display_store = "Tanishq - Taj Dubai"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)                       
    elif selected_catchment == "Tanishq-Oman Avenue Mall (XOM)":
        display_store = "Tanishq - Oman Avenue Mall"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq-Doha Festival City (XQF)":
        display_store = "Tanishq Jewellery - Doha Festival City"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Mia-Dubai BurJuman (XDJ)":
        display_store = "Mia by Tanishq - BurJuman, Dubai"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq-Doha Lulu (XQD)":
        display_store = "Tanishq Jewellery - Doha Lulu, D Ring Rd"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)                
    elif selected_catchment == "Tanishq-Sharjah Central (XSL)":
        display_store = "Tanishq Jewellery - Sharjah Central"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq-Meena Bazar (XDM)":
        display_store = "Tanishq Jewellers - Meena Bazar"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq-Karama Centre (XDK)":
        display_store = "Tanishq Jewellers - Al Karama"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq-Al Fahidi (XDF)":
        display_store = "Tanishq Jewellers - Al Fahidi , Bur Dubai"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq-Abu Dhabi (XAH)":
        display_store = "Tanishq Jewellers - Hamdan Bin Mohammed Street"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq-Al Barsha (XDB)":
        display_store = "Tanishq Jewellers - Al Barsha"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq Jewellers-Gold Souk (XDG)":
        display_store = "Tanishq Jewellers - Gold Souk"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Mia-Al Wahda Mall (XAW)":
        display_store = "Mia by Tanishq - Al Wahda Mall"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    elif selected_catchment == "Tanishq-Silicon Central (XDS)":
        display_store = "Tanishq Jewellery - Silicon Central"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq-Rolla Sharjah (XSR)":
        display_store = "Tanishq Jewellery- Rolla, Sharjah"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq Santa Clara-California (XBA)":
        display_store = "Tanishq Jewellers - Santa Clara"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)
    elif selected_catchment == "Tanishq Jewellers-UW Mall Al Mankhool (XDX)":
        display_store = "Tanishq Jewellers-Al Mankhool UW Mall"
        st.markdown(f"<h1 class='sticky-left-header'>Metrics for {display_store}</h1>", unsafe_allow_html=True)        
    else:
        pass

#based on analysis type        
    if selected_type == "Q on Q":
        col1, col2, col3 = st.columns(3)
        with col1:
            #st.subheader(f":orange[Maps]",divider = 'grey')
            st.markdown(f"<h1 class='sticky-left-subheader'>Maps</h1>", unsafe_allow_html=True)
#----------------line graph
            st.markdown(f'**Quarter on Quarter Trend for the FY {selected_year}**')
            #Melting the dataframe for plotly compatibility
            melted_df = pd.melt(grouped_df_gm, id_vars=['quarter'], var_name='parameter_tag', value_name='views')

            #Customizing hue labels and colors
            hue_labels = {'gm-desktop_views': 'Desktop Views', 'gm-mobile_views': 'Mobile Views'}
            hue_colors = ['green', 'orange']

            #Creating the interactive line plot
            fig = px.line(
                            melted_df, 
                            x='quarter', 
                            y='views', 
                            color='parameter_tag', 
                            markers=True, 
                            #title=f'Quarter on Quarter Trend for the FY {selected_year}',
                            color_discrete_sequence=hue_colors,
                            labels={'parameter_tag': 'Views', 'quarter': f'Quarters FY {selected_year}'}
                        )

            #Updating title color to blue
            #fig.update_layout(title_font=dict(color='lightblue'))

            #Adding data labels to the plot
            fig.update_traces(text=melted_df['views'], textposition='top center')
            
            #Positioning the legend inside the graph area
            fig.update_layout(
                                legend=dict(
                                                x=0.9,
                                                y=1.3,
                                                xanchor='center',
                                                yanchor='top',
                                                #bgcolor='rgba(255,255,255,0.5)'
                                            )
                            )

            #Updating legend labels
            fig.for_each_trace(lambda t: t.update(name = hue_labels[t.name]))
            st.plotly_chart(fig, use_container_width=True)
            # Assuming grouped_df_gm is your dataframe
            grouped_df_gm = grouped_df_gm.reset_index(drop=True)

            # Display the dataframe without the index
            st.dataframe(grouped_df_gm_a[columns_to_display_gm], hide_index=True)
            
            #------------- bar graph
#             st.markdown(f'**Quarter on Quarter Trend for the FY {selected_year}**')            
#             # Melting the dataframe for plotly compatibility
#             melted_df = pd.melt(grouped_df_gm, id_vars=['quarter'], var_name='parameter_tag', value_name='views')

#             # Customizing hue labels and colors
#             hue_labels = {'gm-desktop_views': 'Desktop Views', 'gm-mobile_views': 'Mobile Views'}
#             hue_colors = ['green', 'orange']

#             # Map the parameter_tag to readable labels
#             melted_df['parameter_tag'] = melted_df['parameter_tag'].map(hue_labels)

#             # Creating the interactive bar plot
#             fig = px.bar(
#                             melted_df, 
#                             x='quarter', 
#                             y='views', 
#                             color='parameter_tag', 
#                             #title=f'Quarter on Quarter Trend for the FY {selected_year}',
#                             color_discrete_sequence=hue_colors,
#                             labels={'parameter_tag': 'Views', 'quarter': f'Quarters FY {selected_year}'},
#                             text='views'  # Adding text labels directly
#                         )

#             # Setting the bar mode to group
#             fig.update_layout(barmode='group')

#             # Adjusting text position and format
#             fig.update_traces(textposition='outside')

#             #Positioning the legend inside the graph area
#             fig.update_layout(
#                                 legend=dict(
#                                                 x=0.9,
#                                                 y=1.3,
#                                                 xanchor='center',
#                                                 yanchor='top',
#                                                 #bgcolor='rgba(255,255,255,0.5)'
#                                             )
#                             )
            
#             # Displaying the plot in Streamlit
#             st.plotly_chart(fig, use_container_width=True)
            # Display the dataframe without the index
#            st.dataframe(grouped_df_gm_a[columns_to_display_gm])         
            
            
#------------- line graph            
#             #Set the style without grid lines
#             sns.set(style="white", palette="muted")

#             #Plotting the line chart with Seaborn
#             plt.figure(figsize=(10, 6))
#             ax = sns.lineplot(data=grouped_df_gm.melt(id_vars='quarter', var_name='parameter_tag', value_name='count'),
#                               x='quarter', y='count', hue='parameter_tag', marker='o')

#             # Adding data labels above the lines
#             for i, parameter_tag in enumerate(['gm-mobile_views', 'gm-desktop_views']):
#                 for x, y in zip(grouped_df_gm['quarter'], grouped_df_gm[parameter_tag]):
#                     plt.text(x, y + (0.05 * y), str(y), fontsize=12, ha='center', va='bottom')

#             # Remove the top and right spines (borders)
#             ax.spines['top'].set_visible(False)
#             ax.spines['right'].set_visible(False)

#             # Set title with increased padding
#             plt.title('Quarter on Quarter Trend for Various Parameter Tags (FY 23-24)', pad=20)
#             plt.xlabel('Quarter')
#             plt.ylabel('Count')

#             # Rename legend labels and ensure colors are visible
#             handles, labels = ax.get_legend_handles_labels()
#             new_labels = ['Desktop Views', 'Mobile Views']
#             ax.legend(handles=handles, labels=new_labels, title='Parameter')

#             plt.grid(False)

#             # Display the plot in Streamlit
#             st.pyplot(plt)        
            
#-------------bar graph
#             # Melt the dataframe for seaborn
#             melted_df_gm = grouped_df_gm.melt(id_vars='quarter', var_name='parameter_tag', value_name='count')

#             # Plotting the vertical bar plot with Seaborn
#             plt.figure(figsize=(10, 6))
#             ax = sns.barplot(data=melted_df_gm, x='quarter', y='count', hue='parameter_tag')

#             # Adding data labels above the bars
#             for p in ax.patches:
#                 ax.annotate(format(p.get_height(), '.0f'), 
#                             (p.get_x() + p.get_width() / 2., p.get_height()), 
#                             ha = 'center', va = 'center', 
#                             xytext = (0, 9), 
#                             textcoords = 'offset points')

#             # Remove the top and right spines (borders)
#             ax.spines['top'].set_visible(False)
#             ax.spines['right'].set_visible(False)

#             # Set title with increased padding
#             plt.title('Quarter on Quarter Trend for Various Parameter Tags (FY 23-24)', pad=20)
#             plt.xlabel('Quarter')
#             plt.ylabel('Count')

#             # Rename legend labels and ensure colors are visible
#             handles, labels = ax.get_legend_handles_labels()
#             new_labels = ['Desktop Views', 'Mobile Views']
#             ax.legend(handles=handles, labels=new_labels, title='Parameter')

#             plt.grid(False)

#             # Display the plot in Streamlit
#             st.pyplot(plt)            
            
            

        with col2:
            #st.subheader(f":orange[Search]",divider = 'grey')
            st.markdown(f"<h1 class='sticky-left-subheader'>Search</h1>", unsafe_allow_html=True)
#----------------line graph      
            st.markdown(f'**Quarter on Quarter Trend for the FY {selected_year}**')
            #Melting the dataframe for plotly compatibility
            melted_df = pd.melt(grouped_df_gs, id_vars=['quarter'], var_name='parameter_tag', value_name='views')

            #Customizing hue labels and colors
            hue_labels = {'gs-desktop_views': 'Desktop Views', 'gs-mobile_views': 'Mobile Views'}
            hue_colors = ['green', 'orange']

            #Creating the interactive line plot
            fig = px.line(
                            melted_df, 
                            x='quarter', 
                            y='views', 
                            color='parameter_tag', 
                            markers=True, 
                            #title=f'Quarter on Quarter Trend for the FY {selected_year}',
                            color_discrete_sequence=hue_colors,
                            labels={'parameter_tag': 'Views', 'quarter': f'Quarters FY {selected_year}'}
                        )

            #Updating title color to blue
            #fig.update_layout(title_font=dict(color='lightblue'))

            #Adding data labels to the plot
            fig.update_traces(text=melted_df['views'], textposition='top center')
            
            #Positioning the legend inside the graph area
            fig.update_layout(
                                legend=dict(
                                                x=0.9,
                                                y=1.3,
                                                xanchor='center',
                                                yanchor='top',
                                                #bgcolor='rgba(255,255,255,0.5)'
                                            )
                            )
            
            #Updating legend labels
            fig.for_each_trace(lambda t: t.update(name = hue_labels[t.name]))
            st.plotly_chart(fig, use_container_width=True)
            # Display the dataframe without the index
            st.dataframe(grouped_df_gs_a[columns_to_display_gs],hide_index=True)

# #------------- bar graph
#             st.markdown(f'**Quarter on Quarter Trend for the FY {selected_year}**')            
#             # Melting the dataframe for plotly compatibility
#             melted_df = pd.melt(grouped_df_gs, id_vars=['quarter'], var_name='parameter_tag', value_name='views')

#             # Customizing hue labels and colors
#             hue_labels = {'gs-desktop_views': 'Desktop Views', 'gs-mobile_views': 'Mobile Views'}
#             hue_colors = ['green', 'orange']

#             # Map the parameter_tag to readable labels
#             melted_df['parameter_tag'] = melted_df['parameter_tag'].map(hue_labels)

#             # Creating the interactive bar plot
#             fig = px.bar(
#                             melted_df, 
#                             x='quarter', 
#                             y='views', 
#                             color='parameter_tag', 
#                             #title=f'Quarter on Quarter Trend for the FY {selected_year}',
#                             color_discrete_sequence=hue_colors,
#                             labels={'parameter_tag': 'Views', 'quarter': f'Quarters FY {selected_year}'},
#                             text='views'  # Adding text labels directly
#                         )

#             # Setting the bar mode to group
#             fig.update_layout(barmode='group')

#             # Adjusting text position and format
#             fig.update_traces(textposition='outside')

#             #Positioning the legend inside the graph area
#             fig.update_layout(
#                                 legend=dict(
#                                                 x=0.9,
#                                                 y=1.3,
#                                                 xanchor='center',
#                                                 yanchor='top',
#                                                 #bgcolor='rgba(255,255,255,0.5)'
#                                             )
#                             )

#             # Displaying the plot in Streamlit
#             st.plotly_chart(fig, use_container_width=True)
            # Display the dataframe without the index
#            st.dataframe(grouped_df_gm_a[columns_to_display_gm])            

        with col3:
            #st.subheader(f":orange[Interactions]",divider = 'grey')
            st.markdown(f"<h1 class='sticky-left-subheader'>Interactions</h1>", unsafe_allow_html=True)            
#----------------line graph            
            st.markdown(f'**Quarter on Quarter Trend for the FY {selected_year}**')
            #Melting the dataframe for plotly compatibility
            melted_df = pd.melt(grouped_df_bpi, id_vars=['quarter'], var_name='parameter_tag', value_name='interactions')

            #Customizing hue labels and colors
            hue_labels = {'bpi-call_button' : 'Call Button', 'bpi-directions_button' : 'Direction Button', 'bpi-website_button' :  'Website Button'}
            hue_colors = ['green', 'orange', 'blue']

            #Creating the interactive line plot
            fig = px.line(
                            melted_df, 
                            x='quarter', 
                            y='interactions', 
                            color='parameter_tag', 
                            markers=True, 
                            #title=f'Quarter on Quarter Trend for the FY {selected_year}',
                            color_discrete_sequence=hue_colors,
                            labels={'parameter_tag': 'Interaction Type', 'quarter' : f'Quarters FY {selected_year}'}
                        )

            #Updating title color to blue
            #fig.update_layout(title_font=dict(color='lightblue'))

            #Adding data labels to the plot
            fig.update_traces(text=melted_df['interactions'], textposition='top center')

            #Positioning the legend inside the graph area
            fig.update_layout(
                                legend=dict(
                                                x=0.9,
                                                y=1.3,
                                                xanchor='center',
                                                yanchor='top',
                                                #bgcolor='rgba(255,255,255,0.5)'
                                            )
                            )

            #Updating legend labels
            fig.for_each_trace(lambda t: t.update(name = hue_labels[t.name]))
            st.plotly_chart(fig, use_container_width=True)
            # Display the dataframe without the index
            st.dataframe(grouped_df_bpi_a[columns_to_display_bpi],hide_index=True)
            
#------------- bar graph
#             st.markdown(f'**Quarter on Quarter Trend for the FY {selected_year}**')
#             # Melting the dataframe for plotly compatibility
#             melted_df = pd.melt(grouped_df_bpi, id_vars=['quarter'], var_name='parameter_tag', value_name='interactions')

#             #Customizing hue labels and colors
#             hue_labels = {'bpi-call_button' : 'Call Button Interactions', 'bpi-directions' : 'Direction Button Interactions', 'bpi-website' :  'Website Button Interactions'}
#             hue_colors = ['green', 'orange', 'blue']

#             # Map the parameter_tag to readable labels
#             melted_df['parameter_tag'] = melted_df['parameter_tag'].map(hue_labels)

#             # Creating the interactive bar plot
#             fig = px.bar(
#                             melted_df, 
#                             x='quarter', 
#                             y='interactions', 
#                             color='parameter_tag', 
#                             #title=f'Quarter on Quarter Trend for the FY {selected_year}',
#                             color_discrete_sequence=hue_colors,
#                             labels={'parameter_tag': 'Interactions Type'},
#                             text='interactions'  # Adding text labels directly
#                         )

#             # Setting the bar mode to group
#             fig.update_layout(barmode='group')

#             # Adjusting text position and format
#             fig.update_traces(textposition='outside')

#             #Positioning the legend inside the graph area
#             fig.update_layout(
#                                 legend=dict(
#                                                 x=0.9,
#                                                 y=1.3,
#                                                 xanchor='center',
#                                                 yanchor='top',
#                                                 #bgcolor='rgba(255,255,255,0.5)'
#                                             )
#                             )
            
#             # Displaying the plot in Streamlit
#             st.plotly_chart(fig, use_container_width=True)
            # Display the dataframe without the index
#            st.dataframe(grouped_df_gm_a[columns_to_display_gm])
           
    elif selected_type == "M on M":
        col1, col2, col3 = st.columns(3)
 
        with col1:
            #st.subheader(f":orange[Maps]",divider = 'grey')
            st.markdown(f"<h1 class='sticky-left-subheader'>Maps</h1>", unsafe_allow_html=True)            
#----------------line graph  
            st.markdown(f'**Month on Month Trend for the year {selected_year}**')
            #Melting the dataframe for plotly compatibility
            melted_df = pd.melt(grouped_df_gm, id_vars=['month'], var_name='parameter_tag', value_name='views')

            #Customizing hue labels and colors
            hue_labels = {'gm-desktop_views': 'Desktop Views', 'gm-mobile_views': 'Mobile Views'}
            hue_colors = ['green', 'orange']

            #Creating the interactive line plot
            fig = px.line(
                            melted_df, 
                            x='month', 
                            y='views', 
                            color='parameter_tag', 
                            markers=True, 
                            #title=f'Month on Month Trend for the year {selected_year}',
                            color_discrete_sequence=hue_colors,
                            labels={'parameter_tag': 'Views', 'month': f'Months FY {selected_year}'},
                            #category_orders={'month': month_order}
            )

            #Updating title color to blue
            #fig.update_layout(title_font=dict(color='lightblue'))

            #Adding data labels to the plot
            fig.update_traces(text=melted_df['views'], textposition='top center')
            
            #Positioning the legend inside the graph area
            fig.update_layout(
                                legend=dict(
                                                x=0.9,
                                                y=1.3,
                                                xanchor='center',
                                                yanchor='top',
                                                #bgcolor='rgba(255,255,255,0.5)'
                                            )
                            )

            #Updating legend labels
            fig.for_each_trace(lambda t: t.update(name = hue_labels[t.name]))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(grouped_df_gm_a[columns_to_display_gm],hide_index=True)

#------------- bar graph
#             st.markdown(f'**Month on Month Trend for the year {selected_year}**')
#             # Melting the dataframe for plotly compatibility
#             melted_df = pd.melt(grouped_df_gm, id_vars=['month'], var_name='parameter_tag', value_name='views')

#             # Customizing hue labels and colors
#             hue_labels = {'gm-desktop_views': 'Desktop Views', 'gm-mobile_views': 'Mobile Views'}
#             hue_colors = ['green', 'orange']

#             # Map the parameter_tag to readable labels
#             melted_df['parameter_tag'] = melted_df['parameter_tag'].map(hue_labels)

#             # Creating the interactive bar plot
#             fig = px.bar(
#                             melted_df, 
#                             x='month', 
#                             y='views', 
#                             color='parameter_tag', 
#                             #title=f'Month on Month Trend for the year {selected_year}',
#                             color_discrete_sequence=hue_colors,
#                             labels={'parameter_tag': 'Views', 'month': f'Months FY {selected_year}'},
#                             text='views'  # Adding text labels directly
#                         )

#             # Setting the bar mode to group
#             fig.update_layout(barmode='group')

#             # Adjusting text position and format
#             fig.update_traces(textposition='outside')

#             #Positioning the legend inside the graph area
#             fig.update_layout(
#                                 legend=dict(
#                                                 x=0.9,
#                                                 y=1.3,
#                                                 xanchor='center',
#                                                 yanchor='top',
#                                                 #bgcolor='rgba(255,255,255,0.5)'
#                                             )
#                             )
            
#             # Displaying the plot in Streamlit
#             st.plotly_chart(fig, use_container_width=True)
#             #st.dataframe(grouped_df_gm)            
            
            
#------------- line graph            
#             #Set the style without grid lines
#             sns.set(style="white", palette="muted")

#             #Plotting the line chart with Seaborn
#             plt.figure(figsize=(10, 6))
#             ax = sns.lineplot(data=grouped_df_gm.melt(id_vars='month', var_name='parameter_tag', value_name='count'),
#                               x='Month', y='count', hue='parameter_tag', marker='o')

#             # Adding data labels above the lines
#             for i, parameter_tag in enumerate(['gm-mobile_views', 'gm-desktop_views']):
#                 for x, y in zip(grouped_df_gm['month'], grouped_df_gm[parameter_tag]):
#                     plt.text(x, y + (0.05 * y), str(y), fontsize=12, ha='center', va='bottom')

#             # Remove the top and right spines (borders)
#             ax.spines['top'].set_visible(False)
#             ax.spines['right'].set_visible(False)

#             # Set title with increased padding
#             plt.title('Month on Month Trend for Various Parameter Tags (FY 23-24)', pad=20)
#             plt.xlabel('Month')
#             plt.ylabel('Count')

#             # Rename legend labels and ensure colors are visible
#             handles, labels = ax.get_legend_handles_labels()
#             new_labels = ['Desktop Views', 'Mobile Views']
#             ax.legend(handles=handles, labels=new_labels, title='Parameter')

#             plt.grid(False)

#             # Display the plot in Streamlit
#             st.pyplot(plt)        
            
#-------------bar graph
#             # Melt the dataframe for seaborn
#             melted_df_gm = grouped_df_gm.melt(id_vars='month', var_name='parameter_tag', value_name='count')

#             # Plotting the vertical bar plot with Seaborn
#             plt.figure(figsize=(10, 6))
#             ax = sns.barplot(data=melted_df_gm, x='month', y='count', hue='parameter_tag')

#             # Adding data labels above the bars
#             for p in ax.patches:
#                 ax.annotate(format(p.get_height(), '.0f'), 
#                             (p.get_x() + p.get_width() / 2., p.get_height()), 
#                             ha = 'center', va = 'center', 
#                             xytext = (0, 9), 
#                             textcoords = 'offset points')

#             # Remove the top and right spines (borders)
#             ax.spines['top'].set_visible(False)
#             ax.spines['right'].set_visible(False)

#             # Set title with increased padding
#             plt.title('Month on Month Trend for Various Parameter Tags (FY 23-24)', pad=20)
#             plt.xlabel('Month')
#             plt.ylabel('Count')

#             # Rename legend labels and ensure colors are visible
#             handles, labels = ax.get_legend_handles_labels()
#             new_labels = ['Desktop Views', 'Mobile Views']
#             ax.legend(handles=handles, labels=new_labels, title='Parameter')

#             plt.grid(False)

#             # Display the plot in Streamlit
#             st.pyplot(plt)            
            
            

        with col2:
            #st.subheader(f":orange[Search]",divider = 'grey')
            st.markdown(f"<h1 class='sticky-left-subheader'>Search</h1>", unsafe_allow_html=True)            
#----------------line graph
            st.markdown(f'**Month on Month Trend for the year {selected_year}**')
            #Melting the dataframe for plotly compatibility
            melted_df = pd.melt(grouped_df_gs, id_vars=['month'], var_name='parameter_tag', value_name='views')

            #Customizing hue labels and colors
            hue_labels = {'gs-desktop_views': 'Desktop Views', 'gs-mobile_views': 'Mobile Views'}
            hue_colors = ['green', 'orange']

            #Creating the interactive line plot
            fig = px.line(
                            melted_df, 
                            x='month', 
                            y='views', 
                            color='parameter_tag', 
                            markers=True, 
                            #title=f'Month on Month Trend for the year {selected_year}',
                            color_discrete_sequence=hue_colors,
                            labels={'parameter_tag': 'Views', 'month': f'Months FY {selected_year}'}
                        )

            #Updating title color to blue
            #fig.update_layout(title_font=dict(color='lightblue'))

            #Adding data labels to the plot
            fig.update_traces(text=melted_df['views'], textposition='top center')
            
            #Positioning the legend inside the graph area
            fig.update_layout(
                                legend=dict(
                                                x=0.9,
                                                y=1.3,
                                                xanchor='center',
                                                yanchor='top',
                                                #bgcolor='rgba(255,255,255,0.5)'
                                            )
                            )
            
            #Updating legend labels
            fig.for_each_trace(lambda t: t.update(name = hue_labels[t.name]))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(grouped_df_gs_a[columns_to_display_gs],hide_index=True)

#------------- bar graph
#             st.markdown(f'**Month on Month Trend for the year {selected_year}**')            
#             # Melting the dataframe for plotly compatibility
#             melted_df = pd.melt(grouped_df_gs, id_vars=['month'], var_name='parameter_tag', value_name='views')

#             # Customizing hue labels and colors
#             hue_labels = {'gs-desktop_views': 'Desktop Views', 'gs-mobile_views': 'Mobile Views'}
#             hue_colors = ['green', 'orange']

#             # Map the parameter_tag to readable labels
#             melted_df['parameter_tag'] = melted_df['parameter_tag'].map(hue_labels)

#             # Creating the interactive bar plot
#             fig = px.bar(
#                             melted_df, 
#                             x='month', 
#                             y='views', 
#                             color='parameter_tag', 
#                             #title=f'Month on Month Trend for the year {selected_year}',
#                             color_discrete_sequence=hue_colors,
#                             labels={'parameter_tag': 'Views', 'month': f'Months FY {selected_year}'},
#                             text='views'  # Adding text labels directly
#                         )

#             # Setting the bar mode to group
#             fig.update_layout(barmode='group')

#             # Adjusting text position and format
#             fig.update_traces(textposition='outside')

#             #Positioning the legend inside the graph area
#             fig.update_layout(
#                                 legend=dict(
#                                                 x=0.9,
#                                                 y=1.3,
#                                                 xanchor='center',
#                                                 yanchor='top',
#                                                 #bgcolor='rgba(255,255,255,0.5)'
#                                             )
#                             )

#             # Displaying the plot in Streamlit
#             st.plotly_chart(fig, use_container_width=True)
#             #st.dataframe(grouped_df_gs)            

        with col3:
            #st.subheader(f":orange[Interactions]",divider = 'grey')
            st.markdown(f"<h1 class='sticky-left-subheader'>Interactions</h1>", unsafe_allow_html=True)              
#----------------line graph            
            st.markdown(f'**Month on Month Trend for the year {selected_year}**')
            #Melting the dataframe for plotly compatibility
            melted_df = pd.melt(grouped_df_bpi, id_vars=['month'], var_name='parameter_tag', value_name='interactions')

            #Customizing hue labels and colors
            hue_labels = {'bpi-call_button' : 'Call Button', 'bpi-directions_button' : 'Direction Button', 'bpi-website_button' :  'Website Button'}
            hue_colors = ['green', 'orange', 'blue']

            #Creating the interactive line plot
            fig = px.line(
                            melted_df, 
                            x='month', 
                            y='interactions', 
                            color='parameter_tag', 
                            markers=True, 
                            #title=f'Month on Month Trend for the year {selected_year}',
                            color_discrete_sequence=hue_colors,
                            labels={'parameter_tag': 'Interactions', 'month':f'Months FY {selected_year}'}
                        )

            #Updating title color to blue
            #fig.update_layout(title_font=dict(color='lightblue'))

            #Adding data labels to the plot
            fig.update_traces(text=melted_df['interactions'], textposition='top center')
            
            #Positioning the legend inside the graph area
            fig.update_layout(
                                legend=dict(
                                                x=0.9,
                                                y=1.3,
                                                xanchor='center',
                                                yanchor='top',
                                                #bgcolor='rgba(255,255,255,0.5)'
                                            )
                            )
            
            #Updating legend labels
            fig.for_each_trace(lambda t: t.update(name = hue_labels[t.name]))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(grouped_df_bpi_a[columns_to_display_bpi],hide_index=True)

            
#------------- bar graph
#             st.markdown(f'**Month on Month Trend for the year {selected_year}**')
#             # Melting the dataframe for plotly compatibility
#             melted_df = pd.melt(grouped_df_bpi, id_vars=['month'], var_name='parameter_tag', value_name='interactions')

#             #Customizing hue labels and colors
#             hue_labels = {'bpi-call_button' : 'Call Button Interactions', 'bpi-directions' : 'Direction Button Interactions', 'bpi-website' :  'Website Button Interactions'}
#             hue_colors = ['green', 'orange', 'blue']

#             # Map the parameter_tag to readable labels
#             melted_df['parameter_tag'] = melted_df['parameter_tag'].map(hue_labels)

#             # Creating the interactive bar plot
#             fig = px.bar(
#                             melted_df, 
#                             x='month', 
#                             y='interactions', 
#                             color='parameter_tag', 
#                             #title=f'Month on Month Trend for the year {selected_year}',
#                             color_discrete_sequence=hue_colors,
#                             labels={'parameter_tag': 'Interactions', 'month':f'Months FY {selected_year}'},
#                             text='interactions'  # Adding text labels directly
#                         )

#             # Setting the bar mode to group
#             fig.update_layout(barmode='group')

#             # Adjusting text position and format
#             fig.update_traces(textposition='outside')

#             #Positioning the legend inside the graph area
#             fig.update_layout(
#                                 legend=dict(
#                                                 x=0.9,
#                                                 y=1.3,
#                                                 xanchor='center',
#                                                 yanchor='top',
#                                                 #bgcolor='rgba(255,255,255,0.5)'
#                                             )
#                             )
            
#             # Displaying the plot in Streamlit
#             st.plotly_chart(fig, use_container_width=True)
#             #st.dataframe(grouped_df_bpi)                    
###==Download Sentiment Data==

    st.markdown(get_table_download_link(year_filtered_df[['country','store','parameter','count','year','month','quarter','fy']]), unsafe_allow_html=True)