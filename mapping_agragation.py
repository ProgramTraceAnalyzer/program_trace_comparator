"""mapping_agragation.py

Агрегация результатов венгерского алгоритма на множестве тестов.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Any


def aggregate_mappings(
    hungarian_results: List[Dict[str, Any]],
    threshold: float = 0.6,
) -> Dict[str, str]:
    """Агрегирует несколько результатов венгерского алгоритма в итоговый mapping.

    Args:
        hungarian_results: список результатов `hungarian_mapping`,
            каждый элемент — dict вида:
            {
                "mapping": {row_name: col_name, ...},
                ...
            }
        threshold: порог доли (0..1). Если для строки лучшая колонка
            набирает долю < threshold, итогового сопоставления для этой строки
            не делаем.

            Например, если:
                - 43 % случаев: a -> w,
                - 57 % случаев: a -> h,
            и threshold = 0.6, то a ни с кем не сопоставляем.

    Returns:
        Итоговый mapping: {row_name: col_name, ...}.
    """

    # row -> col -> count
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for res in hungarian_results:
        mapping = res.get("mapping", {}) or {}
        for row, col in mapping.items():
            counts[row][col] += 1

    aggregated: Dict[str, str] = {}

    for row, col_counts in counts.items():
        total = sum(col_counts.values())
        if total == 0:
            continue

        # Находим колонку с максимальным числом совпадений
        best_col, best_count = max(col_counts.items(), key=lambda kv: kv[1])
        freq = best_count / total

        if freq >= threshold:
            aggregated[row] = best_col
        # иначе — оставляем строку без сопоставления

    return aggregated


if __name__ == "__main__":  # небольшой самотест
    # Пример: a -> w (3 раза), a -> h (4 раза)
    results = []
    for _ in range(3):
        results.append({"mapping": {"a": "w"}})
    for _ in range(4):
        results.append({"mapping": {"a": "h"}})

    print("threshold=0.5:", aggregate_mappings(results, threshold=0.5))
    print("threshold=0.6:", aggregate_mappings(results, threshold=0.6))
