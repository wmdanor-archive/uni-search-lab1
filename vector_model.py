import os
import sys
import numpy as np
from utils import read_documents, remove_punctuation, get_most_common_word_count, read_document_formatted

def execute():
  documents_dir_location = input('Enter documents directory location (default: "./data/documents"): ')
  if (documents_dir_location == ''): documents_dir_location = './data/documents'
  model = VectorModel(documents_dir_location)

  while True:
    query = input('Enter query ("Ctrl + C" for exit): ')

    result = model.search(query)

    if not result:
      print('No matches')

      continue

    counter = 1
    for key, value in result.items():
      print(f"\n{counter}. {key}\n{value}")
      counter += 1


class VectorModel:
  def __init__(self, documents_dir_location: str) -> None:
    self.documents_locations = [
      os.path.join(documents_dir_location, file) for file in os.listdir(documents_dir_location) if os.path.isfile(os.path.join(documents_dir_location, file))
    ]

    self.terms = self.create_terms()
    self.document_vectors = self.create_documents_vectors()

  def search(self, query: str) -> dict:
    query = remove_punctuation(query).lower()
    query_vector = self.create_vector(query)
    cosine_similarities = {}

    for document_location in self.documents_locations:
      euclidean_norm = np.linalg.norm(query_vector)*np.linalg.norm(self.document_vectors[document_location])

      if euclidean_norm == 0:
        cosine_similarities[document_location] = 0

        continue

      cosine_similarities[document_location] = np.dot(query_vector, self.document_vectors[document_location]) / euclidean_norm

    ranked_documents = self.rank_documents(cosine_similarities)

    return read_documents(ranked_documents)

  def rank_documents(self, cosine_similarities: dict) -> dict:
    for k, v in cosine_similarities.items():
      print(k, v)

    return dict(sorted([(k, v) for k, v in cosine_similarities.items() if 0.0 < v < 0.99], key=lambda item: item[1], reverse=True))

  def create_vector(self, data: str) -> np.ndarray:
    most_common_word_count = get_most_common_word_count(data)

    return np.array([
      self.get_tf_value(data.split().count(term), most_common_word_count) * self.get_idf_value(term) for term in self.terms
    ])

  def create_documents_vectors(self) -> dict:
    result = {}

    for document_location in self.documents_locations:
      document_data = read_document_formatted(document_location)
      result[document_location] = self.create_vector(document_data)

    return result

  def create_terms(self) -> list[str]:
    result = list()

    for document in self.documents_locations:
      data = read_document_formatted(document)
      result.extend(data.split())

    return list(set(result))

  def get_tf_value(self, term_count: int, max_term_count: int) -> float:
    return 0.5 + 0.5 * ( term_count / max_term_count )

  def get_idf_value(self, term: str) -> float:
    N = len(self.documents_locations)
    documents_counter = 0

    for document in self.documents_locations:
      line = read_document_formatted(document)

      if term in line:
        documents_counter += 1

    if N - documents_counter == 0 :
      return -1

    return np.log( (N - documents_counter) / documents_counter )


execute()
