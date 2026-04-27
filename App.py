#Purpose:
# This module implements an interactive NBA analytics dashboard using Streamlit.
# It allows users to explore player performance through data visualization,
# compare multiple players, and generate probability-based predictions using
# historical game statistics. The application serves as the presentation layer
# of the ETL pipeline, transforming stored data into meaningful insights. 
#Sprint: 3
#To run use: python -m streamlit run App.py 

# This application still follows a pipeline (pipe-and-filter) architecture,
# where data flows through distinct stages: extraction, transformation,
# storage, and visualization. This part focuses on the visualization aspect allowing
# the user to access the data collected in a meaningful way.
# Based on:
# https://medium.com/@mohamedsallam953/fundamental-of-software-architecture-chapter-11-pipeline-architecture-style-53e8bedefe14


#Used Streamlit Documentation
#https://docs.streamlit.io/

import streamlit as st
import sqlite3
import pandas as pd


st.set_page_config(page_title="NBA Analytics Dashboard")

st.title("NBA Analytics Dashboard")

st.markdown("Use the sidebar to navigate between pages.")



# This application is deployed to a cloud environment to improve accessibility,
# scalability, and reliability. Cloud deployment allows the system to be accessed
# from any device without requiring local setup, while also enabling centralized
# hosting of the application and data services.
# The deployment is implemented using Microsoft Azure App Service, which provides
# managed hosting for Python-based web applications.
# Based on:
# https://learn.microsoft.com/en-us/azure/app-service/overview




