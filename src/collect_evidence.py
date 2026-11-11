"""Save supporting public pages/PDFs without overwriting existing evidence."""
import sys,re,concurrent.futures
from pathlib import Path
from urllib.parse import urljoin,unquote
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from bs4 import BeautifulSoup
from acquire_selfpub import download
URLS={
'nz_isbn_2006.pdf':'https://hint.co.nz/pdfs/New_Zealand_Standard_Book_Numbering_Agency_%28ISBN%29__factsheet.pdf',
'qc_isbn_guide.pdf':'https://www.banq.qc.ca/sites/default/files/2022-08/Guide_ISBN.pdf',
'qc_selfpublishing_guide.pdf':'https://www.banq.qc.ca/sites/default/files/2022-08/Guide_autoedition_Qc.pdf',
'nz_publishing_2023.html':'https://natlib.govt.nz/events/time-to-publish-national-library-services-for-publishers-and-authors-august-15-2023',
'afnil_tarification.html':'https://www.afnil.org/tarification/',
'afnil_history_2019.html':'https://gaellekermen.net/2016/06/10/publication-afnil-et-isbn/',
'nielsen_prices.html':'https://www.nielsenisbnstore.com/Home/Isbn',
'bnf_selfdeposit.html':'https://www.bnf.fr/fr/le-depot-legal-de-lautoedition-la-bnf',
'bnb_scope.html':'https://www.ifla.org/g/bibliography/british-national-bibliography/',
'bnb_exclusions.html':'https://www.ifla.org/g/bibliography/scoping-and-selection-use-cases/',
'lulu.html':'https://www.lulu.com/',
'authorhouse.html':'https://www.authorhouse.com/en',
'xlibris.html':'https://www.xlibris.com/en',
'iuniverse.html':'https://www.iuniverse.com/en',
'trafford.html':'https://www.trafford.com/en',
'matador.html':'https://matadorpublishers.com/',
'grosvenorhouse.html':'https://www.grosvenorhousepublishing.co.uk/',
'feedaread.html':'https://www.feedaread.com/',
'copy_press.html':'https://www.copypress.co.nz/',
'maryegan.html':'https://www.maryegan.co.nz/',
'bookprint.html':'https://bookprint.co.nz/',
'bod.html':'https://www.bod.fr/',
'edilivre.html':'https://www.edilivre.com/',
'publibook.html':'https://www.publibook.com/',
'editionsdunet.html':'https://www.leseditionsdunet.com/',
'librinova.html':'https://www.librinova.com/',
'bookedition.html':'https://www.thebookedition.com/fr/',
'kdp_isbn.html':'https://kdp.amazon.com/en_US/help/topic/G201834170',
'newgeneration.html':'https://www.newgeneration-publishing.com/',
'youcaxton.html':'https://www.youcaxton.co.uk/',
'silverwood.html':'https://www.silverwoodbooks.co.uk/',
'bookguild.html':'https://www.bookguild.co.uk/',
'pegasus.html':'https://pegasuspublishers.com/',
'olympia.html':'https://olympiapublishers.com/',
'austinmacauley.html':'https://www.austinmacauley.com/',
}
def main():
 s=BeautifulSoup((ROOT/'data/raw/research/bnf_observatoire.html').read_text(),'html.parser')
 for a in s.select('a[href]'):
  u=urljoin('https://www.bnf.fr',a['href']);label=a.get_text(' ',strip=True)
  if ('Livres' in label and '.xls' in u) or ('synthèse' in label and '.pdf' in u):
   name=unquote(u.split('/')[-1]);URLS[name]=u
 def work(kv):
  name,u=kv
  try:return str(download(u,'data/raw/evidence/'+name,'Public evidence; underlying rights apply',u.split('/')[2]))
  except Exception as e:return name+': '+repr(e)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for result in ex.map(work,URLS.items()):print(result,flush=True)
if __name__=='__main__':main()
