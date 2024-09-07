from elasticsearch import Elasticsearch


class ElasticsearchService:
    def __init__(self):
        self.es = Elasticsearch(
            cloud_id="6200:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRiZTllZjE5NDRkNTg0MDE3YTU0NDg0MzcwYjk5MjQzMSQ2Zjg1ODJhNWRjMGY0NDBhODU1Njk1MDQ4NzMyNmU2Yg==",
            http_auth=("elastic", "fwOhKti7myB3PKFHQavQBhcr"),
        )

    def search(self, text_query):
        INDEX = "crawler"
        MAX_RESULTS = 200
        response = self.es.search(
            index=INDEX,
            body={
                "query": {
                    "multi_match": {"query": text_query, "fields": ["title", "content"]}
                }
            },
            size=MAX_RESULTS,
        )
        return response
