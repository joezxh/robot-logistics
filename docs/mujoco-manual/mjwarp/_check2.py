import re

t = open('d:/projects/robot-logic/docs/mujoco-manual/mjwarp/api_CN.md', encoding='utf-8').read()
lines = t.split('\n')
# Description lines are those that are NOT: '类型：', blank, contain 'wp.', pure identifier,
# start with '[', 'http', '`', or are shape patterns like (nworld, ...)
bad = []
for i, line in enumerate(lines, 1):
    s = line.strip()
    if not s:
        continue
    if s == '类型：':
        continue
    if 'wp.' in line or 'vec' in line or 'warp.' in line or 'dict' in line or 'list' in line or 'tuple' in line or 'bool' in line or 'int' in line or 'float' in line or 'Callable' in line or 'mat' in line:
        continue
    if s.startswith('[') or s.startswith('http') or '](' in line or '`' in line:
        continue
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', s):
        continue
    if re.match(r'^[A-Z][A-Z0-9_]+$', s):
        continue
    # shape pattern e.g. (nworld, nflexnode, 3)
    if re.match(r'^\([a-z0-9, \n]*\)$', s):
        continue
    # detect mixed english words
    # strip known-good chinese+identifier mixes
    tmp = re.sub(r'[A-Za-z_][A-Za-z0-9_]*', '', line)
    tmp = re.sub(r'[\(\)\.,\s]', '', tmp)
    if re.search(r'[a-zA-Z]', tmp):
        bad.append((i, line))

print('mixed/english description lines in api_CN.md:', len(bad))
for b in bad[:80]:
    print(b)
