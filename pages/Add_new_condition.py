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

# session states
if "disabled" not in st.session_state:
    st.session_state.disabled = False
    st.session_state.submitted = False
    st.session_state.cond_visible = "Get conditions data"
    st.session_state.cond_data = False

# this focuses input on text window
components.html(
    f"""
        <script>
            var input = window.parent.document.querySelectorAll("input[type=text]");
            for (var i = 0; i < input.length; ++i) {{
                input[i].focus();
            }}
    </script>
    """,
    height=0,
)
st.page_link("home.py", label="Home")
st.title("Conservation input")
destination = ""
conservation_status = ""
public_note = ""
staff_note = ""


def search_aspace():
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
    st.write(title)


def status_form():
    public_note = ""
    staff_note = ""
    arsenic = ""
    conservation_status = st.selectbox(
        "Conservation status: ",
        ("C1: Good", "C2: Fair", "C3: Poor", "C4: Unacceptable"),
        index=None,
        placeholder="Select a Conservation Status",
        disabled=st.session_state.disabled,
    )
    if conservation_status == "C1: Good":
        public_note = st.text_input(
            "Public note: ",
            "Handle with care",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    elif conservation_status == "C2: Fair":
        public_note = st.text_input(
            "Public note: ",
            "Please be careful when handling this book, it may be damaged",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    elif conservation_status == "C3: Poor":
        public_note = st.text_input(
            "Public note: ",
            "This book is very fragile and may require special handling",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    elif conservation_status == "C4: Unacceptable":
        public_note = st.text_input(
            "Public note: ",
            "This book is too damaged to be handled",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    # st.checkbox('Arsenic')
    # if st.checkbox:
    #    arsenic = True
    return conservation_status, public_note, staff_note  # , arsenic


def search_primo():
    url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={identifier}&apikey={apiKey}"
    r = requests.get(url, headers=headers).json()
    title = r["bib_data"]["title"].replace(" /", "")
    author = r["bib_data"]["author"]
    st.write(f"{title} by {author}")


def primo_submit(identifier, conservation_status, public_note, staff_note):
    url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={identifier}&apikey={apiKey}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        conservation_status = conservation_status[:2]
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
                if r.status_code != 200:
                    st.write(
                        f"Work order not sent (probably location/library problem: {library})"
                    )


identifier = st.text_input(
    "Enter the barcode (Alma) or Identifier (ArchivesSpace): ",
    key="search_term",
    disabled=st.session_state.disabled,
)
if identifier != "":
    if "." in identifier:
        destination = "ArchivesSpace"
        try:
            search_aspace()
            conservation_status, public_note, staff_note = status_form()
        except IndexError:
            st.write("Identifier not found")
    elif identifier.lower().startswith(("b", "v")):
        destination = "Primo"
        try:
            search_primo()
            conservation_status, public_note, staff_note = status_form()
        except (IndexError, KeyError):
            st.write("Barcode not found")
    else:
        st.write("Please enter a Alma barcode or ArchivesSpace identifier")


def lock():
    st.session_state.disabled = True


def clear_text():
    st.session_state.disabled = False
    st.session_state.submitted = False
    st.session_state["search_term"] = ""


if (conservation_status is not None) and (conservation_status != ""):
    submitted = st.button(
        "Submit", type="primary", disabled=st.session_state.disabled, on_click=lock
    )
    if submitted:
        st.session_state.submitted = True
        st.button("Change another record", type="primary", on_click=clear_text)

if st.session_state.submitted:
    if destination == "Primo":
        primo_submit(identifier, conservation_status, public_note, staff_note)
    if destination == "ArchivesSpace":
        pass  # TODO add archivesspace stuff
    st.markdown(
        f"""### The following info was sent to {destination} for {identifier}:
        
__Conservation status:__ {conservation_status}

__Public Note:__ {public_note}

__Staff Note (Fulfillment note):__ {staff_note}"""
    )
