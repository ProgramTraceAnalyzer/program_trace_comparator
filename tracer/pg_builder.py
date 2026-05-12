"""
PG_builder.py — строит ProgramGraph2 из C++ кода.

Основная точка входа:
    cpp_to_program_graph(cpp_code, func_name='main', initial_memory=None) -> ProgramGraph2
"""
import sys
import re
import os

sys.path.insert(0, os.path.dirname(__file__))

from pycparser import c_parser, c_ast, c_generator

from tracer.memory import Memory
from tracer.variable import Variable, VariableType
from tracer.action import create_assign_action, create_logic_action
from tracer.expr_node import parse_expr_from_rpn, ExprType, copy_node
from tracer.program_graph2 import ProgramGraph2


# ---------------------------------------------------------------------------
# TAC-конвертер (без изменений логики)
# ---------------------------------------------------------------------------

class TACConverter:
    def __init__(self):
        self.tac = []
        self.temp_count = 0
        self.generator = c_generator.CGenerator()
        self.label_map = {}
        self.next_label_id = 0
        self.loop_stack = []
        self.curr_temp_var_id = 0

    def new_temp(self):
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def new_label(self):
        label = f"L{self.next_label_id}"
        self.next_label_id += 1
        return label

    def to_rpn(self, expr):
        if isinstance(expr, c_ast.Constant):
            return expr.value
        elif isinstance(expr, c_ast.ID):
            return expr.name
        elif isinstance(expr, c_ast.ArrayRef):
            array_name = self.to_rpn(expr.name)
            subscript = self.to_rpn(expr.subscript)
            return f"{array_name} {subscript} []"
        elif isinstance(expr, c_ast.UnaryOp):
            operand = self.to_rpn(expr.expr)
            op = expr.op
            if op in ("+", "-"):
                op = "_" + op
            if op == "&":
                raise ValueError(f"Address-of operator (&) not supported")
            elif op == "p++":
                tmp = f"'t{self.curr_temp_var_id}"; self.curr_temp_var_id += 1
                self.tac.append(('assign', tmp, f"{operand}"))
                self.tac.append(('assign', operand, f"{operand} 1 +"))
                return tmp
            elif op == "++":
                tmp = f"'t{self.curr_temp_var_id}"; self.curr_temp_var_id += 1
                self.tac.append(('assign', tmp, f"{operand} 1 +"))
                self.tac.append(('assign', operand, f"{operand} 1 +"))
                return tmp
            elif op == "p--":
                tmp = f"'t{self.curr_temp_var_id}"; self.curr_temp_var_id += 1
                self.tac.append(('assign', tmp, f"{operand}"))
                self.tac.append(('assign', operand, f"{operand} 1 -"))
                return tmp
            elif op == "--":
                tmp = f"'t{self.curr_temp_var_id}"; self.curr_temp_var_id += 1
                self.tac.append(('assign', tmp, f"{operand} 1 -"))
                self.tac.append(('assign', operand, f"{operand} 1 -"))
                return tmp
            return f"{operand} {op}"
        elif isinstance(expr, c_ast.BinaryOp):
            left = self.to_rpn(expr.left)
            right = self.to_rpn(expr.right)
            return f"{left} {right} {expr.op}"
        elif isinstance(expr, c_ast.TernaryOp):
            cond = self.to_rpn(expr.cond)
            iftrue = self.to_rpn(expr.iftrue)
            iffalse = self.to_rpn(expr.iffalse)
            return f"{cond} {iftrue} {iffalse} ?:"
        elif isinstance(expr, c_ast.Assignment):
            left = self.to_rpn(expr.lvalue)
            right = self.to_rpn(expr.rvalue)
            return f"{left} {right} {expr.op}"
        else:
            return self.generator.visit(expr)

    def add_assignment(self, lhs, rhs, assign_type):
        if isinstance(lhs, c_ast.ArrayRef):
            lhs_rpn = self.to_rpn(lhs)
        elif isinstance(lhs, c_ast.ID):
            lhs_rpn = lhs.name
        else:
            lhs_rpn = lhs

        rhs_rpn = self.to_rpn(rhs)
        if assign_type != "=":
            rhs_rpn = f"{lhs_rpn} {rhs_rpn} {assign_type[0]}"

        if not isinstance(lhs, c_ast.ArrayRef):
            self.tac.append(('assign', lhs_rpn, rhs_rpn))
        else:
            self.tac.append(('array_assign', lhs_rpn, rhs_rpn))

    def add_if(self, cond, true_label):
        self.tac.append(('if', self.to_rpn(cond), true_label))

    def add_goto(self, label):
        self.tac.append(('goto', label))

    def add_label(self, label):
        self.label_map[label] = len(self.tac)

    def add_return(self, expr):
        rpn = self.to_rpn(expr) if expr else ''
        self.tac.append(('return', rpn))

    def visit(self, node):
        if isinstance(node, c_ast.Assignment):
            self.add_assignment(node.lvalue, node.rvalue, node.op)
        elif isinstance(node, c_ast.UnaryOp):
            rhs_rpn = self.to_rpn(node.expr)
            if node.op in ("p++", "++"):
                self.tac.append(('assign', self.to_rpn(node.expr), f"{rhs_rpn} 1 +"))
            elif node.op in ("p--", "--"):
                self.tac.append(('assign', self.to_rpn(node.expr), f"{rhs_rpn} 1 -"))
        elif isinstance(node, c_ast.If):
            true_label = self.new_label()
            end_label = self.new_label()
            self.add_if(node.cond, true_label)
            if node.iffalse:
                self.visit(node.iffalse)
            self.add_goto(end_label)
            self.add_label(true_label)
            self.visit(node.iftrue)
            self.add_label(end_label)
        elif isinstance(node, c_ast.While):
            start_label = self.new_label()
            body_label = self.new_label()
            end_label = self.new_label()
            self.loop_stack.append((end_label, start_label))
            self.add_label(start_label)
            self.add_if(node.cond, body_label)
            self.add_goto(end_label)
            self.add_label(body_label)
            self.visit(node.stmt)
            self.add_goto(start_label)
            self.add_label(end_label)
            self.loop_stack.pop()
        elif isinstance(node, c_ast.For):
            init_label = self.new_label()
            start_label = self.new_label()
            body_label = self.new_label()
            next_label = self.new_label()
            end_label = self.new_label()
            self.loop_stack.append((end_label, next_label))
            if node.init:
                self.visit(node.init)
            self.add_label(init_label)
            self.add_label(start_label)
            if node.cond:
                self.add_if(node.cond, body_label)
                self.add_goto(end_label)
            else:
                self.add_goto(body_label)
            self.add_label(body_label)
            self.visit(node.stmt)
            self.add_label(next_label)
            if node.next:
                self.visit(node.next)
            self.add_goto(start_label)
            self.add_label(end_label)
            self.loop_stack.pop()
        elif isinstance(node, c_ast.DoWhile):
            body_label = self.new_label()
            cond_label = self.new_label()
            end_label = self.new_label()
            self.loop_stack.append((end_label, cond_label))
            self.add_label(body_label)
            self.visit(node.stmt)
            self.add_label(cond_label)
            if node.cond:
                self.add_if(node.cond, body_label)
                self.add_goto(end_label)
            else:
                self.add_goto(body_label)
            self.add_label(end_label)
            self.loop_stack.pop()
        elif isinstance(node, c_ast.Break):
            if self.loop_stack:
                self.add_goto(self.loop_stack[-1][0])
        elif isinstance(node, c_ast.Continue):
            if self.loop_stack:
                self.add_goto(self.loop_stack[-1][1])
        elif isinstance(node, c_ast.Compound):
            if node.block_items:
                for item in node.block_items:
                    self.visit(item)
        elif isinstance(node, c_ast.Return):
            self.add_return(node.expr)
        elif isinstance(node, c_ast.Decl):
            if node.init:
                self.add_assignment(node.name, node.init, "=")
        elif isinstance(node, c_ast.DeclList):
            for decl in node.decls:
                self.visit(decl)


