import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
body = open(os.path.join(ROOT,'src','app.html')).read()
data = open(os.path.join(ROOT,'build','data.json')).read()
body = body.replace('__DATA__', data)
open(os.path.join(ROOT,'build','artifact.html'),'w').write(body)
open(os.path.join(ROOT,'index.html'),'w').write(
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    + body.replace('</div>\n<div id="tip"', '</div>\n<div id="tip"', 1)
      .replace('<title>', '<title>', 1)
      .replace('<div class="wrap">', '</head>\n<body>\n<div class="wrap">', 1)
    + '\n</body>\n</html>\n')
for f in ('build/artifact.html','index.html'):
    print(f, os.path.getsize(os.path.join(ROOT,f)))
