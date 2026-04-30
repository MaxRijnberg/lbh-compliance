import streamlit as st
from lbh_compliance.config.page_setup import setup_page


def main() -> None:
    setup_page("Transaction screening")

    st.write("This is hopefully working now")


if __name__ == "__main__":
    main()
