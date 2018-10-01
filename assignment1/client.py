import socket
import calculator

server_port = 8181
bufsize = 16


server_name = socket.gethostname()
print('Hostname: ', server_name)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_name, server_port))
print('Connected to server ', server_name)

with open("expressions.txt", "r") as f:
  expressions = list(filter(lambda expr : len(expr) > 0, f.read().split("\n")))
  s.sendall(calculator.zfp_encode(expressions))
  for pair in zip(expressions, calculator.zfp_decode(s, bufsize)):
    print("{0} ==> {1}".format(pair[0], pair[1]))
  s.close()
