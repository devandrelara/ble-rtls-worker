from typing import Dict, Optional
from pydantic import BaseModel

class Scanner(BaseModel):
  name: str
  area: int
  x: float
  y: float

class ScannerList(BaseModel):
  __root__: Dict[str,Scanner]

class Area(BaseModel):
  id: int
  name: str
  floorplan: str
  width: float
  height: float

class Node(BaseModel):
  id: str
  mac_address: str
  description: Optional[str]

class Position(BaseModel):
  area: int
  node: int
  x: float
  y: float



