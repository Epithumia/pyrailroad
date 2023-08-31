<!-- markdownlint-disable-file MD033 MD024 -->
# Base elements

These are base diagram elements and are automatically added if omitted since they represent the whole diagram, start and end thereof respectively.

## Diagram

The root element of a railroad diagram is the Diagram element. If the input does not start with a Diagram, then one is automatically inserted at the root and will include all the elements in the input as its sub-elements.

### Syntax

=== "DSL"

    ```dsl
    Diagram:
        ...
    ```

=== "JSON"

    ```json
    {
        "element": "Diagram",
        "items": [
            ...
        ]
    }
    ```

=== "YAML"

    ```yaml
    element: Diagram
    items:
    - ...
    ```

## Start

Start is an element that represents the start of the diagram. If it is not explicitly added, it will be inserted as the first element. It can take an optional `label` as a property with all three parsers, and an optional `type` property in JSON and YAML.

### Syntax

=== "DSL"

    Without a label:

    ```dsl
    Start:
    ```

    Without a label:

    ```dsl
    Start: my label
    ```

=== "JSON"

    Without a label:

    ```json
    {
        "element": "Start"
    }
    ```

    With a label:

    ```json
    {
        "element": "Start",
        "label": "my label"
    }
    ```

    With the sql type:

    ```json
    {
        "element": "Start",
        "type": "sql"
    }
    ```

=== "YAML"

    Without a label:

    ```yaml
    element: Start
    ```

    With a label

    ```yaml
    element: Start
    label: my label
    ```

    With the sql type:

    ```yaml
    element: Start
    type: sql
    ```

### Properties

- **label**: a string
- **type**: one of *simple*, *complex* or *sql*. Setting this property at the element level will override what is specified in the parameter file.

### Output

<figure markdown>
![Start with no label](../images/start_no_label.svg)
<figcaption>Without a label</figcaption>
</figure>
<figure markdown>
![Start with a label](../images/start_label.svg)
<figcaption>With a label</figcaption>
</figure>
<figure markdown>
![Start with sql type](../images/start_sql.svg)
<figcaption>With sql type</figcaption>
</figure>

## End

End is symmetric with Start and represents the end of the diagram. If it is not explicitly added, it will be inserted as the last element. It can take an optional `type` as a property in JSON and YAML.

### Syntax

=== "DSL"

    ```dsl
    End:
    ```

=== "JSON"

    Without a label:

    ```json
    {
        "element": "End"
    }
    ```

    With sql type:

    ```json
    {
        "element": "End",
        "type": "sql"
    }
    ```

=== "YAML"

    Without a label:

    ```yaml
    element: End
    ```

    With sql type:

    ```yaml
    element: End
    type: sql
    ```

### Properties

- **type**: one of *simple*, *complex* or *sql*. Setting this property at the element level will override what is specified in the parameter file.

### Output

<figure markdown>
![End with no label](../images/end_no_label.svg)
<figcaption>Without a label</figcaption>
</figure>
<figure markdown>
![End with sql type](../images/end_sql.svg)
<figcaption>With sql type</figcaption>
</figure>
