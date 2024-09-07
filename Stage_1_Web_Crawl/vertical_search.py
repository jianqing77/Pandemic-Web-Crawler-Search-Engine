from urllib.parse import urlparse
import streamlit as st
from elasticsearch import Elasticsearch
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')

# Function to retrieve domain from URL
def domain_retrieval(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

# Function to highlight text hits with reduced opacity
def highlight_text(text, query):
    highlighted_text = re.sub(f'({query})', r'<span style="background-color: rgba(255, 255, 0, 0.5);">\1</span>', text, flags=re.IGNORECASE)
    return highlighted_text

# Streamlit app
def main():
    st.title("Vertical Search Page HW3")
    # User input
    text_query = st.text_input("Enter your Query")
    if st.button("Search"):
        INDEX = 'crawler'
        es = Elasticsearch(cloud_id= "0feeb24636464a578a9c7a1ce9739181:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQyMzcyNjZmYzcwMzg0ZTA2OTM1MTJkZGIxMDgzYTRmMyQ1N2RhZjIzZTNiMWM0MjAwYjBhMDQ0MGY1ZTEyZTc2Yw==",
                        http_auth=("elastic", "pETnMazDlmfyCT2rZ2NAWh2V"))
        response = es.search(
            index=INDEX,
            body={
            "query": {
                "multi_match": {
                "query": text_query,
                "fields": ["title", "content"]
                }
            }
            }, size=25
        )
        
        display_list = {}
        for hit in response['hits']['hits']:
            display_list[hit["_id"]] = {
                "content": hit["_source"]["content"],
                "author": hit["_source"]["author"],
                "title": hit["_source"]["title"]
            }
        # Display search results with improved design
        if display_list:
            for article_id, article_info in display_list.items():
                domain = domain_retrieval(article_id)
                try:
                    with st.expander(f"**Domain:** {domain}-----Article ID: {article_id}"):
                        st.markdown(f"# {article_info['title'].strip()}")
                        st.markdown(f"**Author:** {','.join(article_info['author'])}")
                        highlighted_content = highlight_text(article_info['content'], text_query)
                        st.markdown(highlighted_content, unsafe_allow_html=True)
                except Exception as e:
                    print(f"Check {article_id}")
        else:
            st.write("No results found.")
            
            
if __name__ == "__main__":
    main()