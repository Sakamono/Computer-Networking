import socket
import _thread
import function
import sys

MAX = 65535
host_port = None
usage_message = 'Usage: $ python3 proxy.py -P <port_number>'
if len(sys.argv) > 2 and sys.argv[1] == '-P':
    try:
        host_port = int(sys.argv[2])
    except ValueError:
        print(usage_message)
        print("Invalid port number")
        quit()
else:
    print(usage_message)
    quit()

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host_ip, host_port))
s.listen()
print('Proxy server start in device {name}, listening {ip}:{port}'.format(name=host_name, ip=host_ip,
                                                                          port=host_port))


def handler(conn, addr):
    request_to_proxy = conn.recv(MAX)
    print('Server connected by', addr)
    data = function.proxy(request_to_proxy)
    conn.sendall(data)
    conn.close()


while True:
    _thread.start_new_thread(handler, s.accept())
