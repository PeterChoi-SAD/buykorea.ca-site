import json,re
from urllib.parse import urlparse,unquote
d=json.load(open('tools/extracted.json'))
PERSONAL=('hanmail.net','naver.com','gmail.com','daum.net','kakao.com')
def local(u):
    if not u: return ''
    p=unquote(urlparse(u).path)
    i=p.find('/wp-content/uploads/')
    return 'assets/uploads/'+p[i+len('/wp-content/uploads/'):] if i>=0 else ''
imgs=set()
vs=[]
for v in d['vendors']:
    e=v['email']
    hide=any(e.lower().endswith(x) for x in PERSONAL)
    img=local(v['image']); 
    if v['image']: imgs.add(v['image'])
    web=v['website']
    if web and not web.startswith('http'): web='http://'+web
    vs.append(dict(id=v['id'],name=v['title'],slug=v['slug'],category=(v['categories'] or [''])[0],
      region=(v['locations'] or [''])[0],phone=v['phone'].replace('+82 ','+82-',1) if v['phone'] else '',
      email=e,hide_email=hide,website=web,address=v['address'],image=img,
      description=re.sub('<[^>]+>','',v['body']).strip(),old_url=v['old_url']))
ns=[]
for n in d['news']:
    body=n['body']
    for u in re.findall(r'src="([^"]+)"',body):
        imgs.add(u); body=body.replace(u,local(u))
    if n['image']: imgs.add(n['image'])
    ns.append(dict(id=n['id'],title=n['title'],date=n['date'],image=local(n['image']),
      body=body,source_url='',old_url=n['old_url']))
json.dump(vs,open('data/vendors.json','w'),ensure_ascii=False,indent=1)
json.dump(ns,open('data/news.json','w'),ensure_ascii=False,indent=1)
open('IMAGES_TO_DOWNLOAD.txt','w').write('\n'.join(sorted(imgs))+'\n')
print(len(vs),len(ns),len(imgs))
