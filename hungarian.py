from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def hungarian_mapping(
    similarity_df: pd.DataFrame,
    threshold: float,
    unmatched_value: float = -1e9,
) -> Dict[str, Any]:
    """Венгерский алгоритм для матрицы схожести в виде pandas.DataFrame.

    Args:
        similarity_df: DataFrame, где индекс — имена строк (например, переменные
            первой программы), столбцы — имена столбцов (переменные второй
            программы), значения — схожесть в процентах (0..100).
        threshold:     минимально допустимая схожесть; пары ниже порога запрещены.
        unmatched_value: очень маленькое значение, используемое как стоимость
            для запрещённых пар и паддинга до квадратной матрицы.

    Returns:
        Словарь:
        {
            "mapping": {row_name: col_name, ...},
            "pairs": [
                {"row": row_name, "col": col_name, "score": float}, ...
            ],
            "total_score": float,
            "unmatched_rows": [..],
            "unused_cols": [..],
        }
    """

    # Имена строк и столбцов
    row_names = list(similarity_df.index.astype(str))
    col_names = list(similarity_df.columns.astype(str))

    n_rows = len(row_names)
    n_cols = len(col_names)
    size = max(n_rows, n_cols)

    # Приводим к numpy-массиву и обрабатываем NaN
    values = similarity_df.to_numpy(dtype=float)

    # Строим квадратную матрицу стоимости для венгерского алгоритма
    score_matrix = np.full((size, size), unmatched_value, dtype=float)

    for i in range(n_rows):
        for j in range(n_cols):
            val = values[i, j]
            if np.isnan(val) or val < threshold:
                score_matrix[i, j] = unmatched_value
            else:
                score_matrix[i, j] = val

    # Запускаем венгерский алгоритм на матрице стоимости (максимизация схожести)
    row_ind, col_ind = linear_sum_assignment(score_matrix, maximize=True)

    mapping: Dict[str, str] = {}
    pairs = []
    matched_rows = set()
    matched_cols = set()
    total_score = 0.0

    for i, j in zip(row_ind, col_ind):
        if i >= n_rows or j >= n_cols:
            # Ячейки паддинга (не соответствуют реальным строкам/столбцам)
            continue

        score = score_matrix[i, j]
        if score < threshold:
            # Пара ниже порога — считаем несопоставленной
            continue

        row_name = row_names[i]
        col_name = col_names[j]

        mapping[row_name] = col_name
        pairs.append({
            "row": row_name,
            "col": col_name,
            "score": float(score),
        })
        matched_rows.add(row_name)
        matched_cols.add(col_name)
        total_score += float(score)

    unmatched_rows = [r for r in row_names if r not in matched_rows]
    unused_cols = [c for c in col_names if c not in matched_cols]

    pairs_sorted = sorted(pairs, key=lambda x: x["score"], reverse=True)

    return {
        "mapping": mapping,
        "pairs": pairs_sorted,
        "total_score": total_score,
        "unmatched_rows": unmatched_rows,
        "unused_cols": unused_cols,
    }
