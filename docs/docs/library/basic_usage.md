<!-- markdownlint-disable MD007 MD031 -->
# Using pyrailroad as a library

## Building a diagram

If you are familiar with [tabatkins' railroad-diagrams](https://github.com/tabatkins/railroad-diagrams), building a diagram should be a straightforward task, with a few differences for two elements (Optional and ZeroOrMore).

A really simple diagram would be:
```python
from pyrailroad.elements import Diagram, Terminal
d = Diagram(Terminal("foo"))
```

To write it out as SVG, do:
```python
# Write an SVG file without stylesheet
with open('foo.svg', 'w') as f:
    d.write_svg(f.write)
```
or
```python
# Write an SVG file with a CSS styleshzeet included
with open('foo.svg', 'w') as f:
    d.write_standalone(f.write)
```

To crate a text-format diagram instead, do:
```python
from sys import stdout
d.write_text(stdout.write)
```

## Summary of elements used in a diagram

### Base elements

#### Diagram

The constructor for `Diagram` takes any element, a dictionary of parameters (to override the diagram class) and an optional type.

By default, a `Diagram` will always include a [Start](#start) and an [End](#end) when printed even if they were omitted.

Examples

  * Text element

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram
    d = Diagram("foo")
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A Terminal again (explicitly called), with the *sql* type
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Terminal
    d = Diagram(Terminal("foo"), type="sql")
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Multiple diagram elements, with the *complex* type and a parameter override
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram
    d = Diagram("foo", "bar", parameters={'diagram_class': 'custom'},type="complex")
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Start

This is the element that starts a diagram at the top left, you'd usually only use one. The constructor for `Start` takes a type (same as [Diagram](#diagram)), an optional label and an optional dictionary of parameters to override `char_width`.

Examples

  * Simple
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Start
    d = Diagram(Start(label="foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Customized
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Start
    d = Diagram(Start(label="foo", parameters={"char_width": 25}, type="sql"))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### End

This is the opposite end of the diagram. The constructor is similar to [Start](#start) but doesn't have a label. You can pass a dictionary of parameters, but they have no effect on End (this is kept for practical coding reasons so that all elements can take the full parameters dictionary recursively and use only what they need).

Examples

  * Simple
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, End
    d = Diagram(End())
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Customized
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, End
    d = Diagram(End(type="sql"))
    d.write_svg(print)  # markdown-exec: hide
    ```

### Text elements

#### Terminal

In a grammar, a Terminal is a symbol that cannot be replaced by other symbols of the vocabulary. Typically, this will be keywords for your language/tool, or literals.

The constructor for `Terminal` takes a text, an optional href that will be converted to a link in SVG only, an optional title, a optional class for SVG styling and an optional dictionary of parameters to override `char_width`.

Examples

  * Simple
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Terminal
    d = Diagram(Terminal("foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Customized
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Terminal
    d = Diagram(Terminal("foo"), Terminal("bar", href="https://github.com", parameters={"char_width": 25}, title="This is a terminal with a link", cls="term"))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### NonTerminal

By opposition, a NonTerminal is a symbol that is replaceable (and likely defined in another diagram).

The constructor for `NonTerminal` takes a text, an optional href that will be converted to a link in SVG only, an optional title, a optional class for SVG styling and an optional dictionary of parameters to override `char_width`.

  * Simple
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, NonTerminal
    d = Diagram(NonTerminal("foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Customized
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, NonTerminal
    d = Diagram(NonTerminal("foo"), NonTerminal("bar", href="https://github.com", parameters={"char_width": 25}, title="This is a non-terminal with a link", cls="term"))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Comment

A comment is a neutral element that is best used to label branches in some of the block elements (repeat lines for example).

The constructor for `Comment` takes a text, an optional href that will be converted to a link in SVG only, an optional title, a optional class for SVG styling and an optional dictionary of parameters to override `comment_char_width`.

  * Simple
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Comment
    d = Diagram(Comment("foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Customized
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Comment
    d = Diagram(Comment("foo"), Comment("bar", href="https://github.com", parameters={"comment_char_width": 25}, title="This is a comment with a link", cls="term"))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Arrow

The arrow element is an addition in pyrailroad over railroad-diagram that lets you add an arrow to a line to help read a longer or more complex diagram.

The constructor for `Arrow` takes an optional direction (and like [End](#end), a parameters dictionary that has no effect).

Examples

  * Arrow to the right
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Arrow
    d = Diagram("going", Arrow(), "right")
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Arrow to the left
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Arrow
    d = Diagram("left", Arrow("left"), "going")
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Undirected (similar to a [Skip](#skip))
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Arrow
    d = Diagram("step on", Arrow("skip"), "no pets")
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Skip

This element lets you add spacing in your diagram by adding an empty line (in a[Stack](#stack), typically).

The constructor only takes an optional parameters dictionary.

Example

  * One Skip
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Stack, Skip
    d = Diagram(Stack("one", Skip(), "skip"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Three Skips
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Stack, Skip
    d = Diagram(Stack("three", Skip(), Skip(), Skip(), "skips"))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Expression

The expression element is an addition in pyrailroad over railroad-diagram. It was added to deal with EBNF grammars having ambiguities in their notations which means the parser has to guess for some elements and it can't decide how to represent it other than as an *expression*. The best example is when a grammar contains a *regular expression*.

The constructor for `Expression` takes a text, an optional href that will be converted to a link in SVG only, an optional title, a optional class for SVG styling and an optional dictionary of parameters to override `char_width`.

Examples

  * Simple
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Expression
    d = Diagram(Expression("foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * Customized
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Expression
    d = Diagram(Expression("foo"), Expression("bar", href="https://github.com", parameters={"char_width": 25}, title="This is an expression with a link", cls="term"))
    d.write_svg(print)  # markdown-exec: hide
    ```

### Block elements

#### Sequence

As the name says, this is a sequence of elements. This is a useful container when you build more complex diagrams that use the other block elements (like [Stack](#stack), for example).

The constructor for `Sequence` takes one or more elements and an optional parameter dictionary.

Example

```python exec="true" source="tabbed-left" html="1"
from pyrailroad.elements import Diagram, Sequence, Arrow
d = Diagram(Sequence("foo", Arrow(), "bar"))
d.write_svg(print)  # markdown-exec: hide
```

#### Stack

This allows you to stack elements vertically.

The constructor for `Stack` takes one or more elements and an optional parameter dictionary (to modify the arc radius of curves).

Examples

  * A simple stack

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Stack
    d = Diagram(Stack("foo", "bar"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A customized stack with more elements

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Stack, Sequence, Terminal, NonTerminal
    d = Diagram(
            Stack(
                Sequence(NonTerminal("foo"), Terminal("bar")),
                Sequence(NonTerminal("baz"), Terminal("buzz")),
                parameters={'AR':20}
                )
            )
    d.write_svg(print)  # markdown-exec: hide
    ```

#### OptionalSequence

This block is a sequence of elements where you must choose at least one element among the elements passed to it. If only one element is provided, it is turned into a [Sequence](#sequence).

The constructor for `OptionalSequence` takes one or more elements and an optional parameter dictionary (to modify the arc radius of curves).

Examples

  * A simple optional sequence

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, OptionalSequence
    d = Diagram(OptionalSequence("foo", "bar"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A customized optional sequence with more elements

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, OptionalSequence, Sequence, Terminal, NonTerminal, Expression
    d = Diagram(
            OptionalSequence(
                Sequence(NonTerminal("foo"), Terminal("bar")),
                Sequence(NonTerminal("baz"), Terminal("buzz")),
                Expression("fizz"),
                parameters={'AR':20}
                )
            )
    d.write_svg(print)  # markdown-exec: hide
    ```

#### AlternatingSequence

This block means that the two arguments may repeat any number of times, by alternating between the two. You have to take at least one of the two elements.

The constructor for `AlternatingSequence` takes exactly two elements and an optional parameter dictionary (to modify the arc radius of curves).

Examples

  * A simple alternating sequence

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, AlternatingSequence
    d = Diagram(AlternatingSequence("foo", "bar"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A customized alternating sequence with more elements

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, AlternatingSequence, Sequence, Terminal, NonTerminal
    d = Diagram(
            AlternatingSequence(
                Sequence(NonTerminal("foo"), Terminal("bar")),
                Sequence(NonTerminal("baz"), Terminal("buzz")),
                parameters={'AR':20}
                )
            )
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Choice

This block lets you choose one element among multiple elements.

The constructor for `Choice` takes one integer (index for the default element, starting at 0), one or more elements and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * A simple choice

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Choice
    d = Diagram(Choice(0, "foo", "bar"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A customized choice with more elements

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Choice, Sequence, Terminal, NonTerminal
    d = Diagram(
            Choice(
                1,
                Sequence(NonTerminal("foo"), Terminal("bar")),
                Sequence(NonTerminal("baz"), Terminal("buzz")),
                parameters={'VS':50, 'AR': 5}
                )
            )
    d.write_svg(print)  # markdown-exec: hide
    ```

#### MultipleChoice

This block lets you choose one or more elements among multiple elements. Unlike [Choice](#choice), more than one branch can be taken.

The constructor for `MultipleChoice` takes one integer (index for the default element, starting at 0), one of "any" (at least one branch must be taken) or "all" (all branches must be taken), one or more elements and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * A simple alternating sequence

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, MultipleChoice
    d = Diagram(MultipleChoice(0, "any", "foo", "bar"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A customized alternating sequence with more elements

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, MultipleChoice, Sequence, Terminal, NonTerminal
    d = Diagram(
            MultipleChoice(
                1, "all",
                Sequence(NonTerminal("foo"), Terminal("bar")),
                Sequence(NonTerminal("baz"), Terminal("buzz")),
                parameters={'VS':50, 'AR': 5}
                )
            )
    d.write_svg(print)  # markdown-exec: hide
    ```

#### HorizontalChoice

This block lets you choose one element among multiple elements. Unlike [Choice](#choice), items are stacked horizontally, there is no default choice.

The constructor for `HorizontalChoice` takes one or more elements and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * A simple choice

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, HorizontalChoice
    d = Diagram(HorizontalChoice("foo", "bar"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A customized choice with more elements

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, HorizontalChoice, Stack, Terminal, NonTerminal
    d = Diagram(
            HorizontalChoice(
                Stack(NonTerminal("foo"), Terminal("bar")),
                Stack(NonTerminal("baz"), Terminal("buzz")),
                parameters={'VS':50, 'AR': 5}
                )
            )
    d.write_svg(print)  # markdown-exec: hide
    ```

#### optional

This pseudo-block is a shortcut for `#!python Choice(skip?, Skip(), element)`.

`optional` takes one element, an optional boolean (default: `False`) indicating if skipping is the default, and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * optional with skip = False
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, optional
    d = Diagram(optional("foo", False))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * optional with skip = True and customization
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, optional
    d = Diagram(optional("foo", True, parameters={'VS':50, 'AR': 5}))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### OneOrMore

This lets you repeat an element.

The contructor for `OneOrMore` takes one item, an optional repeated item (for example a comment) and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * OneOrMore with no repeat item
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, OneOrMore
    d = Diagram(OneOrMore("foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * OneOrMore with a repeat item and customization
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, OneOrMore, Comment
    d = Diagram(OneOrMore("foo", Comment("bar"), parameters={'VS':50, 'AR': 5}))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### zero_or_more

This pseudo block is a shortcut for `#!python optional(OneOrMore(child, repeat), skip)`.

`zero_or_more` takes one element, an optional repeated item, an optional boolean (default: False) indicating if skipping is the default, and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * zero_or_more with no repeat item
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, zero_or_more
    d = Diagram(zero_or_more("foo"))
    d.write_svg(print)  # markdown-exec: hide
    ```

  * zero_or_more with a repeat item and customization
    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, zero_or_more, Comment
    d = Diagram(zero_or_more("foo", Comment("bar"), True, parameters={'VS':50, 'AR': 5}))
    d.write_svg(print)  # markdown-exec: hide
    ```

#### Group

This lets you highlight an element with a dashed outline.

The constructor for `Group` takes an element, an optioanl label and an optional parameter dictionary (to modify the arc radius of curves or the vertical seperation between lines).

Examples

  * A group with no label

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Choice, Group
    d = Diagram("foo", Group(Choice(0, "opt1", "opt2")) ,"bar")
    d.write_svg(print)  # markdown-exec: hide
    ```

  * A group with a label and customization

    ```python exec="true" source="tabbed-left" html="1"
    from pyrailroad.elements import Diagram, Choice, Group
    d = Diagram("foo", Group(Choice(0, "opt1", "opt2"), "a group", parameters={'VS':50, 'AR': 5}) ,"bar")
    d.write_svg(print)  # markdown-exec: hide
    ```
