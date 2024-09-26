## NB - largely cannibalised (in haste) from the clipping description app. Hence some odd naming conventions etc.

import pandas as pd

# streamlit
import streamlit as st
import html
import markdown
from datetime import datetime

# for scrape
import requests
import json
#from bs4 import BeautifulSoup
from collections import namedtuple

#for OpenAI
from openai import OpenAI

# local util for creds
from utils import get_creds



#setup stuff
creds = get_creds()

ai_key = creds['openai_key_citapp']
client = OpenAI(api_key=ai_key)

today = datetime.today()

if 'transcript_url' not in st.session_state:
    st.session_state.transcript_url = ''

if 'url_input' not in st.session_state:
    st.session_state.url_input = ''

if 'prompt_text_user' not in st.session_state:
    st.session_state.prompt_text_user = ''

if 'prompt_input' not in st.session_state:
    st.session_state.prompt_input = ''


df_cols = ['timestamp', 'Id','fmp_link', 'DatasetName', 'RecordMetadataId', 'SourceCategory', 'SourceCollection', 'sapi_info', 'prompt', 'response_content', 'model', 'usage', 'cost_text']

if 'citation_df' not in st.session_state:
    try:
        st.session_state.citation_df = pd.read_pickle('./data/citation_df.pkl')
        df_save_name = './data/citation_df.pkl'
        st.session_state.citation_df.to_pickle(df_save_name)
    except:
        #for first time only or exception handling
        st.session_state.citation_df = pd.DataFrame(columns=df_cols)
        df_save_name = './data/new_citation_df.pkl'
        st.session_state.citation_df.to_pickle(df_save_name)
else:
    df_save_name = './data/citation_df.pkl'


st.write(st.session_state.prompt_text_user)

#functions

#scrape URL for title
st.cache_data()
def get_clip_data(sapi_url):
    response = requests.get(sapi_url)
    response_text = response.content.decode('utf-8')
    info = json.loads(response_text)
    return info


prompt_text = """
        Attached below is a json structured data object for a historical record transcription.
        Can you format and create a citation to academic structure and standards for this document?
        The reponse should include 3 different academic citation formats, and each citation should include
        the fullest possible reference data,
        including any repository or archive series data and reference numbers.
        In addition, can you also add a genealogy style citation - as described by Elizabeth Shown Mills,
         in "Evidence Explained: Citing History Sources from Artifacts to Cyberspace"
        """


prompt_data = """
        The access date should be {}.
        The reference URL should be {}
        The json object for the record transcription is {}
        """

prompt = prompt_text+prompt_data

#model = "gpt-4o"
model = "gpt-4o-mini"

st.cache_data()
def call_chatgpt_for_citation(p, model=model):
    messages = [{"role": "user",
                 "content": p}]

    retval = client.chat.completions.create(model=model, messages=messages,
                                            max_tokens=4000, timeout=300)
    return retval


st.cache_data()
def get_sapi_url(transcript_url):
    upp_id = transcript_url.split('?id=')[-1].split('&')[0]
    retval_url = f'http://sapi.dun.fh/v6.4.0/records/recordsinglewithsiteconfig/false/false/true/{upp_id}?consumingSiteId=FMP_UK_FULL'
    retval = (upp_id, retval_url)
    return retval


def submit():
    st.session_state['transcript_url'] = st.session_state['url_input']
    st.session_state.url_input = ''


def text_submit():
    st.session_state['prompt_text_user'] = st.session_state['prompt_input']
    #st.text(st.session_state.prompt_text_user)
    st.session_state.prompt_input = ''


st.cache_data()
def get_cost(usage, model=model):
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens
    cost_dict = {'gpt-4o':{'input':5.00, 'output':15.00}, 'gpt-4o-mini':{'input':0.150, 'output':0.60}}   #pricing at 19/7/24
    input_token_cost = cost_dict[model]['input']
    output_token_cost = cost_dict[model]['output']
    input_price = input_token_cost/1000000  #$5.00 per 1M tokens
    output_price = output_token_cost/1000000 #$15.00 per 1M tokens
    input_cost = input_tokens * input_price
    output_cost = output_tokens * output_price
    total_cost = input_cost + output_cost
    cost_detail = (f'input tokens:{input_tokens}/output tokens:{output_tokens}/total tokens:{total_tokens} @ ${input_token_cost:.2f}, ${output_token_cost:.2f} (in, out) /1M tokens')
    retval = (total_cost, cost_detail)
    return retval


#####################
### Start of Main ###
#####################
st.title('Transcript Citation - Test tool')



