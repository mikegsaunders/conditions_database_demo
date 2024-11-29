import streamlit as st
import streamlit.components.v1 as components
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
import os
import requests

# parameters
username = "admin"
password = os.environ["ASPACE"]
sandbox = os.environ["ASPACE_SANDBOX_API"]
production = os.environ["ASPACE_PRODUCTION_API"]
search_identifier = "repositories/2/find_by_id/resources"
search_component_identifier = "repositories/2/find_by_id/archival_objects"
apiKey = os.environ["ALMA_API_SANDBOX"]
assessments = "/repositories/2/assessments"

st.set_page_config(
    initial_sidebar_state="collapsed",
)

st.sidebar.page_link("Add_new_condition.py", label="Conservation input")
st.sidebar.page_link("pages/Condition_database.py", label="Condition database")

st.markdown(
    """<style>
            a[data-testid="stPageLink-NavLink"] {
                background-color: mediumvioletred;
            }
            a[data-testid="stPageLink-NavLink"]:hover {
                background-color: gray;
            }
            .st-emotion-cache-10fz3ls.e1nzilvr5 {
                color: white;
            }
            .st-emotion-cache-q3uqly:disabled {
                display:none;
            }
            div[role="alert"] {
            display: none;
            }
            </style>""",
    unsafe_allow_html=True,
)

st.write("## Conservation issues")
col1, col2 = st.columns(2)

with col1:
    st.checkbox("Surface Dirt")
    st.checkbox("Detatched Boards")
    st.checkbox("Planar Distortions")
    st.checkbox("Rehousing")
    st.checkbox("Other")

with col2:
    st.checkbox("Tears and/or Losses")
    st.checkbox("Creases and/or Folds")
    st.checkbox("PST and/or Adhesive Staining")
    st.checkbox("Staining")
