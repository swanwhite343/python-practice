from __future__ import annotations

from typing import Annotated, Union
from pydantic import Field

from .configs import (
    ChainGeometryConfig,
    SquareGeometryConfig,
    HoneycombGeometryConfig,
    ABRingGeometryConfig,
)

GeometryConfig = Annotated[
    Union[
        ChainGeometryConfig,
        SquareGeometryConfig,
        HoneycombGeometryConfig,
        ABRingGeometryConfig,
    ],
    Field(discriminator="lattice"),
]