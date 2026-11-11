"""Regression tests for errors that change the study denominator or numerator."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from lxml import etree
from study_common import isbn_pairs,base
from classify_selfpub import match_name,flags
from build_nz_selfpub import parse
class Rules(unittest.TestCase):
 def test_isbn_qualifier_numbers_do_not_corrupt_isbn(self):
  ids,qs=isbn_pairs([('0-306-40615-2 (vol. 2 : pbk.)',''),('9780306406157','hardback')])
  self.assertEqual(ids,['9780306406157']);self.assertIn('vol. 2',qs[0])
 def test_bad_checksum(self):self.assertEqual(isbn_pairs([('9780306406158','')]),([],[]))
 def test_names(self):
  self.assertEqual(match_name('Smith, John, 1950-','J. Smith'),'compatible_initials')
  self.assertEqual(match_name('Smith, John','Jane Smith'),'')
  self.assertEqual(match_name('Smith, John','Smith Press'),'')
  self.assertEqual(match_name('Éric André','Éditions Éric André'),'exact_name')
  self.assertEqual(match_name('Te Rangi, Hēmi','Hemi Te Rangi'),'exact_name')
 def test_corporate_author_is_not_personal_selfpub(self):
  r=base('nz',pub_year=2000,publishers=['The author'],authors_corporate=['Ministry of Health']);r['isbn13']='9780306406157';f=flags(r)
  self.assertFalse(f['self_pub']);self.assertTrue(f['corporate_self'])
 def test_service_and_mixed_models(self):
  r=base('uk',pub_year=2012,publishers=['The Book Guild']);r['isbn13']='9780306406157';f=flags(r)
  self.assertFalse(f['self_pub']);self.assertTrue(f['service_mixed'])
  r['publishers']=['Matador'];self.assertTrue(flags(r)['self_pub'])
 def test_9798_not_amazon_inference(self):
  r=base('nz',pub_year=2020,publishers=['Example Press']);r['isbn13']='9798000000000';f=flags(r)
  self.assertTrue(f['us_9798']);self.assertFalse(f['amazon_imprint'])
 def test_marc_electronic_and_author_roles(self):
  xml='''<record xmlns="http://www.loc.gov/MARC21/slim"><leader>00000nam a2200000 a 4500</leader><controlfield tag="008">060101s2006    nz            000 0 eng  </controlfield><controlfield tag="007">cr</controlfield><datafield tag="100"><subfield code="a">Smith, John</subfield></datafield><datafield tag="700"><subfield code="a">Brown, Jane</subfield><subfield code="e">illustrator</subfield></datafield><datafield tag="020"><subfield code="a">9780306406157</subfield><subfield code="q">PDF</subfield></datafield></record>'''
  r=parse(etree.fromstring(xml));self.assertFalse(r['is_print']);self.assertEqual(r['authors_personal'],['Smith, John']);self.assertEqual(r['contributors_personal'],['Brown, Jane'])
if __name__=='__main__':unittest.main()
