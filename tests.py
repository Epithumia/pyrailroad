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


def silent_remove_dir(path):
    try:
        dirpath, _, filenames = list(os.walk(path))[0]
        for file in filenames:
            silent_remove(os.path.join(dirpath, file))
        os.rmdir(path)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred
    except IndexError:
        pass


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
        from pyrailroad.elements import Terminal, Diagram

        with pytest.raises(TypeError):
            Terminal()  # type: ignore
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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/terminal_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_non_terminal(self):
        from pyrailroad.elements import NonTerminal, Diagram

        with pytest.raises(TypeError):
            NonTerminal()  # type: ignore
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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/non_terminal_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_comment(self):
        from pyrailroad.elements import Comment, Diagram

        with pytest.raises(TypeError):
            Comment()  # type: ignore
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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/comment_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_arrow(self):
        from pyrailroad.elements import Arrow, Diagram

        t = Arrow()
        assert t.to_dict() == {"element": "Arrow", "direction": "right"}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/arrow_right.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/arrow_right_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/arrow_right_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

        t = Arrow("left")
        assert t.to_dict() == {"element": "Arrow", "direction": "left"}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/arrow_left.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/arrow_left_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/arrow_left_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

        t = Arrow("undirected")
        assert t.to_dict() == {"element": "Arrow", "direction": "undirected"}
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/arrow_undirected.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/arrow_undirected_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/arrow_undirected_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_expression(self):
        from pyrailroad.elements import Expression, Diagram

        with pytest.raises(TypeError):
            Expression()  # type: ignore
        t = Expression("text")
        assert t.to_dict() == {
            "element": "Expression",
            "text": "text",
            "href": None,
            "title": None,
            "cls": "",
        }
        t = Expression("text", "href")
        assert t.to_dict() == {
            "element": "Expression",
            "text": "text",
            "href": "href",
            "title": None,
            "cls": "",
        }
        t = Expression("text", "href", "title")
        assert t.to_dict() == {
            "element": "Expression",
            "text": "text",
            "href": "href",
            "title": "title",
            "cls": "",
        }
        d = Diagram(t)
        svg = []
        d.write_svg(svg.append)
        with open("tests/expression.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        svg = []
        d.write_standalone(svg.append)
        with open("tests/expression_standalone.svg", "r") as f:
            svg_result = f.read()
        assert " ".join(svg) == svg_result
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/expression_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_skip(self):
        from pyrailroad.elements import Skip, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/skip_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_sequence(self):
        from pyrailroad.elements import Terminal, Sequence, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/sequence_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_stack(self):
        from pyrailroad.elements import Terminal, Diagram, Stack

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/stack_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_optional_sequence(self):
        from pyrailroad.elements import Terminal, OptionalSequence, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/optional_sequence_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_alternating_sequence(self):
        from pyrailroad.elements import Terminal, AlternatingSequence, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/alternating_sequence_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_choice(self):
        from pyrailroad.elements import Terminal, Choice, Diagram

        with pytest.raises(TypeError):
            Choice(Terminal("term1"), Terminal("term2"))  # type: ignore
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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/choice0_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/choice1_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_multiple_choice(self):
        from pyrailroad.elements import Terminal, MultipleChoice, Diagram

        with pytest.raises(TypeError):
            MultipleChoice()  # type: ignore
        with pytest.raises(TypeError):
            MultipleChoice(Terminal("term1"))  # type: ignore
        with pytest.raises(TypeError):
            MultipleChoice(Terminal("term1"), Terminal("term2"))  # type: ignore
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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/multiple_choice0_all_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result
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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/multiple_choice1_all_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/multiple_choice0_any_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/multiple_choice1_any_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_horizontal_choice(self):
        from pyrailroad.elements import Terminal, HorizontalChoice, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/horizontal_choice_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_optional(self):
        from pyrailroad.elements import Terminal, optional, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/optional_no_skip_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/optional_skip_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_one_or_more(self):
        from pyrailroad.elements import Diagram, OneOrMore, Terminal

        with pytest.raises(TypeError):
            OneOrMore()  # type: ignore

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/one_or_more_skip_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/one_or_more_repeat_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_zero_or_more(self):
        from pyrailroad.elements import Diagram, zero_or_more, Terminal

        with pytest.raises(TypeError):
            zero_or_more()  # type: ignore

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/zero_or_more_skip1_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/zero_or_more_skip0_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/zero_or_more_repeat1_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/zero_or_more_repeat0_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_group(self):
        from pyrailroad.elements import Diagram, Group, Terminal

        with pytest.raises(TypeError):
            Group()  # type: ignore

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/group_no_label_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/group_label_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_start(self):
        from pyrailroad.elements import Start, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/start_simple_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/start_label_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/start_complex_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/start_sql_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

    def test_end(self):
        from pyrailroad.elements import End, Diagram

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/end_simple_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/end_complex_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result

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
        text = []
        d.write_text(text.append)
        text = "".join(text)
        with open("tests/end_sql_text.txt", "r") as f:
            text_result = f.read()
        assert text == text_result


class JSONParserTests(BaseTest):
    def test_parse_json(self):
        from pyrailroad.parser import parse_json
        from pyrailroad.elements import Diagram

        input_string = """{
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
}"""
        r = parse_json(
            input_string, {"standalone": False, "type": "complex", "css": None}
        )
        assert isinstance(r, Diagram)

    def test_missing_element_json(self):
        from pyrailroad.parser import parse_json
        from pyrailroad.exceptions import ParseException

        input_string = """{
    "error": "Choice",
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
}"""
        with pytest.raises(ParseException) as e:
            parse_json(
                input_string, {"standalone": False, "type": "complex", "css": None}
            )
        assert e.value.msg == "Invalid input file : 'element' is missing from the root."

    def test_choice_error_json(self):
        from pyrailroad.parser import parse_json
        from pyrailroad.exceptions import ParseException

        input_string = """{
    "element": "Choice",
    "default": null,
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
}"""
        with pytest.raises(ParseException) as e:
            parse_json(
                input_string, {"standalone": False, "type": "complex", "css": None}
            )
        assert e.value.msg == 'Attribute "default" must be an integer, got: None.'

    def test_unknown_element_json(self):
        from pyrailroad.parser import parse_json
        from pyrailroad.exceptions import ParseException

        input_string = """{
    "element": "Chance",
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
}"""
        with pytest.raises(ParseException) as e:
            parse_json(
                input_string, {"standalone": False, "type": "complex", "css": None}
            )
        assert e.value.msg == "Unknown element: Chance."


class DSLExceptionTests(BaseTest):
    def test_general_parsing_errors(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        unknown_element = "Terminally: foo"
        with pytest.raises(ParseException) as e:
            parse(unknown_element, True)
        assert (
            e.value.msg
            == "Line 1 doesn't contain a valid railroad-diagram command. Got:\nTerminally: foo"
        )

        bad_indent = "    Choice: 0\n  Terminal: foo\n  Terminal: bar"
        with pytest.raises(ParseException) as e:
            parse(bad_indent, True)
        assert (
            e.value.msg
            == "Inconsistent indentation: line 1 is indented less than the first line."
        )

        bad_block_grammar = "Sequence foo:\n  Terminal: bar\n  Terminal: bar"
        with pytest.raises(ParseException) as e:
            parse(bad_block_grammar, True)
        assert (
            e.value.msg
            == "Line 1 doesn't match the grammar 'Command: optional-prelude'. Got:\nSequence foo:"
        )

        bad_multiple_choice_grammar = "MultipleChoice foo: bar"
        with pytest.raises(ParseException) as e:
            parse(bad_multiple_choice_grammar, True)
        assert (
            e.value.msg
            == "Line 1 doesn't match the grammar 'MultipleChoice: optional-prelude'. Got:\nMultipleChoice foo: bar"
        )

        bad_indents = "Sequence:\n\tTerminal: foo\n\tTerminal: bar\nSequence:\n\t\tTerminal: foo\n\t\tTerminal: bar"
        with pytest.raises(ParseException) as e:
            parse(bad_indents, True)
        assert (
            e.value.msg
            == "Line 5 jumps more than 1 indent level from the previous line:\nTerminal: foo"
        )

    def test_terminal_parsing_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Terminal:\n  Terminal: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Terminal commands cannot have children."

    def test_non_terminal_parsing_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "NonTerminal:\n  Terminal: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - NonTerminal commands cannot have children."

    def test_comment_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Comment:\n  Terminal: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Comment commands cannot have children."

    def test_skip_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Skip:\n  Terminal: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Skip commands cannot have children."

        element = "Skip: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Skip commands cannot have text."

    def test_sequence_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Sequence: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Sequence commands cannot have preludes."

        element = "Sequence:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Sequence commands need at least one child."

    def test_stack_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Stack: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Stack commands cannot have preludes."

        element = "Stack:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Stack commands need at least one child."

    def test_horizontal_choice_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "HorizontalChoice: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - HorizontalChoice commands cannot have preludes."

        element = "HorizontalChoice:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg == "Line 1 - HorizontalChoice commands need at least one child."
        )

    def test_optional_sequence_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "OptionalSequence: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - OptionalSequence commands cannot have preludes."

        element = "OptionalSequence:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg == "Line 1 - OptionalSequence commands need at least one child."
        )

    def test_alternating_sequence_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "AlternatingSequence: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg == "Line 1 - AlternatingSequence commands cannot have preludes."
        )

        element = "AlternatingSequence:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg
            == "Line 1 - AlternatingSequence commands need exactly two children."
        )

    def test_one_or_more_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "OneOrMore: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - OneOrMore commands cannot have preludes."

        element = "OneOrMore:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg == "Line 1 - OneOrMore commands must have one or two children."
        )

    def test_zero_or_more_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "ZeroOrMore: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg
            == "Line 1 - ZeroOrMore preludes must be nothing or 'skip'. Got:\nfoo"
        )

        element = "ZeroOrMore:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg == "Line 1 - ZeroOrMore commands must have one or two children."
        )

    def test_group_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Group:\n\tTerminal: foo\n\tTerminal: bar"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Group commands need exactly one child."

    def test_optional_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Optional: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg
            == "Line 1 - Optional preludes must be nothing or 'skip'. Got:\nfoo"
        )

        element = "Optional:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Optional commands need exactly one child."

    def test_choice_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "Choice: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Choice preludes must be an integer. Got:\nfoo"

        element = "Choice:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - Choice commands need at least one child."

    def test_multiple_choice_error(self):
        from pyrailroad.parser import parse
        from pyrailroad.exceptions import ParseException

        element = "MultipleChoice: foo"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert e.value.msg == "Line 1 - MultipleChoice type must be any or all."

        element = "MultipleChoice:"
        with pytest.raises(ParseException) as e:
            parse(element, True)
        assert (
            e.value.msg == "Line 1 - MultipleChoice commands need at least one child."
        )


