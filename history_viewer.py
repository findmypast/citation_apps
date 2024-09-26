
import pandas as pd

# streamlit
import streamlit as st

request_history_df = pd.read_pickle('./data/citation_df.pkl')

#####################
### Start of Main ###
#####################
st.title('Transcript Citation Request History')

st.dataframe(request_history_df)
