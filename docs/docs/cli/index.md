<!-- markdownlint-disable-file MD033 MD024 -->
# Command Line Interface

## Using PyRailroad

Usage: `py-railroad [OPTIONS] COMMAND [ARGS]...`

Options: `--help` : shows the help message.

Commands:

- `dsl`: parses a DSL FILE for railroad diagrams, based on significant whitespace and writes it into TARGET file.
- `json`: parses a JSON FILE for railroad diagrams and writes it into TARGET file.
- `yaml`: parses a YAML FILE for railroad diagrams and writes it into TARGET file.
- `ebnf`: parses a grammar FILE in EBNF format and writes all the definitions in separate files in the TARGET directory.

For both `json`, `yaml` and `ebnf`, various parameters of the diagram engine can be specified in a PARAMETERS file. For `dsl`, two additional options exist:

- `--simple`: draws the diagram using the "simple" style.
- `--standalone`: embeds a default stylesheet inside the output for rendering.

For `ebnf`, there is another option:

- `--to-json`: writes the diagrams into JSON files instead of SVG files.

Both styles are named so in the original code and haven't been changed (yet).

Examples:

=== "DSL"

    Basic usage:

    ```bash
    py-railroad dsl diagram_source.dsl diagram_output.svg
    ```

    Generate a diagram using the simple style:

    ```bash
    py-railroad dsl diagram_source.dsl diagram_output.svg --simple
    ```

    Generate a standalone diagram:

    ```bash
    py-railroad dsl diagram_source.dsl diagram_output.svg --standalone
    ```

=== "JSON"

    Basic usage (default parameters):

    ```bash
    py-railroad json diagram_source.json diagram_output.svg
    ```

    Usage with a parameters file:

    ```bash
    py-railroad json diagram_source.json diagram_output.svg custom_parameters.json
    ```

=== "YAML"

    Basic usage (default parameters):

    ```bash
    py-railroad yaml diagram_source.json diagram_output.svg
    ```

    Usage with a parameters file:

    ```bash
    py-railroad yaml diagram_source.yaml diagram_output.svg my_parameters.yaml
    ```

=== "EBNF"

    Basic usage:

    ```bash
    py-railroad ebnf grammar.ebnf output_dir
    ```

    Usage with a parameters file:

    ```bash
    py-railroad yaml ebnf grammar.ebnf output_dir my_parameters.json
    ```

    Usage with a parameters file, write JSON files instead of SVG:

    ```bash
    py-railroad yaml ebnf --to-json grammar.ebnf output_dir my_parameters.json
    ```

DSL support was initially developed by [tabatkins](https://github.com/tabatkins) in [railroadparser.py](https://github.com/speced/bikeshed/blob/main/bikeshed/railroadparser.py[) and extended to support all the elements from [railroad-diagrams](https://github.com/tabatkins/railroad-diagrams) that were missing. While complete in terms of elements, customization is limited to simple/complex styles and standalone or not. Several customizations of the diagram and of elements themselves are only available using the JSON or YAML parser.

## Diagram syntax

Diagrams are written in files using one of DSL, JSON or YAML languages. In this section we'll go over the various elements that go in a diagram and the output obtained. Unless otherwise noted, the output show is done using the simple style and no other parameter changed.

There are three categories of elements:

- [Base elements](base_elem.md)
- [Text elements](text_elem.md)
- [Block elements](block_elem.md)

## EBNF Grammar

Unfortunately, there is too much to say and too many variants to explain. This program assumes that you know what you are doing if using EBNF as input.

If you wish to learn more, the [Wikipedia article](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form) might be useful, as well as this [article by  Federico Tomassetti](https://tomassetti.me/ebnf/)
