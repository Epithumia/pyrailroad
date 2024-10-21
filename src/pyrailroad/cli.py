import typer

import json
import yaml

from typing_extensions import Annotated, Optional
from pathlib import Path

from .parser import parse_json, parse
from .utils import write_diagram

from rich.markdown import Markdown

cli = typer.Typer(add_completion=False, rich_markup_mode="rich", no_args_is_help=True)

input_file_argument = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        show_default=False,
        help="Path to the input file.",
    ),
]

target_argument = Annotated[
    Path,
    typer.Argument(
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        show_default=False,
        help="Path to the output file.",
    ),
]

parameters_argument = Annotated[
    Optional[Path],
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Path to the parameters file. If omitted, default parameters will be used.",
    ),
]

help_yaml = """
Parses a YAML [bold]FILE[/bold] for railroad diagrams and writes it into [bold]TARGET[/bold] file.
Various parameters of the diagram engine can be specified in a YAML [bold]PARAMETERS[/bold] file.

An input file would look like this:
[italic]
default: 0
element: Choice
items:
- element: Terminal
  text: foo
- element: Terminal
  href: raw
  text: bar
[/italic]
"""


@cli.command("yaml", no_args_is_help=True, help=help_yaml)
def parse_yaml_file(
    file: input_file_argument,
    target: target_argument,
    parameters: parameters_argument = None,
) -> None:
    if parameters:
        with open(parameters) as f:
            params = yaml.safe_load(f.read())
        if "standalone" not in params:
            params["standalone"] = False
        if "css" not in params:
            params["css"] = None
        else:
            with open(params["css"]) as f:
                params["css"] = f.read()
        if "type" not in params:
            params["type"] = "complex"
    else:
        params = {"standalone": False, "type": "complex", "css": None}
    with open(file) as f:
        yaml_input = yaml.safe_load(f.read())
        json_input = json.dumps(yaml_input)
        diagram = parse_json(json_input, params)
    if diagram:
        write_diagram(diagram, target, params["standalone"], params["css"])


help_json = """
Parses a JSON [bold]FILE[/bold] for railroad diagrams and writes it into [bold]TARGET[/bold] file.
Various parameters of the diagram engine can be specified in a JSON [bold]PARAMETERS[/bold] file.

An input file would look like this:
[italic]
{
    "element": "Choice",
    "default": 0,
    "items": [
        {
            "element": "Terminal",
            "text": "foo"
        },
        {
            "element": "Terminal",
            "text": "bar",
            "href": "raw"
        }
    ]
}
[/italic]
"""


@cli.command("json", no_args_is_help=True, help=help_json)
def parse_json_file(
    file: input_file_argument,
    target: target_argument,
    parameters: parameters_argument = None,
) -> None:
    if parameters:
        with open(parameters, "r") as p:
            params = json.loads(p.read())
        if "standalone" not in params:
            params["standalone"] = False
        if "css" not in params:
            params["css"] = None
        else:
            with open(params["css"]) as f:
                params["css"] = f.read()
        if "type" not in params:
            params["type"] = "complex"
    else:
        params = {"standalone": False, "type": "complex", "css": None}
    with open(file) as f:
        diagram = parse_json(f.read(), params)
    if diagram:
        write_diagram(diagram, target, params["standalone"], params["css"])


help_dsl = """
Parses a DSL [bold]FILE[/bold] for railroad diagrams, based on significant whitespace and writes it into [bold]TARGET[/bold] file.

Each command must be on its own line, and is written like "Sequence:\\n".

Children are indented on following lines.

Some commands have non-child arguments, for block commands they are put on the same line, after the :, for text commands they are put on the same line [italic]before[/italic] the :, like:
[italic]
Choice: 0
    Terminal: foo
    Terminal raw: bar
[/italic]
"""


@cli.command("dsl", no_args_is_help=True, help=help_dsl)
def parse_dsl_file(
    file: input_file_argument,
    target: target_argument,
    simple: Annotated[
        bool,
        typer.Option(
            "--simple",
            help="Toggle the simple diagram type. If omitted, uses the complex diagram type.",
        ),
    ] = False,
    standalone: Annotated[
        bool,
        typer.Option(
            "--standalone",
            help="Writes a standalone SVG containing the stylesheet to display it.",
        ),
    ] = False,
) -> None:
    with open(file) as f:
        diagram = parse(f.read(), simple)
    if diagram:
        write_diagram(diagram, target, standalone)


if __name__ == "__main__":
    cli()  # pragma: no cover
