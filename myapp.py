import os.path
import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout = "wide")

m3u_filepaths_file = 'playlists/streamlit.m3u8'
ESSENTIA_ANALYSIS_PATH = 'data/audio_essentia_features_5.csv'

@st.cache_data
def load_essentia_analysis():
    df = pd.read_csv(ESSENTIA_ANALYSIS_PATH, index_col = 0)
    return df

audio_analysis = load_essentia_analysis()
st.title('Essential Playlist')

# Get the list of columns header names from audio_analysis dataframe
audio_analysis_styles = audio_analysis.columns[7: -1]

# st.write('Style activation statistics:')
style_select = st.sidebar.multiselect('🔍 Genre', audio_analysis_styles)

if style_select:
    style_select_str = ', '.join(style_select)
    style_select_range = st.sidebar.slider(f'Select tracks with `{style_select_str}` activations within range:', value=[0.0, 1.0])

    index_styles_selected = audio_analysis.columns.get_indexer(style_select)
    ranked_styles =  audio_analysis.columns[index_styles_selected]
    style_rank = st.sidebar.multiselect('🔝 Rank by genre', ranked_styles, [])

    # Define minimum and maximum values for tempo slider
    min_val = round(float(audio_analysis['tempo'].min()), 2)
    max_val = round(float(audio_analysis['tempo'].max()), 2)


    #st.sidebar.write('##  Tempo in BPM')
    tempo_range_val = st.sidebar.slider('🥁 Tempo in BPM',min_val, max_val, (min_val, max_val))
    voice_instrumental = st.sidebar.radio('🎵 Choose Voice/Instrumental:', ['Voice','Instrumental'])
    danceability = st.sidebar.slider('👯 Danceability:', min_value = 0.0, max_value =  3.0, value = [0.0, 3.0])
    arousal_range = st.sidebar.slider('🔥 Arousal:', min_value = 1.0, max_value =  9.0, value = [1.0, 9.0])
    valence_range = st.sidebar.slider('🎶Valence:', min_value = 1.0, max_value =  9.0, value = [1.0, 9.0])



st.write('## 🔀 Playlist Results')
max_tracks = st.number_input('Maximum number of tracks (0 for all):', value=0)
shuffle = st.checkbox('Random shuffle')

# Run the query.
if st.sidebar.button("RUN"):
    st.write('## 🔊 Results')
    mp3s = list(audio_analysis.index)
    
    # df.loc is used for label based indexing and df.iloc is used for positional indexing
    # difference is that loc uses the index and iloc uses the position in the list
    # https://stackoverflow.com/questions/31593201/pandas-iloc-vs-ix-vs-loc-explanation
    # this explains that loc is used for labels and iloc is used for positions
    # position means the index of the row and loc is used for the name of the row
    if style_select:
        df = audio_analysis.loc[mp3s][style_select]
        for style in style_select:
            df = df.loc[df[style] >= style_select_range[0]]
        mp3s = df.index
    

    if style_rank:
        df = audio_analysis.loc[mp3s][style_rank]
        df['RANK'] = df[style_rank[0]]
        for style in style_rank[1:]:
            df['RANK'] *= df[style]
        df = df.sort_values(['RANK'], ascending=[False])
        df = df[['RANK'] + style_rank]
        mp3s = list(df.index)


    if tempo_range_val:
        df = audio_analysis.loc[mp3s]
        df = df[(df["tempo"] >= tempo_range_val[0]) & (df["tempo"] <= tempo_range_val[1])]
        mp3s = list(df.index)

    if voice_instrumental == 'Voice':
        df = audio_analysis.loc[mp3s]
        df = df[(df["voice"] >= 0.5)]
        mp3s = list(df.index)
    else:
        df = audio_analysis.loc[mp3s]
        df = df[(df["instrumental"] >= 0.5)]
        mp3s = list(df.index)

    if danceability:
        df = audio_analysis.loc[mp3s]
        df = df[(df["danceability"] >= danceability[0]) & (df["danceability"] <= danceability[1])]
        mp3s = list(df.index)
    
    if arousal_range:
        df = audio_analysis.loc[mp3s]
        df = df[(df["arousal"] >= arousal_range[0]) & (df["arousal"] <= arousal_range[1])]
        mp3s = list(df.index)

    if valence_range:
        df = audio_analysis.loc[mp3s]
        df = df[(df["valence"] >= valence_range[0]) & (df["valence"] <= valence_range[1])]
        mp3s = list(df.index)

    if max_tracks:
        mp3s = mp3s[:max_tracks]
        st.write('Using top', len(mp3s), 'tracks from the results.')
    
    if shuffle:
        random.shuffle(mp3s)

    # Create a playlist folder.
    with open(m3u_filepaths_file, 'w') as f:
        # Modify relative mp3 paths to make them accessible from the playlist folder.
        try:
            mp3_paths = [os.path.join('..', mp3) for mp3 in mp3s]
            f.write('\n'.join(mp3_paths))
        except Exception as e:
            print('err', e)
    
    st.write('Audio previews for the first 10 results:')
    if len(mp3s) > 0:
        for mp3 in mp3s[:10]:
            st.audio(mp3, format="audio/mp3", start_time=0)
    else:
        st.write('## Oops! Looks like there are no songs for your filters! Try again with different options may be?')