import math
from typing import List

from ble_rtls_worker.schemas.measures import ScannerQueue

MEASURED_BEACON_POWER = -54 # rssi at 1 meter away
DISTANCE_CONSTANT = 0.89976
POWER_CONSTANT = 7.7095

def distance_from_rssi(rssi):
  if(rssi==0):
    return -1

  ratio = rssi/MEASURED_BEACON_POWER
  if(ratio<1):
    return math.pow(ratio,10)
  else:
    return DISTANCE_CONSTANT * math.pow(ratio,POWER_CONSTANT) + 0.111


def one_scanner_position(
  top_scanner_rssi: int,
  top_scanner_x: float, 
  top_scanner_y: float,
):
  top_scanner_distance = distance_from_rssi(top_scanner_rssi)
  return top_scanner_x,top_scanner_y

def two_scanner_position(
  top_scanner_rssi: int,
  top_scanner_x: float, 
  top_scanner_y: float,
  mid_scanner_rssi: int,
  mid_scanner_x: float, 
  mid_scanner_y: float):
  return 0,0

def three_scanner_position(top_scanner_rssi: int,
                           top_scanner_x: float, 
                           top_scanner_y: float,
                           mid_scanner_rssi: int,
                           mid_scanner_x: float, 
                           mid_scanner_y: float,
                           bot_scanner_rssi: int,
                           bot_scanner_x: float, 
                           bot_scanner_y: float):
  """
  This trilateration is based on the distance equations
  (x - x¹)² + (y - y¹)² = (r¹)² 
  (x - x²)² + (y - y²)² = (r²)² 
  (x - x³)² + (y - y³)² = (r³)² 
  """
  top_scanner_distance = distance_from_rssi(top_scanner_rssi)
  mid_scanner_distance = distance_from_rssi(mid_scanner_rssi)
  bot_scanner_distance = distance_from_rssi(bot_scanner_rssi)
  A = (-2 * top_scanner_x) + (2 * mid_scanner_x)
  B = (-2 * top_scanner_y) + (2 * mid_scanner_y)
  C = math.pow(top_scanner_distance,2) - math.pow(mid_scanner_distance,2) \
     - math.pow(top_scanner_x,2) + math.pow(mid_scanner_x,2) \
      - math.pow(top_scanner_y,2) + math.pow(mid_scanner_y,2)
  D = (-2 * mid_scanner_x) + (2 * bot_scanner_x)
  E = (-2 * mid_scanner_y) + (2 * bot_scanner_y)
  F = math.pow(mid_scanner_distance,2) - math.pow(bot_scanner_distance,2) \
     - math.pow(mid_scanner_x,2) + math.pow(bot_scanner_x,2) \
      - math.pow(mid_scanner_y,2) + math.pow(bot_scanner_y,2)

  x = ((C*E)-(F*B))/((E*A)-(B*D))
  y = ((C*D)-(A*F))/((B*D)-(A*E))
                           
  return x,y

def calculate_position(top_measures: List[ScannerQueue]):
  if len(top_measures)==3:
    x,y = three_scanner_position(
      top_measures[0].get_avg_measure(),
      top_measures[0].x_pos,
      top_measures[0].y_pos,
      top_measures[1].get_avg_measure(),
      top_measures[1].x_pos,
      top_measures[1].y_pos,
      top_measures[2].get_avg_measure(),
      top_measures[2].x_pos,
      top_measures[2].y_pos
    )
  if len(top_measures)==2:
    x,y = two_scanner_position(
      top_measures[0].get_avg_measure(),
      top_measures[0].x_pos,
      top_measures[0].y_pos,
      top_measures[1].get_avg_measure(),
      top_measures[1].x_pos,
      top_measures[1].y_pos
    )
  if len(top_measures)==1:
    x,y = one_scanner_position(
      top_measures[0].get_avg_measure(),
      top_measures[0].x_pos,
      top_measures[0].y_pos
    )

  return x,y
  
"""
TODOS:
- implement positioning for 2 points
- for 1 point scanning, implement scanner distance as measure error
- get areas from the scanners to define the area to save the position
- handle top measures from different areas
- limit the position to room space (not nullable)
- test Kalman Filter over Average measures
"""

