import streamlit as st
from typing import Dict, Set, List

from lbh_compliance.config.page_setup import setup_page
from lbh_compliance.config.patterns import BL_PATTERN
from lbh_compliance.config.settings import SCREENING_COLOURS, SCREENING_STATUSES
from lbh_compliance.api.portable import PortAbleAPIClient
from lbh_compliance.api.pascal import PascalAPIClient
from lbh_compliance.api.bl import BLReader
from lbh_compliance.api.seasearcher import SeaSearcherAPIClient


def get_paa_client() -> PortAbleAPIClient:
    if "paa_client" not in st.session_state:
        paa = PortAbleAPIClient()
        paa.login()
        st.session_state["paa_client"] = paa
    return st.session_state["paa_client"]


def init_state() -> None:
    if "manual_parties" not in st.session_state:
        st.session_state["manual_parties"] = set()

    if "selected_parties" not in st.session_state:
        st.session_state["selected_parties"] = {}

    if "bl_processed" not in st.session_state:
        st.session_state["bl_processed"] = False

    if "active_pc_id" not in st.session_state:
        st.session_state["active_pc_id"] = None


def build_all_parties(parties: Dict[str, Set[str]], other_parties: Set[str]):
    all_parties = {}

    # Structured PAA parties
    for p, roles in parties.items():
        all_parties[p] = list(roles)

    # Unstructured parties
    for p in other_parties:
        all_parties.setdefault(p, ["Other party"])

    # Manual parties
    for p in st.session_state["manual_parties"]:
        all_parties.setdefault(p, ["Manually added"])

    return all_parties


def main() -> None:
    setup_page("Transaction screening")
    init_state()

    if st.button("Reconnect to PortAble Agent"):
        if "paa_client" in st.session_state:
            del st.session_state["paa_client"]
        st.rerun()

    pc_id = st.text_input("Enter portcall number (e.g. UY260001)")
    if not pc_id:
        return

    if st.session_state["active_pc_id"] != pc_id:
        # Clear UI-related state
        st.session_state["manual_parties"] = set()
        st.session_state["selected_parties"] = {}
        st.session_state["bl_processed"] = False
        st.session_state["active_pc_id"] = pc_id
        st.rerun()

    paa = get_paa_client()
    paa.find_parties_from_portcall(pc_id)

    parties = {k: set(v) for k, v in paa.parties.items()}
    other_parties = set(paa.other_parties)
    attachments = dict(paa.attachments_dict)

    st.subheader("Select BLs to extract more parties from")
    selected_attachments = []
    for name, url in attachments.items():
        likely_bl = bool(BL_PATTERN.search(name))
        if st.checkbox(name, value=likely_bl, key=f"att_{name}"):
            selected_attachments.append((name, url))

    if st.button("Extract parties from selected BL(s)"):
        for name, url in selected_attachments:
            try:
                bl_bytes = paa._download_bl_file(url)

                if bl_bytes:
                    reader = BLReader(bl_bytes)
                    bl_parties = reader.get_parties_from_bl()

                    for party, role in bl_parties.items():
                        if party in paa.parties:
                            parties[party].add(role)
                        else:
                            parties[party] = {role}

            except Exception as e:
                st.warning(f"Failed to process {name}: {e}")

        st.session_state["bl_processed"] = True

    all_parties = build_all_parties(parties, other_parties)

    for party in all_parties:
        if party not in st.session_state.selected_parties:
            st.session_state.selected_parties[party] = True

    st.subheader("Review detected parties")
    for party, roles in all_parties.items():
        key = f"party_{party}"

        st.session_state["selected_parties"][party] = st.checkbox(
            f"{party} ({', '.join(roles)})",
            value=st.session_state["selected_parties"][party],
            key=key,
        )

    st.subheader("Add additional parties")
    new_party = st.text_input("Add party name")
    if st.button("Add party"):
        if new_party:
            st.session_state["manual_parties"].add(new_party)
            st.session_state["selected_parties"][new_party] = True
            st.rerun()

    # Full party list
    final_parties: List[str] = [
        p for p, selected in st.session_state.selected_parties.items() if selected
    ]

    st.write(f"You have selected: {', '.join(final_parties)}")

    if st.button("Run screening"):
        pas = PascalAPIClient()
        sea = SeaSearcherAPIClient()

        for party in final_parties:

            response, msg = pas.get_case_if_exists(party)
            if response is not None:
                result, url = pas.get_sanctions(response)
                colour = SCREENING_COLOURS[result]
                party_status = SCREENING_STATUSES[result]
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.html(
                        f'<ul style="background-color:{colour};">{party} {party_status}</ul>'
                    )
                with col2:
                    st.html(url)
            else:
                st.html(f'<p style="border: 2px solid #FF0000;">{msg}</p>')

        st.html("<h3>Vessel data screened with SeaSearcher</h3>")
        if sea.is_sanctioned(paa.vessel_imo):
            colour = SCREENING_COLOURS[2]
            st.html(
                f"<ul style=\"background-color:{colour};\">Vessel '{paa.vessel_name}' (IMO: {paa.vessel_imo}) is SANCTIONED</ul>"
            )
        else:
            colour = SCREENING_COLOURS[0]
            st.html(
                f"<ul style=\"background-color:{colour};\">Vessel '{paa.vessel_name}' (IMO: {paa.vessel_imo}) is NOT sanctioned.</ul>"
            )


if __name__ == "__main__":
    main()
