import re

t = open('d:/projects/robot-logic/docs/mujoco-manual/mjwarp/api_CN.md', encoding='utf-8').read()
lines = t.split('\n')
bad = []
for i, line in enumerate(lines, 1):
    s = line.strip()
    if not s:
        continue
    if 'wp.' in line or '`(' in line or '](' in line or s.startswith('['):
        continue
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', s):
        continue
    if re.match(r'^[A-Z][A-Z0-9_]+$', s):
        continue
    if re.match(r'^\([a-z0-9, \n]*\)$', s):
        continue
    # detect when a Chinese character is adjacent (within word boundary) to a latin word
    # find latin words
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', line))
    # latin words of length>=2 not in parentheses
    latin = re.findall(r'[A-Za-z][A-Za-z0-9_]+', line)
    if has_chinese and latin:
        # these are the "cartesian 柔性体 node 位置s" cases -> flag
        bad.append((i, line))

print('suspicious mixed lines:', len(bad))
for b in bad[:100]:
    print(b)
