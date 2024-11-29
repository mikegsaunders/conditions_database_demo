import streamlit as st
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
import os
import pandas as pd
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

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

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
            div[role="alert"] {
                display: none;
            }
            </style>""",
    unsafe_allow_html=True,
)


def clear_text():
    st.session_state.disabled = False
    st.session_state.submitted = False
    st.session_state["search_term"] = ""


# st.page_link("Add_new_condition.py", label="Back (to add new condition)")
st.page_link("home.py", label="Home")
st.title("Conservation database")
with st.spinner(text="Fetching conservation data from Alma and ArchivesSpace..."):
    set_id = "17065550790004341"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{set_id}/members?apikey={apiKey}"
    r = requests.get(url, headers=headers).json()
    barcodes = []
    for item in r["member"]:
        barcodes.append(item["description"])
    itemdata = []
    for barcode in barcodes:
        search_url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={barcode}&apikey={apiKey}"
        search_r = requests.get(search_url, headers=headers).json()
        title = search_r["bib_data"]["title"].replace(" /", "")
        author = search_r["bib_data"]["author"]
        pub_note = search_r["item_data"]["public_note"]
        ful_note = search_r["item_data"]["fulfillment_note"]
        condition = search_r["item_data"]["physical_condition"]["desc"]
        dict = {
            "database": "Alma",
            "identifier": barcode,
            "title": title,
            "author": author,
            "public note": pub_note,
            "staff note": ful_note,
            "condition": condition,
        }
        itemdata.append(dict)
    try:
        client = ASnakeClient(baseurl=sandbox, username=username, password=password)
        client.authorize()
    except NameError:
        st.write(
            ":face_with_spiral_eyes: Can't connect to ArchivesSpace - are you connected to the VPN?"
        )
    except ASnakeAuthError:
        st.write(
            ":face_with_spiral_eyes: Can't connect to ArchivesSpace - are you connected to the VPN?"
        )
    assessment_results = client.get(assessments, params={"all_ids": "true"}).json()
    for id in assessment_results:
        rec_data = client.get(f"{assessments}/{id}").json()
        rec = rec_data["records"][0]["ref"]
        staff_note = rec_data.get("conservation_note")
        options = rec_data["conservation_issues"]
        issues = []
        for each in options:
            if each.get("value"):
                issues.append(each["label"])
        issues = ", ".join(issues)
        item_rec = client.get(rec).json()
        title = item_rec["title"]
        try:
            identifier = item_rec["id_0"]
        except KeyError:
            identifier = item_rec["component_id"]
        dict = {
            "database": "ArchivesSpace",
            "identifier": identifier,
            "title": title,
            "author": "",
            "public note": pub_note,
            "staff note": staff_note,
            "condition": issues,
        }
        itemdata.append(dict)
    df = pd.DataFrame(itemdata)
    pd.options.display.max_colwidth = 30
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={"title": st.column_config.Column(width="medium")},
    )
