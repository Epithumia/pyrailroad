# -*- coding: utf-8 -*-
from __future__ import annotations

import math as Math

from typing import TYPE_CHECKING

from .exceptions import ParseException

# TODO: add TextDiagram and methods from https://github.com/tabatkins/railroad-diagrams/blob/gh-pages/railroad.py + _repr_ partout où nécessaire

if TYPE_CHECKING:
    from typing import (  # pragma: no cover
        Any,
        Callable,
        Dict,
        List,
        Tuple,
        Optional as Opt,
        Sequence as Seq,
        TypeVar,
        Union,
    )

    T = TypeVar("T")  # pragma: no cover
    Node = Union[str, "DiagramItem"]  # pragma: no cover
    WriterF = Callable[[str], Any]  # pragma: no cover
    WalkerF = Callable[["DiagramItem"], Any]  # pragma: no cover
    AttrsT = Dict[str, Any]  # pragma: no cover


class DiagramItem:
    def __init__(
        self,
        name: str,
        attrs: Opt[AttrsT] = None,
        text: Opt[Node] = None,
        parameters: AttrsT = dict(),
    ):
        """
        Create a new DiagramItem.

        DiagramItems are the building blocks of a Diagram. They are both logical diagram elements and SVG elements.

        Parameters:
            name: The name of the DiagramItem, used for debugging.
            attrs: The SVG attributes for the DiagramItem.
            text: The text of the DiagramItem, if it is a text element.
            parameters: The diagram parameters.

        Some of the diagram parameters will be initialized to default values if not provided, they are:

          * *debug*: enable debug information
          * *stroke_odd_pixel_length*: whether the stroke width is an odd (1px, 3px, etc) pixel length
          * *diagram_class*: the class to put on the root `<svg>` element
          * *VS*: the minimum vertical separation between things
          * *AR*: the minimum horizontal separation between things
          * *char_width*: the width of each monospace character
          * *comment_char_width*: the width of each comment character
          * *internal_alignment*: how to align items when they have extra space (left/right/center)
          * *escape_html*: should Diagram.write_text() produce HTML-escaped text, or raw?

        The default values for these parameters can be found in defaults.py
        """
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
        from .defaults import (
            DIAGRAM_CLASS,
            DEBUG,
            STROKE_ODD_PIXEL_LENGTH,
            VS,
            AR,
            CHAR_WIDTH,
            COMMENT_CHAR_WIDTH,
            INTERNAL_ALIGNMENT,
            ESCAPE_HTML,
            FORMATTING,
        )

        self.parameters = {
            "debug": DEBUG,
            "stroke_odd_pixel_length": STROKE_ODD_PIXEL_LENGTH,
            "diagram_class": DIAGRAM_CLASS,
            "VS": VS,
            "AR": AR,
            "char_width": CHAR_WIDTH,
            "comment_char_width": COMMENT_CHAR_WIDTH,
            "internal_alignment": INTERNAL_ALIGNMENT,
            "escape_html": ESCAPE_HTML,
            "formatting": FORMATTING,
        }
        for k in parameters.keys():
            self.parameters[k] = parameters[k]

        # DiagramItems pull double duty as SVG elements.
        self.attrs: AttrsT = attrs or {}
        # Subclasses store their meaningful children as .item or .items;
        # .children instead stores their formatted SVG nodes.
        self.children: List[Node | Path | Style] = [text] if text else []

        # Set TextDiagram formatting
        if self.parameters["formatting"] == "ascii":
            TextDiagram.set_formatting(TextDiagram.PARTS_ASCII)
        else:
            TextDiagram.set_formatting(TextDiagram.PARTS_UNICODE)

    def format(self, x: float, y: float, width: float) -> DiagramItem:
        raise NotImplementedError  # pragma: no cover

    def add_to(self, parent: DiagramItem) -> DiagramItem:
        parent.children.append(self)
        return self

    def write_svg(self, write: WriterF) -> None:
        from .utils import escape_attr, escape_html

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
        raise NotImplementedError("Virtual")  # pragma: no cover

    def text_diagram(self) -> TextDiagram:
        raise NotImplementedError("Virtual")

    def __repr__(self) -> str:
        return f"DiagramItem({self.name}, {self.attrs}, {self.children})"

    @classmethod
    def from_dict(cls, data: dict, parameters: dict = dict()) -> DiagramItem | None:
        if "element" not in data.keys():
            return None
        match data["element"]:
            case "Diagram":
                return Diagram(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),  # type: ignore
                    type=parameters.get("type", "simple"),
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
            case "Arrow":
                if "direction" not in data.keys() or data["direction"] is None:
                    direction = "right"
                else:
                    direction = data["direction"]
                return Arrow(direction, parameters=parameters)
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
                    ),  # type: ignore
                    parameters=parameters,
                )
            case "Choice":
                try:
                    int(data["default"])
                except TypeError:
                    raise ParseException(
                        f"Attribute \"default\" must be an integer, got: {data['default']}."
                    )
                except KeyError:
                    data["default"] = 0
                return Choice(
                    int(data["default"]),
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),  # type: ignore
                    parameters=parameters,
                )
            case "HorizontalChoice":
                return HorizontalChoice(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),  # type: ignore
                    parameters=parameters,
                )
            case "OptionalSequence":
                return OptionalSequence(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),  # type: ignore
                    parameters=parameters,
                )
            case "AlternatingSequence":
                return AlternatingSequence(
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),  # type: ignore
                    parameters=parameters,
                )
            case "MultipleChoice":
                return MultipleChoice(
                    int(data["default"]),
                    data["type"],
                    *(
                        DiagramItem.from_dict(item, parameters)
                        for item in data["items"]
                    ),  # type: ignore
                    parameters=parameters,
                )
            case "Skip":
                return Skip(parameters=parameters)
            case "OneOrMore":
                if "repeat" not in data.keys() or data["repeat"] is None:
                    return OneOrMore(
                        DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                        parameters=parameters,
                    )
                return OneOrMore(
                    DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                    DiagramItem.from_dict(data["repeat"], parameters),
                    parameters=parameters,
                )
            case "ZeroOrMore":
                if "repeat" not in data.keys() or data["repeat"] is None:
                    return zero_or_more(
                        DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                        skip=data.get("skip", False),
                        parameters=parameters,
                    )
                return zero_or_more(
                    DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                    DiagramItem.from_dict(data["repeat"], parameters),
                    skip=data.get("skip", False),
                    parameters=parameters,
                )
            case "Optional":
                return optional(
                    DiagramItem.from_dict(data["item"], parameters),  # type: ignore
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
                        for item in data["items"]  # type: ignore
                    ),
                    parameters=parameters,
                )
            case "Group":
                if "label" not in data.keys() or data["label"] is None:
                    return Group(
                        item=DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                        parameters=parameters,
                    )
                if isinstance(data["label"], str):
                    return Group(
                        item=DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                        label=data["label"],
                        parameters=parameters,
                    )
                return Group(
                    item=DiagramItem.from_dict(data["item"], parameters),  # type: ignore
                    label=DiagramItem.from_dict(data["label"], parameters),
                    parameters=parameters,
                )
            case "Expression":
                return Expression(
                    text=data["text"],
                    href=data.get("href", None),
                    title=data.get("title", None),
                    cls=data.get("cls", ""),
                    parameters=parameters,
                )
            case _:
                raise ParseException(f"Unknown element: {data['element']}.")


# def apply_properties(properties: dict):
#    """Need to make the global parameters not global"""
#    pass


class DiagramMultiContainer(DiagramItem):
    def __init__(
        self,
        name: str,
        items: Seq[Node],
        attrs: Opt[Dict[str, str]] = None,
        text: Opt[str] = None,
        parameters: AttrsT = dict(),
    ):
        DiagramItem.__init__(self, name, attrs, text, parameters=parameters)
        from .utils import wrap_string

        self.items: List[DiagramItem] = [wrap_string(item) for item in items]

    def format(self, x: float, y: float, width: float) -> DiagramItem:
        raise NotImplementedError  # Virtual

    def __repr__(self) -> str:
        return f"DiagramMultiContainer({self.name}, {self.items}. {self.attrs}, {self.children})"

    def walk(self, cb: WalkerF) -> None:
        cb(self)
        for item in self.items:
            item.walk(cb)


class Path:
    def __init__(self, x: float, y: float, cls: Opt[str] = None, ar: Opt[float] = None):
        from .defaults import AR

        self.x = x
        self.y = y
        self.AR = ar or AR
        self.attrs = {"d": f"M{x} {y}"}
        if cls is not None:
            self.attrs = {"class": cls, "d": f"M{x} {y}"}

    def m(self, x: float, y: float) -> Path:
        self.attrs["d"] += f"m{x} {y}"
        return self

    def big_m(self, x: float, y: float) -> Path:
        self.attrs["d"] += f"M{x} {y}"
        return self

    def a(self, r: float) -> Path:
        self.attrs[
            "d"
        ] += f"a {r},{r} 0 0 1 -{r},{r} {r},{r} 0 0 1 -{r},-{r} {r},{r} 0 0 1 {r},-{r} {r},{r} 0 0 1 {r},{r} z"
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
        from .utils import escape_attr

        write("<path")
        for name, value in sorted(self.attrs.items()):
            write(f' {name}="{escape_attr(value)}"')
        write(" />")

    def format(self) -> Path:
        self.attrs["d"] += "h.5"
        return self

    def text_diagram(self) -> TextDiagram:
        return TextDiagram(0, 0, [])

    def __repr__(self) -> str:
        return f"Path({repr(self.x)}, {repr(self.y)})"


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

    def text_diagram(self) -> TextDiagram:
        return TextDiagram(0, 0, [])

    def write_svg(self, write: WriterF) -> None:
        # Write included stylesheet as CDATA. See https:#developer.mozilla.org/en-US/docs/Web/SVG/Element/style
        cdata = "/* <![CDATA[ */\n{css}\n/* ]]> */\n".format(css=self.css)
        write("<style>{cdata}</style>".format(cdata=cdata))


