import socket
import threading
import json
import time

class NetworkCommunication:
    def __init__(self, port=5000, message_callback=None, connection_callback=None):
        self.port = port
        self.server_socket = None
        self.connections = {}  # {address: socket}
        self.server_thread = None
        self.running = False
        self.message_callback = message_callback
        self.connection_callback = connection_callback
        
    def start_server(self):
        """Start the server to listen for incoming connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.running = True
        self.server_thread = threading.Thread(target=self._accept_connections)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"Server started on port {self.port}")
        
    def _accept_connections(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address}")
                
                # Start a thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                # Store the connection
                self.connections[address] = client_socket
                
                # Notify about new connection
                if self.connection_callback:
                    self.connection_callback(address, True)
                    
            except Exception as e:
                if self.running:  # Only print error if we're supposed to be running
                    print(f"Error accepting connection: {e}")
                    
    def _handle_client(self, client_socket, address):
        """Handle communication with a connected client."""
        try:
            while self.running:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                # Process the received message
                try:
                    message = json.loads(data.decode('utf-8'))
                    print(f"Received from {address}: {message}")
                    
                    # Call the message callback
                    if self.message_callback:
                        self.message_callback(address, message)
                except json.JSONDecodeError:
                    print(f"Received invalid JSON from {address}")
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Clean up
            client_socket.close()
            if address in self.connections:
                del self.connections[address]
            
            # Notify about disconnection
            if self.connection_callback:
                self.connection_callback(address, False)
                
    def connect_to_peer(self, ip, port):
        """Connect to a peer on the network."""
        try:
            # Create a socket and connect
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((ip, port))
            address = (ip, port)
            
            # Store the connection
            self.connections[address] = peer_socket
            
            # Start a thread to handle this connection
            client_thread = threading.Thread(
                target=self._handle_client,
                args=(peer_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()
            
            # Notify about new connection
            if self.connection_callback:
                self.connection_callback(address, True)
                
            print(f"Connected to peer at {ip}:{port}")
            return True
            
        except Exception as e:
            print(f"Error connecting to peer at {ip}:{port}: {e}")
            return False
            
    def send_message(self, address, message):
        """Send a message to a specific peer."""
        if address in self.connections:
            try:
                # Convert message to JSON and send
                data = json.dumps(message).encode('utf-8')
                self.connections[address].sendall(data)
                return True
            except Exception as e:
                print(f"Error sending message to {address}: {e}")
                # Remove the broken connection
                self.connections[address].close()
                del self.connections[address]
                if self.connection_callback:
                    self.connection_callback(address, False)
                return False
        else:
            print(f"No connection to {address}")
            return False
            
    def broadcast_message(self, message):
        """Send a message to all connected peers."""
        disconnected = []
        for address, conn in list(self.connections.items()):
            try:
                data = json.dumps(message).encode('utf-8')
                conn.sendall(data)
            except Exception as e:
                print(f"Error broadcasting to {address}: {e}")
                disconnected.append(address)
                
        # Clean up disconnected peers
        for address in disconnected:
            if address in self.connections:
                self.connections[address].close()
                del self.connections[address]
                if self.connection_callback:
                    self.connection_callback(address, False)
                    
    def stop(self):
        """Stop the server and close all connections."""
        self.running = False
        
        # Close all client connections
        for address, conn in list(self.connections.items()):
            try:
                conn.close()
            except:
                pass
        self.connections.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            
        print("Network communication stopped")
