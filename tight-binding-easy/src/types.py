from typing import Annotated
from pydantic import Field

NonNegInt = Annotated[int, Field(ge=0, strict=True)]

HashLength = Annotated[int, Field(ge=6, le=32, strict=True)]
Seed = Annotated[int, Field(ge=0, strict=True)]
LatticeSide = Annotated[int, Field(ge=3, strict=True)]
HoppingAmp = Annotated[float, Field(strict=True)]
OnsiteChem = Annotated[float, Field(strict=True)]
Temperature = Annotated[float, Field(ge=0, strict=True)]
LatticeCoord = Annotated[int, Field(ge=0, strict=True)]