## NB -

# pandas
import pandas as pd  # don't need?

# streamlit
import streamlit as st
from datetime import datetime

import json
import requests
#import glob

# local util for creds
from utils import get_creds, get_cdo_struct

#setup stuff
creds = get_creds()
cdo_struct = get_cdo_struct()
today = datetime.today()


if 'transcript_url' not in st.session_state:
    st.session_state.transcript_url = ''

if 'url_input' not in st.session_state:
    st.session_state.url_input = ''

if 'cdo' not in st.session_state:
    st.session_state.cdo = {}

if 'filename' not in st.session_state:
    st.session_state.filename = ''

#st.write(st.session_state.prompt_text_user)

### FUNCTIONS

st.cache_data()
def get_clip_data(sapi_url):
    response = requests.get(sapi_url)
    response_text = response.content.decode('utf-8')
    info = json.loads(response_text)
    return info


st.cache_data()
def get_sapi_url(transcript_url):
    upp_id = transcript_url.split('?id=')[-1].split('&')[0]
    retval_url = f'http://sapi.dun.fh/v6.4.0/records/recordsinglewithsiteconfig/false/false/true/{upp_id}?consumingSiteId=FMP_UK_FULL'
    retval = (upp_id, retval_url)
    return retval


def submit():
    st.session_state['transcript_url'] = st.session_state['url_input']
    st.session_state.url_input = ''
    st.session_state.cdo = {}
    for k in cdo_struct.keys():
        if k != 'citationType':
            st.session_state[k] = ''


def proc(**kwargs):
    arg = kwargs['field']
    st.session_state.cdo[arg] = st.session_state[arg].strip('"')
    st.write(st.session_state[arg])
    write_json_file(st.session_state.cdo, filename=st.session_state.filename)


def proc_ok(**kwargs):
    st.write(st.session_state[kwargs['approve']])
    st.session_state.cdo["admin_info"][kwargs['approve']] = st.session_state[kwargs['approve']]
    write_json_file(st.session_state.cdo, filename=st.session_state.filename)
    return


def get_filename(td):
    retval = td['Id'].replace('/','_')
    return retval


def write_json_file(object, filename='testfile', path='./data/training_cdo/'):
    json_object = json.dumps(object)
    with open(f'{path}{filename}.json', 'w') as outfile:
        outfile.write(json_object)



def set_initial_knowns():
    #set the direct matches in CDO - for now
    if "URL" not in st.session_state.cdo.keys():
        st.session_state.cdo["URL"] = transcript_ref_dict['fmp_link']
        st.session_state.url =  st.session_state.cdo["URL"]

    if 'title' not in st.session_state.cdo.keys():
        st.session_state.cdo["title"] = transcript_ref_dict['DatasetName']
        st.session_state["title"] = st.session_state.cdo["title"]

    if 'lastName' not in st.session_state.cdo.keys():
        try:
            st.session_state.cdo["lastName"] = transcript_ref_dict['sapi_info']['d']['results'][0]['LastName']
            st.session_state["lastName"] = st.session_state.cdo["lastName"]
        except:
            pass

    if 'firstName' not in st.session_state.cdo.keys():
        try:
            st.session_state.cdo["firstName"] = transcript_ref_dict['sapi_info']['d']['results'][0]['FirstName']
            st.session_state["firstName"] = st.session_state.cdo["firstName"]
        except:
            pass


    if 'eventYear' not in st.session_state.cdo.keys():
        try:
            st.session_state.cdo["eventYear"] = str(transcript_ref_dict['sapi_info']['d']['results'][0]['EventYear'])
            st.session_state["eventYear"] = st.session_state.cdo["eventYear"]
        except:
            pass

    if 'birthYear' not in st.session_state.cdo.keys():
        try:
            st.session_state.cdo["birthYear"] = str(transcript_ref_dict['sapi_info']['d']['results'][0]['YearOfBirth'])
            st.session_state["birthYear"] = st.session_state.cdo["birthYear"]
        except:
            pass

    if 'admin_info' not in st.session_state.cdo.keys():
        try:
            st.session_state.cdo["admin_info"] = {'sha_ok':False, 'fmp_ok':False}
        except:
            pass

    return



