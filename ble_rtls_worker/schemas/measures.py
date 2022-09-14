from typing import List
from pydantic import BaseModel
import heapq

from ble_rtls_worker.schemas.api import Scanner

class RSSIMeasure(BaseModel):
  scanner: str
  mac_address: str
  rssi: int
  measure_time: float

class ScannerQueue(BaseModel):
  scanner: str
  x_pos: float
  y_pos: float
  rssi_measures: List[int]

  def register_rssi_measure(self, measure: int):
    self.rssi_measures.append(measure)
  
  def get_latest_measure(self)->int:
    return self.rssi_measures[len(self.rssi_measures)-1]

  def get_avg_measure(self)->int:
    return sum(self.rssi_measures)/len(self.rssi_measures)
  def clean_measures(self):
    self.rssi_measures = []

class NodeMeasuresQueue(BaseModel):
  node_id: int
  node_mac_address: str
  measures_by_scanner: List[ScannerQueue]

  def register_measure(self,measure: RSSIMeasure, scanner: Scanner)->None:
    for scanner_queue in self.measures_by_scanner:
      if scanner_queue.scanner == measure.scanner:
        scanner_queue.register_rssi_measure(measure.rssi)
        return
    self.measures_by_scanner.append(
        ScannerQueue(
          scanner=measure.scanner,
          rssi_measures=[measure.rssi],
          x_pos=scanner.x,
          y_pos=scanner.y
        )
      )
  
  def clean_measures(self)->None:
    self.measures_by_scanner = []

  def find_top_measures(self)-> List[ScannerQueue]:
    n_value = 3 if len(self.measures_by_scanner)>2 else len(self.measures_by_scanner)
    return heapq.nlargest(n_value, self.measures_by_scanner,key= lambda a: a.get_avg_measure())


# node_queue = NodeMeasuresQueue(node_mac_address='5f:6c:bc:e5:49:cc', 
#                               measures_by_scanner=[
#                                 ScannerQueue(scanner="rpiscanner00",rssi_measures=[-70,-70,-70]),
#                                 ScannerQueue(scanner="rpiscanner01",rssi_measures=[-79,-70,-60]),
#                                 ScannerQueue(scanner="rpiscanner02",rssi_measures=[-70,-70,-70]),
#                                 ScannerQueue(scanner="rpiscanner03",rssi_measures=[-70,-70,-60]),
#                                 ScannerQueue(scanner="rpiscanner04",rssi_measures=[-70,-70,-60]),
#                               ])



# largests = node_queue.find_top_measures()

# print(largests)  




