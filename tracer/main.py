"""
Точка входа. Аналог main.cpp.

Использование:
    python main.py <pg_file.dot> [--scalar_var <name> <val>]... [--array_var <name> <len> <v0> <v1> ...]...

Выходные файлы:
    my_pg.dot, state_sequence.json, action_sequence.json,
    read_var_sequence.json, PIDG.dot
"""
from __future__ import annotations
import sys
import re
import os

sys.path.insert(0, os.path.dirname(__file__))

from tracer.scalar_memory import ScalarMemory
from tracer.array_memory import ArrayMemory
from tracer.array_class import Array
from tracer.memory import Memory
from tracer.variable import Variable, VariableType
from tracer.action import create_assign_action, create_logic_action
from tracer.expr_node import parse_expr_from_rpn, ExprType, copy_node
from tracer.program_graph2 import ProgramGraph2
from tracer.pidg_node import get_abstract_pidg_node
from tracer.pg_builder import cpp_to_program_graph


# ---------------------------------------------------------------------------
# Утилиты вывода
# ---------------------------------------------------------------------------

def value_to_green_color(value: float) -> str:
    if value < 0 or value > 1:
        return "#FFFFFF"
    g = int(value * 255)
    return f"#{0:02x}{g:02x}{0:02x}"


def print_heat_map_as_html_table(heat_map: dict) -> None:
    max_row = max(heat_map.keys(), default=-1)
    max_col = max((max(cols.keys(), default=-1) for cols in heat_map.values()), default=-1)

    print("<table border='1'>")
    print("  <tr>")
    print("    <th></th>")
    for j in range(max_col + 1):
        print(f"    <th>{j}</th>")
    print("  </tr>")

    for i in range(max_row + 1):
        print("  <tr>")
        print(f"    <th>{i}</th>")
        for j in range(max_col + 1):
            value = heat_map.get(i, {}).get(j, 0.0)
            color = value_to_green_color(value)
            print(f"    <td style='background-color: {color};'>{value:.2f}</td>")
        print("  </tr>")
    print("</table>")


def generate_html_table(accordance: dict) -> str:
    html = "<table border='1'>\n  <tr>\n    <th></th>\n"
    keys = sorted(accordance.keys())
    for k in keys:
        html += f"    <th>{k}</th>\n"
    html += "  </tr>\n"
    for k1 in keys:
        html += f"  <tr>\n    <th>{k1}</th>\n"
        for k2 in keys:
            found = k2 in accordance.get(k1, {})
            value = accordance[k1].get(k2, False) if found else False
            style = ""
            if found:
                style = "background-color: #AAFFAA;" if value else "background-color: #FFAAAA;"
            cell = ("true" if value else "false") if found else ""
            html += f'    <td style="{style}">{cell}</td>\n'
        html += "  </tr>\n"
    html += "</table>\n"
    return html


# ---------------------------------------------------------------------------
# Парсинг DOT-файла → ProgramGraph2
# ---------------------------------------------------------------------------

EDGE_RE = re.compile(r'q?(\d+)\s*->\s*q?(\d+)\s*\[label="(.*?)"\]')
FINAL_RE = re.compile(r'q?(\d+)\s*\[shape\s*=\s*doublecircle\]')


def parse_dot_text(pg: ProgramGraph2, dot_text: str) -> int:
    final_node = -1
    for line in dot_text.splitlines():
        m_final = FINAL_RE.search(line)
        if m_final:
            final_node = int(m_final.group(1))
            pg.set_terminal_loc(final_node)

        m_edge = EDGE_RE.search(line)
        if m_edge:
            source_node = int(m_edge.group(1))
            target_node = int(m_edge.group(2))
            label = m_edge.group(3).strip()

            expr = parse_expr_from_rpn(label)
            if expr is None:
                continue

            if expr.type == ExprType.ASSIGN_EXPR:
                var = Variable()
                if expr.left.type == ExprType.VAR:
                    var.type = VariableType.SCALAR_VAR
                    var.name = expr.left.var_name
                elif expr.left.type == ExprType.ARRAY_INDEX:
                    var.type = VariableType.ABSTRACT_ARR_ELEMENT
                    var.name = expr.left.left.var_name
                    var.index_expr = copy_node(expr.left.right)
                action = create_assign_action(var, expr.right)
            else:
                action = create_logic_action(expr)

            pg.add_action_edge(source_node, target_node, action)

    return final_node


# ---------------------------------------------------------------------------
# Чтение / запись файлов
# ---------------------------------------------------------------------------

def read_file(filename: str) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(f"Ошибка: Не удалось открыть файл {filename}: {e}", file=sys.stderr)
        return ""


def write_file(filename: str, content: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> None:
    for i, arg in enumerate(argv):
        print(i, arg)

    if len(argv) < 2:
        return

    pg_file = argv[1]
    scalar_memory = ScalarMemory()
    array_memory = ArrayMemory()

    current_arg = 2
    while current_arg < len(argv) - 1:
        if argv[current_arg] == "--scalar_var":
            var_name = argv[current_arg + 1]
            val = int(argv[current_arg + 2])
            scalar_memory.var_values[var_name] = val
            current_arg += 3
        elif argv[current_arg] == "--array_var":
            var_name = argv[current_arg + 1]
            length = int(argv[current_arg + 2])
            current_arg += 3
            arr: dict[int, int] = {}
            idx = 0
            print("ARRAY READ")
            while (current_arg < len(argv)
                   and argv[current_arg] not in ("--scalar_var", "--array_var")):
                arr[idx] = int(argv[current_arg])
                idx += 1
                current_arg += 1
            array_memory.array_values[var_name] = Array(size=length, index_values=arr)
        else:
            current_arg += 1

    memory = Memory(scalar_memory, array_memory)
    dot_text = read_file(pg_file)

    pg = ProgramGraph2(initial_memory=memory, terminal_loc=0)
    parse_dot_text(pg, dot_text)

    write_file("my_pg.dot", pg.to_dot())

    execution_fragment = pg.execute()
    write_file("state_sequence.json", execution_fragment.state_sequence.to_json())
    write_file("action_sequence.json", execution_fragment.action_sequence.to_json())
    write_file("read_var_sequence.json", execution_fragment.get_json_sequence_read_variables())
    write_file("PIDG.dot", execution_fragment.build_pidg_dot())


if __name__ == "__main__":
    cpp_path = r"D:\Гугл-Диск\КулюкинКС_кандидатская\Сравнение трасс программ\Наши разработки\Эксперименты\Эксперимент_май2025\3\CppSolutions\aaa168_2024.txt\2.cpp"
    code = ""
    with open(cpp_path,"r",encoding="utf-8") as f:
        code = f.read()
    program_graph = cpp_to_program_graph(code,"cut_rectangle_into_squares")
    print(program_graph.to_dot())
    #main(sys.argv)
