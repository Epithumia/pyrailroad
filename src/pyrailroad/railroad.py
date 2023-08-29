# -*- coding: utf-8 -*-
from __future__ import annotations

import math as Math
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Dict,
        Generator,
        List,
        Optional as Opt,
        Sequence as Seq,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    T = TypeVar("T")
    Node = Union[str, DiagramItem]  # type: ignore # pylint: disable=used-before-assignment
    WriterF = Callable[[str], Any]
    WalkerF = Callable[[DiagramItem], Any]  # type: ignore # pylint: disable=used-before-assignment
    AttrsT = Dict[str, Any]

# Display constants
DIAGRAM_CLASS = "railroad-diagram"  # class to put on the root <svg>


class RRException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def escape_attr(val: Union[str, float]) -> str:
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


class DiagramItem:
    def __init__(
        self,
        name: str,
        attrs: Opt[AttrsT] = None,
        text: Opt[Node] = None,
        parameters: Opt[AttrsT] = {},
    ):
        self.name = name
        # up = distance it projects above the entry line
        self.up: float = 0
        # height = distance between the entry/exit lines
        self.height: float = 0
        # down = distance it projects below the exit line
        self.down: float = 0
        # width = distance between the entry/exit lines horizontally
        self.width: float = 0
        # Whether the item is okay with being snug against another item or not
        self.needs_space = False

        # Parameters
        self.parameters = {
            "debug": False,  # if True, add debug info to the diagram
            "stroke_odd_pixel_length": True,
            "diagram_class": "railroad-diagram",  # Default class for the svg diagram
            "VS": 8,  # minimum vertical separation between things. For a 3px stroke, must be at least 4
            "AR": 10,  # radius of arcs
            "char_width": 8,  # width of each monospace character. play until you find the right value for your font
            "comment_char_width": 7,  # comments are in smaller text by default
            "internal_alignment": "center",  # how to align items when they have extra space. left/right/center
        }
        for k in parameters.keys():
            self.parameters[k] = parameters[k]

        # DiagramItems pull double duty as SVG elements.
        self.attrs: AttrsT = attrs or {}
        # Subclasses store their meaningful children as .item or .items;
        # .children instead stores their formatted SVG nodes.
        self.children: List[Union[Node, Path, Style]] = [text] if text else []

    def format(self, x: float, y: float, width: float) -> DiagramItem:
        raise NotImplementedError  # Virtual

    def add_to(self, parent: DiagramItem) -> DiagramItem:
        parent.children.append(self)
        return self

    def write_svg(self, write: WriterF) -> None:
        write("<{0}".format(self.name))
        for name, value in sorted(self.attrs.items()):
            write(' {0}="{1}"'.format(name, escape_attr(value)))
        write(">")
        if self.name in ["g", "svg"]:
            write("\n")
        for child in self.children:
            if isinstance(child, (DiagramItem, Path, Style)):
                child.write_svg(write)
            else:
                write(escape_html(child))
        write("</{0}>".format(self.name))

    def walk(self, cb: WalkerF) -> None:
        cb(self)

    def to_dict(self) -> dict:
        raise NotImplementedError  # Virtual

    @classmethod
    def from_dict(
        cls, data: dict, parameters: dict | None = None
    ) -> DiagramItem | None:
        if "element" not in data.keys():
            return None
        match data["element"]:
            case "Diagram":
                return Diagram(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    type=parameters["type"],
                    parameters=parameters,
                )
            case "Start":
                if "type" not in data.keys() or data["type"] is None:
                    start_type = parameters.get("type", "simple")
                else:
                    start_type = data["type"]
                return Start(start_type, data.get("label", None), parameters=parameters)
            case "End":
                if "type" not in data.keys() or data["type"] is None:
                    end_type = parameters.get("type", "simple")
                else:
                    end_type = data["type"]
                return End(end_type, parameters=parameters)
            case "Terminal":
                return Terminal(
                    text=data["text"],
                    href=data.get("href", None),
                    title=data.get("title", None),
                    cls=data.get("cls", ""),
                    parameters=parameters,
                )
            case "NonTerminal":
                return NonTerminal(
                    text=data["text"],
                    href=data.get("href", None),
                    title=data.get("title", None),
                    cls=data.get("cls", ""),
                    parameters=parameters,
                )
            case "Stack":
                return Stack(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "Choice":
                return Choice(
                    int(data["default"]),
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "HorizontalChoice":
                return HorizontalChoice(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "OptionalSequence":
                return OptionalSequence(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "AlternatingSequence":
                return AlternatingSequence(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "MultipleChoice":
                return MultipleChoice(
                    int(data["default"]),
                    data["type"],
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "Skip":
                return Skip(parameters=parameters)
            case "OneOrMore":
                if "repeat" not in data.keys() or data["repeat"] is None:
                    return OneOrMore(data["item"], parameters=parameters)
                return OneOrMore(
                    DiagramItem.from_dict(data["item"], parameters),
                    DiagramItem.from_dict(data["repeat"], parameters),
                    parameters=parameters,
                )
            case "ZeroOrMore":
                if "repeat" not in data.keys() or data["repeat"] is None:
                    return zero_or_more(
                        DiagramItem.from_dict(data["item"], parameters),
                        skip=data.get("skip", False),
                        parameters=parameters,
                    )
                return zero_or_more(
                    DiagramItem.from_dict(data["item"], parameters),
                    DiagramItem.from_dict(data["repeat"], parameters),
                    skip=data.get("skip", False),
                    parameters=parameters,
                )
            case "Optional":
                return optional(
                    DiagramItem.from_dict(data["item"], parameters),
                    data.get("skip", False),
                    parameters=parameters,
                )
            case "Comment":
                return Comment(
                    text=data["text"],
                    href=data.get("href", None),
                    title=data.get("title", None),
                    cls=data.get("cls", ""),
                    parameters=parameters,
                )
            case "Sequence":
                return Sequence(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),
                    parameters=parameters,
                )
            case "Group":
                if "label" not in data.keys() or data["label"] is None:
                    return Group(
                        item=DiagramItem.from_dict(data["item"], parameters),
                        parameters=parameters,
                    )
                if isinstance(data["label"], str):
                    return Group(
                        item=DiagramItem.from_dict(data["item"], parameters),
                        label=data["label"],
                        parameters=parameters,
                    )
                return Group(
                    item=DiagramItem.from_dict(data["item"], parameters),
                    label=DiagramItem.from_dict(data["label"], parameters),
                    parameters=parameters,
                )
            case _:
                raise RRException("Unknown element")


def apply_properties(properties: dict):
    """Need to make the global parameters not global"""
    pass


class DiagramMultiContainer(DiagramItem):
    def __init__(
        self,
        name: str,
        items: Seq[Node],
        attrs: Opt[Dict[str, str]] = None,
        text: Opt[str] = None,
        parameters: Opt[AttrsT] = {},
    ):
        DiagramItem.__init__(self, name, attrs, text, parameters=parameters)
        self.items: List[DiagramItem] = [wrap_string(item) for item in items]

    def format(self, x: float, y: float, width: float) -> DiagramItem:
        raise NotImplementedError  # Virtual

    def walk(self, cb: WalkerF) -> None:
        cb(self)
        for item in self.items:
            item.walk(cb)


class Path:
    def __init__(self, x: float, y: float, cls: str = None, AR: float = None):
        self.x = x
        self.y = y
        self.AR = AR
        self.attrs = {"d": f"M{x} {y}"}
        if cls is not None:
            self.attrs = {"class": cls, "d": f"M{x} {y}"}

    def m(self, x: float, y: float) -> Path:
        self.attrs["d"] += f"m{x} {y}"
        return self

    def l(self, x: float, y: float) -> Path:
        self.attrs["d"] += f"l{x} {y}"
        return self

    def h(self, val: float) -> Path:
        self.attrs["d"] += f"h{val}"
        return self

    def right(self, val: float) -> Path:
        return self.h(max(0, val))

    def left(self, val: float) -> Path:
        return self.h(-max(0, val))

    def v(self, val: float) -> Path:
        self.attrs["d"] += f"v{val}"
        return self

    def down(self, val: float) -> Path:
        return self.v(max(0, val))

    def up(self, val: float) -> Path:
        return self.v(-max(0, val))

    def arc_8(self, start: str, dir: str) -> Path:
        # 1/8 of a circle
        arc = self.AR
        s2 = 1 / Math.sqrt(2) * arc
        s2inv = arc - s2
        sweep = "1" if dir == "cw" else "0"
        path = f"a {arc} {arc} 0 0 {sweep} "
        sd = start + dir
        offset: List[float]
        match sd:
            case "ncw":
                offset = [s2, s2inv]
            case "necw":
                offset = [s2inv, s2]
            case "ecw":
                offset = [-s2inv, s2]
            case "secw":
                offset = [-s2, s2inv]
            case "scw":
                offset = [-s2, -s2inv]
            case "swcw":
                offset = [-s2inv, -s2]
            case "wcw":
                offset = [s2inv, -s2]
            case "nwcw":
                offset = [s2, -s2inv]
            case "nccw":
                offset = [-s2, s2inv]
            case "nwccw":
                offset = [-s2inv, s2]
            case "wccw":
                offset = [s2inv, s2]
            case "swccw":
                offset = [s2, s2inv]
            case "sccw":
                offset = [s2, -s2inv]
            case "seccw":
                offset = [s2inv, -s2]
            case "eccw":
                offset = [-s2inv, -s2]
            case "neccw":
                offset = [-s2, -s2inv]

        path += " ".join(str(x) for x in offset)
        self.attrs["d"] += path
        return self

    def arc(self, sweep: str) -> Path:
        x = self.AR
        y = self.AR
        if sweep[0] == "e" or sweep[1] == "w":
            x *= -1
        if sweep[0] == "s" or sweep[1] == "n":
            y *= -1
        cw = 1 if sweep in ("ne", "es", "sw", "wn") else 0
        self.attrs["d"] += f"a{self.AR} {self.AR} 0 0 {cw} {x} {y}"
        return self

    def add_to(self, parent: DiagramItem) -> Path:
        parent.children.append(self)
        return self

    def write_svg(self, write: WriterF) -> None:
        write("<path")
        for name, value in sorted(self.attrs.items()):
            write(f' {name}="{escape_attr(value)}"')
        write(" />")

    def format(self) -> Path:
        self.attrs["d"] += "h.5"
        return self

    def __repr__(self) -> str:
        return f"Path({repr(self.x)}, {repr(self.y)})"


def wrap_string(value: Node) -> DiagramItem:
    return value if isinstance(value, DiagramItem) else Terminal(value)


class Style:
    def __init__(self, css: str):
        self.css = css

    def __repr__(self) -> str:
        return f"Style({repr(self.css)})"

    def add_to(self, parent: DiagramItem) -> Style:
        parent.children.append(self)
        return self

    def format(self) -> Style:
        return self

    def write_svg(self, write: WriterF) -> None:
        # Write included stylesheet as CDATA. See https:#developer.mozilla.org/en-US/docs/Web/SVG/Element/style
        cdata = "/* <![CDATA[ */\n{css}\n/* ]]> */\n".format(css=self.css)
        write("<style>{cdata}</style>".format(cdata=cdata))


class Diagram(DiagramMultiContainer):
    def __init__(self, *items: Node, parameters: Opt[AttrsT] = {}, **kwargs: str):
        # Accepts a type=[simple|complex] kwarg
        DiagramMultiContainer.__init__(
            self,
            "svg",
            list(items),
            {
                "class": parameters.get("diagram_class", DIAGRAM_CLASS),
            },
        )
        self.type = kwargs.get("type", "simple")
        if items and not isinstance(items[0], Start):
            self.items.insert(0, Start(self.type))
        if items and not isinstance(items[-1], End):
            self.items.append(End(self.type))
        self.up = 0
        self.down = 0
        self.height = 0
        self.width = 0
        for item in self.items:
            if isinstance(item, Style):
                continue
            self.width += item.width + (20 if item.needs_space else 0)
            self.up = max(self.up, item.up - self.height)
            self.height += item.height
            self.down = max(self.down - item.height, item.down)
        if self.items[0].needs_space:
            self.width -= 10
        if self.items[-1].needs_space:
            self.width -= 10
        self.formatted = False

    def to_dict(self) -> dict:
        return {"element": "Diagram", "items": [i.to_dict() for i in self.items]}

    def __repr__(self) -> str:
        items = ", ".join(map(repr, self.items[1:-1]))
        pieces = [] if not items else [items]
        if self.type != "simple":
            pieces.append(f"type={repr(self.type)}")
        return f'Diagram({", ".join(pieces)})'

    def format(
        self,
        padding_top: float = 20,
        padding_right: Opt[float] = None,
        padding_bottom: Opt[float] = None,
        padding_left: Opt[float] = None,
    ) -> Diagram:
        if padding_right is None:
            padding_right = padding_top
        if padding_bottom is None:
            padding_bottom = padding_top
        if padding_left is None:
            padding_left = padding_right
        assert padding_right is not None
        assert padding_bottom is not None
        assert padding_left is not None
        x = padding_left
        y = padding_top + self.up
        g = DiagramItem("g")
        if self.parameters["stroke_odd_pixel_length"]:
            g.attrs["transform"] = "translate(.5 .5)"
        for item in self.items:
            if item.needs_space:
                Path(x, y, cls="class1", AR=self.parameters["AR"]).h(10).add_to(g)
                x += 10
            item.format(x, y, item.width).add_to(g)
            x += item.width
            y += item.height
            if item.needs_space:
                Path(x, y, cls="class2", AR=self.parameters["AR"]).h(10).add_to(g)
                x += 10
        self.attrs["width"] = str(self.width + padding_left + padding_right)
        self.attrs["height"] = str(
            self.up + self.height + self.down + padding_top + padding_bottom
        )
        self.attrs["viewBox"] = f"0 0 {self.attrs['width']} {self.attrs['height']}"
        g.add_to(self)
        self.formatted = True
        return self

    def write_svg(self, write: WriterF) -> None:
        if not self.formatted:
            self.format()
        return DiagramItem.write_svg(self, write)

    def write_standalone(self, write: WriterF, css: str | None = None) -> None:
        if not self.formatted:
            self.format()
        if css is None:
            from importlib import resources as r
            from . import style

            inp_file = r.files(style) / "default.css"
            with inp_file.open("rt") as f:
                css = f.read()
        Style(css).add_to(self)
        self.attrs["xmlns"] = "http://www.w3.org/2000/svg"
        self.attrs["xmlns:xlink"] = "http://www.w3.org/1999/xlink"
        DiagramItem.write_svg(self, write)
        self.children.pop()
        del self.attrs["xmlns"]
        del self.attrs["xmlns:xlink"]


class Sequence(DiagramMultiContainer):
    def __init__(self, *items: Node, parameters: Opt[AttrsT] = {}):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        self.needs_space = True
        self.up = 0
        self.down = 0
        self.height = 0
        self.width = 0
        for item in self.items:
            self.width += item.width + (20 if item.needs_space else 0)
            self.up = max(self.up, item.up - self.height)
            self.height += item.height
            self.down = max(self.down - item.height, item.down)
        if self.items[0].needs_space:
            self.width -= 10
        if self.items[-1].needs_space:
            self.width -= 10
        add_debug(self)

    def to_dict(self) -> dict:
        return {"element": "Sequence", "items": [i.to_dict() for i in self.items]}

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return f"Sequence({items})"

    def format(self, x: float, y: float, width: float) -> Sequence:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="class3", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class4",
            AR=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap
        for i, item in enumerate(self.items):
            if item.needs_space and i > 0:
                Path(x, y, cls="class5", AR=self.parameters["AR"]).h(10).add_to(self)
                x += 10
            item.format(x, y, item.width).add_to(self)
            x += item.width
            y += item.height
            if item.needs_space and i < len(self.items) - 1:
                Path(x, y, cls="class6", AR=self.parameters["AR"]).h(10).add_to(self)
                x += 10
        return self


class Stack(DiagramMultiContainer):
    def __init__(self, *items: Node, parameters: Opt[AttrsT] = {}):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        self.needs_space = True
        self.width = max(
            item.width + (20 if item.needs_space else 0) for item in self.items
        )
        # pretty sure that space calc is totes wrong
        if len(self.items) > 1:
            self.width += self.parameters["AR"] * 2
        self.up = self.items[0].up
        self.down = self.items[-1].down
        self.height = 0
        last = len(self.items) - 1
        for i, item in enumerate(self.items):
            self.height += item.height
            if i > 0:
                self.height += max(
                    self.parameters["AR"] * 2, item.up + self.parameters["VS"]
                )
            if i < last:
                self.height += max(
                    self.parameters["AR"] * 2, item.down + self.parameters["VS"]
                )
        add_debug(self)

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return f"Stack({items})"

    def to_dict(self) -> dict:
        return {"element": "Stack", "items": [i.to_dict() for i in self.items]}

    def format(self, x: float, y: float, width: float) -> Stack:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="class7", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        x += left_gap
        x_initial = x
        if len(self.items) > 1:
            Path(x, y, cls="class8", AR=self.parameters["AR"]).h(
                self.parameters["AR"]
            ).add_to(self)
            x += self.parameters["AR"]
            inner_width = self.width - self.parameters["AR"] * 2
        else:
            inner_width = self.width
        for i, item in enumerate(self.items):
            item.format(x, y, inner_width).add_to(self)
            x += inner_width
            y += item.height
            if i != len(self.items) - 1:
                (
                    Path(x, y, cls="class9", AR=self.parameters["AR"])
                    .arc("ne")
                    .down(
                        max(
                            0,
                            item.down
                            + self.parameters["VS"]
                            - self.parameters["AR"] * 2,
                        )
                    )
                    .arc("es")
                    .left(inner_width)
                    .arc("nw")
                    .down(
                        max(
                            0,
                            self.items[i + 1].up
                            + self.parameters["VS"]
                            - self.parameters["AR"] * 2,
                        )
                    )
                    .arc("ws")
                    .add_to(self)
                )
                y += max(
                    item.down + self.parameters["VS"], self.parameters["AR"] * 2
                ) + max(
                    self.items[i + 1].up + self.parameters["VS"],
                    self.parameters["AR"] * 2,
                )
                x = x_initial + self.parameters["AR"]
        if len(self.items) > 1:
            Path(x, y, cls="class10", AR=self.parameters["AR"]).h(
                self.parameters["AR"]
            ).add_to(self)
            x += self.parameters["AR"]
        Path(x, y, cls="class11", AR=self.parameters["AR"]).h(right_gap).add_to(self)
        return self


class OptionalSequence(DiagramMultiContainer):
    def __new__(cls, *items: Node, parameters: Opt[AttrsT] = {}) -> Any:
        if len(items) <= 1:
            return Sequence(*items, parameters=parameters)
        else:
            return super(OptionalSequence, cls).__new__(cls)

    def __init__(self, *items: Node, parameters: Opt[AttrsT] = {}):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        self.needs_space = False
        self.width = 0
        self.up = 0
        self.height = sum(item.height for item in self.items)
        self.down = self.items[0].down
        height_so_far: float = 0
        for i, item in enumerate(self.items):
            self.up = max(
                self.up,
                max(self.parameters["AR"] * 2, item.up + self.parameters["VS"])
                - height_so_far,
            )
            height_so_far += item.height
            if i > 0:
                self.down = (
                    max(
                        self.height + self.down,
                        height_so_far
                        + max(
                            self.parameters["AR"] * 2, item.down + self.parameters["VS"]
                        ),
                    )
                    - self.height
                )
            item_width = item.width + (10 if item.needs_space else 0)
            if i == 0:
                self.width += self.parameters["AR"] + max(
                    item_width, self.parameters["AR"]
                )
            else:
                self.width += (
                    self.parameters["AR"] * 2
                    + max(item_width, self.parameters["AR"])
                    + self.parameters["AR"]
                )
        add_debug(self)

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return f"OptionalSequence({items})"

    def to_dict(self) -> dict:
        return {
            "element": "OptionalSequence",
            "items": [i.to_dict() for i in self.items],
        }

    def format(self, x: float, y: float, width: float) -> OptionalSequence:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="class12", AR=self.parameters["AR"]).right(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class13",
            AR=self.parameters["AR"],
        ).right(right_gap).add_to(self)
        x += left_gap
        upper_line_y = y - self.up
        last = len(self.items) - 1
        for i, item in enumerate(self.items):
            item_space = 10 if item.needs_space else 0
            item_width = item.width + item_space
            if i == 0:
                # Upper skip
                (
                    Path(x, y, cls="class14", AR=self.parameters["AR"])
                    .arc("se")
                    .up(y - upper_line_y - self.parameters["AR"] * 2)
                    .arc("wn")
                    .right(item_width - self.parameters["AR"])
                    .arc("ne")
                    .down(y + item.height - upper_line_y - self.parameters["AR"] * 2)
                    .arc("ws")
                    .add_to(self)
                )
                # Straight line
                (
                    Path(x, y, cls="class15", AR=self.parameters["AR"])
                    .right(item_space + self.parameters["AR"])
                    .add_to(self)
                )
                item.format(
                    x + item_space + self.parameters["AR"], y, item.width
                ).add_to(self)
                x += item_width + self.parameters["AR"]
                y += item.height
            elif i < last:
                # Upper skip
                (
                    Path(x, upper_line_y, cls="class16", AR=self.parameters["AR"])
                    .right(
                        self.parameters["AR"] * 2
                        + max(item_width, self.parameters["AR"])
                        + self.parameters["AR"]
                    )
                    .arc("ne")
                    .down(y - upper_line_y + item.height - self.parameters["AR"] * 2)
                    .arc("ws")
                    .add_to(self)
                )
                # Straight line
                (
                    Path(x, y, cls="class17", AR=self.parameters["AR"])
                    .right(self.parameters["AR"] * 2)
                    .add_to(self)
                )
                item.format(x + self.parameters["AR"] * 2, y, item.width).add_to(self)
                (
                    Path(
                        x + item.width + self.parameters["AR"] * 2,
                        y + item.height,
                        cls="class18",
                        AR=self.parameters["AR"],
                    )
                    .right(item_space + self.parameters["AR"])
                    .add_to(self)
                )
                # Lower skip
                (
                    Path(x, y, cls="class19", AR=self.parameters["AR"])
                    .arc("ne")
                    .down(
                        item.height
                        + max(
                            item.down + self.parameters["VS"], self.parameters["AR"] * 2
                        )
                        - self.parameters["AR"] * 2
                    )
                    .arc("ws")
                    .right(item_width - self.parameters["AR"])
                    .arc("se")
                    .up(item.down + self.parameters["VS"] - self.parameters["AR"] * 2)
                    .arc("wn")
                    .add_to(self)
                )
                x += (
                    self.parameters["AR"] * 2
                    + max(item_width, self.parameters["AR"])
                    + self.parameters["AR"]
                )
                y += item.height
            else:
                # Straight line
                (
                    Path(x, y, cls="class20", AR=self.parameters["AR"])
                    .right(self.parameters["AR"] * 2)
                    .add_to(self)
                )
                item.format(x + self.parameters["AR"] * 2, y, item.width).add_to(self)
                (
                    Path(
                        x + self.parameters["AR"] * 2 + item.width,
                        y + item.height,
                        cls="class21",
                        AR=self.parameters["AR"],
                    )
                    .right(item_space + self.parameters["AR"])
                    .add_to(self)
                )
                # Lower skip
                (
                    Path(x, y, cls="class22", AR=self.parameters["AR"])
                    .arc("ne")
                    .down(
                        item.height
                        + max(
                            item.down + self.parameters["VS"], self.parameters["AR"] * 2
                        )
                        - self.parameters["AR"] * 2
                    )
                    .arc("ws")
                    .right(item_width - self.parameters["AR"])
                    .arc("se")
                    .up(item.down + self.parameters["VS"] - self.parameters["AR"] * 2)
                    .arc("wn")
                    .add_to(self)
                )
        return self


class AlternatingSequence(DiagramMultiContainer):
    def __new__(cls, *items: Node, parameters: Opt[AttrsT] = {}) -> AlternatingSequence:
        if len(items) == 2:
            return super(AlternatingSequence, cls).__new__(cls)
        else:
            raise RRException(
                "AlternatingSequence takes exactly two arguments, but got {0} arguments.".format(
                    len(items)
                )
            )

    def __init__(self, *items: Node, parameters: Opt[AttrsT] = {}):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        self.needs_space = False

        arc = self.parameters["AR"]
        vert = self.parameters["VS"]
        first = self.items[0]
        second = self.items[1]

        arc_x = 1 / Math.sqrt(2) * arc * 2
        arc_y = (1 - 1 / Math.sqrt(2)) * arc * 2
        cross_y = max(arc, vert)
        cross_x = (cross_y - arc_y) + arc_x

        first_out = max(
            arc + arc, cross_y / 2 + arc + arc, cross_y / 2 + vert + first.down
        )
        self.up = first_out + first.height + first.up

        second_in = max(
            arc + arc, cross_y / 2 + arc + arc, cross_y / 2 + vert + second.up
        )
        self.down = second_in + second.height + second.down

        self.height = 0

        first_width = (20 if first.needs_space else 0) + first.width
        second_width = (20 if second.needs_space else 0) + second.width
        self.width = 2 * arc + max(first_width, cross_x, second_width) + 2 * arc
        add_debug(self)

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return f"AlternatingSequence({items})"

    def to_dict(self) -> dict:
        return {
            "element": "AlternatingSequence",
            "items": [i.to_dict() for i in self.items],
        }

    def format(self, x: float, y: float, width: float) -> AlternatingSequence:
        arc = self.parameters["AR"]
        gaps = determine_gaps(width, self.width, self.parameters["internal_alignment"])
        Path(x, y, cls="class23", AR=self.parameters["AR"]).right(gaps[0]).add_to(self)
        x += gaps[0]
        Path(x + self.width, y, cls="class24", AR=self.parameters["AR"]).right(
            gaps[1]
        ).add_to(self)
        # bounding box
        # Path(x+gaps[0], y).up(self.up).right(self.width).down(self.up+self.down).left(self.width).up(self.down).addTo(self)
        first = self.items[0]
        second = self.items[1]

        # top
        first_in = self.up - first.up
        first_out = self.up - first.up - first.height
        Path(x, y, cls="class25", AR=self.parameters["AR"]).arc("se").up(
            first_in - 2 * arc
        ).arc("wn").add_to(self)
        first.format(x + 2 * arc, y - first_in, self.width - 4 * arc).add_to(self)
        Path(
            x + self.width - 2 * arc,
            y - first_out,
            cls="class26",
            AR=self.parameters["AR"],
        ).arc("ne").down(first_out - 2 * arc).arc("ws").add_to(self)

        # bottom
        second_in = self.down - second.down - second.height
        second_out = self.down - second.down
        Path(x, y, cls="class27", AR=self.parameters["AR"]).arc("ne").down(
            second_in - 2 * arc
        ).arc("ws").add_to(self)
        second.format(x + 2 * arc, y + second_in, self.width - 4 * arc).add_to(self)
        Path(
            x + self.width - 2 * arc,
            y + second_out,
            cls="class28",
            AR=self.parameters["AR"],
        ).arc("se").up(second_out - 2 * arc).arc("wn").add_to(self)

        # crossover
        arc_x = 1 / Math.sqrt(2) * arc * 2
        arc_y = (1 - 1 / Math.sqrt(2)) * arc * 2
        cross_y = max(arc, self.parameters["VS"])
        cross_x = (cross_y - arc_y) + arc_x
        cross_bar = (self.width - 4 * arc - cross_x) / 2
        (
            Path(
                x + arc, y - cross_y / 2 - arc, cls="class29", AR=self.parameters["AR"]
            )
            .arc("ws")
            .right(cross_bar)
            .arc_8("n", "cw")
            .l(cross_x - arc_x, cross_y - arc_y)
            .arc_8("sw", "ccw")
            .right(cross_bar)
            .arc("ne")
            .add_to(self)
        )
        (
            Path(
                x + arc, y + cross_y / 2 + arc, cls="class30", AR=self.parameters["AR"]
            )
            .arc("wn")
            .right(cross_bar)
            .arc_8("s", "ccw")
            .l(cross_x - arc_x, -(cross_y - arc_y))
            .arc_8("nw", "cw")
            .right(cross_bar)
            .arc("se")
            .add_to(self)
        )

        return self


class Choice(DiagramMultiContainer):
    def __init__(self, default: int, *items: Node, parameters: Opt[AttrsT] = {}):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        assert default < len(items)
        self.default = default
        self.width = self.parameters["AR"] * 4 + max(item.width for item in self.items)
        self.up = self.items[0].up
        self.down = self.items[-1].down
        self.height = self.items[default].height
        for i, item in enumerate(self.items):
            if i in [default - 1, default + 1]:
                arcs = self.parameters["AR"] * 2
            else:
                arcs = self.parameters["AR"]
            if i < default:
                self.up += max(
                    arcs,
                    item.height
                    + item.down
                    + self.parameters["VS"]
                    + self.items[i + 1].up,
                )
            elif i == default:
                continue
            else:
                self.down += max(
                    arcs,
                    item.up
                    + self.parameters["VS"]
                    + self.items[i - 1].down
                    + self.items[i - 1].height,
                )
        self.down -= self.items[default].height  # already counted in self.height
        add_debug(self)

    def to_dict(self) -> dict:
        return {
            "element": "Choice",
            "default": self.default,
            "items": [i.to_dict() for i in self.items],
        }

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return "Choice(%r, %s)" % (self.default, items)

    def format(self, x: float, y: float, width: float) -> Choice:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="class31", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class32",
            AR=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        inner_width = self.width - self.parameters["AR"] * 4
        default = self.items[self.default]

        # Do the elements that curve above
        above = self.items[: self.default][::-1]
        if above:
            distance_from_y = max(
                self.parameters["AR"] * 2,
                default.up + self.parameters["VS"] + above[0].down + above[0].height,
            )
        for i, ni, item in double_enumerate(above):
            Path(x, y, cls="class33", AR=self.parameters["AR"]).arc("se").up(
                distance_from_y - self.parameters["AR"] * 2
            ).arc("wn").add_to(self)
            item.format(
                x + self.parameters["AR"] * 2, y - distance_from_y, inner_width
            ).add_to(self)
            Path(
                x + self.parameters["AR"] * 2 + inner_width,
                y - distance_from_y + item.height,
                cls="class34",
                AR=self.parameters["AR"],
            ).arc("ne").down(
                distance_from_y
                - item.height
                + default.height
                - self.parameters["AR"] * 2
            ).arc(
                "ws"
            ).add_to(
                self
            )
            if ni < -1:
                distance_from_y += max(
                    self.parameters["AR"],
                    item.up
                    + self.parameters["VS"]
                    + above[i + 1].down
                    + above[i + 1].height,
                )

        # Do the straight-line path.
        Path(x, y, cls="class35", AR=self.parameters["AR"]).right(
            self.parameters["AR"] * 2
        ).add_to(self)
        self.items[self.default].format(
            x + self.parameters["AR"] * 2, y, inner_width
        ).add_to(self)
        Path(
            x + self.parameters["AR"] * 2 + inner_width,
            y + self.height,
            cls="class36",
            AR=self.parameters["AR"],
        ).right(self.parameters["AR"] * 2).add_to(self)

        # Do the elements that curve below
        below = self.items[self.default + 1 :]
        if below:
            distance_from_y = max(
                self.parameters["AR"] * 2,
                default.height + default.down + self.parameters["VS"] + below[0].up,
            )
        for i, item in enumerate(below):
            Path(x, y, cls="class37", AR=self.parameters["AR"]).arc("ne").down(
                distance_from_y - self.parameters["AR"] * 2
            ).arc("ws").add_to(self)
            item.format(
                x + self.parameters["AR"] * 2, y + distance_from_y, inner_width
            ).add_to(self)
            Path(
                x + self.parameters["AR"] * 2 + inner_width,
                y + distance_from_y + item.height,
                cls="class38",
                AR=self.parameters["AR"],
            ).arc("se").up(
                distance_from_y
                - self.parameters["AR"] * 2
                + item.height
                - default.height
            ).arc(
                "wn"
            ).add_to(
                self
            )
            distance_from_y += max(
                self.parameters["AR"],
                item.height
                + item.down
                + self.parameters["VS"]
                + (below[i + 1].up if i + 1 < len(below) else 0),
            )
        return self


class MultipleChoice(DiagramMultiContainer):
    def __init__(
        self, default: int, type: str, *items: Node, parameters: Opt[AttrsT] = {}
    ):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        assert 0 <= default < len(items)
        assert type in ["any", "all"]
        self.default = default
        self.type = type
        self.needs_space = True
        self.inner_width = max(item.width for item in self.items)
        self.width = (
            30 + self.parameters["AR"] + self.inner_width + self.parameters["AR"] + 20
        )
        self.up = self.items[0].up
        self.down = self.items[-1].down
        self.height = self.items[default].height
        for i, item in enumerate(self.items):
            if i in [default - 1, default + 1]:
                minimum = 10 + self.parameters["AR"]
            else:
                minimum = self.parameters["AR"]
            if i < default:
                self.up += max(
                    minimum,
                    item.height
                    + item.down
                    + self.parameters["VS"]
                    + self.items[i + 1].up,
                )
            elif i == default:
                continue
            else:
                self.down += max(
                    minimum,
                    item.up
                    + self.parameters["VS"]
                    + self.items[i - 1].down
                    + self.items[i - 1].height,
                )
        self.down -= self.items[default].height  # already counted in self.height
        add_debug(self)

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return f"MultipleChoice({repr(self.default)}, {repr(self.type)}, {items})"

    def to_dict(self) -> dict:
        return {
            "element": "MultipleChoice",
            "default": self.default,
            "type": self.type,
            "items": [i.to_dict() for i in self.items],
        }

    def format(self, x: float, y: float, width: float) -> MultipleChoice:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="class39", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class40",
            AR=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        default = self.items[self.default]

        # Do the elements that curve above
        above = self.items[: self.default][::-1]
        if above:
            distance_from_y = max(
                10 + self.parameters["AR"],
                default.up + self.parameters["VS"] + above[0].down + above[0].height,
            )
        for i, ni, item in double_enumerate(above):
            (
                Path(x + 30, y, cls="class41", AR=self.parameters["AR"])
                .up(distance_from_y - self.parameters["AR"])
                .arc("wn")
                .add_to(self)
            )
            item.format(
                x + 30 + self.parameters["AR"], y - distance_from_y, self.inner_width
            ).add_to(self)
            (
                Path(
                    x + 30 + self.parameters["AR"] + self.inner_width,
                    y - distance_from_y + item.height,
                    cls="class42",
                )
                .arc("ne")
                .down(
                    distance_from_y
                    - item.height
                    + default.height
                    - self.parameters["AR"]
                    - 10
                )
                .add_to(self)
            )
            if ni < -1:
                distance_from_y += max(
                    self.parameters["AR"],
                    item.up
                    + self.parameters["VS"]
                    + above[i + 1].down
                    + above[i + 1].height,
                )

        # Do the straight-line path.
        Path(x + 30, y, cls="class43", AR=self.parameters["AR"]).right(
            self.parameters["AR"]
        ).add_to(self)
        self.items[self.default].format(
            x + 30 + self.parameters["AR"], y, self.inner_width
        ).add_to(self)
        Path(
            x + 30 + self.parameters["AR"] + self.inner_width,
            y + self.height,
            cls="class44",
            AR=self.parameters["AR"],
        ).right(self.parameters["AR"]).add_to(self)

        # Do the elements that curve below
        below = self.items[self.default + 1 :]
        if below:
            distance_from_y = max(
                10 + self.parameters["AR"],
                default.height + default.down + self.parameters["VS"] + below[0].up,
            )
        for i, item in enumerate(below):
            (
                Path(x + 30, y, cls="class45", AR=self.parameters["AR"])
                .down(distance_from_y - self.parameters["AR"])
                .arc("ws")
                .add_to(self)
            )
            item.format(
                x + 30 + self.parameters["AR"], y + distance_from_y, self.inner_width
            ).add_to(self)
            (
                Path(
                    x + 30 + self.parameters["AR"] + self.inner_width,
                    y + distance_from_y + item.height,
                    cls="class46",
                    AR=self.parameters["AR"],
                )
                .arc("se")
                .up(
                    distance_from_y
                    - self.parameters["AR"]
                    + item.height
                    - default.height
                    - 10
                )
                .add_to(self)
            )
            distance_from_y += max(
                self.parameters["AR"],
                item.height
                + item.down
                + self.parameters["VS"]
                + (below[i + 1].up if i + 1 < len(below) else 0),
            )
        text = DiagramItem("g", attrs={"class": "diagram-text"}).add_to(self)
        DiagramItem(
            "title",
            text="take one or more branches, once each, in any order"
            if self.type == "any"
            else "take all branches, once each, in any order",
        ).add_to(text)
        DiagramItem(
            "path",
            attrs={
                "d": "M {x} {y} h -26 a 4 4 0 0 0 -4 4 v 12 a 4 4 0 0 0 4 4 h 26 z".format(
                    x=x + 30, y=y - 10
                ),
                "class": "diagram-text",
            },
        ).add_to(text)
        DiagramItem(
            "text",
            text="1+" if self.type == "any" else "all",
            attrs={"x": x + 15, "y": y + 4, "class": "diagram-text"},
        ).add_to(text)
        DiagramItem(
            "path",
            attrs={
                "d": "M {x} {y} h 16 a 4 4 0 0 1 4 4 v 12 a 4 4 0 0 1 -4 4 h -16 z".format(
                    x=x + self.width - 20, y=y - 10
                ),
                "class": "diagram-text",
            },
        ).add_to(text)
        DiagramItem(
            "text",
            text="↺",
            attrs={"x": x + self.width - 10, "y": y + 4, "class": "diagram-arrow"},
        ).add_to(text)
        return self


class HorizontalChoice(DiagramMultiContainer):
    def __new__(cls, *items: Node, parameters: Opt[AttrsT] = {}) -> Any:
        if len(items) <= 1:
            return Sequence(*items, parameters=parameters)
        else:
            return super(HorizontalChoice, cls).__new__(cls)

    def __init__(self, *items: Node, parameters: Opt[AttrsT] = {}):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        all_but_last = self.items[:-1]
        middles = self.items[1:-1]
        first = self.items[0]
        last = self.items[-1]
        self.needs_space = False

        self.width = (
            self.parameters["AR"]  # starting track
            + self.parameters["AR"] * 2 * (len(self.items) - 1)  # in-between tracks
            + sum(x.width + (20 if x.needs_space else 0) for x in self.items)  # items
            + (
                self.parameters["AR"] if last.height > 0 else 0
            )  # needs space to curve up
            + self.parameters["AR"]
        )  # ending track

        # Always exits at entrance height
        self.height = 0

        # All but the last have a track running above them
        self._upperTrack = max(
            self.parameters["AR"] * 2,
            self.parameters["VS"],
            max(x.up for x in all_but_last) + self.parameters["VS"],
        )
        self.up = max(self._upperTrack, last.up)

        # All but the first have a track running below them
        # Last either straight-lines or curves up, so has different calculation
        self._lowerTrack = max(
            self.parameters["VS"],
            max(
                x.height
                + max(x.down + self.parameters["VS"], self.parameters["AR"] * 2)
                for x in middles
            )
            if middles
            else 0,
            last.height + last.down + self.parameters["VS"],
        )
        if first.height < self._lowerTrack:
            # Make sure there's at least 2*self.parameters["AR"] room between first exit and lower track
            self._lowerTrack = max(
                self._lowerTrack, first.height + self.parameters["AR"] * 2
            )
        self.down = max(self._lowerTrack, first.height + first.down)

        add_debug(self)

    def to_dict(self) -> dict:
        return {
            "element": "HorizontalChoice",
            "items": [i.to_dict() for i in self.items],
        }

    def format(self, x: float, y: float, width: float) -> HorizontalChoice:
        # Hook up the two sides if self is narrower than its stated width.
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="class47", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class48",
            AR=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        first = self.items[0]
        last = self.items[-1]

        # upper track
        upper_span = (
            sum(x.width + (20 if x.needs_space else 0) for x in self.items[:-1])
            + (len(self.items) - 2) * self.parameters["AR"] * 2
            - self.parameters["AR"]
        )
        (
            Path(x, y, cls="class49", AR=self.parameters["AR"])
            .arc("se")
            .up(self._upperTrack - self.parameters["AR"] * 2)
            .arc("wn")
            .h(upper_span)
            .add_to(self)
        )

        # lower track
        lower_span = (
            sum(x.width + (20 if x.needs_space else 0) for x in self.items[1:])
            + (len(self.items) - 2) * self.parameters["AR"] * 2
            + (self.parameters["AR"] if last.height > 0 else 0)
            - self.parameters["AR"]
        )
        lower_start = (
            x
            + self.parameters["AR"]
            + first.width
            + (20 if first.needs_space else 0)
            + self.parameters["AR"] * 2
        )
        (
            Path(
                lower_start,
                y + self._lowerTrack,
                cls="class50",
                AR=self.parameters["AR"],
            )
            .h(lower_span)
            .arc("se")
            .up(self._lowerTrack - self.parameters["AR"] * 2)
            .arc("wn")
            .add_to(self)
        )

        # Items
        for [i, item] in enumerate(self.items):
            # input track
            if i == 0:
                (
                    Path(x, y, cls="class51", AR=self.parameters["AR"])
                    .h(self.parameters["AR"])
                    .add_to(self)
                )
                x += self.parameters["AR"]
            else:
                (
                    Path(
                        x, y - self._upperTrack, cls="class52", AR=self.parameters["AR"]
                    )
                    .arc("ne")
                    .v(self._upperTrack - self.parameters["AR"] * 2)
                    .arc("ws")
                    .add_to(self)
                )
                x += self.parameters["AR"] * 2

            # item
            item_width = item.width + (20 if item.needs_space else 0)
            item.format(x, y, item_width).add_to(self)
            x += item_width

            # output track
            if i == len(self.items) - 1:
                if item.height == 0:
                    (
                        Path(x, y, cls="class53", AR=self.parameters["AR"])
                        .h(self.parameters["AR"])
                        .add_to(self)
                    )
                else:
                    (
                        Path(
                            x, y + item.height, cls="class54", AR=self.parameters["AR"]
                        )
                        .arc("se")
                        .add_to(self)
                    )
            elif i == 0 and item.height > self._lowerTrack:
                # Needs to arc up to meet the lower track, not down.
                if item.height - self._lowerTrack >= self.parameters["AR"] * 2:
                    (
                        Path(
                            x, y + item.height, cls="class55", AR=self.parameters["AR"]
                        )
                        .arc("se")
                        .v(self._lowerTrack - item.height + self.parameters["AR"] * 2)
                        .arc("wn")
                        .add_to(self)
                    )
                else:
                    # Not enough space to fit two arcs
                    # so just bail and draw a straight line for now.
                    (
                        Path(
                            x, y + item.height, cls="class56", AR=self.parameters["AR"]
                        )
                        .l(self.parameters["AR"] * 2, self._lowerTrack - item.height)
                        .add_to(self)
                    )
            else:
                (
                    Path(x, y + item.height, cls="class57", AR=self.parameters["AR"])
                    .arc("ne")
                    .v(self._lowerTrack - item.height - self.parameters["AR"] * 2)
                    .arc("ws")
                    .add_to(self)
                )
        return self


def optional(item: Node, skip: bool = False, parameters: Opt[AttrsT] = {}) -> Choice:
    return Choice(
        0 if skip else 1, Skip(parameters=parameters), item, parameters=parameters
    )


class OneOrMore(DiagramItem):
    def __init__(
        self, item: Node, repeat: Opt[Node] = None, parameters: Opt[AttrsT] = {}
    ):
        DiagramItem.__init__(self, "g", parameters=parameters)
        self.item = wrap_string(item)
        repeat = repeat or Skip()
        self.rep = wrap_string(repeat)
        self.width = max(self.item.width, self.rep.width) + self.parameters["AR"] * 2
        self.height = self.item.height
        self.up = self.item.up
        self.down = max(
            self.parameters["AR"] * 2,
            self.item.down
            + self.parameters["VS"]
            + self.rep.up
            + self.rep.height
            + self.rep.down,
        )
        self.needs_space = True
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> OneOrMore:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="class58", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class59",
            AR=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        # Draw item
        Path(x, y, cls="class60", AR=self.parameters["AR"]).right(
            self.parameters["AR"]
        ).add_to(self)
        self.item.format(
            x + self.parameters["AR"], y, self.width - self.parameters["AR"] * 2
        ).add_to(self)
        Path(
            x + self.width - self.parameters["AR"],
            y + self.height,
            cls="class61",
            AR=self.parameters["AR"],
        ).right(self.parameters["AR"]).add_to(self)

        # Draw repeat arc
        distance_from_y = max(
            self.parameters["AR"] * 2,
            self.item.height + self.item.down + self.parameters["VS"] + self.rep.up,
        )
        Path(x + self.parameters["AR"], y, cls="class62", AR=self.parameters["AR"]).arc(
            "nw"
        ).down(distance_from_y - self.parameters["AR"] * 2).arc("ws").add_to(self)
        self.rep.format(
            x + self.parameters["AR"],
            y + distance_from_y,
            self.width - self.parameters["AR"] * 2,
        ).add_to(self)
        Path(
            x + self.width - self.parameters["AR"],
            y + distance_from_y + self.rep.height,
            cls="class63",
            AR=self.parameters["AR"],
        ).arc("se").up(
            distance_from_y
            - self.parameters["AR"] * 2
            + self.rep.height
            - self.item.height
        ).arc(
            "en"
        ).add_to(
            self
        )

        return self

    def walk(self, cb: WalkerF) -> None:
        cb(self)
        self.item.walk(cb)
        self.rep.walk(cb)

    def __repr__(self) -> str:
        return f"OneOrMore({repr(self.item)}, repeat={repr(self.rep)})"

    def to_dict(self) -> dict:
        return {
            "element": "OneOrMore",
            "item": self.item.to_dict(),
            "repeat": self.rep.to_dict(),
        }


def zero_or_more(
    item: Node,
    repeat: Opt[Node] = None,
    skip: bool = False,
    parameters: Opt[AttrsT] = {},
) -> Choice:
    result = optional(
        OneOrMore(item, repeat, parameters=parameters), skip, parameters=parameters
    )
    return result


class Group(DiagramItem):
    def __init__(
        self, item: Node, label: Opt[Node] = None, parameters: Opt[AttrsT] = {}
    ):
        DiagramItem.__init__(self, "g", parameters=parameters)
        self.item = wrap_string(item)
        self.label: Opt[DiagramItem]
        if isinstance(label, DiagramItem):
            self.label = label
        elif label:
            self.label = Comment(label)
        else:
            self.label = None

        self.width = max(
            self.item.width + (20 if self.item.needs_space else 0),
            self.label.width if self.label else 0,
            self.parameters["AR"] * 2,
        )
        self.height = self.item.height
        self.boxUp = max(self.item.up + self.parameters["VS"], self.parameters["AR"])
        self.up = self.boxUp
        if self.label:
            self.up += self.label.up + self.label.height + self.label.down
        self.down = max(self.item.down + self.parameters["VS"], self.parameters["AR"])
        self.needs_space = True
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> Group:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="class64", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="class65",
            AR=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        DiagramItem(
            "rect",
            {
                "x": x,
                "y": y - self.boxUp,
                "width": self.width,
                "height": self.boxUp + self.height + self.down,
                "rx": self.parameters["AR"],
                "ry": self.parameters["AR"],
                "class": "group-box",
            },
        ).add_to(self)

        self.item.format(x, y, self.width).add_to(self)
        if self.label:
            self.label.format(
                x,
                y - (self.boxUp + self.label.down + self.label.height),
                self.label.width,
            ).add_to(self)

        return self

    def walk(self, cb: WalkerF) -> None:
        cb(self)
        self.item.walk(cb)
        if self.label:
            self.label.walk(cb)

    def to_dict(self) -> dict:
        if self.label is None:
            return {"element": "Group", "item": self.item.to_dict(), "label": None}
        return {
            "element": "Group",
            "item": self.item.to_dict(),
            "label": self.label.to_dict(),
        }


class Start(DiagramItem):
    def __init__(
        self, type: str = "simple", label: Opt[str] = None, parameters: Opt[AttrsT] = {}
    ):
        DiagramItem.__init__(self, "g", parameters=parameters)
        if label:
            self.width = max(20, len(label) * self.parameters["char_width"] + 10)
        else:
            self.width = 20
        self.up = 10
        self.down = 10
        self.type = type
        self.label = label
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> Start:
        path = Path(x, y - 10)
        if self.type == "complex":
            path.attrs["cls"] = "class66c"
            path.down(20).m(0, -10).right(self.width).add_to(self)
        else:
            path.attrs["cls"] = "class66s"
            path.down(20).m(10, -20).down(20).m(-10, -10).right(self.width).add_to(self)
        if self.label:
            DiagramItem(
                "text",
                attrs={"x": x, "y": y - 15, "style": "text-anchor:start"},
                text=self.label,
            ).add_to(self)
        return self

    def __repr__(self) -> str:
        return f"Start(type={repr(self.type)}, label={repr(self.label)})"

    def to_dict(self) -> dict:
        return {"element": "Start", "type": self.type, "label": self.label}


class End(DiagramItem):
    def __init__(self, type: str = "simple", parameters: Opt[AttrsT] = {}):
        DiagramItem.__init__(self, "path", parameters=parameters)
        self.width = 20
        self.up = 10
        self.down = 10
        self.type = type
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> End:
        if self.type == "simple":
            self.attrs["cls"] = "class74s"
            self.attrs["d"] = "M {0} {1} h 20 m -10 -10 v 20 m 10 -20 v 20".format(x, y)
        elif self.type == "complex":
            self.attrs["cls"] = "class74c"
            self.attrs["d"] = "M {0} {1} h 20 m 0 -10 v 20".format(x, y)
        return self

    def __repr__(self) -> str:
        return f"End(type={repr(self.type)})"

    def to_dict(self) -> dict:
        return {"element": "End", "type": self.type}


class Terminal(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: Opt[AttrsT] = {},
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["terminal", cls])}, parameters=parameters
        )
        self.text = text
        self.href = href
        self.title = title
        self.cls = cls
        self.width = len(text) * self.parameters["char_width"] + 20
        self.up = 11
        self.down = 11
        self.needs_space = True
        add_debug(self)

    def to_dict(self) -> dict:
        return {
            "element": "Terminal",
            "text": self.text,
            "href": self.href,
            "title": self.title,
            "cls": self.cls,
        }

    def __repr__(self) -> str:
        return f"Terminal({repr(self.text)}, href={repr(self.href)}, title={repr(self.title)}, cls={repr(self.cls)})"

    def format(self, x: float, y: float, width: float) -> Terminal:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="class67", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(x + left_gap + self.width, y, cls="class68", AR=self.parameters["AR"]).h(
            right_gap
        ).add_to(self)

        DiagramItem(
            "rect",
            {
                "x": x + left_gap,
                "y": y - 11,
                "width": self.width,
                "height": self.up + self.down,
                "rx": 10,
                "ry": 10,
            },
        ).add_to(self)
        text = DiagramItem(
            "text", {"x": x + left_gap + self.width / 2, "y": y + 4}, self.text
        )
        if self.href is not None:
            a = DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
            text.add_to(a)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self


class NonTerminal(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: Opt[AttrsT] = {},
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["non-terminal", cls])}, parameters=parameters
        )
        self.text = text
        self.href = href
        self.title = title
        self.cls = cls
        self.width = len(text) * self.parameters["char_width"] + 20
        self.up = 11
        self.down = 11
        self.needs_space = True
        add_debug(self)

    def to_dict(self) -> dict:
        return {
            "element": "NonTerminal",
            "text": self.text,
            "href": self.href,
            "title": self.title,
            "cls": self.cls,
        }

    def __repr__(self) -> str:
        return f"NonTerminal({repr(self.text)}, href={repr(self.href)}, title={repr(self.title)}, cls={repr(self.cls)})"

    def format(self, x: float, y: float, width: float) -> NonTerminal:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="class69", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(x + left_gap + self.width, y, cls="class70", AR=self.parameters["AR"]).h(
            right_gap
        ).add_to(self)

        DiagramItem(
            "rect",
            {
                "x": x + left_gap,
                "y": y - 11,
                "width": self.width,
                "height": self.up + self.down,
            },
        ).add_to(self)
        text = DiagramItem(
            "text", {"x": x + left_gap + self.width / 2, "y": y + 4}, self.text
        )
        if self.href is not None:
            a = DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
            text.add_to(a)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self


