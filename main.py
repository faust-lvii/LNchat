import threading
import time
import sys
import socket
import json
from network_discovery import NetworkDiscovery
from network_communication import NetworkCommunication
from chat_ui import ChatUI

class LNChat:
    def __init__(self, port=5000):
        self.port = port
        self.running = False
        
        # Initialize network discovery
        self.discovery = NetworkDiscovery(port=port)
        self.discovery.add_listener(self._on_service_change)
        
        # Initialize network communication
        self.communication = NetworkCommunication(
            port=port,
            message_callback=self._on_message_received,
            connection_callback=self._on_connection_change
        )
        
        # Initialize UI
        self.ui = ChatUI(
            send_callback=self._on_send_message,
            connect_callback=self._on_connect_to_peer
        )
        
        # Keep track of connection attempts to avoid duplicates
        self.connection_attempts = set()
        
    def _on_service_change(self, service_info, added):
        """Handle service discovery events."""
        ip, port = service_info
        
        if added:
            print(f"Discovered service: {ip}:{port}")
            
            # Attempt to connect to the discovered service
            # Use a thread to avoid blocking
            if (ip, port) not in self.connection_attempts:
                self.connection_attempts.add((ip, port))
                threading.Thread(
                    target=self._connect_to_service,
                    args=(ip, port)
                ).start()
        else:
            print(f"Service removed: {ip}:{port}")
            
    def _connect_to_service(self, ip, port):
        """Connect to a discovered service."""
        # Wait a bit to avoid connection race conditions
        time.sleep(1)
        
        # Attempt to connect
        success = self.communication.connect_to_peer(ip, port)
        if success:
            print(f"Successfully connected to {ip}:{port}")
        else:
            # Remove from connection attempts to allow retry
            self.connection_attempts.discard((ip, port))
            
    def _on_message_received(self, address, message):
        """Handle received messages."""
        if message.get("type") == "message":
            content = message.get("content", "")
            sender_name = self.ui.peers.get(address, f"Peer ({address[0]}:{address[1]})")
            
            # Add message to UI
            self.ui.add_message(sender_name, content)
            
    def _on_connection_change(self, address, connected):
        """Handle connection changes."""
        if connected:
            # Add peer to UI
            self.ui.add_peer(address)
        else:
            # Remove peer from UI
            self.ui.remove_peer(address)
            
            # Allow reconnection attempts
            self.connection_attempts.discard(address)
            
    def _on_send_message(self, address, message):
        """Handle sending a message from the UI."""
        return self.communication.send_message(address, message)
        
    def _on_connect_to_peer(self, ip, port):
        """Handle manual connection to a peer."""
        if (ip, port) not in self.connection_attempts:
            self.connection_attempts.add((ip, port))
            return self.communication.connect_to_peer(ip, port)
        return False
        
    def start(self):
        """Start the chat application."""
        self.running = True
        
        # Start network communication
        self.communication.start_server()
        
        # Start network discovery
        self.discovery.register_service()
        self.discovery.start_discovery()
        
        # Start UI in the main thread
        try:
            self.ui.start()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            
    def stop(self):
        """Stop the chat application."""
        if not self.running:
            return
            
        self.running = False
        
        # Stop network discovery
        self.discovery.stop()
        
        # Stop network communication
        self.communication.stop()
        
        # Stop UI
        self.ui.stop()
        
if __name__ == "__main__":
    # Default port
    port = 5000
    
    # Check if port is provided as command line argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port {port}.")
    
    # Create and start the chat application
    chat = LNChat(port=port)
    chat.start()
