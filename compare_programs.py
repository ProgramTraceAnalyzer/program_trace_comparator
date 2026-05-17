"""
compare_programs.py

Свободная функция compare_programs() — сравнивает две C++ программы
по схожести трасс переменных.
"""
from __future__ import annotations

import copy
import sys
import os
from typing import List

from tracer.execution_fragment import ExecutionFragment
from similarity_matrix import build_similarity_matrix
from tracer.memory import Memory

from tracer.pg_builder import cpp_to_program_graph
from metrics import LCSStrategy
from similarity_matrix import build_similarity_matrix
from hungarian import hungarian_mapping

from mapping_agragation import aggregate_mappings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def compare_programs(
    cpp_code1: str,
    cpp_code2: str,
    func_name: str,
    memory,
    remove_death_actions: bool,
    strategy=None,
    nan_strategy: str = "drop",
    fill_value: int = 0,
    max_steps: int = 10000,
    **strategy_kwargs,
):
    """
    Сравнивает две C++ программы по схожести последовательностей значений
    переменных, полученных при исполнении.

    Args:
        cpp_code1:       исходный код первой программы
        cpp_code2:       исходный код второй программы
        func_name:       имя анализируемой функции (одинаковое для обеих программ)
        memory:          начальное состояние памяти (Memory); используется для обеих программ
        strategy:        экземпляр SequenceDistanceMeasureStrategy.
                         По умолчанию LCSStrategy().
        nan_strategy:    "drop" — удалить NaN, "fill" — заменить на fill_value
        fill_value:      значение для замены NaN при nan_strategy="fill"
        max_steps:       максимальное число шагов исполнения графа программы
        **strategy_kwargs: дополнительные параметры стратегии
                          (например, match_score=3 для SmithWatermanStrategy)

    Returns:
        pandas.DataFrame — матрица схожести переменных:
            индекс   = переменные первой программы,
            колонки  = переменные второй программы,
            значения = процент схожести [0.0, 100.0].
            :param remove_death_actions:
    """


    if strategy is None:
        strategy = LCSStrategy()

    # Исполняем обе программы с копиями памяти (чтобы не мутировать оригинал)
    mem1 = copy.deepcopy(memory)
    mem2 = copy.deepcopy(memory)

    pg1 = cpp_to_program_graph(cpp_code1, func_name=func_name)
    pg2 = cpp_to_program_graph(cpp_code2, func_name=func_name)

    ef1 = pg1.execute(_initial_memory=mem1, max_steps=max_steps)
    ef2 = pg2.execute(_initial_memory=mem2, max_steps=max_steps)

    return build_executions_similarity_matrix(ef1,ef2,remove_death_actions, strategy, nan_strategy, fill_value,  **strategy_kwargs)



def build_executions_similarity_matrix(ef1: ExecutionFragment, ef2: ExecutionFragment, except_var_names: list, remove_death_actions: bool, remove_stutter_steps: bool, strategy,
        nan_strategy,
        fill_value,
        **strategy_kwargs,):

    if remove_death_actions:
        # Убираем «мёртвые» присваивания
        ef1 = ef1.remove_unused_actions()
        ef2 = ef2.remove_unused_actions()

    # Получаем последовательности памяти → DataFrame
    df1 = ef1.state_sequence.get_memory_sequence().to_pd_dataframe()
    df1 = df1.drop(columns=except_var_names, errors="ignore")
    df2 = ef2.state_sequence.get_memory_sequence().to_pd_dataframe()
    df2 = df2.drop(columns=except_var_names, errors="ignore")

    return build_similarity_matrix(
        df1, df2,
        strategy=strategy,
        nan_strategy=nan_strategy,
        fill_value=fill_value,
        **strategy_kwargs,
    )

def build_program_matrix_list_on_test_list(cpp_code1: str,
    cpp_code2: str,
    except_var_names: list,
    func_name: str,
    test_list: List[Memory],
    remove_death_actions: bool,
    remove_stutter_steps: bool = False,
    strategy=None,
    nan_strategy: str = "drop",
    fill_value: int = 0,
    max_steps: int = 10000,
    **strategy_kwargs,
    ):

    matrix_list = []
    for test in test_list:
        if strategy is None:
            strategy = LCSStrategy()

        # Исполняем обе программы с копиями памяти (чтобы не мутировать оригинал)
        mem1 = copy.deepcopy(test)
        mem2 = copy.deepcopy(test)

        pg1 = cpp_to_program_graph(cpp_code1, func_name=func_name)
        pg2 = cpp_to_program_graph(cpp_code2, func_name=func_name)

        ef1 = pg1.execute(_initial_memory=mem1, max_steps=max_steps)
        ef2 = pg2.execute(_initial_memory=mem2, max_steps=max_steps)

        matrix = (build_executions_similarity_matrix(ef1, ef2, except_var_names, remove_death_actions, remove_stutter_steps, strategy, nan_strategy, fill_value,
                                                  **strategy_kwargs))
        matrix_list.append(matrix)

    return matrix_list

def mapping_by_matrix_list(matrix_list: list,
    treshold_mapping: float = 0.6,
    treshold_agragation: float = 0.6):

    mapping_list = []
    for matrix in matrix_list:
        print(matrix)
        mapping = hungarian_mapping(matrix, treshold_mapping)
        print(mapping)
        mapping_list.append(mapping)
    result_mapping = aggregate_mappings(mapping_list, treshold_agragation)
    return result_mapping



def compare_programs_on_test_list(cpp_code1: str,
    cpp_code2: str,
    except_var_names: list,
    func_name: str,
    test_list: List[Memory],
    remove_death_actions: bool,
    remove_stutter_steps: bool = False,
    treshold_mapping: float = 0.6,
    treshold_agragation: float = 0.6,
    strategy=None,
    nan_strategy: str = "drop",
    fill_value: int = 0,
    max_steps: int = 10000,
    **strategy_kwargs,):

    mapping_list = []

    for test in test_list:
        if strategy is None:
            strategy = LCSStrategy()

        # Исполняем обе программы с копиями памяти (чтобы не мутировать оригинал)
        mem1 = copy.deepcopy(test)
        mem2 = copy.deepcopy(test)

        pg1 = cpp_to_program_graph(cpp_code1, func_name=func_name)
        pg2 = cpp_to_program_graph(cpp_code2, func_name=func_name)

        ef1 = pg1.execute(_initial_memory=mem1, max_steps=max_steps)
        ef2 = pg2.execute(_initial_memory=mem2, max_steps=max_steps)

        matrix = (build_executions_similarity_matrix(ef1, ef2, except_var_names, remove_death_actions, remove_stutter_steps, strategy, nan_strategy, fill_value,
                                                  **strategy_kwargs))
        print(matrix)
        mapping = hungarian_mapping(matrix, treshold_mapping)
        print(mapping)
        mapping_list.append(mapping)
    result_mapping = aggregate_mappings(mapping_list,treshold_agragation)
    return result_mapping