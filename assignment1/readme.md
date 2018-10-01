#Usage

## Start server
`$ python3 tcp-calculator-server.py`

## Write expressions
Write in `expressions.txt`, one expression per line. Empty line will be ignored.

Example:

```
1+2
4+8
1*(2+3)
(((4)))
```


## Start Client
`$ python3 tcp-calculator-client.py`

for example expressions, the client will receive and print

```
1+2 ==> 3
4+8 ==> 12
1*(2+3) ==> 5
(((4))) ==> 4
```