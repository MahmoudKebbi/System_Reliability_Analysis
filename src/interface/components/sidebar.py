"""
Sidebar component for the Streamlit interface.
"""

import streamlit as st


class Sidebar:
    """
    Sidebar navigation component.
    """

    @staticmethod
    def render():
        """
        Render the navigation sidebar.

        Returns:
            Selected page
        """
        st.sidebar.title("Navigation")

        page = st.sidebar.radio(
            "Select Page",
            ["System Builder", "Cut Set Analysis", "Simulation Analysis", "Help"],
        )

        # Add application info
        st.sidebar.markdown("---")
        st.sidebar.markdown("### About")
        st.sidebar.info(
            "This is an advanced reliability analysis tool "
            "for calculating minimal cut sets and system unreliability."
        )

        # Version info
        st.sidebar.markdown("---")
        st.sidebar.markdown("Version 1.0.0")
        st.sidebar.markdown(
            "[GitHub](https://github.com/MahmoudKebbireliabiility-analyzer)"
        )

        return page
