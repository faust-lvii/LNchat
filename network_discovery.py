import socket
import threading
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
import time
import uuid

class NetworkDiscovery:
    def __init__(self, service_name="_lnchat._tcp.local.", port=5000):
        self.zeroconf = Zeroconf()
        self.service_name = service_name
        self.port = port
        self.discovered_services = {}
        self.listeners = []
        self.local_ip = self._get_local_ip()
        self.unique_id = str(uuid.uuid4())
        self.browser = None
        self.info = None
        
    def _get_local_ip(self):
        """Get the local IP address of this machine."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
        
    def register_service(self):
        """Register this service on the network."""
        self.info = ServiceInfo(
            self.service_name,
            f"LNChat-{self.unique_id}.{self.service_name}",
            addresses=[socket.inet_aton(self.local_ip)],
            port=self.port,
            properties={'id': self.unique_id}
        )
        self.zeroconf.register_service(self.info)
        print(f"Service registered: {self.local_ip}:{self.port}")
        
    def add_listener(self, callback):
        """Add a listener for service discovery events."""
        self.listeners.append(callback)
        
    def remove_listener(self, callback):
        """Remove a listener for service discovery events."""
        if callback in self.listeners:
            self.listeners.remove(callback)
            
    def notify_listeners(self, service_info, added=True):
        """Notify all listeners of a service change."""
        for listener in self.listeners:
            listener(service_info, added)
            
    class ServiceListener:
        """Listener for zeroconf service events."""
        def __init__(self, discovery):
            self.discovery = discovery
            
        def add_service(self, zc, type_, name):
            info = zc.get_service_info(type_, name)
            if info:
                service_id = info.properties.get(b'id', b'').decode('utf-8')
                # Don't add our own service
                if service_id != self.discovery.unique_id:
                    ip = socket.inet_ntoa(info.addresses[0])
                    port = info.port
                    self.discovery.discovered_services[name] = (ip, port)
                    print(f"Service added: {name} at {ip}:{port}")
                    self.discovery.notify_listeners((ip, port), added=True)
                    
        def remove_service(self, zc, type_, name):
            if name in self.discovery.discovered_services:
                ip, port = self.discovery.discovered_services[name]
                del self.discovery.discovered_services[name]
                print(f"Service removed: {name}")
                self.discovery.notify_listeners((ip, port), added=False)
                
        def update_service(self, zc, type_, name):
            self.add_service(zc, type_, name)
            
    def start_discovery(self):
        """Start discovering services on the network."""
        self.browser = ServiceBrowser(
            self.zeroconf, 
            self.service_name, 
            self.ServiceListener(self)
        )
        
    def get_discovered_services(self):
        """Get all discovered services."""
        return list(self.discovered_services.values())
        
    def stop(self):
        """Stop service discovery and unregister service."""
        if self.browser:
            self.browser.cancel()
        if self.info:
            self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()
