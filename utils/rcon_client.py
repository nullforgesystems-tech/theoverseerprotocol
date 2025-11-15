"""
The Overseer - ASA Automation Framework
© 2025 NullForge Systems™
All Rights Reserved.
"""

import socket
import struct
import time


class RCON_Client:
    """ The beginnings of a reusable RCON Class that will be compatible with various games"""

    #RCON Packet types
    SERVERDATA_AUTH = 3
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0

    def __init__(self, host, port, password, timeout=5):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.socket = None
        self.request_id = 0
        self.authed = False

    #Connection handeling
    def connect(self):
        #Connect to RCON server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)

        try:
            self.socket.connect((self.host, self.port))
            self.authed = self.authenticate()
        
        except Exception as e:
            raise ConnectionError(f"Failed to connect to RCON Server {e}")

        if not self.authed:
            raise PermissionError("Invalid RCON Password. Authentication failed")
        
    
    def disconnect(self):
        #Gracefully disconnect
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.authed = False

    #--------------------Authentication-------------------------------------------------------------

    def authenticate(self):
        #Authenticate using RCON password
        response = self._send_packet(self.SERVERDATA_AUTH, self.password)

        #valid authentication returns request ID in response
        return response == self.request_id
    

    #--------------------Send RCON Commands---------------------------------------------------------

    def send(self, command):
        #Send RCON command and return server response, reconnect if needed

        if not self.authed:
            self.connect()

        try:
            result = self._send_packet(self.SERVERDATA_EXECCOMMAND, command)
            return result
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            #Attempt reconnect once
            time.sleep(0.2)
            self.connect()
            return self._send_packet(self.SERVERDATA_EXECCOMMAND, command)
        
    #--------------------Packet Handeling-----------------------------------------------------------

    def _send_packet(self, packet_type, body):
        #Build and send a properly formatted RCON packet
        self.request_id += 1

        #packet layout : (int32 request_id, int 32 type, body, null, null)
        payload = struct.pack("<ii", self.request_id, packet_type)+ body.encode("utf-8") + b"\x00\x00"

        packet = struct.pack("<i", len(payload)) + payload
        self.socket.sendall(packet)

        return self._read_respones()
    
    def _read_response(self):
        #Reads RCON response packet returns the request_id OR the response string depending on the packet
        
        # Response size
        response_size_raw = self.socket.recv(4)

        if not response_size_raw:
            return ""

        (response_size, ) = struct.unpack("<i", response_size_raw)

        #Full packet read
        response_raw = self.socket.recv(response_size)
        if len(response_raw) < 8:
            return ""
        response_id, response_type = struct.unpack("<i", response_raw[:8])
        response_body = response_raw[8:-2].decode("utf-8", errors="ignore")

        #if auth response return request ID
        if response_type == self.SERVERDATA_AUTH:
            return response_id
        return response_body

        