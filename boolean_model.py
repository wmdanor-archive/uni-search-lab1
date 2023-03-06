import os
import string
from utils import read_documents

def execute():
  terms_file_location = input('Enter terms file location (default: "./data/terms.txt"): ')
  documents_dir_location = input('Enter documents directory location (default: "./data/documents"): ')
  if (terms_file_location == ''): terms_file_location = './data/terms.txt'
  if (documents_dir_location == ''): documents_dir_location = './data/documents'
  model = BooleanModel(terms_file_location, documents_dir_location)

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


class BooleanModel:
  def __init__(self, terms_file_location: str, documents_dir_location: str) -> None:
    self.clauses = []
    self.terms = []

    self.documents_locations = [
      os.path.join(documents_dir_location, file) for file in os.listdir(documents_dir_location) if os.path.isfile(os.path.join(documents_dir_location, file))
    ]

    with open(terms_file_location, 'r', encoding='UTF-8') as file:
      lines = file.readlines()
      for line in lines:
        self.terms.extend(self.parse_terms_line(line))

    self.create_table()

  def search(self, query: str) -> dict:
    self.parse_dnf(query)
    documents = self.get_documents_collisions()

    return read_documents(documents)

  def get_documents_collisions(self) -> set:
    query = set()

    for clause_str in self.clauses:
      clause = []
      is_negative = False
      result_set = set()
      clause = str(clause_str[0]).split(' AND ')

      if len(clause) > 1:
        for _, predicate in enumerate(clause):
          is_negative = False
          current_predicate = predicate.lower()

          if predicate.find('NOT ') != -1:
            is_negative = True
            current_predicate = predicate.split('NOT ')[1].lower()
          if not self.does_term_exist(current_predicate):
            continue
          if len(result_set) == 0:
            if is_negative:
              result_set = set(self.documents_locations).difference(self.table[current_predicate])
            else:
              result_set = self.table[current_predicate]
          else:
            if is_negative:
              result_set = result_set.difference(self.table[current_predicate])
            else:
              result_set = result_set.intersection(self.table[current_predicate])
      else:
        if clause[0].find('NOT') != -1:
          is_negative = True
          clause[0] = clause[0].split('NOT ')[1].lower()

        if not self.does_term_exist(clause[0].lower()):
          continue

        if is_negative:
          result_set = set(self.documents_locations).difference(self.table[clause[0]])
        else:
          result_set = self.table[clause[0].lower()]

      if len(query) == 0:
        query = result_set
      else:
        query = query.union(result_set)

    return query

  def does_term_exist(self, term: str) -> bool:
    return term in self.table

  def create_table(self) -> None:
    table = {}

    for term in self.terms:
      table[term] = set()

      for document_location in self.documents_locations:
        with open(document_location, 'r', encoding='UTF-8') as file:
          for line in file:
            if term in line.lower():
              table[term].add(document_location)

              break

    self.table = table

  def parse_terms_line(self, line: str) -> list[str]:
    lower_case_line = line.lower()
    translator = str.maketrans('', '', string.punctuation)
    translated_line = lower_case_line.translate(translator)

    return list(set(translated_line.split()))

  def parse_dnf(self, dnf: str) -> None:
    self.clauses = []
    clauses = dnf.split(' OR ')

    for clause_str in clauses:
      clause = []
      # extract literals from brackets
      literal_start_index = clause_str.find('(')

      while literal_start_index != -1:
        literal_end_index = clause_str.find(')', literal_start_index)
        clause.append(clause_str[literal_start_index+1:literal_end_index])
        literal_start_index = clause_str.find('(', literal_end_index)

      # if no brackets in the clause, extract literals without brackets
      if not clause:
        clause.append(clause_str)

      self.clauses.append(clause)


execute()
