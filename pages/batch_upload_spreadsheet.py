import streamlit as st
import streamlit.components.v1 as components
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
import os
import requests
import pandas as pd
from contextlib import contextmanager

# parameters
username = "admin"
password = os.environ["ASPACE"]
sandbox = os.environ["ASPACE_SANDBOX_API"]
production = os.environ["ASPACE_PRODUCTION_API"]
search_identifier = "repositories/2/find_by_id/resources"
search_component_identifier = "repositories/2/find_by_id/archival_objects"
apiKey = os.environ["ALMA_API_SANDBOX"]
assessments = "/repositories/2/assessments"
headers = {"accept": "application/json", "Content-Type": "application/json"}

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
            .stDownloadButton > button {
                background-color: mediumvioletred;
                border: none;
            }
            .stDownloadButton > button:hover {
                background-color: gray;
                color: white;
            }
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

HORIZONTAL_STYLE = """
<style class="hide-element">
    /* Hides the style container and removes the extra spacing */
    .element-container:has(.hide-element) {
        display: none;
    }
    /*
        The selector for >.element-container is necessary to avoid selecting the whole
        body of the streamlit app, which is also a stVerticalBlock.
    */
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) {
        display: flex;
        flex-direction: row !important;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: baseline;
    }
    /* Buttons and their parent container all have a width of 704px, which we need to override */
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) div {
        width: max-content !important;
    }
    /* Just an example of how you would style buttons, if desired */
    /*
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) button {
        border-color: red;
    }
    */
</style>
"""


@contextmanager
def st_horizontal():
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown(
            '<span class="hide-element horizontal-marker"></span>',
            unsafe_allow_html=True,
        )
        yield


def primo_submit(almadata):
    for row in almadata:
        identifier = row["identifier"]
        conservation_status = row["condition"]
        staff_note = row["staff_note"]
        public_note = row["public_note"]
        url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={identifier}&apikey={apiKey}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            data["item_data"]["physical_condition"]["value"] = conservation_status[:2]
            data["item_data"]["physical_condition"]["description"] = conservation_status
            if public_note != "":
                data["item_data"]["public_note"] = public_note
            if staff_note != "":
                data["item_data"]["fulfillment_note"] = staff_note
            mmsID = data["bib_data"]["mms_id"]
            holdingID = data["holding_data"]["holding_id"]
            itemID = data["item_data"]["pid"]
            url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mmsID}/holdings/{holdingID}/items/{itemID}?apikey={apiKey}"
            r = requests.put(url, json=data, headers=headers)


st.page_link("home.py", label="Home")
st.title("Upload spreadsheet")
with st_horizontal():
    with open("Conservation_template.xlsx", "rb") as f:
        st.download_button(
            label="Download template",
            data=f,
            file_name="Conservation_template.xlsx",
        )
    st.write("Use this template for your conservation data")
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
        with st.spinner("Uploading to Alma..."):
            primo_submit(almadata)
        st.write("Data sent to Alma:")
        st.write(almadata)
    if len(aspacedata) > 0:
        st.write("Data sent to ArchivesSpace:")
        st.write(aspacedata)
