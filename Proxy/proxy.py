#!/usr/bin/env python3
import sys
import hashlib
import os
from socket import socket

USER_AGENT = "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0\r\n"
ACCEPT_HDR = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
CONNECTION_HDR = "Connection: close\r\n"
PROXY_CONNECTION_HDR = "Proxy-Connection: close\r\n"

# A buffer size.  Use when buffers have sizes.  Recommended over reading entire
# files or responses into a single bytes object, which may not be particularly
# good when I'm trying to listen to di.fm using the proxy.
BUFSIZ = 4096

# Class used to store a parsed URI with a default port number of 80
class URIContent:
    def __init__(self):
        self.host = ""
        self.path = ""
        self.port = 80
        self.fullPath = ""

def pe(*args, **kwargs):
    """Print to standard error.

    Nothing earth-shattering here, just saves typing.  Use exactly the same as
    you would the print() function.
    """
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)

def establishPortNumber():
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
                pe("Invalid port number")
                sys.exit(1)
    else:
        port = 8000 
    return port

def connectProxy():
    while True:
        clientConnection, clientAddress = proxyServer.accept()
        print(f"Accepted connection from{clientAddress}\r\n")
        handleAndSendRequest(clientConnection)
        clientConnection.close()

def handleAndSendRequest(clientConnection: socket ):
    linesOfInput = readEntireRequestAndSplit(clientConnection)
    parsedUri = parseUri(linesOfInput[0])
    cacheResult = checkCacheAndReturnCachedIfPresent(parsedUri.fullPath)
    if cacheResult:
        clientConnection.send(cacheResult)
    else:
        wasHostMentioned, pairs = readKeyValuePairs(linesOfInput)
        newRequest = formNewRequest(wasHostMentioned, pairs, parsedUri)
        response = sendMessageToServer(newRequest, parsedUri, clientConnection)
        cacheUrl(parsedUri.fullPath, response)
        clientConnection.send(response)

def readEntireRequestAndSplit(clientConnection: socket) -> list[str]:
    try:
        totalOutput = ""
        while True:
            totalOutput += clientConnection.recv(BUFSIZ).decode()
            print("INPUT: "+totalOutput)
            if "\r\n\r\n" in totalOutput or "\n\n" in totalOutput:
                break
        linesOfInput = totalOutput.strip().split('\r\n')
        return linesOfInput
    except:
        print("Request inputted incorrectly")
        clientConnection.close()
        sys.exit()

def parseUri(firstLine :str) -> URIContent:
    #Will provide the Method, Path, and the Version
    fullUri = firstLine.strip().split()
    fullPath = fullUri[1]

    if fullPath.find("http://") != -1:
        uri = URIContent()
        pathIndex = fullPath.find("/", 7)
        
        if ":" in fullPath[7:pathIndex]:
            portIndex = 7 + fullPath[7:pathIndex].find(":")
            uri.host = fullPath[7:portIndex]
            uri.port = int(fullPath[(1 + portIndex):pathIndex])
        else:
            uri.host = fullPath[7:pathIndex]
            uri.port = 80
        uri.path = fullPath[pathIndex:]
        uri.fullPath = fullPath
        return uri
    pe("The path could not be parsed")

def readKeyValuePairs(linesOfInput : list) -> (bool, str):
    hostMentioned = False
    data = ""
    for index in range(1, len(linesOfInput)):
        data += linesOfInput[index] + "\r\n"
        if "Host" in linesOfInput[index]:
            hostMentioned = True
    return hostMentioned, data

def formNewRequest(hostMentioned :bool, data :str, parsedUri :URIContent) -> str:
    newRequest = f"GET {parsedUri.path} HTTP/1.0\r\n"
    if not hostMentioned:
        newRequest += f"Host:{parsedUri.host}\r\n"
    newRequest += data
    if "User-Agent" not in data:
        newRequest += USER_AGENT
    if "Accept" not in data:
        newRequest += ACCEPT_HDR
    newRequest += CONNECTION_HDR
    if "Proxy-Connection" not in data:
        newRequest += PROXY_CONNECTION_HDR
    newRequest += "\r\n"
    return newRequest

def sendMessageToServer(request :str, parsedUri :URIContent, clientConnection: socket) -> bytes:

    try:
        server = socket()
        server.connect((parsedUri.host, parsedUri.port))
        server.send(request.encode())
        response = b""
        while True:
            chunk = server.recv(BUFSIZ)
            if not chunk:
                break
            response += chunk
        clientConnection.send(response)
        server.close()
        return response
    except:
        pe("Error connecting to the server")
        clientConnection.close()
        sys.exit()

def cachefile(url):
    """Return a specific filename to use for caching the given URL.

    Please use this to generate cache filenames, passing it the full URL as
    given in the client request.  (This will help me write tests for grading.)
    """
    return 'cache/' + hashlib.sha256(url).hexdigest()

def cacheUrl(url :str, response :bytes):

    fileName = cachefile(url.encode())
    if not os.path.exists("cache"):
        os.mkdir("cache")
    with open(fileName, 'wb') as file:
        file.write(response)

def checkCacheAndReturnCachedIfPresent(FullPath :str) -> bytes:
    fileName = cachefile(FullPath.encode())
    if os.path.exists(fileName):
            with open(fileName, 'rb') as file:
                content = file.readlines()
                return b''.join(content)
    return b""           

if __name__=="__main__":
    HOST = "localhost"
    PORT = establishPortNumber()
    proxyServer = socket()

    try:
        proxyServer.bind((HOST, PORT))
    except:
        print("This port is already taken or is in use")
        sys.exit()

    print(f"Proxy server is listening on {HOST}:{PORT}")
    proxyServer.listen(1)

    connectProxy()