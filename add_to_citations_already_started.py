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


if 'cdo' not in st.session_state:
    st.session_state.cdo = {}


if "cdo_past" not in st.session_state:
    st.session_state.messages_past = []


if 'path' not in st.session_state:
    st.session_state.path = ''

cdo_dir = './data/training_cdo/'



### FUNCTIONS

def get_history_and_make_dict():
    cdo_list = glob.glob(cdo_dir+'*.json')
    #chat_list.sort(key=file_timestamp, reverse=True)
    #id_title_dict = {x.split('/')[-1][:-5]:'' for x in cdo_list}
    id_path_dict = {x:x.split('/')[-1][:-5] for x in cdo_list}
    id_admin_dict = {}
    for k in id_path_dict.keys():
        try:
            js = read_json_file(k)
            id_admin_dict[k] = js['admin_info']
        except:
            id_admin_dict[k] = {}
    return (id_path_dict, id_admin_dict)


def sb_format(opt):
    return st.session_state.id_path_dict[opt]


def read_json_file(file):
    with open(file, 'r') as openfile:
        retval = json.load(openfile)
    return retval


def proc(**kwargs):
    arg = kwargs['field']
    st.write(st.session_state[arg].strip('"'))
    st.session_state.cdo_past[arg] = st.session_state[arg].strip('"')
    write_json_file(st.session_state.cdo_past, path=st.session_state.path)


def proc_ok(**kwargs):
    st.session_state.cdo_past["admin_info"][kwargs['approve']] = st.session_state[kwargs['approve']]
    write_json_file(st.session_state.cdo_past, path=st.session_state.path)
    #st.session_state.approval_filter = 0. not sure this helped....
    return


def get_options_list(filter):
    retval = []
    if filter == 0:
        retval = list(st.session_state.id_path_dict.keys())
        return retval
    for k,v in st.session_state.id_admin_dict.items():
        if filter == 1:
            if (not v['sha_ok']) and not (v['fmp_ok']):
                retval.append(k)
        if filter == 2:
            if (v['sha_ok']) and not (v['fmp_ok']):
                retval.append(k)
        if filter == 3:
            if (not v['sha_ok']) and (v['fmp_ok']):
                retval.append(k)
        if filter == 4:
            if (v['sha_ok']) and (v['fmp_ok']):
                retval.append(k)
    return retval


def write_json_file(object, path):
    json_object = json.dumps(object)
    with open(f'{path}', 'w') as outfile:
        outfile.write(json_object)


### MAIN
st.write('### WIP - Transcript Citation - Training entry amendment')
st.session_state.id_path_dict,  st.session_state.id_admin_dict = get_history_and_make_dict()
#st.json(st.session_state.id_path_dict)
#st.json(st.session_state.id_admin_dict)

with st.sidebar:
    st.write('### Review past CDOs')

    label = 'What approval status CDOs do you want to look at?'
    options = {0:'All', 1:'No approval',  2:'SHA approved (not FMP approved)', 3:'FMP approved (not SHA approved)', 4:'Approved by both'}
    st.selectbox(label, options, key='approval_filter', index=0, format_func=lambda x: options[x])
    #st.write(st.session_state.approval_filter)

    label = 'Select a past CDO'
    options = get_options_list(st.session_state.approval_filter)
    #options = list(st.session_state.id_path_dict.keys())
    cdo_selection = st.selectbox(label, options, index=None, format_func=sb_format)

    if cdo_selection:
        st.session_state.cdo_past = read_json_file(cdo_selection)
        st.session_state.path = cdo_selection
        st.write(st.session_state.id_path_dict[st.session_state.path])
        st.write(f'Transcript URL provided:')
        #url = st.session_state.cdo_past['source_json']['fmp_link']
        st.write(f"{st.session_state.cdo_past['source_json']['fmp_link']}")


        st.write(st.session_state.cdo_past )

if cdo_selection:
    id = st.session_state.cdo_past['source_json']['Id']
    st.write(f"#### Amend training CDO for {st.session_state.cdo_past['source_json']['Id']}")
    st.markdown("*(expand the json below to see the CDO as it stands)*")

    #put the CDO (WIP)at the top of the page
    st.json(st.session_state.cdo_past, expanded=False)


    for k,v in cdo_struct.items():
    #    st.write(k,v)
        if  k in st.session_state.cdo_past.keys():
            placeholder = st.session_state.cdo_past[k]
        else:
            placeholder = v

        if k == 'citationType':
            st.selectbox(k, options=['Primary', 'Secondary'], index=0, key=k,
                            on_change=proc, kwargs={'field':k}, help='tooltip')
            try:
                st.write(f":orange[{st.session_state.cdo_past[k]}]")
            except:
                pass
        else:
            st.text_input(k, placeholder=placeholder, key=k, on_change=proc,
                                            kwargs={'field':k}, help='tooltip')
            try:
                text = st.session_state.cdo_past[k]
                st.write(f":orange[{st.session_state.cdo_past[k]}]")
            except:
                pass

    st.write('#### Approval / completion of training data CDO')
    st.checkbox('Complete for SHA purposes', key='sha_ok', on_change=proc_ok,
                                    value=st.session_state.cdo_past['admin_info']['sha_ok'],
                                    kwargs={'approve':'sha_ok'})
    st.checkbox('Complete for FMP purposes', key='fmp_ok', on_change=proc_ok,
                                    value=st.session_state.cdo_past['admin_info']['fmp_ok'],
                                    kwargs={'approve': 'fmp_ok'})