# Diagram gallery

A simplified SELECT statement in SQL :

![SQL SELECT](images/sql_select_stmt_simple.svg)

`parameters.yaml`:

```yaml
type: sql
```

`select.yaml`:

```yaml
element: Sequence
items:
  - element: Arrow
  - element: Terminal
    text: SELECT
  - element: Arrow
  - element: OneOrMore
    item:
      element: NonTerminal
      text: column
    repeat:
      element: Sequence
      items:
        - element: Arrow
          direction: left
        - element: Terminal
          text: ','
        - element: Arrow
          direction: left
  - element: Arrow
  - element: Terminal
    text: FROM
  - element: Arrow
  - element: OneOrMore
    item:
      element: NonTerminal
      text: table
    repeat:
      element: Sequence
      items:
        - element: Arrow
          direction: left
        - element: Terminal
          text: ','
        - element: Arrow
          direction: left
  - element: Arrow
  - element: Terminal
    text: WHERE
  - element: Arrow
  - element: NonTerminal
    text: condition
```
