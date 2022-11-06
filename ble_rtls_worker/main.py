from cgitb import lookup
from typing import List
from pydantic import parse_obj_as
import paho.mqtt.client as mqtt
from ble_rtls_worker.client.api import get_scanners, get_areas, get_nodes, post_position
from ble_rtls_worker.schemas.api import Scanner, ScannerList, Position
from ble_rtls_worker.schemas.measures import NodeMeasuresQueue, RSSIMeasure, ScannerQueue
from ble_rtls_worker.logger import logger
from threading import Thread, main_thread
import time
from ble_rtls_worker.settings import MQTT_BROKER_HOST

from ble_rtls_worker.utils.positioning import calculate_position, distance_from_rssi

nodes_queue_list = [NodeMeasuresQueue(node_id=node.id,node_mac_address='5d:f2:07:b0:57:b8', measures_by_scanner=[]) for node in get_nodes()]

scanner_list = get_scanners()

def find_node_queue(nodes_queue_list: List[NodeMeasuresQueue],lookup_mac_address: str) -> NodeMeasuresQueue:
  for node_queue in nodes_queue_list:
    if node_queue.node_mac_address == lookup_mac_address: return node_queue
  return None 


def register_measure(measure: RSSIMeasure):
  node_queue = find_node_queue(nodes_queue_list,'5d:f2:07:b0:57:b8')
  scanner = parse_obj_as(Scanner,scanner_list.__root__[measure.scanner])
  if not node_queue:
    return
  else:
    node_queue.register_measure(measure,scanner)


    

def on_message_print(client, userdata, message):
    try:
      msg = message.payload.decode("utf-8")
      scanner_name = msg.split("&")[0].split("=")[1]
      node_mac_address = msg.split("&")[1].split("=")[1]
      rssi = int(msg.split("&")[2].split("=")[1])
      # distance = distance_from_rssi(rssi=rssi)
      # print(distance)
      time = float(msg.split("&")[3].split("=")[1])
    except Exception as e:
      logger.error(e)
      logger.error("Error parsing incoming mqtt incoming payload")
      return
    
    new_measure = RSSIMeasure(
      scanner=scanner_name,
      mac_address=node_mac_address,
      rssi=rssi,
      measure_time=time
    )
    register_measure(new_measure)



# subscribe.callback(on_message_print, "aoliveira/rtls", hostname="192.168.0.9")


class PositioningThread(Thread):
  def __init__(self):
    Thread.__init__(self)
  counter = 0
  def run(self):
    print("Started thread")
    while True:

      self.counter+=1

      for queue in nodes_queue_list:
        if queue.measures_by_scanner:
          top_measures = queue.find_top_measures()
          x,y = calculate_position(top_measures)
          position = Position(area=1,node=queue.node_id,x=x,y=y)
          post_position(position=position)

        

      if self.counter >20:
        self.counter =0
        for queue in nodes_queue_list:
          queue.clean_measures()
        
      time.sleep(1)
      

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("aoliveira/rtls")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message_print

client.connect(MQTT_BROKER_HOST, 1883, 60)
# client.loop_forever()
client.loop_start()
main_thread = PositioningThread()
main_thread.start()


