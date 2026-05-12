from __future__ import annotations
from typing import List, Set
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.memory import Memory


class MemorySequence:
    def __init__(self, memory_seq: List[Memory] = None):
        self.memory_seq: List[Memory] = memory_seq if memory_seq is not None else []

    def get_submemory_sequence(self, variables: Set[str]) -> "MemorySequence":
        res = MemorySequence()
        for mem in self.memory_seq:
            res.memory_seq.append(mem.get_submemory(variables))
        return res

    def get_without_stutter_steps(self) -> "MemorySequence":
        res = MemorySequence()
        res.memory_seq.append(self.memory_seq[0])
        for mem in self.memory_seq:
            if mem != res.memory_seq[-1]:
                res.memory_seq.append(mem)
        return res

    def to_html(self) -> str:
        html = '<table class="table table-striped">'
        for num, mem in enumerate(self.memory_seq):
            html += f"<tr><th>{num}</th><td>{mem.to_html()}</td></tr>"
        html += "</table>"
        return html

    def to_pd_dataframe(self):
        """
        Преобразует последовательность памяти в pandas DataFrame.

        - Скалярные переменные → колонки с именем переменной.
        - Элементы массивов → колонки вида arr[0], arr[1], ...
        - Отсутствующие значения → pd.NA (столбцы имеют тип Int64 — nullable integer).
        """
        import pandas as pd

        rows = []
        for mem in self.memory_seq:
            row = {}
            # скалярные переменные
            for name, val in mem.scalar_memory.var_values.items():
                row[name] = val
            # массивы — разворачиваем в скаляры
            for arr_name, arr in mem.array_memory.array_values.items():
                for idx in range(arr.size):
                    col = f"{arr_name}[{idx}]"
                    if idx in arr.index_values:
                        row[col] = arr.index_values[idx]
                    # иначе — ключ просто отсутствует → станет pd.NA
            rows.append(row)

        df = pd.DataFrame(rows)

        # Приводим все столбцы к nullable integer (Int64), чтобы NaN оставался
        # целочисленным типом, а не float
        for col in df.columns:
            df[col] = df[col].astype("Int64")

        return df
