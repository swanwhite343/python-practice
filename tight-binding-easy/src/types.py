from typing import Annotated
from pydantic import Field

HashLength = Annotated[int, Field(ge=6, le=32)]
Seed = Annotated[int, Field(ge=0)]
LatticeSide = Annotated[int, Field(ge=3)]
Temperature = Annotated[float, Field(ge=0)]