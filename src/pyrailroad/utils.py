from __future__ import annotations
from pathlib import Path

from .elements import Diagram, DiagramItem, Terminal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (  # pragma: no cover
        Generator,
        Sequence as Seq,
        Tuple,
        TypeVar,
    )

    T = TypeVar("T")  # pragma: no cover
    Node = str | DiagramItem  # pragma: no cover


def write_diagram(diagram: Diagram, target: Path, standalone: bool = False):
    with open(target, "w") as t:
        if standalone:
            diagram.write_standalone(t.write)
        else:
            diagram.write_svg(t.write)


def escape_attr(val: str | float) -> str:
    if isinstance(val, str):
        return val.replace("&", "&amp;").replace("'", "&apos;").replace('"', "&quot;")
    return f"{val:g}"


def escape_html(val: str) -> str:
    return escape_attr(val).replace("<", "&lt;")


def determine_gaps(
    outer: float, inner: float, internal_alignment: str
) -> Tuple[float, float]:
    diff = outer - inner
    if internal_alignment == "left":
        return 0, diff
    elif internal_alignment == "right":
        return diff, 0
    else:
        return diff / 2, diff / 2


def double_enumerate(seq: Seq[T]) -> Generator[Tuple[int, int, T], None, None]:
    length = len(list(seq))
    for i, item in enumerate(seq):
        yield i, i - length, item


def add_debug(el: DiagramItem) -> None:
    if not el.parameters["debug"]:
        return
    el.attrs["data-x"] = "{0} w:{1} h:{2}/{3}/{4}".format(
        type(el).__name__, el.width, el.up, el.height, el.down
    )


def wrap_string(value: Node) -> DiagramItem:
    return value if isinstance(value, DiagramItem) else Terminal(value)
