import streamlit as st
# import libraries & setup

import numpy as np
import pandas as pd

from urllib.request import urlopen
import urllib.parse
import json
import pickle
import re

import requests

sample_base = 12


### SESSION STATE VARs ###
if 'url_input_sample' not in st.session_state:
    st.session_state.url_input_sample = ''

if 'results_url' not in st.session_state:
    st.session_state.results_url = ''
    st.session_state.disable_generate = False

if 'sample_text' not in st.session_state:
    st.session_state.sample_text = sample_base

if 'text_name' not in st.session_state:
    st.session_state.text_name = ''
    st.session_state.sample_link_dict = {}

if 'random_key' not in st.session_state:
    st.session_state.random_key = np.random.randint(1, 999999)

if 'show_samples' not in st.session_state:
    st.session_state.show_samples = False

if 'sample_set' not in st.session_state:
    st.session_state.sample_set = ''

if 'solr_query' not in st.session_state:
    st.session_state.solr_query = ''

if 'unencoded_name' not in st.session_state:
    st.session_state.unencoded_name = ''

if 'encoded_name' not in st.session_state:
    st.session_state.encoded_name = ''

if 'sample_link_dict' not in st.session_state:
    st.session_state.sample_link_dict = {}


### FUNCTIONS ###
def submit():
    st.session_state.results_url = st.session_state['url_input_sample']
    st.session_state.url_input_sample = ''
    st.session_state.unencoded_name = get_dataset_name(st.session_state.results_url)
    st.session_state.encoded_name = get_encoded_dataset_name(st.session_state.unencoded_name)
    st.session_state.disable_generate = False


def gen_sample_submit():
    st.session_state.show_samples = True
    st.session_state.random_key = np.random.randint(1, 999999)
    st.session_state.solr_query = get_solr_query(st.session_state.encoded_name,
                                                 rows=st.session_state.sample_size,
                                                 key=st.session_state.random_key)
    st.session_state.sample_set = get_samples(st.session_state.solr_query)
    st.session_state.disable_generate = True
    st.session_state.sample_text = st.session_state.sample_size
    st.session_state.text_name = st.session_state.unencoded_name


def sample_size_submit():
    st.session_state.disable_generate = False


def get_dataset_name(url_in):
    patt = "datasetname=(\S+)&"  # ignore syntax warning
    retval = re.search(patt, url_in).group(1)
    retval = urllib.parse.unquote(retval)
    retval = retval.replace('+', ' ')
    return retval


def get_encoded_dataset_name(name_in):
    if name_in[0].isdigit():
        retval = '2_' + name_in
    else:
        retval = '1_' + name_in

    retval = (urllib.parse.quote(retval, safe='()')
              .replace('%20', "\\%20")
              .replace('(', "\\(")
              .replace(')', "\\)"))
    return retval


def get_solr_query(dname, rows=2, key=789):
    retval = f"http://sapi.dun.fh/solr/select?json.nl=map&wt=json&sort=random_{key}%20asc&rows={rows}&fq=DatasetName__facet_text_ordered:{dname}"
    return retval


def get_samples(q):
    response = requests.get(q)
    create_sample_link_dict(response.json())


def create_sample_link_dict(json):
    st.session_state.sample_link_dict = {}
    for s in json['response']['docs']:
        id = s['Id'].replace('/', '%2F')
        url = f"https://www.findmypast.co.uk/transcript?id={id}&tab=this"
        st.session_state.sample_link_dict[id] = url



#### MAIN
st.write('### Generation of random transcript(s) sample from a dataset')

with st.sidebar:
    st.markdown("""
    ###
    ##### If you want some random transcript samples - enter the *RESULTS PAGE* URL below
    """)
    st.text_input("Results URL", key='url_input_sample', on_change=submit)
    st.write(f'Last Results URL provided:')
    st.write(f'{st.session_state.results_url}')
    st.number_input("Number of samples wanted",
                    min_value=1, max_value=50,
                    value=sample_base, step=1,
                    key='sample_size',
                    on_change=sample_size_submit)


    st.write(st.session_state.encoded_name)
    st.write(st.session_state.solr_query)

    generate_sample = st.button('Generate a random sample of transcripts',
                                type='primary',
                                key='generate_sample',
                                disabled=st.session_state.disable_generate,
                                on_click=gen_sample_submit)


if st.session_state.show_samples == True:
    st.write(f'Here are {st.session_state.sample_text} samples from: {st.session_state.text_name}')

    get_samples(st.session_state.solr_query)

    for v in st.session_state.sample_link_dict.values():
        st.write(v)





