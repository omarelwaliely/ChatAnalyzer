import pandas as pd
import re
import streamlit as st
import plotly.express as px
from pandas.api.types import CategoricalDtype
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io
from io import StringIO

class WebApp():
    def __init__(self):
        self.hist = pd.DataFrame()
        self.cloud = {}

    def toDF(self,path):
        hist = pd.DataFrame()
        pattern = r"^\[\d{1,2}\/\d{1,2}\/\d{2,4}, \d{1,2}:\d{1,2}:\d{1,2} (?:AM|PM)\] .+$"
        messages = []
        with open(path,'r', encoding='utf-8') as chat:
            special = chat.read()
            specialrem = re.sub('\u200E+', '', special)
            messages = re.findall(pattern, specialrem, re.MULTILINE)
        histrows = []
        for message in messages:
            newpattern = r"^\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{1,2}:\d{1,2} [AP]M)\] (.+?): (.+)$"
            match = re.match(newpattern, message)
            if match:
                date = match.group(1)
                time = match.group(2)
                name = match.group(3)
                text = match.group(4)
                histrows.append({'Date': date, 'Time': time, 'Name': name, 'Text': text})
            else:
                print(f"No match found for{message}")
        hist = pd.DataFrame.from_records(histrows)
        return hist
    def StringtoDF(self,chat):
        hist = pd.DataFrame()
        pattern = r"^\[\d{1,2}\/\d{1,2}\/\d{2,4}, \d{1,2}:\d{1,2}:\d{1,2} (?:AM|PM)\] .+$"
        messages = []
        special = chat.read()
        specialrem = re.sub('\u200E+', '', special)
        messages = re.findall(pattern, specialrem, re.MULTILINE)
        histrows = []
        for message in messages:
            newpattern = r"^\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{1,2}:\d{1,2} [AP]M)\] (.+?): (.+)$"
            match = re.match(newpattern, message)
            if match:
                date = match.group(1)
                time = match.group(2)
                name = match.group(3)
                text = match.group(4)
                histrows.append({'Date': date, 'Time': time, 'Name': name, 'Text': text})
            else:
                print(f"No match found for{message}")
        hist = pd.DataFrame.from_records(histrows)
        return hist
    def download(self):
        file = self.hist.to_csv(index = False).encode('utf-8')
        st.download_button(
        label="Download data as CSV",
        data=file,
        file_name='chats.csv',
        mime='text/csv',
        key = "csvfile")
    def download_wordcloud(self):
        wordcloud = WordCloud()
        w = wordcloud.generate_from_frequencies(frequencies=self.cloud)
        _ , ax = plt.subplots(figsize=(16, 16))
        ax.imshow(w, interpolation="bilinear")
        ax.axis("off")
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close()
        st.download_button(
            label="Download WordCloud",
            data=img_bytes.getvalue(),
            file_name=f"wordcloud.png",
            mime='image/png',
            key="wordcloud"
        )

    def findMedia(self,textCell):
        if 'sticker omitted' in textCell:
            return "Sticker"
        elif 'image omitted' in textCell:
            return "Image"
        elif "video omitted" in textCell:
            return "Video"
        elif "document omitted" in textCell:
            return "Document"
        elif "audio omitted" in textCell:
            return "Audio"
        elif "Contact card omitted" in textCell:
            return "Contact Card"
        elif "GIF omitted" in textCell:
            return "GIF"
        return None

    def usefulAddons(self):
        self.hist.reset_index(inplace = True)
        self.hist = self.hist[pd.to_datetime(self.hist['Date'], format='%m/%d/%y', errors='coerce').notnull()]
        self.hist = self.hist[pd.to_datetime(self.hist['Time'], format='%I:%M:%S %p', errors='coerce').notnull()]
        self.hist['Date'] = pd.to_datetime(self.hist['Date'], format='%m/%d/%y')
        bounds = pd.date_range(start=self.hist['Date'].min(), end=self.hist['Date'].max(), freq='MS')
        self.allmonths = pd.DataFrame({'Date': bounds})
        self.hist['Time'] = pd.to_datetime(self.hist['Time'], format='%I:%M:%S %p')
        self.hist['Year'] = self.hist['Date'].dt.year
        self.allyears = list(range(self.hist['Year'].min(), self.hist['Year'].max() + 1))
        self.hist['Month'] = self.hist['Date'].dt.month
        self.hist['YearMonth'] = self.hist['Month'].astype(str) + '/' + self.hist['Year'].astype(str)
        self.hist['Day'] = self.hist['Date'].dt.day
        self.hist['Hour'] = self.hist['Time'].dt.hour
        self.hist['CalenderDay'] = self.hist['Date'].dt.day_name()
        self.hist['Media'] = self.hist['Text'].apply(self.findMedia)
        self.hist['Words'] = self.hist['Text'].apply(lambda x: len(x.split()))
        self.hist.loc[self.hist['Media'].notnull(), 'Words'] = 0
        self.noMedia = self.hist[self.hist['Media'].isnull()]

        self.cloud.clear()
        for text in self.noMedia['Text']:
            if text != 'This message was deleted.':
                for word in text.split():
                    word = re.sub(r'[^\w\s]', '', word)
                    word = word.lower()
                    if not word in STOPWORDS:
                        if not word in self.cloud:
                            self.cloud[word] = 1
                        else:
                            self.cloud[word] = self.cloud[word] + 1
        return self.hist
    
    def searchWord(self,search):
        count = 0
        for text in self.noMedia['Text']:
            for word in text.split():
                word = re.sub(r'[^\w\s]', '', word)
                word = word.lower()
                if word == search.lower():
                    count+=1
        return count
    def wordSearchModule(self):
        userWord = st.text_input(
        "Input a word to see how many times it was said:",
        key="wordsearch")
        if userWord:
            st.write(self.searchWord(userWord))

    def messagesOverTime(self):
        chart = st.empty()
        option = st.selectbox('Select View',('Monthly', 'Yearly'), key = 'messagetime')
        if option == 'Yearly':
           chart.plotly_chart(self.messagesPerYear(),use_container_width=True)
        else:
           chart.plotly_chart(self.messagesPerMonth(),use_container_width=True)

    def wordsOverTime(self):
        chart = st.empty()
        option = st.selectbox('Select View',('Monthly', 'Yearly'),key = 'wordtime')
        if option == 'Yearly':
            chart.plotly_chart(self.wordsPerYear(), use_container_width=True)
        else:
            chart.plotly_chart(self.wordsPerMonth(),use_container_width=True)

    def displayMediaUsage(self):
        mediaOpt = list(self.hist['Media'].unique())
        del mediaOpt[0]
        chart = st.empty()
        mediaOpt.append('ALL OF THE ABOVE')
        option = st.selectbox('Select View',mediaOpt,key = 'mediatime')
        if option== 'ALL OF THE ABOVE':
            chatDistribution = self.hist[self.hist['Media'].notnull()].groupby('Date')["Text"].count().reset_index()
            chatDistribution = pd.merge(self.allmonths, chatDistribution, on='Date', how='left').fillna(0)
            fig = px.line(chatDistribution, x='Date', y='Text', labels={ "Date" : "Date", "Text" : "Number of Media"},title='Number of Media')
            fig.update_traces(line=dict(color='magenta'))
            chart.plotly_chart(fig,use_container_width=True)
        else:
            chatDistribution = self.hist[self.hist['Media']== option].groupby('Date')["Text"].count().reset_index()
            chatDistribution = pd.merge(self.allmonths, chatDistribution, on='Date', how='left').fillna(0)
            fig = px.line(chatDistribution, x='Date', y='Text', labels={ "Date" : "Date", "Text" : f"Number of {option}s"},title=f'Number of {option}s')
            fig.update_traces(line=dict(color='magenta'))
            chart.plotly_chart(fig,use_container_width=True)

    def timeHeatMap(self):
        order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday']
        cat_type = CategoricalDtype(categories=order, ordered=True)
        chatDistribution = self.hist.copy()
        chatDistribution['CalenderDay'] = chatDistribution['CalenderDay'].astype(cat_type)
        chatDistribution = chatDistribution.groupby(['CalenderDay','Hour'])["Text"].count().reset_index()
        fig = px.density_heatmap(chatDistribution, x="CalenderDay", y="Hour", z="Text",nbinsx = 7, nbinsy = 24, color_continuous_scale = 'Reds',labels={"Hour" : "Time" , "CalenderDay": "Day",} ,title='Day-Time Heat Map', height = 800, width = 800)
        fig.update_layout(coloraxis_colorbar_title_text = 'Texts')
        st.plotly_chart(fig,use_container_width=True)

    def messagesPerYear(self):
        chatDistribution = self.hist.groupby('Year')["Text"].count().reset_index()
        chatDistribution = pd.merge(pd.DataFrame({'Year': self.allyears}), chatDistribution, on='Year', how='left').fillna(0)
        fig = px.line(chatDistribution, x='Year', y='Text', labels={ "Year" : "Year", "Text" : "Number of Texts"},title='Number of Texts Per Year')
        return fig

    def messagesPerMonth(self):
        chatDistribution = self.hist.groupby('Date')["Text"].count().reset_index()
        chatDistribution = pd.merge(self.allmonths, chatDistribution, on='Date', how='left').fillna(0)
        fig = px.line(chatDistribution, x='Date', y='Text', labels={ "Date" : "Date", "Text" : "Number of Texts"},title='Number of Texts Per Month')
        return fig
    
    def messagesPerPerson(self):
        amountoftexts = self.hist.groupby('Name')["Text"].count().reset_index()
        atextsgraph = px.bar(amountoftexts, x='Name', y='Text', labels={"Text" : "Number of Texts"},title='Messages per Person',color = 'Name')
        return st.plotly_chart(atextsgraph,use_container_width=True)

    def wordsPerYear(self):
        chatDistribution = self.hist.groupby('Year')["Words"].sum().reset_index()
        chatDistribution = pd.merge(pd.DataFrame({'Year': self.allyears}), chatDistribution, on='Year', how='left').fillna(0)
        fig = px.line(chatDistribution, x='Year', y='Words', labels={ "Year" : "Year", "Words" : "Number of Words"},title='Number of Words Per Year')
        return fig

    def wordsPerMonth(self):
        chatDistribution = self.hist.groupby('Date')["Words"].sum().reset_index()
        chatDistribution = pd.merge(self.allmonths, chatDistribution, on='Date', how='left').fillna(0)
        fig = px.line(chatDistribution, x='Date', y='Words', labels={ "Date" : "Date", "Words" : "Number of Words"},title='Number of Words Per Month')
        return fig

    def wordsPerPerson(self):
        amountoftexts = self.hist.groupby('Name')["Words"].sum().reset_index()
        atextsgraph = px.bar(amountoftexts, x='Name', y='Words', labels={"Words" : "Number of Words"},title='Words per Person',color = 'Name')
        st.plotly_chart(atextsgraph,use_container_width=True)

    def selectDate(self):
        self.startDate = st.date_input('Select Start Date', self.hist['Date'].iloc[0])
        self.endDate = st.date_input('Select End Date', self.hist['Date'].iloc[-1])
        self.hist = self.hist[self.hist['Date'].between(pd.to_datetime(self.startDate),pd.to_datetime(self.endDate))]
        
    def selectPeople(self):
        people = self.hist['Name'].unique()
        options = st.multiselect('Select the users you want to include:',people , people,key = 'people')
        self.hist = self.hist[self.hist['Name'].isin(options)]
        
    def run_demo(self):
        st.set_page_config(page_title="Demo", page_icon="🌟",layout="wide")
        self.hist = self.toDF("chat.txt")
        self.usefulAddons()
        csvCol, cloudCol = st.columns(2,gap = "large")
        with csvCol:
            self.download()
        with cloudCol:
            self.download_wordcloud()
        self.selectPeople()
        try:
            self.selectDate()
            mesCol, wordCol = st.columns(2,gap = "large")
            with st.container():
                with mesCol:
                    self.messagesPerPerson()
                    self.messagesOverTime()
                with wordCol:
                    self.wordsPerPerson()
                    self.wordsOverTime()
            self.displayMediaUsage()
            self.timeHeatMap()
            self.wordSearchModule()
        except:
            st.error("Please Input At Least One Name, and a Valid Date Range")
    def run(self):
        st.set_page_config(page_title="Demo", page_icon="🌟",layout="wide")
        uploaded_file = st.file_uploader("Upload the Chat", key = "userfile")
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            stringio = StringIO(bytes_data.decode("utf-8"))
            self.hist = self.StringtoDF(stringio)
            self.usefulAddons()
            csvCol, cloudCol = st.columns(2,gap = "large")
            with csvCol:
                self.download()
            with cloudCol:
                self.download_wordcloud()
            self.selectPeople()
            try:
                self.selectDate()
                mesCol, wordCol = st.columns(2,gap = "large")
                with st.container():
                    with mesCol:
                        self.messagesPerPerson()
                        self.messagesOverTime()
                    with wordCol:
                        self.wordsPerPerson()
                        self.wordsOverTime()
                self.displayMediaUsage()
                self.timeHeatMap()
                self.wordSearchModule()
            except:
                st.error("Please Input At Least One Name, and a Valid Date Range")