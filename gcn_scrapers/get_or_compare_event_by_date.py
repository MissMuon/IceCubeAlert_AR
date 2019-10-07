import requests
import difflib
import os
from os.path import exists
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


if len(sys.argv)<2:
 print("Usage: {} datetime <maybefilterhere>".format(sys.argv[0]))
 sys.exit(0)

datestr=sys.argv[1]

try:
 event_filter=sys.argv[2]
except:
  event_filter=None

pat=re.compile("\d\d\d\d\d\d")

if pat.match(datestr) is None:
 print("Usage: {} datetime ...; Datetime should be like 191001".format(sys.argv[0]))
 sys.exit(0)
 

circ_storage_path="./circulars"

try:
 os.makedirs(circ_storage_path)
except:
 pass

url_format="https://gcn.gsfc.nasa.gov/other/icecube_{}{}.gcn3"

suffixes=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

no_suffix_url=url_format.format(datestr,'')


results=[]
try:
 ns_page=requests.get(no_suffix_url)
 if ns_page.status_code<300:
   ns_text=ns_page.text
   if event_filter is None or event_filter in ns_text:
    results.append((datestr,'',ns_text))
except:
 pass

for suf in suffixes:
  suffix_url=url_format.format(datestr,suf)
  try:
   page=requests.get(suffix_url)
   if page.status_code<300:
     text=page.text
     if event_filter is None or event_filter in text:
       results.append((datestr,suf,text))
   else:
     break
  except:
   break

if len(results)==0:
  print("{}")
  sys.exit(0)


diff=[]
for (datestr,suf,txt) in results:
  filename='{}/{}{}.html'.format(circ_storage_path,datestr,suf)
  if exists(filename):
    try:
      fl=open(filename,'r')
      fltext=fl.read()
      fl.close()
    except:
      continue
    lnsbefore=fltext.splitlines(False)
    lnsnow=txt.splitlines(False)
    diffz=difflib.ndiff(lnsbefore,lnsnow)
    lns=[]
    for ln in diffz:
     if ln.startswith('+') and len(ln)>2:
       lns.append(ln[2:])
    if len(lns)==0: #no difference?
     continue
    diffstr='\n'.join(lns)
    diff.append((datestr,suf,diffstr,'upd'))
  else:
   diff.append((datestr,suf,txt,'new'))
  fl=open(filename,'w') #maybe needs trycatch
  fl.write(txt)
  fl.close()
if len(diff)==0:
  print("{}")
  sys.exit(0)

import json
print (json.dumps(diff))
   
