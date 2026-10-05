#!/usr/bin/env python3
"""정적 사이트 생성: data/*.json -> dist/. 실행: python3 build.py"""
import json,shutil,html,re
from urllib.parse import quote
from pathlib import Path
R=Path(__file__).parent; D=R/'dist'
S=json.load(open(R/'site.json')); V=json.load(open(R/'data/vendors.json')); N=json.load(open(R/'data/news.json'))
N.sort(key=lambda n:n['date'],reverse=True)
e=lambda s:html.escape(str(s or ''),quote=True)
def para(t):
    if '<' in t: return t
    return ''.join(f'<p>{e(p)}</p>' for p in re.split(r'\n\s*\n',t.strip()) if p.strip())
def page(path,title,body,desc='',depth=0,og=''):
    r='../'*depth
    url=f"https://{S['domain']}/{path}"
    h=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc or S['description'])}">
<link rel="canonical" href="{e(url)}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc or S['description'])}">{('<meta property="og:image" content="https://%s/%s">'%(S['domain'],og)) if og else ''}
<link rel="stylesheet" href="{r}style.css"></head><body>
<header><div class="w"><a class="logo" href="{r}">{e(S['name'])}</a><nav><a href="{r}news/">뉴스</a><a href="{r}vendors/">벤더 소개</a><a href="{r}about/">소개</a></nav></div></header>
<main class="w">{body}</main>
<footer><div class="w">© {e(S['company'])} · {e(S['name'])}</div></footer></body></html>'''
    p=D/path/'index.html' if not path.endswith('.html') else D/path
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(h,encoding='utf-8')
def img(src,r,alt='',cls=''):
    return f'<img class="{cls}" src="{r}{e(src)}" alt="{e(alt)}" loading="lazy" onerror="this.style.display=\'none\'">' if src else ''
def vcard(v,r):
    return f'''<a class="card" href="{r}vendors/{quote(v['slug'])}/"><div class="th">{img(v['image'],r,v['name'])}</div><div class="cb"><span class="tag">{e(v['category'])}</span><h3>{e(v['name'])}</h3><p class="m">{e(v['region'])}</p></div></a>'''
def ncard(n,r):
    return f'''<a class="card" href="{r}news/{n['id']}/"><div class="th">{img(n['image'],r,n['title'])}</div><div class="cb"><span class="m">{e(n['date'])}</span><h3>{e(n['title'])}</h3></div></a>'''

if D.exists(): shutil.rmtree(D)
D.mkdir()
shutil.copy(R/'style.css',D/'style.css')
if (R/'assets').exists(): shutil.copytree(R/'assets',D/'assets')
if (R/'CNAME').exists(): shutil.copy(R/'CNAME',D/'CNAME')
(D/'.nojekyll').write_text('')

# home
page('',f"{S['name']} - {S['tagline']}",f'''<section class="hero"><h1>{e(S['tagline'])}</h1><p>{e(S['description'])}</p></section>
<h2>최신 뉴스 <a class="more" href="news/">전체 보기 →</a></h2><div class="grid">{''.join(ncard(n,'') for n in N[:3])}</div>
<h2>벤더 소개 <a class="more" href="vendors/">전체 보기 →</a></h2><div class="grid">{''.join(vcard(v,'') for v in V[:6])}</div>''')
# lists
page('news',f"뉴스 | {S['name']}",f'<h1>뉴스</h1><div class="grid">{"".join(ncard(n,"../") for n in N)}</div>',depth=1)
cats=sorted({v['category'] for v in V if v['category']})
page('vendors',f"벤더 소개 | {S['name']}",f'<h1>벤더 소개</h1><p class="m">분류: {" · ".join(e(c) for c in cats)}</p><div class="grid">{"".join(vcard(v,"../") for v in V)}</div>',depth=1)
# news detail
for n in N:
    page(f"news/{n['id']}",f"{n['title']} | {S['name']}",f'''<article><p class="m">{e(n['date'])}</p><h1>{e(n['title'])}</h1>{img(n['image'],'../../',n['title'],'hero-img')}<div class="body">{para(n['body'].replace('src="assets','src="../../assets'))}</div>{('<p><a href="%s" rel="noopener">원문 보기 →</a></p>'%e(n['source_url'])) if n.get('source_url') else ''}<p><a href="../">← 뉴스 목록</a></p></article>''',desc=re.sub('<[^>]+>','',n['body'])[:120],depth=2,og=n['image'])
# vendor detail
for v in V:
    rows=[('분류',v['category']),('지역',v['region']),('주소',v['address']),('전화',v['phone'])]
    if v['email'] and not v['hide_email']: rows.append(('이메일',f'<a href="mailto:{e(v["email"])}">{e(v["email"])}</a>'))
    if v['website']: rows.append(('웹사이트',f'<a href="{e(v["website"])}" rel="noopener" target="_blank">{e(v["website"])}</a>'))
    tb=''.join(f'<tr><th>{k}</th><td>{x if "<a" in str(x) else e(x)}</td></tr>' for k,x in rows if x)
    page(f"vendors/{v['slug']}",f"{v['name']} | {S['name']}",f'''<article><h1>{e(v['name'])}</h1>{img(v['image'],'../../',v['name'],'logo-img')}{('<div class="body">'+para(v['description'])+'</div>') if v['description'] else ''}<table class="info">{tb}</table><p><a href="../">← 벤더 목록</a></p></article>''',desc=f"{v['name']} - {v['category']} {v['region']}",depth=2,og=v['image'])
# about
page('about',f"소개 | {S['name']}",f'<h1>소개</h1><div class="body"><p>{e(S["name"])}는 {e(S["company"])}가 운영하는 정보 사이트로, 캐나다 시장 진출을 준비하는 한국 기업(벤더)과 관련 뉴스를 소개합니다.</p>'+(f'<p>문의: <a href="mailto:{e(S["contact_email"])}">{e(S["contact_email"])}</a></p>' if S['contact_email'] else '')+'</div>',depth=1)
# sitemap, robots
urls=['']+['news/','vendors/','about/']+[f"news/{n['id']}/" for n in N]+[f"vendors/{v['slug']}/" for v in V]
(D/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f"<url><loc>https://{S['domain']}/{quote(u)}</loc></url>" for u in urls)+'</urlset>')
(D/'robots.txt').write_text(f"User-agent: *\nAllow: /\nSitemap: https://{S['domain']}/sitemap.xml\n")
# 404 + old-URL redirects (GitHub Pages has no server redirects; use meta-refresh stubs)
def redirect(path,to):
    p=D/path/'index.html'; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={to}"><link rel="canonical" href="https://{S["domain"]}{to}"><a href="{to}">이동</a>')
for v in V: redirect(f"directory/{v['slug']}",f"/vendors/{quote(v['slug'])}/")
redirect('directory','/vendors/')
(D/'404.html').write_text(f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/style.css"><main class="w"><h1>페이지를 찾을 수 없습니다</h1><p><a href="/">홈으로</a> · <a href="/news/">뉴스</a> · <a href="/vendors/">벤더 소개</a></p></main></html>')
print('built',len(list(D.rglob('*.html'))),'pages')