class Diagram(DiagramMultiContainer):
    def __init__(self, *items: Node, parameters: AttrsT = dict(), **kwargs: str):
        # Accepts a type=[simple|complex] kwarg

        from .defaults import DIAGRAM_CLASS

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
                Path(x, y, ar=self.parameters["AR"]).h(10).add_to(g)
                x += 10
            item.format(x, y, item.width).add_to(g)
            x += item.width
            y += item.height
            if item.needs_space:
                Path(x, y, ar=self.parameters["AR"]).h(10).add_to(g)
                x += 10
        self.attrs["width"] = str(self.width + padding_left + padding_right)
        self.attrs["height"] = str(
            self.up + self.height + self.down + padding_top + padding_bottom
        )
        self.attrs["viewBox"] = f"0 0 {self.attrs['width']} {self.attrs['height']}"
        g.add_to(self)
        self.formatted = True
        return self

    def text_diagram(self) -> TextDiagram:
        (separator,) = TextDiagram._get_parts(["separator"])
        diagram_td = self.items[0].text_diagram()
        for item in self.items[1:]:
            itemTD = item.text_diagram()
            if item.needs_space:
                itemTD = itemTD.expand(1, 1, 0, 0)
            diagram_td = diagram_td.append_right(itemTD, separator)
        return diagram_td

    def write_svg(self, write: WriterF) -> None:
        if not self.formatted:
            self.format()
        return DiagramItem.write_svg(self, write)

    def write_text(self, write: WriterF) -> None:
        from .defaults import ESCAPE_HTML

        escape_html = self.parameters.get("escape_html", ESCAPE_HTML)

        output = self.text_diagram()
        output = "\n".join(output.lines) + "\n"
        if escape_html:
            output = (
                output.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
        write(output)

    def write_standalone(self, write: WriterF, css: Opt[str] = None) -> None:
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
    def __init__(self, *items: Node, parameters: AttrsT = dict()):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        from .utils import add_debug

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="seq seq1", ar=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="seq seq2",
            ar=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap
        for i, item in enumerate(self.items):
            if item.needs_space and i > 0:
                Path(x, y, cls="seq seq3", ar=self.parameters["AR"]).h(10).add_to(self)
                x += 10
            item.format(x, y, item.width).add_to(self)
            x += item.width
            y += item.height
            if item.needs_space and i < len(self.items) - 1:
                Path(x, y, cls="seq seq4", ar=self.parameters["AR"]).h(10).add_to(self)
                x += 10
        return self

    def text_diagram(self) -> TextDiagram:
        (separator,) = TextDiagram._get_parts(["separator"])
        diagram_td = TextDiagram(0, 0, [""])
        for item in self.items:
            item_td = item.text_diagram()
            if item.needs_space:
                item_td = item_td.expand(1, 1, 0, 0)
            diagram_td = diagram_td.append_right(item_td, separator)
        return diagram_td


class Stack(DiagramMultiContainer):
    def __init__(self, *items: Node, parameters: AttrsT = dict()):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        from .utils import add_debug

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="stack stack1", ar=self.parameters["AR"]).h(left_gap).add_to(
            self
        )
        x += left_gap
        x_initial = x
        if len(self.items) > 1:
            Path(x, y, cls="stack stack2", ar=self.parameters["AR"]).h(
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
                    Path(x, y, cls="stack stack3", ar=self.parameters["AR"])
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
                    .right(10)
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
            Path(x, y, cls="stack stack4", ar=self.parameters["AR"]).h(
                self.parameters["AR"]
            ).add_to(self)
            x += self.parameters["AR"]
        Path(x, y, cls="stack stack5", ar=self.parameters["AR"]).h(right_gap).add_to(
            self
        )
        return self

    def text_diagram(self) -> TextDiagram:
        from .defaults import INTERNAL_ALIGNMENT

        internal_alignment = self.parameters.get(
            "internal_alignment", INTERNAL_ALIGNMENT
        )
        (
            corner_bot_left,
            corner_bot_right,
            corner_top_left,
            corner_top_right,
            line,
            line_vertical,
        ) = TextDiagram._get_parts(
            [
                "corner_bot_left",
                "corner_bot_right",
                "corner_top_left",
                "corner_top_right",
                "line",
                "line_vertical",
            ]
        )

        # Format all the child items, so we can know the maximum width.
        items_td = []
        for item in self.items:
            items_td.append(item.text_diagram())
        max_width = max([itemTD.width for itemTD in items_td])

        left_lines = []
        right_lines = []
        separator_td = TextDiagram(0, 0, [line * max_width])
        diagram_td = TextDiagram(0, 0, [])  # Top item will replace it.

        for item_num, item_td in enumerate(items_td):
            if item_num == 0:
                # The top item enters directly from its left.
                left_lines += [line * 2]
                left_lines += [" " * 2] * (item_td.height - item_td.entry - 1)
            else:
                # All items below the top enter from a snake-line from the previous item's exit.
                # Here, we resume that line, already having descended from above on the right.
                diagram_td = diagram_td.append_below(separator_td, [])
                left_lines += [corner_top_left + line]
                left_lines += [line_vertical + " "] * (item_td.entry)
                left_lines += [corner_bot_left + line]
                left_lines += [" " * 2] * (item_td.height - item_td.entry - 1)
                right_lines += [" " * 2] * (item_td.exit)
            if item_num < len(items_td) - 1:
                # All items above the bottom exit via a snake-line to the next item's entry.
                # Here, we start that line on the right.
                right_lines += [line + corner_top_right]
                right_lines += [" " + line_vertical] * (
                    item_td.height - item_td.exit - 1
                )
                right_lines += [line + corner_bot_right]
            else:
                # The bottom item exits directly to its right.
                right_lines += [line * 2]
            leftPad, rightPad = TextDiagram._gaps(
                max_width, item_td.width, internal_alignment
            )
            item_td = item_td.expand(leftPad, rightPad, 0, 0)
            if item_num == 0:
                diagram_td = item_td
            else:
                diagram_td = diagram_td.append_below(item_td, [])

        left_td = TextDiagram(0, 0, left_lines)
        diagram_td = left_td.append_right(diagram_td, "")
        right_td = TextDiagram(0, len(right_lines) - 1, right_lines)
        diagram_td = diagram_td.append_right(right_td, "")
        return diagram_td


class OptionalSequence(DiagramMultiContainer):
    def __new__(cls, *items: Node, parameters: AttrsT = dict()) -> Any:
        if len(items) <= 1:
            return Sequence(*items, parameters=parameters)
        else:
            return super(OptionalSequence, cls).__new__(cls)

    def __init__(self, *items: Node, parameters: AttrsT = dict()):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        from .utils import add_debug

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="optseq os1", ar=self.parameters["AR"]).right(left_gap).add_to(
            self
        )
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="optseq os2",
            ar=self.parameters["AR"],
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
                    Path(x, y, cls="optseq os3", ar=self.parameters["AR"])
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
                    Path(x, y, cls="optseq os4", ar=self.parameters["AR"])
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
                    Path(x, upper_line_y, cls="optseq os5", ar=self.parameters["AR"])
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
                    Path(x, y, cls="optseq os6", ar=self.parameters["AR"])
                    .right(self.parameters["AR"] * 2)
                    .add_to(self)
                )
                item.format(x + self.parameters["AR"] * 2, y, item.width).add_to(self)
                (
                    Path(
                        x + item.width + self.parameters["AR"] * 2,
                        y + item.height,
                        cls="optseq os7",
                        ar=self.parameters["AR"],
                    )
                    .right(item_space + self.parameters["AR"])
                    .add_to(self)
                )
                # Lower skip
                (
                    Path(x, y, cls="optseq os8", ar=self.parameters["AR"])
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
                    Path(x, y, cls="optseq os9", ar=self.parameters["AR"])
                    .right(self.parameters["AR"] * 2)
                    .add_to(self)
                )
                item.format(x + self.parameters["AR"] * 2, y, item.width).add_to(self)
                (
                    Path(
                        x + self.parameters["AR"] * 2 + item.width,
                        y + item.height,
                        cls="optseq os10",
                        ar=self.parameters["AR"],
                    )
                    .right(item_space + self.parameters["AR"])
                    .add_to(self)
                )
                # Lower skip
                (
                    Path(x, y, cls="optseq os11", ar=self.parameters["AR"])
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

    def text_diagram(self) -> TextDiagram:
        (
            line,
            line_vertical,
            round_corner_bot_left,
            round_corner_bot_right,
            round_corner_top_left,
            round_corner_top_right,
        ) = TextDiagram._get_parts(
            [
                "line",
                "line_vertical",
                "round_corner_bot_left",
                "round_corner_bot_right",
                "round_corner_top_left",
                "round_corner_top_right",
            ]
        )

        # Format all the child items, so we can know the maximum entry.
        items_td = []
        for item in self.items:
            items_td.append(item.text_diagram())
        # diagram_entry: distance from top to lowest entry, aka distance from top to diagram entry, aka final diagram entry and exit.
        diagram_entry = max([item_td.entry for item_td in items_td])
        # SOIL_height: distance from top to lowest entry before rightmost item, aka distance from skip-over-items line to rightmost entry, aka SOIL height.
        SOIL_height = max([item_td.entry for item_td in items_td[:-1]])
        # top_to_SOIL: distance from top to skip-over-items line.
        top_to_SOIL = diagram_entry - SOIL_height

        # The diagram starts with a line from its entry up to the skip-over-items line:
        lines = [" " * 2] * top_to_SOIL
        lines += [round_corner_top_left + line]
        lines += [line_vertical + " "] * SOIL_height
        lines += [round_corner_bot_right + line]
        diagram_td = TextDiagram(len(lines) - 1, len(lines) - 1, lines)
        for item_num, item_td in enumerate(items_td):
            if item_num > 0:
                # All items except the leftmost start with a line from their entry down to their skip-under-item line,
                # with a joining-line across at the skip-over-items line:
                lines = []
                lines += [" " * 2] * top_to_SOIL
                lines += [line * 2]
                lines += [" " * 2] * (diagram_td.exit - top_to_SOIL - 1)
                lines += [line + round_corner_top_right]
                lines += [" " + line_vertical] * (item_td.height - item_td.entry - 1)
                lines += [" " + round_corner_bot_left]
                skip_down_td = TextDiagram(diagram_td.exit, diagram_td.exit, lines)
                diagram_td = diagram_td.append_right(skip_down_td, "")
                # All items except the leftmost next have a line from skip-over-items line down to their entry,
                # with joining-lines at their entry and at their skip-under-item line:
                lines = []
                lines += [" " * 2] * top_to_SOIL
                # All such items except the rightmost also have a continuation of the skip-over-items line:
                line_to_next_item = line if item_num < len(items_td) - 1 else " "
                lines += [line + round_corner_top_right + line_to_next_item]
                lines += [" " + line_vertical + " "] * (
                    diagram_td.exit - top_to_SOIL - 1
                )
                lines += [line + round_corner_bot_left + line]
                lines += [" " * 3] * (item_td.height - item_td.entry - 1)
                lines += [line * 3]
                entry_td = TextDiagram(diagram_td.exit, diagram_td.exit, lines)
                diagram_td = diagram_td.append_right(entry_td, "")
            part_td = TextDiagram(0, 0, [])
            if item_num < len(items_td) - 1:
                # All items except the rightmost have a segment of the skip-over-items line at the top,
                # followed by enough blank lines to push their entry down to the previous item's exit:
                lines = []
                lines += [line * item_td.width]
                lines += [" " * item_td.width] * (SOIL_height - item_td.entry)
                SOIL_segment = TextDiagram(0, 0, lines)
                part_td = part_td.append_below(SOIL_segment, [])
            part_td = part_td.append_below(item_td, [], move_entry=True, move_exit=True)
            if item_num > 0:
                # All items except the leftmost have their skip-under-item line at the bottom.
                SUIL_segment = TextDiagram(0, 0, [line * item_td.width])
                part_td = part_td.append_below(SUIL_segment, [])
            diagram_td = diagram_td.append_right(part_td, "")
            if 0 < item_num:
                # All items except the leftmost have a line from their skip-under-item line to their exit:
                lines = []
                lines += [" " * 2] * top_to_SOIL
                # All such items except the rightmost also have a joining-line across at the skip-over-items line:
                skip_over_char = line if item_num < len(items_td) - 1 else " "
                lines += [skip_over_char * 2]
                lines += [" " * 2] * (diagram_td.exit - top_to_SOIL - 1)
                lines += [line + round_corner_top_left]
                lines += [" " + line_vertical] * (part_td.height - part_td.exit - 2)
                lines += [line + round_corner_bot_right]
                skip_up_td = TextDiagram(diagram_td.exit, diagram_td.exit, lines)
                diagram_td = diagram_td.append_right(skip_up_td, "")
        return diagram_td


class AlternatingSequence(DiagramMultiContainer):
    def __new__(cls, *items: Node, parameters: AttrsT = dict()) -> AlternatingSequence:
        if len(items) == 2:
            return super(AlternatingSequence, cls).__new__(cls)
        else:
            raise ParseException(
                "AlternatingSequence takes exactly two arguments, but got {0} arguments.".format(
                    len(items)
                )
            )

    def __init__(self, *items: Node, parameters: AttrsT = dict()):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        from .utils import add_debug

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
        from .utils import determine_gaps

        arc = self.parameters["AR"]
        gaps = determine_gaps(width, self.width, self.parameters["internal_alignment"])
        Path(x, y, cls="altseq as1", ar=self.parameters["AR"]).right(gaps[0]).add_to(
            self
        )
        x += gaps[0]
        Path(x + self.width, y, cls="altseq as2", ar=self.parameters["AR"]).right(
            gaps[1]
        ).add_to(self)
        # bounding box
        # Path(x+gaps[0], y).up(self.up).right(self.width).down(self.up+self.down).left(self.width).up(self.down).addTo(self)
        first = self.items[0]
        second = self.items[1]

        # top
        first_in = self.up - first.up
        first_out = self.up - first.up - first.height
        Path(x, y, cls="altseq as3", ar=self.parameters["AR"]).arc("se").up(
            first_in - 2 * arc
        ).arc("wn").add_to(self)
        first.format(x + 2 * arc, y - first_in, self.width - 4 * arc).add_to(self)
        Path(
            x + self.width - 2 * arc,
            y - first_out,
            cls="altseq as4",
            ar=self.parameters["AR"],
        ).arc("ne").down(first_out - 2 * arc).arc("ws").add_to(self)

        # bottom
        second_in = self.down - second.down - second.height
        second_out = self.down - second.down
        Path(x, y, cls="altseq as5", ar=self.parameters["AR"]).arc("ne").down(
            second_in - 2 * arc
        ).arc("ws").add_to(self)
        second.format(x + 2 * arc, y + second_in, self.width - 4 * arc).add_to(self)
        Path(
            x + self.width - 2 * arc,
            y + second_out,
            cls="altseq as6",
            ar=self.parameters["AR"],
        ).arc("se").up(second_out - 2 * arc).arc("wn").add_to(self)

        # crossover
        arc_x = 1 / Math.sqrt(2) * arc * 2
        arc_y = (1 - 1 / Math.sqrt(2)) * arc * 2
        cross_y = max(arc, self.parameters["VS"])
        cross_x = (cross_y - arc_y) + arc_x
        cross_bar = (self.width - 4 * arc - cross_x) / 2
        (
            Path(
                x + arc,
                y - cross_y / 2 - arc,
                cls="altseq as7",
                ar=self.parameters["AR"],
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
                x + arc,
                y + cross_y / 2 + arc,
                cls="altseq as8",
                ar=self.parameters["AR"],
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

    def text_diagram(self) -> TextDiagram:
        from .defaults import INTERNAL_ALIGNMENT

        internal_alignment = self.parameters.get(
            "internal_alignment", INTERNAL_ALIGNMENT
        )
        (
            cross_diag,
            corner_bot_left,
            corner_bot_right,
            corner_top_left,
            corner_top_right,
            line,
            line_vertical,
            tee_left,
            tee_right,
        ) = TextDiagram._get_parts(
            [
                "cross_diag",
                "round_corner_bot_left",
                "round_corner_bot_right",
                "round_corner_top_left",
                "round_corner_top_right",
                "line",
                "line_vertical",
                "tee_left",
                "tee_right",
            ]
        )

        first_td = self.items[0].text_diagram()
        second_td = self.items[1].text_diagram()
        max_width = TextDiagram._max_width(first_td, second_td)
        left_width, right_width = TextDiagram._gaps(max_width, 0, internal_alignment)
        left_lines = []
        right_lines = []
        separator = []
        left_size, right_size = TextDiagram._gaps(first_td.width, 0, internal_alignment)
        if internal_alignment == "left":
            right_size -= 1
        elif internal_alignment == "right":
            left_size -= 2
        diagram_td = first_td.expand(
            left_width - left_size, right_width - right_size, 0, 0
        )
        left_lines += [" " * 2] * (diagram_td.entry)
        left_lines += [corner_top_left + line]
        left_lines += [line_vertical + " "] * (diagram_td.height - diagram_td.entry - 1)
        left_lines += [corner_bot_left + line]
        right_lines += [" " * 2] * (diagram_td.entry)
        right_lines += [line + corner_top_right]
        right_lines += [" " + line_vertical] * (
            diagram_td.height - diagram_td.entry - 1
        )
        right_lines += [line + corner_bot_right]

        separator += [
            (line * (left_width - 1))
            + corner_top_right
            + " "
            + corner_top_left
            + (line * (right_width - 2))
        ]
        separator += [
            (" " * (left_width - 1))
            + " "
            + cross_diag
            + " "
            + (" " * (right_width - 2))
        ]
        separator += [
            (line * (left_width - 1))
            + corner_bot_right
            + " "
            + corner_bot_left
            + (line * (right_width - 2))
        ]
        left_lines += [" " * 2]
        right_lines += [" " * 2]

        left_size, right_size = TextDiagram._gaps(
            second_td.width, 0, internal_alignment
        )
        if internal_alignment == "left":
            right_size -= 1
        elif internal_alignment == "right":
            left_size -= 2
        second_td = second_td.expand(
            left_width - left_size, right_width - right_size, 0, 0
        )
        diagram_td = diagram_td.append_below(
            second_td, separator, move_entry=True, move_exit=True
        )
        left_lines += [corner_top_left + line]
        left_lines += [line_vertical + " "] * second_td.entry
        left_lines += [corner_bot_left + line]
        right_lines += [line + corner_top_right]
        right_lines += [" " + line_vertical] * second_td.entry
        right_lines += [line + corner_bot_right]

        diagram_td = diagram_td.alter(
            entry=first_td.height + (len(separator) // 2),
            exit=first_td.height + (len(separator) // 2),
        )
        left_td = TextDiagram(
            first_td.height + (len(separator) // 2),
            first_td.height + (len(separator) // 2),
            left_lines,
        )
        right_td = TextDiagram(
            first_td.height + (len(separator) // 2),
            first_td.height + (len(separator) // 2),
            right_lines,
        )
        diagram_td = left_td.append_right(diagram_td, "").append_right(right_td, "")
        diagram_td = (
            TextDiagram(1, 1, [corner_top_left, tee_left, corner_bot_left])
            .append_right(diagram_td, "")
            .append_right(
                TextDiagram(1, 1, [corner_top_right, tee_right, corner_bot_right]), ""
            )
        )
        return diagram_td


class Choice(DiagramMultiContainer):
    def __init__(self, default: int, *items: Node, parameters: AttrsT = dict()):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        assert default < len(items)
        from .utils import add_debug

        self.default = default
        self.width = self.parameters["AR"] * 4 + max(item.width for item in self.items)

        # The size of the vertical separation between an item
        # and the following item.
        # The calcs are non-trivial and need to be done both here
        # and in .format(), so no reason to do it twice.
        self.separators: list[int] = [self.parameters["VS"]] * (len(items) - 1)

        # If the entry or exit lines would be too close together
        # to accommodate the arcs,
        # bump up the vertical separation to compensate.
        self.up = 0
        for i in range(default - 1, -1, -1):
            if i == default - 1:
                arcs = self.parameters["AR"] * 2
            else:
                arcs = self.parameters["AR"]

            item = self.items[i]
            lowerItem = self.items[i + 1]

            entryDelta = lowerItem.up + self.parameters["VS"] + item.down + item.height
            exitDelta = (
                lowerItem.height + lowerItem.up + self.parameters["VS"] + item.down
            )

            separator = self.parameters["VS"]
            if exitDelta < arcs or entryDelta < arcs:
                separator += max(arcs - entryDelta, arcs - exitDelta)
            self.separators[i] = separator
            self.up += lowerItem.up + separator + item.down + item.height
        self.up += self.items[0].up

        self.height = self.items[default].height

        for i in range(default + 1, len(self.items)):
            if i == default + 1:
                arcs = self.parameters["AR"] * 2
            else:
                arcs = self.parameters["AR"]

            item = self.items[i]
            upperItem = self.items[i - 1]

            entryDelta = (
                upperItem.height + upperItem.down + self.parameters["VS"] + item.up
            )
            exitDelta = upperItem.down + self.parameters["VS"] + item.up + item.height

            separator = self.parameters["VS"]
            if entryDelta < arcs or exitDelta < arcs:
                separator += max(arcs - entryDelta, arcs - exitDelta)
            self.separators[i - 1] = separator
            self.down += upperItem.down + separator + item.up + item.height
        self.down += self.items[-1].down
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
        from .utils import determine_gaps, double_enumerate

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="choice ch1", ar=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="choice ch2",
            ar=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        inner_width = self.width - self.parameters["AR"] * 4
        default = self.items[self.default]

        # Do the elements that curve above
        distance_from_y = 0
        for i in range(self.default - 1, -1, -1):
            item = self.items[i]
            lower_item = self.items[i + 1]
            distance_from_y += (
                lower_item.up + self.separators[i] + item.down + item.height
            )
            Path(x, y, cls="choice ch3", ar=self.parameters["AR"]).arc("se").up(
                distance_from_y - self.parameters["AR"] * 2
            ).arc("wn").add_to(self)
            item.format(
                x + self.parameters["AR"] * 2, y - distance_from_y, inner_width
            ).add_to(self)
            Path(
                x + self.parameters["AR"] * 2 + inner_width,
                y - distance_from_y + item.height,
                cls="choice ch4",
                ar=self.parameters["AR"],
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

        # Do the straight-line path.
        Path(x, y, cls="choice ch5", ar=self.parameters["AR"]).right(
            self.parameters["AR"] * 2
        ).add_to(self)
        self.items[self.default].format(
            x + self.parameters["AR"] * 2, y, inner_width
        ).add_to(self)
        Path(
            x + self.parameters["AR"] * 2 + inner_width,
            y + self.height,
            cls="choice ch6",
            ar=self.parameters["AR"],
        ).right(self.parameters["AR"] * 2).add_to(self)

        # Do the elements that curve below
        distance_from_y = 0
        for i in range(self.default + 1, len(self.items)):
            item = self.items[i]
            upper_item = self.items[i - 1]
            distance_from_y += (
                upper_item.height + upper_item.down + self.separators[i - 1] + item.up
            )
            Path(x, y, cls="choice ch7", ar=self.parameters["AR"]).arc("ne").down(
                distance_from_y - self.parameters["AR"] * 2
            ).arc("ws").add_to(self)
            item.format(
                x + self.parameters["AR"] * 2, y + distance_from_y, inner_width
            ).add_to(self)
            Path(
                x + self.parameters["AR"] * 2 + inner_width,
                y + distance_from_y + item.height,
                cls="choice ch8",
                ar=self.parameters["AR"],
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

        return self

    def text_diagram(self) -> TextDiagram:
        from .defaults import INTERNAL_ALIGNMENT

        internal_alignment = self.parameters.get(
            "internal_alignment", INTERNAL_ALIGNMENT
        )
        (
            cross,
            line,
            line_vertical,
            round_corner_bot_left,
            round_corner_bot_right,
            round_corner_top_left,
            round_corner_top_right,
        ) = TextDiagram._get_parts(
            [
                "cross",
                "line",
                "line_vertical",
                "round_corner_bot_left",
                "round_corner_bot_right",
                "round_corner_top_left",
                "round_corner_top_right",
            ]
        )
        # Format all the child items, so we can know the maximum width.
        items_td = []
        for item in self.items:
            items_td.append(item.text_diagram().expand(1, 1, 0, 0))
        max_item_width = max([i.width for i in items_td])
        diagram_td = TextDiagram(0, 0, [])
        # Format the choice collection.
        for item_num, item_td in enumerate(items_td):
            left_pad, right_pad = TextDiagram._gaps(
                max_item_width, item_td.width, internal_alignment
            )
            item_td = item_td.expand(left_pad, right_pad, 0, 0)
            has_separator = True
            left_lines = [line_vertical] * item_td.height
            right_lines = [line_vertical] * item_td.height
            move_entry = False
            move_exit = False
            if item_num <= self.default:
                # Item above the line: round off the entry/exit lines upwards.
                left_lines[item_td.entry] = round_corner_top_left
                right_lines[item_td.exit] = round_corner_top_right
                if item_num == 0:
                    # First item and above the line: also remove ascenders above the item's entry and exit, suppress the separator above it.
                    has_separator = False
                    for i in range(0, item_td.entry):
                        left_lines[i] = " "
                    for i in range(0, item_td.exit):
                        right_lines[i] = " "
            if item_num >= self.default:
                # Item below the line: round off the entry/exit lines downwards.
                left_lines[item_td.entry] = round_corner_bot_left
                right_lines[item_td.exit] = round_corner_bot_right
                if item_num == 0:
                    # First item and below the line: also suppress the separator above it.
                    has_separator = False
                if item_num == (len(self.items) - 1):
                    # Last item and below the line: also remove descenders below the item's entry and exit
                    for i in range(item_td.entry + 1, item_td.height):
                        left_lines[i] = " "
                    for i in range(item_td.exit + 1, item_td.height):
                        right_lines[i] = " "
            if item_num == self.default:
                # Item on the line: entry/exit are horizontal, and sets the outer entry/exit.
                left_lines[item_td.entry] = cross
                right_lines[item_td.exit] = cross
                move_entry = True
                move_exit = True
                if item_num == 0 and item_num == (len(self.items) - 1):
                    # Only item and on the line: set entry/exit for straight through.
                    left_lines[item_td.entry] = line
                    right_lines[item_td.exit] = line
                elif item_num == 0:
                    # First item and on the line: set entry/exit for no ascenders.
                    left_lines[item_td.entry] = round_corner_top_right
                    right_lines[item_td.exit] = round_corner_top_left
                elif item_num == (len(self.items) - 1):
                    # Last item and on the line: set entry/exit for no descenders.
                    left_lines[item_td.entry] = round_corner_bot_right
                    right_lines[item_td.exit] = round_corner_bot_left
            left_joint_td = TextDiagram(item_td.entry, item_td.entry, left_lines)
            right_joint_td = TextDiagram(item_td.exit, item_td.exit, right_lines)
            item_td = left_joint_td.append_right(item_td, "").append_right(
                right_joint_td, ""
            )
            separator = (
                [
                    line_vertical
                    + (" " * (TextDiagram._max_width(diagram_td, item_td) - 2))
                    + line_vertical
                ]
                if has_separator
                else []
            )
            diagram_td = diagram_td.append_below(
                item_td, separator, move_entry=move_entry, move_exit=move_exit
            )
        return diagram_td


class MultipleChoice(DiagramMultiContainer):
    def __init__(
        self, default: int, type: str, *items: Node, parameters: AttrsT = dict()
    ):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        from .utils import add_debug

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
        from .utils import determine_gaps, double_enumerate

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="multichoice mc1", ar=self.parameters["AR"]).h(left_gap).add_to(
            self
        )
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="multichoice mc2",
            ar=self.parameters["AR"],
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
                Path(x + 30, y, cls="multichoice mc3", ar=self.parameters["AR"])
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
                    cls="multichoice mc4",
                    ar=self.parameters["AR"],
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
        Path(x + 30, y, cls="multichoice mc5", ar=self.parameters["AR"]).right(
            self.parameters["AR"]
        ).add_to(self)
        self.items[self.default].format(
            x + 30 + self.parameters["AR"], y, self.inner_width
        ).add_to(self)
        Path(
            x + 30 + self.parameters["AR"] + self.inner_width,
            y + self.height,
            cls="multichoice mc6",
            ar=self.parameters["AR"],
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
                Path(x + 30, y, cls="multichoice mc7", ar=self.parameters["AR"])
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
                    cls="multichoice mc8",
                    ar=self.parameters["AR"],
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
            text=(
                "take one or more branches, once each, in any order"
                if self.type == "any"
                else "take all branches, once each, in any order"
            ),
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

    def text_diagram(self) -> TextDiagram:
        (multi_repeat,) = TextDiagram._get_parts(["multi_repeat"])
        any_all = TextDiagram.rect("1+" if self.type == "any" else "all")
        diagram_td = Choice.text_diagram(self)
        repeat_td = TextDiagram.rect(multi_repeat)
        diagram_td = any_all.append_right(diagram_td, "")
        diagram_td = diagram_td.append_right(repeat_td, "")
        return diagram_td


class HorizontalChoice(DiagramMultiContainer):
    def __new__(cls, *items: Node, parameters: AttrsT = dict()) -> Any:
        if len(items) <= 1:
            return Sequence(*items, parameters=parameters)
        else:
            return super(HorizontalChoice, cls).__new__(cls)

    def __init__(self, *items: Node, parameters: AttrsT = dict()):
        DiagramMultiContainer.__init__(self, "g", items, parameters=parameters)
        from .utils import add_debug

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
            (
                max(
                    x.height
                    + max(x.down + self.parameters["VS"], self.parameters["AR"] * 2)
                    for x in middles
                )
                if middles
                else 0
            ),
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
        from .utils import determine_gaps

        # Hook up the two sides if self is narrower than its stated width.
        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="horizchoice hc1", ar=self.parameters["AR"]).h(left_gap).add_to(
            self
        )
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="horizchoice hc2",
            ar=self.parameters["AR"],
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
            Path(x, y, cls="horizchoice hc3", ar=self.parameters["AR"])
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
                cls="horizchoice hc4",
                ar=self.parameters["AR"],
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
                    Path(x, y, cls="horizchoice hc5", ar=self.parameters["AR"])
                    .h(self.parameters["AR"])
                    .add_to(self)
                )
                x += self.parameters["AR"]
            else:
                (
                    Path(
                        x,
                        y - self._upperTrack,
                        cls="horizchoice hc6",
                        ar=self.parameters["AR"],
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
                        Path(x, y, cls="horizchoice hc7", ar=self.parameters["AR"])
                        .h(self.parameters["AR"])
                        .add_to(self)
                    )
                else:
                    (
                        Path(
                            x,
                            y + item.height,
                            cls="horizchoice hc8",
                            ar=self.parameters["AR"],
                        )
                        .arc("se")
                        .add_to(self)
                    )
            elif i == 0 and item.height > self._lowerTrack:
                # Needs to arc up to meet the lower track, not down.
                if item.height - self._lowerTrack >= self.parameters["AR"] * 2:
                    (
                        Path(
                            x,
                            y + item.height,
                            cls="horizchoice hc9",
                            ar=self.parameters["AR"],
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
                            x,
                            y + item.height,
                            cls="horizchoice hc10",
                            ar=self.parameters["AR"],
                        )
                        .l(self.parameters["AR"] * 2, self._lowerTrack - item.height)
                        .add_to(self)
                    )
            else:
                (
                    Path(
                        x,
                        y + item.height,
                        cls="horizchoice hc11",
                        ar=self.parameters["AR"],
                    )
                    .arc("ne")
                    .v(self._lowerTrack - item.height - self.parameters["AR"] * 2)
                    .arc("ws")
                    .add_to(self)
                )
        return self

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self.items)
        return f"HorizontalChoice({items})"

    def text_diagram(self) -> TextDiagram:
        (
            line,
            line_vertical,
            round_corner_bot_left,
            round_corner_bot_right,
            round_corner_top_left,
            round_corner_top_right,
        ) = TextDiagram._get_parts(
            [
                "line",
                "line_vertical",
                "round_corner_bot_left",
                "round_corner_bot_right",
                "round_corner_top_left",
                "round_corner_top_right",
            ]
        )

        # Format all the child items, so we can know the maximum entry, exit, and height.
        items_td = []
        for item in self.items:
            items_td.append(item.text_diagram())
        # diagram_entry: distance from top to lowest entry, aka distance from top to diagram entry, aka final diagram entry and exit.
        diagram_entry = max([itemTD.entry for itemTD in items_td])
        # SOIL_to_baseline: distance from top to lowest entry before rightmost item, aka distance from skip-over-items line to rightmost entry, aka SOIL height.
        SOIL_to_baseline = max([itemTD.entry for itemTD in items_td[:-1]])
        # top_to_SOIL: distance from top to skip-over-items line.
        top_to_SOIL = diagram_entry - SOIL_to_baseline
        # baseline_to_SUIL: distance from lowest entry or exit after leftmost item to bottom, aka distance from entry to skip-under-items line, aka SUIL height.
        baseline_to_SUIL = (
            max(
                [
                    item_td.height - min(item_td.entry, item_td.exit)
                    for item_td in items_td[1:]
                ]
            )
            - 1
        )

        # The diagram starts with a line from its entry up to skip-over-items line:
        lines = [" " * 2] * top_to_SOIL
        lines += [round_corner_top_left + line]
        lines += [line_vertical + " "] * SOIL_to_baseline
        lines += [round_corner_bot_right + line]
        diagram_td = TextDiagram(len(lines) - 1, len(lines) - 1, lines)
        for item_num, item_td in enumerate(items_td):
            if item_num > 0:
                # All items except the leftmost start with a line from the skip-over-items line down to their entry,
                # with a joining-line across at the skip-under-items line:
                lines = []
                lines += [" " * 2] * top_to_SOIL
                # All such items except the rightmost also have a continuation of the skip-over-items line:
                line_to_next_item = " " if item_num == len(items_td) - 1 else line
                lines += [round_corner_top_right + line_to_next_item]
                lines += [line_vertical + " "] * SOIL_to_baseline
                lines += [round_corner_bot_left + line]
                lines += [" " * 2] * baseline_to_SUIL
                lines += [line * 2]
                entryTD = TextDiagram(diagram_td.exit, diagram_td.exit, lines)
                diagram_td = diagram_td.append_right(entryTD, "")
            part_td = TextDiagram(0, 0, [])
            if item_num < len(items_td) - 1:
                # All items except the rightmost start with a segment of the skip-over-items line at the top.
                # followed by enough blank lines to push their entry down to the previous item's exit:
                lines = []
                lines += [line * item_td.width]
                lines += [" " * item_td.width] * (SOIL_to_baseline - item_td.entry)
                SOIL_segment = TextDiagram(0, 0, lines)
                part_td = part_td.append_below(SOIL_segment, [])
            part_td = part_td.append_below(item_td, [], move_entry=True, move_exit=True)
            if item_num > 0:
                # All items except the leftmost end with enough blank lines to pad down to the skip-under-items
                # line, followed by a segment of the skip-under-items line:
                lines = []
                lines += [" " * item_td.width] * (
                    baseline_to_SUIL - (item_td.height - item_td.entry) + 1
                )
                lines += [line * item_td.width]
                SUIL_segment = TextDiagram(0, 0, lines)
                part_td = part_td.append_below(SUIL_segment, [])
            diagram_td = diagram_td.append_right(part_td, "")
            if item_num < len(items_td) - 1:
                # All items except the rightmost have a line from their exit down to the skip-under-items line,
                # with a joining-line across at the skip-over-items line:
                lines = []
                lines += [" " * 2] * top_to_SOIL
                lines += [line * 2]
                lines += [" " * 2] * (diagram_td.exit - top_to_SOIL - 1)
                lines += [line + round_corner_top_right]
                lines += [" " + line_vertical] * (
                    baseline_to_SUIL - (diagram_td.exit - diagram_td.entry)
                )
                # All such items except the leftmost also have are continuing of the skip-under-items line from the previous item:
                lineFromPrevItem = line if item_num > 0 else " "
                lines += [lineFromPrevItem + round_corner_bot_left]
                entry = diagram_entry + 1 + (diagram_td.exit - diagram_td.entry)
                exit_td = TextDiagram(entry, diagram_entry + 1, lines)
                diagram_td = diagram_td.append_right(exit_td, "")
            else:
                # The rightmost item has a line from the skip-under-items line and from its exit up to the diagram exit:
                lines = []
                lineFromExit = " " if diagram_td.exit != diagram_td.entry else line
                lines += [lineFromExit + round_corner_top_left]
                lines += [" " + line_vertical] * (
                    diagram_td.exit - diagram_td.entry - 1
                )
                if diagram_td.exit != diagram_td.entry:
                    lines += [line + round_corner_bot_right]
                lines += [" " + line_vertical] * (
                    baseline_to_SUIL - (diagram_td.exit - diagram_td.entry)
                )
                lines += [line + round_corner_bot_right]
                exit_td = TextDiagram(diagram_td.exit - diagram_td.entry, 0, lines)
                diagram_td = diagram_td.append_right(exit_td, "")
        return diagram_td


def optional(item: Node, skip: bool = False, parameters: AttrsT = dict()) -> Choice:
    return Choice(
        0 if skip else 1, Skip(parameters=parameters), item, parameters=parameters
    )


class OneOrMore(DiagramItem):
    def __init__(
        self, item: Node, repeat: Opt[Node] = None, parameters: AttrsT = dict()
    ):
        DiagramItem.__init__(self, "g", parameters=parameters)
        from .utils import add_debug, wrap_string

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="oneor oom1", ar=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="oneor oom2",
            ar=self.parameters["AR"],
        ).h(right_gap).add_to(self)
        x += left_gap

        # Draw item
        Path(x, y, cls="oneor oom3", ar=self.parameters["AR"]).right(
            self.parameters["AR"]
        ).add_to(self)
        self.item.format(
            x + self.parameters["AR"], y, self.width - self.parameters["AR"] * 2
        ).add_to(self)
        Path(
            x + self.width - self.parameters["AR"],
            y + self.height,
            cls="oneor oom4",
            ar=self.parameters["AR"],
        ).right(self.parameters["AR"]).add_to(self)

        # Draw repeat arc
        distance_from_y = max(
            self.parameters["AR"] * 2,
            self.item.height + self.item.down + self.parameters["VS"] + self.rep.up,
        )
        Path(
            x + self.parameters["AR"], y, cls="oneor oom5", ar=self.parameters["AR"]
        ).arc("nw").down(distance_from_y - self.parameters["AR"] * 2).arc("ws").add_to(
            self
        )
        self.rep.format(
            x + self.parameters["AR"],
            y + distance_from_y,
            self.width - self.parameters["AR"] * 2,
        ).add_to(self)
        Path(
            x + self.width - self.parameters["AR"],
            y + distance_from_y + self.rep.height,
            cls="oneor oom6",
            ar=self.parameters["AR"],
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

    def text_diagram(self) -> TextDiagram:
        (
            line,
            repeat_top_left,
            repeat_left,
            repeat_bot_left,
            repeat_top_right,
            repeat_right,
            repeat_bot_right,
        ) = TextDiagram._get_parts(
            [
                "line",
                "repeat_top_left",
                "repeat_left",
                "repeat_bot_left",
                "repeat_top_right",
                "repeat_right",
                "repeat_bot_right",
            ]
        )
        # Format the item and then format the repeat append it to tbe bottom, after a spacer.
        item_td = self.item.text_diagram()
        repeat_td = self.rep.text_diagram()
        f_IR_width = TextDiagram._max_width(item_td, repeat_td)
        repeat_td = repeat_td.expand(0, f_IR_width - repeat_td.width, 0, 0)
        item_td = item_td.expand(0, f_IR_width - item_td.width, 0, 0)
        item_and_repeat_td = item_td.append_below(repeat_td, [])
        # Build the left side of the repeat line and append the combined item and repeat to its right.
        left_lines = []
        left_lines += [repeat_top_left + line]
        left_lines += [repeat_left + " "] * (
            (item_td.height - item_td.entry) + repeat_td.entry - 1
        )
        left_lines += [repeat_bot_left + line]
        left_td = TextDiagram(0, 0, left_lines)
        left_td = left_td.append_right(item_and_repeat_td, "")
        # Build the right side of the repeat line and append it to the combined left side, item, and repeat's right.
        right_lines = []
        right_lines += [line + repeat_top_right]
        right_lines += [" " + repeat_right] * (
            (item_td.height - item_td.exit) + repeat_td.exit - 1
        )
        right_lines += [line + repeat_bot_right]
        right_td = TextDiagram(0, 0, right_lines)
        diagram_td = left_td.append_right(right_td, "")
        return diagram_td


def zero_or_more(
    item: Node,
    repeat: Opt[Node] = None,
    skip: bool = False,
    parameters: AttrsT = dict(),
) -> Choice:
    result = optional(
        OneOrMore(item, repeat, parameters=parameters), skip, parameters=parameters
    )
    return result


class Group(DiagramItem):
    def __init__(
        self, item: Node, label: Opt[Node] = None, parameters: AttrsT = dict()
    ):
        DiagramItem.__init__(self, "g", parameters=parameters)
        from .utils import add_debug, wrap_string

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )
        Path(x, y, cls="group gr1", ar=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width,
            y + self.height,
            cls="group gr2",
            ar=self.parameters["AR"],
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

    def text_diagram(self) -> TextDiagram:
        diagram_td = TextDiagram.round_rect(self.item.text_diagram(), dashed=True)
        if self.label:
            label_td = self.label.text_diagram()
            diagram_td = label_td.append_below(
                diagram_td, [], move_entry=True, move_exit=True
            ).expand(0, 0, 1, 0)
        return diagram_td

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
        self, type: str = "simple", label: Opt[str] = None, parameters: AttrsT = dict()
    ):
        DiagramItem.__init__(self, "g", parameters=parameters)
        from .utils import add_debug

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
        path = Path(x, y - 10, cls="start")
        if self.type == "complex":
            path.down(20).m(0, -10).right(self.width).add_to(self)
        elif self.type == "sql":
            path = Path(x, y - 10, cls="start ")
            path.m(0, 10).a(3.7).big_m(x, y).right(self.width).add_to(self)
        else:
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

    def text_diagram(self) -> TextDiagram:
        cross, line, tee_right, ball = TextDiagram._get_parts(
            ["cross", "line", "tee_right", "ball"]
        )
        if self.type == "simple":
            start = tee_right + cross + line
        elif self.type == "sql":
            start = ball + line
        else:
            start = tee_right + line
        label_td = TextDiagram(0, 0, [])
        if self.label:
            label_td = TextDiagram(0, 0, [self.label])
            start = TextDiagram._padR(start, label_td.width, line)
        start_td = TextDiagram(0, 0, [start])
        return label_td.append_below(start_td, [], move_entry=True, move_exit=True)

    def to_dict(self) -> dict:
        return {"element": "Start", "type": self.type, "label": self.label}


class End(DiagramItem):
    def __init__(self, type: str = "simple", parameters: AttrsT = dict()):
        DiagramItem.__init__(self, "path", parameters=parameters)
        from .utils import add_debug

        self.width = 20
        self.up = 10
        self.down = 10
        self.type = type
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> End:
        # TODO: use the width
        self.attrs["class"] = "end"
        if self.type == "simple":
            self.attrs["d"] = "M {0} {1} h 20 m -10 -10 v 20 m 10 -20 v 20".format(x, y)
        elif self.type == "complex":
            self.attrs["d"] = "M {0} {1} h 20 m 0 -10 v 20".format(x, y)
        elif self.type == "sql":
            self.attrs["d"] = "M {0} {1} h 20 m -5 -5 5,5 -5,5".format(x, y)
        return self

    def __repr__(self) -> str:
        return f"End(type={repr(self.type)})"

    def text_diagram(self) -> TextDiagram:
        cross, line, tee_left, arrow_right = TextDiagram._get_parts(
            ["cross", "line", "tee_left", "arrow_right"]
        )
        if self.type == "simple":
            end = line + cross + tee_left
        elif self.type == "sql":
            end = line + arrow_right
        else:
            end = line + tee_left
        return TextDiagram(0, 0, [end])

    def to_dict(self) -> dict:
        return {"element": "End", "type": self.type}


class Arrow(DiagramItem):
    def __init__(self, direction: str = "right", parameters: AttrsT = dict()):
        DiagramItem.__init__(self, "path", parameters=parameters)
        from .utils import add_debug

        self.width = 20
        self.up = 10
        self.down = 10
        self.direction = direction
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> Arrow:
        self.attrs["class"] = "arrow"
        if self.direction == "right":
            self.attrs["d"] = "M {0} {1} h {2} m -5 -5 5,5 -5,5".format(x, y, width)
        elif self.direction == "left":
            self.attrs["d"] = "M {0} {1} m 5 -5 -5,5 5,5 -5,-5 h {2}".format(
                x, y, width
            )
        else:
            self.attrs["d"] = "M {0} {1} h {2}".format(x, y, width)
        return self

    def __repr__(self) -> str:
        return f"Arrow(direction={repr(self.direction)})"

    def text_diagram(self) -> TextDiagram:
        line, arrow_right, arrow_left = TextDiagram._get_parts(
            ["line", "arrow_right", "arrow_left"]
        )
        if self.direction == "right":
            arrow = line + arrow_right + line
        elif self.direction == "left":
            arrow = line + arrow_left + line
        else:
            arrow = line + line + line
        return TextDiagram(0, 0, [arrow])

    def to_dict(self) -> dict:
        return {"element": "Arrow", "direction": self.direction}


class Terminal(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: AttrsT = dict(),
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["terminal", cls])}, parameters=parameters
        )
        from .utils import add_debug

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="terminal term1", ar=self.parameters["AR"]).h(left_gap).add_to(
            self
        )
        Path(
            x + left_gap + self.width, y, cls="terminal term2", ar=self.parameters["AR"]
        ).h(right_gap).add_to(self)

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
            DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self

    def text_diagram(self) -> TextDiagram:
        # Note: href, title, and cls are ignored for text diagrams.
        return TextDiagram.round_rect(self.text)


class NonTerminal(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: AttrsT = dict(),
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["non-terminal", cls])}, parameters=parameters
        )
        from .utils import add_debug

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="nonterm nt1", ar=self.parameters["AR"]).h(left_gap).add_to(self)
        Path(
            x + left_gap + self.width, y, cls="nonterm nt2", ar=self.parameters["AR"]
        ).h(right_gap).add_to(self)

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
            DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self

    def text_diagram(self) -> TextDiagram:
        # Note: href, title, and cls are ignored for text diagrams.
        return TextDiagram.rect(self.text)


class Expression(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: AttrsT = dict(),
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["expression", cls])}, parameters=parameters
        )
        from .utils import add_debug

        self.text = text
        self.href = href
        self.title = title
        self.cls = cls
        self.width = len(text) * self.parameters["char_width"] + 40
        self.up = 11
        self.down = 11
        self.needs_space = True
        add_debug(self)

    def to_dict(self) -> dict:
        return {
            "element": "Expression",
            "text": self.text,
            "href": self.href,
            "title": self.title,
            "cls": self.cls,
        }

    def __repr__(self) -> str:
        return f"Expression({repr(self.text)}, href={repr(self.href)}, title={repr(self.title)}, cls={repr(self.cls)})"

    def format(self, x: float, y: float, width: float) -> Expression:
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="expression exp1", ar=self.parameters["AR"]).h(left_gap).add_to(
            self
        )
        Path(
            x + left_gap + self.width,
            y,
            cls="expression exp2",
            ar=self.parameters["AR"],
        ).h(right_gap).add_to(self)

        w = self.width
        h = self.up + self.down
        DiagramItem(
            "polygon",
            {
                "points": f"{x + left_gap + 10}, {y-11} {x + left_gap + w - 10}, {y-11} {x + left_gap + w}, {y} {x + left_gap + w - 10}, {y-11 + h} {x + left_gap + 10}, {y-11 + h} {x + left_gap}, {y}"
            },
        ).add_to(self)
        text = DiagramItem(
            "text", {"x": x + left_gap + self.width / 2, "y": y + 4}, self.text
        )
        if self.href is not None:
            DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self

    def text_diagram(self) -> TextDiagram:
        return TextDiagram.angle_rect(self.text)


