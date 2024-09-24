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


if 'clipping_url' not in st.session_state:
    st.session_state.clipping_url = ''

if 'url_input' not in st.session_state:
    st.session_state.url_input = ''

#functions

#scrape URL for title
st.cache_data()
def get_clip_data(share_id):
    response = requests.get(f'https://www.findmypast.co.uk/titan/marshal/obscura/api/clipping/{share_id}')
    response_text = response.content.decode('utf-8')
    info = json.loads(response_text)
    #st.write(info)
    clip_data = namedtuple("clip_info", ["title", "pub_date", "username"])
    retval = clip_data(*(info['clipping']['issueTitle'].rstrip('.'), info['clipping']['publicationDate'], info['clipping']['userProfile']['username']))
    return retval




prompt = """
         The image is a clipping from a newspaper or magazine.
         The title of the newspaper or magazine and the date of publication are {}
         Describe the clipping and summarise its content.
         If there are any photographs or illustrations in the clipping, describe them.
         Provide a full transcription of all of the text in the clipping.
         The response should include at least 3 sections: Description, Summary, Transcription.
         If any individual names are mentioned in the clipping, then also create a separate section
         at the end titled 'Names mentioned in clipping' and list the names (including titles, locations and ages, if mentioned) of
         all the people mentioned.
         If any locations or places are named in the clipping, then also create a separate section
         at the end titled 'Places mentioned in clipping' and list the places and if possible provide a link
         to a page about the named place on wikipedia.
         If any organisations are named in the clipping, then also create a separate section at the end titled
         'Organisations mentioned in clipping' and list the places and if possible provide a link
         to a page about the named organisation on wikipedia.

         ### HTML Output Formatting Instructions:

        - The **Description** section should provide an overview of the clipping, including any photographs or illustrations.
        - The **Summary** section should summarize the main content of the clipping.
        - The **Transcription** section should contain the full text transcription of the clipping.
        - Ensure that each section is clearly demarcated with appropriate headings (e.g., ### Description, ### Summary, ### Transcription).
        - If there are any individual names mentioned, ensure they are listed in a separate section titled 'Names mentioned in clipping'.
        - If there are any locations or places mentioned, include them in a separate section titled 'Places mentioned in clipping', with links to relevant Wikipedia pages if available.
        - If any organisations are mentioned, list them in a separate section titled 'Organisations mentioned in clipping', with links to relevant Wikipedia pages if available.

        Please follow these instructions to ensure the output is in the correct format for conversion to HTML using the provided function.
         """

#model = "gpt-4o"
model = "gpt-4o-mini"

st.cache_data()
def call_chatgpt_for_description(link, prompt=prompt, model=model):
    messages = [{"role": "user",
                 "content": [{"type": "text",
                              "text": prompt},
                             {"type": "image_url",
                              "image_url": {"url": link}}]}]

    retval = client.chat.completions.create(model=model, messages=messages,
                                            max_tokens=4000, timeout=300)
    return retval



st.cache_data()
def call_chatgpt_for_description_alt(image_base64, prompt=prompt, model=model):
    messages = [{"role": "user",
                 "content": [{"type": "text",
                              "text": prompt},
                             {"type": "text",
                              "text":image_base64}]}]

    retval = client.chat.completions.create(model=model, messages=messages,
                                            max_tokens=4000, timeout=300)
    return retval





st.cache_data()
def get_picture_url(clipping_url):
    share_id = clipping_url.split('/')[-1].split('?')[0]
    retval = f'https://www.findmypast.co.uk/titan/marshal/obscura/api/clipping/image/{share_id}'
    return retval


def submit():
    st.session_state['clipping_url'] = st.session_state['url_input']
    st.session_state.url_input = ''


