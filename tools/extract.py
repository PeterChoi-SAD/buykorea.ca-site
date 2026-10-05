import json, sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote

W='{http://wordpress.org/export/1.2/}'
C='{http://purl.org/rss/1.0/modules/content/}'

tree = ET.parse(sys.argv[1])
items = tree.getroot().find('channel').findall('item')

def meta(it):
    d={}
    for pm in it.findall(W+'postmeta'):
        d[pm.find(W+'meta_key').text]=pm.find(W+'meta_value').text
    return d

att={}
for it in items:
    if it.find(W+'post_type').text=='attachment':
        att[it.find(W+'post_id').text]=it.find(W+'attachment_url').text

def clean(s):
    return (s or '').strip()

vendors=[]
news=[]
for it in items:
    pt=it.find(W+'post_type').text
    st=it.find(W+'status').text
    if st!='publish': continue
    title=clean(it.find('title').text)
    pid=it.find(W+'post_id').text
    date=it.find(W+'post_date').text
    body=clean(it.find(C+'encoded').text)
    link=it.find('link').text
    if pt=='at_biz_dir':
        m=meta(it)
        cats=[c.text for c in it.findall('category') if c.get('domain')=='at_biz_dir-category']
        locs=[c.text for c in it.findall('category') if c.get('domain')=='at_biz_dir-location']
        lat,lng=m.get('_manual_lat'),m.get('_manual_lng')
        if lat=='49.2608724': lat=lng=None   # plugin default (Vancouver), not the vendor's location
        img=att.get(m.get('_listing_prv_img') or m.get('_thumbnail_id') or '')
        vendors.append(dict(id=int(pid),title=title,slug=unquote(link.rstrip('/').split('/')[-1]),
            old_url=link,date=date[:10],categories=cats,locations=locs,
            phone=clean(m.get('_phone')),email=clean(m.get('_email')),website=clean(m.get('_website')),
            address=clean(m.get('_address')),lat=lat,lng=lng,image=img,body=body))
    elif pt=='kboard':
        m=meta(it)
        news.append(dict(id=int(pid),title=title,old_url=link,date=date[:10],
            image=att.get(m.get('_thumbnail_id') or ''),body=body))

vendors.sort(key=lambda v:v['id'])
news.sort(key=lambda n:n['date'],reverse=True)
json.dump(dict(vendors=vendors,news=news),open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(vendors),'vendors',len(news),'news')
for v in vendors: print(v['id'],v['title'],v['categories'],v['locations'],'IMG' if v['image'] else 'noimg','body' if v['body'] else '-')
for n in news: print(n['id'],n['date'],n['title'][:30],'IMG' if n['image'] else 'noimg')
