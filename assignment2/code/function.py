import socket
from datetime import datetime


def log(message):
    with open('log.txt', 'a') as f:
        f.write(message + "\n")


def recv_all(conn, bufsize=1024):
    res = b''
    temp = conn.recv(bufsize)
    while len(temp) > 0:
        res += temp
        temp = conn.recv(bufsize)
    return res


def construct_request(method, path, version, options, body):
    req = b''
    req += b' '.join((method, path, version)) + b'\r\n'
    req += b'\r\n'.join([key + b': ' + options[key] for key in options])
    req += b'\r\n'
    req += b''.join(body)
    req += b'\r\n'
    return req


def get_content_delimiter(content_byte):
    first_line = content_byte.split(b'\n')[0]
    if first_line[-1] == 13:  # ascii code for \r
        return b'\r\n'
    else:
        return b'\n'


def proxy(request_byte):
    content = request_byte.split(get_content_delimiter(request_byte))
    seg = content.index(b'')
    request_type, path, http_version = content[0].split(b' ')

    if request_type != b'GET':
        return http_version + b' 400 Bad Request'

    d = b': '
    options = {lines.split(d, 1)[0]: lines.split(d, 1)[1]
               for lines in content[1: seg] if len(lines.split(d, 1)) > 1}
    body = content[seg + 1:]
    options[b'Connection'] = b'close'

    new_request = construct_request(request_type, path, http_version, options, body)
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((options[b'Host'], 80))
    conn.sendall(new_request)
    response = recv_all(conn)
    conn.close()

    log(path.decode('ascii') + " " + str(datetime.now()))
    return response