#####################
### Start of Main ###
#####################
st.write('### WIP - Transcript Citation - Training entry creation')

with st.sidebar:
    st.markdown("""
    ###
    ##### If you want to create a new citation - enter the transcript URL below
    """)
    st.text_input("Transcript URL", key='url_input', on_change=submit)
    st.write(f'Last Transcript URL provided:')
    st.write(f'{st.session_state.transcript_url}')

    if st.session_state.transcript_url:
        upp_id, sapi_url = get_sapi_url(st.session_state.transcript_url)

        sapi_info = (get_clip_data(sapi_url))
        #citation_prompt = prompt.format(today, st.session_state.transcript_url, sapi_info)
        #st.write(f"upp_id: {upp_id.replace('%2F', '/')}")
        transcript_ref_dict = {'Id':upp_id.replace('%2F', '/'), 'fmp_link':st.session_state.transcript_url}
        fields = ['DatasetName', 'RecordMetadataId', 'SourceCategory', 'SourceCollection']
        for field in fields:
            transcript_ref_dict[field] = sapi_info['d']['results'][0][field]
            #st.write(f"{field}: {sapi_info['d']['results'][0][field]}")

        transcript_ref_dict['sapi_info'] = sapi_info
        st.write('Transcript information and full retrieved json:')
        st.json(transcript_ref_dict, expanded=True)
        st.session_state.cdo['source_json'] = transcript_ref_dict
        st.session_state.filename = get_filename(transcript_ref_dict)


        st.markdown("""
        ##
        ##### Transcript upp_id and SAPI information link:""")
        st.write(upp_id, sapi_url)



#show_clipping = st.button('Show Clipping image', key='show_clip_image')
if st.session_state.transcript_url:
    st.write(f"#### Create training CDO for {transcript_ref_dict['Id']}")
    st.markdown("*(expand the json below to see the CDO as it stands)*")

    #set the direct matches in CDO - for now
    set_initial_knowns()


    # default citation type
    if "citationType" not in st.session_state.cdo.keys():
        st.session_state.cdo["citationType"] = 'Primary'



    #put the CDO (WIP)at the top of the page
    st.json(st.session_state.cdo, expanded=False)

    try:
        st.write(st.session_state['citationType'])
    except:
        pass


    for k,v in cdo_struct.items():

        if k not in st.session_state.cdo.keys():
            st.session_state.cdo[k] = ''
            st.session_state[k] = ''

        if k == 'citationType':
            st.selectbox(k, options=['Primary', 'Secondary'], index=0, key=k,
                            on_change=proc, kwargs={'field':k}, help='tooltip')
            try:
                st.write(f":orange[{st.session_state.cdo[k]}]")
            except:
                pass
        else:
            if st.session_state.cdo[k] == '':
                #st.write('empty session state k')
                st.text_input(k, placeholder=v, key=k, on_change=proc,
                                            kwargs={'field':k}, help='tooltip')
            else:
                #st.write('populated session state k')
                #st.write(st.session_state.cdo[k])
                #st.write(st.session_state[k])
                st.text_input(k, key=k, on_change=proc, value=st.session_state.cdo[k],
                              kwargs={'field': k}, help='tooltip')
            try:
                text = st.session_state.cdo[k]
                st.write(f":orange[{st.session_state.cdo[k]}]")
            except:
                pass

    st.write('#### Approval / completion of training data CDO')
    st.checkbox('Complete for SHA purposes', key='sha_ok', on_change=proc_ok,
                                    kwargs={'approve':'sha_ok'})
    st.checkbox('Complete for FMP purposes', key='fmp_ok', on_change=proc_ok,
                                    kwargs={'approve': 'fmp_ok'})