<!-- markdownlint-disable-file MD033 MD024 -->
# Text elements

Text elements are single elements on the diagram and the base building blocks. They are either [**Terminal**](#terminal), [**NonTerminal**](#nonterminal), [**Comment**](#comment) or [**Skip**](#skip).

## Terminal

Terminal represents literal text. The Terminal element has a required property `text`, and three optional properties `href`, `title` and `cls`. The last two properties are only available with the JSON and YAML parsers.

### Syntax

=== "DSL"

    Basic syntax:

    ```dsl
    Terminal: my text
    ```

    With a href:

    ```dsl
    Terminal https://github.com: github
    ```

=== "JSON"

    Basic syntax:

    ```json
    {
        "element": "Terminal",
        "text": "my text"
    }
    ```

    With href:

    ```json
    {
        "element": "Terminal",
        "text": "github",
        "href": "https://github.com"
    }
    ```

    With additional options:

    ```json
    {
        "element": "Terminal",
        "text": "github",
        "href": "https://github.com",
        "title": "This is a link",
        "cls": "custom_terminal"
    }
    ```

=== "YAML"

    Without a label:

    ```yaml
    element: Terminal
    text: my text
    ```

    With href

    ```yaml
    element: Terminal
    text: github
    href: https://github.com
    ```

    With additional options:

    ```yaml
    element: Terminal
    text: github
    href: https://github.com
    title: This is a link
    cls: custom_terminal
    ```

### Properties

- **text**: string, required
- **href**: string, optional
- **title**: string, optional, only available with the JSON and YAML parsers
- **cls**: string, optional, only available with the JSON and YAML parsers

### Output

<figure markdown>
![Terminal with only text](../images/terminal_base.svg)
<figcaption>Simple Terminal</figcaption>
</figure>
<figure markdown>
![Terminal with only href](../images/terminal_href.svg)
<figcaption>With href</figcaption>
</figure>
<figure markdown>
![Terminal with additional options](../images/terminal_full.svg)
<figcaption>With additional options (hover for the title)</figcaption>
</figure>

## NonTerminal

NonTerminal represents another production or diagram. The NonTerminal element has a required property `text`, and three optional properties `href`, `title` and `cls`. The last two properties are only available with the JSON and YAML parsers.

### Syntax

=== "DSL"

    Basic syntax:

    ```dsl
    NonTerminal: my text
    ```

    With a href:

    ```dsl
    NonTerminal https://github.com: github
    ```

=== "JSON"

    Basic syntax:

    ```json
    {
        "element": "NonTerminal",
        "text": "my text"
    }
    ```

    With href:

    ```json
    {
        "element": "NonTerminal",
        "text": "github",
        "href": "https://github.com"
    }
    ```

    With additional options:

    ```json
    {
        "element": "NonTerminal",
        "text": "github",
        "href": "https://github.com",
        "title": "This is a link",
        "cls": "custom_terminal"
    }
    ```

=== "YAML"

    Without a label:

    ```yaml
    element: NonTerminal
    text: my text
    ```

    With href

    ```yaml
    element: NonTerminal
    text: github
    href: https://github.com
    ```

    With additional options:

    ```yaml
    element: NonTerminal
    text: github
    href: https://github.com
    title: This is a link
    cls: custom_terminal
    ```

### Properties

- **text**: string, required
- **href**: string, optional
- **title**: string, optional, only available with the JSON and YAML parsers
- **cls**: string, optional, only available with the JSON and YAML parsers

### Output

<figure markdown>
![NonTerminal with only text](../images/non_terminal_base.svg)
<figcaption>Simple Terminal</figcaption>
</figure>
<figure markdown>
![NonTerminal with only href](../images/non_terminal_href.svg)
<figcaption>With href</figcaption>
</figure>
<figure markdown>
![NonTerminal with additional options](../images/non_terminal_full.svg)
<figcaption>With additional options (hover for the title)</figcaption>
</figure>

## Comment

Represents a comment. The Comment element has a required property `text`, and three optional properties `href`, `title` and `cls`. The last two properties are only available with the JSON and YAML parsers.

### Syntax

=== "DSL"

    Basic syntax:

    ```dsl
    Comment: my text
    ```

    With a href:

    ```dsl
    Comment https://github.com: github
    ```

=== "JSON"

    Basic syntax:

    ```json
    {
        "element": "Comment",
        "text": "my text"
    }
    ```

    With href:

    ```json
    {
        "element": "Comment",
        "text": "github",
        "href": "https://github.com"
    }
    ```

    With additional options:

    ```json
    {
        "element": "Comment",
        "text": "github",
        "href": "https://github.com",
        "title": "This is a link",
        "cls": "custom_terminal"
    }
    ```

=== "YAML"

    Without a label:

    ```yaml
    element: Comment
    text: my text
    ```

    With href

    ```yaml
    element: Comment
    text: github
    href: https://github.com
    ```

    With additional options:

    ```yaml
    element: Comment
    text: github
    href: https://github.com
    title: This is a link
    cls: custom_terminal
    ```

### Properties

- **text**: string, required
- **href**: string, optional
- **title**: string, optional, only available with the JSON and YAML parsers
- **cls**: string, optional, only available with the JSON and YAML parsers

### Output

<figure markdown>
![Comment with only text](../images/comment_base.svg)
<figcaption>Simple Comment</figcaption>
</figure>
<figure markdown>
![Comment with only href](../images/comment_href.svg)
<figcaption>With href</figcaption>
</figure>
<figure markdown>
![Comment with additional options](../images/comment_full.svg)
<figcaption>With additional options (hover for the title)</figcaption>
</figure>

## Skip

An empty line. Used for vertical blocks like Stack.

### Syntax

### Syntax

=== "DSL"

    Basic syntax:

    ```dsl
    Skip:
    ```

=== "JSON"

    Basic syntax:

    ```json
    {
        "element": "Skip",
    }
    ```

=== "YAML"

    Basic syntax:

    ```yaml
    element: Skip
    ```

### Properties

This element has no properties.

### Output

<figure markdown>
![Stack without Skip](../images/stack_no_skip.svg)
<figcaption>Stack without Skip</figcaption>
</figure>
<figure markdown>
![Stack with Skip](../images/stack_skip.svg)
<figcaption>Stack with Skip</figcaption>
</figure>
