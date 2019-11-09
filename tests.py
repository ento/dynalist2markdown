import io
import json
from pathlib import Path

import pytest

from dynalist2markdown import render


@pytest.mark.parametrize('nodes_file', [
    'fixtures/all-markups.json',
])
def test_render(nodes_file):
    with open(nodes_file) as f:
        nodes = json.load(f)['nodes']
    with open(Path(nodes_file).with_suffix('.md')) as f:
        expected = f.read()
    out = io.StringIO()
    render(out, nodes)
    assert out.getvalue() == expected
