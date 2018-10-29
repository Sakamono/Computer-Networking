import udt
import threading
import config
from function import *

# Go-Back-N reliable transport protocol.
class GoBackN:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  def __init__(self, local_ip, local_port,
               remote_ip, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_ip, local_port,
                                          remote_ip, remote_port, self)
    self.msg_handler = msg_handler
    self.pipe = []
    self.next_seq = 0
    self.receiver_expected_seq = 0
    self.base = 0
    self.p = threading.Thread(target=self.timer_event, daemon=True)
    self.start_timer_event = threading.Event()
    self.reset_timer_event = threading.Event()
    self.stop_timer_event = threading.Event()
    self.sender_lock = threading.Lock()
    self.terminate_event = threading.Event()
    self.lock = threading.Lock()
    self.queue_lock = threading.Lock()

  def timer_event(self):
        def __loop():
            # wait for stop timer or terminate, if timeout and timer was not reset, then resend.
            while True:
                if self.terminate_event.is_set() or self.stop_timer_event.wait(config.TIMEOUT_MSEC / 1000):
                    self.stop_timer_event.clear()
                    return
                else:
                    if self.reset_timer_event.is_set():
                        self.reset_timer_event.clear()
                        continue
                    with self.queue_lock:
                        for pkt, _, _ in self.pipe:
                            self.network_layer.send(pkt)

        while True:
            if self.terminate_event.is_set():
                return
            if len(self.pipe) > 0 or self.start_timer_event.wait():
                __loop()
                self.start_timer_event.clear()

  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
    # lazy start
      with self.lock:
          if not self.p.is_alive():
              self.p.start()

      if self.next_seq - self.base == config.WINDOW_SIZE:  # pipeline full
          return False

      # a packet and corresponding event, for blocking until this packet is acked and return
      pkt, event = make_pkt(DATA_TYPE, self.next_seq, msg), threading.Event()
      with self.queue_lock:
          self.pipe.append((pkt, event, self.next_seq))
      self.network_layer.send(pkt)

      with self.lock:  # if queue is not empty, start timer
          self.next_seq += 1
          if self.next_seq - self.base == 1:
              self.start_timer_event.set()
      return event.wait()

  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    msg = self.network_layer.recv()
    # TODO: impl protocol to handle arrived packet from network layer.
    # call self.msg_handler() to deliver to application layer.
    msg = unpacket(msg)
    if msg is None:  # corrupted package, ignore.
        return
    type_number, seq, data = msg

    if type_number == ACK_TYPE:  # sender get ack
        # all packets with smaller seq number are received by receiver. set to allow sender return true
        with self.queue_lock:
            for _, event, _ in [t for t in self.pipe if t[2] <= seq]:
                event.set()
            self.pipe = [t for t in self.pipe if t[2] > seq]

        # ready to send next packet
        self.base = seq + 1

        # if no more packet in queue, stop timer, otherwise reset timer
        if self.base == self.next_seq:
            self.stop_timer_event.set()
        else:
            self.reset_timer_event.set()
    elif type_number == DATA_TYPE and seq == self.receiver_expected_seq:  # receiver get data with expected data
        # print(data.decode())
        self.msg_handler(data.decode())
        self.network_layer.send(make_pkt(ACK_TYPE, self.receiver_expected_seq))
        self.receiver_expected_seq += 1  # expecting next packet
    else:
        if type_number == DATA_TYPE and self.receiver_expected_seq > 0:  # receiver get duplicate data, ack latest received data again.
            self.network_layer.send(make_pkt(ACK_TYPE, self.receiver_expected_seq - 1))


  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    self.terminate_event.set()
    self.network_layer.shutdown()
    self.terminate_event.set()
