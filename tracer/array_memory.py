from __future__ import annotations
from typing import Dict, Set
from tracer.array_class import Array


class ArrayMemory:
    def __init__(self, array_values: Dict[str, Array] = None):
        self.array_values: Dict[str, Array] = array_values if array_values is not None else {}

    def get_submemory(self, variable_names: Set[str]) -> "ArrayMemory":
        values = {k: v for k, v in self.array_values.items() if k in variable_names}
        return ArrayMemory(values)

    def to_html(self) -> str:
        html = '<table style="margin: 0px; padding: 0px;" class="table">'
        for name, arr in self.array_values.items():
            html += (
                f'<tr><th style="margin: 0px; padding: 0px;">{name}</th>'
                f'<td style="margin: 0px; padding: 0px;">{arr.to_html()}</td></tr>'
            )
        html += "</table>"
        return html

    def to_json(self) -> str:
        parts = [f'"{k}":{v.to_json()}' for k, v in self.array_values.items()]
        return "{" + ",".join(parts) + "}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArrayMemory):
            return NotImplemented
        return self.array_values == other.array_values
