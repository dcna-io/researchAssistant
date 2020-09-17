import requests
import time

from ..models import Paper


class ScienceDirect:

  def __init__(self, token):
    self.token = token


  def search(self, search_params):
    url = "https://api.elsevier.com/content/search/sciencedirect"
    headers = {'X-ELS-APIKey': self.token,
               'Accept': 'application/json',
               'Content-Type': 'application/json'}
    offset = 0
    data = {
        "qs": search_params['search_string'],
        "date": search_params['date'],
        "display": {
            "offset": offset,
            "sortBy": "date",
            "show": 25
        }
      }
    results = []
    resp = requests.put(url, headers=headers, json=data)
    total_found = resp.json()['resultsFound']
    results = resp.json()['results']
    offset += 25
    #import pdb; pdb.set_trace()
    time.sleep(1)
    while offset < total_found:
      try:
        resp = requests.put(url, headers=headers, json=data)
        try:
          results += resp.json().get('results', "Null")
        except:
          print(resp.text)
        offset += 25
        data['display']['offset'] = offset
      except requests.exceptions.RequestException as e:
        print(resp.text)
        print(resp.status_code)
        raise SystemExit(e)
      time.sleep(5)
    return self.consolidate_results(results)


  def get_abstract(self, doi):
    base_url = "https://api.elsevier.com/content/article/doi/"
    headers = {'X-ELS-APIKey': self.token,
               'Accept': 'application/json',
               'Content-Type': 'application/json'}
    url = base_url + doi
    resp = resp = requests.get(url, headers=headers)
    abstract = resp.json().get('full-text-retrieval-response', "Null").get('coredata', 'Null').get("dc:description", "Null")
    if abstract == None:
      abstract = "Null"
    else:
      abstract = self.sanitize_string(abstract) 
    return abstract


  def consolidate_results(self, search_results):
    papers = {}
    #import pdb; pdb.set_trace()
    for result in search_results:
      paper = Paper()
      paper.doi = result['doi']
      paper.pubdate = result.get("publicationDate", "Null") 
      paper.publication = result.get("publication", "Null") 
      paper.title = self.sanitize_string(result.get('title', "Null"))
      paper.url = result.get('uri', "Null")
      if result.get('authors'):
        authors = ""
        for author in result.get('authors'):
            authors += author.get('name', "Null")+','
      else:
        authors = "Null"
      paper.authors = authors
      paper.abstract = self.get_abstract(paper.doi)
      papers[paper.doi] = paper
    return papers

  
  def sanitize_string(self, string):
    string = string.replace("\n", " ")
    spaces = 0
    char = string[spaces]
    while char == ' ':
      spaces += 1
      char = string[spaces]
    return string[spaces:]