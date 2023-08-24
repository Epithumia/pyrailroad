from pathlib import Path

import dataclasses
import typing as t
from .railroad import (
    Diagram,
    Terminal,
    Comment,
    NonTerminal,
    Skip,
    Sequence,
    Stack,
    MultipleChoice,
    Choice,
    HorizontalChoice,
    AlternatingSequence,
    OptionalSequence,
    DiagramItem,
    OneOrMore,
    Group,
    zero_or_more,
    optional,
)
from typing_extensions import Annotated
import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def parse_file(
    file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    target: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
        ),
    ],
    simple: Annotated[bool, typer.Option("--simple")] = False,
    standalone: Annotated[bool, typer.Option("--standalone")] = False,
) -> Diagram:
    with open(file) as f:
        diagram = parse(f.read(), simple)
    if diagram:
        write_diagram(diagram, target, standalone)


def write_diagram(diagram: Diagram, target: Path, standalone: bool = False):
    with open(target, "w") as t:
        if standalone:
            diagram.write_standalone(t.write)
        else:
            diagram.write_svg(t.write)


def parse(string: str, simple: bool) -> Diagram | None:
    """
    Parses a DSL for railroad diagrams, based on significant whitespace.
    Each command must be on its own line, and is written like "Sequence:\n".
    Children are indented on following lines.
    Some commands have non-child arguments;
    for block commands they are put on the same line, after the :,
    for text commands they are put on the same line *before* the :,
    like:
        Choice: 0
            Terminal: foo
            Terminal raw: bar
    """
    import re

    diagram_type = "complex"
    if simple:
        diagram_type = "simple"

    lines = string.splitlines()

    # Strip off any common initial whitespace from lines.
    initial_indent = t.cast(re.Match, re.match(r"(\s*)", lines[0])).group(1)
    for i, line in enumerate(lines):
        if line.startswith(initial_indent):
            lines[i] = line[len(initial_indent) :]
        else:
            print(
                f"Inconsistent indentation: line {i} is indented less than the first line."
            )
            return Diagram()

    # Determine subsequent indentation
    for line in lines:
        match = re.match(r"(\s+)", line)
        if match:
            indent_text = match.group(1)
            break
    else:
        indent_text = "\t"

    # Turn lines into tree
    last_indent = 0
    tree = RRCommand(name="Diagram", prelude="", children=[], text=None, line=0)
    active_commands = {"0": tree}
    block_names = "And|Seq|Sequence|Stack|Or|Choice|Opt|Optional|Plus|OneOrMore|Star|ZeroOrMore|OptionalSequence|HorizontalChoice|AlternatingSequence|Group"
    text_names = "T|Terminal|N|NonTerminal|C|Comment|S|Skip"
    for i, line in enumerate(lines, 1):
        indent = 0
        while line.startswith(indent_text):
            indent += 1
            line = line[len(indent_text) :]
        if indent > last_indent + 1:
            print(
                f"Line {i} jumps more than 1 indent level from the previous line:\n{line.strip()}"
            )
            return Diagram()
        last_indent = indent
        if re.match(rf"\s*({block_names})\W", line):
            match = re.match(r"\s*(\w+)\s*:\s*(.*)", line)
            if not match:
                print(
                    f"Line {i} doesn't match the grammar 'Command: optional-prelude'. Got:\n{line.strip()}"
                )
                return Diagram()
            command = match.group(1)
            prelude = match.group(2).strip()
            node = RRCommand(
                name=command, prelude=prelude, children=[], text=None, line=i
            )
        elif re.match(r"\s*(MultipleChoice)\W", line):
            match = re.match(r"\s*(\w+)\s*:\s*(\d*)\s*(.*)", line)
            if not match:
                print(
                    f"Line {i} doesn't match the grammar 'Command: optional-prelude'. Got:\n{line.strip()}"
                )
                return Diagram()
            command = match.group(1)
            prelude = [match.group(2).strip(), match.group(3).strip()]
            node = RRCommand(
                name=command, prelude=prelude, children=[], text=None, line=i
            )
        elif re.match(rf"\s*({text_names})\W", line):
            match = re.match(r"\s*(\w+)(\s[\w\s]+)?:\s*(.*)", line)
            if not match:
                print(
                    f"Line {i} doesn't match the grammar 'Command [optional prelude]: text'. Got:\n{line.strip()},"
                )
                return Diagram()
            command = match.group(1)
            if match.group(2):
                prelude = match.group(2).strip()
            else:
                prelude = None
            text = match.group(3).strip()
            node = RRCommand(
                name=command,
                prelude=prelude,
                children=[],
                text=text,
                line=i,
            )
        else:
            print(
                f"Line {i} doesn't contain a valid railroad-diagram command. Got:\n{line.strip()}",
            )
            return None

        active_commands[str(indent)].children.append(node)
        active_commands[str(indent + 1)] = node

    diagram = create_diagram(tree, diagram_type=diagram_type)
    assert diagram is None or isinstance(diagram, Diagram)
    return diagram


@dataclasses.dataclass
class RRCommand:
    name: str
    prelude: str | None
    children: list["RRCommand"]
    text: str | None
    line: int


