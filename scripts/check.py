#!/usr/bin/env python3
"""Data, CSV import and generated HTML checks (not browser tests)."""
import json,copy,re
from html.parser import HTMLParser
from pathlib import Path
from build import ROOT,validate,PUBLICATION_TYPES
from import_csv import read_csv,import_catalog
catalog=json.loads((ROOT/'data/catalog.json').read_text());pubs=catalog['publications'];topics=catalog['topics'];validate(pubs,topics)
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.articles=[];self.hrefs=[];self.assets=[];self.checks=[];self.types=[];self.current=None;self.heading=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='article':self.current={**a,'links':[],'title_links':[],'medals':0};self.articles.append(self.current)
  if tag=='h3':self.heading=True
  if tag=='svg' and self.current is not None and a.get('class')=='award-medal':self.current['medals']+=1
  if tag=='a' and self.current is not None:
   self.current['links'].append(a)
   if self.heading:self.current['title_links'].append(a)
  if tag=='a':self.hrefs.append(a.get('href',''))
  if tag=='script' and a.get('src'):self.assets.append(a['src'])
  if tag=='link' and a.get('rel')=='stylesheet':self.assets.append(a['href'])
  if tag=='input' and a.get('type')=='checkbox':(self.types if a.get('name')=='publication_type' else self.checks).append(a['value'])
 def handle_endtag(self,tag):
  if tag=='article':self.current=None
  if tag=='h3':self.heading=False
page=Page();page.feed((ROOT/'index.html').read_text())
assert len(page.ids)==len(set(page.ids)), 'Duplicate HTML IDs'
assert {p['id'] for p in pubs}=={p['id'] for p in page.articles}, 'Missing/extra rendered publication'
assert len(page.articles)==len(pubs)
assert set(page.checks)=={t['id'] for t in topics}
assert set(page.types)==set(PUBLICATION_TYPES)
rendered={p['id']:p for p in page.articles}
for p in pubs:
 a=rendered[p['id']]
 assert a['data-type']==p['publication_type']
 assert a['data-year']==str(p['year'])
 assert not a['title_links'], 'Titles must be plain text'
 paper_links=[link for link in a['links'] if link.get('aria-label','').startswith('Paper: ')]
 assert len(paper_links)==bool(p.get('paper_url')), p['id']
 assert len(a['links'])==len({link['href'] for link in a['links']}), 'Duplicate link'
assert rendered['pub-012']['medals']==1
assert rendered['pub-039']['medals']==1
assert rendered['pub-032']['medals']==0
assert re.search(r'id="clear-topics"[^>]*>All publications</button>',(ROOT/'index.html').read_text())
assert all((ROOT/a).is_file() for a in page.assets), 'Missing asset'
assert all(not h.startswith(('javascript:','file:','data:')) for h in page.hrefs)
assert all('X-Amz-' not in h for h in page.hrefs), 'Temporary signed URL published'
roundtrip=import_catalog(read_csv(ROOT/'data/publications.csv'),read_csv(ROOT/'data/topics.csv'),catalog)
for a,b in zip(pubs,roundtrip['publications']):
 for k in ['id','year','title','authors','venue','publication_type','paper_url','remarks','topics','links']:assert a.get(k)==b.get(k),(a['id'],k)
# Invalid changes must be refused before a build or data replacement.
for mutate in [lambda c:c['publications'][0].update(publication_type='invalid'),lambda c:c['publications'][0].update(topics=['does-not-exist']),lambda c:c['publications'][0].update(paper_url='javascript:alert(1)'),lambda c:c['publications'][0].update(year='2026'),lambda c:c['publications'].append(copy.deepcopy(c['publications'][0]))]:
 invalid=copy.deepcopy(catalog);mutate(invalid)
 try:validate(invalid['publications'],invalid['topics'])
 except ValueError:pass
 else:raise AssertionError('Invalid input was accepted')
# A genuinely new category and paper need only data changes, not a code edit.
pr=read_csv(ROOT/'data/publications.csv');tr=read_csv(ROOT/'data/topics.csv');tr.append({'label':'Test topic','id':'test-topic'})
pr.append({'title':'CSV regression fixture','authors':'Example Author','venue':'Example Venue','publication_type':'conference','year':'2026','paper_url':'https://example.org/paper','topics':'Test topic; Discourse','remarks':'A comma, a quote " and Unicode: ü'})
new=import_catalog(pr,tr,catalog);assert new['publications'][-1]['topics']==['test-topic','discourse'];assert len(new['publications'])==len(pubs)+1
assert 'Test topic' not in {t['label'] for t in topics}, 'Test mutated source data'
print(f'PASS: {len(pubs)} records rendered once; {len(topics)} topics; all assets exist.')
print('PASS: CSV round trip, new-topic import, and invalid-data rejection.')
print('PASS: publication types, plain titles, unique paper links, award medals and sidebar count removal.')
