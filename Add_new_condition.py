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
st.page_link("pages/Condition_database.py", label="Condition database")
st.write(
    """
# Conservation input
        """
)
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
        ("Broken", "Arsenic", "Frayed"),
        index=None,
        placeholder="Select a Conservation Status",
        disabled=st.session_state.disabled,
    )
    if conservation_status == "Arsenic":
        public_note = st.text_input(
            "Public note: ",
            "Wear gloves!",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "Tell people to wear gloves!",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    elif conservation_status == "Frayed":
        public_note = st.text_input(
            "Public note: ",
            "Please be careful when handling this book, it may be damaged",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "Frayed, but loanable",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    elif conservation_status == "Broken":
        public_note = st.text_input(
            "Public note: ",
            "This book is currently unavailable as it is being repaired",
            key="public_note",
            disabled=st.session_state.disabled,
        )
        staff_note = st.text_input(
            "Staff note: ",
            "Damaged, not loanable",
            key="private_note",
            disabled=st.session_state.disabled,
        )
    # st.checkbox('Arsenic')
    # if st.checkbox:
    #    arsenic = True
    return conservation_status, public_note, staff_note  # , arsenic


def search_primo():
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode={identifier}&apikey={apiKey}"
    r = requests.get(url, headers=headers).json()
    title = r["bib_data"]["title"].replace(" /", "")
    author = r["bib_data"]["author"]
    st.write(f"{title} by {author}")


identifier = st.text_input(
    "Enter the barcode (Library Search) or Identifier (ArchivesSpace): ",
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
        st.write("Please enter a Library Search barcode or ArchivesSpace identifier")


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
    st.markdown(
        f"""### The following info was sent to {destination} for {identifier}:
            
__Conservation status:__ {conservation_status}

__Public Note:__ {public_note}

__Staff Note:__ {staff_note}"""
    )