class Comment(DiagramItem):
    def __init__(
        self,
        text: str,
        href: Opt[str] = None,
        title: Opt[str] = None,
        cls: str = "",
        parameters: AttrsT = dict(),
    ):
        DiagramItem.__init__(
            self, "g", {"class": " ".join(["non-terminal", cls])}, parameters=parameters
        )
        from .utils import add_debug

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
        from .utils import determine_gaps

        left_gap, right_gap = determine_gaps(
            width, self.width, self.parameters["internal_alignment"]
        )

        # Hook up the two sides if self is narrower than its stated width.
        Path(x, y, cls="comment com1", ar=self.parameters["AR"]).h(left_gap).add_to(
            self
        )
        Path(
            x + left_gap + self.width, y, cls="comment com2", ar=self.parameters["AR"]
        ).h(right_gap).add_to(self)

        text = DiagramItem(
            "text",
            {"x": x + left_gap + self.width / 2, "y": y + 5, "class": "comment"},
            self.text,
        )
        if self.href is not None:
            DiagramItem("a", {"xlink:href": self.href}, text).add_to(self)
        else:
            text.add_to(self)
        if self.title is not None:
            DiagramItem("title", {}, self.title).add_to(self)
        return self

    def text_diagram(self) -> TextDiagram:
        # Note: href, title, and cls are ignored for text diagrams.
        return TextDiagram(0, 0, [self.text])