st.cache_data()
def create_html(image_path, title, text, url, cost_text_html, html_path):
    # Convert markdown text to HTML
    text_html = markdown.markdown(text.lstrip("```html").rstrip("```"))

    # HTML content with UTF-8 charset and parsed text
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{html.escape(title)}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 10px;
                margin-bottom: 10px;
                line-height: 1.2;
            }}
            p {{
                margin: 5px 0;
            }}
            pre {{
                white-space: pre-wrap;
            }}
            .formatted-text {{
                width: 60%;
                max-width: 60%;
                margin: 20px auto;
                font-size: 18px;
            }}
            .title {{
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 20px;
            }}
            .cost-text {{
                font-family: Courier, monospace;
                font-size: 14px;
                color: grey;
            }}
        </style>
    </head>
    <body>
        <img src="{html.escape(image_path)}" alt="Image" style="max-width: 60%; height: auto; display: block; margin: auto;">
        <div class="title"><a href="{html.escape(url)}">{html.escape(title)}</a></div>
        <div class="formatted-text">{text_html}</div>
        <div class="formatted-text cost-text">{cost_text_html}</div>
    </body>
    </html>
    """
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)



st.cache_data()
def download_image(image_url, image_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")


# Function to resize and encode the image from a URL
st.cache_data()
def resize_and_encode_image_from_url(image_url, max_width, max_height):
    response = requests.get(image_url)
    response.raise_for_status()  # Ensure the request was successful
    image_data = response.content

    # Open the image with Pillow
    image = Image.open(BytesIO(image_data))

    # Resize the image, maintaining the aspect ratio
    image.thumbnail((max_width, max_height), Image.ANTIALIAS)

    # Save the resized image to a bytes buffer
    buffered = BytesIO()
    image.save(buffered, format="JPEG")

    # Encode the buffered image to base64
    return base64.b64encode(buffered.getvalue()).decode('utf-8')



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
st.title('Clipping Description - Test tool')

#st.write('HELLO')

output_url = 'http://fh1-donut02.dun.fh:8543'
st.markdown("""
###
##### If you want to look at previously created descriptions - take a look in here:
""")
st.write(output_url)


st.markdown("""
###
##### If you want to create a new description - enter the clipping URL below
""")
st.text_input("Clipping URL", key='url_input', on_change=submit)
st.write(f'Last Clipping URL provided:')
st.write(f'{st.session_state.clipping_url}')

#show_clipping = st.button('Show Clipping image', key='show_clip_image')
if st.session_state.clipping_url:
    share_id = st.session_state.clipping_url.split('/')[-1].split('?')[0]

    clip_data = get_clip_data(share_id)

    title = clip_data.title+' - '+clip_data.pub_date
    st.write(title)

    pic_link = get_picture_url(st.session_state.clipping_url)
    #st.write(pic_link)

    st.image(pic_link, width=600)



model = st.radio('Which ChatGPT model do you want to use?',
                  ['gpt-4o', 'gpt-4o-mini'])
get_description = st.button('Get a description from ChatGPT-4', key='get_openai_desc')

if get_description:
    st.write(f'model chosen = {model}')
    try:
        completion = call_chatgpt_for_description(pic_link, prompt.format(title), model)
        st.write(completion.choices[0].message.content)
        #total_cost = get_cost(completion.usage[0])
        #st.write(total_cost)
        try:
            share_id = st.session_state.clipping_url.split('/')[-1].split('?')[0]
            download_image(pic_link, f'./html_outputs/images/{share_id}.jpg')
            text = completion.choices[0].message.content
            link_title = title.replace(' ','_')
            total_cost = get_cost(completion.usage, model)
            #st.write(total_cost)
            cost_text = f"Total cost of Chat-GPT for this description: ${total_cost[0]:.3f}  (=${total_cost[0]*1000:.2f}/1,000)  \nCost detail: {total_cost[1]}  \nCreated at: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')} using model: {model}"
            model_for_path = model.replace('-','')
            create_html(f'./images/{share_id}.jpg', title, text,
                        st.session_state.clipping_url, cost_text, f'./html_outputs/{share_id}_{link_title}_{model_for_path}.html')

            clip_out_url = f"http://fh1-donut02.dun.fh:8544/{share_id}_{link_title}_{model_for_path}.html"
            link_text = f'[**(HTML output saved successfully)**]({clip_out_url})'
            st.write(link_text)
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
