## NB - largely cannibalised (in haste) from the clipping description app. Hence some odd naming conventions etc.


# streamlit
import streamlit as st
import html
import markdown
from datetime import datetime

# for scrape
import requests
import json
from bs4 import BeautifulSoup
from collections import namedtuple

#for OpenAI
from openai import OpenAI

# local util for creds
from utils import get_creds



#setup stuff
creds = get_creds()

ai_key = creds['openai_key_cb']
client = OpenAI(api_key=ai_key)

today = datetime.today()

if 'transcript_url' not in st.session_state:
    st.session_state.transcript_url = ''

if 'url_input' not in st.session_state:
    st.session_state.url_input = ''

#functions

#scrape URL for title
st.cache_data()
def get_clip_data(sapi_url):
    response = requests.get(sapi_url)
    response_text = response.content.decode('utf-8')
    info = json.loads(response_text)
    #st.write(info)
    #clip_data = namedtuple("clip_info", ["title", "pub_date", "username"])
    #retval = clip_data(*(info['clipping']['issueTitle'].rstrip('.'), info['clipping']['publicationDate'], info['clipping']['userProfile']['username']))
    return info




prompt = """
        Attached below is a json structured data object for a historical record transcription.
        Can you format and create a citation to academic structure and standards for this document?
        The reponse should include 3 different academic citation formats, and each citation should include the fullest possible reference data,
        including any repository or archive series data and reference numbers.
        In addition, can you also add a genealogy style citation - as described by Elizabeth Shown Mills, in "Evidence Explained: Citing History Sources from Artifacts to Cyberspace"
        The access date should be {}.
        The reference URL should be {}

        {}
        """


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
    #st.write(upp_id)
    retval_url = f'http://sapi.dun.fh/v6.4.0/records/recordsinglewithsiteconfig/false/false/true/{upp_id}?consumingSiteId=FMP_UK_FULL'
    retval = (upp_id, retval_url)
    return retval


def submit():
    st.session_state['transcript_url'] = st.session_state['url_input']
    st.session_state.url_input = ''







# Function to resize and encode the image from a URL



#def format_text_for_html(text):
    # Replace newlines with <br> tags and preserve spaces
 #    formatted_text = text.replace('\n', '<br>')#.replace(' ', '&nbsp;')
 #    return formatted_text


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

#st.write('HELLO')

output_url = 'http://www.google.com'
#st.markdown("""
###
##### [NOT YET WORKING _ IGNORE] If you want to look at previously created citations - take a look in here:
#""")
#st.write(output_url)


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
    st.write(upp_id, sapi_url)
    sapi_info = (get_clip_data(sapi_url))
    citation_prompt = prompt.format(today, st.session_state.transcript_url, sapi_info)
    #st.write(citation_prompt)


model = st.radio('Which ChatGPT model do you want to use?',
                  ['gpt-4o', 'gpt-4o-mini'])
get_citation = st.button('Get a citation from ChatGPT-4', key='get_openai_cit')


if get_citation:
    st.write(f'model chosen = {model}')
    try:
        completion = call_chatgpt_for_citation(citation_prompt)
        st.write(completion.choices[0].message.content)
        #total_cost = get_cost(completion.usage[0])
        #st.write(total_cost)
        try:
            #share_id = st.session_state.clipping_url.split('/')[-1].split('?')[0]
            #download_image(pic_link, f'./html_outputs/images/{share_id}.jpg')
            #text = completion.choices[0].message.content
            #link_title = title.replace(' ','_')
            total_cost = get_cost(completion.usage, model)
            #st.write(total_cost)
            cost_text = f"Total cost of Chat-GPT for this description: ${total_cost[0]:.3f}  (=${total_cost[0]*1000:.2f}/1,000)  \nCost detail: {total_cost[1]}  \nCreated at: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')} using model: {model}"
            #model_for_path = model.replace('-','')
            #create_html(f'./images/{share_id}.jpg', title, text,
            #                st.session_state.clipping_url, cost_text, f'./html_outputs/{share_id}_{link_title}_{model_for_path}.html')

            #clip_out_url = f"http://fh1-donut02.dun.fh:8544/{share_id}_{link_title}_{model_for_path}.html"
            #link_text = f'[**(HTML output saved successfully)**]({clip_out_url})'
            #st.write(link_text)
            st.text(cost_text)
            #st.text(text)
            #st.write('test  \ntest')
            #st.write(clip_out_url)
        except:
            pass

    except:
        st.write('Try again - there was an error')
        st.write('(Sometimes this fails - it usually works after another attempt or two (or three, or four....))')
        st.write("""(This is likely an image rendering speed issue - so very large clippings / whole pages can be problematic.
                    If you want to improve the chance of success at first attempt, try it with a smaller clipping)""")
        get_description=False