# ---------------------------------------------------------------------------
# Построение CFG из TAC
# ---------------------------------------------------------------------------

def build_cfg(tac, label_map):
    nodes = list(range(len(tac)))
    edges = []
    final_node = len(tac)

    for i, instr in enumerate(tac):
        if instr[0] == 'assign':
            edges.append((i, i + 1, f"{instr[2]} {instr[1]} ="))
        elif instr[0] == 'array_assign':
            edges.append((i, i + 1, f"{instr[2]} {instr[1][:-3]} []="))
        elif instr[0] == 'if':
            cond = instr[1]
            true_index = label_map[instr[2]]
            edges.append((i, true_index, cond))
            if i + 1 < len(tac):
                edges.append((i, i + 1, f"{cond} !"))
        elif instr[0] == 'goto':
            edges.append((i, label_map[instr[1]], "skip"))
        elif instr[0] == 'return':
            action = f"{instr[1]} return" if instr[1] else "return"
            edges.append((i, final_node, action))

    return nodes, edges, final_node


def optimize(nodes, edges, final_node):
    new_edges = []

    for e in edges:
        if e[2] == "skip" or "return" in e[2]:
            continue

        ends = [e[1]]
        push_forward = True
        while push_forward:
            push_forward = False
            new_ends = []
            for end in ends:
                tails = [e1[1] for e1 in edges
                         if e1[0] == end and (e1[2] == "skip" or "return" in e1[2])]
                if tails:
                    push_forward = True
                    new_ends += tails
                else:
                    new_ends.append(end)
            ends = new_ends

        for end in ends:
            new_edges.append((e[0], end, e[2]))

    new_nodes_set = set()
    for e in new_edges:
        new_nodes_set.add(e[0])
        new_nodes_set.add(e[1])
    new_nodes = list(new_nodes_set)

    nodes_to_delete = []
    buffer_nodes = [n for n in new_nodes
                    if n != 0 and n not in [e[1] for e in new_edges]]
    while buffer_nodes:
        nodes_to_delete += buffer_nodes
        buffer_nodes = [
            n for n in new_nodes
            if n != 0
            and n not in nodes_to_delete
            and not [e for e in new_edges if e[1] == n and e[0] not in nodes_to_delete]
        ]

    new_nodes = [n for n in new_nodes if n not in nodes_to_delete]
    new_edges = [e for e in new_edges if e[0] in new_nodes and e[1] in new_nodes]

    return new_nodes, new_edges, final_node


