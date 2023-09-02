import dataclasses
import json
import typing as t
from .elements import (
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
    Arrow,
)

from .exceptions import ParseException


@dataclasses.dataclass
class RRCommand:
    name: str
    prelude: str | None
    children: list["RRCommand"]
    text: str | None
    line: int


def parse_json(string: str, properties: {}) -> Diagram | None:
    data = json.loads(string)
    if "element" not in data:
        raise ParseException("Invalid input file : 'element' is missing from the root.")
    if data["element"] != "Diagram":
        input_data = {"element": "Diagram", "items": [data]}
    else:
        input_data = data
    diagram = Diagram.from_dict(input_data, properties)
    return diagram


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
            raise ParseException(
                f"Inconsistent indentation: line {i} is indented less than the first line."
            )

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
    text_names = "T|Terminal|N|NonTerminal|C|Comment|S|Skip|Arrow"
    for i, line in enumerate(lines, 1):
        indent = 0
        while line.startswith(indent_text):
            indent += 1
            line = line[len(indent_text) :]
        if indent > last_indent + 1:
            raise ParseException(
                f"Line {i} jumps more than 1 indent level from the previous line:\n{line.strip()}"
            )
        last_indent = indent
        if re.match(rf"\s*({block_names})\W", line):
            match = re.match(r"\s*(\w+)\s*:\s*(.*)", line)
            if not match:
                raise ParseException(
                    f"Line {i} doesn't match the grammar 'Command: optional-prelude'. Got:\n{line.strip()}"
                )
            command = match.group(1)
            prelude = match.group(2).strip()
            node = RRCommand(
                name=command, prelude=prelude, children=[], text=None, line=i
            )
        elif re.match(r"\s*(MultipleChoice)\W", line):
            match = re.match(r"\s*(\w+)\s*:\s*(\d*)\s*(.*)", line)
            if not match:
                raise ParseException(
                    f"Line {i} doesn't match the grammar 'MultipleChoice: optional-prelude'. Got:\n{line.strip()}"
                )
            command = match.group(1)
            prelude = [match.group(2).strip(), match.group(3).strip()]
            node = RRCommand(
                name=command, prelude=prelude, children=[], text=None, line=i
            )
        elif re.match(rf"\s*({text_names})\W", line):
            match = re.match(r"\s*(\w+)\s*(\"[\w\s/:.-]+\"|[\w\s]+)?:\s*(.*)", line)
            if not match:  # Unreachable?
                raise ParseException(
                    f"Line {i} doesn't match the grammar 'Command [optional prelude]: text'. Got:\n{line.strip()},"
                )
            command = match.group(1)
            if match.group(2):
                prelude = match.group(2).strip().strip('"')
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
            raise ParseException(
                f"Line {i} doesn't contain a valid railroad-diagram command. Got:\n{line.strip()}",
            )

        active_commands[str(indent)].children.append(node)
        active_commands[str(indent + 1)] = node

    diagram = create_diagram(tree, diagram_type=diagram_type)
    assert diagram is None or isinstance(diagram, Diagram)
    return diagram


def create_diagram_node(command: RRCommand, diagram_type: str) -> Diagram:
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return Diagram(*children, type=diagram_type)


def create_terminal_node(command: RRCommand) -> Terminal | None:
    if command.children:
        raise ParseException(
            f"Line {command.line} - Terminal commands cannot have children."
        )
    return Terminal(command.text or "", command.prelude)


def create_non_terminal_node(command: RRCommand) -> NonTerminal | None:
    if command.children:
        raise ParseException(
            f"Line {command.line} - NonTerminal commands cannot have children."
        )
    return NonTerminal(command.text or "", command.prelude)


def create_comment_node(command: RRCommand) -> Comment | None:
    if command.children:
        raise ParseException(
            f"Line {command.line} - Comment commands cannot have children."
        )
    return Comment(command.text or "", command.prelude)


def create_arrow_node(command: RRCommand) -> Comment | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - Arrow commands cannot have preludes."
        )
    if command.children:
        raise ParseException(
            f"Line {command.line} - Arrow commands cannot have children."
        )
    return Arrow(command.text or "right")


def create_skip_node(command: RRCommand) -> Skip | None:
    if command.children:
        raise ParseException(
            f"Line {command.line} - Skip commands cannot have children."
        )
    if command.text:
        raise ParseException(f"Line {command.line} - Skip commands cannot have text.")
    return Skip()


