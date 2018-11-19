import os.path
import socket
import table
import threading
import util
import time

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000


def _ToPort(router_id):
    return _BASE_ID + router_id


def _ToRouterId(port):
    return port - _BASE_ID


class Router:
    def __init__(self, config_filename):
        # ForwardingTable has 3 columns (DestinationId,NextHop,Cost). It's
        # threadsafe.
        self._forwarding_table = table.ForwardingTable()
        # Config file has router_id, neighbors, and link cost to reach
        # them.
        self._config_filename = config_filename
        self._router_id = None
        # Socket used to send/recv update messages (using UDP).
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._config_updater = None
        self.neighbor_dvs = {}  # neighbor id : {des : cost}
        self.dv = {}  # {neighbor_id : cost}
        self.lock = threading.Lock()
        self.report_count = 0

    def start(self):
        # Start a periodic closure to update config.
        self._config_updater = util.PeriodicClosure(
            self.load_config, _CONFIG_UPDATE_INTERVAL_SEC)
        self._config_updater.start()
        while True:
            byte_fw, (_, port) = self._socket.recvfrom(_MAX_UPDATE_MSG_SIZE)
            with self.lock:
                prev_ss, prev_dv, prev_ndv = self._forwarding_table.snapshot(), dict(self.dv), dict(self.neighbor_dvs)
                # save them for comparing with new

                self.neighbor_dvs[_ToRouterId(port)] = _decode_forwarding_table_to_graph(byte_fw)  # get neighbor's dv
                self.calculate_forwarding_table()  # do Bellman-Ford algorithm
                self.send_to_neighbors()  # send new forwarding table to neighbors
                self.printState(prev_ss, prev_dv, prev_ndv)  # print printState

    def stop(self):
        if self._config_updater:
            self._config_updater.stop()
        self._socket.close()

    def load_config(self):
        assert os.path.isfile(self._config_filename)
        with open(self._config_filename, 'r') as f:
            prev_ss, prev_dv, prev_ndv = self._forwarding_table.snapshot(), dict(self.dv), dict(self.neighbor_dvs)
            # save them for comparing with new
            # Only set router_id when first initialize.
            router_id = int(f.readline().strip())
            if not self._router_id:
                self._socket.bind(('localhost', _ToPort(router_id)))
                self._router_id = router_id
            with self.lock:
                self.dv = {int(v.strip().split(",")[0]): int(v.strip().split(",")[1])
                           for v in f.read().split("\n") if len(v) > 0}  # {neighbor_id : cost}
                self.calculate_forwarding_table()  # do Bellman-Ford algorithm
                self.printState(prev_ss, prev_dv, prev_ndv)  # print printState
                self.send_to_neighbors()  # send new forwarding table to neighbors

    def send_to_neighbors(self):
        for neighbor_id in self.dv:
            self._socket.sendto(_encode_forwarding_table_to_byte(self._forwarding_table),
                                ('localhost', _ToPort(neighbor_id)))
# Using Bellman_Ford Algorithm to update forwarding table
    def calculate_forwarding_table(self):
        # graph: {des_router_id , total cost from here to des}
        graph, next_hops = {}, {}
        graph[self._router_id] = 0  # no cost on self
        next_hops[self._router_id] = self._router_id

        for neighbor_id, cost in self.dv.items():
            graph[neighbor_id] = cost
            next_hops[neighbor_id] = neighbor_id

        for neighbor_id, n_dv in self.neighbor_dvs.items():
            for des, neighbor_to_des_cost in n_dv.items():
                # update when find a new des is reachable via neighbor, or find lower cost via some neighbor
                if (des not in graph) or graph[des] > neighbor_to_des_cost + graph[neighbor_id]:
                    next_hops[des] = neighbor_id
                    graph[des] = neighbor_to_des_cost + graph[neighbor_id]

        # no need to put self on forwarding table
        graph.pop(self._router_id)
        next_hops.pop(self._router_id)

        self._forwarding_table.reset(turn_graph_and_next_hops_to_snapshot(graph, next_hops))

# Output the updated information of every state
    def printState(self, prev_ss, prev_dv, prev_neighbor_dvs):
        dv_change, ndv_change, snap_change = self.dv != prev_dv, \
                                             self.neighbor_dvs != prev_neighbor_dvs, \
                                             set(self._forwarding_table.snapshot()) != set(prev_ss)

        any_changes = dv_change or ndv_change or snap_change
        if any_changes:
            print("Router #", self._router_id, end = " ")
            print("State #", self.report_count, end = " ")
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) 
            self.report_count += 1

        msg = "forwarding table has changed." if snap_change else "forwarding table hasn't changed."
        if snap_change and not ndv_change:
            print("Received new distance vector and", msg)

        if ndv_change:
            print("Received neighbor's new distance vector and", msg)

        if snap_change:
            print("Sent updated forwarding table to neighbors:")
            print(self._forwarding_table.__str__())
            
        if any_changes:
            print("\n")

# turn snapshot to graph
def turn_snapshot_to_graph_and_next_hops(snap):
    # snapshot -> {des : cost}, {des : next_hops}
    return {v[0]: v[2] for v in snap}, {v[0]: v[1] for v in snap}

# turn graph to snapshot
def turn_graph_and_next_hops_to_snapshot(graph, next_hops):
    assert (graph.keys() == next_hops.keys())
    return [(v, next_hops[v], graph[v]) for v in graph]

# decode forwaring table to graph
def _decode_forwarding_table_to_graph(byte_msg):
    count, payload = int.from_bytes(byte_msg[:2], 'big'), byte_msg[2:]
    if count == 0 or count % 2 != 0:
        raise Exception("encoding error")
    chunks = [payload[i:i + 4] for i in range(0, 2 * count, 4)]
    return {int.from_bytes(c[:2], 'big'): int.from_bytes(c[2:], 'big') for c in chunks}

# encode forwaring table to byte
def _encode_forwarding_table_to_byte(forward_table):
    return b''.join(
        [(2 * forward_table.size()).to_bytes(2, byteorder='big')] +
        [v[0].to_bytes(2, 'big') + v[2].to_bytes(2, 'big') for v
         in forward_table.snapshot()])
