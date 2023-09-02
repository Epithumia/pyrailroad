from DHParser import Node
from DHParser.ebnf import HeuristicEBNFGrammar, transform_ebnf

from .elements import Diagram
from .exceptions import ParseException


def parse_ebnf(string: str, parameters: {}) -> dict[str:Diagram]:
    parse = HeuristicEBNFGrammar()

    cst = parse(string)

    if cst.error_flag > 999:
        raise ParseException(str(cst.errors[0]))
    elif cst.error_flag > 0:
        for e in cst.errors:
            print(e)

    ast = transform_ebnf(cst)
    data = ast_to_dict(ast)

    diagrams = {}
    for diagram_data in data["grammar"]:
        name = diagram_data["items"][0]["label"]
        diagrams[name] = Diagram.from_dict(diagram_data, parameters)

    return diagrams


def ast_to_dict(tree: Node) -> dict:
    non_terminals = []
    if tree.name == "syntax":
        for child in tree.children:
            if non_terminal := get_non_terminal(child):
                non_terminals.append(non_terminal)
        return {"grammar": [process(child, non_terminals) for child in tree.children]}
    return {}


def process(tree: Node, non_terminals: []):
    match tree.name:
        case "definition":
            result = {
                "element": "Diagram",
                "items": [{"element": "Start", "label": tree.children[0].content}],
            }

            result["items"].append(process(tree.children[1], non_terminals))

            result["items"].append({"element": "End"})

            return result
        case "repetition":
            return {
                "element": "ZeroOrMore",
                "item": process(tree.children[0], non_terminals),
            }
        case "oneormore":
            return {
                "element": "OneOrMore",
                "item": process(tree.children[0], non_terminals),
            }
        case "sequence":
            return {
                "element": "Sequence",
                "items": [process(child, non_terminals) for child in tree.children],
            }
        case "symbol":
            if tree.content in non_terminals:
                return {"element": "NonTerminal", "text": tree.content}
            else:
                return {"element": "Terminal", "text": tree.content}
        case "literal":
            return {"element": "Terminal", "text": tree.content}
        case "expression":
            return {
                "element": "Choice",
                "default": len(tree.children) // 2,
                "items": [process(child, non_terminals) for child in tree.children],
            }
        case "group":
            if len(tree.children) > 1:
                raise NotImplementedError()
            return process(tree.children[0], non_terminals)
        case "char_range":
            return {
                "element": "Expression",
                "text": f"[{''.join(child.content for child in tree.children)}]",
            }
        case "difference":
            if len(tree.children) != 2:
                raise NotImplementedError()
            return {
                "element": "Expression",
                "text": f"{tree.children[0].content} - {tree.children[1].content}",
            }
        case _:
            print(tree.to_json_obj())
            raise NotImplementedError()


def get_non_terminal(tree: Node) -> str | None:
    if tree.name == "definition":
        return get_non_terminal(tree.children[0])
    if tree.name == "symbol":
        return tree.content
    return None
