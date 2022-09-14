from typing import List, Literal
from urllib.error import HTTPError
from ble_rtls_worker.client.exceptions import rtlsApiConnectionError, rtlsClientError
from ble_rtls_worker.schemas.api import Area, Position, Scanner, Node, ScannerList
from pydantic import BaseModel, parse_obj_as
import requests
from ble_rtls_worker.settings import API_BASE_URL

def get_nodes() -> List[Node]:
  return parse_obj_as(List[Node],_make_request('GET',f"{API_BASE_URL}/node"))

def get_scanners() -> ScannerList:
  return parse_obj_as(ScannerList,_make_request('GET',f"{API_BASE_URL}/scanner"))

def get_areas() -> List[Area]:
  return parse_obj_as(List[Area],_make_request('GET',f"{API_BASE_URL}/area"))

def post_position(position: Position) -> Position:
  headers = {'Content-Type': 'application/json','accept': 'application/json'}
  return parse_obj_as(Position,_make_request(
    method='POST',
    url=f"{API_BASE_URL}/position/",
    payload=position.dict(),
    headers=headers))
def _make_request(
  method:Literal['GET','POST'],
  url: str, 
  payload: BaseModel = None,
  headers: dict[str,str]=None) -> dict:

  headers = {**(headers if headers else {})}
  try:
    response = requests.request(
      method=method,
      url=url,
      headers=headers,
      json=payload if payload else None)
  except ConnectionError as connection_error:
    raise rtlsApiConnectionError(f"Could not connect to RTLS API. Error:{connection_error}")
  
  try:
    response.raise_for_status()
    return response.json()
  except HTTPError as client_error:
    raise rtlsClientError(f"Client error on request to RTLS API. Error: {client_error}")

