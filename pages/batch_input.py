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
headers = {"accept": "application/json", "Content-Type": "application/json"}

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
            .st-emotion-cache-q3uqly:disabled {
                display:none;
            }
            # div[role="alert"] {
            # display: none;
            # }
            </style>""",
    unsafe_allow_html=True,
)
st.page_link("home.py", label="Home")
st.title("Batch input")
df = pd.DataFrame(columns=["Identifier", "Condition", "Staff note", "Public note"])
conditions = ["C1: Good", "C2: Fair", "C3: Poor", "C4: Unacceptable"]
config = {
    "Identifier": st.column_config.TextColumn(required=True),
    "Condition": st.column_config.SelectboxColumn(
        required=True, options=conditions, default="C1: Good"
    ),
    "Staff note": st.column_config.TextColumn(width="large"),
    "Public note": st.column_config.TextColumn(width="large", default="Fragile"),
}
st.write("##### Click the plus sign at the bottom of any column to add a new row")
st.data_editor(
    df,
    key="batch",
    column_config=config,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
)


def primo_submit(collected_alma):
    for row in collected_alma:
        identifier = row["identifier"]
        conservation_status = row["condition"][:2]
        staff_note = row["staff_note"]
        public_note = row["public_note"]
        url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={identifier}&apikey={apiKey}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            data["item_data"]["physical_condition"]["value"] = conservation_status
            if public_note != "":
                data["item_data"]["public_note"] = public_note
            if staff_note != "":
                data["item_data"]["fulfillment_note"] = staff_note
            mmsID = data["bib_data"]["mms_id"]
            holdingID = data["holding_data"]["holding_id"]
            itemID = data["item_data"]["pid"]
            library = data["item_data"]["library"]["value"]
            url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mmsID}/holdings/{holdingID}/items/{itemID}?apikey={apiKey}"
            r = requests.put(url, json=data, headers=headers)
            if r.status_code == 200:
                if conservation_status == "C4":
                    data = r.json()
                    data["holding_data"]["temp_library"]["value"] = library
                    data["holding_data"]["in_temp_location"] = "true"
                    data["holding_data"]["temp_location"]["value"] = "C4"

                    # send work order location
                    url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mmsID}/holdings/{holdingID}/items/{itemID}"
                    if library == "GRR":
                        circ_desk = "WO_GRR"
                    elif library == "SCRR":
                        circ_desk = "WO_SCRR"
                    params = {
                        "apikey": apiKey,
                        "op": "scan",
                        "library": library,
                        "circ_desk": circ_desk,
                        "work_order_type": "CONSERVE",
                    }
                    r = requests.post(url, params=params, headers=headers)


def search_aspace(identifier):
    client = ASnakeClient(baseurl=sandbox, username=username, password=password)
    client.authorize()
    try:
        idResults = client.get(
            search_identifier,
            params={"identifier[]": [f'["{identifier}"]'], "resolve[]": "resources"},
        ).json()
        title = idResults["resources"][0]["_resolved"]["title"]
    except IndexError:
        idResults = client.get(
            search_component_identifier,
            params={"component_id[]": identifier, "resolve[]": "archival_objects"},
        ).json()
        title = idResults["archival_objects"][0]["_resolved"]["title"]
    return title


def search_alma(identifier):
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={identifier}&apikey={apiKey}"
    r = requests.get(url, headers=headers).json()
    title = r["bib_data"]["title"].replace(" /", "")
    author = r["bib_data"]["author"]
    return title, author


def submit(edited_dataframe):
    data = edited_dataframe["added_rows"]
    collected_alma = []
    collected_aspace = []
    identifier_error = []
    # validate data
    with st.spinner("Processing..."):
        for row in data:
            identifier = row["Identifier"]
            if "." in identifier:
                try:
                    aspace_data = search_aspace(identifier)
                    new = {
                        "title": aspace_data,
                        "identifier": identifier,
                        "condition": row.get("Condition"),
                        "staff_note": row.get("Staff note"),
                        "public_note": row.get("Public note"),
                    }
                    collected_aspace.append(new)
                except (IndexError, KeyError):
                    identifier_error.append(identifier)
                    continue
            elif identifier.lower().startswith(("b", "v")):
                try:
                    alma_title, alma_author = search_alma(identifier)
                    new = {
                        "title": alma_title,
                        "author": alma_author,
                        "identifier": identifier,
                        "condition": row.get("Condition"),
                        "staff_note": row.get("Staff note"),
                        "public_note": row.get("Public note"),
                    }
                    collected_alma.append(new)
                except (IndexError, KeyError):
                    identifier_error.append(identifier)
                    continue
    if len(identifier_error) > 0:
        errorList = (
            str(identifier_error).replace("[", "").replace("]", "").replace("'", "")
        )
        st.error(f"Identifiers not found:\n{errorList}")
    if len(collected_aspace) > 0:
        st.write("Data added to Archivesspace:")
        st.write(collected_aspace)
    else:
        st.write("No aspace data")
    if len(collected_alma) > 0:
        with st.spinner("Uploading to Alma..."):
            primo_submit(collected_alma)
        st.write("Data added to Alma:")
        st.write(collected_alma)
    else:
        st.write("No alma data")


if st.button("Submit"):
    submit(st.session_state["batch"])
