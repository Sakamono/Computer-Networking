# zfp = zhifeng's protocol

# given a connection, keep looping to read given size.
def recv_buffered(conn, target_byte_size, bufsize):
    paylaod = b''
    while target_byte_size > 0:
        size = min([target_byte_size, bufsize])
        raw_byte = conn.recv(size)
        if not raw_byte:
            return None
        paylaod += raw_byte
        target_byte_size -= len(raw_byte)
    return paylaod


# encode a list of expressions string
def zfp_encode(exprs_list):
    encode_single_item = lambda expr: len(expr).to_bytes(2, 'big') + str.encode(expr)
    return len(exprs_list).to_bytes(2, 'big') + b''.join([encode_single_item(e) for e in exprs_list])


# decode from a byte string to a list of expressions string
def zfp_decode(conn, bufsize):
    exprs_number_byte = recv_buffered(conn, 2, bufsize)
    if exprs_number_byte is None:
        return None
    for i in range(int.from_bytes(exprs_number_byte, 'big')):
        expr_size_remainder = int.from_bytes(recv_buffered(conn, 2, bufsize), 'big')
        payload = recv_buffered(conn, expr_size_remainder, bufsize)
        yield payload.decode()


# calculator.
def calc(e):
    def scan_outside_parentheses(expr, ops):
        po = 0
        res = -1
        for i, c, in enumerate(expr):
            if c == "(":
                po += 1
            elif c == ")":
                po -= 1
            if c in ops and po == 0:
                res = i
        return res

    e = "".join(e.split(" "))
    try:
        return int(e)
    except ValueError:
        if scan_outside_parentheses(e, "+-*/") == -1:
            return calc(e[1: -1])
        else:
            p1, p2 = scan_outside_parentheses(e, "+-"), scan_outside_parentheses(e, "*/")
            if p1 != -1:
                return int(calc(e[:p1]) + calc(e[p1 + 1:]) if e[p1] == "+" else calc(e[:p1]) - calc(e[p1 + 1:]))
            else:
                return int(calc(e[:p2]) * calc(e[p2 + 1:]) if e[p2] == "*" else calc(e[:p2]) / calc(e[p2 + 1:]))
