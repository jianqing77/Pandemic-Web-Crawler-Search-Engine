# 🌐 Pandemic Data Explorer

Welcome to the Pandemic Data Explorer project, an innovative two-stage system designed to harness the power of web crawling and search engine analytics to provide insights into pandemic-related web content. Our project is divided into two primary components:

## 🕷️ Stage 1: Web Crawler (`Stage_1_Web_Crawler`)

This stage focuses on the development of a robust web crawler using Python. Here's what makes our crawler special:

-   **Efficient Data Handling:** Utilizes the HTTP requests library coupled with Python's multithreading capabilities to swiftly process and expand from a set of canonicalized seed URLs.
-   **Advanced Parsing Techniques:** Employs Beautiful Soup and regex to meticulously extract data from over 30,000 pandemic-related websites.
-   **Smart Frontier Management:** Implements a priority queue to manage the crawling frontier efficiently and handle socket timeouts for unresponsive sites.
-   **Ethical Crawling:** Adheres strictly to `robots.txt` guidelines for crawling delays and ensures ethical data collection.
-   **Natural Language Processing:** Enhances data quality with NLTK-based tokenization and stemming.

## 🔍 Stage 2: Search Engine Analysis (`Stage_2_Search_Engine_Analysis`)

In this stage, we turn the crawled data into actionable insights with a custom search engine and analytics dashboard:

-   **Powerful Search Engine:** Developed using Streamlit, this vertical search engine allows users to manually rate search results and generate QREL files for further analysis.
-   **Data Storage and Retrieval:** Utilizes Elasticsearch with a customized index configuration for efficient data storage, indexing, and retrieval. Integrated seamlessly with Elastic Cloud for scalable management.
-   **Dynamic Data Visualization:** Employs Kibana for dynamic and insightful visualization of indexed data.
-   **Precision Analysis:** Integrates trec_eval to process QREL files, producing precision-recall plots and key metrics to enhance data analysis.
