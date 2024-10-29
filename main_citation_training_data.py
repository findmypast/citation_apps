import streamlit as st
#from page_functions import page1




#st.set_page_config(
#    page_title="Hello",
#    page_icon="👋",
#)


pg = st.navigation([st.Page('create_citation_training_data.py'),
                    st.Page('add_to_citations_already_started.py'),
                    st.Page('stats_collation.py')
                        ])
pg.run()


#st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select an app")
#st.markdown('#### Choose an app')
