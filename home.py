import streamlit as st
import streamlit.components.v1 as components
from contextlib import contextmanager

st.set_page_config(
    initial_sidebar_state="collapsed",
)

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

st.sidebar.page_link("home.py", label="Home")
st.sidebar.page_link("pages/Add_new_condition.py", label="Conservation input")
st.sidebar.page_link("pages/Condition_database.py", label="Condition database")
# st.sidebar.page_link("pages/demopage.py", label="Demo Page")
st.sidebar.page_link("pages/batch_input.py", label="Batch input")
st.sidebar.page_link("pages/batch_upload_spreadsheet.py", label="Upload spreadsheet")

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

st.title("Conservation tools")


@contextmanager
def st_horizontal():
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown(
            '<span class="hide-element horizontal-marker"></span>',
            unsafe_allow_html=True,
        )
        yield


with st_horizontal():
    st.page_link("pages/Add_new_condition.py", label="Add a single item")
    st.write(f"if you've just got one conservation note to add")
with st_horizontal():
    st.page_link("pages/batch_input.py", label="Batch input")
    st.write("if you've got multiple notes to add")
with st_horizontal():
    st.page_link("pages/batch_upload_spreadsheet.py", label="Upload a spreadsheet")
    st.write("if you've already got a spreadsheet of conservation notes to add")
with st_horizontal():
    st.page_link("pages/Condition_database.py", label="View the Condition Database")
    st.write("to see all the conservation notes in Alma and ArchivesSpace")