# ---------------------------------------------------------------------------
# RPN-метка → Action (ключевая новая функция)
# ---------------------------------------------------------------------------

def _label_to_action(label: str):
    """Преобразует RPN-метку ребра CFG в объект Action."""
    expr = parse_expr_from_rpn(label)
    if expr is None:
        return None

    if expr.type == ExprType.ASSIGN_EXPR:
        var = Variable()
        if expr.left.type == ExprType.VAR:
            var.type = VariableType.SCALAR_VAR
            var.name = expr.left.var_name
        elif expr.left.type == ExprType.ARRAY_INDEX:
            var.type = VariableType.ABSTRACT_ARR_ELEMENT
            var.name = expr.left.left.var_name
            var.index_expr = copy_node(expr.left.right)
        return create_assign_action(var, expr.right)
    else:
        return create_logic_action(expr)


# ---------------------------------------------------------------------------
# Публичные функции
# ---------------------------------------------------------------------------

def clear_code(code_text: str) -> str:
    code_text = re.sub(r'/\*[\w\W]*?\*/', '', code_text)
    code_text = re.sub(r'//.*', '', code_text)
    code_text = re.sub(r'^[ \t]*#(include|pragma|if|else|elif|endif|warning|error).*', '', code_text, flags=re.MULTILINE)
    code_text = re.sub(r'^[ \t]*#(define|ifdef|ifndef|elif|elifdef|elifndef)(.*\\\n)*.*', '', code_text, flags=re.MULTILINE)
    return code_text


def cpp_to_program_graph(
    cpp_code: str,
    func_name: str = 'main',
    initial_memory: Memory = None,
) -> ProgramGraph2:
    """
    Разбирает C/C++ код, строит граф программы и возвращает ProgramGraph2.

    Args:
        cpp_code:        исходный код (C/C++)
        func_name:       имя функции для анализа (по умолчанию 'main')
        initial_memory:  начальное состояние памяти (Memory); если None — пустая память

    Returns:
        ProgramGraph2 с заполненными рёбрами и terminal_loc
    """
    cleaned = clear_code(cpp_code)

    parser = c_parser.CParser()
    ast = parser.parse(cleaned)

    converter = TACConverter()
    if isinstance(ast, c_ast.FileAST):
        for ext in ast.ext:
            if isinstance(ext, c_ast.FuncDef) and ext.decl.name == func_name:
                converter.visit(ext.body)

    tac = converter.tac
    nodes, edges, final_node = build_cfg(tac, converter.label_map)
    nodes, edges, final_node = optimize(nodes, edges, final_node)

    if initial_memory is None:
        initial_memory = Memory()

    pg = ProgramGraph2(initial_memory=initial_memory, terminal_loc=final_node)

    for src, dst, label in edges:
        action = _label_to_action(label)
        if action is not None:
            pg.add_action_edge(src, dst, action)

    return pg


# ---------------------------------------------------------------------------
# Обратная совместимость: c_to_pg по-прежнему возвращает DOT-строку
# ---------------------------------------------------------------------------

def generate_dot(nodes, edges, final_node):
    dot = ["digraph PG {", "  node [shape=circle];",
           f"  q{final_node} [shape=doublecircle];"]
    for node in nodes:
        dot.append(f"  q{node};")
    dot.append(f"  q{final_node};")
    for src, dst, action in edges:
        dot.append(f'  q{src} -> q{dst} [label="{action}"];')
    dot.append("}")
    return "\n".join(dot)


def c_to_pg(c_code: str, func_name: str = 'main') -> str:
    """Оригинальная функция — возвращает DOT-строку."""
    cleaned = clear_code(c_code)
    parser = c_parser.CParser()
    ast = parser.parse(cleaned)
    converter = TACConverter()
    if isinstance(ast, c_ast.FileAST):
        for ext in ast.ext:
            if isinstance(ext, c_ast.FuncDef) and ext.decl.name == func_name:
                converter.visit(ext.body)
    tac = converter.tac
    nodes, edges, final_node = build_cfg(tac, converter.label_map)
    nodes, edges, final_node = optimize(nodes, edges, final_node)
    return generate_dot(nodes, edges, final_node)


# ---------------------------------------------------------------------------
# CLI (аналог оригинального __main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    code_file_path = sys.argv[1] if len(sys.argv) >= 2 else "file.c"
    func_name = sys.argv[2] if len(sys.argv) >= 3 else "main"
    save_pg_file_path = sys.argv[3] if len(sys.argv) >= 4 else "pg.dot"

    with open(code_file_path, "r") as f:
        c_code = f.read()

    pg = cpp_to_program_graph(c_code, func_name)
    with open(save_pg_file_path, "w") as f:
        f.write(pg.to_dot())