def create_diagram(command: RRCommand, diagram_type="simple") -> DiagramItem | None:
    """
    From a tree of commands,
    create an actual Diagram class.
    Each command must be {command, prelude, children}
    """
    if command.name == "Diagram":
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return Diagram(*children, type=diagram_type)
    if command.name in ("T", "Terminal"):
        if command.children:
            print(f"Line {command.line} - Terminal commands cannot have children.")
            return None
        return Terminal(command.text or "", command.prelude)
    if command.name in ("N", "NonTerminal"):
        if command.children:
            print(f"Line {command.line} - NonTerminal commands cannot have children.")
            return None
        return NonTerminal(command.text or "", command.prelude)
    if command.name in ("C", "Comment"):
        if command.children:
            print(f"Line {command.line} - Comment commands cannot have children.")
            return None
        return Comment(command.text or "", command.prelude)
    if command.name in ("S", "Skip"):
        if command.children:
            print(f"Line {command.line} - Skip commands cannot have children.")
            return None
        if command.text:
            print(f"Line {command.line} - Skip commands cannot have text.")
            return None
        return Skip()
    if command.name in ("And", "Seq", "Sequence"):
        if command.prelude:
            print(f"Line {command.line} - Sequence commands cannot have preludes.")
            return None
        if not command.children:
            print(f"Line {command.line} - Sequence commands need at least one child.")
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return Sequence(*children)
    if command.name in ("Stack",):
        if command.prelude:
            print(f"Line {command.line} - Stack commands cannot have preludes.")
            return None
        if not command.children:
            print(f"Line {command.line} - Stack commands need at least one child.")
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return Stack(*children)
    if command.name in ("HorizontalChoice",):
        if command.prelude:
            print(
                f"Line {command.line} - HorizontalChoice commands cannot have preludes."
            )
            return None
        if not command.children:
            print(
                f"Line {command.line} - HorizontalChoice commands need at least one child."
            )
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return HorizontalChoice(*children)
    if command.name in ("MultipleChoice",):
        if (default := command.prelude[0]) == "":
            default = 0
        try:
            default = int(t.cast(str, default))
        except ValueError:
            print(
                f"Line {command.line} - Choice preludes must be an integer. Got:\n{command.prelude}"
            )
            default = 0
        if (mc_type := command.prelude[1]) == "":
            mc_type = "any"
        if mc_type not in ["any", "all"]:
            print(f"Line {command.line} - MultipleChoice type must be any or all.")
            return None
        if not command.children:
            print(
                f"Line {command.line} - MultipleChoice commands need at least one child."
            )
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return MultipleChoice(default, mc_type, *children)
    if command.name in ("OptionalSequence",):
        if command.prelude:
            print(
                f"Line {command.line} - OptionalSequence commands cannot have preludes."
            )
            return None
        if not command.children:
            print(
                f"Line {command.line} - OptionalSequence commands need at least one child."
            )
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return OptionalSequence(*children)
    if command.name in ("Or", "Choice"):
        if command.prelude == "":
            default = 0
        else:
            try:
                default = int(t.cast(str, command.prelude))
            except ValueError:
                print(
                    f"Line {command.line} - Choice preludes must be an integer. Got:\n{command.prelude}"
                )
                default = 0
        if not command.children:
            print(f"Line {command.line} - Choice commands need at least one child.")
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return Choice(default, *children)
    if command.name in ("Opt", "Optional"):
        if command.prelude not in (None, "", "skip"):
            print(
                f"Line {command.line} - Optional preludes must be nothing or 'skip'. Got:\n{command.prelude}"
            )
            return None
        if len(command.children) != 1:
            print(f"Line {command.line} - Optional commands need exactly one child.")
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return optional(children[0], skip=(command.prelude == "skip"))
    if command.name in ("AlternatingSequence"):
        if command.prelude:
            print(
                f"Line {command.line} - AlternatingSequence commands cannot have preludes."
            )
            return None
        if len(command.children) != 2:
            print(
                f"Line {command.line} - AlternatingSequence commands need exactly two children."
            )
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return AlternatingSequence(children[0], children[1])
    if command.name in ("Group"):
        if len(command.children) != 1:
            print(f"Line {command.line} - Group commands need exactly one child.")
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        if command.prelude:
            return Group(children[0], label=command.prelude)
        return Group(children[0])
    if command.name in ("Plus", "OneOrMore"):
        if command.prelude:
            print(f"Line {command.line} - OneOrMore commands cannot have preludes.")
            return None
        if 0 == len(command.children) > 2:
            print(
                f"Line {command.line} - OneOrMore commands must have one or two children."
            )
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        return OneOrMore(*children)
    if command.name in ("Star", "ZeroOrMore"):
        if command.prelude not in (None, "", "skip"):
            print(
                f"Line {command.line} - ZeroOrMore preludes must be nothing or 'skip'. Got:\n{command.prelude}"
            )
            return None
        if 0 == len(command.children) > 2:
            print(
                f"Line {command.line} - ZeroOrMore commands must have one or two children."
            )
            return None
        children = [
            _f for _f in [create_diagram(child) for child in command.children] if _f
        ]
        if not children:
            print(f"Line {command.line} - ZeroOrMore has no valid children.")
            return None
        repeat = children[1] if len(children) == 2 else None
        return zero_or_more(
            children[0], repeat=repeat, skip=(command.prelude == "skip")
        )
    print(f"Line {command.line} - Unknown command '{command.name}'.")
    return None


if __name__ == "__main__":
    app()
