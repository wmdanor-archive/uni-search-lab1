import string
from collections import Counter

def remove_punctuation(data: str) -> str:
  translator = data.maketrans('', '', string.punctuation)
  formatted = data.translate(translator)

  return formatted.replace('\n', ' ')


def read_document_formatted(document_file_location: str) -> str:
  result = ''

  try:
    with open(document_file_location, 'r', encoding='UTF-8') as file:
      data = file.read()
      result = remove_punctuation(data)
  except Exception as error:
    print('Error', error)

  return result.lower()


def get_most_common_word_count(data: str) -> int:
  _, count = Counter(data.split()).most_common(1)[0]

  return count


def read_documents(documents_files_locations: set) -> dict:
  result = {}

  for document_file_location in documents_files_locations:
    with open(document_file_location, 'r', encoding='UTF-8') as file:
      data = file.read()

    result[document_file_location] = data

  return result
