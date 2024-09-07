import re
from urllib.parse import urlparse
import streamlit as st


def load_css(file_name):
    with open(file_name) as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


def highlight_text(text, query):
    # tokenize the query string into words
    tokens = query.split()

    # loop through each token and apply highlighting
    for token in tokens:
        highlighted_text = re.sub(
            f"\\b({re.escape(token)})\\b",
            r'<span class="highlight">\1</span>',
            text,
            flags=re.IGNORECASE,
        )
        text = highlighted_text

    return text


def scrollable_container():
    st.markdown('<div class="scrollable">', unsafe_allow_html=True)


def bg_blue():
    st.markdown('<div class="bg-blue">', unsafe_allow_html=True)
