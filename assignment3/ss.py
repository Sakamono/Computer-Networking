import udt
import threading
import config
from function import *


# Stop-And-Wait reliable transport protocol.
class StopAndWait:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  def __init__(self, local_ip, local_port, 
               remote_ip, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_ip, local_port,
                                          remote_ip, remote_port, self)
    self.msg_handler = msg_handler
    self.state = 0
    self.lock = threading.Lock()
    self.event = None

  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
      self.event, pkt = threading.Event(), make_pkt(DATA_TYPE, self.state, msg)
      self.network_layer.send(pkt)
      while True:
              # wait until event is set by handler, resend if timeout
          if self.event.wait(config.TIMEOUT_MSEC / 1000):
              with self.lock:
                  self.state = (self.state + 1) % 2
              return True
          else:
              self.network_layer.send(pkt)

  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
      msg = self.network_layer.recv()
    # TODO: impl protocol to handle arrived packet from network layer.
    # call self.msg_handler() to deliver to application layer.
      msg = unpacket(msg)
      if msg is None:
          return
      type_number, seq, data = msg
      if type_number == ACK_TYPE and seq == self.state:  # correct ack
          self.event.set()
      elif type_number == DATA_TYPE and seq == self.state:  # receiver get data
          self.msg_handler(data.decode())
          self.network_layer.send(make_pkt(ACK_TYPE, self.state))
          self.state = (self.state + 1) % 2
      else:
          if type_number == DATA_TYPE:  # bad data, ack previous data.
              self.network_layer.send(make_pkt(ACK_TYPE, (self.state + 1) % 2))

  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    self.network_layer.shutdown()
