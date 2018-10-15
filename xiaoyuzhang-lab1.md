### Step1

1. What version of HTTP is the server running?

   HTTP/1.1

2. How is the beginning of the content sent by the server recognized by the client?

   After options, there is a blank line, then the content body. When client see an empty line, client know the
   following is content.

3. How does the client know what type of content is returned?

   ```Content-Type: text/html``` This declears that the response is html text

### Step2

1. What is the format of a header line? Give a simple description that fits the headers you see.

   ```<key>: <value>``` pairs of the response parameters, split by ```\r\n```

2. What headers are used to indicate the kind and length of content that is returned in a response?

   ```
   Content-Type: image/jpeg\r\n
   Content-Length: 121054\r\n
   ```

   ​	

### Step4

1. What is the name of the header the browser sends to let the server work out whether to send fresh
   content?

   ```If-Modified-Since```

2. Where exactly does the timestamp value carried by the header come from?

   ```Last-Modified```

   ​	



