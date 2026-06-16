import streamlit as st

from lbh_compliance.config.page_setup import setup_page
from lbh_compliance.config.settings import SCREENING_COLOURS
from lbh_compliance.api.portable import PortAbleAPIClient
from lbh_compliance.api.pascal import PascalAPIClient


def main() -> None:
    setup_page("Transaction screening")

    pc_id = st.text_input("Enter portcall number (e.g. UY260001)")
    if pc_id not in ["", None]:
        paa = PortAbleAPIClient()
        paa.login()
        paa.find_parties_from_portcall(pc_id)
        st.write(paa.parties)
        st.write(paa.other_parties)

        if "selected_parties" not in st.session_state:
            st.session_state["selected_parties"] = {}

        all_parties = {}

        for p, roles in paa.parties.items():
            all_parties[p] = roles

        for p in paa.other_parties:
            all_parties.setdefault(p, ["Other party"])

        st.subheader("Review detected parties")

        for party, roles in all_parties.items():
            key = f"party_{party}"

            checked = st.checkbox(f"{party} ({', '.join(roles)})", value=True, key=key)
            st.session_state["selected_parties"][party] = checked

        st.subheader("Add additional parties")
        new_party = st.text_input("Add party name")
        if st.button("Add party"):
            if new_party:
                st.session_state["selected_parties"][new_party] = True

        st.subheader("Select attachments for parsing (if BL detection failed)")
        selected_attachments = []
        for name, url in paa.attachments_dict.items():
            if st.checkbox(name, key=f"att_{name}"):
                selected_attachments.append((name, url))

        if st.button("Run screening"):
            pas = PascalAPIClient()

            selected = [
                p for p, use in st.session_state.selected_parties.items() if use
            ]

            for party in selected:
                response, msg = pas.get_case_if_exists(party)
                if response is not None:
                    result = pas.get_sanctions(response)
                    colour = SCREENING_COLOURS[result]
                    st.html(f'<ul style="background-color:{colour};">{party}</ul>')
                else:
                    st.html(f'<p style="border: 2px solid #FF0000;">{msg}</p>')


if __name__ == "__main__":
    main()
