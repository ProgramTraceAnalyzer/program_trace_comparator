"""
metrics.py — стратегии измерения схожести последовательностей.

Иерархия:
    SequenceDistanceMeasureStrategy   (абстрактный базовый класс)
    ├── SmithWatermanStrategy
    ├── LCSStrategy
    └── DTWStrategy

Каждая стратегия реализует:
    do(seq1, seq2, **kwargs) -> SequenceAlignmentResult

SequenceAlignmentResult содержит:
    .similarity  float   — процентная схожесть [0, 100]
    .path        list    — путь выравнивания [(i,j), ...]
    .matrix      ndarray — матрица DP / score-матрица
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Результат
# ---------------------------------------------------------------------------

@dataclass
class SequenceAlignmentResult:
    similarity: float                          # процент схожести [0, 100]
    path: List[Tuple[int, int]] = field(default_factory=list)
    matrix: NDArray = field(default_factory=lambda: np.empty((0, 0)))


# ---------------------------------------------------------------------------
# Абстрактная стратегия
# ---------------------------------------------------------------------------

class SequenceDistanceMeasureStrategy(ABC):
    """
    Абстрактный базовый класс для метрик схожести последовательностей.

    Подкласс обязан реализовать метод `do`.
    """

    @abstractmethod
    def do(
        self,
        seq1: NDArray[np.int64],
        seq2: NDArray[np.int64],
        **kwargs,
    ) -> SequenceAlignmentResult:
        """
        Сравнивает две последовательности.

        Args:
            seq1:    первая последовательность (numpy int64 array)
            seq2:    вторая последовательность (numpy int64 array)
            **kwargs: дополнительные параметры метрики

        Returns:
            SequenceAlignmentResult
        """


# ---------------------------------------------------------------------------
# Smith-Waterman (локальное выравнивание)
# ---------------------------------------------------------------------------

class SmithWatermanStrategy(SequenceDistanceMeasureStrategy):
    """
    Локальное выравнивание последовательностей алгоритмом Смита–Уотермана.

    Параметры do():
        match_score      (int, default=2)   — очки за совпадение
        mismatch_penalty (int, default=-1)  — штраф за несовпадение
        gap_penalty      (int, default=-1)  — штраф за пропуск
    """

    def do(
        self,
        seq1: NDArray[np.int64],
        seq2: NDArray[np.int64],
        match_score: int = 2,
        mismatch_penalty: int = -1,
        gap_penalty: int = -1,
        **kwargs,
    ) -> SequenceAlignmentResult:
        s1 = seq1.tolist()
        s2 = seq2.tolist()
        n, m = len(s1), len(s2)

        score_matrix = [[0] * (m + 1) for _ in range(n + 1)]
        traceback    = [[0] * (m + 1) for _ in range(n + 1)]
        max_score, max_i, max_j = 0, 0, 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                diag = score_matrix[i-1][j-1] + (match_score if s1[i-1] == s2[j-1] else mismatch_penalty)
                up   = score_matrix[i-1][j] + gap_penalty
                left = score_matrix[i][j-1] + gap_penalty
                best = max(0, diag, up, left)
                score_matrix[i][j] = best

                if best == 0:       traceback[i][j] = 0
                elif best == diag:  traceback[i][j] = 1
                elif best == up:    traceback[i][j] = 2
                else:               traceback[i][j] = 3

                if best > max_score:
                    max_score, max_i, max_j = best, i, j

        # Обратный ход
        path = []
        i, j = max_i, max_j
        while i > 0 and j > 0 and score_matrix[i][j] > 0:
            tb = traceback[i][j]
            if tb == 1:
                path.append((i - 1, j - 1)); i -= 1; j -= 1
            elif tb == 2:
                path.append((i - 1, j));     i -= 1
            elif tb == 3:
                path.append((i, j - 1));     j -= 1
            else:
                break
        path.reverse()

        # Схожесть (глобальная: совпадения / max длина)
        matches = sum(1 for pi, pj in path if s1[pi] == s2[pj])
        total   = max(n, m) or 1
        similarity = matches / total

        matrix = np.array(score_matrix, dtype=float)
        return SequenceAlignmentResult(similarity=similarity, path=path, matrix=matrix)


# ---------------------------------------------------------------------------
# LCS — Longest Common Subsequence
# ---------------------------------------------------------------------------

class LCSStrategy(SequenceDistanceMeasureStrategy):
    """
    Схожесть на основе длиннейшей общей подпоследовательности (LCS).

    Параметры do(): нет дополнительных.
    """

    def do(
        self,
        seq1: NDArray[np.int64],
        seq2: NDArray[np.int64],
        **kwargs,
    ) -> SequenceAlignmentResult:
        s1 = seq1.tolist()
        s2 = seq2.tolist()
        n, m = len(s1), len(s2)

        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        # Обратный ход
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            if s1[i-1] == s2[j-1]:
                path.append((i - 1, j - 1)); i -= 1; j -= 1
            elif dp[i-1][j] >= dp[i][j-1]:
                i -= 1
            else:
                j -= 1
        path.reverse()

        matches = sum(1 for pi, pj in path if s1[pi] == s2[pj])
        total   = max(n, m) or 1
        similarity = matches / total

        matrix = np.array(dp, dtype=float)
        return SequenceAlignmentResult(similarity=similarity, path=path, matrix=matrix)


# ---------------------------------------------------------------------------
# DTW — Dynamic Time Warping
# ---------------------------------------------------------------------------

class DTWStrategy(SequenceDistanceMeasureStrategy):
    """
    Динамическая трансформация времени (DTW).

    Параметры do(): нет дополнительных.
    """

    def do(
        self,
        seq1: NDArray[np.int64],
        seq2: NDArray[np.int64],
        **kwargs,
    ) -> SequenceAlignmentResult:
        s1 = seq1.astype(int).tolist()
        s2 = seq2.astype(int).tolist()
        n, m = len(s1), len(s2)

        dtw_matrix = np.zeros((n + 1, m + 1), dtype=float)
        dtw_matrix[1:, 0] = np.inf
        dtw_matrix[0, 1:] = np.inf

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = abs(s1[i-1] - s2[j-1])
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i-1, j],
                    dtw_matrix[i,   j-1],
                    dtw_matrix[i-1, j-1],
                )

        # Обратный ход
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            mv = min(dtw_matrix[i-1, j], dtw_matrix[i, j-1], dtw_matrix[i-1, j-1])
            if mv == dtw_matrix[i-1, j-1]:
                i -= 1; j -= 1
            elif mv == dtw_matrix[i-1, j]:
                i -= 1
            else:
                j -= 1
        path.reverse()

        # Нормализованная схожесть
        total_cost = dtw_matrix[n, m]
        max_diff   = max(
            abs(max(s1, default=0) - min(s2, default=0)),
            abs(max(s2, default=0) - min(s1, default=0)),
            1,
        )
        max_cost   = (n + m) * max_diff
        similarity = max(0.0, 1.0 - total_cost / max_cost ) if max_cost > 0 else 1.0

        return SequenceAlignmentResult(similarity=similarity, path=path, matrix=dtw_matrix)
