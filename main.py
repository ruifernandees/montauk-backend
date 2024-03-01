import pandas as pd
import json
from difflib import SequenceMatcher
import re
from fuzzywuzzy import fuzz

dataframe = pd.read_csv('./dataset.csv')

legalStructures = {"inc", "llc", "lp", "ltd"} 

def preprocess(name):
  nameWithoutPunctuation = re.sub(r'[^\w\s]', '', name)
  nameWithCorrectWhitespaces = re.sub(r'\s+', ' ', nameWithoutPunctuation)
  nameWithTrim = nameWithCorrectWhitespaces.strip().lower()
  for structure in legalStructures:
    if (nameWithTrim.endswith(structure)):
      nameWithTrim = nameWithTrim.replace(structure, '').strip()
      break
  return nameWithTrim

def fuzzyMatch(name1, name2):
  return fuzz.ratio(name1, name2)

def normalizeCompanyNames(data, column):
  # normalizedName = {}
  possibleGroups = []

  for rowIndex, record in data.iterrows():
    # print(_)
    normalizedName = preprocess(record['organization'])

    if (possibleGroups.count == 0):
      possibleGroups.append([
        {column: normalizedName, 'count': 1, 'rows': [rowIndex]}
      ])
    else:
      chosenGroup = -1
      greatestMatch = 96
      equalItemIndex = -1
      for index, group  in enumerate(possibleGroups):
        for nameIndex, item in enumerate(group):
          name = item[column]
          currentMatch = fuzzyMatch(normalizedName, name)
          # print("currentMatch ", currentMatch, normalizedName, name)
          if (currentMatch > greatestMatch):
            greatestMatch = currentMatch
            chosenGroup = index
          print(name)
          if (normalizedName == name):
            equalItemIndex = nameIndex
          # if (normalizedName == "elta systems ltd"):
          #   print(chosenGroup, greatestMatch, equalItemIndex)
          #   print("currentMatch ", currentMatch, normalizedName, name)
      if (chosenGroup != -1):
        if (equalItemIndex != -1):
          possibleGroups[chosenGroup][equalItemIndex]['count'] += 1 
          possibleGroups[chosenGroup][equalItemIndex]['rows'].append(rowIndex)
        else:
          possibleGroups[chosenGroup].append({column: normalizedName, 'count': 1, 'rows': [rowIndex]})
      else:
        print('CREATE NEW GROUP FOR ', normalizedName)
        possibleGroups.append([
          {column: normalizedName, 'count': 1, 'rows': [rowIndex]}
        ])

  # print(possibleGroups)
  json_object = json.dumps(possibleGroups, indent=4)
  with open("sample.json", "w") as outfile:
    outfile.write(json_object)

  canonical_names = {}
  for groupIndex, group in enumerate(possibleGroups):
    greatestCount = 0
    chosenItemIndex = -1
    for index, item in enumerate(group):
      count = item['count']
      if (count > greatestCount):
        greatestCount = count
        chosenItemIndex = index
    chosenItem = group[chosenItemIndex]
    for index, item in enumerate(group):
      for row in item['rows']:
        data['organization'][row] = chosenItem[column].upper()

  return data
    
result = normalizeCompanyNames(dataframe, 'name')
result = normalizeCompanyNames(result, 'city')
result.to_csv('./result-dataset.csv', sep=',', encoding='utf-8')