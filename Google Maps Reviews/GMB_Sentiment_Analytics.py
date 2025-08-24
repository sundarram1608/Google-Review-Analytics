import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from PIL import Image
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components
import base64
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
import io
import json


# === Page Configuration ===
st.set_page_config(page_title="Google Review Analytics", 
                   layout='wide', 
                   initial_sidebar_state = 'expanded', 
                   menu_items={'About': f"Google Review Analytics Webapp.\n\nThis platform visualizes the Sentiment Analytics on Google Maps reviews for certain Jewellery stores of USA & UAE.\n Time Period: Apr 2024 to May 2025"})


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
            color: #FFBD36;
            /*text-decoration: underline;*/
            padding: 75px 0; /* Add some padding */
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
#Function to convert dataframe to Excel and return it as a BytesIO object (in-memory file)
def dataframe_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        writer.save()
    output.seek(0)  # Go back to the beginning of the BytesIO stream
    return output

#Function to create a zip file in memory
def create_zip(files_data):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'a') as zip_file:
        for file_name, data in files_data:
            zip_file.writestr(file_name, data.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

#Function to convert the ZIP buffer to a base64 string
def get_zip_base64(zip_buffer):
    return base64.b64encode(zip_buffer.read()).decode('utf-8')

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
    
# === Mapping of stores & countries ===
stores_dict = {"Select a Country":[],
                "GCC":["Tanishq Jewellers-Al Barsha, DB",
                        "Tanishq Jewellers-Al Fahidi, DB",
                        "Tanishq Jewellers-Al Karama, DB",
                        "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD",
                        "Tanishq Jewellers-Meena Bazar, DB",
                        "Tanishq Jewellers-Silicon Central, DB",
                        "Mia-Al Wahda Mall, AD",
                        "Mia-Burjuman, DB",
                        "Tanishq Jewellers-Avenues Mall, OM",
                        "Tanishq Jewellers-Festival City, QA",
                        "Tanishq Jewellers-Gold Souk, DB",
                        "Tanishq Jewellers-Lulu Hypermarket, QA",
                        "Tanishq Jewellers-UW Mall Al Mankhool, DB",
                        "Tanishq Jewellers-Rolla, SH",
                        "Tanishq Jewellers-Sharjah Central, SH",
                        "Tanishq Jewellers-Taj, DB",
                        "Joyalukkas Jewellery(AF)",
                        "Joyalukkas Jewellery - AF St(AF)",
                        "Malabar - AF St - Branch 1(AF)",
                        "Malabar - SAK Building - Branch 2(AF)",
                        "Malabar Gold and Diamonds(MB)",
                        "Meena Jewellers(MB)",
                        "Joyalukkas - Dalma Plaza(AD)",
                        "Joyalukkas - Shabia(AD)",
                        "Joyalukkas - Madinat Zayed(AD)",
                        "Malabar - Al Wahda Mall(AD)",
                        "Malabar - Hamdan Street - 1 (AD)",
                        "Malabar - Hamdan Street - 2 (AD)",
                        "Malabar - Dalma Mall(AD)",
                        "Malabar - Lulu Hypermarket(AD)",
                        "Malabar - Shabia Musaffah(AD)",
                        "Joyalukkas Jewellery(AB)",
                        "Malabar Gold and Diamonds(AB)",
                        "Joyalukkas Jewellery(AK)",
                        "Malabar Gold and Diamonds(AK)",
                        "Bhima(AK)",
                        "Mint(AK)",
                        "Malabar Gold and Diamonds(SC)",
                        "Arakkal Gold and Diamonds(MB)",
                        "Kanz Jewellers(MB)"], 
                "USA":["Tanishq-Chicago, IL",
                        "Tanishq-Frisco, TX",
                        "Tanishq-Houston, TX",
                        "Tanishq-New Jersey, NJ",
                        "Tanishq-Atlanta, GA",
                        "Tanishq-Redmond Seattle, WA",
                        "Tanishq-Santa Clara, CA",
                        "Jared-Aurora, IL",
                        "Jared-Lombard, IL",
                        "Jared-Schaumburg, IL",
                        "Jared-Bolingbrook, IL",
                        "Jared-Algonquin, IL",
                        "Jared-Orland Park, IL",
                        "Jared-Vernon Hills, IL",
                        "Joyalukkas Jewellery-Chicago, IL",
                        "Joyalukkas Jewellery-Houston, TX",
                        "Joyalukkas Jewellery-Frisco, TX",
                        "Malabar Gold & Diamonds-Chicago, IL",
                        "Malabar Gold & Diamonds-Naperville, IL",
                        "Malabar Gold & Diamonds-Iselin, NJ",
                        "Malabar Gold & Diamonds-Frisco, TX",
                        "Malani Jewellers-Richardson, TX",
                        "May Jewelers-Vienna, VA",
                        "Sona Jewelers-Iselin, NJ",
                        "Tiffany & Co-Northbrook, IL",
                        "Tiffany & Co-Skokie, IL",
                        "Tiffany & Co-Chicago, IL",
                        "Tiffany & Co-Paramus, NJ",
                        "Tiffany & Co-Hackensack, NJ",
                        "Tiffany & Co-East Rutherford, NJ",
                        "Tiffany & Co-Red Bank, NJ",
                        "Tiffany & Co-Short Hills, NJ",
                        "Tiffany & Co-Vienna, VA",
                        "Tiffany & Co-Richmond, VA",
                        "VBJ Jewellers-Frisco, TX"]}

# List of countries
countries = list(stores_dict.keys())


mapping_dict = {
                "Joyalukkas Jewellery(AF)": "Joyalukkas Jewellery - Al Fahidi",
                "Joyalukkas Jewellery - AF St(AF)": "Joyalukkas Jewellery - Al Fahidi st - Al Fahidi",
                "Malabar - AF St - Branch 1(AF)": "Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)",
                "Malabar - SAK Building - Branch 2(AF)": "Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)",
                "Malabar Gold and Diamonds(MB)": "Malabar Gold and Diamonds - Meena Bazar - Dubai",
                "Meena Jewellers(MB)": "Meena Jewellers - Meena Bazar",
                "Joyalukkas - Dalma Plaza(AD)": "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi",
                "Joyalukkas - Shabia(AD)": "Joyalukkas Jewellery - Shabia - Abu Dhabi",
                "Joyalukkas - Madinat Zayed(AD)": "Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi",
                "Malabar - Al Wahda Mall(AD)": "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi",
                "Malabar - Hamdan Street - 1 (AD)": "Malabar Gold and Diamonds - Hamdan Street ( Branch 1)",
                "Malabar - Hamdan Street - 2 (AD)": "Malabar Gold and Diamonds - Hamdan Street (Branch 2)",
                "Malabar - Dalma Mall(AD)": "Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi",
                "Malabar - Lulu Hypermarket(AD)": "Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed",
                "Malabar - Shabia Musaffah(AD)": "Malabar Gold and Diamonds - Shabia Musaffah",
                "Joyalukkas Jewellery(AB)": "Joyalukkas Jewellery - Al Barsha",
                "Malabar Gold and Diamonds(AB)": "Malabar Gold and Diamonds - Al Barsha - Dubai",
                "Joyalukkas Jewellery(AK)": "Joyalukkas Jewellery - Al Karama",
                "Malabar Gold and Diamonds(AK)": "Malabar Gold and Diamonds - Al Karama - Dubai",
                "Bhima(AK)": "Bhima Jewellers - Al Karama",
                "Mint(AK)": "Mint Jewels - Al Karama",
                "Malabar Gold and Diamonds(SC)": "Malabar Gold & Diamonds - Silicon Oasis Central",
                "Arakkal Gold and Diamonds(MB)": "Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)",
                "Kanz Jewellers(MB)": "Kanz Jewellers",    
                "Jared-Aurora, IL":"Jared-Aurora, IL",
                "Jared-Lombard, IL":"Jared-Lombard, IL",
                "Jared-Schaumburg, IL":"Jared-Schaumburg, IL",
                "Jared-Bolingbrook, IL":"Jared-Bolingbrook, IL",
                "Jared-Algonquin, IL":"Jared-Algonquin, IL",
                "Jared-Orland Park, IL":"Jared-Orland Park, IL",
                "Jared-Vernon Hills, IL":"Jared-Vernon Hills, IL",
                "Joyalukkas Jewellery-Chicago, IL":"Joyalukkas Jewellery-Chicago, IL",
                "Joyalukkas Jewellery-Houston, TX":"Joyalukkas Jewellery-Houston, TX",
                "Joyalukkas Jewellery-Frisco, TX":"Joyalukkas Jewellery-Frisco, TX",
                "Malabar Gold & Diamonds-Chicago, IL":"Malabar Gold & Diamonds-Chicago, IL",
                "Malabar Gold & Diamonds-Naperville, IL":"Malabar Gold & Diamonds-Naperville, IL",
                "Malabar Gold & Diamonds-Iselin, NJ":"Malabar Gold & Diamonds-Iselin, NJ",
                "Malabar Gold & Diamonds-Frisco, TX":"Malabar Gold & Diamonds-Frisco, TX",
                "Malani Jewellers-Richardson, TX":"Malani Jewellers-Richardson, TX",
                "May Jewelers-Vienna, VA":"May Jewelers-Vienna, VA",
                "Sona Jewelers-Iselin, NJ":"Sona Jewelers-Iselin, NJ",
                "Tiffany & Co-Northbrook, IL":"Tiffany & Co-Northbrook, IL",
                "Tiffany & Co-Skokie, IL":"Tiffany & Co-Skokie, IL",
                "Tiffany & Co-Chicago, IL":"Tiffany & Co-Chicago, IL",
                "Tiffany & Co-Paramus, NJ":"Tiffany & Co-Paramus, NJ",
                "Tiffany & Co-Hackensack, NJ":"Tiffany & Co-Hackensack, NJ",
                "Tiffany & Co-East Rutherford, NJ":"Tiffany & Co-East Rutherford, NJ",
                "Tiffany & Co-Red Bank, NJ":"Tiffany & Co-Red Bank, NJ",
                "Tiffany & Co-Short Hills, NJ":"Tiffany & Co-Short Hills, NJ",
                "Tiffany & Co-Vienna, VA":"Tiffany & Co-Vienna, VA",
                "Tiffany & Co-Richmond, VA":"Tiffany & Co-Richmond, VA",
                "VBJ Jewellers-Frisco, TX":"VBJ Jewellers-Frisco, TX",
        
                "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD" : "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD",
                "Tanishq Jewellers-Al Karama, DB" : "Tanishq Jewellers-Al Karama, DB",
                "Tanishq Jewellers-Al Fahidi, DB" : "Tanishq Jewellers-Al Fahidi, DB",
                "Tanishq Jewellers-Al Barsha, DB" : "Tanishq Jewellers-Al Barsha, DB",
                "Tanishq Jewellers-Meena Bazar, DB" : "Tanishq Jewellers-Meena Bazar, DB",
                "Tanishq Jewellers-Silicon Central, DB" : "Tanishq Jewellers-Silicon Central, DB",
                "Mia-Al Wahda Mall, AD" : "Mia-Al Wahda Mall, AD",
                "Mia-Burjuman, DB":"Mia-Burjuman, DB",
                "Tanishq Jewellers-Avenues Mall, OM":"Tanishq Jewellers-Avenues Mall, OM",
                "Tanishq Jewellers-Festival City, QA":"Tanishq Jewellers-Festival City, QA",
                "Tanishq Jewellers-Gold Souk, DB":"Tanishq Jewellers-Gold Souk, DB",
                "Tanishq Jewellers-Lulu Hypermarket, QA":"Tanishq Jewellers-Lulu Hypermarket, QA",
                "Tanishq Jewellers-UW Mall Al Mankhool, DB":"Tanishq Jewellers-UW Mall Al Mankhool, DB",
                "Tanishq Jewellers-Rolla, SH":"Tanishq Jewellers-Rolla, SH",
                "Tanishq Jewellers-Sharjah Central, SH":"Tanishq Jewellers-Sharjah Central, SH",
               "Tanishq Jewellers-Taj, DB":"Tanishq Jewellers-Taj, DB",                            
                "Tanishq-Chicago, IL":"Tanishq-Chicago, IL",
                "Tanishq-Frisco, TX":"Tanishq-Frisco, TX",
                "Tanishq-Houston, TX":"Tanishq-Houston, TX",
                "Tanishq-New Jersey, NJ":"Tanishq-New Jersey, NJ",
                "Tanishq-Atlanta, GA":"Tanishq-Atlanta, GA",
               "Tanishq-Redmond Seattle, WA":"Tanishq-Redmond Seattle, WA",
               "Tanishq-Santa Clara, CA":"Tanishq-Santa Clara, CA"
                }

# === Front End UI coding ===
# Title - Display image and text
st.markdown(f"""
            <div class="container">
            <img class="logo-img" src="data:image/png;base64,{img_to_base64(Image.open("GMB.png"))}">
            <h1 style="color: #4AB4FF;">GMB Review Analytics</h1>
            </div>""", unsafe_allow_html=True)


#Create radio buttons in the sidebar
with st.sidebar:        
    #Create a column layout for the country and catchment selection
    col1, col2 = st.columns(2)
    with col1:
        #Create a dropdown to select a country
        selected_country = st.selectbox("Select a country", countries, index=0)

    with col2:
        # Check if a country has been selected
        if selected_country != "Select a country":
            stores_list = stores_dict[selected_country]
            # Create a second drop-down select box for the user to choose a catchment area
            selected_store1 = st.selectbox("Select a store", stores_list, index=0)

    if selected_store1 is not None:
        filtered_store_list = [store for store in stores_list if store != selected_store1]
        # Create a third drop-down select box for selecting competitors in the chosen catchmen
        selected_store2 = st.selectbox("Select a second store", filtered_store_list, index=0) 

        multi_comparison_stores = st.checkbox("Compare another store")             
        if multi_comparison_stores:
        # If multi-store comparison is enabled, create a select box for store 3
            filtered_store_list2 = [store for store in filtered_store_list if store != selected_store2]
            selected_store3 = st.selectbox("Select a third store", filtered_store_list2, index=0)

    submit_button_stores = st.button("Analyze",key="submit_stores",help="Click to start analysis")
    
# === Back end working code ===
if selected_country == "GCC":
    if submit_button_stores:
        #Reading data
        combined_df = pd.read_parquet("final_sentiment_mapped/combined_df_final_S.parquet", engine='pyarrow')
        combined_df_keywords = pd.read_parquet("recent_keywords_filtered/combined_keywords.parquet", engine='pyarrow')
        #st.dataframe(combined_df_keywords)
#for Country Level Summary
        country_level_data = combined_df[combined_df['Country'] == "GCC"]
    
#for Catchment Level Summary    
        store_name = mapping_dict[selected_store1]
        selected_store1_group = combined_df[combined_df['Store Name'] == store_name]['Catchment'].iloc[0]
        #st.write(selected_store1_group)
        catchment_level_stores_df = combined_df[combined_df['Catchment'] == selected_store1_group]
        #st.dataframe(catchment_level_stores_df)
        group_store_list = catchment_level_stores_df['Grouped Store Name'].unique().tolist()
        #st.write(group_store_list)
        #Initialize an empty dictionary to hold the dataframes
        group_level_dataframes_dict = {}
        for group_store_name in group_store_list:
            #Create the dataframe name by appending 'df' to the group_store_name
            dataframe_name = f"{group_store_name}_df"
            #Filter the catchment_level_stores_df to get only the rows with the current group_store_name
            filtered_df = catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == group_store_name]
            #Store the filtered dataframe in the dictionary with the new name as key
            group_level_dataframes_dict[dataframe_name] = filtered_df

        # Filter the dataframe based on store1 area selection
        if selected_store1 == "Tanishq Jewellers-Al Fahidi, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Fahidi, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Fahidi, DB"] 
        elif selected_store1 == "Tanishq Jewellers-Meena Bazar, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Meena Bazar, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Meena Bazar"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Meena Bazar, DB"]
        elif selected_store1 == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD"]
        elif selected_store1 == "Tanishq Jewellers-Al Barsha, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Barsha, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Barsha, DB"]
        elif selected_store1 == "Tanishq Jewellers-Al Karama, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Karama, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Karama"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Karama, DB"]
        elif selected_store1 == "Tanishq Jewellers-Silicon Central, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Silicon Central, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Silicon Central, DB"]
        elif selected_store1 == "Mia-Al Wahda Mall, AD":
            store1_df = combined_df[combined_df['Store Name'] == "Mia-Al Wahda Mall, AD"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Mia-Al Wahda Mall, AD"]
        elif selected_store1 == "Mia-Burjuman, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Mia-Burjuman, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Mia-Burjuman, DB"]
        elif selected_store1 == "Tanishq Jewellers-Avenues Mall, OM":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Avenues Mall, OM"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Avenues Mall, OM"]
        elif selected_store1 == "Tanishq Jewellers-Festival City, QA":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Festival City, QA"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Festival City, QA"]
        elif selected_store1 == "Tanishq Jewellers-Gold Souk, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Gold Souk, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Gold Souk, DB"]
        elif selected_store1 == "Tanishq Jewellers-Lulu Hypermarket, QA":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Lulu Hypermarket, QA"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Lulu Hypermarket, QA"]
        elif selected_store1 == "Tanishq Jewellers-UW Mall Al Mankhool, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-UW Mall Al Mankhool, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-UW Mall Al Mankhool, DB"]
        elif selected_store1 == "Tanishq Jewellers-Rolla, SH":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Rolla, SH"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Rolla, SH"]            
        elif selected_store1 == "Tanishq Jewellers-Sharjah Central, SH":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Sharjah Central, SH"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Sharjah Central, SH"]
        elif selected_store1 == "Tanishq Jewellers-Taj, DB":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Taj, DB"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Taj, DB"]
        elif selected_store1 == "Joyalukkas Jewellery(AF)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi"])]
        elif selected_store1 == "Joyalukkas Jewellery - AF St(AF)":
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi st - Al Fahidi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi st - Al Fahidi"])]
        elif selected_store1 == "Malabar - AF St - Branch 1(AF)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)"])] 
        elif selected_store1 == "Malabar - SAK Building - Branch 2(AF)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)"])]
        elif selected_store1 == "Malabar Gold and Diamonds(MB)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Meena Bazar - Dubai"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Meena Bazar - Dubai"])]   
        elif selected_store1 == "Meena Jewellers(MB)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Meena Jewellers - Meena Bazar"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Meena Jewellers - Meena Bazar"])]            
        elif selected_store1 == "Joyalukkas - Dalma Plaza(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin([ "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi"])]        
        elif selected_store1 == "Joyalukkas - Shabia(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin([ "Joyalukkas Jewellery - Shabia - Abu Dhabi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Shabia - Abu Dhabi"])]        
        elif selected_store1 == "Joyalukkas - Madinat Zayed(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi"])]
        elif selected_store1 == "Malabar - Al Wahda Mall(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin([ "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi"])]        
        elif selected_store1 == "Malabar - Hamdan Street - 1 (AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street ( Branch 1)"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Hamdan Street ( Branch 1)"])]        
        elif selected_store1 == "Malabar - Hamdan Street - 2 (AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street (Branch 2)"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street (Branch 2)"])]        
        elif selected_store1 == "Malabar - Dalma Mall(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi"])]        
        elif selected_store1 == "Malabar - Lulu Hypermarket(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed"])]
        elif selected_store1 == "Malabar - Shabia Musaffah(AD)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Shabia Musaffah"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Shabia Musaffah"])]      
        elif selected_store1 == "Joyalukkas Jewellery(AB)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Barsha"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Barsha"])]        
        elif selected_store1 == "Malabar Gold and Diamonds(AB)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Barsha - Dubai"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Barsha - Dubai"])]     
        elif selected_store1 == "Joyalukkas Jewellery(AK)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Karama"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Karama"])]        
        elif selected_store1 == "Malabar Gold and Diamonds(AK)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Karama - Dubai"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Karama - Dubai"])]     
        elif selected_store1 == "Bhima(AK)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Bhima Jewellers - Al Karama"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Bhima Jewellers - Al Karama"])]        
        elif selected_store1 == "Mint(AK)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Mint Jewels - Al Karama"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Mint Jewels - Al Karama"])]        
        elif selected_store1 == "Malabar Gold and Diamonds(SC)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds - Silicon Oasis Central"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds - Silicon Oasis Central"])]
        elif selected_store1 == "Arakkal Gold and Diamonds(MB)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)"])]   
        elif selected_store1 == "Kanz Jewellers(MB)":
            # Filtering the combined_df DataFrame
            store1_df = combined_df[combined_df['Store Name'].isin(["Kanz Jewellers"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Kanz Jewellers"])]    
        elif selected_store1 == "None":
            store1_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            #store1_df_summary = pd.DataFrame()
            store1_df_keywords = pd.DataFrame()
        elif selected_store1 == "":
            store1_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            #store1_df_summary = pd.DataFrame()
            store1_df_keywords = pd.DataFrame()
        else:
            st.error("Reselect all the data") 
        

        # Filter the dataframe based on catchment area selection
        if selected_store2 == "Tanishq Jewellers-Al Fahidi, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Fahidi, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Fahidi, DB"] 
        elif selected_store2 == "Tanishq Jewellers-Meena Bazar, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Meena Bazar, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Meena Bazar"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Meena Bazar, DB"]
        elif selected_store2 == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD"]
        elif selected_store2 == "Tanishq Jewellers-Al Barsha, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Barsha, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Barsha, DB"]
        elif selected_store2 == "Tanishq Jewellers-Al Karama, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Karama, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Karama"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Karama, DB"]
        elif selected_store2 == "Tanishq Jewellers-Silicon Central, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Silicon Central, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Silicon Central, DB"]
        elif selected_store2 == "Mia-Al Wahda Mall, AD":
            store2_df = combined_df[combined_df['Store Name'] == "Mia-Al Wahda Mall, AD"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Mia-Al Wahda Mall, AD"]
        elif selected_store2 == "Mia-Burjuman, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Mia-Burjuman, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Mia-Burjuman, DB"]
        elif selected_store2 == "Tanishq Jewellers-Avenues Mall, OM":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Avenues Mall, OM"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Avenues Mall, OM"]
        elif selected_store2 == "Tanishq Jewellers-Festival City, QA":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Festival City, QA"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Festival City, QA"]
        elif selected_store2 == "Tanishq Jewellers-Gold Souk, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Gold Souk, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Gold Souk, DB"]
        elif selected_store2 == "Tanishq Jewellers-Lulu Hypermarket, QA":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Lulu Hypermarket, QA"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Lulu Hypermarket, QA"]
        elif selected_store2 == "Tanishq Jewellers-UW Mall Al Mankhool, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-UW Mall Al Mankhool, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-UW Mall Al Mankhool, DB"]
        elif selected_store2 == "Tanishq Jewellers-Rolla, SH":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Rolla, SH"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Rolla, SH"]            
        elif selected_store2 == "Tanishq Jewellers-Sharjah Central, SH":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Sharjah Central, SH"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Sharjah Central, SH"]
        elif selected_store2 == "Tanishq Jewellers-Taj, DB":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Taj, DB"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Taj, DB"]
        elif selected_store2 == "Joyalukkas Jewellery(AF)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi"])]
        elif selected_store2 == "Joyalukkas Jewellery - AF St(AF)":
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi st - Al Fahidi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi st - Al Fahidi"])]
        elif selected_store2 == "Malabar - AF St - Branch 1(AF)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)"])] 
        elif selected_store2 == "Malabar - SAK Building - Branch 2(AF)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)"])]
        elif selected_store2 == "Malabar Gold and Diamonds(MB)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Meena Bazar - Dubai"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Meena Bazar - Dubai"])]   
        elif selected_store2 == "Meena Jewellers(MB)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Meena Jewellers - Meena Bazar"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Meena Jewellers - Meena Bazar"])]            
        elif selected_store2 == "Joyalukkas - Dalma Plaza(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin([ "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi"])]        
        elif selected_store2 == "Joyalukkas - Shabia(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin([ "Joyalukkas Jewellery - Shabia - Abu Dhabi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Shabia - Abu Dhabi"])]        
        elif selected_store2 == "Joyalukkas - Madinat Zayed(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi"])]
        elif selected_store2 == "Malabar - Al Wahda Mall(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin([ "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi"])]        
        elif selected_store2 == "Malabar - Hamdan Street - 1 (AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street ( Branch 1)"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Hamdan Street ( Branch 1)"])]        
        elif selected_store2 == "Malabar - Hamdan Street - 2 (AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street (Branch 2)"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street (Branch 2)"])]        
        elif selected_store2 == "Malabar - Dalma Mall(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi"])]        
        elif selected_store2 == "Malabar - Lulu Hypermarket(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed"])]
        elif selected_store2 == "Malabar - Shabia Musaffah(AD)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Shabia Musaffah"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Shabia Musaffah"])]      
        elif selected_store2 == "Joyalukkas Jewellery(AB)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Barsha"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Barsha"])]        
        elif selected_store2 == "Malabar Gold and Diamonds(AB)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Barsha - Dubai"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Barsha - Dubai"])]     
        elif selected_store2 == "Joyalukkas Jewellery(AK)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Karama"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Karama"])]        
        elif selected_store2 == "Malabar Gold and Diamonds(AK)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Karama - Dubai"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Karama - Dubai"])]     
        elif selected_store2 == "Bhima(AK)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Bhima Jewellers - Al Karama"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Bhima Jewellers - Al Karama"])]        
        elif selected_store2 == "Mint(AK)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Mint Jewels - Al Karama"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Mint Jewels - Al Karama"])]        
        elif selected_store2 == "Malabar Gold and Diamonds(SC)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds - Silicon Oasis Central"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds - Silicon Oasis Central"])]
        elif selected_store2 == "Arakkal Gold and Diamonds(MB)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)"])]   
        elif selected_store2 == "Kanz Jewellers(MB)":
            # Filtering the combined_df DataFrame
            store2_df = combined_df[combined_df['Store Name'].isin(["Kanz Jewellers"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Kanz Jewellers"])]    
        elif selected_store2 == "None":
            store2_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            #store2_df_summary = pd.DataFrame()
            store2_df_keywords = pd.DataFrame()
        elif selected_store2 == "":
            store2_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            #store2_df_summary = pd.DataFrame()
            store2_df_keywords = pd.DataFrame()
        else:
            st.error("Reselect all the data")


        if multi_comparison_stores:    

            if selected_store3 == "Tanishq Jewellers-Al Fahidi, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Fahidi, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Fahidi, DB"] 
            elif selected_store3 == "Tanishq Jewellers-Meena Bazar, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Meena Bazar, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Meena Bazar"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Meena Bazar, DB"]
            elif selected_store3 == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Hamdan Bin Mohammed Street, AD"]
            elif selected_store3 == "Tanishq Jewellers-Al Barsha, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Barsha, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Barsha, DB"]
            elif selected_store3 == "Tanishq Jewellers-Al Karama, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Al Karama, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Karama"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Al Karama, DB"]
            elif selected_store3 == "Tanishq Jewellers-Silicon Central, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Silicon Central, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Silicon Central, DB"]
            elif selected_store3 == "Mia-Al Wahda Mall, AD":
                store3_df = combined_df[combined_df['Store Name'] == "Mia-Al Wahda Mall, AD"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Mia-Al Wahda Mall, AD"]
            elif selected_store3 == "Mia-Burjuman, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Mia-Burjuman, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Mia-Burjuman, DB"]
            elif selected_store3 == "Tanishq Jewellers-Avenues Mall, OM":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Avenues Mall, OM"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Avenues Mall, OM"]
            elif selected_store3 == "Tanishq Jewellers-Festival City, QA":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Festival City, QA"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Festival City, QA"]
            elif selected_store3 == "Tanishq Jewellers-Gold Souk, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Gold Souk, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Gold Souk, DB"]
            elif selected_store3 == "Tanishq Jewellers-Lulu Hypermarket, QA":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Lulu Hypermarket, QA"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Lulu Hypermarket, QA"]
            elif selected_store3 == "Tanishq Jewellers-UW Mall Al Mankhool, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-UW Mall Al Mankhool, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-UW Mall Al Mankhool, DB"]
            elif selected_store3 == "Tanishq Jewellers-Rolla, SH":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Rolla, SH"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Rolla, SH"]            
            elif selected_store3 == "Tanishq Jewellers-Sharjah Central, SH":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Sharjah Central, SH"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Sharjah Central, SH"]
            elif selected_store3 == "Tanishq Jewellers-Taj, DB":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq Jewellers-Taj, DB"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Silicon Central"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq Jewellers-Taj, DB"]
            elif selected_store3 == "Joyalukkas Jewellery(AF)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi"])]
            elif selected_store3 == "Joyalukkas Jewellery - AF St(AF)":
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi st - Al Fahidi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Fahidi st - Al Fahidi"])]
            elif selected_store3 == "Malabar - AF St - Branch 1(AF)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Fahidi Street - Bur Dubai (Branch 1)"])] 
            elif selected_store3 == "Malabar - SAK Building - Branch 2(AF)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Souq Al Kabeer Building - Bur Dubai (Branch 2)"])]        
            elif selected_store3 == "Malabar Gold and Diamonds(MB)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Meena Bazar - Dubai"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Meena Bazar - Dubai"])]   
            elif selected_store3 == "Meena Jewellers(MB)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Meena Jewellers - Meena Bazar"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Meena Jewellers - Meena Bazar"])]        

            elif selected_store3 == "Joyalukkas - Dalma Plaza(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin([ "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Joyalukkas Jewellery - Dalma Plaza - Abu Dhabi"])]        
            elif selected_store3 == "Joyalukkas - Shabia(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin([ "Joyalukkas Jewellery - Shabia - Abu Dhabi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Shabia - Abu Dhabi"])]        
            elif selected_store3 == "Joyalukkas - Madinat Zayed(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Madinat Zayed Shopping Centre - Abu Dhabi"])]
            elif selected_store3 == "Malabar - Al Wahda Mall(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin([ "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Al Wahda Mall - Abu Dhabi"])]        
            elif selected_store3 == "Malabar - Hamdan Street - 1 (AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street ( Branch 1)"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin([ "Malabar Gold and Diamonds - Hamdan Street ( Branch 1)"])]        
            elif selected_store3 == "Malabar - Hamdan Street - 2 (AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street (Branch 2)"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Hamdan Street (Branch 2)"])]        
            elif selected_store3 == "Malabar - Dalma Mall(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Dalma Mall - Abu Dhabi"])]        
            elif selected_store3 == "Malabar - Lulu Hypermarket(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Lulu Hypermarket - Madinat Zayed"])]
            elif selected_store3 == "Malabar - Shabia Musaffah(AD)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Shabia Musaffah"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Shabia Musaffah"])]        
            elif selected_store3 == "Joyalukkas Jewellery(AB)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Barsha"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Barsha"])]        
            elif selected_store3 == "Malabar Gold and Diamonds(AB)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Barsha - Dubai"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Barsha - Dubai"])]     
            elif selected_store3 == "Joyalukkas Jewellery(AK)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery - Al Karama"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery - Al Karama"])]        
            elif selected_store3 == "Malabar Gold and Diamonds(AK)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold and Diamonds - Al Karama - Dubai"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold and Diamonds - Al Karama - Dubai"])]     
            elif selected_store3 == "Bhima(AK)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Bhima Jewellers - Al Karama"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Bhima Jewellers - Al Karama"])]        
            elif selected_store3 == "Mint(AK)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Mint Jewels - Al Karama"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Mint Jewels - Al Karama"])]        
            elif selected_store3 == "Malabar Gold and Diamonds(SC)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds - Silicon Oasis Central"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds - Silicon Oasis Central"])]
            elif selected_store3 == "Arakkal Gold and Diamonds(MB)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Arakkal Gold and Diamonds LLC - Meena Bazar - Bur Dubai (Branch 3)"])]   
            elif selected_store3 == "Kanz Jewellers(MB)":
                # Filtering the combined_df DataFrame
                store3_df = combined_df[combined_df['Store Name'].isin(["Kanz Jewellers"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Kanz Jewellers"])]   
            elif selected_store3 == "None":
                store3_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
                #store3_df_summary = pd.DataFrame()
                store3_df_keywords = pd.DataFrame()
            else:
                store3_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
                #store3_df_summary = pd.DataFrame()
                store3_df_keywords = pd.DataFrame()
        #st.success("Done!")


elif selected_country == "USA":
    if submit_button_stores:
        #Reading data
        combined_df = pd.read_parquet("final_sentiment_mapped/combined_df_final_S.parquet", engine = 'pyarrow')
        #combined_df_summary = pd.read_excel('combined_summary.xlsx')
        combined_df_keywords =  pd.read_parquet("recent_keywords_filtered/combined_keywords.parquet", engine='pyarrow')

#for Country Level Summary
        country_level_data = combined_df[combined_df['Country'] == "USA"]
    
#for Catchment Level Summary    
        store_name = mapping_dict[selected_store1]
        selected_store1_group = combined_df[combined_df['Store Name'] == store_name]['Catchment'].iloc[0]
        #st.write(selected_store1_group)
        catchment_level_stores_df = combined_df[combined_df['Catchment'] == selected_store1_group]
        #st.dataframe(catchment_level_stores_df)
        group_store_list = catchment_level_stores_df['Grouped Store Name'].unique().tolist()
        #st.write(group_store_list)
        #Initialize an empty dictionary to hold the dataframes
        group_level_dataframes_dict = {}
        for group_store_name in group_store_list:
            #Create the dataframe name by appending 'df' to the group_store_name
            dataframe_name = f"{group_store_name}_df"
            #Filter the catchment_level_stores_df to get only the rows with the current group_store_name
            filtered_df = catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == group_store_name]
            #Store the filtered dataframe in the dictionary with the new name as key
            group_level_dataframes_dict[dataframe_name] = filtered_df
            

        # Filter the dataframe based on Store1 selection
        if selected_store1 == "Tanishq-Chicago, IL":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-Chicago, IL"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Chicago, IL"] 
        elif selected_store1 == "Tanishq-Frisco, TX":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-Frisco, TX"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Meena Bazar"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Frisco, TX"]
        elif selected_store1 == "Tanishq-Houston, TX":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-Houston, TX"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Houston, TX"]
        elif selected_store1 == "Tanishq-New Jersey, NJ":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-New Jersey, NJ"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-New Jersey, NJ"]
        elif selected_store1 == "Tanishq-Atlanta, GA":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-Atlanta, GA"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Atlanta, GA"]
        elif selected_store1 == "Tanishq-Redmond Seattle, WA":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-Redmond Seattle, WA"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Redmond Seattle, WA"]
        elif selected_store1 == "Tanishq-Santa Clara, CA":
            store1_df = combined_df[combined_df['Store Name'] == "Tanishq-Santa Clara, CA"]
            #store1_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Santa Clara, CA"]                                  
        elif selected_store1 == "Jared-Aurora, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Aurora, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Aurora, IL"])]
        elif selected_store1 == "Jared-Lombard, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Lombard, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Lombard, IL"])]
        elif selected_store1 == "Jared-Schaumburg, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Schaumburg, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Schaumburg, IL"])]
        elif selected_store1 == "Jared-Bolingbrook, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Bolingbrook, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Bolingbrook, IL"])]
        elif selected_store1 == "Jared-Algonquin, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Algonquin, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Algonquin, IL"])]
        elif selected_store1 == "Jared-Orland Park, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Orland Park, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Orland Park, IL"])]
        elif selected_store1 == "Jared-Vernon Hills, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Jared-Vernon Hills, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Vernon Hills, IL"])]
        elif selected_store1 == "Joyalukkas Jewellery-Chicago, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Chicago, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Chicago, IL"])]
        elif selected_store1 == "Joyalukkas Jewellery-Houston, TX":
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Houston, TX"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Houston, TX"])]
        elif selected_store1 == "Joyalukkas Jewellery-Frisco, TX":
            store1_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Frisco, TX"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Frisco, TX"])]
        elif selected_store1 == "Malabar Gold & Diamonds-Chicago, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Chicago, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Chicago, IL"])]
        elif selected_store1 == "Malabar Gold & Diamonds-Naperville, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Naperville, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Naperville, IL"])]
        elif selected_store1 == "Malabar Gold & Diamonds-Iselin, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Iselin, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Iselin, NJ"])]
        elif selected_store1 == "Malabar Gold & Diamonds-Frisco, TX":
            store1_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Frisco, TX"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Frisco, TX"])]
        elif selected_store1 == "Malani Jewellers-Richardson, TX":
            store1_df = combined_df[combined_df['Store Name'].isin(["Malani Jewellers-Richardson, TX"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malani Jewellers-Richardson, TX"])]
        elif selected_store1 == "May Jewelers-Vienna, VA":
            store1_df = combined_df[combined_df['Store Name'].isin(["May Jewelers-Vienna, VA"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["May Jewelers-Vienna, VA"])]
        elif selected_store1 == "Sona Jewelers-Iselin, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Sona Jewelers-Iselin, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Sona Jewelers-Iselin, NJ"])]
        elif selected_store1 == "Tiffany & Co-Northbrook, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Northbrook, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Northbrook, IL"])]
        elif selected_store1 == "Tiffany & Co-Skokie, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Skokie, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Skokie, IL"])]
        elif selected_store1 == "Tiffany & Co-Chicago, IL":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Chicago, IL"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Chicago, IL"])]
        elif selected_store1 == "Tiffany & Co-Paramus, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Paramus, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Paramus, NJ"])]
        elif selected_store1 == "Tiffany & Co-Hackensack, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Hackensack, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Hackensack, NJ"])]
        elif selected_store1 == "Tiffany & Co-East Rutherford, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-East Rutherford, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-East Rutherford, NJ"])]
        elif selected_store1 == "Tiffany & Co-Red Bank, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Red Bank, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Red Bank, NJ"])]
        elif selected_store1 == "Tiffany & Co-Short Hills, NJ":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Short Hills, NJ"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Short Hills, NJ"])]
        elif selected_store1 == "Tiffany & Co-Vienna, VA":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Vienna, VA"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Vienna, VA"])]
        elif selected_store1 == "Tiffany & Co-Richmond, VA":
            store1_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Richmond, VA"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Richmond, VA"])]
        elif selected_store1 == "VBJ Jewellers-Frisco, TX":
            store1_df = combined_df[combined_df['Store Name'].isin(["VBJ Jewellers-Frisco, TX"])]
            store1_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["VBJ Jewellers-Frisco, TX"])]
        elif selected_store1 == "None":
            store1_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            store1_df_keywords = pd.DataFrame()
        elif selected_store1 == "":
            store1_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            store1_df_keywords = pd.DataFrame()
        else:
            st.error("Reselect all the data")


        # Filter the dataframe based on Store1 selection
        if selected_store2 == "Tanishq-Chicago, IL":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-Chicago, IL"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Chicago, IL"] 
        elif selected_store2 == "Tanishq-Frisco, TX":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-Frisco, TX"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Meena Bazar"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Frisco, TX"]
        elif selected_store2 == "Tanishq-Houston, TX":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-Houston, TX"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Houston, TX"]
        elif selected_store2 == "Tanishq-New Jersey, NJ":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-New Jersey, NJ"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-New Jersey, NJ"]
        elif selected_store2 == "Tanishq-Atlanta, GA":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-Atlanta, GA"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Atlanta, GA"]
        elif selected_store2 == "Tanishq-Redmond Seattle, WA":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-Redmond Seattle, WA"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Redmond Seattle, WA"]
        elif selected_store2 == "Tanishq-Santa Clara, CA":
            store2_df = combined_df[combined_df['Store Name'] == "Tanishq-Santa Clara, CA"]
            #store2_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Santa Clara, CA"]                                  
        elif selected_store2 == "Jared-Aurora, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Aurora, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Aurora, IL"])]
        elif selected_store2 == "Jared-Lombard, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Lombard, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Lombard, IL"])]
        elif selected_store2 == "Jared-Schaumburg, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Schaumburg, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Schaumburg, IL"])]
        elif selected_store2 == "Jared-Bolingbrook, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Bolingbrook, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Bolingbrook, IL"])]
        elif selected_store2 == "Jared-Algonquin, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Algonquin, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Algonquin, IL"])]
        elif selected_store2 == "Jared-Orland Park, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Orland Park, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Orland Park, IL"])]
        elif selected_store2 == "Jared-Vernon Hills, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Jared-Vernon Hills, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Vernon Hills, IL"])]
        elif selected_store2 == "Joyalukkas Jewellery-Chicago, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Chicago, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Chicago, IL"])]
        elif selected_store2 == "Joyalukkas Jewellery-Houston, TX":
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Houston, TX"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Houston, TX"])]
        elif selected_store2 == "Joyalukkas Jewellery-Frisco, TX":
            store2_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Frisco, TX"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Frisco, TX"])]
        elif selected_store2 == "Malabar Gold & Diamonds-Chicago, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Chicago, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Chicago, IL"])]
        elif selected_store2 == "Malabar Gold & Diamonds-Naperville, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Naperville, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Naperville, IL"])]
        elif selected_store2 == "Malabar Gold & Diamonds-Iselin, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Iselin, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Iselin, NJ"])]
        elif selected_store2 == "Malabar Gold & Diamonds-Frisco, TX":
            store2_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Frisco, TX"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Frisco, TX"])]
        elif selected_store2 == "Malani Jewellers-Richardson, TX":
            store2_df = combined_df[combined_df['Store Name'].isin(["Malani Jewellers-Richardson, TX"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malani Jewellers-Richardson, TX"])]
        elif selected_store2 == "May Jewelers-Vienna, VA":
            store2_df = combined_df[combined_df['Store Name'].isin(["May Jewelers-Vienna, VA"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["May Jewelers-Vienna, VA"])]
        elif selected_store2 == "Sona Jewelers-Iselin, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Sona Jewelers-Iselin, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Sona Jewelers-Iselin, NJ"])]
        elif selected_store2 == "Tiffany & Co-Northbrook, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Northbrook, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Northbrook, IL"])]
        elif selected_store2 == "Tiffany & Co-Skokie, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Skokie, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Skokie, IL"])]
        elif selected_store2 == "Tiffany & Co-Chicago, IL":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Chicago, IL"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Chicago, IL"])]
        elif selected_store2 == "Tiffany & Co-Paramus, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Paramus, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Paramus, NJ"])]
        elif selected_store2 == "Tiffany & Co-Hackensack, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Hackensack, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Hackensack, NJ"])]
        elif selected_store2 == "Tiffany & Co-East Rutherford, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-East Rutherford, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-East Rutherford, NJ"])]
        elif selected_store2 == "Tiffany & Co-Red Bank, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Red Bank, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Red Bank, NJ"])]
        elif selected_store2 == "Tiffany & Co-Short Hills, NJ":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Short Hills, NJ"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Short Hills, NJ"])]
        elif selected_store2 == "Tiffany & Co-Vienna, VA":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Vienna, VA"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Vienna, VA"])]
        elif selected_store2 == "Tiffany & Co-Richmond, VA":
            store2_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Richmond, VA"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Richmond, VA"])]
        elif selected_store2 == "VBJ Jewellers-Frisco, TX":
            store2_df = combined_df[combined_df['Store Name'].isin(["VBJ Jewellers-Frisco, TX"])]
            store2_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["VBJ Jewellers-Frisco, TX"])]
        elif selected_store2 == "None":
            store2_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            store2_df_keywords = pd.DataFrame()
        elif selected_store2 == "":
            store2_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
            store2_df_keywords = pd.DataFrame()
        else:
            st.error("Reselect all the data")

        
        if multi_comparison_stores:    
            # Filter the dataframe based on Store1 selection
            if selected_store3 == "Tanishq-Chicago, IL":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-Chicago, IL"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Fahidi , Bur Dubai"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Chicago, IL"] 
            elif selected_store3 == "Tanishq-Frisco, TX":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-Frisco, TX"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Meena Bazar"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Frisco, TX"]
            elif selected_store3 == "Tanishq-Houston, TX":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-Houston, TX"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Hamdan Bin Mohammed Street"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Houston, TX"]
            elif selected_store3 == "Tanishq-New Jersey, NJ":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-New Jersey, NJ"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-New Jersey, NJ"]
            elif selected_store3 == "Tanishq-Atlanta, GA":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-Atlanta, GA"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Atlanta, GA"]
            elif selected_store3 == "Tanishq-Redmond Seattle, WA":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-Redmond Seattle, WA"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Redmond Seattle, WA"]
            elif selected_store3 == "Tanishq-Santa Clara, CA":
                store3_df = combined_df[combined_df['Store Name'] == "Tanishq-Santa Clara, CA"]
                #store3_df_summary = combined_df_summary[combined_df_summary['Store Name'] == "Tanishq Jewellers - Al Barsha"]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'] == "Tanishq-Santa Clara, CA"]                                  
            elif selected_store3 == "Jared-Aurora, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Aurora, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Aurora, IL"])]
            elif selected_store3 == "Jared-Lombard, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Lombard, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Lombard, IL"])]
            elif selected_store3 == "Jared-Schaumburg, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Schaumburg, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Schaumburg, IL"])]
            elif selected_store3 == "Jared-Bolingbrook, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Bolingbrook, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Bolingbrook, IL"])]
            elif selected_store3 == "Jared-Algonquin, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Algonquin, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Algonquin, IL"])]
            elif selected_store3 == "Jared-Orland Park, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Orland Park, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Orland Park, IL"])]
            elif selected_store3 == "Jared-Vernon Hills, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Jared-Vernon Hills, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Jared-Vernon Hills, IL"])]
            elif selected_store3 == "Joyalukkas Jewellery-Chicago, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Chicago, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Chicago, IL"])]
            elif selected_store3 == "Joyalukkas Jewellery-Houston, TX":
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Houston, TX"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Houston, TX"])]
            elif selected_store3 == "Joyalukkas Jewellery-Frisco, TX":
                store3_df = combined_df[combined_df['Store Name'].isin(["Joyalukkas Jewellery-Frisco, TX"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Joyalukkas Jewellery-Frisco, TX"])]
            elif selected_store3 == "Malabar Gold & Diamonds-Chicago, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Chicago, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Chicago, IL"])]
            elif selected_store3 == "Malabar Gold & Diamonds-Naperville, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Naperville, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Naperville, IL"])]
            elif selected_store3 == "Malabar Gold & Diamonds-Iselin, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Iselin, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Iselin, NJ"])]
            elif selected_store3 == "Malabar Gold & Diamonds-Frisco, TX":
                store3_df = combined_df[combined_df['Store Name'].isin(["Malabar Gold & Diamonds-Frisco, TX"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malabar Gold & Diamonds-Frisco, TX"])]
            elif selected_store3 == "Malani Jewellers-Richardson, TX":
                store3_df = combined_df[combined_df['Store Name'].isin(["Malani Jewellers-Richardson, TX"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Malani Jewellers-Richardson, TX"])]
            elif selected_store3 == "May Jewelers-Vienna, VA":
                store3_df = combined_df[combined_df['Store Name'].isin(["May Jewelers-Vienna, VA"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["May Jewelers-Vienna, VA"])]
            elif selected_store3 == "Sona Jewelers-Iselin, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Sona Jewelers-Iselin, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Sona Jewelers-Iselin, NJ"])]
            elif selected_store3 == "Tiffany & Co-Northbrook, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Northbrook, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Northbrook, IL"])]
            elif selected_store3 == "Tiffany & Co-Skokie, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Skokie, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Skokie, IL"])]
            elif selected_store3 == "Tiffany & Co-Chicago, IL":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Chicago, IL"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Chicago, IL"])]
            elif selected_store3 == "Tiffany & Co-Paramus, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Paramus, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Paramus, NJ"])]
            elif selected_store3 == "Tiffany & Co-Hackensack, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Hackensack, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Hackensack, NJ"])]
            elif selected_store3 == "Tiffany & Co-East Rutherford, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-East Rutherford, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-East Rutherford, NJ"])]
            elif selected_store3 == "Tiffany & Co-Red Bank, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Red Bank, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Red Bank, NJ"])]
            elif selected_store3 == "Tiffany & Co-Short Hills, NJ":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Short Hills, NJ"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Short Hills, NJ"])]
            elif selected_store3 == "Tiffany & Co-Vienna, VA":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Vienna, VA"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Vienna, VA"])]
            elif selected_store3 == "Tiffany & Co-Richmond, VA":
                store3_df = combined_df[combined_df['Store Name'].isin(["Tiffany & Co-Richmond, VA"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["Tiffany & Co-Richmond, VA"])]
            elif selected_store3 == "VBJ Jewellers-Frisco, TX":
                store3_df = combined_df[combined_df['Store Name'].isin(["VBJ Jewellers-Frisco, TX"])]
                store3_df_keywords = combined_df_keywords[combined_df_keywords['Store Name'].isin(["VBJ Jewellers-Frisco, TX"])]
            elif selected_store3 == "None":
                store3_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
                store3_df_keywords = pd.DataFrame()
            elif selected_store3 == "":
                store3_df = pd.DataFrame()  # Empty DataFrame for unhandled catchment areas
                store3_df_keywords = pd.DataFrame()
            else:
                st.error("Reselect all the data")
        #st.success("Done!")
                                                       
# === Front end working code ===
if submit_button_stores:
    tab1, tab2, tab3 = st.tabs(["Brand Summary - Country Level", "Brand Summary - Catchment Level", "Selection Summary - Store Level"])
    with tab1:
        brand_list = country_level_data['Grouped Store Name'].unique().tolist()
        number_of_brands = len(brand_list)
        columns = st.columns(number_of_brands)
        # Now you can use these columns
        for brand_name, column in zip(brand_list, columns):
            with column:
                st.subheader(f":orange[{brand_name}]")#,divider = 'grey')
                number_of_stores = country_level_data[country_level_data['Grouped Store Name'] == brand_name]['Store Name'].nunique()
                st.write(f"***Total Stores:*** **:blue[{number_of_stores}]**")
                brand_number_of_ratings_df = country_level_data[country_level_data['Grouped Store Name'] == brand_name][['Store Name','Total Reviews']]
                #check
                #st.dataframe(brand_number_of_ratings_df)
                
                #brand_number_of_ratings_df.drop_duplicates(inplace=True)
                #brand_number_of_ratings = brand_number_of_ratings_df['Total Reviews'].sum()
                brand_number_of_ratings = len(brand_number_of_ratings_df)
                st.write(f"***Total Ratings(Apr'24 - May'25):***")
                st.write(f"**:blue[{brand_number_of_ratings}]**")
                brand_average_rating = round(country_level_data[country_level_data['Grouped Store Name'] == brand_name]['Avg Rating'].mean(),1)
                st.write(f"***Average Rating:***")
                st.write(f"**:blue[{brand_average_rating}]**")

                brand_rating_counts = country_level_data[country_level_data['Grouped Store Name'] == brand_name]['review_rating'].value_counts()
                brand_normalized_percentages = round(country_level_data[country_level_data['Grouped Store Name'] == brand_name]['review_rating'].value_counts(normalize=True) * 100,0)
                brand_normalized_percentages = brand_normalized_percentages.apply(lambda x: '<1' if x < 1 else x)
                brand_rating_data = pd.DataFrame({'Rating': brand_rating_counts.index,
                                                        'Count': brand_rating_counts.values,
                                                        '%':brand_normalized_percentages})

                #Sort the DataFrame in descending order of 'Rating'
                brand_rating_data = brand_rating_data.sort_values('Rating', ascending=False)
                st.write(f"***Rating Spread:***")
                st.dataframe(brand_rating_data[['Rating','%']],hide_index=True)
    with tab2:
        st.subheader(f":green[{selected_store1_group}] ")#, divider='grey')
        number_of_brands_catchment = len(group_store_list)
        columns = st.columns(number_of_brands_catchment)
        # Now you can use these columns
        for brand_name, column in zip(group_store_list, columns):
            with column:
                st.subheader(f":orange[{brand_name}]")#,divider = 'grey')
                number_of_stores_catchment = catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == brand_name]['Store Name'].nunique()
                st.write(f"***Total Stores:*** **:blue[{number_of_stores_catchment}]**")
                brand_number_of_ratings_catchment = catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == brand_name][['Store Name','Grouped Store Name','Total Reviews']]
                #st.dataframe(brand_number_of_ratings_catchment)
                #brand_number_of_ratings_catchment.drop_duplicates(inplace=True)
                #brand_number_of_ratings_catchment = brand_number_of_ratings_catchment['Total Reviews'].sum()
                brand_number_of_ratings_catchment = len(brand_number_of_ratings_catchment)
