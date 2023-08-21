import pandas as pd
import re
import streamlit as st
import plotly.express as px
from pandas.api.types import CategoricalDtype
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from appStructure import WebApp

user = WebApp()
user.run()
