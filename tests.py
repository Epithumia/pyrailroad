import os
import errno
import unittest
import pytest


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


class UnitTests(BaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_terminal(self):
        from pyrailroad.railroad import Terminal, Diagram

        with pytest.raises(TypeError):
            Terminal()
        t = Terminal("text")
        assert t.to_dict() == {
            "element": "Terminal",
            "text": "text",
            "href": None,
            "title": None,
            "cls": "",
        }
        t = Terminal("text", "href")
        assert t.to_dict() == {
            "element": "Terminal",
            "text": "text",
            "href": "href",
            "title": None,
            "cls": "",
        }
        t = Terminal("text", "href", "title")
        assert t.to_dict() == {
            "element": "Terminal",
            "text": "text",
            "href": "href",
            "title": "title",
            "cls": "",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/terminal.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/terminal_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_non_terminal(self):
        from pyrailroad.railroad import NonTerminal, Diagram

        with pytest.raises(TypeError):
            NonTerminal()
        t = NonTerminal("text")
        assert t.to_dict() == {
            "element": "NonTerminal",
            "text": "text",
            "href": None,
            "title": None,
            "cls": "",
        }
        t = NonTerminal("text", "href")
        assert t.to_dict() == {
            "element": "NonTerminal",
            "text": "text",
            "href": "href",
            "title": None,
            "cls": "",
        }
        t = NonTerminal("text", "href", "title")
        assert t.to_dict() == {
            "element": "NonTerminal",
            "text": "text",
            "href": "href",
            "title": "title",
            "cls": "",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/non_terminal.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/non_terminal_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_comment(self):
        from pyrailroad.railroad import Comment, Diagram

        with pytest.raises(TypeError):
            Comment()
        t = Comment("text")
        assert t.to_dict() == {
            "element": "Comment",
            "text": "text",
            "href": None,
            "title": None,
            "cls": "",
        }
        t = Comment("text", "href")
        assert t.to_dict() == {
            "element": "Comment",
            "text": "text",
            "href": "href",
            "title": None,
            "cls": "",
        }
        t = Comment("text", "href", "title")
        assert t.to_dict() == {
            "element": "Comment",
            "text": "text",
            "href": "href",
            "title": "title",
            "cls": "",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/comment.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/comment_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_skip(self):
        from pyrailroad.railroad import Skip, Diagram

        t = Skip()
        assert t.to_dict() == {"element": "Skip"}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/skip.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/skip_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_sequence(self):
        from pyrailroad.railroad import Terminal, Sequence, Diagram

        t = Sequence(Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "element": "Sequence",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/sequence.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/sequence_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_stack(self):
        from pyrailroad.railroad import Terminal, Diagram, Stack

        t = Stack(Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "element": "Stack",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/stack.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/stack_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_optional_sequence(self):
        from pyrailroad.railroad import Terminal, OptionalSequence, Diagram

        t = OptionalSequence(Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "element": "OptionalSequence",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/optional_sequence.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/optional_sequence_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_alternating_sequence(self):
        from pyrailroad.railroad import Terminal, AlternatingSequence, Diagram

        t = AlternatingSequence(Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "element": "AlternatingSequence",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/alternating_sequence.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/alternating_sequence_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_choice(self):
        from pyrailroad.railroad import Terminal, Choice, Diagram

        with pytest.raises(TypeError):
            Choice(Terminal("term1"), Terminal("term2"))
        t = Choice(0, Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "default": 0,
            "element": "Choice",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/choice0.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/choice0_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        t = Choice(1, Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "default": 1,
            "element": "Choice",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/choice1.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/choice1_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_multiple_choice(self):
        from pyrailroad.railroad import Terminal, MultipleChoice, Diagram

        with pytest.raises(TypeError):
            MultipleChoice()
        with pytest.raises(TypeError):
            MultipleChoice(Terminal("term1"))
        with pytest.raises(TypeError):
            MultipleChoice(Terminal("term1"), Terminal("term2"))
        t = MultipleChoice(0, "all", Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "default": 0,
            "element": "MultipleChoice",
            "type": "all",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/multiple_choice0_all.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/multiple_choice0_all_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        t = MultipleChoice(1, "all", Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "default": 1,
            "element": "MultipleChoice",
            "type": "all",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/multiple_choice1_all.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/multiple_choice1_all_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        t = MultipleChoice(0, "any", Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "default": 0,
            "element": "MultipleChoice",
            "type": "any",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/multiple_choice0_any.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/multiple_choice0_any_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        t = MultipleChoice(1, "any", Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "default": 1,
            "element": "MultipleChoice",
            "type": "any",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/multiple_choice1_any.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/multiple_choice1_any_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_horizontal_choice(self):
        from pyrailroad.railroad import Terminal, HorizontalChoice, Diagram

        with pytest.raises(IndexError):
            HorizontalChoice()

        t = HorizontalChoice(Terminal("term1"))
        assert t.to_dict() == {
            "element": "Sequence",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                }
            ],
        }

        t = HorizontalChoice(Terminal("term1"), Terminal("term2"))
        assert t.to_dict() == {
            "element": "HorizontalChoice",
            "items": [
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term1",
                    "title": None,
                },
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term2",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/horizontal_choice.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/horizontal_choice_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_optional(self):
        from pyrailroad.railroad import Terminal, optional, Diagram

        t = optional(Terminal("term"))
        assert t.to_dict() == {
            "default": 1,
            "element": "Choice",
            "items": [
                {"element": "Skip"},
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/optional_no_skip.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/optional_no_skip_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = optional(Terminal("term"), True)
        assert t.to_dict() == {
            "default": 0,
            "element": "Choice",
            "items": [
                {"element": "Skip"},
                {
                    "cls": "",
                    "element": "Terminal",
                    "href": None,
                    "text": "term",
                    "title": None,
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/optional_skip.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/optional_skip_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_one_or_more(self):
        from pyrailroad.railroad import Diagram, OneOrMore, Terminal

        with pytest.raises(TypeError):
            OneOrMore()

        t = OneOrMore(Terminal("term"))
        assert t.to_dict() == {
            "element": "OneOrMore",
            "item": {
                "cls": "",
                "element": "Terminal",
                "href": None,
                "text": "term",
                "title": None,
            },
            "repeat": {"element": "Skip"},
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/one_or_more_skip.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/one_or_more_skip_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = OneOrMore(Terminal("term"), Terminal("repeat"))
        assert t.to_dict() == {
            "element": "OneOrMore",
            "item": {
                "cls": "",
                "element": "Terminal",
                "href": None,
                "text": "term",
                "title": None,
            },
            "repeat": {
                "cls": "",
                "element": "Terminal",
                "href": None,
                "text": "repeat",
                "title": None,
            },
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/one_or_more_repeat.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/one_or_more_repeat_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_zero_or_more(self):
        from pyrailroad.railroad import Diagram, zero_or_more, Terminal

        with pytest.raises(TypeError):
            zero_or_more()  # NOSONAR

        t = zero_or_more(Terminal("term"))
        assert t.to_dict() == {
            "element": "Choice",
            "default": 1,
            "items": [
                {"element": "Skip"},
                {
                    "element": "OneOrMore",
                    "item": {
                        "element": "Terminal",
                        "text": "term",
                        "href": None,
                        "title": None,
                        "cls": "",
                    },
                    "repeat": {"element": "Skip"},
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/zero_or_more_skip1.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/zero_or_more_skip1_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = zero_or_more(Terminal("term"), skip=True)
        assert t.to_dict() == {
            "element": "Choice",
            "default": 0,
            "items": [
                {"element": "Skip"},
                {
                    "element": "OneOrMore",
                    "item": {
                        "element": "Terminal",
                        "text": "term",
                        "href": None,
                        "title": None,
                        "cls": "",
                    },
                    "repeat": {"element": "Skip"},
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/zero_or_more_skip0.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/zero_or_more_skip0_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = zero_or_more(Terminal("term"), Terminal("repeat"))
        assert t.to_dict() == {
            "element": "Choice",
            "default": 1,
            "items": [
                {"element": "Skip"},
                {
                    "element": "OneOrMore",
                    "item": {
                        "element": "Terminal",
                        "text": "term",
                        "href": None,
                        "title": None,
                        "cls": "",
                    },
                    "repeat": {
                        "element": "Terminal",
                        "text": "repeat",
                        "href": None,
                        "title": None,
                        "cls": "",
                    },
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/zero_or_more_repeat1.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/zero_or_more_repeat1_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = zero_or_more(Terminal("term"), Terminal("repeat"), skip=True)
        assert t.to_dict() == {
            "element": "Choice",
            "default": 0,
            "items": [
                {"element": "Skip"},
                {
                    "element": "OneOrMore",
                    "item": {
                        "element": "Terminal",
                        "text": "term",
                        "href": None,
                        "title": None,
                        "cls": "",
                    },
                    "repeat": {
                        "element": "Terminal",
                        "text": "repeat",
                        "href": None,
                        "title": None,
                        "cls": "",
                    },
                },
            ],
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/zero_or_more_repeat0.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/zero_or_more_repeat0_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_group(self):
        from pyrailroad.railroad import Diagram, Group, Terminal

        with pytest.raises(TypeError):
            Group()

        t = Group(Terminal("term"))
        assert t.to_dict() == {
            "element": "Group",
            "item": {
                "element": "Terminal",
                "text": "term",
                "href": None,
                "title": None,
                "cls": "",
            },
            "label": None,
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/group_no_label.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/group_no_label_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = Group(Terminal("term"), "label")
        assert t.to_dict() == {
            "element": "Group",
            "item": {
                "element": "Terminal",
                "text": "term",
                "href": None,
                "title": None,
                "cls": "",
            },
            "label": {
                "element": "Comment",
                "text": "label",
                "href": None,
                "title": None,
                "cls": "",
            },
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/group_label.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/group_label_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_start(self):
        from pyrailroad.railroad import Start, Diagram

        t = Start()
        assert t.to_dict() == {"element": "Start", "type": "simple", "label": None}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/start_simple.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/start_simple_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = Start(label="label")
        assert t.to_dict() == {"element": "Start", "type": "simple", "label": "label"}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/start_label.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/start_label_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = Start("complex")
        assert t.to_dict() == {"element": "Start", "type": "complex", "label": None}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/start_complex.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/start_complex_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = Start("sql")
        assert t.to_dict() == {"element": "Start", "type": "sql", "label": None}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/start_sql.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/start_sql_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

    def test_end(self):
        from pyrailroad.railroad import End, Diagram

        t = End()
        assert t.to_dict() == {
            "element": "End",
            "type": "simple",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/end_simple.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/end_simple_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = End("complex")
        assert t.to_dict() == {
            "element": "End",
            "type": "complex",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/end_complex.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/end_complex_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result

        t = End("sql")
        assert t.to_dict() == {
            "element": "End",
            "type": "sql",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/end_sql.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/end_sql_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result


class CLITests(BaseTest):
    def setUp(self):
        super().setUp()
        from typer.testing import CliRunner

        self.runner = CliRunner()

    def tearDown(self):
        silent_remove("tests/cli/output.svg")
        super().tearDown()

    def test_cli_help(self):
        from pyrailroad.parser import app

        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "dsl" in result.stdout
        assert "json" in result.stdout
        assert "yaml" in result.stdout
        result = self.runner.invoke(app, ["dsl", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        result = self.runner.invoke(app, ["json", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        assert "properties" in result.stdout
        result = self.runner.invoke(app, ["yaml", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        assert "properties" in result.stdout

    def test_cli_dsl(self):
        from pyrailroad.parser import app

        in_file = "tests/cli/diagram.dsl"
        out_file = "tests/cli/output.svg"
        result = self.runner.invoke(app, ["dsl", in_file, out_file])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(app, ["dsl", in_file, out_file, "--standalone"])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["dsl", in_file, out_file, "--standalone", "--simple"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_simple.svg", "r") as base:
                assert res.read() == base.read()

    def test_cli_json(self):
        from pyrailroad.parser import app

        in_file = "tests/cli/diagram.json"
        out_file = "tests/cli/output.svg"
        result = self.runner.invoke(app, ["json", in_file, out_file])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["json", in_file, out_file, "tests/cli/complex_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["json", in_file, out_file, "tests/cli/simple_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_simple.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["json", in_file, out_file, "tests/cli/customized_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_custom.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["yaml", in_file, out_file, "tests/cli/sql_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_sql_standalone.svg", "r") as base:
                assert res.read() == base.read()

    def test_cli_yaml(self):
        from pyrailroad.parser import app

        in_file = "tests/cli/diagram.yaml"
        out_file = "tests/cli/output.svg"
        result = self.runner.invoke(app, ["yaml", in_file, out_file])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["yaml", in_file, out_file, "tests/cli/complex_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["yaml", in_file, out_file, "tests/cli/simple_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_simple.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["yaml", in_file, out_file, "tests/cli/customized_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_custom.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            app, ["yaml", in_file, out_file, "tests/cli/sql_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_sql_standalone.svg", "r") as base:
                assert res.read() == base.read()
