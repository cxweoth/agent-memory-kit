#!/usr/bin/env python3
"""Local tool for the agent-memory-kit spec. Reads spec/spec.json from a clone of the kit.

  python3 gen_spec.py <path/to/spec.json> [out_dir, default memory/spec]   spec -> markdown copy
  python3 gen_spec.py --get <kit_dir> [dest, default memory/tools]        copy the kit's tools/ into dest

The copy has one file per section. The rule table also produces rule files in rules/;
BOOT.md collects only the rules whose layer is Boot. VERSION holds the spec version and
the generation date, for the sweep line to compare against the kit's VERSION.
The copy is always generated; never edit it by hand. Moving rule files into your own
3_procedural/ counts as Add or Update and follows the rules.
--get only copies files and reports what is new or changed; it never runs anything."""
import sys, re, json, html, pathlib, datetime, shutil

MARK = '<!-- Generated file; do not edit by hand.'
MODEL = {}


def load(src):
    return json.loads(pathlib.Path(src).read_text(encoding='utf-8'))


def md(t):
    t = re.sub(r'</?(strong|b)>', '**', t)
    t = re.sub(r'</?code>', '`', t)
    t = re.sub(r'<br\s*/?>', ' ', t)
    return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()


def block(b, h='##'):
    out = [h + ' ' + md(b['h3']), '']
    if b['kind'] == 'rules':
        return '\n'.join(out) + rules_md(b['rules']) + '\n'
    if b['kind'] == 'rulefiles':
        return '\n'.join(out) + 'See the files in rules/.\n'
    if b['kind'] == 'toolfiles':
        docs = MODEL.get('toolDocs', {})
        out += ['| Script | What it does |', '|---|---|'] + ['| `%s` | %s |' % (n, md(d.get('desc', '')).replace('|', '\\|')) for n, d in docs.items()]
        for n, d in docs.items():
            if d.get('steps'):
                out += ['', '### %s' % n, ''] + ['%d. %s' % (i + 1, md(x)) for i, x in enumerate(d['steps'])]
        return '\n'.join(out) + '\n'
    if b.get('tree'):
        tree = re.sub(r'<(br|/div)[^>]*>', '\n', b['tree'])
        out += ['```', html.unescape(re.sub(r'<[^>]+>', '', tree)).strip('\n'), '```', '']
    if b['kind'] == 'table':
        cell = lambda c: md(c).replace('|', '\\|')
        out += ['| ' + ' | '.join(map(cell, b['cols'])) + ' |', '|' + '---|' * len(b['cols'])]
        out += ['| ' + ' | '.join(map(cell, r)) + ' |' for r in b['rows']]
        out += [''] if b.get('items') else []
    mark = (lambda i: '%d. ' % (i + 1)) if b['kind'] == 'ol' else (lambda i: '- ')
    out += [mark(i) + md(it) for i, it in enumerate(b.get('items') or [])]
    return '\n'.join(out) + '\n'


def rules_md(rules, h='###'):
    """Rules listed in groups of (types, layer); each rule is prefixed with the operations it applies to."""
    out, last = [], None
    for r in rules:
        key = (', '.join(r['types']), r['layer'])
        if key != last:
            out += ['', '%s %s · %s' % (h, key[0], key[1]), '']
            last = key
        topic = '[%s] ' % md(r['topic']) if r.get('topic') else ''
        tools = ' (tools: %s)' % ', '.join(r['tools']) if r.get('tools') else ''
        no = '%02d ' % r['no'] if r.get('no') else ''
        out.append('- %s[%s] %s%s%s' % (no, '/'.join(r['ops']), topic, md(r['text']), tools))
    return '\n'.join(out).strip('\n') + '\n'


def rule_file_text(f, rules, updated):
    mine = [r for r in rules if r.get('file') == f['name']]
    return ('# %s\n\n## Memory Summary\n- Visibility: Public\n- Brief: %s\n- Upstream: <the episodic that recorded importing this spec>\n'
            '- Access: %s\n- Scope: universal\n- Updated: %s\n\n## Memory Content\n\n%s\n') % (
        re.sub(r'\.md$', '', f['name']), md(f['intro']), f['layer'], updated,
        '\n'.join('- ' + md(r['text']) for r in mine))


def slug(name):
    return re.sub(r'[^A-Za-z0-9_-]+', '_', name).strip('_')


def gen(src, out='memory/spec'):
    global MODEL
    model = load(src)
    MODEL = model
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('*.md'):  # remove only files this tool generated last time; leave anything else alone
        if MARK in old.read_text(encoding='utf-8')[:300]:
            old.unlink()
    today = datetime.date.today()
    version = model.get('version', '?')
    head = '%s Source: %s v%s; generated on %s -->\n\n' % (MARK, md(model['title']), version, today)
    # the sweep line compares line 1 with the kit's VERSION; memory_check.py reads the date on line 2
    (out / 'VERSION').write_text('%s\n%s\n' % (version, today), encoding='utf-8')
    for i, sec in enumerate(model['sections']):
        name = md(sec['name'])
        body = '\n'.join(block(b) for b in sec['blocks'])
        path = out / ('%02d_%s.md' % (i, slug(name)))
        # the H1 must be on the first line, or memdoc.py will not recognize the file
        path.write_text('# %s\n\n%s`%s`\n\n%s' % (name, head, md(sec['path']), body), encoding='utf-8')
    rules = [r for sec in model['sections'] for b in sec['blocks'] if b['kind'] == 'rules' for r in b['rules']]
    rdir = out / 'rules'
    rdir.mkdir(exist_ok=True)
    names = [f['name'] for f in model.get('ruleFiles', [])]
    for f in model.get('ruleFiles', []):
        (rdir / pathlib.Path(f['name']).name).write_text(rule_file_text(f, rules, model.get('updated', '')), encoding='utf-8')
    stale = [p.name for p in rdir.glob('*.md') if p.name not in names]  # never deleted, only reported
    if stale:
        print('These rule files are no longer in the spec: ' + ', '.join(stale))
    # BOOT.md holds only the rules whose layer is Boot, and no section content
    (out / 'BOOT.md').write_text('# Boot layer\n\n' + head + rules_md([r for r in rules if r['layer'] == 'Boot'], '##'), encoding='utf-8')
    print('%s v%s: %d sections, %d rule files -> %s' % (md(model['title']), version, len(model['sections']), len(names), out))


def get(kit, dest='memory/tools'):
    src = pathlib.Path(kit) / 'tools'
    if not src.is_dir():
        sys.exit('No tools/ directory in %s; pass the path of your kit clone.' % kit)
    dest = pathlib.Path(dest)
    changed = 0
    for p in sorted(src.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        rel = p.relative_to(src)  # keep subfolders, e.g. UserPromptSubmit/now.py
        target = dest / rel
        if not target.exists():
            state = 'new'
        elif target.read_bytes() == p.read_bytes():
            state = 'same'
        else:
            state = 'changed'
        if state != 'same':
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            changed += 1
        print('%-8s %s' % (state, target))
    print('%d file(s) new or changed. Review them with git diff before running anything.' % changed)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
    elif args[0] == '--get':
        if len(args) < 2:
            sys.exit('usage: gen_spec.py --get <kit_dir> [dest]')
        get(*args[1:3])
    else:
        gen(*args[:2])
