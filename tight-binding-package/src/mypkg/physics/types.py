from __future__ import annotations

from typing import Literal, Tuple, List

BasisAxis = Literal["orb", "spin"]  #"nambu"
ComplexPair = Tuple[float, float]      # (re, im)
PairRow = List[ComplexPair]           # one row