import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

ms = re.findall(r'document\.getElementById\(([\''\"])(.+?)\1\)\.textContent\s*=', text)
print('Found:', ms)
