import re

t = open('d:/projects/robot-logic/docs/mujoco-manual/mjwarp/api.md', encoding='utf-8').read()
lines = t.split('\n')
descs = set()
for line in lines:
    s = line.strip()
    if not s:
        continue
    if s == 'Type:':
        continue
    if 'wp.' in line or 'warp.' in line or '](' in line or s.startswith('[') or '`' in line:
        continue
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', s):
        continue
    if re.match(r'^[A-Z][A-Z0-9_]+$', s):
        continue
    if re.match(r'^\([a-z0-9, \n]*\)$', s):
        continue
    if re.match(r'^_class _', s) or re.match(r'^step\(', s) or re.match(r'^[a-z_]+\(', s):
        continue
    descs.add(s)

for d in sorted(descs):
    print(d)
print('TOTAL', len(descs))
