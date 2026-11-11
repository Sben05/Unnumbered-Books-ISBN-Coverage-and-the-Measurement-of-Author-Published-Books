"""Streaming reader for BNP MARCXchange (UNIMARC) files -> dict records."""
import xml.etree.ElementTree as ET
NS='{info:lc/xmlns/marcxchange-v1}'
def records(path):
 for _,el in ET.iterparse(path,events=('end',)):
  if el.tag!=NS+'record':continue
  r={'leader':(el.find(NS+'leader').text or '') if el.find(NS+'leader') is not None else ''}
  for c in el:
   if c.tag==NS+'controlfield':r.setdefault(c.get('tag'),[]).append(c.text or '')
   elif c.tag==NS+'datafield':r.setdefault(c.get('tag'),[]).append((c.get('ind1'),c.get('ind2'),[(s.get('code'),s.text or '') for s in c]))
  yield r
  el.clear()
