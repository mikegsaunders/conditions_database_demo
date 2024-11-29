import streamlit as st
import streamlit.components.v1 as components
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
import os
import requests
import pandas as pd

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

st.sidebar.page_link("home.py", label="Home")
st.sidebar.page_link("pages/Add_new_condition.py", label="Conservation input")
st.sidebar.page_link("pages/Condition_database.py", label="Condition database")
# st.sidebar.page_link("pages/demopage.py", label="Demo Page")
st.sidebar.page_link("pages/batch_input.py", label="Batch input")
st.sidebar.page_link("pages/batch_upload_spreadsheet.py", label="Upload spreadsheet")

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
            label.st-emotion-cache-1qg05tj.e1y5xkzn3 {
            display: none;
            }
            </style>""",
    unsafe_allow_html=True,
)
st.page_link("home.py", label="Home")
st.title("Upload spreadsheet")
with open("Conservation_template.xlsx", "rb") as f:
    st.download_button(
        label="Download template",
        data=f,
        file_name="Conservation_template.xlsx",
    )
batch_file = st.file_uploader("Upload a spreadsheet", type=["csv", "xls", "xlsx"])
if batch_file is not None:
    df = pd.read_excel(batch_file)
    st.dataframe(df, hide_index=True)
    with st.spinner("Uploading..."):
        almadata = []
        aspacedata = []
        for index, row in df.iterrows():
            data = {
                "identifier": row.get("Identifier"),
                "condition": row.get("Condition"),
                "staff_note": row.get("Staff note"),
                "public_note": row.get("Public note"),
            }
            if "." in row.get("Identifier"):
                aspacedata.append(data)
            elif row.get("Identifier").lower().startswith(("b", "v")):
                almadata.append(data)
    if len(almadata) > 0:
        st.write("Data sent to Alma:")
        st.write(almadata)
    if len(aspacedata) > 0:
        st.write("Data sent to ArchivesSpace:")
        st.write(aspacedata)