output_url = 'http://www.google.com'
#st.markdown("""
###
##### [NOT YET WORKING _ IGNORE] If you want to look at previously created citations - take a look in here:
#""")
#st.write(output_url)


# use this approach for offering option to change prompt:
# https://docs.streamlit.io/develop/api-reference/widgets/st.text_input
# or perhaps use text_area:
# https://docs.streamlit.io/develop/api-reference/widgets/st.text_area




st.markdown("""
###
##### If you want to create a new citation - enter the transcript URL below
""")
st.text_input("Transcript URL", key='url_input', on_change=submit)
st.write(f'Last Transcript URL provided:')
st.write(f'{st.session_state.transcript_url}')

#show_clipping = st.button('Show Clipping image', key='show_clip_image')
if st.session_state.transcript_url:
    upp_id, sapi_url = get_sapi_url(st.session_state.transcript_url)
    st.markdown("""
    ##
    ##### Transcript upp_id and SAPI information link:""")
    st.write(upp_id, sapi_url)
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
    st.json(transcript_ref_dict, expanded=False)

    st.markdown("""
    ##
    ##### Model and prompt choices""")

    model = st.radio('Which ChatGPT model do you want to use?',
                      ['gpt-4o', 'gpt-4o-mini'])



    prompt_choice = st.radio("Do you want to use the default prompt, or write your own?",
                             key="p_choice",
                             options=["Use default", "Write my own"],
                             )
    st.write('NOTE - the date, reference URL and transcript json object will be appended to your prompt for submission to ChatGPT')


    if prompt_choice == "Use default":
        st.markdown("""
        ####
        ##### Default prompt used:""")
        st.text(prompt_text)
        citation_prompt = prompt.format(today.date(), st.session_state.transcript_url, sapi_info)
    elif prompt_choice == "Write my own":
        st.markdown('##### Amend / write your own prompt below (for expert use)')
        st.markdown('For reference - here is the default prompt:')
        st.text(prompt_text)
        st.session_state.prompt_input = st.text_area('Write your prompt:')
        alt_prompt = st.session_state.prompt_input + prompt_data
        citation_prompt = alt_prompt.format(today.date(), st.session_state.transcript_url, sapi_info)


    show_prompt = st.button('Show me the prompt you will be using', key='show_p')

    if show_prompt:
        st.text(st.session_state.prompt_text_user)
        st.text(citation_prompt)


    st.markdown("""
    ###
    ##### Press the button below to get a citation """)


    get_citation = st.button('Get a citation from ChatGPT-4', key='get_openai_cit')

    #st.write(citation_prompt)


    if get_citation:
        st.write(f'model chosen = {model}')
        #st.write(citation_prompt)
        try:
            completion = call_chatgpt_for_citation(citation_prompt, model=model)
            st.write(completion.choices[0].message.content)
            try:
                total_cost = get_cost(completion.usage, model)
                #st.write(total_cost)
                cost_text = f"Total cost of Chat-GPT for this description: ${total_cost[0]:.3f}  (=${total_cost[0]*1000:.2f}/1,000)  \nCost detail: {total_cost[1]}  \nCreated at: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')} using model: {model}"

                sub_and_response = {'timestamp':datetime.today(),
                                    'prompt':citation_prompt,
                                    'response_content':completion.choices[0].message.content,
                                    'model':model,
                                    'usage':completion.usage,
                                    'cost_text':cost_text}
                st.text(cost_text)

                line_for_df = {**transcript_ref_dict, **sub_and_response}
                st.write('Citation request information to be added to logging dataframe:')
                st.json(line_for_df, expanded=False)
                st.session_state.citation_df = pd.concat([st.session_state.citation_df, pd.DataFrame.from_dict([line_for_df], orient='columns', dtype='str')])
                st.session_state.citation_df.drop_duplicates(inplace=True)
                st.session_state.citation_df.to_pickle(df_save_name)


            except:
                pass

        except:
            st.write('Try again - there was an error')
            #st.write('(Sometimes this fails - it usually works after another attempt or two (or three, or four....))')
            #st.write("""(This is likely an image rendering speed issue - so very large clippings / whole pages can be problematic.
            #            If you want to improve the chance of success at first attempt, try it with a smaller clipping)""")
            #get_description=False



st.markdown("""
###
##### Recent citation request data """)


st.write('Last 12 citation requests:')
st.dataframe(st.session_state.citation_df.tail(12))

st.markdown("""
###
##### Full citation request data """)
st.write('The *Full* history of requests & responses is here:')
st.write('http://fh1-donut02.dun.fh:8571')
