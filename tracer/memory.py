from __future__ import annotations
from typing import Set
from tracer.scalar_memory import ScalarMemory
from tracer.array_memory import ArrayMemory


class Memory:
    def __init__(self, scalar_memory: ScalarMemory = None, array_memory: ArrayMemory = None):
        self.scalar_memory: ScalarMemory = scalar_memory if scalar_memory is not None else ScalarMemory()
        self.array_memory: ArrayMemory = array_memory if array_memory is not None else ArrayMemory()

    def get_submemory(self, variable_names: Set[str]) -> "Memory":
        return Memory(
            self.scalar_memory.get_submemory(variable_names),
            self.array_memory.get_submemory(variable_names),
        )

    def to_html(self) -> str:
        html = (
            '<table style="margin: 0px; padding: 0px;" class="table">'
            "<tr><th>Scalars</th><th>Arrays</th></tr> "
            f"<tr><td>{self.scalar_memory.to_html()}</td>"
            f"<td>{self.array_memory.to_html()}</td></tr> "
            "</table>"
        )
        return html

    def to_json(self) -> str:
        return (
            '{"scalar_memory":'
            + self.scalar_memory.to_json()
            + ',"array_memory":'
            + self.array_memory.to_json()
            + "}"
        )

    def get_scalar_variable_value(self, var_name: str) -> int:
        return self.scalar_memory.var_values[var_name]

    def get_array_element_value(self, arr_name: str, index: int) -> int:
        return self.array_memory.array_values[arr_name].index_values[index]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Memory):
            return NotImplemented
        return self.array_memory == other.array_memory and self.scalar_memory == other.scalar_memory
