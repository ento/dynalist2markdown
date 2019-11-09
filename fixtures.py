import argparse
import json
from pathlib import Path

from dynalist2markdown import ensure_token, get_document


def _write_doc(path, doc):
    path.write_text(json.dumps(doc, indent=2))
    print(path)


def update_all():
    token = ensure_token()
    for doc_path in Path('fixtures').glob('*.json'):
        doc = json.loads(doc_path.read_text())
        updated = get_document(token, doc['file_id'])
        _write_doc(doc_path, updated)


def add(file_id, name):
    token = ensure_token()
    path = Path('fixtures', name).with_suffix('.json')
    doc = get_document(token, file_id)
    _write_doc(path, doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['add', 'update-all'])
    parser.add_argument('--file-id')
    parser.add_argument('--name')
    args = parser.parse_args()

    if args.command == 'update-all':
        update_all()
    elif args.command == 'all':
        add(args.file_id, args.name)