#                    brand_number_of_ratings_catchment = catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == brand_name]['review_rating'])
                st.write(f"***Total Ratings(Apr'24 - May'25):***")
                st.write(f"**:blue[{brand_number_of_ratings_catchment}]**")
                brand_average_rating_catchment = round(catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == brand_name]['Avg Rating'].mean(),1)
                st.write(f"***Average Rating:***")
                st.write(f"**:blue[{brand_average_rating_catchment}]**")

                brand_rating_counts_catchment = catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == brand_name]['review_rating'].value_counts()
                brand_normalized_percentages_catchment = round(catchment_level_stores_df[catchment_level_stores_df['Grouped Store Name'] == brand_name]['review_rating'].value_counts(normalize=True) * 100,0)
                brand_normalized_percentages_catchment = brand_normalized_percentages_catchment.apply(lambda x: '<1' if x < 1 else x)
                brand_rating_data_catchment = pd.DataFrame({'Rating': brand_rating_counts_catchment.index,
                                                        'Count': brand_rating_counts_catchment.values,
                                                        '%':brand_normalized_percentages_catchment})

                #Sort the DataFrame in descending order of 'Rating'
                brand_rating_data_catchment = brand_rating_data_catchment.sort_values('Rating', ascending=False)
                st.write(f"***Rating Spread:***")
                st.dataframe(brand_rating_data_catchment[['Rating','%']],hide_index=True)
    with tab3: 
        if multi_comparison_stores:
            col3,col4,col5 = st.columns(3)
            with col3:
        ###Display name of the store
                st.markdown(f"<h1 class='sticky-left-header'>{selected_store1}</h1>", unsafe_allow_html=True)
        ###==Overview Expander==
                with st.expander(f"Overview🌐"):
        ###Display Total ratings
                    #total_number_of_ratings_catchment = store1_df['Total Reviews'].iloc[0]
                    total_number_of_ratings_catchment = len(store1_df)                       
                    st.markdown(f"<h1 class='left-content'>Total Ratings ::</h1>", unsafe_allow_html=True)
                    st.markdown(total_number_of_ratings_catchment)
        ###Display Average Rating
                    avg_rating_catchment = round(store1_df['Avg Rating'].mean(),1)
                    st.markdown(f"<h1 class='left-content'>Average Rating ::</h1>", unsafe_allow_html=True)
                    st.markdown(f"{avg_rating_catchment} Stars")
        ###Display % spread of reviews
                    st.markdown(f"<h1 class='left-content'>Rating Spread ::</h1>", unsafe_allow_html=True)
                    #Count the occurrences of each rating
                    rating_counts_catchment = store1_df['review_rating'].value_counts()
                    #Create a DataFrame
                    normalized_percentages = round(store1_df['review_rating'].value_counts(normalize=True) * 100,0)
                    normalized_percentages = normalized_percentages.apply(lambda x: '<1' if x < 1 else x)
                    rating_data_catchment = pd.DataFrame({'Rating': rating_counts_catchment.index,
                                                            'Count': rating_counts_catchment.values,
                                                            '%':normalized_percentages})

                    #Sort the DataFrame in descending order of 'Rating'
                    rating_data_catchment = rating_data_catchment.sort_values('Rating', ascending=False)
                    st.dataframe(rating_data_catchment[['Rating','%']],hide_index=True)

    ###==Top Spoken Topics 📢 Expander==            
                with st.expander("Top Spoken Topics 📢"):
        ###Display Total ratings with text
                    non_null_count_catchment = store1_df['review_text'].count()
        ###Top Spoken Topics
                    #Define the topics
                    topics = ["Customer Confidence", "Store Experience", "Store Staff", "Product Design","Product Variety", 
                                "Discount", "Making Charge", "Price", "Product Quality", "Jewellery Exchange"]
                    #Take only reviews with text
                    store1_df_non_null = store1_df.dropna(subset=['review_text'])
                    #Initialize a dictionary to hold the count of discussed topics
                    discussed_topics_count_catchment = {}
                    #Count the number of non-zero entries for each topic in the DataFrame
                    for topic in topics:
                        # A topic is considered discussed if its score is 1 or -1
                        discussed_topics_count_catchment[topic] = store1_df_non_null[topic][store1_df_non_null[topic] != 0].count()
                    # Convert the dictionary to a DataFrame for visualization
                    topics_df_catchment = pd.DataFrame(list(discussed_topics_count_catchment.items()), columns=['Topic', 'Count'])
                    # Calculate the percentage of total reviews for each topic
                    topics_df_catchment['Percentage'] = (topics_df_catchment['Count'] / non_null_count_catchment) * 100
                    # Sort the DataFrame based on the count of discussed topics in descending order
                    topics_df_catchment = topics_df_catchment.sort_values('Count', ascending=False)
                    # Create the horizontal bar chart using Plotly Express
                    fig_catchment = px.bar(
                                            topics_df_catchment, 
                                            x='Topic', 
                                            y='Count', 
                                            orientation='v',
                                            text='Percentage'
                                        )
                    # Update the layout for a cleaner look
                    fig_catchment.update_layout(
                                                yaxis={'categoryorder':'total ascending'},
                                                xaxis_title="Topics",
                                                yaxis_title="Number of Reviews",
                                                title="Top Spoken Topics",
                                                showlegend=False,
                                                autosize=True,
                                                annotations=[dict(xref='paper', yref='paper',x=0.5, y=1.05,
                                                                    xanchor='center', yanchor='top',
                                                                    text=f"Total Spoken Reviews: {len(store1_df_non_null)}",
                                                                    font=dict(size=14),showarrow=False)]
                                            )
                    # Update the bar element to display the percentage text
                    fig_catchment.update_traces(
                                                texttemplate='%{text:.1f}%', textposition='outside',
                                                hovertemplate = "<b>Topic</b>: %{x}<br>" + 
                                                                "<b>Count</b>: %{y}<br>" + 
                                                                "<b>Percentage</b>: %{text:.1f}%<extra></extra>"
                                            )
                    # Display the bar chart in Streamlit
                    st.plotly_chart(fig_catchment,use_container_width=True)

    ###==Sentiment Analytics Expander==            
                with st.expander("Topic wise sentiments😃😢"):                    
                    ###Sentiment in each topic
                    # Initialize a list to hold the count of positive and negative sentiments for each topic
                    sentiment_counts_catchment = []
                    # Count the number of positive and negative sentiments for each topic
                    for topic in topics:
                        positive_count_catchment = (store1_df[topic] == 1).sum()
                        negative_count_catchment = (store1_df[topic] == -1).sum()
                        total_count_catchment = positive_count_catchment + negative_count_catchment
                        sentiment_counts_catchment.append({
                                                            'Topic': topic, 
                                                            'Positive': positive_count_catchment, 
                                                            'Negative': negative_count_catchment,
                                                            'Total': total_count_catchment
                                                        })
                    # Create a DataFrame for visualization
                    sentiment_df_catchment = pd.DataFrame(sentiment_counts_catchment)
                    # Sort the DataFrame based on the total count of reviews in descending order
                    sentiment_df_catchment.sort_values('Total', ascending=False, inplace=True)
                    # Melt the DataFrame to long format for Plotly
                    sentiment_long_df_catchment = sentiment_df_catchment.melt(id_vars=['Topic', 'Total'], value_vars=['Positive', 'Negative'],
                                                                                var_name='Sentiment', value_name='Count')
                    # Calculate the percentage for each sentiment
                    sentiment_long_df_catchment['Percentage'] = (sentiment_long_df_catchment['Count'] / sentiment_long_df_catchment['Total'] * 100).round(1)
                    # Create the horizontal (transposed) bar chart using Plotly Express
                    fig_sentiments_catchment = px.bar(
                                                        sentiment_long_df_catchment,
                                                        y='Topic',
                                                        x='Count',
                                                        color='Sentiment',
                                                        color_discrete_map={'Positive': '#39CEFF', 'Negative': '#FF735D'},  # Custom colors
                                                        barmode='group',
                                                        orientation='h',  # This creates a horizontal bar chart
                                                        category_orders={"Topic": sentiment_df_catchment['Topic'].tolist()},
                                                        text='Percentage'
                                                        )
                    # Update the layout for a cleaner look
                    fig_sentiments_catchment.update_layout(
                                                            yaxis_title="Topics",
                                                            xaxis_title="Count of Sentiments",
                                                            title="Overview",
                                                            showlegend=True,
                                                            legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="right", x=0.9),
                                                        )
                    # Format the text on the bars to show the percentage with one decimal & Customizing hovertemplate to show one decimal place for the percentage
                    fig_sentiments_catchment.update_traces(
                                                            texttemplate='%{text}%', textposition='outside',
                                                            hovertemplate="<b>Topic</b>: %{y}<br><b>Count</b>: %{x}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{text}%",customdata=sentiment_long_df_catchment[['Total']].values
                                                )
                    # Display the horizontal bar chart in Streamlit
                    st.plotly_chart(fig_sentiments_catchment, use_container_width=True)

    ###==Pain Points Expander==
                with st.expander("Analyzing Pain Points ❌"):                                      
                    # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                    negative_reviews_df_catchment = sentiment_df_catchment[['Topic', 'Negative', 'Total']]
                    # Calculate the percentage of negative reviews
                    negative_reviews_df_catchment['Percentage'] = round(negative_reviews_df_catchment['Negative'] / negative_reviews_df_catchment['Total'] * 100,1)
                    # Sort the DataFrame based on the count of negative reviews in descending order
                    negative_reviews_df_sorted_catchment = negative_reviews_df_catchment.sort_values(['Percentage', 'Total'], ascending=[True,False])

                    # Create the bar chart using Plotly Express
                    fig_negative_reviews = px.bar(
                                                    negative_reviews_df_sorted_catchment,
                                                    y='Topic',
                                                    x='Percentage',
                                                    orientation='h',  # This creates a horizontal bar chart
                                                    color_discrete_sequence=['#FF735D'],
                                                    )
                    # Update the layout for a cleaner look
                    fig_negative_reviews.update_layout(
                                                        #yaxis_title="Topics",
                                                        xaxis_title="% of Negative Reviews",
                                                        title="Pain Points Spread across Topics",
                                                        showlegend=False,
                                                        )
                    # Format the hovertemplate to show the desired data
                    fig_negative_reviews.update_traces(
                                                        texttemplate='%{x}%',textposition='outside',
                                                        hovertemplate="<b>Topic</b>: %{y}<br><b>Negative Count</b>: %{customdata[1]}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{x}%",
                                                        customdata=negative_reviews_df_sorted_catchment[['Total', 'Negative']].values
                                                        )
                    # Display the bar chart in Streamlit
                    #st.plotly_chart(fig_negative_reviews, use_container_width=True)
                    sentiment_df_catchment['Negative Percentage'] = sentiment_df_catchment['Negative'] / sentiment_df_catchment['Total'] * 100
                    Negative_sorted_catchment = sentiment_df_catchment.sort_values(['Negative Percentage', 'Total'], 
                                                                                    ascending=[False, False]).reset_index(drop=True)
            
                    #top_5_Negative_topics_catchment = Negative_sorted_catchment.head(5)['Topic'] 
                    top_5_Negative_topics_catchment = Negative_sorted_catchment['Topic']
                    st.markdown("\n")
                    st.markdown("**Phrases**")
                    # st.title("phrases")

                    #for topic in top_5_Negative_topics_catchment:  #For top 5 negatives 
                    for topic in top_5_Negative_topics_catchment:
                        # Get the row from the dataframe for the current topic
                        row_catchment = sentiment_df_catchment[sentiment_df_catchment['Topic'] == topic]
                        # st.dataframe(row_catchment)
                        # st.write("Shape of row_catchment:", row_catchment.shape)
                                                
                        # Extract the Negative and total counts for the topic
                        Negative_count_catchment = row_catchment['Negative'].values[0]
                        total_count_catchment = row_catchment['Total'].values[0]
                        # Filter the rows for Negative type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                        Negative_phrases_list_catchment = store1_df_keywords[(store1_df_keywords['Sentiment'] == 'negative') & (store1_df_keywords['Type'] == 'phrases')][topic].dropna().values
                        #st.dataframe(store1_df_keywords)

                        # Display the topic header
                        st.markdown(f"<h1 class='left-content-2'>{topic}: {Negative_count_catchment} out of {total_count_catchment} ({round((Negative_count_catchment/ total_count_catchment)*100,1)}%)</h1>", unsafe_allow_html=True)
                        # Container to hold the keyword boxes
                        phrase_boxes = ""

                        if Negative_phrases_list_catchment.size > 0:
                        # Now, display each keyword in a separate styled box
                            phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                            phrase_counter = 0
                            for phrase_line in Negative_phrases_list_catchment:    
                                # Split the keyword phrase by comma and strip spaces
                                phrases = phrase_line.split(',')
                                for phrase in phrases:
                                    # Remove the numbers, colons and trim whitespace
                                    phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                    if phrase_text == "No relevant negative phrases":
                                        phrase_boxes += f"<span class='keyword-box-green'>None</span>"
                                        break
                                    elif phrase_text:  # Only display if there's a keyword
                                        # Append each keyword to the container
                                        phrase_boxes += f"<span class='keyword-box-red'>{phrase_text}</span>"
                                        phrase_counter += 1
                                        # Limit the display to the first 5 keywords
                                        if phrase_counter >= 5:
                                            break
                                if phrase_counter >= 5:
                                    break
                            phrase_boxes += "</div>"
                        else:
                            phrase_boxes += f"<span class='keyword-box-green'>None</span>"  

                        # Display the keyword boxes
                        st.markdown(phrase_boxes, unsafe_allow_html=True)                   

    ###==Delight Factors Expander==         
                with st.expander("Delight Factors🌟"):
                    sentiment_df_catchment['Positive Percentage'] = sentiment_df_catchment['Positive'] / sentiment_df_catchment['Total'] * 100
                    positive_sorted_catchment = sentiment_df_catchment.sort_values(['Positive Percentage', 'Total'], 
                                                                                    ascending=[False, False]).reset_index(drop=True)
                    #top_5_positive_topics_catchment = positive_sorted_catchment.head(5)['Topic']    
                    top_5_positive_topics_catchment = positive_sorted_catchment['Topic']
                    st.markdown("\n")
                    st.markdown("**Phrases**")
                    for topic in top_5_positive_topics_catchment:
                        # Get the row from the dataframe for the current topic
                        row_catchment = sentiment_df_catchment[sentiment_df_catchment['Topic'] == topic]
                        # Extract the positive and total counts for the topic
                        positive_count_catchment = row_catchment['Positive'].values[0]
                        total_count_catchment = row_catchment['Total'].values[0]
                        # Filter the rows for Positive type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                        positive_phrases_list_catchment = store1_df_keywords[(store1_df_keywords['Sentiment'] == 'Positive') & (store1_df_keywords['Type'] == 'phrases')][topic].dropna().values

                        # Display the topic header
                        st.markdown(f"<h1 class='left-content-2'>{topic}: {positive_count_catchment} out of {total_count_catchment} ({round((positive_count_catchment/ total_count_catchment)*100,1)}%)</h1>", unsafe_allow_html=True)
                        # Container to hold the keyword boxes
                        phrase_boxes = ""

                        if positive_phrases_list_catchment.size > 0:
                        # Now, display each keyword in a separate styled box
                            phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                            phrase_counter = 0
                            for phrase_line in positive_phrases_list_catchment:    
                                # Split the keyword phrase by comma and strip spaces
                                phrases = phrase_line.split(',')
                                for phrase in phrases:
                                    # Remove the numbers, colons and trim whitespace
                                    phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                    if phrase_text == "No relevant positive phrases":
                                        phrase_boxes += f"<span class='keyword-box-red'>None</span>"
                                        if phrase_counter >= 5:
                                            break
                                    if phrase_text:  # Only display if there's a keyword
                                        # Append each keyword to the container
                                        phrase_boxes += f"<span class='keyword-box-green'>{phrase_text}</span>"
                                        phrase_counter += 1
                                        # Limit the display to the first 5 keywords
                                        if phrase_counter >= 5:
                                            break
                                if phrase_counter >= 5:
                                    break
                            phrase_boxes += "</div>"
                        else:
                            phrase_boxes += f"<span class='keyword-box-red'>None</span>"  

                        # Display the keyword boxes
                        st.markdown(phrase_boxes, unsafe_allow_html=True)                   
            with col4:
                if selected_store2 == "None":
                    pass
                else:
            ###Display name of the store
                    #st.markdown(f"<h1 class='left-header'>{selected_competitor_1}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h1 class='sticky-left-header'>{selected_store2}</h1>", unsafe_allow_html=True)
        ###==Overview Expander==
                    with st.expander("Overview🌐"):
            ###Display Total ratings
                        #total_number_of_ratings_store2 = store2_df['Total Reviews'].iloc[0]
                        total_number_of_ratings_store2 = len(store2_df)
                        st.markdown(f"<h1 class='left-content'>Total Ratings ::</h1>", unsafe_allow_html=True)
                        st.markdown(total_number_of_ratings_store2)
            ###Display Average Rating
                        avg_rating_store2 = round(store2_df['Avg Rating'].mean(),1)
                        st.markdown(f"<h1 class='left-content'>Average Rating ::</h1>", unsafe_allow_html=True)
                        st.markdown(f"{avg_rating_store2} Stars")
            ###Display % spread of reviews
                        st.markdown(f"<h1 class='left-content'>Rating Spread ::</h1>", unsafe_allow_html=True)
                        #Count the occurrences of each rating
                        rating_counts_store2 = store2_df['review_rating'].value_counts()
                        #Create a DataFrame
                        normalized_percentages = round(store2_df['review_rating'].value_counts(normalize=True) * 100,0)
                        normalized_percentages = normalized_percentages.apply(lambda x: '<1' if x < 1 else x)
                        rating_data_store2 = pd.DataFrame({'Rating': rating_counts_store2.index,
                                                                'Count': rating_counts_store2.values,
                                                                '%':normalized_percentages})
                        #Sort the DataFrame in descending order of 'Rating'
                        rating_data_store2 = rating_data_store2.sort_values('Rating', ascending=False)
                        st.dataframe(rating_data_store2[['Rating','%']],hide_index=True)

        ###==Top Spoken Topics 📢 Expander==            
                    with st.expander("Top Spoken Topics 📢"):
            ###Display Total ratings with text
                        non_null_count_store2 = store2_df['review_text'].count()
            ###Top Spoken Topics
                        #Define the topics
                        topics = ["Customer Confidence", "Store Experience", "Store Staff", "Product Design","Product Variety", 
                                    "Discount", "Making Charge", "Price", "Product Quality", "Jewellery Exchange"]
                        #Take only reviews with text
                        store2_df_non_null = store2_df.dropna(subset=['review_text'])
                        #Initialize a dictionary to hold the count of discussed topics
                        discussed_topics_count_store2 = {}
                        #Count the number of non-zero entries for each topic in the DataFrame
                        for topic in topics:
                            # A topic is considered discussed if its score is 1 or -1
                            discussed_topics_count_store2[topic] = store2_df_non_null[topic][store2_df_non_null[topic] != 0].count()
                        # Convert the dictionary to a DataFrame for visualization
                        topics_df_store2 = pd.DataFrame(list(discussed_topics_count_store2.items()), columns=['Topic', 'Count'])
                        # Calculate the percentage of total reviews for each topic
                        topics_df_store2['Percentage'] = (topics_df_store2['Count'] / non_null_count_store2) * 100
                        # Sort the DataFrame based on the count of discussed topics in descending order
                        topics_df_store2 = topics_df_store2.sort_values('Count', ascending=False)
                        # Create the horizontal bar chart using Plotly Express
                        fig_store2 = px.bar(
                                                topics_df_store2, 
                                                x='Topic', 
                                                y='Count', 
                                                orientation='v',
                                                text='Percentage'
                                            )
                        # Update the layout for a cleaner look
                        fig_store2.update_layout(
                                                    yaxis={'categoryorder':'total ascending'},
                                                    xaxis_title="Topics",
                                                    yaxis_title="Number of Reviews",
                                                    title="Top Spoken Topics",
                                                    showlegend=False,
                                                    autosize=True,
                                                    annotations=[dict(xref='paper', yref='paper',x=0.5, y=1.05,
                                                                        xanchor='center', yanchor='top',
                                                                        text=f"Total Spoken Reviews: {len(store2_df_non_null)}",
                                                                        font=dict(size=14),showarrow=False)]
                                                )
                        # Update the bar element to display the percentage text
                        fig_store2.update_traces(
                                                    texttemplate='%{text:.1f}%', textposition='outside',
                                                    hovertemplate = "<b>Topic</b>: %{x}<br>" + 
                                                                    "<b>Count</b>: %{y}<br>" + 
                                                                    "<b>Percentage</b>: %{text:.1f}%<extra></extra>"
                                                )
                        # Display the bar chart in Streamlit
                        st.plotly_chart(fig_store2,use_container_width=True)

        ###==Sentiment Analytics Expander==            
                    with st.expander("Topic wise sentiments😃😢"):                    
            ###Sentiment in each topic
                        # Initialize a list to hold the count of positive and negative sentiments for each topic
                        sentiment_counts_store2 = []
                        # Count the number of positive and negative sentiments for each topic
                        for topic in topics:
                            positive_count_store2 = (store2_df[topic] == 1).sum()
                            negative_count_store2 = (store2_df[topic] == -1).sum()
                            total_count_store2 = positive_count_store2 + negative_count_store2
                            sentiment_counts_store2.append({
                                                                'Topic': topic, 
                                                                'Positive': positive_count_store2, 
                                                                'Negative': negative_count_store2,
                                                                'Total': total_count_store2
                                                            })
                        # Create a DataFrame for visualization
                        sentiment_df_store2 = pd.DataFrame(sentiment_counts_store2)
                        # Sort the DataFrame based on the total count of reviews in descending order
                        sentiment_df_store2.sort_values('Total', ascending=False, inplace=True)
                        # Melt the DataFrame to long format for Plotly
                        sentiment_long_df_store2 = sentiment_df_store2.melt(id_vars=['Topic', 'Total'], value_vars=['Positive', 'Negative'],
                                                                                    var_name='Sentiment', value_name='Count')
                        # Calculate the percentage for each sentiment
                        sentiment_long_df_store2['Percentage'] = (sentiment_long_df_store2['Count'] / sentiment_long_df_store2['Total'] * 100).round(1)
                        # Create the horizontal (transposed) bar chart using Plotly Express
                        fig_sentiments_store2 = px.bar(
                                                            sentiment_long_df_store2,
                                                            y='Topic',
                                                            x='Count',
                                                            color='Sentiment',
                                                            color_discrete_map={'Positive': '#39CEFF', 'Negative': '#FF735D'},  # Custom colors
                                                            barmode='group',
                                                            orientation='h',  # This creates a horizontal bar chart
                                                            category_orders={"Topic": sentiment_df_store2['Topic'].tolist()},
                                                            text='Percentage'
                                                            )
                        # Update the layout for a cleaner look
                        fig_sentiments_store2.update_layout(
                                                                yaxis_title="Topics",
                                                                xaxis_title="Count of Sentiments",
                                                                title="Overview",
                                                                showlegend=True,
                                                                legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="right", x=0.9),
                                                            )
                        # Format the text on the bars to show the percentage with one decimal & Customizing hovertemplate to show one decimal place for the percentage
                        fig_sentiments_store2.update_traces(
                                                                texttemplate='%{text}%', textposition='outside',
                                                                hovertemplate="<b>Topic</b>: %{y}<br><b>Count</b>: %{x}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{text}%",customdata=sentiment_long_df_store2[['Total']].values
                                                    )
                        # Display the horizontal bar chart in Streamlit
                        st.plotly_chart(fig_sentiments_store2, use_container_width=True)
        ###==Pain Points Expander==            
                    with st.expander("Analyzing Pain Points ❌"):                            
                        # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                        negative_reviews_df_store2 = sentiment_df_store2[['Topic', 'Negative', 'Total']]
                        # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                        negative_reviews_df_catchment = sentiment_df_catchment[['Topic', 'Negative', 'Total']]
                        # Calculate the percentage of negative reviews
                        negative_reviews_df_catchment['Percentage'] = round(negative_reviews_df_catchment['Negative'] / negative_reviews_df_catchment['Total'] * 100,1)
                        # Sort the DataFrame based on the count of negative reviews in descending order
                        negative_reviews_df_sorted_catchment = negative_reviews_df_catchment.sort_values('Percentage', ascending=True)
                        # Calculate the percentage of negative reviews
                        negative_reviews_df_store2['Percentage'] = round(negative_reviews_df_store2['Negative'] / negative_reviews_df_store2['Total'] * 100,1)
                        # Create the bar chart using Plotly Express
                        # Align the order of topics in negative_reviews_df_store2 with the sorted order in negative_reviews_df_sorted_catchment
                        negative_reviews_df_ordered_store2 = negative_reviews_df_sorted_catchment[['Topic']].merge(negative_reviews_df_store2, on='Topic', how='left')

                        fig_negative_reviews = px.bar(
                                                        negative_reviews_df_ordered_store2,
                                                        y='Topic',
                                                        x='Percentage',
                                                        orientation='h',  # This creates a horizontal bar chart
                                                        color_discrete_sequence=['#FF735D'],
                                                        )
                        # Update the layout for a cleaner look
                        fig_negative_reviews.update_layout(
                                                            #yaxis_title="Topics",
                                                            xaxis_title="% of Negative Reviews",
                                                            title="Pain Points Spread across Topics",
                                                            showlegend=False,
                                                            )
                        # Format the hovertemplate to show the desired data
                        fig_negative_reviews.update_traces(
                                                            texttemplate='%{x}%',textposition='outside',
                                                            hovertemplate="<b>Topic</b>: %{y}<br><b>Negative Count</b>: %{customdata[1]}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{x}%",
                                                            customdata=negative_reviews_df_ordered_store2[['Total', 'Negative']].values
                                                            )
                        # Display the bar chart in Streamlit
                        #st.plotly_chart(fig_negative_reviews, use_container_width=True)
                        sentiment_df_store2['Negative Percentage'] = sentiment_df_store2['Negative'] / sentiment_df_store2['Total'] * 100
                        Negative_sorted_store2 = sentiment_df_store2.sort_values(['Negative Percentage', 'Total'], 
                                                                                        ascending=[False, False]).reset_index(drop=True)
                        #top_5_Negative_topics_catchment = Negative_sorted_catchment.head(5)['Topic'] 
                        top_5_Negative_topics_catchment = Negative_sorted_catchment['Topic']
                        # Now, for each of these top 5 topics, print the Negative Keywords separately
                        st.markdown("\n")
                        st.markdown("**Phrases**")

                        for topic in top_5_Negative_topics_catchment:
                            # Get the row from the dataframe for the current topic
                            row_store2 = sentiment_df_store2[sentiment_df_store2['Topic'] == topic]
                            # Extract the Negative and total counts for the topic
                            Negative_count_store2 = row_store2['Negative'].values[0]
                            total_count_store2 = row_store2['Total'].values[0]
                            # Filter the rows for Negative type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                            Negative_phrases_list_store2 = store2_df_keywords[(store2_df_keywords['Sentiment'] == 'negative') & (store2_df_keywords['Type'] == 'phrases')][topic].dropna().values
                            # Display the topic header
                            st.markdown(f"<h1 class='left-content-2'>{topic}: {Negative_count_store2} out of {total_count_store2} ({round((Negative_count_store2/ total_count_store2)*100,1)}%)</h1>", unsafe_allow_html=True)
                            # Container to hold the keyword boxes
                            phrase_boxes = ""
                            if Negative_phrases_list_store2.size > 0:
                            # Now, display each keyword in a separate styled box
                                phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                                phrase_counter = 0
                                for phrase_line in Negative_phrases_list_store2:    
                                    # Split the keyword phrase by comma and strip spaces
                                    phrases = phrase_line.split(',')
                                    for phrase in phrases:
                                        # Remove the numbers, colons and trim whitespace
                                        phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                        if phrase_text == "No relevant negative phrases":
                                            phrase_boxes += f"<span class='keyword-box-green'>None</span>"
                                            break
                                        if phrase_text:  # Only display if there's a keyword
                                            # Append each keyword to the container
                                            phrase_boxes += f"<span class='keyword-box-red'>{phrase_text}</span>"
                                            phrase_counter += 1
                                            # Limit the display to the first 5 keywords
                                            if phrase_counter >= 5:
                                                break
                                    if phrase_counter >= 5:
                                        break
                                phrase_boxes += "</div>"
                            else:
                                phrase_boxes += f"<span class='keyword-box-green'>None</span>"  
                            # Display the keyword boxes
                            st.markdown(phrase_boxes, unsafe_allow_html=True)                   
        ###==Delight Factors Expander==         
                    with st.expander("Delight Factors🌟"):                                      
                        sentiment_df_store2['Positive Percentage'] = sentiment_df_store2['Positive'] / sentiment_df_store2['Total'] * 100
                        positive_sorted_store2 = sentiment_df_store2.sort_values(['Positive Percentage', 'Total'], 
                                                                                        ascending=[False, False]).reset_index(drop=True)
                        #top_5_positive_topics_store2 = positive_sorted_store2.head(5)['Topic']
                        top_5_positive_topics_store2 = positive_sorted_store2['Topic']
                        # Now, for each of these top 5 topics, print the Positive Keywords separately
                        st.markdown("\n")
                        st.markdown("**Phrases**")
                        for topic in top_5_positive_topics_store2:
                            # Get the row from the dataframe for the current topic
                            row_store2 = sentiment_df_store2[sentiment_df_store2['Topic'] == topic]
                            # Extract the positive and total counts for the topic
                            positive_count_store2 = row_store2['Positive'].values[0]
                            total_count_store2 = row_store2['Total'].values[0]
                            # Filter the rows for Positive type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                            positive_phrases_list_store2 = store2_df_keywords[(store2_df_keywords['Sentiment'] == 'Positive') & (store2_df_keywords['Type'] == 'phrases')][topic].dropna().values
                            # Display the topic header
                            st.markdown(f"<h1 class='left-content-2'>{topic}: {positive_count_store2} out of {total_count_store2} ({round((positive_count_store2/ total_count_store2)*100,1)}%)</h1>", unsafe_allow_html=True)
                            # Container to hold the keyword boxes
                            phrase_boxes = ""

                            if positive_phrases_list_store2.size > 0:
                            # Now, display each keyword in a separate styled box
                                phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                                phrase_counter = 0
                                for phrase_line in positive_phrases_list_store2:    
                                    # Split the keyword phrase by comma and strip spaces
                                    phrases = phrase_line.split(',')
                                    for phrase in phrases:
                                        # Remove the numbers, colons and trim whitespace
                                        phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                        if phrase_text == "No relevant positive phrases":
                                            phrase_boxes += f"<span class='keyword-box-red'>None</span>"
                                            if phrase_counter >= 5:
                                                break
                                        if phrase_text:  # Only display if there's a keyword
                                            # Append each keyword to the container
                                            phrase_boxes += f"<span class='keyword-box-green'>{phrase_text}</span>"
                                            phrase_counter += 1
                                            # Limit the display to the first 5 keywords
                                            if phrase_counter >= 5:
                                                break
                                    if phrase_counter >= 5:
                                        break
                                phrase_boxes += "</div>"
                            else:
                                phrase_boxes += f"<span class='keyword-box-red'>None</span>"  
                            # Display the keyword boxes
                            st.markdown(phrase_boxes, unsafe_allow_html=True)                   
            with col5:
                if selected_store3 == "None":
                    pass
                elif selected_store3 == "":
                    pass
                else:
                    ###Display name of the store
                    st.markdown(f"<h1 class='sticky-left-header'>{selected_store3}</h1>", unsafe_allow_html=True)
        ###==Overview Expander==
                    with st.expander("Overview🌐"):
            ###Display Total ratings
                        # total_number_of_ratings_store3 = selected_store3['Total Reviews'].iloc[0]
                        total_number_of_ratings_store3 = len(selected_store3)
                        st.markdown(f"<h1 class='left-content'>Total Ratings(Apr'24 - May'25) ::</h1>", unsafe_allow_html=True)
                        st.markdown(total_number_of_ratings_store3)
            ###Display Average Rating
                        avg_rating_store3 = round(store3_df['Avg Rating'].mean(),1)
                        st.markdown(f"<h1 class='left-content'>Average Rating ::</h1>", unsafe_allow_html=True)
                        st.markdown(f"{avg_rating_store3} Stars")
            ###Display % spread of reviews
                        st.markdown(f"<h1 class='left-content'>Rating Spread ::</h1>", unsafe_allow_html=True)
                        #Count the occurrences of each rating
                        rating_counts_store3 = store3_df['review_rating'].value_counts()
                        #Create a DataFrame
                        normalized_percentages = round(store3_df['review_rating'].value_counts(normalize=True) * 100,0)
                        normalized_percentages = normalized_percentages.apply(lambda x: '<1' if x < 1 else x)
                        rating_data_store3 = pd.DataFrame({'Rating': rating_counts_store3.index,
                                                                'Count': rating_counts_store3.values,
                                                                '%':normalized_percentages})

                        #Sort the DataFrame in descending order of 'Rating'
                        rating_data_store3 = rating_data_store3.sort_values('Rating', ascending=False)
                        st.dataframe(rating_data_store3[['Rating','%']],hide_index=True)

        ###==Top Spoken Topics 📢 Expander==            
                    with st.expander("Top Spoken Topics 📢"):
            ###Display Total ratings with text
                        non_null_count_store3 = store3_df['review_text'].count()
            ###Top Spoken Topics
                        #Define the topics
                        topics = ["Customer Confidence", "Store Experience", "Store Staff", "Product Design","Product Variety", 
                                    "Discount", "Making Charge", "Price", "Product Quality", "Jewellery Exchange"]
                        #Take only reviews with text
                        selected_store3_non_null = store3_df.dropna(subset=['review_text'])
                        #Initialize a dictionary to hold the count of discussed topics
                        discussed_topics_count_store3 = {}
                        #Count the number of non-zero entries for each topic in the DataFrame
                        for topic in topics:
                            # A topic is considered discussed if its score is 1 or -1
                            discussed_topics_count_store3[topic] = selected_store3_non_null[topic][selected_store3_non_null[topic] != 0].count()
                        # Convert the dictionary to a DataFrame for visualization
                        topics_df_store3 = pd.DataFrame(list(discussed_topics_count_store3.items()), columns=['Topic', 'Count'])
                        # Calculate the percentage of total reviews for each topic
                        topics_df_store3['Percentage'] = (topics_df_store3['Count'] / non_null_count_store3) * 100
                        # Sort the DataFrame based on the count of discussed topics in descending order
                        topics_df_store3 = topics_df_store3.sort_values('Count', ascending=False)
                        # Create the horizontal bar chart using Plotly Express
                        fig_store3 = px.bar(
                                                topics_df_store3, 
                                                x='Topic', 
                                                y='Count', 
                                                orientation='v',
                                                text='Percentage'
                                            )
                        # Update the layout for a cleaner look
                        fig_store3.update_layout(
                                                    yaxis={'categoryorder':'total ascending'},
                                                    xaxis_title="Topics",
                                                    yaxis_title="Number of Reviews",
                                                    title="Top Spoken Topics",
                                                    showlegend=False,
                                                    autosize=True,
                                                    annotations=[dict(xref='paper', yref='paper',x=0.5, y=1.05,
                                                                        xanchor='center', yanchor='top',
                                                                        text=f"Total Spoken Reviews: {len(selected_store3_non_null)}",
                                                                        font=dict(size=14),showarrow=False)]
                                                )
                        # Update the bar element to display the percentage text
                        fig_store3.update_traces(
                                                    texttemplate='%{text:.1f}%', textposition='outside',
                                                    hovertemplate = "<b>Topic</b>: %{x}<br>" + 
                                                                    "<b>Count</b>: %{y}<br>" + 
                                                                    "<b>Percentage</b>: %{text:.1f}%<extra></extra>"
                                                )
                        # Display the bar chart in Streamlit
                        st.plotly_chart(fig_store3,use_container_width=True)
        ###==Sentiment Analytics Expander==            
                    with st.expander("Topic wise sentiments😃😢"):                    
            ###Sentiment in each topic
                        # Initialize a list to hold the count of positive and negative sentiments for each topic
                        sentiment_counts_store3 = []
                        # Count the number of positive and negative sentiments for each topic
                        for topic in topics:
                            positive_count_store3 = (store3_df[topic] == 1).sum()
                            negative_count_store3 = (store3_df[topic] == -1).sum()
                            total_count_store3 = positive_count_store3 + negative_count_store3
                            sentiment_counts_store3.append({
                                                                'Topic': topic, 
                                                                'Positive': positive_count_store3, 
                                                                'Negative': negative_count_store3,
                                                                'Total': total_count_store3
                                                            })
                        # Create a DataFrame for visualization
                        sentiment_df_store3 = pd.DataFrame(sentiment_counts_store3)
                        # Sort the DataFrame based on the total count of reviews in descending order
                        sentiment_df_store3.sort_values('Total', ascending=False, inplace=True)
                        # Melt the DataFrame to long format for Plotly
                        sentiment_long_df_store3 = sentiment_df_store3.melt(id_vars=['Topic', 'Total'], value_vars=['Positive', 'Negative'],
                                                                                    var_name='Sentiment', value_name='Count')
                        # Calculate the percentage for each sentiment
                        sentiment_long_df_store3['Percentage'] = (sentiment_long_df_store3['Count'] / sentiment_long_df_store3['Total'] * 100).round(1)
                        # Create the horizontal (transposed) bar chart using Plotly Express
                        fig_sentiments_store3 = px.bar(
                                                            sentiment_long_df_store3,
                                                            y='Topic',
                                                            x='Count',
                                                            color='Sentiment',
                                                            color_discrete_map={'Positive': '#39CEFF', 'Negative': '#FF735D'},  # Custom colors
                                                            barmode='group',
                                                            orientation='h',  # This creates a horizontal bar chart
                                                            category_orders={"Topic": sentiment_df_store3['Topic'].tolist()},
                                                            text='Percentage'
                                                            )
                        # Update the layout for a cleaner look
                        fig_sentiments_store3.update_layout(
                                                                yaxis_title="Topics",
                                                                xaxis_title="Count of Sentiments",
                                                                title="Overview",
                                                                showlegend=True,
                                                                legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="right", x=0.9),
                                                            )
                        # Format the text on the bars to show the percentage with one decimal & Customizing hovertemplate to show one decimal place for the percentage
                        fig_sentiments_store3.update_traces(
                                                                texttemplate='%{text}%', textposition='outside',
                                                                hovertemplate="<b>Topic</b>: %{y}<br><b>Count</b>: %{x}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{text}%",customdata=sentiment_long_df_store3[['Total']].values
                                                    )
                        # Display the horizontal bar chart in Streamlit
                        st.plotly_chart(fig_sentiments_store3, use_container_width=True)

        ###==Pain Points Expander==            
                    with st.expander("Analyzing Pain Points ❌"):                            
                        # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                        negative_reviews_df_store3 = sentiment_df_store3[['Topic', 'Negative', 'Total']]
                        # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                        negative_reviews_df_catchment = sentiment_df_catchment[['Topic', 'Negative', 'Total']]
                        # Calculate the percentage of negative reviews
                        negative_reviews_df_catchment['Percentage'] = round(negative_reviews_df_catchment['Negative'] / negative_reviews_df_catchment['Total'] * 100,1)
                        # Sort the DataFrame based on the count of negative reviews in descending order
                        negative_reviews_df_sorted_catchment = negative_reviews_df_catchment.sort_values('Percentage', ascending=True)
                        # Calculate the percentage of negative reviews
                        negative_reviews_df_store3['Percentage'] = round(negative_reviews_df_store3['Negative'] / negative_reviews_df_store3['Total'] * 100,1)
                        # Create the bar chart using Plotly Express
                        # Align the order of topics in negative_reviews_df_store3 with the sorted order in negative_reviews_df_sorted_catchment
                        negative_reviews_df_ordered_store3 = negative_reviews_df_sorted_catchment[['Topic']].merge(negative_reviews_df_store3, on='Topic', how='left')

                        fig_negative_reviews = px.bar(
                                                        negative_reviews_df_ordered_store3,
                                                        y='Topic',
                                                        x='Percentage',
                                                        orientation='h',  # This creates a horizontal bar chart
                                                        color_discrete_sequence=['#FF735D'],
                                                        )
                        # Update the layout for a cleaner look
                        fig_negative_reviews.update_layout(
                                                            #yaxis_title="Topics",
                                                            xaxis_title="% of Negative Reviews",
                                                            title="Pain Points Spread across Topics",
                                                            showlegend=False,
                                                            )
                        # Format the hovertemplate to show the desired data
                        fig_negative_reviews.update_traces(
                                                            texttemplate='%{x}%',textposition='outside',
                                                            hovertemplate="<b>Topic</b>: %{y}<br><b>Negative Count</b>: %{customdata[1]}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{x}%",
                                                            customdata=negative_reviews_df_ordered_store3[['Total', 'Negative']].values
                                                            )
                        # Display the bar chart in Streamlit
                        #st.plotly_chart(fig_negative_reviews, use_container_width=True)
                        sentiment_df_store3['Negative Percentage'] = sentiment_df_store3['Negative'] / sentiment_df_store3['Total'] * 100
                        Negative_sorted_store3 = sentiment_df_store3.sort_values(['Negative Percentage', 'Total'], 
                                                                                        ascending=[False, False]).reset_index(drop=True)
                        #top_5_Negative_topics_catchment = Negative_sorted_catchment.head(5)['Topic']      
                        top_5_Negative_topics_catchment = Negative_sorted_catchment['Topic']
                        # Now, for each of these top 5 topics, print the Negative Keywords separately
                        st.markdown("\n")
                        st.markdown("**Phrases**")
                        for topic in top_5_Negative_topics_catchment:
                            # Get the row from the dataframe for the current topic
                            row_store3 = sentiment_df_store3[sentiment_df_store3['Topic'] == topic]
                            # Extract the Negative and total counts for the topic
                            Negative_count_store3 = row_store3['Negative'].values[0]
                            total_count_store3 = row_store3['Total'].values[0]
                            # Filter the rows for Negative type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                            Negative_phrases_list_store3 = store3_df_keywords[(store3_df_keywords['Sentiment'] == 'negative') & (store3_df_keywords['Type'] == 'phrases')][topic].dropna().values
                            # Display the topic header
                            st.markdown(f"<h1 class='left-content-2'>{topic}: {Negative_count_store3} out of {total_count_store3} ({round((Negative_count_store3/ total_count_store3)*100,1)}%)</h1>", unsafe_allow_html=True)
                            # Container to hold the keyword boxes
                            phrase_boxes = ""

                            if Negative_phrases_list_store3.size > 0:
                            # Now, display each keyword in a separate styled box
                                phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                                phrase_counter = 0
                                for phrase_line in Negative_phrases_list_store3:    
                                    # Split the keyword phrase by comma and strip spaces
                                    phrases = phrase_line.split(',')
                                    for phrase in phrases:
                                        # Remove the numbers, colons and trim whitespace
                                        phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                        if phrase_text == "No relevant negative phrases":
                                            phrase_boxes += f"<span class='keyword-box-green'>None</span>"
                                            break
                                        if phrase_text:  # Only display if there's a keyword
                                            # Append each keyword to the container
                                            phrase_boxes += f"<span class='keyword-box-red'>{phrase_text}</span>"
                                            phrase_counter += 1
                                            # Limit the display to the first 5 keywords
                                            if phrase_counter >= 5:
                                                break
                                    if phrase_counter >= 5:
                                        break
                                phrase_boxes += "</div>"
                            else:
                                phrase_boxes += f"<span class='keyword-box-green'>None</span>"  

                            # Display the keyword boxes
                            st.markdown(phrase_boxes, unsafe_allow_html=True)                   
        ###==Delight Factors Expander==         
                    with st.expander("Delight Factors🌟"):                                      
                        sentiment_df_store3['Positive Percentage'] = sentiment_df_store3['Positive'] / sentiment_df_store3['Total'] * 100
                        positive_sorted_store3 = sentiment_df_store3.sort_values(['Positive Percentage', 'Total'], 
                                                                                        ascending=[False, False]).reset_index(drop=True)
                        #top_5_positive_topics_store3 = positive_sorted_store3.head(5)['Topic']    
                        top_5_positive_topics_store3 = positive_sorted_store3['Topic']
                        # Now, for each of these top 5 topics, print the Positive Keywords separately
                        st.markdown("\n")
                        st.markdown("**Phrases**")
                        for topic in top_5_positive_topics_store3:
                            # Get the row from the dataframe for the current topic
                            row_store3 = sentiment_df_store3[sentiment_df_store3['Topic'] == topic]
                            # Extract the positive and total counts for the topic
                            positive_count_store3 = row_store3['Positive'].values[0]
                            total_count_store3 = row_store3['Total'].values[0]
                            # Filter the rows for Positive type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                            positive_phrases_list_store3 = store3_df_keywords[(store3_df_keywords['Sentiment'] == 'Positive') & (store3_df_keywords['Type'] == 'phrases')][topic].dropna().values
                            # Display the topic header
                            st.markdown(f"<h1 class='left-content-2'>{topic}: {positive_count_store3} out of {total_count_store3} ({round((positive_count_store3/ total_count_store3)*100,1)}%)</h1>", unsafe_allow_html=True)
                            # Container to hold the keyword boxes
                            phrase_boxes = ""
                            if positive_phrases_list_store3.size > 0:
                            # Now, display each keyword in a separate styled box
                                phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                                phrase_counter = 0
                                for phrase_line in positive_phrases_list_store3:    
                                    # Split the keyword phrase by comma and strip spaces
                                    phrases = phrase_line.split(',')
                                    for phrase in phrases:
                                        # Remove the numbers, colons and trim whitespace
                                        phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                        if phrase_text == "No relevant positive keywords":
                                            phrase_boxes += f"<span class='keyword-box-red'>None</span>"
                                            if phrase_counter >= 5:
                                                break
                                        if phrase_text:  # Only display if there's a keyword
                                            # Append each keyword to the container
                                            phrase_boxes += f"<span class='keyword-box-green'>{phrase_text}</span>"
                                            phrase_counter += 1
                                            # Limit the display to the first 5 keywords
                                            if phrase_counter >= 5:
                                                break
                                    if phrase_counter >= 5:
                                        break
                                phrase_boxes += "</div>"
                            else:
                                phrase_boxes += f"<span class='keyword-box-red'>None</span>"  
                            # Display the keyword boxes
                            st.markdown(phrase_boxes, unsafe_allow_html=True)                   
        ###==Download Sentiment Data== 
            #Get the current timestamp and format it
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            #List of columns to be selected
            selected_columns = ['Name of the Reviewer', 'Total Reviews', 'review_rating','Store Name', 
                                'Avg Rating', 'year','review_text','Customer Confidence','Store Experience',
                                'Store Staff','Product Design', 'Product Variety', 'Discount', 'Making Charge',
                                'Price', 'Jewellery Exchange']
            #Creating a new DataFrame with only the selected columns
            download_store1_df = store1_df[selected_columns]
            download_store2_df = store2_df[selected_columns]
            download_store3_df = store3_df[selected_columns]
            # Create filenames with the timestamp
            file_names = [(f"catchment_data_{timestamp}.xlsx", dataframe_to_excel(download_store1_df)),
                            (f"store2_data_{timestamp}.xlsx", dataframe_to_excel(download_store2_df)),
                                (f"store3_data_{timestamp}.xlsx", dataframe_to_excel(download_store3_df))]
            #Zip all the Excel files
            zip_buffer = create_zip(file_names)                                                      
            #Encode the ZIP file to base64
            zip_b64 = get_zip_base64(zip_buffer)
            # Create a download filename with the timestamp
            download_filename = f"Reviews_{timestamp}.zip"
            # Create the download link with the emoji and display it with Streamlit
            st.markdown(f'<a href="data:application/zip;base64,{zip_b64}" download="{download_filename}" class="btn btn-primary">⬇️ Download Reviews</a>', unsafe_allow_html=True)

        else:
            col3,col4 = st.columns(2)
            with col3:
        ###Display name of the store
                st.markdown(f"<h1 class='sticky-left-header'>{selected_store1}</h1>", unsafe_allow_html=True)
        ###==Overview Expander==
                with st.expander(f"Overview🌐"):
        ###Display Total ratings
                    #total_number_of_ratings_catchment = store1_df['Total Reviews'].iloc[0]
                    total_number_of_ratings_catchment = len(store1_df)
                    st.markdown(f"<h1 class='left-content'>Total Ratings(Apr'24 - May'25) ::</h1>", unsafe_allow_html=True)
                    st.markdown(total_number_of_ratings_catchment)
        ###Display Average Rating
                    avg_rating_catchment = round(store1_df['Avg Rating'].mean(),1)
                    st.markdown(f"<h1 class='left-content'>Average Rating ::</h1>", unsafe_allow_html=True)
                    st.markdown(f"{avg_rating_catchment} Stars")
        ###Display % spread of reviews
                    st.markdown(f"<h1 class='left-content'>Rating Spread ::</h1>", unsafe_allow_html=True)
                    #Count the occurrences of each rating
                    rating_counts_catchment = store1_df['review_rating'].value_counts()
                    #Create a DataFrame
                    normalized_percentages = round(store1_df['review_rating'].value_counts(normalize=True) * 100,0)
                    normalized_percentages = normalized_percentages.apply(lambda x: '<1' if x < 1 else x)
                    rating_data_catchment = pd.DataFrame({'Rating': rating_counts_catchment.index,
                                                            'Count': rating_counts_catchment.values,
                                                            '%':normalized_percentages})

                    #Sort the DataFrame in descending order of 'Rating'
                    rating_data_catchment = rating_data_catchment.sort_values('Rating', ascending=False)
                    st.dataframe(rating_data_catchment[['Rating','%']],hide_index=True)

    ###==Top Spoken Topics 📢 Expander==            
                with st.expander("Top Spoken Topics 📢"):
        ###Display Total ratings with text
                    non_null_count_catchment = store1_df['review_text'].count()
        ###Top Spoken Topics
                    #Define the topics
                    topics = ["Customer Confidence", "Store Experience", "Store Staff", "Product Design","Product Variety", 
                                "Discount", "Making Charge", "Price", "Product Quality", "Jewellery Exchange"]
                    #Take only reviews with text
                    store1_df_non_null = store1_df.dropna(subset=['review_text'])
                    #Initialize a dictionary to hold the count of discussed topics
                    discussed_topics_count_catchment = {}
                    #Count the number of non-zero entries for each topic in the DataFrame
                    for topic in topics:
                        # A topic is considered discussed if its score is 1 or -1
                        discussed_topics_count_catchment[topic] = store1_df_non_null[topic][store1_df_non_null[topic] != 0].count()
                    # Convert the dictionary to a DataFrame for visualization
                    topics_df_catchment = pd.DataFrame(list(discussed_topics_count_catchment.items()), columns=['Topic', 'Count'])
                    # Calculate the percentage of total reviews for each topic
                    topics_df_catchment['Percentage'] = (topics_df_catchment['Count'] / non_null_count_catchment) * 100
                    # Sort the DataFrame based on the count of discussed topics in descending order
                    topics_df_catchment = topics_df_catchment.sort_values('Count', ascending=False)
                    # Create the horizontal bar chart using Plotly Express
                    fig_catchment = px.bar(
                                            topics_df_catchment, 
                                            x='Topic', 
                                            y='Count', 
                                            orientation='v',
                                            text='Percentage'
                                        )
                    # Update the layout for a cleaner look
                    fig_catchment.update_layout(
                                                yaxis={'categoryorder':'total ascending'},
                                                xaxis_title="Topics",
                                                yaxis_title="Number of Reviews",
                                                title="Top Spoken Topics",
                                                showlegend=False,
                                                autosize=True,
                                                annotations=[dict(xref='paper', yref='paper',x=0.5, y=1.05,
                                                                    xanchor='center', yanchor='top',
                                                                    text=f"Total Spoken Reviews: {len(store1_df_non_null)}",
                                                                    font=dict(size=14),showarrow=False)]
                                            )
                    # Update the bar element to display the percentage text
                    fig_catchment.update_traces(
                                                texttemplate='%{text:.1f}%', textposition='outside',
                                                hovertemplate = "<b>Topic</b>: %{x}<br>" + 
                                                                "<b>Count</b>: %{y}<br>" + 
                                                                "<b>Percentage</b>: %{text:.1f}%<extra></extra>"
                                            )
                    # Display the bar chart in Streamlit
                    st.plotly_chart(fig_catchment,use_container_width=True)

    ###==Sentiment Analytics Expander==            
                with st.expander("Topic wise sentiments😃😢"):                    
                    ###Sentiment in each topic
                    # Initialize a list to hold the count of positive and negative sentiments for each topic
                    sentiment_counts_catchment = []
                    # Count the number of positive and negative sentiments for each topic
                    for topic in topics:
                        positive_count_catchment = (store1_df[topic] == 1).sum()
                        negative_count_catchment = (store1_df[topic] == -1).sum()
                        total_count_catchment = positive_count_catchment + negative_count_catchment
                        sentiment_counts_catchment.append({
                                                            'Topic': topic, 
                                                            'Positive': positive_count_catchment, 
                                                            'Negative': negative_count_catchment,
                                                            'Total': total_count_catchment
                                                        })
                    # Create a DataFrame for visualization
                    sentiment_df_catchment = pd.DataFrame(sentiment_counts_catchment)
                    # Sort the DataFrame based on the total count of reviews in descending order
                    sentiment_df_catchment.sort_values('Total', ascending=False, inplace=True)
                    # Melt the DataFrame to long format for Plotly
                    sentiment_long_df_catchment = sentiment_df_catchment.melt(id_vars=['Topic', 'Total'], value_vars=['Positive', 'Negative'],
                                                                                var_name='Sentiment', value_name='Count')
                    # Calculate the percentage for each sentiment
                    sentiment_long_df_catchment['Percentage'] = (sentiment_long_df_catchment['Count'] / sentiment_long_df_catchment['Total'] * 100).round(1)
                    # Create the horizontal (transposed) bar chart using Plotly Express
                    fig_sentiments_catchment = px.bar(
                                                        sentiment_long_df_catchment,
                                                        y='Topic',
                                                        x='Count',
                                                        color='Sentiment',
                                                        color_discrete_map={'Positive': '#39CEFF', 'Negative': '#FF735D'},  # Custom colors
                                                        barmode='group',
                                                        orientation='h',  # This creates a horizontal bar chart
                                                        category_orders={"Topic": sentiment_df_catchment['Topic'].tolist()},
                                                        text='Percentage'
                                                        )
                    # Update the layout for a cleaner look
                    fig_sentiments_catchment.update_layout(
                                                            yaxis_title="Topics",
                                                            xaxis_title="Count of Sentiments",
                                                            title="Overview",
                                                            showlegend=True,
                                                            legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="right", x=0.9),
                                                        )
                    # Format the text on the bars to show the percentage with one decimal & Customizing hovertemplate to show one decimal place for the percentage
                    fig_sentiments_catchment.update_traces(
                                                            texttemplate='%{text}%', textposition='outside',
                                                            hovertemplate="<b>Topic</b>: %{y}<br><b>Count</b>: %{x}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{text}%",customdata=sentiment_long_df_catchment[['Total']].values
                                                )
                    # Display the horizontal bar chart in Streamlit
                    st.plotly_chart(fig_sentiments_catchment, use_container_width=True)

    ###==Pain Points Expander==
                with st.expander("Analyzing Pain Points ❌"):                                      
                    # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                    negative_reviews_df_catchment = sentiment_df_catchment[['Topic', 'Negative', 'Total']]
                    # Calculate the percentage of negative reviews
                    negative_reviews_df_catchment['Percentage'] = round(negative_reviews_df_catchment['Negative'] / negative_reviews_df_catchment['Total'] * 100,1)
                    # Sort the DataFrame based on the count of negative reviews in descending order
                    negative_reviews_df_sorted_catchment = negative_reviews_df_catchment.sort_values(['Percentage', 'Total'], ascending=[True,False])

                    # Create the bar chart using Plotly Express
                    fig_negative_reviews = px.bar(
                                                    negative_reviews_df_sorted_catchment,
                                                    y='Topic',
                                                    x='Percentage',
                                                    orientation='h',  # This creates a horizontal bar chart
                                                    color_discrete_sequence=['#FF735D'],
                                                    )
                    # Update the layout for a cleaner look
                    fig_negative_reviews.update_layout(
                                                        #yaxis_title="Topics",
                                                        xaxis_title="% of Negative Reviews",
                                                        title="Pain Points Spread across Topics",
                                                        showlegend=False,
                                                        )
                    # Format the hovertemplate to show the desired data
                    fig_negative_reviews.update_traces(
                                                        texttemplate='%{x}%',textposition='outside',
                                                        hovertemplate="<b>Topic</b>: %{y}<br><b>Negative Count</b>: %{customdata[1]}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{x}%",
                                                        customdata=negative_reviews_df_sorted_catchment[['Total', 'Negative']].values
                                                        )
                    # Display the bar chart in Streamlit
                    #st.plotly_chart(fig_negative_reviews, use_container_width=True)
                    sentiment_df_catchment['Negative Percentage'] = sentiment_df_catchment['Negative'] / sentiment_df_catchment['Total'] * 100
                    Negative_sorted_catchment = sentiment_df_catchment.sort_values(['Negative Percentage', 'Total'], 
                                                                                    ascending=[False, False]).reset_index(drop=True)
                    #top_5_Negative_topics_catchment = Negative_sorted_catchment.head(5)['Topic']
                    top_5_Negative_topics_catchment = Negative_sorted_catchment['Topic']                    
                    st.markdown("\n")
                    st.markdown("**Phrases**")

                    for topic in top_5_Negative_topics_catchment:
                        # Get the row from the dataframe for the current topic
                        row_catchment = sentiment_df_catchment[sentiment_df_catchment['Topic'] == topic]
                        # Extract the Negative and total counts for the topic
                        Negative_count_catchment = row_catchment['Negative'].values[0]
                        total_count_catchment = row_catchment['Total'].values[0]
                        # Filter the rows for Negative type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                        Negative_phrases_list_catchment = store1_df_keywords[(store1_df_keywords['Sentiment'] == 'negative') & (store1_df_keywords['Type'] == 'phrases')][topic].dropna().values

                        # Display the topic header
                        st.markdown(f"<h1 class='left-content-2'>{topic}: {Negative_count_catchment} out of {total_count_catchment} ({round((Negative_count_catchment/ total_count_catchment)*100,1)}%)</h1>", unsafe_allow_html=True)
                        # Container to hold the keyword boxes
                        phrase_boxes = ""

                        if Negative_phrases_list_catchment.size > 0:
                        # Now, display each keyword in a separate styled box
                            phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                            phrase_counter = 0
                            for phrase_line in Negative_phrases_list_catchment:    
                                # Split the keyword phrase by comma and strip spaces
                                phrases = phrase_line.split(',')
                                for phrase in phrases:
                                    # Remove the numbers, colons and trim whitespace
                                    phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                    if phrase_text == "No relevant negative phrases":
                                        phrase_boxes += f"<span class='keyword-box-green'>None</span>"
                                        break
                                    elif phrase_text:  # Only display if there's a keyword
                                        # Append each keyword to the container
                                        phrase_boxes += f"<span class='keyword-box-red'>{phrase_text}</span>"
                                        phrase_counter += 1
                                        # Limit the display to the first 5 keywords
                                        if phrase_counter >= 5:
                                            break
                                if phrase_counter >= 5:
                                    break
                            phrase_boxes += "</div>"
                        else:
                            phrase_boxes += f"<span class='keyword-box-green'>None</span>"  

                        # Display the keyword boxes
                        st.markdown(phrase_boxes, unsafe_allow_html=True)                   

    ###==Delight Factors Expander==         
                with st.expander("Delight Factors🌟"):
                    sentiment_df_catchment['Positive Percentage'] = sentiment_df_catchment['Positive'] / sentiment_df_catchment['Total'] * 100
                    positive_sorted_catchment = sentiment_df_catchment.sort_values(['Positive Percentage', 'Total'], 
                                                                                    ascending=[False, False]).reset_index(drop=True)
                    #top_5_positive_topics_catchment = positive_sorted_catchment.head(5)['Topic']           
                    top_5_positive_topics_catchment = positive_sorted_catchment['Topic']
                    st.markdown("\n")
                    st.markdown("**Phrases**")
                    for topic in top_5_positive_topics_catchment:
                        # Get the row from the dataframe for the current topic
                        row_catchment = sentiment_df_catchment[sentiment_df_catchment['Topic'] == topic]
                        # Extract the positive and total counts for the topic
                        positive_count_catchment = row_catchment['Positive'].values[0]
                        total_count_catchment = row_catchment['Total'].values[0]
                        # Filter the rows for Positive type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                        positive_phrases_list_catchment = store1_df_keywords[(store1_df_keywords['Sentiment'] == 'Positive') & (store1_df_keywords['Type'] == 'phrases')][topic].dropna().values

                        # Display the topic header
                        st.markdown(f"<h1 class='left-content-2'>{topic}: {positive_count_catchment} out of {total_count_catchment} ({round((positive_count_catchment/ total_count_catchment)*100,1)}%)</h1>", unsafe_allow_html=True)
                        # Container to hold the keyword boxes
                        phrase_boxes = ""

                        if positive_phrases_list_catchment.size > 0:
                        # Now, display each keyword in a separate styled box
                            phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                            phrase_counter = 0
                            for phrase_line in positive_phrases_list_catchment:    
                                # Split the keyword phrase by comma and strip spaces
                                phrases = phrase_line.split(',')
                                for phrase in phrases:
                                    # Remove the numbers, colons and trim whitespace
                                    phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                    if phrase_text == "No relevant positive phrases":
                                        phrase_boxes += f"<span class='keyword-box-red'>None</span>"
                                        if phrase_counter >= 5:
                                            break
                                    if phrase_text:  # Only display if there's a keyword
                                        # Append each keyword to the container
                                        phrase_boxes += f"<span class='keyword-box-green'>{phrase_text}</span>"
                                        phrase_counter += 1
                                        # Limit the display to the first 5 keywords
                                        if phrase_counter >= 5:
                                            break
                                if phrase_counter >= 5:
                                    break
                            phrase_boxes += "</div>"
                        else:
                            phrase_boxes += f"<span class='keyword-box-red'>None</span>"  

                        # Display the keyword boxes
                        st.markdown(phrase_boxes, unsafe_allow_html=True)                   
            with col4:
                if selected_store2 == "None":
                    pass
                else:
            ###Display name of the store
                    #st.markdown(f"<h1 class='left-header'>{selected_competitor_1}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h1 class='sticky-left-header'>{selected_store2}</h1>", unsafe_allow_html=True)
        ###==Overview Expander==
                    with st.expander("Overview🌐"):
            ###Display Total Ratings(Apr'24 - May'25)
                        #total_number_of_ratings_store2 = store2_df['Total Reviews'].iloc[0]
                        total_number_of_ratings_store2 = len(store2_df)
                        st.markdown(f"<h1 class='left-content'>Total Ratings(Apr'24 - May'25) ::</h1>", unsafe_allow_html=True)
                        st.markdown(total_number_of_ratings_store2)
            ###Display Average Rating
                        avg_rating_store2 = round(store2_df['Avg Rating'].mean(),1)
                        st.markdown(f"<h1 class='left-content'>Average Rating ::</h1>", unsafe_allow_html=True)
                        st.markdown(f"{avg_rating_store2} Stars")
            ###Display % spread of reviews
                        st.markdown(f"<h1 class='left-content'>Rating Spread ::</h1>", unsafe_allow_html=True)
                        #Count the occurrences of each rating
                        rating_counts_store2 = store2_df['review_rating'].value_counts()
                        #Create a DataFrame
                        normalized_percentages = round(store2_df['review_rating'].value_counts(normalize=True) * 100,0)
                        normalized_percentages = normalized_percentages.apply(lambda x: '<1' if x < 1 else x)
                        rating_data_store2 = pd.DataFrame({'Rating': rating_counts_store2.index,
                                                                'Count': rating_counts_store2.values,
                                                                '%':normalized_percentages})
                        #Sort the DataFrame in descending order of 'Rating'
                        rating_data_store2 = rating_data_store2.sort_values('Rating', ascending=False)
                        st.dataframe(rating_data_store2[['Rating','%']],hide_index=True)

        ###==Top Spoken Topics 📢 Expander==            
                    with st.expander("Top Spoken Topics 📢"):
            ###Display Total ratings with text
                        non_null_count_store2 = store2_df['review_text'].count()
            ###Top Spoken Topics
                        #Define the topics
                        topics = ["Customer Confidence", "Store Experience", "Store Staff", "Product Design","Product Variety", 
                                    "Discount", "Making Charge", "Price", "Product Quality", "Jewellery Exchange"]
                        #Take only reviews with text
                        store2_df_non_null = store2_df.dropna(subset=['review_text'])
                        #Initialize a dictionary to hold the count of discussed topics
                        discussed_topics_count_store2 = {}
                        #Count the number of non-zero entries for each topic in the DataFrame
                        for topic in topics:
                            # A topic is considered discussed if its score is 1 or -1
                            discussed_topics_count_store2[topic] = store2_df_non_null[topic][store2_df_non_null[topic] != 0].count()
                        # Convert the dictionary to a DataFrame for visualization
                        topics_df_store2 = pd.DataFrame(list(discussed_topics_count_store2.items()), columns=['Topic', 'Count'])
                        # Calculate the percentage of total reviews for each topic
                        topics_df_store2['Percentage'] = (topics_df_store2['Count'] / non_null_count_store2) * 100
                        # Sort the DataFrame based on the count of discussed topics in descending order
                        topics_df_store2 = topics_df_store2.sort_values('Count', ascending=False)
                        # Create the horizontal bar chart using Plotly Express
                        fig_store2 = px.bar(
                                                topics_df_store2, 
                                                x='Topic', 
                                                y='Count', 
                                                orientation='v',
                                                text='Percentage'
                                            )
                        # Update the layout for a cleaner look
                        fig_store2.update_layout(
                                                    yaxis={'categoryorder':'total ascending'},
                                                    xaxis_title="Topics",
                                                    yaxis_title="Number of Reviews",
                                                    title="Top Spoken Topics",
                                                    showlegend=False,
                                                    autosize=True,
                                                    annotations=[dict(xref='paper', yref='paper',x=0.5, y=1.05,
                                                                        xanchor='center', yanchor='top',
                                                                        text=f"Total Spoken Reviews: {len(store2_df_non_null)}",
                                                                        font=dict(size=14),showarrow=False)]
                                                )
                        # Update the bar element to display the percentage text
                        fig_store2.update_traces(
                                                    texttemplate='%{text:.1f}%', textposition='outside',
                                                    hovertemplate = "<b>Topic</b>: %{x}<br>" + 
                                                                    "<b>Count</b>: %{y}<br>" + 
                                                                    "<b>Percentage</b>: %{text:.1f}%<extra></extra>"
                                                )
                        # Display the bar chart in Streamlit
                        st.plotly_chart(fig_store2,use_container_width=True)

        ###==Sentiment Analytics Expander==            
                    with st.expander("Topic wise sentiments😃😢"):                    
            ###Sentiment in each topic
                        # Initialize a list to hold the count of positive and negative sentiments for each topic
                        sentiment_counts_store2 = []
                        # Count the number of positive and negative sentiments for each topic
                        for topic in topics:
                            positive_count_store2 = (store2_df[topic] == 1).sum()
                            negative_count_store2 = (store2_df[topic] == -1).sum()
                            total_count_store2 = positive_count_store2 + negative_count_store2
                            sentiment_counts_store2.append({
                                                                'Topic': topic, 
                                                                'Positive': positive_count_store2, 
                                                                'Negative': negative_count_store2,
                                                                'Total': total_count_store2
                                                            })
                        # Create a DataFrame for visualization
                        sentiment_df_store2 = pd.DataFrame(sentiment_counts_store2)
                        # Sort the DataFrame based on the total count of reviews in descending order
                        sentiment_df_store2.sort_values('Total', ascending=False, inplace=True)
                        # Melt the DataFrame to long format for Plotly
                        sentiment_long_df_store2 = sentiment_df_store2.melt(id_vars=['Topic', 'Total'], value_vars=['Positive', 'Negative'],
                                                                                    var_name='Sentiment', value_name='Count')
                        # Calculate the percentage for each sentiment
                        sentiment_long_df_store2['Percentage'] = (sentiment_long_df_store2['Count'] / sentiment_long_df_store2['Total'] * 100).round(1)
                        # Create the horizontal (transposed) bar chart using Plotly Express
                        fig_sentiments_store2 = px.bar(
                                                            sentiment_long_df_store2,
                                                            y='Topic',
                                                            x='Count',
                                                            color='Sentiment',
                                                            color_discrete_map={'Positive': '#39CEFF', 'Negative': '#FF735D'},  # Custom colors
                                                            barmode='group',
                                                            orientation='h',  # This creates a horizontal bar chart
                                                            category_orders={"Topic": sentiment_df_store2['Topic'].tolist()},
                                                            text='Percentage'
                                                            )
                        # Update the layout for a cleaner look
                        fig_sentiments_store2.update_layout(
                                                                yaxis_title="Topics",
                                                                xaxis_title="Count of Sentiments",
                                                                title="Overview",
                                                                showlegend=True,
                                                                legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="right", x=0.9),
                                                            )
                        # Format the text on the bars to show the percentage with one decimal & Customizing hovertemplate to show one decimal place for the percentage
                        fig_sentiments_store2.update_traces(
                                                                texttemplate='%{text}%', textposition='outside',
                                                                hovertemplate="<b>Topic</b>: %{y}<br><b>Count</b>: %{x}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{text}%",customdata=sentiment_long_df_store2[['Total']].values
                                                    )
                        # Display the horizontal bar chart in Streamlit
                        st.plotly_chart(fig_sentiments_store2, use_container_width=True)
        ###==Pain Points Expander==            
                    with st.expander("Analyzing Pain Points ❌"):                            
                        # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                        negative_reviews_df_store2 = sentiment_df_store2[['Topic', 'Negative', 'Total']]
                        # Select only the relevant columns ('Topic', 'Negative', and 'Total') for the new bar chart
                        negative_reviews_df_catchment = sentiment_df_catchment[['Topic', 'Negative', 'Total']]
                        # Calculate the percentage of negative reviews
                        negative_reviews_df_catchment['Percentage'] = round(negative_reviews_df_catchment['Negative'] / negative_reviews_df_catchment['Total'] * 100,1)
                        # Sort the DataFrame based on the count of negative reviews in descending order
                        negative_reviews_df_sorted_catchment = negative_reviews_df_catchment.sort_values('Percentage', ascending=True)
                        # Calculate the percentage of negative reviews
                        negative_reviews_df_store2['Percentage'] = round(negative_reviews_df_store2['Negative'] / negative_reviews_df_store2['Total'] * 100,1)
                        # Create the bar chart using Plotly Express
                        # Align the order of topics in negative_reviews_df_store2 with the sorted order in negative_reviews_df_sorted_catchment
                        negative_reviews_df_ordered_store2 = negative_reviews_df_sorted_catchment[['Topic']].merge(negative_reviews_df_store2, on='Topic', how='left')

                        fig_negative_reviews = px.bar(
                                                        negative_reviews_df_ordered_store2,
                                                        y='Topic',
                                                        x='Percentage',
                                                        orientation='h',  # This creates a horizontal bar chart
                                                        color_discrete_sequence=['#FF735D'],
                                                        )
                        # Update the layout for a cleaner look
                        fig_negative_reviews.update_layout(
                                                            #yaxis_title="Topics",
                                                            xaxis_title="% of Negative Reviews",
                                                            title="Pain Points Spread across Topics",
                                                            showlegend=False,
                                                            )
                        # Format the hovertemplate to show the desired data
                        fig_negative_reviews.update_traces(
                                                            texttemplate='%{x}%',textposition='outside',
                                                            hovertemplate="<b>Topic</b>: %{y}<br><b>Negative Count</b>: %{customdata[1]}<br><b>Total</b>: %{customdata[0]}<br><b>Percentage</b>: %{x}%",
                                                            customdata=negative_reviews_df_ordered_store2[['Total', 'Negative']].values
                                                            )
                        # Display the bar chart in Streamlit
                        #st.plotly_chart(fig_negative_reviews, use_container_width=True)
                        sentiment_df_store2['Negative Percentage'] = sentiment_df_store2['Negative'] / sentiment_df_store2['Total'] * 100
                        Negative_sorted_store2 = sentiment_df_store2.sort_values(['Negative Percentage', 'Total'], 
                                                                                        ascending=[False, False]).reset_index(drop=True)
                        #top_5_Negative_topics_catchment = Negative_sorted_catchment.head(5)['Topic']     
                        top_5_Negative_topics_catchment = Negative_sorted_catchment['Topic']
                        # Now, for each of these top 5 topics, print the Negative Keywords separately
                        st.markdown("\n")
                        st.markdown("**Phrases**")

                        for topic in top_5_Negative_topics_catchment:
                            # Get the row from the dataframe for the current topic
                            row_store2 = sentiment_df_store2[sentiment_df_store2['Topic'] == topic]
                            # Extract the Negative and total counts for the topic
                            Negative_count_store2 = row_store2['Negative'].values[0]
                            total_count_store2 = row_store2['Total'].values[0]
                            # Filter the rows for Negative type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                            Negative_phrases_list_store2 = store2_df_keywords[(store2_df_keywords['Sentiment'] == 'negative') & (store2_df_keywords['Type'] == 'phrases')][topic].dropna().values
                            # Display the topic header
                            st.markdown(f"<h1 class='left-content-2'>{topic}: {Negative_count_store2} out of {total_count_store2} ({round((Negative_count_store2/ total_count_store2)*100,1)}%)</h1>", unsafe_allow_html=True)
                            # Container to hold the keyword boxes
                            phrase_boxes = ""
                            if Negative_phrases_list_store2.size > 0:
                            # Now, display each keyword in a separate styled box
                                phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                                phrase_counter = 0
                                for phrase_line in Negative_phrases_list_store2:    
                                    # Split the keyword phrase by comma and strip spaces
                                    phrases = phrase_line.split(',')
                                    for phrase in phrases:
                                        # Remove the numbers, colons and trim whitespace
                                        phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                        if phrase_text == "No relevant negative phrases":
                                            phrase_boxes += f"<span class='keyword-box-green'>None</span>"
                                            break
                                        if phrase_text:  # Only display if there's a keyword
                                            # Append each keyword to the container
                                            phrase_boxes += f"<span class='keyword-box-red'>{phrase_text}</span>"
                                            phrase_counter += 1
                                            # Limit the display to the first 5 keywords
                                            if phrase_counter >= 5:
                                                break
                                    if phrase_counter >= 5:
                                        break
                                phrase_boxes += "</div>"
                            else:
                                phrase_boxes += f"<span class='keyword-box-green'>None</span>"  
                            # Display the keyword boxes
                            st.markdown(phrase_boxes, unsafe_allow_html=True)                   
        ###==Delight Factors Expander==         
                    with st.expander("Delight Factors🌟"):                                      
                        sentiment_df_store2['Positive Percentage'] = sentiment_df_store2['Positive'] / sentiment_df_store2['Total'] * 100
                        positive_sorted_store2 = sentiment_df_store2.sort_values(['Positive Percentage', 'Total'], 
                                                                                        ascending=[False, False]).reset_index(drop=True)
                        #top_5_positive_topics_store2 = positive_sorted_store2.head(5)['Topic']      
                        top_5_positive_topics_store2 = positive_sorted_store2['Topic']
                        # Now, for each of these top 5 topics, print the Positive Keywords separately
                        st.markdown("\n")
                        st.markdown("**Phrases**")
                        for topic in top_5_positive_topics_store2:
                            # Get the row from the dataframe for the current topic
                            row_store2 = sentiment_df_store2[sentiment_df_store2['Topic'] == topic]
                            # Extract the positive and total counts for the topic
                            positive_count_store2 = row_store2['Positive'].values[0]
                            total_count_store2 = row_store2['Total'].values[0]
                            # Filter the rows for Positive type and extract the keywords for the current topic & Use dropna() to ignore any NaN values
                            positive_phrases_list_store2 = store2_df_keywords[(store2_df_keywords['Sentiment'] == 'Positive') & (store2_df_keywords['Type'] == 'phrases')][topic].dropna().values
                            # Display the topic header
                            st.markdown(f"<h1 class='left-content-2'>{topic}: {positive_count_store2} out of {total_count_store2} ({round((positive_count_store2/ total_count_store2)*100,1)}%)</h1>", unsafe_allow_html=True)
                            # Container to hold the keyword boxes
                            phrase_boxes = ""

                            if positive_phrases_list_store2.size > 0:
                            # Now, display each keyword in a separate styled box
                                phrase_boxes += "<div style='display: flex; flex-wrap: wrap;'>" #New Addition
                                phrase_counter = 0
                                for phrase_line in positive_phrases_list_store2:    
                                    # Split the keyword phrase by comma and strip spaces
                                    phrases = phrase_line.split(',')
                                    for phrase in phrases:
                                        # Remove the numbers, colons and trim whitespace
                                        phrase_text = ''.join([i for i in phrase if not i.isdigit() and i != ':']).strip()
                                        if phrase_text == "No relevant positive phrases":
                                            phrase_boxes += f"<span class='keyword-box-red'>None</span>"
                                            if phrase_counter >= 5:
                                                break
                                        if phrase_text:  # Only display if there's a keyword
                                            # Append each keyword to the container
                                            phrase_boxes += f"<span class='keyword-box-green'>{phrase_text}</span>"
                                            phrase_counter += 1
                                            # Limit the display to the first 5 keywords
                                            if phrase_counter >= 5:
                                                break
                                    if phrase_counter >= 5:
                                        break
                                phrase_boxes += "</div>"
                            else:
                                phrase_boxes += f"<span class='keyword-box-red'>None</span>"  
                            # Display the keyword boxes
                            st.markdown(phrase_boxes, unsafe_allow_html=True)                   
        ###==Download Sentiment Data== 
            #Get the current timestamp and format it
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            #List of columns to be selected
            selected_columns = ['Name of the Reviewer', 'Total Reviews', 'review_rating','Store Name', 
                                'Avg Rating', 'year','review_text','Customer Confidence','Store Experience',
                                'Store Staff','Product Design', 'Product Variety', 'Discount', 'Making Charge',
                                'Price', 'Jewellery Exchange']
            #Creating a new DataFrame with only the selected columns
            download_store1_df = store1_df[selected_columns]
            if selected_store2 == "None":
                download_store2_df = pd.DataFrame()
            else:
                download_store2_df = store2_df[selected_columns]
            # Create filenames with the timestamp
            file_names = [(f"catchment_data_{timestamp}.xlsx", dataframe_to_excel(download_store1_df)),
                            (f"store2_data_{timestamp}.xlsx", dataframe_to_excel(download_store2_df))]
            #Zip all the Excel files
            zip_buffer = create_zip(file_names)                                                      
            #Encode the ZIP file to base64
            zip_b64 = get_zip_base64(zip_buffer)
            # Create a download filename with the timestamp
            download_filename = f"Reviews_{timestamp}.zip"
            # Create the download link with the emoji and display it with Streamlit
            st.markdown(f'<a href="data:application/zip;base64,{zip_b64}" download="{download_filename}" class="btn btn-primary">⬇️ Download Reviews</a>', unsafe_allow_html=True)
else:
    pass