import streamlit as st
import pandas as pd
import plotly.express as px

def plot_object_count(df):
    """
    Create a plot tracking the object count over time.
    """
    fig = px.line(df, x='date', y='object_count', title='Object Count Over Time', markers=True)
    fig.update_layout(xaxis_title='Date', yaxis_title='Object Count')
    return fig
