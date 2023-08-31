<!-- markdownlint-disable-file MD033 MD024 -->
# Block elements

Block elements helps you structure your diagram logically and/or spatially. The spatial elements are: [**Sequence**](#sequence), [**Stack**](#stack) and [**Group**](#group); Logical elements are [**OptionalSequence**](#optionalsequence), [**Choice**](#choice), [**MultipleChoice**](#multiplechoice), [**Optional**](#optional), [**OneOrMore**](#oneormore), [**ZeroOrMore**](#zeroormore), [**AlternatingSequence**](#alternatingsequence), and finally [**HorizontalChoice**](#horizontalchoice) combines both spatial and logic.

## Sequence

Sequence is a concatenation of other elements and requires at least one child element.

### Syntax

=== "DSL"

    ```dsl
    Sequence:
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "Sequence",
        "items": [
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: Sequence
    items:
    - ...
    ```

### Properties

- **items**: an array/list of elements

### Output

<figure markdown>
![Sequence of three Terminals 1, 2 and 3](../images/sequence.svg)
<figcaption>Sequence of three Terminals 1, 2 and 3</figcaption>
</figure>

## Stack

Identical to a Sequence, but the items are stacked vertically rather than horizontally. Best used when a simple Sequence would be too wide; instead, you can break the items up into a Stack of Sequences of an appropriate width.

### Syntax

=== "DSL"

    ```dsl
    Stack:
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "Stack",
        "items": [
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: Stack
    items:
    - ...
    ```

### Properties

- **items**: an array/list of elements

### Output

<figure markdown>
![Stack of three Terminals 1, 2 and 3](../images/stack.svg)
<figcaption>Stack of three Terminals 1, 2 and 3</figcaption>
</figure>

## Group

Highlights its child with a dashed outline, and optionally labels it. Passing a string as the label constructs a Comment, or you can build one yourself (to give an href or title). The DSL parser only accepts text labels, the JSON and YAML parsers accept any element as well as text.

### Syntax

=== "DSL"

    Without a label:

    ```dsl
    Group:
        ...
    ```

    With a label:

    ```dsl
    Group: label
        ...
    ```

=== "JSON"

    Without a label:

    ```json
    {
        "element": "Group",
        "item": {
            ...
        }
    }
    ```

    With a label:

    ```json
    {
        "element": "Group",
        "label": ...
        "item": {
            ...
        }
    }
    ```

=== "YAML"

    Without a label:

    ```yaml
    element: Group
    item:
      ...
    ```

    With a label:

    ```yaml
    element: Group
    label: ...
    item:
      ...
    ```

### Properties

- **label**: optional, can be a string, or when using the JSON or YAML parsers, any element. The most likely case is using a [**Comment**](../text_elem#comment) but any element will work.
- **item** : a single element, mandatory.

### Output

<figure markdown>
![Group with no label](../images/group_no_label.svg)
<figcaption>Group with no label</figcaption>
</figure>
<figure markdown>
![Group with a label](../images/group_label.svg)
<figcaption>Group with a (Comment) label</figcaption>
</figure>

## Choice

An exclusive choice among all branches.

### Syntax

=== "DSL"

    Without default:

    ```dsl
    Choice:
        ...
        ...
    ```

    With a default branch:

    ```dsl
    Choice: value
        ...
        ...
    ```

=== "JSON"

    Without default:

    ```json
    {
        "element": "Choice",
        "items": [
            ...
            ...
        ]
    }
    ```

    With a default branch:

    ```json
    {
        "element": "Choice",
        "default": value,
        "items": [
            ...
            ...
        ]
    }
    ```

=== "YAML"

    Without default:

    ```yaml
    element: Choice
    items:
      ...
      ...
    ```

    With a default branch:

    ```yaml
    element: Choice
    default: value
    items:
      ...
      ...
    ```

### Properties

- **default**: int, optional (if not set: 0). Specifies which child is the "normal" choice and should go in the middle (starting from 0 for the first child).
- **items**: an array/list of elements. Each element will have its own line.

### Output

<figure markdown>
![Choice between three values](../images/choice.svg)
<figcaption>Choice between three values</figcaption>
</figure>

## HorizontalChoice

Identical to Choice, but the items are stacked horizontally rather than vertically. There's no "straight-line" choice, so it just takes a list of children. Best used when a simple Choice would be too tall; instead, you can break up the items into a HorizontalChoice of Choices of an appropriate height.

### Syntax

=== "DSL"

    ```dsl
    HorizontalChoice:
        ...
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "HorizontalChoice",
        "items": [
            ...
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: HorizontalChoice
    items:
      ...
      ...
    ```

### Properties

- **items**: an array/list of elements. Each element will have its own "column".

### Output

<figure markdown>
![Choice between six values, broken in two blocks](../images/horizontal_choice.svg)
<figcaption>Choice between six values, broken in two blocks</figcaption>
</figure>

## MultipleChoice

Similar to a Choice, but more than one branch can be taken.

### Syntax

=== "DSL"

    ```dsl
    MultipleChoice: value any|all
        ...
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "MultipleChoice",
        "default": value,
        "type": "any|all",
        "items": [
            ...
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: MultipleChoice
    default: value
    type: any|all
    items:
      ...
      ...
    ```

### Properties

All properties are mandatory.

- **default**: int, specifies which child is the "normal" choice and should go in the middle
- **type**: either *any* (1+ branches can be taken) or *all*  (all branches must be taken).
- **items**: an array/list of elements. Each element will have its own line.

### Output

<figure markdown>
![MultipleChoice: any of three](../images/multiple_choice_any.svg)
<figcaption>MultipleChoice: any of three</figcaption>
</figure>
<figure markdown>
![MultipleChoice: all of three](../images/multiple_choice_any.svg)
<figcaption>MultipleChoice: all of three</figcaption>
</figure>

## Optional

A shorthand for Choice(0|1, Skip(), child).

### Syntax

=== "DSL"

    Don't skip:

    ```dsl
    Optional:
        ...
    ```

    Skip:

    ```dsl
    Optional: skip
        ...
    ```

=== "JSON"

    Don't skip:

    ```json
    {
        "element": "Optional",
        "item": {
            ...
        }
    }
    ```

    Skip:

    ```json
    {
        "element": "Optional",
        "skip": true,
        "item": {
            ...
        }
    }
    ```

=== "YAML"

    Don't skip:

    ```yaml
    element: Optional
    item:
      ...
    ```

    Skip:

    ```yaml
    element: Optional
    skip: true
    item:
      ...
    ```

### Properties

- **skip**: with DSL, this is either empty or the string "skip" ; in JSON/YAML, this is an optional boolean (*false* if not specified).
- **item**: an element, mandatory.

### Output

<figure markdown>
![Optional without skip](../images/optional_no_skip.svg)
<figcaption>Optional without skip</figcaption>
</figure>
<figure markdown>
![Optional with skip](../images/optional_skip.svg)
<figcaption>Optional with skip</figcaption>
</figure>

## OptionalSequence

A Sequence where every item is individually optional, but at least one item must be chosen.

=== "DSL"

    ```dsl
    OptionalSequence:
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "OptionalSequence",
        "items": [
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: OptionalSequence
    items:
    - ...
    ```

### Properties

- **items**: an array/list of elements

### Output

<figure markdown>
![OptionalSequence of three Terminals 1, 2 and 3](../images/optional_sequence.svg)
<figcaption>OptionalSequence of three Terminals 1, 2 and 3</figcaption>
</figure>

## OneOrMore

A loop that requires taking the first element at least once. The loop is typically a Comment but can be any element.

### Syntax

=== "DSL"

    Simple repeat:

    ```dsl
    OneOrMore:
        ...
    ```

    Labelled repeat:

    ```dsl
    OneOrMore: label
        ...
    ```

=== "JSON"

    Simple repeat:

    ```json
    {
        "element": "OneOrMore",
        "item": {
            ...
        }
    }
    ```

    Repeat with an element:

    ```json
    {
        "element": "OneOrMore",
        "item": {
            ...
        },
        "repeat": {
            ...
        }
    }
    ```

=== "YAML"

    Simple repeat:

    ```yaml
    element: OneOrMore
    item:
      ...
    ```

    Repeat with an element:

    ```yaml
    element: OneOrMore
    item:
      ...
    repeat:
      ...
    ```

### Properties

- **item** : a single element, mandatory.
- **repeat**: if empty, will just draw a line, else will insert the element on the loop. With the DSL parser, this is a string.

### Output

<figure markdown>
![Simple OneOrMore](../images/one_or_more_simple.svg)
<figcaption>Simple OneOrMore</figcaption>
</figure>
<figure markdown>
![Simple OneOrMore](../images/one_or_more_label.svg)
<figcaption>OneOrMore with a label or Comment</figcaption>
</figure>
<figure markdown>
![Simple OneOrMore](../images/one_or_more_element.svg)
<figcaption>OneOrMore with a Terminal (",")</figcaption>
</figure>

## ZeroOrMore

A shorthand for Optional(OneOrMore(child, repeat), skip). Like OneOrMore, this is a loop, but it can be skipped.

### Syntax

=== "DSL"

    Simple ZeroOrMore:

    ```dsl
    ZeroOrMore:
        ...
    ```

    ZeroOrMore with an element and skip as default::

    ```dsl
    OneOrMore: skip
        ...
        ... (repeat)
    ```

=== "JSON"

    Simple ZeroOrMore:

    ```json
    {
        "element": "ZeroOrMore",
        "item": {
            ...
        }
    }
    ```

    ZeroOrMore with an element and skip as default:

    ```json
    {
        "element": "ZeroOrMore",
        "item": {
            ...
        },
        "skip": true,
        "repeat": {
            ...
        }
    }
    ```

=== "YAML"

    Simple ZeroOrMore:

    ```yaml
    element: ZeroOrMore
    item:
      ...
    ```

    ZeroOrMore with an element and skip as default:

    ```yaml
    element: OneOrMore
    skip: true
    item:
      ...
    repeat:
      ...
    ```

### Properties

- **item** : a single element, mandatory.
- **repeat**: if omitted, will just draw a line, else will insert the element on the loop. With the DSL parser, this is a string.
- **skip**: with DSL, this is either empty or the string "skip" ; in JSON/YAML, this is an optional boolean (*false* if not specified).

### Output

<figure markdown>
![Simple ZeroOrMore](../images/zero_or_more_simple.svg)
<figcaption>Simple ZeroOrMore</figcaption>
</figure>
<figure markdown>
![ZeroOrMore with skip and a label](../images/zero_or_more_complex.svg)
<figcaption>ZeroOrMore with skip and a label</figcaption>
</figure>

## AlternatingSequence

Similar to a OneOrMore, where you must alternate between the two choices, but allows you to start and end with either element (OneOrMore requires you to start and end with the "child" node).

### Syntax

=== "DSL"

    ```dsl
    AlternatingSequence:
        ...
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "AlternatingSequence",
        "items": [
            ...
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: AlternatingSequence
    items:
    - ...
    - ...
    ```

### Properties

- **items**: an array/list of exactly two elements

### Output

<figure markdown>
![AlternatingSequence](../images/alternating_sequence.svg)
<figcaption>AlternatingSequence</figcaption>
</figure>