def create_sequence_node(command: RRCommand) -> Sequence | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - Sequence commands cannot have preludes."
        )
    if not command.children:
        raise ParseException(
            f"Line {command.line} - Sequence commands need at least one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return Sequence(*children)


def create_stack_node(command: RRCommand) -> Stack | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - Stack commands cannot have preludes."
        )
    if not command.children:
        raise ParseException(
            f"Line {command.line} - Stack commands need at least one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return Stack(*children)


def create_horizontal_choice_node(command: RRCommand) -> HorizontalChoice | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - HorizontalChoice commands cannot have preludes."
        )
    if not command.children:
        raise ParseException(
            f"Line {command.line} - HorizontalChoice commands need at least one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return HorizontalChoice(*children)


def create_multiple_choice_node(command: RRCommand) -> MultipleChoice | None:
    if (default := command.prelude[0]) == "":
        default = 0
    try:
        default = int(t.cast(str, default))
    except ValueError:
        raise ParseException(  # Unreachable?
            f"Line {command.line} - MultipleChoice preludes must be an integer. Got:\n{command.prelude}"
        )
    if (mc_type := command.prelude[1]) == "":
        mc_type = "any"
    if mc_type not in ["any", "all"]:
        raise ParseException(
            f"Line {command.line} - MultipleChoice type must be any or all."
        )
    if not command.children:
        raise ParseException(
            f"Line {command.line} - MultipleChoice commands need at least one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return MultipleChoice(default, mc_type, *children)


def create_optional_sequence_node(command: RRCommand) -> OptionalSequence | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - OptionalSequence commands cannot have preludes."
        )
    if not command.children:
        raise ParseException(
            f"Line {command.line} - OptionalSequence commands need at least one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return OptionalSequence(*children)


def create_choice_node(command: RRCommand) -> Choice | None:
    if command.prelude == "":
        default = 0
    else:
        try:
            default = int(t.cast(str, command.prelude))
        except ValueError:
            raise ParseException(
                f"Line {command.line} - Choice preludes must be an integer. Got:\n{command.prelude}"
            )
    if not command.children:
        raise ParseException(
            f"Line {command.line} - Choice commands need at least one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return Choice(default, *children)


def create_optional_node(command: RRCommand) -> Choice | None:
    if command.prelude not in (None, "", "skip"):
        raise ParseException(
            f"Line {command.line} - Optional preludes must be nothing or 'skip'. Got:\n{command.prelude}"
        )
    if len(command.children) != 1:
        raise ParseException(
            f"Line {command.line} - Optional commands need exactly one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return optional(children[0], skip=(command.prelude == "skip"))


def create_alternating_sequence_node(command: RRCommand) -> AlternatingSequence | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - AlternatingSequence commands cannot have preludes."
        )
    if len(command.children) != 2:
        raise ParseException(
            f"Line {command.line} - AlternatingSequence commands need exactly two children."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return AlternatingSequence(children[0], children[1])


def create_group_node(command: RRCommand) -> Group | None:
    if len(command.children) != 1:
        raise ParseException(
            f"Line {command.line} - Group commands need exactly one child."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    if command.prelude:
        return Group(children[0], label=command.prelude)
    return Group(children[0])


def create_one_or_more_node(command: RRCommand) -> OneOrMore | None:
    if command.prelude:
        raise ParseException(
            f"Line {command.line} - OneOrMore commands cannot have preludes."
        )
    if not (1 <= len(command.children) <= 2):
        raise ParseException(
            f"Line {command.line} - OneOrMore commands must have one or two children."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    return OneOrMore(*children)


def create_zero_or_more_node(command: RRCommand) -> Choice | None:
    if command.prelude not in (None, "", "skip"):
        raise ParseException(
            f"Line {command.line} - ZeroOrMore preludes must be nothing or 'skip'. Got:\n{command.prelude}"
        )
    if not (1 <= len(command.children) <= 2):
        raise ParseException(
            f"Line {command.line} - ZeroOrMore commands must have one or two children."
        )
    children = [
        _f for _f in [create_diagram(child) for child in command.children] if _f
    ]
    if not children:
        raise ParseException(
            f"Line {command.line} - ZeroOrMore has no valid children."
        )  # Unreachable?
    repeat = children[1] if len(children) == 2 else None
    return zero_or_more(children[0], repeat=repeat, skip=(command.prelude == "skip"))


def create_diagram(command: RRCommand, diagram_type="simple") -> DiagramItem | None:
    """
    From a tree of commands,
    create an actual Diagram class.
    Each command must be {command, prelude, children}
    """
    match command.name:
        case "Diagram":
            return create_diagram_node(command, diagram_type)
        case "T" | "Terminal":
            return create_terminal_node(command)
        case "N" | "NonTerminal":
            return create_non_terminal_node(command)
        case "C" | "Comment":
            return create_comment_node(command)
        case "S" | "Skip":
            return create_skip_node(command)
        case "Arrow":
            return create_arrow_node(command)
        case "And" | "Seq" | "Sequence":
            return create_sequence_node(command)
        case "Stack":
            return create_stack_node(command)
        case "HorizontalChoice":
            return create_horizontal_choice_node(command)
        case "MultipleChoice":
            return create_multiple_choice_node(command)
        case "OptionalSequence":
            return create_optional_sequence_node(command)
        case "Or" | "Choice":
            return create_choice_node(command)
        case "Opt" | "Optional":
            return create_optional_node(command)
        case "AlternatingSequence":
            return create_alternating_sequence_node(command)
        case "Group":
            return create_group_node(command)
        case "Plus" | "OneOrMore":
            return create_one_or_more_node(command)
        case "Star" | "ZeroOrMore":
            return create_zero_or_more_node(command)
        case _:
            raise ParseException(
                f"Line {command.line} - Unknown command '{command.name}'."
            )
