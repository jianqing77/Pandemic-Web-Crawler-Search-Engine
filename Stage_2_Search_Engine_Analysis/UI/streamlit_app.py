import os

os.environ["STREAMLIT_CONFIG_LOCATION"] = "./.streamlit/config.toml"
import streamlit as st
from .elasticsearch_service import ElasticsearchService
from .helper import load_css, highlight_text
import os


QUERIES = {
    "1529": "Global Pandemics in history",
    "152901": "West African Ebola epidemic",
    "152902": "H1N1 Swine Flu pandemic",
    "152903": "COVID 19",
}


class StreamlitApp:

    def __init__(self):
        self.es_service = ElasticsearchService()
        self.response = None  # elasticsearch response
        self.result_dict = {}  # stores the results returned from elasticsearch
        self.total_hits = 0  # store the total hits returned from elasticsearch

        self.assessments = {}  # store the assessment info, key: doc_id, value: score

        self.st = st
        self.st.set_page_config(layout="wide")
        self._init_ui()

    def _init_ui(self):
        base_dir = os.path.dirname(__file__)
        css_path = os.path.join(base_dir, "..", "static", "style.css")
        load_css(css_path)

    def get_query_input(self):
        text_query = self.st.text_input(
            "Query",
            placeholder="Enter query or keyword to start searching...",
        )
        return text_query

    def get_accessor_input(self):
        assessor_id = self.st.text_input(
            "Assessor",
            placeholder="Enter the assessor name, e.g. John_Doe",
        )
        return assessor_id

    def run(self):
        _, input_col, output_col, _ = self.st.columns([1, 2, 4, 1])
        with input_col:
            self.st.header("Relevance Assessor")
            # main input here
            assessor_id = self.get_accessor_input()
            query = self.get_query_input()

            _, btn_col, _ = self.st.columns(3)
            with btn_col:
                # with the button here
                search_btn = self.st.button("Search")
            if "assessments" in self.st.session_state:
                self.assessments = self.st.session_state["assessments"]
                # self.st.write(self.st.session_state["assessments"])

        with output_col:
            # if search_btn is clicked
            if search_btn:
                self.search_handler(query, assessor_id)
            elif (
                "result_dict" in self.st.session_state
                and self.st.session_state["result_dict"]
            ):
                # if there are already results stored, display them
                self.display_results(query, assessor_id)

    def search_handler(self, query, assessor_id):
        # new search without submit button
        if "last_query" not in self.st.session_state:
            self.st.session_state["last_query"] = None
        query_has_changed = query != self.st.session_state.get("last_query")

        if query_has_changed:
            self.st.session_state.clear()
            self.st.session_state["last_query"] = query
        # if no session record: no result found previously or search not performed yet
        if (
            "result_dict" not in self.st.session_state
            or not self.st.session_state["result_dict"]
        ):
            self.get_es_result(query)
            self.st.session_state["assessments"] = self.assessments
            # no result found
            if not self.result_dict:
                self.st.info("No result found")
                return

        # if search performed and have result_dict in the session state
        self.display_results(query, assessor_id)

    def get_es_result(self, text_query):
        """
        Get es response and return the display list and total number of the result
        """
        self.response = self.es_service.search(text_query)
        for hit in self.response["hits"]["hits"]:
            self.result_dict[hit["_id"]] = {
                "score": hit["_score"],
                "content": hit["_source"]["content"],
                "author": hit["_source"]["author"],
                "title": hit["_source"]["title"],
            }
        # Get the total number of hits
        self.total_hits = self.response["hits"]["total"]["value"]

        # save the result_dict to the session state
        self.st.session_state["result_dict"] = self.result_dict
        self.st.session_state["total_hits"] = self.total_hits

    def display_results(self, query, assessor_id):
        """
        display elasticsearch results and total hits
        """

        self.result_dict = st.session_state["result_dict"]
        self.total_hits = st.session_state["total_hits"]
        self.assessments = st.session_state.get("assessments", {})

        # title
        results_to_display = min(200, len(self.result_dict))
        self.st.markdown(
            f"**Displaying:** {results_to_display}/{self.total_hits} results"
        )

        # display elements
        for idx, (doc_id, doc_info) in enumerate(self.result_dict.items(), start=1):
            result_col, score_col = self.st.columns([4, 1])

            # display static results
            with result_col:
                with st.expander(f"**#{idx}. URL:** {doc_id}"):
                    highlighted_title = highlight_text(doc_info["title"].strip(), query)
                    self.st.markdown(
                        f"#### {highlighted_title}", unsafe_allow_html=True
                    )
                    self.st.markdown(f"**Score:** {doc_info['score']}")
                    self.st.markdown(f"**Author:** {','.join(doc_info['author'])}")
                    highlighted_content = highlight_text(doc_info["content"], query)
                    self.st.markdown(highlighted_content, unsafe_allow_html=True)
            # display the score input
            with score_col:
                score_input_key = f"input_{doc_id}"
                if score_input_key not in st.session_state:
                    st.session_state[score_input_key] = self.assessments.get(doc_id, "")

                relevance_score = self.st.text_input(
                    "Relevance Score",
                    value=st.session_state[score_input_key],
                    key=score_input_key,
                    placeholder="0, 1, 2",
                )
                self.assessments[doc_id] = relevance_score
                st.session_state["assessments"] = self.assessments

                # Update the session_state and assessments dictionary when the user inputs a score
                if relevance_score != st.session_state[score_input_key]:
                    st.session_state[score_input_key] = relevance_score
                    self.assessments[doc_id] = relevance_score

        # Update the session state with the current assessments
        self.st.session_state["assessments"] = self.assessments
        # submit assessment
        _, btn_col, _ = self.st.columns(3)

        with btn_col:
            submit_btn = self.st.button("Submit Assessment")

        if submit_btn:
            # check if any assessment value is empty
            all_filled = all(
                value.strip() for value in self.st.session_state["assessments"].values()
            )

            if all_filled:
                # all assessments have values, proceed with saving
                self.save_assessment(query, assessor_id)

                _, msg_col, _ = self.st.columns([1, 3, 1])
                with msg_col:
                    self.st.success(
                        f"Assessment record generated for {len(self.st.session_state['assessments'])} documents.\n"
                    )
                    print(
                        f"Query: {query} \nAssessment record generated for {len(self.st.session_state['assessments'])} documents.\nSaved in assessment.txt"
                    )
                self.assessments.clear()
                self.st.session_state.clear()
            else:
                # not all assessments have values, display warning message
                _, msg_col, _ = self.st.columns([1, 3, 1])
                with msg_col:
                    self.st.warning(
                        "Please complete all assessments before submitting."
                    )

    def save_assessment(self, query, assessor_id):

        normalized_query = query.lower()
        query_id = None

        # find the corresponding query ID by matching the normalized query values
        for key, value in QUERIES.items():
            if value.lower() == normalized_query:
                query_id = key
                break

        # if no matching query ID was found, use the original query
        if query_id is None:
            query_id = query

        # write to file
        with open("qrel.txt", "a") as file:
            for doc_id, grade in self.st.session_state["assessments"].items():
                file.write(f"{query_id} {assessor_id} {doc_id} {grade}\n")


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
