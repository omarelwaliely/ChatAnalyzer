import pandas as pd
import re
import streamlit as st
import plotly.express as px
from pandas.api.types import CategoricalDtype
from wordcloud import WordCloud, STOPWORDS
from appStructure import WebApp

demo = WebApp()
demo.run_demo()