<!-- markdownlint-disable-file MD033 MD024 MD046 -->
# Text elements

Text elements are single elements on the diagram and the base building blocks. They are either [**Expression**](#expression), [**Terminal**](#terminal), [**NonTerminal**](#nonterminal), [**Comment**](#comment), [**Arrow**](#arrow) or [**Skip**](#skip).

## Expression

An expression is either a sub-diagram for a bigger diagram (typically, a clause in a grammar, which will appear as non-terminal in another part of the grammar), or something that the EBNF parser couldn't handle on its own (and will need a little help rewriting).

For exemple, the [W3C blindfold grammar for EBNF](https://www.w3.org/2001/06/blindfold/grammar) is specified as follows:

```ebnf
grammar ::= clause*                   # A grammar is zero or more clauses
clause  ::= clauseName "::=" pattern  # A clause associates a name with a pattern
pattern ::= branch ("|" branch)*      # A pattern has one or more branches (alternatives)
branch  ::= term+                     # A branch is one or more terms
term    ::=                           # A term is:  
            string                    #  a string in single or double quotes
          | charset                   #  a character set (as in perl: [a-z0-9], etc) 
          | "(" pattern ")"           #  a pattern, in parentheses 
          | clauseName                #  a clauseName, matching a pattern by name
          | term [*+?]                #  a term followed by a "*", "+", or "?" operator
```

There are five expressions in that grammar, and running py-railroad on it produces the following diagrams:

<figure markdown>
![grammar](../images/w3c_blindfold/grammar.svg)
<figcaption>grammar</figcaption>
</figure>
<figure markdown>
![clause](../images/w3c_blindfold/clause.svg)
<figcaption>clause</figcaption>
</figure>
<figure markdown>
![pattern](../images/w3c_blindfold/pattern.svg)
<figcaption>pattern</figcaption>
</figure>
<figure markdown>
![branch](../images/w3c_blindfold/branch.svg)
<figcaption>branch</figcaption>
</figure>
<figure markdown>
![term](../images/w3c_blindfold/term.svg)
<figcaption>term</figcaption>
</figure>

In the last expression, the last element is [*+?] because the parser treated it as a character range and couldn't tell whether it was a finite list of characters (a [**Choice**](block_elem.md#choice)) or an actual range (ie. "all characters from a to z").

### Syntax

=== "DSL"

    Basic syntax:

    ```dsl
    Expression: my text
    ```

    With a href:

    ```dsl
    Expression "https://github.com": github
    ```

=== "JSON"

    Basic syntax:

    ```json
    {
        "element": "Expression",
        "text": "my expression"
    }
    ```

    With href:

    ```json
    {
        "element": "Expression",
        "text": "github",
        "href": "https://github.com"
    }
    ```

    With additional options:

    ```json
    {
        "element": "Expression",
        "text": "github",
        "href": "https://github.com",
        "title": "This is a link",
        "cls": "custom_terminal"
    }
    ```

=== "YAML"

    Basic:

    ```yaml
    element: Expression
    text: my expression
    ```

    With href

    ```yaml
    element: Expression
    text: github
    href: https://github.com
    ```

    With additional options:

    ```yaml
    element: Expression
    text: github
    href: https://github.com
    title: This is a link
    cls: custom_terminal
    ```

### Properties

### Output

<figure markdown>
![Expression with only text](../images/expression_base.svg)
<figcaption>Expression</figcaption>
</figure>

<figure markdown>
![Expression with href](../images/expression_href.svg)
<figcaption>Expression with href</figcaption>
</figure>

<figure markdown>
![Expression with additional options](../images/expression_full.svg)
<figcaption>Expression with additional options</figcaption>
</figure>

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
    Terminal"https://github.com": github
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
    NonTerminal "https://github.com": github
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
    Comment "https://github.com": github
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

## Arrow

### Syntax

=== "DSL"

    Arrow right:

    ```dsl
    Arrow:
    ```

    With a direction:

    ```dsl
    Arrow: left|right
    ```

    Undirected:

    ```dsl
    Arrow: undirected
    ```

=== "JSON"

    Arrow right:

    ```json
    {
        "element": "Arrow"
    }
    ```

    With a direction:

    ```json
    {
        "element": "Arrow",
        "direction": "left|right"
    }
    ```

    Undirected (draws a line):

    ```json
    {
        "element": "Arrow",
        "direction": "undirected"
    }
    ```

=== "YAML"

    Arrow right:

    ```yaml
    element: Arrow
    ```

    With a direction:

    ```yaml
    element: Arrow
    direction: left|right
    ```

    Undirected:

    ```yaml
    element: Arrow
    direction: undirected
    ```

### Properties

**direction**: optional string, can be *left* or *right* to orient the arrow left or right, or any other string to draw a plain line instead.

### Output

<figure markdown>
![Arrow left](../images/arrow_left.svg)
<figcaption>Arrow left</figcaption>
</figure>
<figure markdown>
![Arrow right](../images/arrow_right.svg)
<figcaption>Arrow right</figcaption>
</figure>
<figure markdown>
![Undirected: a line](../images/arrow_undir.svg)
<figcaption>Undirected: a line</figcaption>
</figure>

## Skip

An empty line. Used for vertical blocks like Stack.

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
        "element": "Skip"
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
