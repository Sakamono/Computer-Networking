import socket
import _thread
import calculator

host_port = 8181
bufsize = 16

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host_ip, host_port))
s.listen()
print('Server started. Waiting for connection...')


def handler(conn, addr):
  print('Server connected by', addr)
  while True:
    exp_generator = calculator.zfp_decode(conn, bufsize)
    res = [str(calculator.calc(exp)) for exp in exp_generator]
    if res == []:
      conn.close()
      print("Connection closed by client.")
      break
    else:
      print("Result send: {0}, waiting for next request.".format(res))
      conn.sendall(calculator.zfp_encode(res))

while True:
  _thread.start_new_thread(handler, s.accept())

