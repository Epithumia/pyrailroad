# Release notes

## v0.3.0

First release. This is on par with [tabatkins' railroad.py](https://github.com/tabatkins/railroad-diagrams/blob/gh-pages/railroad.py) with a couple fixes.

- CLI functionality is mostly complete, and documented;
  - Parser for [Bikeshed DSL](https://speced.github.io/bikeshed/#railroad)
  - Parser for Json
  - Parser for YAML
- library usage needs documentation.

## v0.3.1

- Added an Arrow element to have diagrams with explicit orientation of paths.

## v0.3.2

- Added support for external css files in yaml and json mode.

## v0.4.0-pre

- Added parsing of EBNF grammar on a best-effort basis. This notably doesn't include eliminating recursions or reductions. Best used to generate a JSON representation then tweaking that to get the desired result.
