import streamlit as st


def setup_page(title: str):
    """
    Sets the page used in the webapp

    Args:
        title (str): The title of the page, to be displayed in the tab.
    """
    st.set_page_config(page_title=title, page_icon="📈")
