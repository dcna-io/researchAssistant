import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

from ..models import Paper


class Acm:

  def search(self, search_params):
    url = "https://dl.acm.org/action/doSearch?fillQuickSearch=false&expand=dl&field1=AllField"
    params = {
      'text1':search_params['search_string'] ,
      'AfterYear': search_params['date'],
    }
    resp = requests.get(url, params=params)
    print(resp.request.url)
    soup = bs(resp.text, 'html.parser')

    papers_url = self.get_papers_links(soup)
    papers = {}
    i = 0
    for paper_url in papers_url:
        paper = self.get_paper_metadata(paper_url)
        papers[paper.doi] = paper
        i += 1
        print(i)
    return papers


  def get_paper_metadata(self, paper_url):
    paper = Paper()
    resp = requests.get(paper_url)
    soup = bs(resp.text, 'html.parser')
    print(paper_url)
    paper.title = soup.find_all(class_='citation__title')[0].get_text()
    paper.url = paper_url
    paper.doi = urlparse(paper_url)[2][5:] 
    details = soup.find(class_='issue-item__detail')
    paper.publication = details.find_all('span')[1].get_text()
    paper.pubdate = details.find_all('span')[2].get_text().split(' ')[1].replace(',', '')
    paper.pages = self.sanitize_pages(details)
    paper.abstract = soup.select('.abstractSection > p:nth-child(1)')[0].get_text()
    authors_info = soup.select('div.border-bottom:nth-child(3) > div:nth-child(1)')[0].findAll(class_="loa__author-name")
    authors = ""
    for author in authors_info:
      authors += author.get_text() + ','
    paper.authors = authors
    return paper


  def get_papers_links(self, soup):
    papers_url = []
    base_url = 'https://dl.acm.org'
   # import ipdb; ipdb.set_trace()
    links = soup.find_all(class_="hlFld-Title")
    for link in links:
      papers_url.append(base_url + link.find_all('a')[0].get('href'))
    while soup.select('.pagination__btn--next'):
      next_page = soup.select('.pagination__btn--next')[0].get('href')
      resp = requests.get(next_page)
      soup = bs(resp.text, 'html.parser')
      links = soup.find_all(class_="hlFld-Title") 
      for link in links:
        papers_url.append(base_url + link.find_all('a')[0].get('href'))
    print(papers_url)
    return papers_url

  
  def sanitize_pages(self, details):
    pages = "Null"
    for span in details.find_all('span'):
      if 'Pages' in span:
        page_initial = int(span.split()[1].split('–')[0])
        page_final = int(span.split()[1].split('–')[1])
        pages = page_final - page_initial + 1
        break
    return pages