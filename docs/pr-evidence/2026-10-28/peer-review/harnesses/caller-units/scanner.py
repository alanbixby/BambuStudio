import re

def mask(source):
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern, lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), source)

NAMES = {'create_scaled_bitmap', 'create_scaled_bitmap2', 'ScalableBitmap', 'ScalableButton', 'wxFont', 'wxFontInfo', 'SetPointSize', 'SetFractionalPointSize', 'PointSize', 'Button', 'SideButton', 'ModeButton', 'AnimaIcon', 'sysFont'}

def calls(source, extra_names=()):
    clean = mask(source)
    stack = []
    found = []
    for m in re.finditer(r'[(){}]', clean):
        if m[0] in '({':
            prefix_start = max(0, m.start() - 256)
            name = re.search(r'([A-Za-z_]\w*)\s*$', clean[prefix_start:m.start()])
            stack.append((name[1] if name else '', prefix_start + name.start() if name else m.start(), m.start()))
        elif stack:
            name, start, opening = stack.pop()
            text = source[start:m.end()]
            if name in NAMES or name in extra_names:
                found.append(dict(name=name, line=source.count('\n', 0, start)+1, text=text, code=clean[start:m.end()]))
    return found