class CLITests(BaseTest):
    def setUp(self):
        super().setUp()
        from typer.testing import CliRunner

        self.runner = CliRunner()

    def tearDown(self):
        silent_remove("tests/cli/output.svg")
        silent_remove_dir("tests/cli/ebnf/output")
        super().tearDown()

    def test_cli_help(self):
        from pyrailroad.cli import cli

        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "dsl" in result.stdout
        assert "json" in result.stdout
        assert "yaml" in result.stdout
        assert "ebnf" in result.stdout
        result = self.runner.invoke(cli, ["dsl", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        result = self.runner.invoke(cli, ["json", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        assert "parameters" in result.stdout
        result = self.runner.invoke(cli, ["yaml", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        assert "parameters" in result.stdout
        result = self.runner.invoke(cli, ["ebnf", "--help"])
        assert result.exit_code == 0
        assert "file" in result.stdout
        assert "target" in result.stdout
        assert "parameters" in result.stdout
        assert "JSON" in result.stdout

    def test_cli_dsl(self):
        from pyrailroad.cli import cli

        in_file = "tests/cli/diagram.dsl"
        out_file = "tests/cli/output.svg"
        result = self.runner.invoke(cli, ["dsl", in_file, out_file])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(cli, ["dsl", in_file, out_file, "--standalone"])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["dsl", in_file, out_file, "--standalone", "--simple"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_simple.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["dsl", in_file, out_file, "--text", "--simple"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text_simple.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(cli, ["dsl", in_file, out_file, "--text"])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text.txt", "r") as base:
                assert res.read() == base.read()

    def test_cli_json(self):
        from pyrailroad.cli import cli

        in_file = "tests/cli/diagram.json"
        out_file = "tests/cli/output.svg"
        result = self.runner.invoke(cli, ["json", in_file, out_file])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["json", in_file, out_file, "tests/cli/complex_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["json", in_file, out_file, "tests/cli/simple_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_simple.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["json", in_file, out_file, "tests/cli/customized_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_custom.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/sql_standalone.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_sql_standalone.svg", "r") as base:
                assert res.read() == base.read()

        # Text mode
        result = self.runner.invoke(
            cli, ["json", in_file, out_file, "tests/cli/complex_text.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["json", in_file, out_file, "tests/cli/simple_text.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text_simple.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["json", in_file, out_file, "tests/cli/customized_text.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text_custom.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/sql_text.json"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_sql_text.txt", "r") as base:
                assert res.read() == base.read()

    def test_cli_yaml(self):
        from pyrailroad.cli import cli

        in_file = "tests/cli/diagram.yaml"
        out_file = "tests/cli/output.svg"
        result = self.runner.invoke(cli, ["yaml", in_file, out_file])
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/complex_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/simple_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_simple.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/customized_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_standalone_custom.svg", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/sql_standalone.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_sql_standalone.svg", "r") as base:
                assert res.read() == base.read()

        # Text output
        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/complex_text.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/simple_text.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text_simple.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/customized_text.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_text_custom.txt", "r") as base:
                assert res.read() == base.read()

        result = self.runner.invoke(
            cli, ["yaml", in_file, out_file, "tests/cli/sql_text.yaml"]
        )
        assert result.exit_code == 0
        with open(out_file, "r") as res:
            with open("tests/cli/diagram_sql_text.txt", "r") as base:
                assert res.read() == base.read()

    def test_cli_ebnf(self):
        from pyrailroad.cli import cli

        in_file = "tests/cli/ebnf/error.ebnf"
        out_dir = "tests/cli/ebnf/output"

        result = self.runner.invoke(cli, ["ebnf", in_file, out_dir])

        assert result.exit_code == 1

        in_file = "tests/cli/ebnf/w3c_blindfold_grammar.ebnf"
        out_dir = "tests/cli/ebnf/output"

        result = self.runner.invoke(cli, ["ebnf", in_file, out_dir])

        assert result.exit_code == 0

        result = self.runner.invoke(cli, ["ebnf", in_file, out_dir, "--to-json"])

        assert result.exit_code == 0

        in_file = "tests/cli/ebnf/xml_grammar.ebnf"
        out_dir = "tests/cli/ebnf/output"

        result = self.runner.invoke(cli, ["ebnf", in_file, out_dir])

        assert result.exit_code == 0

        w3c_dir = "tests/cli/ebnf/w3c_blindfold/"
        xml_dir = "tests/cli/ebnf/xml_grammar/"

        dirpath, _, filenames = list(os.walk(w3c_dir))[0]
        for filename in filenames:
            file_ = os.path.join(dirpath, filename)
            with open(file_, "r") as f:
                expected = f.read()
            with open(os.path.join(out_dir, filename), "r") as f:
                actual = f.read()
            assert expected == actual

        dirpath, _, filenames = list(os.walk(xml_dir))[0]
        for filename in filenames:
            file_ = os.path.join(dirpath, filename)
            with open(file_, "r") as f:
                expected = f.read()
            with open(os.path.join(out_dir, filename), "r") as f:
                actual = f.read()
            assert expected == actual
