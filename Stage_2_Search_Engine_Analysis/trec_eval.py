from collections import OrderedDict
import math
import os.path

# hold the final relevant docs
# key: query id
# value:  a list of doc_id that are considered relevant or strongly relevant based on their average relevance score
rele_assess_dict = {}


def retrieve_query_results(query_result_file):
    query_results = OrderedDict()
    with open(query_result_file, "r") as file:
        for line in file:
            query_id, _, doc_id, *rest = (
                line.strip().split()
            )  # get only the query_id and doc_id
            if query_id in query_results:
                query_results[query_id].append(doc_id)  #
            else:
                query_results[query_id] = [doc_id]
    return query_results


def retrieve_relevance_assessment(qrel_file):
    temp_relevance_scores = {}

    with open(qrel_file, "r") as f:
        for line in f:
            query_id, _, doc_id, relevance = line.strip().split()
            relevance = int(relevance)  # convert relevance to int for calculations

            key = (query_id, doc_id)
            print(key)

            # if the key is already in the dictionary, update the sum and count
            if key in temp_relevance_scores:
                temp_relevance_scores[key]["sum"] += relevance
                temp_relevance_scores[key]["count"] += 1
            else:
                # if not, initialize the sum and count
                temp_relevance_scores[key] = {"sum": relevance, "count": 1}

    #  as we have multiple scores for the same query_id and doc_id pair
    for (query_id, doc_id), scores in temp_relevance_scores.items():
        # calculate the average relevance score
        average_relevance = scores["sum"] / scores["count"]
        # check if the average relevance score >= 1
        if average_relevance >= 1:
            if query_id in rele_assess_dict:
                rele_assess_dict[query_id].append(doc_id)
            else:
                rele_assess_dict[query_id] = [doc_id]
    return rele_assess_dict


def print_mean_vals(lst, desc, kVals=[], qid=""):
    print(desc)

    if not kVals:
        # if kVals is empty, calculate and print the mean for the entire list.
        mean_val = math.fsum(lst) / len(lst)
        print("{:.4f}".format(mean_val))
    else:
        # if kVals are provided: calculate and print the mean for each specified sublist.
        for k in kVals:
            mean_val = math.fsum(lst[k]) / len(lst[k])
            # If qid is provided, include it in the print statement.
            if qid != "":
                print("  At {:5} docs for {}: {:.4f}".format(k, qid, mean_val))
            else:
                # use ':5': ensures that the number is right-aligned in a space of 5 chars.
                print("  At {:5} docs: {:.4f}".format(k, mean_val))


def calculate_precision(relevant_number, rank):
    return relevant_number / rank if rank else 0


def calculate_recall(relevant_number, total_relevant):
    return relevant_number / total_relevant if total_relevant else 0


def calculate_f1(precision, recall):
    return (2 * precision * recall) / (precision + recall) if precision + recall else 0


def calculate_nDCG(relevance_scores):
    dc_value = sum(
        score / math.log(1.0 + rank)
        for rank, score in enumerate(relevance_scores, start=1)
    )
    sorted_scores = sorted(relevance_scores, reverse=True)
    idc_value = sum(
        score / math.log(1.0 + rank)
        for rank, score in enumerate(sorted_scores, start=1)
    )
    return dc_value / idc_value if idc_value else 0


def calculate_r_precision(rp, total_relevant):
    return rp / total_relevant if total_relevant else 0


def update_metric(metric_dict, key, value):
    if key in metric_dict:
        metric_dict[key].append(value)
    else:
        metric_dict[key] = [value]


def write_details(f, query_id, document, rank, is_relevant, precision, recall):
    f.write(
        f"{query_id} {document} {rank} {is_relevant} {precision:.4f} {recall:.4f}\n"
    )


