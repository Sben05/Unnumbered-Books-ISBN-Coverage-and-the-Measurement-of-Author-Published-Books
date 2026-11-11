"""Format-invariant author=publisher rule: every publisher token must be a surname token, a given-name token, or a single letter equal to the initial of a given name;
at least one surname token (>=3 letters) and at least one given-name token/initial. Matches 'J. R. Castro', 'José Castro' and 'José Ramos Castro' alike."""
import sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from classify_selfpub import norm
PART_PT={'de','da','do','das','dos','e','del','la','van','von','di'}
PART_ES={'de','del','la','las','los','y','e','i','da','do','dos','van','von','el','di'}
def split_name(n):
 if ',' in n:
  s,g=n.split(',',1);return norm(g).split(),norm(s).split()
 t=norm(n).split();return t[:-1],t[-1:]
def ap_consistent(author,pub_tokens,part):
 """pub_tokens: normalised, corporate-word-stripped publisher tokens (list)."""
 g,s=split_name(author);gs=[x for x in g if x not in part];ss=[x for x in s if x not in part]
 p=[x for x in pub_tokens if x not in part]
 if not gs or not ss or not (2<=len(p)<=6):return False
 ini={x[0] for x in gs};sn=set(ss);gn=set(gs);has_s=has_g=False
 for t in p:
  if t in sn and len(t)>=3:has_s=True
  elif t in gn:has_g=True
  elif len(t)==1 and t in ini:has_g=True
  elif t in sn:has_s=True
  else:return False
 return has_s and has_g
