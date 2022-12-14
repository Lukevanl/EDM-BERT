import math
import numpy as np
import sys

def parse_qrel_line(line):
    # =======Your code=======
    result = line.split('\t')
    query = result[0]
    document = result[2]
    relevancy = min(1, int(result[3]))

    # =======================
    return query, document, relevancy

def parse_results_line(line):
    # =======Your code=======
    result = line.split('\t')
    query = result[0]
    document = result[1]
    rank = int(result[2])
    # =======================
    return query, document, rank

class relevancy_lookup(object):
    def __init__(self):
        self.relevancies = {}
    
    def add(self, query, document, relevancy):
        # =======Your code=======
        if query in self.relevancies:
          self.relevancies[query].update({document:relevancy})
        else:
          self.relevancies.update({query: {document:relevancy}})
        # =======================
        
    def get(self, query, document):
        # =======Your code=======
        if document in self.relevancies[query]:
            return self.relevancies[query][document]
        else:
            return 0
        # =======================

def get_ranked_labels(rel_lookup, query, doc_rank_list): 
    result = np.zeros(len(doc_rank_list), dtype=int)
    for x in doc_rank_list:
        result[x[1]-1] = rel_lookup.get(query, x[0])
    return result

def process_files(qrel_path, results_path):
    relevancies = relevancy_lookup()
    with open(qrel_path, 'r') as qrel_file:
        for line in qrel_file:
            query, document, relevancy = parse_qrel_line(line)
            relevancies.add(query, document, relevancy)
    with open(results_path, 'r') as results_file:
        current_query, document, rank = parse_results_line(next(results_file))    
        doc_rank_list = [(document, rank)]
        for line in results_file:
            query, document, rank = parse_results_line(line)
            if query != current_query:
                yield get_ranked_labels(relevancies, current_query, doc_rank_list)
                current_query = query
                doc_rank_list = [(document, rank)]
            else:
                doc_rank_list.append((document, rank))
        yield get_ranked_labels(relevancies, current_query, doc_rank_list)

def precision(query_relevancy_labels, k):
    # =======Your code=======
    return sum(query_relevancy_labels[:k]) / k
    # =======================

def recall(query_relevancy_labels, k):
    # =======Your code=======
    return sum(query_relevancy_labels[:k]) / max(1, sum(query_relevancy_labels))
    # =======================

def F_score(query_relevancy_labels, k):
    # =======Your code=======
    # Naar de max functie kijken
    return (2 * precision(query_relevancy_labels, k) * recall(query_relevancy_labels, k)) / max(0.01, precision(query_relevancy_labels, k) + recall(query_relevancy_labels, k))
    # =======================

def DCG(query_relevancy_labels, k):
    # Use log with base 2
    # =======Your code=======
    return sum([query_relevancy_labels[i] / math.log2(2 + i) for i in range(min(k, len(query_relevancy_labels)))])
    # =======================

def NDCG(query_relevancy_labels, k):
    # =======Your code=======
    return DCG(query_relevancy_labels, k) / max(1, DCG(np.flip(np.sort(query_relevancy_labels)), k))
    # =======================

def AP(query_relevancy_labels):
    # =======Your code=======
    return sum([query_relevancy_labels[k] * precision(query_relevancy_labels, k+1) for k in range(len(query_relevancy_labels))]) / max(1, sum(query_relevancy_labels))
    # =======================

def RR(query_relevancy_labels):
    # =======Your code=======
    try:
      index = np.argwhere(query_relevancy_labels)[0][0]+1
      return 1/index
    except:
      return 0
    # =======================

def evaluate(qrel_path, results_path):
    results_per_query = {
        'precision@1': [],
        'recall@3': [],
        'recall@50': [],
        'recall@1000': [],
        'F-score@1': [],
        'F-score@5': [],
        'F-score@10': [],
        'F-score@25': [],
        'DCG@1': [],
        'DCG@5': [],
        'DCG@10': [],
        'DCG@25': [],
        'NDCG@10': [],
        'NDCG@100': [],
        'MAP': [],
        'MRR': [],
    }
    for labels in process_files(qrel_path, results_path):
        results_per_query['precision@1'].append(precision(labels, 1))
        results_per_query['recall@3'].append(recall(labels, 3))
        results_per_query['recall@50'].append(recall(labels, 50))
        results_per_query['recall@1000'].append(recall(labels, 1000))
        results_per_query['F-score@1'].append(F_score(labels, 1))
        results_per_query['F-score@5'].append(F_score(labels, 5))
        results_per_query['F-score@10'].append(F_score(labels, 10))
        results_per_query['F-score@25'].append(F_score(labels, 25))
        results_per_query['DCG@1'].append(DCG(labels, 1))
        results_per_query['DCG@5'].append(DCG(labels, 5))
        results_per_query['DCG@10'].append(DCG(labels, 10))
        results_per_query['DCG@25'].append(DCG(labels, 25))
        results_per_query['NDCG@10'].append(NDCG(labels, 10))
        results_per_query['NDCG@100'].append(NDCG(labels, 100))
        results_per_query['MAP'].append(AP(labels))
        results_per_query['MRR'].append(RR(labels))
    
    results = {}
    for key, values in results_per_query.items():
        results[key] = np.mean(values)
    return results


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} qrel.txt testrun.tsv")
        qrel_file = "qrels-v2.txt"
        tsv_file = "testrun.tsv"
        print(f"Now using defaults: {sys.argv[0]} {qrel_file} {tsv_file}")
    else:
        qrel_file = sys.argv[1]
        tsv_file = sys.argv[2]

    Missing_entities = 0
    print(evaluate(qrel_file, tsv_file))
    
    