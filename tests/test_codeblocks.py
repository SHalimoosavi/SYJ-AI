from syj_ai.workflow.codeblocks import extract_file_blocks

SAMPLE = '''
Here is the implementation:

```python:app/main.py
def hello():
    return "hi"
```

And the config:

```json:app/config.json
{"debug": true}
```

Some trailing prose that isn't a file block.
'''


def test_extracts_multiple_blocks():
    blocks = extract_file_blocks(SAMPLE)
    assert len(blocks) == 2
    assert blocks[0].path == "app/main.py"
    assert 'return "hi"' in blocks[0].content
    assert blocks[1].path == "app/config.json"
    assert '"debug": true' in blocks[1].content


def test_no_blocks_returns_empty_list():
    assert extract_file_blocks("just plain text, no code") == []


def test_untagged_block_is_ignored():
    text = "```python\nprint('no path here')\n```"
    assert extract_file_blocks(text) == []