class Comment(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: Opt[AttrsT] = {},
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["non-terminal", cls])}, parameters=parameters
        )
        self.text = text
        self.href = href
        self.title = title
        self.cls = cls
        self.width = len(text) * self.parameters["comment_char_width"] + 10
        self.up = 8
        self.down = 8
        self.needs_space = True
        add_debug(self)

    def to_dict(self) -> dict:
        return {
            "element": "Comment",
            "text": self.text,
            "href": self.href,
            "title": self.title,
            "cls": self.cls,
        }

    def __repr__(self) -> str:
        return f"Comment({repr(self.text)}, href={repr(self.href)}, title={repr(self.title)}, cls={repr(self.cls)})"

    def format(self, x: float, y: float, width: float) -> Comment:
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="class71", AR=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(x + left_gap + self.width, y, cls="class72", AR=self.parameters["AR"]).h(
            right_gap
        ).add_to(self)

        text = DiagramItem(
            "text",
            {"x": x + left_gap + self.width / 2, "y": y + 5, "class": "comment"},
            self.text,
        )
        if self.href is not None:
            a = DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
            text.add_to(a)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self


class Skip(DiagramItem):
    def __init__(self, parameters: Opt[AttrsT] = {}) -> None:
        DiagramItem.__init__(self, "g", parameters=parameters)
        self.width = 0
        self.up = 0
        self.down = 0
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> Skip:
        Path(x, y, cls="class73", AR=self.parameters["AR"]).right(width).add_to(self)
        return self

    def __repr__(self) -> str:
        return "Skip()"

    def to_dict(self) -> dict:
        return {"element": "Skip"}
