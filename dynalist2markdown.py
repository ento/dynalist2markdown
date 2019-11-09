#!/usr/bin/env python3
from typing import TextIO
import os
import sys
import argparse
import json
import textwrap
import dataclasses

import requests


def get_document(token: str, file_id: str) -> list:
    endpoint = 'https://dynalist.io/api/v1/doc/read'
    headers = {
        'Content-Type': 'application/json',
        # urllib.request's default User-Agent is blacklisted;
        # preemptively use our own in case requests's gets blacklisted too
        'User-Agent': 'dyanlist-export',
    }
    params = {'token': token, 'file_id': file_id}
    res = requests.post(endpoint, json=params, headers=headers).json()

    # API doc says _code will be 'OK' but the actual response says 'Ok'.
    # Normalize to futureproof.
    if res['_code'].lower() != 'ok':
        print(res['_msg'], file=sys.stderr)
        sys.exit(1)
    return res


@dataclasses.dataclass
class RenderState:
    nodes_by_id: dict
    under_checkbox: bool
    under_heading: bool
    depth: int
    index: int


def render_node(fp: TextIO, node: dict, state: RenderState):
    is_heading = state.depth == 0 and node.get('heading') is not None
    if is_heading:
        if state.index != 0:
            fp.write('\n')
        fp.write('#' * (node['heading']) + ' ')

    text = ''

    if state.under_checkbox:
        if node.get('checked'):
            text += '[x] '
        else:
            text += '[ ] '

    if state.depth != 0 and node.get('heading') is not None:
        if node.get('content'):
            text += '__' + node.get('content') + '__'
    else:
        text += node.get('content', '')

    if node.get('note'):
        text += '\n' + node['note']

    # The read API doesn't export whether a list is numbered. Hardcode for now
    numbered = False
    if is_heading:
        fp.write(text)
        fp.write('\n')
    else:
        indent_level = state.depth - 1 if state.under_heading else state.depth
        bulleted = (numbered and '1. ' or '* ') + '  '.join(text.splitlines(True))
        fp.write(textwrap.indent(bulleted, '  ' * indent_level))
    fp.write('\n')

    for i, child_id in enumerate(node.get('children', [])):
        new_state = dataclasses.replace(
            state,
            under_heading=state.under_heading or is_heading,
            under_checkbox=state.under_checkbox or bool(node.get('checkbox')),
            depth=state.depth + 1,
            index=i,
        )
        render_node(fp, state.nodes_by_id[child_id], new_state)


def render(fp: TextIO, dynalist_nodes: list):
    by_id = {node['id']: node for node in dynalist_nodes}
    root = by_id['root']
    state = RenderState(
        nodes_by_id=by_id,
        under_checkbox=bool(root.get('checkbox')),
        under_heading=False,
        depth=0,
        index=0,
    )
    for i, child_id in enumerate(root['children']):
        render_node(fp, by_id[child_id], dataclasses.replace(state, index=i))


def main(token: str, args: argparse.Namespace):
    if args.read_raw_from:
        if not os.path.exists(args.read_raw_from):
            print(
                "Specified --read-raw-from path not found:",
                args.read_raw_from,
                file=sys.stderr)
            sys.exit(1)
        with open(args.read_raw_from) as f:
            doc = json.load(f)
    else:
        doc = get_document(token, args.file_id)
    if args.save_raw_to:
        with open(args.save_raw_to, 'w') as f:
            json.dump(doc, f, indent=2)
    with open(args.output, 'w') as f:
        render(f, doc['nodes'])


def ensure_token() -> str:
    secret_token = os.environ.get('DYNALIST_SECRET_TOKEN')
    if not secret_token:
        print("Expected to find your API token in the env var DYNALIST_SECRET_TOKEN", file=sys.stderr)
        sys.exit(1)
    return secret_token


def stripped_string(s: str) -> str:
    '''
    file_id may start with a hyphen '-'. In which case, argparse won't recognize
    it as a valid positional argument: https://bugs.python.org/issue9334
    Workaround is to wrap it in quotes and prefix with a whitespace.
    .strip() will remove the whitespace.
    '''
    return s.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file_id',
        type=stripped_string,
        help='The ID of the document to export. This is the last part of the URL')
    parser.add_argument(
        '--output', '-o',
        metavar='PATH',
        help='Path to write the output to')
    parser.add_argument(
        '--save-raw-to',
        metavar='PATH',
        help='Save the raw response to the specified path')
    parser.add_argument(
        '--read-raw-from',
        metavar='PATH',
        help='Read the raw response from the specified path instead of hitting the API')
    args = parser.parse_args()

    secret_token = None
    if not args.read_raw_from:
        secret_token = ensure_token()
    main(secret_token, args)
