def method(source, signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth = 0
    quote = None
    escaped = False
    line = False
    block = False
    i = brace
    while i < len(source):
        ch = source[i]
        nxt = source[i:i + 2]
        if line:
            if ch == '\n':
                line = False
        elif block:
            if nxt == '*/':
                block = False
                i += 1
        elif quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
        elif nxt == '//':
            line = True
            i += 1
        elif nxt == '/*':
            block = True
            i += 1
        elif ch in ('"', "'"):
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
        i += 1
    raise RuntimeError(signature)
