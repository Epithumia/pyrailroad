# Display constants
DIAGRAM_CLASS = "railroad-diagram"  # class to put on the root <svg>
DEBUG = False  # if True, add debug info to the diagram
STROKE_ODD_PIXEL_LENGTH = (
    True  # is the stroke width an odd (1px, 3px, etc) pixel length?
)
VS = 8  # minimum vertical separation between things. For a 3px stroke, must be at least 4
AR = 10  # radius of arcs
CHAR_WIDTH = 8  # width of each monospace character. play until you find the right value for your font
COMMENT_CHAR_WIDTH = 7  # comments are in smaller text by default
INTERNAL_ALIGNMENT = (
    "center"  # how to align items when they have extra space. left/right/center
)
ESCAPE_HTML = True  # Should Diagram.write_text() produce HTML-escaped text, or raw?
FORMATTING = "unicode"  # "unicode" or "ascii"
