from __future__ import annotations
from typing import Dict, Set, Tuple
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.variable import Variable
from tracer.action import Action, ActionType
from tracer.action_sequence import ActionSequence


class PIDG:
    """Program Intermediate Dependence Graph"""
    def __init__(self):
        # edges[from_action][to_action] = Variable
        self.edges: Dict[int, Dict[int, Variable]] = {}
        # initial_variables[action_index] = set of Variables read from initial memory
        self.initial_variables: Dict[int, Set[Variable]] = {}
        self.action_sequence: ActionSequence = ActionSequence()


def match_two_pidgs(
    pidg1: PIDG, pidg2: PIDG
) -> Dict[int, Dict[int, float]]:
    heat_map: Dict[int, Dict[int, float]] = {}
    n1 = len(pidg1.action_sequence.action_seq)
    n2 = len(pidg2.action_sequence.action_seq)
    for i in range(n1):
        heat_map[i] = {}
        for j in range(n2):
            act1 = pidg1.action_sequence.action_seq[i]
            act2 = pidg2.action_sequence.action_seq[j]
            if act1.type != act2.type:
                heat_map[i][j] = 0.0
            else:
                score = 0.0
                if act1.type == ActionType.ASSIGN:
                    if act1.assigned_variable == act2.assigned_variable:
                        score += 0.25
                    if act1.changed_value == act2.changed_value:
                        score += 0.25
                    score += 0.5 * compare_pidg_nodes_by_read_variables(pidg1, i, pidg2, j)
                elif act1.type == ActionType.LOGIC:
                    score = compare_pidg_nodes_by_read_variables(pidg1, i, pidg2, j)
                heat_map[i][j] = score
    return heat_map


def compare_pidg_nodes_by_read_variables(
    pidg1: PIDG, node1: int, pidg2: PIDG, node2: int
) -> float:
    pidg1_edges: Dict[int, Variable] = pidg1.edges.get(node1, {})
    pidg2_edges: Dict[int, Variable] = pidg2.edges.get(node2, {})

    size = len(pidg1_edges)
    fully_matched = 0
    by_var_matched = 0

    for num1, var1 in pidg1_edges.items():
        matched = False
        effect_matched = False
        for num2, var2 in pidg2_edges.items():
            if var1 == var2:
                matched = True
            act1 = pidg1.action_sequence.action_seq[num1]
            act2 = pidg2.action_sequence.action_seq[num2]
            if act1.type == ActionType.ASSIGN and act2.type == ActionType.ASSIGN:
                effect_matched = (act1.changed_value == act2.changed_value)
            if matched:
                break
        if matched and effect_matched:
            fully_matched += 1
        elif matched:
            by_var_matched += 1

    init_size = len(pidg1.initial_variables.get(node1, set()))
    init_matched = 0
    if node1 in pidg1.initial_variables and node2 in pidg2.initial_variables:
        for v in pidg1.initial_variables[node1]:
            if v in pidg2.initial_variables[node2]:
                init_matched += 1

    sum_size = size + init_size
    if sum_size == 0:
        return 1.0
    if init_size > 0 and size > 0:
        return (0.6 * fully_matched / size
                + 0.4 * init_matched / init_size
                + 0.5 * by_var_matched / sum_size)
    elif init_size == 0 and size > 0:
        return fully_matched / size + 0.5 * by_var_matched / sum_size
    return 0.0