class Skip(DiagramItem):
    def __init__(self, parameters: AttrsT = dict()) -> None:
        DiagramItem.__init__(self, "g", parameters=parameters)
        from .utils import add_debug

        self.width = 0
        self.up = 0
        self.down = 0
        add_debug(self)

    def format(self, x: float, y: float, width: float) -> Skip:
        Path(x, y, cls="skip", ar=self.parameters["AR"]).right(width).add_to(self)
        return self

    def __repr__(self) -> str:
        return "Skip()"

    def text_diagram(self) -> TextDiagram:
        (line,) = TextDiagram._get_parts(["line"])
        return TextDiagram(0, 0, [line])

    def to_dict(self) -> dict:
        return {"element": "Skip"}


class TextDiagram:
    # Characters to use in drawing diagrams.  See setFormatting(), PARTS_ASCII, and PARTS_UNICODE.
    parts: Dict[str, str]

    def __init__(self, entry: int, exit: int, lines: List[str]):
        # entry: The entry line for this diagram-part.
        self.entry: int = entry
        # exit: The exit line for this diagram-part.
        self.exit: int = exit
        # height: The height of this diagram-part, in lines.
        self.height: int = len(lines)
        # lines[]: The visual data of this diagram-part.  Each line must be the same length.
        self.lines: List[str] = lines.copy()
        # width: The width of this diagram-part, in character cells.
        self.width: int = len(lines[0]) if len(lines) > 0 else 0
        nl = "\n"  # f-strings can't contain \n until Python 3.12
        assert entry <= len(
            lines
        ), f"Entry is not within diagram vertically:{nl}{self._dump(False)}"
        assert exit <= len(
            lines
        ), f"Exit is not within diagram vertically:{nl}{self._dump(False)}"
        for i in range(0, len(lines)):
            assert len(lines[0]) == len(
                lines[i]
            ), f"Diagram data is not rectangular:{nl}{self._dump(False)}"

    def alter(
        self,
        entry: Opt[int] = None,
        exit: Opt[int] = None,
        lines: Opt[List[str]] = None,
    ) -> TextDiagram:
        """
        Create and return a new TextDiagram based on this instance, with the specified changes.

        Note: This is used sparingly, and may be a bad idea.
        """
        new_entry = entry or self.entry
        new_exit = exit or self.exit
        new_lines = lines or self.lines
        return self.__class__(new_entry, new_exit, new_lines.copy())

    def append_below(
        self,
        item: TextDiagram,
        lines_between: List[str],
        move_entry=False,
        move_exit=False,
    ) -> TextDiagram:
        """
        Create and return a new TextDiagram by appending the specified lines below this instance's data,
        and then appending the specified TextDiagram below those lines, possibly setting the resulting
        TextDiagram's entry and or exit indices to those of the appended item.
        """
        new_width = max(self.width, item.width)
        new_lines = []
        new_lines += self.center(new_width, " ").lines
        for line in lines_between:
            new_lines += [TextDiagram._padR(line, new_width, " ")]
        new_lines += item.center(new_width, " ").lines
        new_entry = (
            self.height + len(lines_between) + item.entry if move_entry else self.entry
        )
        new_exit = (
            self.height + len(lines_between) + item.exit if move_exit else self.exit
        )
        new_self = self.__class__(new_entry, new_exit, new_lines)
        return new_self

    def append_right(self, item: TextDiagram, charsBetween: str) -> TextDiagram:
        """
        Create and return a new TextDiagram by appending the specified TextDiagram to the right of this instance's data,
        aligning the left-hand exit and the right-hand entry points.  The charsBetween are inserted between the left-exit
        and right-entry, and equivalent spaces on all other lines.
        """
        join_line = max(self.exit, item.entry)
        new_height = max(self.height - self.exit, item.height - item.entry) + join_line
        left_top_add = join_line - self.exit
        left_bot_add = new_height - self.height - left_top_add
        right_top_add = join_line - item.entry
        right_bot_add = new_height - item.height - right_top_add
        left = self.expand(0, 0, left_top_add, left_bot_add)
        right = item.expand(0, 0, right_top_add, right_bot_add)
        new_lines = []
        for i in range(0, new_height):
            sep = " " * len(charsBetween) if i != join_line else charsBetween
            new_lines += [left.lines[i] + sep + right.lines[i]]
        new_entry = self.entry + left_top_add
        new_exit = item.exit + right_top_add
        return self.__class__(new_entry, new_exit, new_lines)

    def center(self, width: int, pad: str) -> TextDiagram:
        """
        Create and return a new TextDiagram by centering the data of this instance within a new, equal or larger widtth.
        """
        assert width >= self.width, "Cannot center into smaller width"
        if width == self.width:
            return self.copy()
        else:
            total_padding = width - self.width
            left_width = total_padding // 2
            left = [pad * left_width] * self.height
            right = [pad * (total_padding - left_width)] * self.height
            return self.__class__(
                self.entry,
                self.exit,
                TextDiagram._enclose_lines(self.lines, left, right),
            )

    def copy(self) -> TextDiagram:
        """
        Create and return a new TextDiagram by copying this instance's data.
        """
        return self.__class__(self.entry, self.exit, self.lines.copy())

    def expand(self, left: int, right: int, top: int, bottom: int) -> TextDiagram:
        """
        Create and return a new TextDiagram by expanding this instance's data by the specified amount in the specified directions.
        """
        assert left >= 0
        assert right >= 0
        assert top >= 0
        assert bottom >= 0
        if left + right + top + bottom == 0:
            return self.copy()
        else:
            line = self.parts["line"]
            new_lines = []
            new_lines += [" " * (self.width + left + right)] * top
            for i in range(0, self.height):
                left_expansion = line if i == self.entry else " "
                right_expansion = line if i == self.exit else " "
                new_lines += [
                    (left_expansion * left) + self.lines[i] + (right_expansion * right)
                ]
            new_lines += [" " * (self.width + left + right)] * bottom
            return self.__class__(self.entry + top, self.exit + top, new_lines)

    @classmethod
    def rect(cls, item: Union[str, TextDiagram], dashed=False) -> TextDiagram:
        """
        Create and return a new TextDiagram for a rectangular box.
        """
        return cls._rectish("rect", item, dashed=dashed)

    @classmethod
    def round_rect(cls, item: Union[str, TextDiagram], dashed=False) -> TextDiagram:
        """
        Create and return a new TextDiagram for a rectangular box with rounded corners.
        """
        return cls._rectish("round_rect", item, dashed=dashed)

    @classmethod
    def angle_rect(cls, item: Union[str, TextDiagram], dashed=False) -> TextDiagram:
        """
        Create and return a new TextDiagram for a rectangular box with rounded corners.
        """
        return cls._rectish("angle_rect", item, dashed=dashed)

    @classmethod
    def set_formatting(
        cls,
        characters: Opt[Dict[str, str]] = None,
        defaults: Opt[Dict[str, str]] = None,
    ) -> None:
        """
        Set the characters to use for drawing text diagrams.
        """
        if characters is not None:
            cls.parts = {}
            if defaults is not None:
                cls.parts.update(defaults)
            cls.parts.update(characters)
        for name in cls.parts:
            assert (
                len(cls.parts[name]) == 1
            ), f"Text part {name} is more than 1 character: {cls.parts[name]}"

    def _dump(self, show=True) -> Opt[str]:
        """
        Dump out the data of this instance for debugging, either displaying or returning it.
        DO NOT use this for actual work, only for debugging or in assertion output.
        """
        nl = "\n"  # f-strings can't contain \n until Python 3.12
        result = f"height={self.height}; len(lines)={len(self.lines)}"
        if self.entry > len(self.lines):
            result += f"; entry outside diagram: entry={self.entry}"
        if self.exit > len(self.lines):
            result += f"; exit outside diagram: exit={self.exit}"
        for y in range(0, max(len(self.lines), self.entry + 1, self.exit + 1)):
            result = result + f"{nl}[{y:03}]"
            if y < len(self.lines):
                result = result + f" '{self.lines[y]}' len={len(self.lines[y])}"
            if y == self.entry and y == self.exit:
                result += " <- entry, exit"
            elif y == self.entry:
                result += " <- entry"
            elif y == self.exit:
                result += " <- exit"
        if show:
            print(result)
        else:
            return result

    @classmethod
    def _enclose_lines(
        cls, lines: List[str], lefts: List[str], rights: List[str]
    ) -> List[str]:
        """
        Join the lefts, lines, and rights arrays together, line-by-line, and return the result.
        """
        assert len(lines) == len(lefts), "All arguments must be the same length"
        assert len(lines) == len(rights), "All arguments must be the same length"
        newLines = []
        for i in range(0, len(lines)):
            newLines.append(lefts[i] + lines[i] + rights[i])
        return newLines

    @staticmethod
    def _gaps(
        outer_width: int, inner_width: int, internal_alignment: str
    ) -> Tuple[int, int]:
        """
        Return the left and right pad spacing based on the alignment configuration setting.
        """
        diff = outer_width - inner_width
        if internal_alignment == "left":
            return 0, diff
        elif internal_alignment == "right":
            return diff, 0
        else:
            left = diff // 2
            right = diff - left
            return left, right

    @classmethod
    def _get_parts(cls, part_names: List[str]) -> List[str]:
        """
        Return a list of text diagram drawing characters for the specified character names.
        """
        return [cls.parts[name] for name in part_names]

    @staticmethod
    def _max_width(*args: Union[int, str, List[str], TextDiagram]) -> int:
        """
        Return the maximum width of all of the arguments.
        """
        max_width = 0
        for arg in args:
            if isinstance(arg, TextDiagram):
                width = arg.width
            elif isinstance(arg, list):
                width = max([len(e) for e in arg])
            elif isinstance(arg, int):
                width = len(str(arg))
            else:
                width = len(arg)
            max_width = width if width > max_width else max_width
        return max_width

    @staticmethod
    def _padL(string: str, width: int, pad: str) -> str:
        """
        Pad the specified string on the left to the specified width with the specified pad string and return the result.
        """
        assert (width - len(string)) % len(
            pad
        ) == 0, f"Gap {width - len(string)} must be a multiple of pad string '{pad}'"
        return (pad * ((width - len(string) // len(pad)))) + string

    @staticmethod
    def _padR(string: str, width: int, pad: str) -> str:
        """
        Pad the specified string on the right to the specified width with the specified pad string and return the result.
        """
        assert (width - len(string)) % len(
            pad
        ) == 0, f"Gap {width - len(string)} must be a multiple of pad string '{pad}'"
        return string + (pad * ((width - len(string) // len(pad))))

    @classmethod
    def _rectish(cls, rect_type: str, data: TextDiagram, dashed=False) -> TextDiagram:
        """
        Create and return a new TextDiagram for a rectangular box surrounding the specified TextDiagram, using the
        specified set of drawing characters (i.e., "rect" or "round_rect"), and possibly using dashed lines.
        """
        line_type = "_dashed" if dashed else ""
        (
            top_left,
            ctr_left,
            bot_left,
            top_right,
            ctr_right,
            bot_right,
            top_horiz,
            bot_horiz,
            line,
            cross,
        ) = cls._get_parts(
            [
                f"{rect_type}_top_left",
                f"{rect_type}_left{line_type}",
                f"{rect_type}_bot_left",
                f"{rect_type}_top_right",
                f"{rect_type}_right{line_type}",
                f"{rect_type}_bot_right",
                f"{rect_type}_top{line_type}",
                f"{rect_type}_bot{line_type}",
                "line",
                "cross",
            ]
        )
        if rect_type == "angle_rect":
            top_left = " " + top_left
            ctr_left = ctr_left + " "
            bot_left = " " + bot_left
            top_right = top_right + " "
            ctr_right = " " + ctr_right
            bot_right = bot_right + " "
        item_was_formatted = isinstance(data, TextDiagram)
        if item_was_formatted:
            item_td = data
        else:
            item_td = TextDiagram(0, 0, [data])
        # Create the rectangle and enclose the item in it.
        lines = []
        lines += [top_horiz * (item_td.width + 2)]
        if item_was_formatted:
            lines += item_td.expand(1, 1, 0, 0).lines
        else:
            for i in range(0, len(item_td.lines)):
                lines += [" " + item_td.lines[i] + " "]
        lines += [bot_horiz * (item_td.width + 2)]
        entry = item_td.entry + 1
        exit = item_td.exit + 1
        left_max_width = cls._max_width(top_left, ctr_left, bot_left)
        lefts = [cls._padR(ctr_left, left_max_width, " ")] * len(lines)
        lefts[0] = cls._padR(top_left, left_max_width, top_horiz)
        lefts[-1] = cls._padR(bot_left, left_max_width, bot_horiz)
        if item_was_formatted:
            lefts[entry] = cross
        right_max_width = cls._max_width(top_right, ctr_right, bot_right)
        rights = [cls._padL(ctr_right, right_max_width, " ")] * len(lines)
        rights[0] = cls._padL(top_right, right_max_width, top_horiz)
        rights[-1] = cls._padL(bot_right, right_max_width, bot_horiz)
        if item_was_formatted:
            rights[exit] = cross
        # Build the entry and exit perimeter.
        lines = TextDiagram._enclose_lines(lines, lefts, rights)
        lefts = [" "] * len(lines)
        lefts[entry] = line
        rights = [" "] * len(lines)
        rights[exit] = line
        lines = TextDiagram._enclose_lines(lines, lefts, rights)
        return cls(entry, exit, lines)

    def __repr__(self) -> str:
        return f"TextDiagram({self.entry}, {self.exit}, {self.lines})"

    # Note:  All the drawing sequences below MUST be single characters.  setFormatting() checks this.

    # Unicode 25xx box drawing characters, plus a few others.
    PARTS_UNICODE = {
        "cross_diag": "\u2573",
        "corner_bot_left": "\u2514",
        "corner_bot_right": "\u2518",
        "corner_top_left": "\u250c",
        "corner_top_right": "\u2510",
        "cross": "\u253c",
        "left": "\u2502",
        "line": "\u2500",
        "line_vertical": "\u2502",
        "multi_repeat": "\u21ba",
        "rect_bot": "\u2500",
        "rect_bot_dashed": "\u2504",
        "rect_bot_left": "\u2514",
        "rect_bot_right": "\u2518",
        "rect_left": "\u2502",
        "rect_left_dashed": "\u2506",
        "rect_right": "\u2502",
        "rect_right_dashed": "\u2506",
        "rect_top": "\u2500",
        "rect_top_dashed": "\u2504",
        "rect_top_left": "\u250c",
        "rect_top_right": "\u2510",
        "repeat_bot_left": "\u2570",
        "repeat_bot_right": "\u256f",
        "repeat_left": "\u2502",
        "repeat_right": "\u2502",
        "repeat_top_left": "\u256d",
        "repeat_top_right": "\u256e",
        "right": "\u2502",
        "round_corner_bot_left": "\u2570",
        "round_corner_bot_right": "\u256f",
        "round_corner_top_left": "\u256d",
        "round_corner_top_right": "\u256e",
        "round_rect_bot": "\u2500",
        "round_rect_bot_dashed": "\u2504",
        "round_rect_bot_left": "\u2570",
        "round_rect_bot_right": "\u256f",
        "round_rect_left": "\u2502",
        "round_rect_left_dashed": "\u2506",
        "round_rect_right": "\u2502",
        "round_rect_right_dashed": "\u2506",
        "round_rect_top": "\u2500",
        "round_rect_top_dashed": "\u2504",
        "round_rect_top_left": "\u256d",
        "round_rect_top_right": "\u256e",
        "angle_rect_bot": "\u2500",
        "angle_rect_bot_dashed": "\u2504",
        "angle_rect_bot_left": "\u25dd",
        "angle_rect_bot_right": "\u25dc",
        "angle_rect_left": "\u27e8",
        "angle_rect_left_dashed": "\u27e8",
        "angle_rect_right": "\u27e9",
        "angle_rect_right_dashed": "\u27e9",
        "angle_rect_top": "\u2500",
        "angle_rect_top_dashed": "\u2504",
        "angle_rect_top_left": "\u25de",
        "angle_rect_top_right": "\u25df",
        "separator": "\u2500",
        "tee_left": "\u2524",
        "tee_right": "\u251c",
        "arrow_right": "\u25ba",
        "arrow_left": "\u25c4",
        "ball": "\u25cf",
    }

    # Plain old ASCII characters.
    PARTS_ASCII = {
        "cross_diag": "X",
        "corner_bot_left": "\\",
        "corner_bot_right": "/",
        "corner_top_left": "/",
        "corner_top_right": "\\",
        "cross": "+",
        "left": "|",
        "line": "-",
        "line_vertical": "|",
        "multi_repeat": "&",
        "rect_bot": "-",
        "rect_bot_dashed": "-",
        "rect_bot_left": "+",
        "rect_bot_right": "+",
        "rect_left": "|",
        "rect_left_dashed": "|",
        "rect_right": "|",
        "rect_right_dashed": "|",
        "rect_top_dashed": "-",
        "rect_top": "-",
        "rect_top_left": "+",
        "rect_top_right": "+",
        "repeat_bot_left": "\\",
        "repeat_bot_right": "/",
        "repeat_left": "|",
        "repeat_right": "|",
        "repeat_top_left": "/",
        "repeat_top_right": "\\",
        "right": "|",
        "round_corner_bot_left": "\\",
        "round_corner_bot_right": "/",
        "round_corner_top_left": "/",
        "round_corner_top_right": "\\",
        "round_rect_bot": "-",
        "round_rect_bot_dashed": "-",
        "round_rect_bot_left": "\\",
        "round_rect_bot_right": "/",
        "round_rect_left": "|",
        "round_rect_left_dashed": "|",
        "round_rect_right": "|",
        "round_rect_right_dashed": "|",
        "round_rect_top": "-",
        "round_rect_top_dashed": "-",
        "round_rect_top_left": "/",
        "round_rect_top_right": "\\",
        "angle_rect_bot": "-",
        "angle_rect_bot_dashed": "-",
        "angle_rect_bot_left": "\\",
        "angle_rect_bot_right": "/",
        "angle_rect_left": "<",
        "angle_rect_left_dashed": "|",
        "angle_rect_right": ">",
        "angle_rect_right_dashed": "|",
        "angle_rect_top": "-",
        "angle_rect_top_dashed": "-",
        "angle_rect_top_left": "/",
        "angle_rect_top_right": "\\",
        "separator": "-",
        "tee_left": "|",
        "tee_right": "|",
        "arrow_right": ">",
        "arrow_left": "<",
        "ball": "o",
    }
