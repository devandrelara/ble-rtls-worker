import math
from typing import List

from ble_rtls_worker.schemas.measures import ScannerQueue

MEASURED_BEACON_POWER = -50 # rssi at 1 meter away
DISTANCE_CONSTANT = 0.89976
POWER_CONSTANT = 7.7095

distance_counter = 0
rssi_distances = []
def distance_from_rssi(rssi):
  global distance_counter
  global rssi_distances
  if(rssi==0):
    return -1
  if distance_counter>=100:
    # print(f"Medições:{str(distance_counter)},RSSI Médio: {sum(rssi_distances)/len(rssi_distances)}")
    
    # print(MEASURED_BEACON_POWER)
    ratio = (sum(rssi_distances)/len(rssi_distances))/MEASURED_BEACON_POWER
    # print(ratio)
    if(ratio<1):
      distance= math.pow(ratio,10)
    else:
      distance= DISTANCE_CONSTANT * math.pow(ratio,POWER_CONSTANT) + 0.111
    # print(f"Medições:{str(distance_counter)}, RSSI Médio: {sum(rssi_distances)/len(rssi_distances)}, Distancia Estimada: {distance}")
    distance_counter=0
    rssi_distances=[]
  distance_counter+=1
  rssi_distances.append(rssi)
  # print(rssi_distances)
  
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
  top_scanner_distance = distance_from_rssi(top_scanner_rssi)
  return top_scanner_x,top_scanner_y

def three_scanner_position(top_scanner_rssi: int,
                           top_scanner_x: float, 
                           top_scanner_y: float,
                           top_scanner: str,
                           mid_scanner_rssi: int,
                           mid_scanner_x: float, 
                           mid_scanner_y: float,
                           mid_scanner: str,
                           bot_scanner_rssi: int,
                           bot_scanner_x: float, 
                           bot_scanner_y: float,
                           bot_scanner: str,):


  distancia12 = math.sqrt(math.pow(top_scanner_x-mid_scanner_x,2)+math.pow(top_scanner_y-mid_scanner_y,2));
  distancia13 = math.sqrt(math.pow(top_scanner_x-bot_scanner_x,2)+math.pow(top_scanner_y-bot_scanner_y,2));
  diferença_medida_maior_medio = top_scanner_rssi-mid_scanner_rssi
  diferença_medida_maior_menor = top_scanner_rssi-bot_scanner_rssi

  peso_distancia_maior_medio = 0.5
  peso_raio_medio = 0.5
  peso_distancia_maior_menor = 0.5
  peso_raio_menor = 0.5

  coeficiente_raio_maior_imediato = 0.02
  coeficiente_raio_maior_perto = 0.08
  media_coeficiente_imediatio = 0.05
  media_coeficiente_perto = 0.03




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

  # print(f"""
  # Maior Sinal: {top_scanner} Sinal Medido: {top_scanner_rssi} Distancia Estimada: {top_scanner_distance} 
  # Segundo Sinal: {mid_scanner} Sinal Medido: {mid_scanner_rssi} Distancia Estimada: {mid_scanner_distance} 
  # Terceiro Sinal: {bot_scanner} Sinal Medido: {bot_scanner_rssi} Distancia Estimada: {bot_scanner_distance}
  # Posição Estimada: {x},{y}
  # """)
  if x<0: x=0.1
  if x>3: x=3
  if y>3: y=3
  if y<0: y=0.1  
  print(f'({top_scanner_x}, {top_scanner_y}) & {round(top_scanner_distance,3)} & ({mid_scanner_x}, {mid_scanner_y}) & {round(mid_scanner_distance,3)} & ({bot_scanner_x}, {bot_scanner_y}) & {round(bot_scanner_distance,3)} & ({round(x,3)}, {round(y,2)}) & (2.5, 2.70) & {round(distance_two_points(x,y,2.5,2.7),3)}')
              
  return x,y

def calculate_position(top_measures: List[ScannerQueue]):
  if len(top_measures)==3:
    x,y = three_scanner_position(
      top_measures[0].get_avg_measure(),
      top_measures[0].x_pos,
      top_measures[0].y_pos,
      top_measures[0].scanner,
      top_measures[1].get_avg_measure(),
      top_measures[1].x_pos,
      top_measures[1].y_pos,
      top_measures[1].scanner,
      top_measures[2].get_avg_measure(),
      top_measures[2].x_pos,
      top_measures[2].y_pos,
      top_measures[2].scanner,
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
def distance_two_points(ax,ay,bx,by):
  return math.sqrt(pow((bx-ax),2)+pow((by-ay),2))
