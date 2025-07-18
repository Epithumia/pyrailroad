from DHParser import Node
from DHParser.ebnf import transform_ebnf
from DHParser.ebnf_flavors.heuristic import HeuristicEBNFGrammar

from .elements import Diagram
from .exceptions import ParseException


def parse_ebnf(string: str, parameters: dict) -> dict[str:Diagram]:
    parse = HeuristicEBNFGrammar()

    cst = parse(string)

    if cst.error_flag > 999:
        raise ParseException(str(cst.errors[0]))
    elif cst.error_flag > 0:
        for e in cst.errors:  # Not sure if the EBNF grammar allows to raise warnings
            print(e)

    ast = transform_ebnf(cst)
    keep_quotes = False
    if "keep_quotes" in parameters.keys():
        keep_quotes = parameters["keep_quotes"]
    data = ast_to_dict(ast, keep_quotes)

    diagrams = {}
    for diagram_data in data["grammar"]:
        name = diagram_data["items"][0]["label"]
        diagrams[name] = Diagram.from_dict(diagram_data, parameters)

    return diagrams


def ast_to_dict(tree: Node, keep_quotes=False) -> dict:
    non_terminals = []
    if tree.name == "syntax":
        ebnf_dict = {"grammar": []}
        for child in tree.children:
            if non_terminal := get_non_terminal(child):
                non_terminals.append(non_terminal)
        for child in tree.children:
            item = process(child, non_terminals, keep_quotes=keep_quotes)
            if item:
                ebnf_dict["grammar"].append(item)
        return ebnf_dict
    return {}


def process(tree: Node, non_terminals: list, explicit_group=False, keep_quotes=False):
    match tree.name:
        case "definition":
            result = {
                "element": "Diagram",
                "items": [{"element": "Start", "label": tree.children[0].content}],
            }
            result["items"].append(
                process(tree.children[1], non_terminals, keep_quotes=keep_quotes)
            )
            result["items"].append({"element": "End"})
            return result
        case "repetition":
            return {
                "element": "ZeroOrMore",
                "item": process(
                    tree.children[0], non_terminals, keep_quotes=keep_quotes
                ),
            }
        case "oneormore":
            return {
                "element": "OneOrMore",
                "item": process(
                    tree.children[0], non_terminals, keep_quotes=keep_quotes
                ),
            }
        case "sequence":
            return {
                "element": "Sequence",
                "items": [
                    process(child, non_terminals, keep_quotes=keep_quotes)
                    for child in tree.children
                ],
            }
        case "symbol":
            if tree.content in non_terminals:
                return {"element": "NonTerminal", "text": tree.content}
            else:
                return {"element": "Terminal", "text": tree.content}
        case "character":
            return {
                "element": "Terminal",
                "text": f"#x{tree.content}",
                "cls": "character",
            }
        case ":Text" | "free_char":
            return {"element": "Terminal", "text": str(tree.content)}
        case "literal":
            if keep_quotes:
                return {"element": "Terminal", "text": str(tree.content)}
            if str(tree.content).startswith('"'):
                return {"element": "Terminal", "text": str(tree.content.strip('"'))}
            return {"element": "Terminal", "text": str(tree.content.strip("'"))}
        case "expression":
            return {
                "element": "Choice",
                "default": len(tree.children) // 2,
                "items": [
                    process(child, non_terminals, keep_quotes=keep_quotes)
                    for child in tree.children
                ],
            }
        case "group":
            if len(tree.children) > 1:
                raise NotImplementedError(
                    "Please open an issue on the github repository with the grammar you used."
                )  # pragma: no cover
            if explicit_group:
                return {
                    "element": "Sequence",
                    "items": [
                        {"element": "Terminal", "text": "("},
                        process(
                            tree.children[0], non_terminals, keep_quotes=keep_quotes
                        ),
                        {"element": "Terminal", "text": ")"},
                    ],
                }
            return process(tree.children[0], non_terminals, keep_quotes=keep_quotes)
        case "char_range":
            return {
                "element": "Expression",
                "text": f"[{''.join([collapse(process(child, [], keep_quotes=keep_quotes)) for child in tree.children])}]",
            }
        case "range_desc":
            return {
                "element": "Expression",
                "text": f"{''.join([collapse(process(child, [], keep_quotes=keep_quotes)) for child in tree.children])}",
            }
        case "difference":
            if len(tree.children) != 2:
                raise NotImplementedError(
                    "Please open an issue on the github repository with the grammar you used."
                )  # pragma: no cover
            return {
                "element": "Expression",
                "text": f"{collapse(process(tree.children[0],[], True, keep_quotes=keep_quotes))} - {collapse(process(tree.children[1],[], True, keep_quotes=keep_quotes))}",
            }
        case "option":
            return {
                "element": "Optional",
                "item": process(
                    tree.children[0], non_terminals, keep_quotes=keep_quotes
                ),
            }
        case _:
            raise NotImplementedError(tree.name)  # pragma: no cover


def collapse(node: dict) -> str:
    match node["element"]:
        case "Terminal" | "Expression":
            return node["text"]
        case "ZeroOrMore":
            return f"{collapse(node['item'])}*"
        case "Sequence":
            return " ".join([collapse(item) for item in node["items"]])
        case "Choice":
            return " | ".join([collapse(item) for item in node["items"]])
        case _:  # pragma: no cover
            raise NotImplementedError(node)  # pragma: no cover


def get_non_terminal(tree: Node) -> str | None:
    if tree.name == "definition":
        return get_non_terminal(tree.children[0])
    if tree.name == "symbol":
        return tree.content
    return None  # pragma: no cover
