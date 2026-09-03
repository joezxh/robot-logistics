import re, sys

def check(path):
    t = open(path, encoding='utf-8').read()
    lines = t.split('\n')
    bad = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        if s.startswith('#'):
            continue
        tmp = re.sub(r'\[[^\]]*\]\([^)]*\)', '', line)
        tmp = re.sub(r'`[^`]*`', '', tmp)
        tmp = re.sub(r'[A-Za-z_][A-Za-z0-9_."=<>/*\-]*', '', tmp)
        tmp = tmp.strip()
        if tmp and re.search(r'[a-zA-Z]', tmp):
            bad.append((i, line[:140]))
    print(path, '-> remaining english-ish lines:', len(bad))
    for b in bad[:60]:
        print('  ', b)

base = 'd:/projects/robot-logic/docs/mujoco-manual/mjwarp/'
check(base + 'index_CN.md')
check(base + 'api_CN.md')
