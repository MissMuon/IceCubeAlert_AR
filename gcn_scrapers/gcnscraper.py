import requests
from urllib.parse import urljoin
import re
import sys


base_url='https://gcn.gsfc.nasa.gov/'
amon_event_lists=['https://gcn.gsfc.nasa.gov/amon_icecube_gold_bronze_events.html',
                   'https://gcn.gsfc.nasa.gov/amon_ehe_events.html',
                   'https://gcn.gsfc.nasa.gov/amon_hese_events.html']

gcn_archives='https://gcn.gsfc.nasa.gov/archives.html'

gcn_latest_circulars='https://gcn.gsfc.nasa.gov/selected.html'


amon_archive_pattern=re.compile(r'>AMON<.+?</td>\s*?<td>\s*?<a href="(.+?)"')

archive_page_text=''
try:
 archive_page=requests.get(gcn_archives)
 archive_page_text=archive_page.text
except Exception as e:
 print('Couldn\'t get archive page: {}'.format(e))

amon_links=amon_archive_pattern.findall(archive_page_text)

for link in amon_links: 
  full_link=urljoin(base_url,link)
  if not full_link in amon_event_lists:
     amon_event_lists.append(full_link)

event_pattern=re.compile(r'href=(.+?)\s*?>\s*?(\d+?)_(\d+?)<')

all_events=[]
for event_list in amon_event_lists:
   events_page_text=''
   try:
     events_page=requests.get(event_list)
     events_page_text=events_page.text
   except Exception as e:
     print('Couldn\'t get event page {} : {}'.format(events_page,e))
   events=event_pattern.findall(events_page_text)
   for (url,run,evn) in events:
     full_ev_url=urljoin(base_url,url)
     #print("{} {} {}".format(full_ev_url,run,evn))
     all_events.append((full_ev_url,run,evn))
print("Got {} events".format(len(all_events)))
circulars_page_text=''
try:
 circulars_page=requests.get(gcn_latest_circulars)
 circulars_page_text=circulars_page.text
except Exception as e:
 print('Couldn\'t get circulars page: {}'.format(e))

older_circulars_pattern=re.compile(r'href="(selected_\d\d\d\d.html)"')
older_circulars=older_circulars_pattern.findall(circulars_page_text)
icecube_pattern=re.compile(r'<a href="(other/icecube_.+?\..+?)">(.+?)</a>')

icecube_links=icecube_pattern.findall(circulars_page_text)
for older in older_circulars:
   full_url=urljoin(base_url,older)
   try:
     circ_page=requests.get(full_url)
     circ_page_text=circ_page.text
     icecube_links.extend(icecube_pattern.findall(circ_page_text))
   except Exception as e:
     print('Couldn\'t get circular page {} : {}'.format(older,e))
print("got all {} icecube circulars...".format(len(icecube_links)))

mentions=[]
evns=[(run,evn,"{}_{}".format(run,evn)) for (url,run,evn) in all_events]
for (ice_link,title) in icecube_links:
   full_url=urljoin(base_url,ice_link)
   page=''
   try:
    circ_page=requests.get(full_url)
    page=circ_page.text
   except:
     continue
   for (a,b,idstr) in evns:
     if idstr in page:
       k=(idstr,full_url,title)
       if not k in mentions:
        mentions.append(k)
import json
for a in mentions:
   print(a)
print("Got {} mentions".format(len(mentions)))
 



