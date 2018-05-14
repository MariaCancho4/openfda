import http.client
import json

limit_of_drugs = 20

print("Pulling {} Drugs Information from https://api.fda.gov".format(limit_of_drugs))

headers = {'User-Agent': 'http-client'}
conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/label.json?limit={}".format(limit_of_drugs), None, headers)
response = conn.getresponse()

print("Status:",response.status, response.reason)
print('fetching 10 drugs with levels please wait...')
raw_text = response.read().decode("utf-8")
conn.close()


data = json.loads(raw_text)
drugs = data['results']

limit = 10
# write it to html
with open('index.html', 'w') as f:
    f.write("<html><head> <title>Practice 1</title></head> <body> <ul>")
    for drug in drugs:
        if limit:
            try:
                f.write('<li>')
                f.write(str(drug['openfda']['generic_name'][0]))
                f.write('</li>')
                limit -= 1
            except KeyError:
                pass



    f.write("</body></html>")


import socket

IP = "127.0.0.1"
PORT = 9096
MAX_OPEN_REQUESTS = 5


def client_handler(clientsocket):

    # decode request message from the socket's byte stream 
    request_msg = clientsocket.recv(1024).decode("utf-8")

    lines = request_msg.replace("\r", "").split("\n")

    request_line = lines[0]
    request = request_line.split(" ")
    req_cmd = request[0]
    path = request[1]

    print("")
    print("REQUEST: ")
    print("Command: {}".format(req_cmd))
    print("Path: {}".format(path))
    print("")

    # Read the html page to send, depending on the path
    if path:
        filename = "index.html"
        print("File to send: {}".format(filename))

        with open(filename, "r") as f:
            content = f.read()

    # Build the HTTP response message. It has the following lines
    # Status line
    status_line = "HTTP/1.1 200 OK\n"

    # Header
    header = "Content-Type: text/html\n"
    header += "Content-Length: {}\n".format(len(str.encode(content)))

    # Message
    response_msg = str.encode(status_line + header + "\n" + content)
    clientsocket.send(response_msg)


# -----------------------------------------------
# ------ The server start its execution here
# -----------------------------------------------

# Create the server socket, for receiving the connections
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    # Give the socket an IP address and a Port
    serversocket.bind((IP, PORT))

    # This is a server socket. It should be configured for listening
    serversocket.listen(MAX_OPEN_REQUESTS)

    # Server main loop. The server is doing nothing but listening for the
    # incoming connections from the clientes. When there is a new connection,
    # the systems gives the server the new client socket for communicating
    # with the client
    while True:
        # When there is an incoming client, their IP address and socket
        # are returned
        print("Waiting for clients at IP: {}, Port: {}".format(IP, PORT))
        (clientsocket, address) = serversocket.accept()

        print("  Client request received. IP: {}".format(address))
        print("Server socket: {}".format(serversocket))
        print("Client socket: {}".format(clientsocket))
        client_handler(clientsocket)
        clientsocket.close()

except socket.error:
    print("Socket error. Problems with the PORT {}".format(PORT))
    print("Launch it again in another port (and check the IP)")





# #https://api.fda.gov/drug/label.json
# PORT= 8001
# class testHTTPRequestHandler(http.server.BaseHTTPRequest.Handler):
#     def do_GET(self):
#          self.send_response(200)

#          self.send.header( Content-type, text/html)
#          self.end_headers()

# Handler= http.server.SimpleHTTPRequestHandler
# Handler= testHTTPRequestHandler

# httpd= socketserver.TCPServer(("", Port), Handler)
# print("serving at port", PORT)
# httpd.serve_forever()
