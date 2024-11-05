import streamlit as st
import glob
import pandas as pd

from datetime import datetime

import json

# local util for creds
from utils import get_creds, get_cdo_struct


#setup stuff
creds = get_creds()
cdo_struct = get_cdo_struct()
today = datetime.today()
cdo_dir = './data/training_cdo/'

if 'cdo_dict' not in st.session_state:
    st.session_state.cdo_dict = {}

### FUNCTIONS

def get_history_and_make_dict():
    cdo_list = glob.glob(cdo_dir+'*.json')
    #chat_list.sort(key=file_timestamp, reverse=True)
    #id_title_dict = {x.split('/')[-1][:-5]:'' for x in cdo_list}
    id_path_dict = {x:x.split('/')[-1][:-5] for x in cdo_list}
    return (id_path_dict)


def sb_format(opt):
    return st.session_state.id_path_dict[opt]


def read_json_file(file):
    with open(file, 'r') as openfile:
        retval = json.load(openfile)
    return retval


def proc(**kwargs):
    arg = kwargs['field']
    st.write(st.session_state.path)
    st.write(st.session_state[arg].strip('"'))
    st.session_state.cdo_past[arg] = st.session_state[arg].strip('"')
    #st.write(st.session_state[arg])
    write_json_file(st.session_state.cdo_past,path=st.session_state.path)


def write_json_file(object, path):
    json_object = json.dumps(object)
    with open(f'{path}', 'w') as outfile:
        outfile.write(json_object)


#### MAIN
st.write('### Summary of training CDOs created / in progress')
st.session_state.id_path_dict = get_history_and_make_dict()

for jp, id in st.session_state.id_path_dict.items():
    st.session_state.cdo_dict[id] = read_json_file(jp)

st.json(st.session_state.cdo_dict, expanded=False)

cdo_df_input_list = []
for k, jso in st.session_state.cdo_dict.items():
    row_tup = (k,
               jso['citationType'],
               jso['title'],
               jso['source_json']['DatasetName'],
               jso['source_json']['RecordMetadataId'],
               jso['source_json']['SourceCategory'],
               jso['source_json']['SourceCollection'],
               jso['admin_info']['sha_ok'],
               jso['admin_info']['fmp_ok'])
    cdo_df_input_list.append(row_tup)

columns = ['upp_id', 'citationType', 'title_from_CDO', 'DatasetName', 'RMID', 'SourceCategory', 'SourceCollection',
           'sha_ok', 'fmp_ok']
st.session_state.cdo_df = pd.DataFrame(cdo_df_input_list, columns=columns)

# lower case all text - to simplify grouping etc.
text_cols = columns[:-2]
for col in text_cols:
    st.session_state.cdo_df[col] = st.session_state.cdo_df[col].apply(str.lower)

st.write('### All data')
st.dataframe(st.session_state.cdo_df)

st.write('### Grouped by DatasetName')
df = (st.session_state.cdo_df.groupby('DatasetName').agg({'upp_id':'count'}))
df = df.rename(columns={'upp_id':'count_of_records'})
st.dataframe(df)

st.write('### Grouped by SourceCategory')
df = (st.session_state.cdo_df.groupby('SourceCategory').agg({'upp_id':'count'}))
df = df.rename(columns={'upp_id':'count_of_records'})
st.dataframe(df)

st.write('### Grouped by Sub-category')
df = (st.session_state.cdo_df.groupby('SourceCollection').agg({'upp_id':'count'}))
df = df.rename(columns={'upp_id':'count_of_records'})
st.dataframe(df)