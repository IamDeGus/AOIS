from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GluePair:
    left: str
    right: str
    merged: str | None


@dataclass(frozen=True)
class GlueStage:
    iteration: int
    pairs: tuple[GluePair, ...]


@dataclass(frozen=True)
class CoverageRow:
    implicant: str
    covers: tuple[int, ...]


@dataclass(frozen=True)
class CoverageTable:
    columns: tuple[int, ...]
    rows: tuple[CoverageRow, ...]


@dataclass(frozen=True)
class MinimizedForm:
    expression: str
    selected_implicants: tuple[str, ...]
    glue_stages: tuple[GlueStage, ...]
    coverage_table: CoverageTable | None


@dataclass(frozen=True)
class MinimizationResult:
    method: str
    dnf: MinimizedForm
    cnf: MinimizedForm
    notes: tuple[str, ...] = ()
