import re, json, html, glob

def find_all_p(summary):
    return re.findall(r'<p[^>]*>(.*?)</p>', summary, re.S)

records, seen = [], set()
files = sorted(glob.glob('pages/page-*.html'), key=lambda f: int(re.search(r'page-(\d+)', f).group(1)))
for f in files:
    h = open(f, encoding='utf-8', errors='replace').read()
    for a in re.findall(r'<article class="entry content-bg loop-entry.*?</article>', h, re.S):
        m = re.search(r'<h2 class="entry-title">\s*<a href="([^"]+)"[^>]*>(.*?)</a>', a, re.S)
        if not m:
            continue
        post_url, title = m.group(1), html.unescape(re.sub(r'<[^>]+>', '', m.group(2)).strip())
        summary = (re.search(r'<div class="entry-summary">(.*?)</div>', a, re.S) or [None])
        summary = re.search(r'<div class="entry-summary">(.*?)</div>\s*<!--', a, re.S)
        summary = summary.group(1) if summary else ''
        # screenshot: prefer the resource__image, else any wp image, else any img
        im = (re.search(r'<img[^>]*class="[^"]*resource__image[^"]*"[^>]*src="([^"]+)"', summary)
              or re.search(r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*resource__image', summary)
              or re.search(r'<img[^>]*src="([^"]+)"', summary))
        img = im.group(1) if im else None
        # external link = first "Visit" style button; fallback to post page
        u = re.search(r'<a class="button[^"]*"[^>]*href="([^"]+)"', summary)
        url = html.unescape(u.group(1) if u else post_url)
        # description: first paragraph with real text once img/buttons are removed
        desc = ''
        for p in find_all_p(summary):
            if 'class="button' in p:
                continue
            t = re.sub(r'<img[^>]*>', '', p)
            t = re.sub(r'<br\s*/?>', ' ', t)
            t = html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
            if len(t) > 5:
                desc = re.sub(r'\s+', ' ', t)
                break
        if not title:
            continue
        key = (title.lower(), url)
        if key in seen:
            continue
        seen.add(key)
        records.append({'t': title, 'd': desc, 'img': img, 'u': url})

for r in records:
    r['img'] = html.unescape(r['img'])
    if r['img'].startswith('http://'):
        r['img'] = 'https://' + r['img'][7:]

print('total cards:', len(records))
print('missing img:', sum(1 for r in records if not r['img']))
print('missing desc:', sum(1 for r in records if not r['d']))
print('missing url:', sum(1 for r in records if not r['u']))
json.dump(records, open('data.json','w'), ensure_ascii=False, separators=(',',':'))
