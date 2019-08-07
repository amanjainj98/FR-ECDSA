#!/usr/bin/python

import socket
import base64

import cryptography.hazmat.backends.openssl.backend as OSSL
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

PRIVKEY = "private.pem"
PRIVKEY1 = "new.pem"
PORT = 12351

def get_priv(fname=PRIVKEY1):
    with open(fname) as f:
        priv_pem = f.read()
        priv = load_pem_private_key(priv_pem, password=None, backend=OSSL)
    return priv

class Server:
    def __init__(self, pkey):
        self._priv = pkey

    def sign (self, data):
        ''' Sign provided data and return encoded signature '''
        sig = self._priv.sign(data, ec.ECDSA(hashes.SHA256()))
        sigenc = base64.b64encode(sig)
        return sigenc

    def start (self, port=PORT):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(('localhost', PORT))
        self._sock.listen(1)

        while True:
            conn, addr = self._sock.accept()
            data = conn.recv(4096)

            # Handle exit condition
            if data == "QUIT":
                conn.close()
                break
            
            sig = self.sign(data)
            conn.send(sig)
            conn.close()

        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

def main():
    priv = get_priv()
    s = Server(priv)
    s.start()

if __name__ == "__main__":
    main()