def calculate_metrics(query_results, option):
    k_vals = [5, 10, 20, 50, 100]
    AP, RP, NDCG = [], [], []
    P, R, F1 = {}, {}, {}
    with open("details.txt", "w") as f:
        for query_id, results in query_results.items():
            relevant_docs = rele_assess_dict.get(query_id, [])
            if not relevant_docs:
                continue

            relevance_scores = []
            p_temp, r_temp, f1_temp = {}, {}, {}
            p_sum, relevant_count, rp = 0, 0, 0
            for rank, document in enumerate(results, start=1):
                is_relevant = document in relevant_docs
                relevant_count += is_relevant
                rp = relevant_count if rank <= len(relevant_docs) else rp
                precision = calculate_precision(relevant_count, rank)
                recall = calculate_recall(relevant_count, len(relevant_docs))
                p_sum += precision * is_relevant

                if rank in k_vals:
                    update_metric(P, rank, precision)
                    update_metric(p_temp, rank, precision)
                    f1 = calculate_f1(precision, recall)
                    update_metric(F1, rank, f1)
                    update_metric(f1_temp, rank, f1)
                    update_metric(R, rank, recall)
                    update_metric(r_temp, rank, recall)

                relevance_scores.append(is_relevant)
                write_details(
                    f, query_id, document, rank, is_relevant, precision, recall
                )

            r_precision = calculate_r_precision(rp, len(relevant_docs))
            RP.append(r_precision)
            ndcg = calculate_nDCG(relevance_scores)
            NDCG.append(ndcg)
            avg_precision = p_sum / len(relevant_docs) if relevant_docs else 0
            AP.append(avg_precision)
            if option == 1:
                print_metric("Average Precision", avg_precision, query_id)
                print_metric("R-Precision", r_precision, query_id)
                print_metric("nDCG", ndcg, query_id)
                print("\nPrecision@ Values")
                print_mean_vals(p_temp, "Mean Precision@", k_vals, query_id)
                print("\nRecall@ Values")
                print_mean_vals(r_temp, "Mean Recall@", k_vals, query_id)
                print("\nF1@ Values")
                print_mean_vals(f1_temp, "Mean F1@", k_vals, query_id)
                print("\n")

    print("========================================")
    print("============== Summary =================")
    print("========================================")
    print_mean_vals(AP, "\nAverage Precision:")
    print_mean_vals(RP, "\nR-Precision:")
    print_mean_vals(NDCG, "\nnDCG:")
    # print("\n========= Precision@k =========")
    print_mean_vals(P, "\n========= Precision@k =========", k_vals)
    # print("\n========= Recall@k =========")
    print_mean_vals(R, "\n=========== Recall@k ==========", k_vals)
    # print("\n========= F1@k =========")
    print_mean_vals(F1, "\n============ F1@k ============", k_vals)


def print_metric(description, value, query_id):
    print(f"{description} for {query_id}: {value:.4f}")


def main():
    # define paths
    cwd = os.getcwd()
    # print(f"Current working directory: {cwd}")
    PATH_SCRIPT = os.path.abspath(cwd)
    PATH_DIR_EVAL = os.path.join(PATH_SCRIPT, "eval_files")

    # user enter command
    cmd = input("Command: ")
    cmd_params = cmd.split(" ")

    try:
        if len(cmd_params) == 4:
            PATH_QRELS_FILE = os.path.join(PATH_DIR_EVAL, cmd_params[2])
            PATH_QUERY_RESULT_FILE = os.path.join(PATH_DIR_EVAL, cmd_params[3])

            print(f"Evaluating with Qrels file: {cmd_params[2]}")
            print(f"Using Query result file: {cmd_params[3]}")

            retrieve_relevance_assessment(PATH_QRELS_FILE)
            query_results = retrieve_query_results(PATH_QUERY_RESULT_FILE)
            calculate_metrics(query_results, 1)

        else:
            PATH_QRELS_FILE = os.path.join(PATH_DIR_EVAL, cmd_params[1])
            PATH_QUERY_RESULT_FILE = os.path.join(PATH_DIR_EVAL, cmd_params[2])

            print(f"Evaluating with Qrels file: {cmd_params[1]}")
            print(f"Using Query result file: {cmd_params[2]}")

            retrieve_relevance_assessment(PATH_QRELS_FILE)
            query_results = retrieve_query_results(PATH_QUERY_RESULT_FILE)

            calculate_metrics(query_results, 2)
    except Exception as e:
        print(f"An error occurred: {e}")


# trec_eval qrels.adhoc.51-100.AP89.txt 1_query_result_es_builtin.txt
# trec_eval qrels.adhoc.51-100.AP89.txt 2_query_result_okapi_tf.txt
# trec_eval qrels.adhoc.51-100.AP89.txt 3_query_result_tfidf.txt
# trec_eval qrels.adhoc.51-100.AP89.txt 4_query_result_okapi_bm25.txt
# trec_eval qrels.adhoc.51-100.AP89.txt 5_query_result_lm_laplace.txt
# trec_eval qrels.adhoc.51-100.AP89.txt 6_query_result_lm_jm.txt

# trec_eval [-q] qrels.adhoc.51-100.AP89.txt 2_query_result_okapi_tf.txt
# trec_eval qrel.txt ranklist.txt
# trec_eval [-q] qrel.txt ranklist.txt

if __name__ == "__main__":
    main()
