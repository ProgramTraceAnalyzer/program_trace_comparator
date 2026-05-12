from __future__ import annotations
from typing import Dict, Set


class ScalarMemory:
    def __init__(self, var_values: Dict[str, int] = None):
        self.var_values: Dict[str, int] = var_values if var_values is not None else {}

    def get_submemory(self, variable_names: Set[str]) -> "ScalarMemory":
        values = {k: v for k, v in self.var_values.items() if k in variable_names}
        return ScalarMemory(values)

    def to_html(self) -> str:
        html = '<table style="margin: 0px; padding: 0px;" class="table">'
        tr1 = ""
        tr2 = ""
        for name, value in self.var_values.items():
            tr1 += f'<th style="margin: 0px; padding: 0px;">{name}</th>'
            tr2 += f'<td style="margin: 0px; padding: 0px;">{value}</td>'
        html += f"<tr>{tr1}</tr><tr>{tr2}</tr></table>"
        return html

    def to_json(self) -> str:
        parts = [f'"{k}":{v}' for k, v in self.var_values.items()]
        return "{" + ",".join(parts) + "}"

    def equals_to(self, other: "ScalarMemory") -> bool:
        return self.var_values == other.var_values

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScalarMemory):
            return NotImplemented
        return self.equals_to(other)
