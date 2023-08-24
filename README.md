# pyrailroad : Railroad-Diagram Generator

Python package to draw railroad (or syntax) diagrams. Based largely on [railroad-diagrams](https://github.com/tabatkins/railroad-diagrams) and the [partial parser](https://github.com/speced/bikeshed/blob/main/bikeshed/railroadparser.py[) by [tbatkins](https://github.com/tabatkins)

This package can be used as a stand-alone (command-line interface) generator or as a library. this generates railroad diagrams (like what [JSON.org](http://json.org) uses) using SVG.

## Diagrams (CLI)

The most simple way to construct diagrams is done using a YAML-like structure, saved in a file and passed to the program.

### Components (CLI)

Components are either leaves (containing only text or similar) or containers (containing other components).

Leaves follow the following format:

```yaml
leaf [prelude]: content
```

Containers follow the following format:

```yaml
container: [prelude]
    child_1
    child_2
    ...
```

#### Leaves

##### Terminal, T

Represents literal text.

```yaml
Terminal: text
```

or

```yaml
T: text
```

![Terminal](images/terminal.svg)

```yaml
Terminal "https://github.com/tabatkins/railroad-diagrams": railroad-diagrams
```

![Terminal](images/terminal_html.svg)

##### NonTerminal, N

Represents an instruction or another production.

```yaml
NonTerminal: text
```

or

```yaml
N: text
```

![NonTerminal](images/non_terminal.svg)

```yaml
NonTerminal "https://github.com/tabatkins/railroad-diagrams": goto railroad-diagrams
```

![NonTerminal](images/non_terminal_html.svg)

##### Comment, C

A comment.

The optional arguments have the same meaning as for Terminal, except that the default class is `'non-terminal'`.

```yaml
Comment: text
```

or

```yaml
C: text
```

![Comment](images/comment.svg)

```yaml
Comment "https://github.com/tabatkins/railroad-diagrams": goto railroad-diagrams
```

![Comment](images/comment_html.svg)

##### Skip, S

An empty line

```yaml
Stack:
    Sequence:
        NonTerminal: non-terminal
        Terminal: terminal
    Skip:
    Sequence:
        NonTerminal: non-terminal
        Terminal: terminal
```

![Skip](images/skip.svg)

Without Skip:

```yaml
Stack:
    Sequence:
        NonTerminal: non-terminal
        Terminal: terminal
    Sequence:
        NonTerminal: non-terminal
        Terminal: terminal
```

![No Skip](images/no_skip.svg)

#### Containers

##### Sequence, Seq, And

A sequence of components, like simple concatenation in a regex.

```yaml
Sequence:
    Terminal: item
    NonTerminal: operation
    Terminal: item2
```

or

```yaml
Seq:
    Terminal: item
    NonTerminal: operation
    Terminal: item2
```

or

```yaml
And:
    Terminal: item
    NonTerminal: operation
    Terminal: item2
```

![Sequence](images/sequence.svg)

##### Stack

Identical to a Sequence, but the items are stacked vertically rather than horizontally. Best used when a simple Sequence would be too wide; instead, you can break the items up into a Stack of Sequences of an appropriate width.

```yaml
Stack:
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

![Stack](images/stack.svg)

##### OptionalSequence

A Sequence where every item is *individually* optional, but at least one item must be chosen

```yaml
OptionalSequence:
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

![Optional Sequence](images/optional_sequence.svg)

##### Choice

Like `|` in a regex.  The optional index argument specifies which child is the "normal" choice and should go in the middle (starting from 0 for the first child).

```yaml
Choice:
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

or

```yaml
Choice: 0
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

![Choice default](images/choice_default.svg)

```yaml
Choice: 1
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

![Choice 1](images/choice_1.svg)

##### MultipleChoice

Like `||` or `&&` in a CSS grammar; it's similar to a Choice, but more than one branch can be taken.  The index argument specifies which child is the "normal" choice and should go in the middle, while the type argument must be either "any" (1+ branches can be taken) or "all" (all branches must be taken).

```yaml
MultipleChoice: 1 any
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

![Choice 1](images/multi_choice_any.svg)

```yaml
MultipleChoice: 1 all
    Terminal: foo
    Terminal: bar
    Terminal: baz
```

![Choice 1](images/multi_choice_all.svg)

##### HorizontalChoice

Identical to Choice, but the items are stacked horizontally rather than vertically. There's no "straight-line" choice, so it just takes a list of children. Best used when a simple Choice would be too tall; instead, you can break up the items into a HorizontalChoice of Choices of an appropriate height.

```yaml
HorizontalChoice:
    Choice: 2
        Terminal: 0
        Terminal: 1
        Terminal: 2
        Terminal: 3
        Terminal: 4
    Choice: 2
        Terminal: 5
        Terminal: 6
        Terminal: 7
        Terminal: 8
        Terminal: 9
```

![Horizontal Choice](images/horizontal_choice.svg)

##### Optional

Like `?` in a regex.  A shorthand for `Choice(1, Skip(), child)`.  If the optional `skip` parameter is `True`, it instead puts the Skip() in the straight-line path, for when the "normal" behavior is to omit the item.

```yaml
Sequence:
    Optional:
        Terminal: foo
    Optional: skip
        Terminal: bar
```

![Optional](images/optional.svg)

##### OneOrMore

Like `+` in a regex.  The 'repeat' argument is optional, and specifies something that must go between the repetitions (usually a `Comment`, but sometimes things like `","`, etc.)

```yaml
Sequence:
    OneOrMore:
        NonTerminal: Row
        Terminal: ,
    Terminal: your boat
```

![One or more](images/one_or_more.svg)

##### ZeroOrMore

Like `*` in a regex.  A shorthand for `Optional(OneOrMore(child, repeat), skip)`.  Both `repeat` (same as in `OneOrMore()`) and `skip` (same as in `Optional()`) are optional.

```yaml
Sequence:
    ZeroOrMore:
        Terminal: foo
        Comment: repeat if necessary
    ZeroOrMore: skip
        Terminal: bar
        Comment: repeat if necessary
```

![One or more](images/zero_or_more.svg)

##### AlternatingSequence

Similar to a `OneOrMore`, where you must alternate between the two choices, but allows you to start and end with either element. (`OneOrMore` requires you to start and end with the "child" node.)

```yaml
AlternatingSequence:
    Terminal: alt1
    Terminal: alt2
```

![AlternatingSequence](images/alternating.svg)

##### Group

Highlights its child with a dashed outline, and optionally labels it. Passing a string as the label constructs a Comment, or you can build one yourself (to give an href or title).

```yaml
Sequence:
    Terminal: foo
    Group: label
        Choice:
            NonTerminal: cmd1
            NonTerminal: cmd2
    Terminal: bar
```

![Group](images/group.svg)

### Options

#### Diagram type : simple, complex, SQL

.

#### Standalone mode or external stylesheet

.
