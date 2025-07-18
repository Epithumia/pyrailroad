<!-- markdownlint-disable-file MD033 -->
# PyRailroad : Railroad-Diagram Generator

<figure>![Title image](images/title.svg)</figure>

PyRailroad is a Python package to draw railroad (or syntax) diagrams. Based largely on [railroad-diagrams](https://github.com/tabatkins/railroad-diagrams) and the [partial parser](https://github.com/speced/bikeshed/blob/main/bikeshed/railroadparser.py), both by [tabatkins](https://github.com/tabatkins)

This package can be used as a stand-alone (command-line interface) generator or as a library. this generates railroad diagrams (like what [JSON.org](http://json.org) uses) using SVG.

Railroad diagrams, or syntax diagrams, are useful in representing *grammar* in the programming sense.

## Getting started

Install it with pip: `python3 -m pip install pyrailroad`

After that, `py-railroad --help` will show you some help.

This tool cas be used standalone as a command line program ([CLI](cli/index.md)) or as a [library](library.md). The former will give you details about the syntax of the input files or code used to generate the various diagram elements.

A [Gallery](gallery.md) is also coming soon to see how all the elements interact together.
