# dynalist2markdown

## Usage

Generate your API token at Dynalist's [Developer page](https://dynalist.io/developer).

If you have [Nix installed](https://nixos.org):

```sh
$ nix-shell
$ DYNALIST_SECRET_TOKEN=<your token> python3 dynalist2markdown.py <file_id> --output <path>
```

If not, make sure you have the `requests` package available in
the Python installation you'll be using.

## This isn't on PyPI?

I'm being lazy at the moment and pushing this up in a state that's
barely only usable for myself.

## Development

Managing fixtures and running tests:

```sh
$ python -m fixtures update-all
$ python -m fixtures add --file-id <file_id> --name <basename>
$ python -m pytest tests.py
```
