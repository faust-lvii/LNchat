import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

class ChatUI:
    def __init__(self, send_callback=None, connect_callback=None):
        self.root = tk.Tk()
        self.root.title("LNChat - Local Network Chat")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.send_callback = send_callback
        self.connect_callback = connect_callback
        
        self.peers = {}  # {address: name}
        self.selected_peer = None
        
        self._create_ui()
        self._setup_styles()
        
    def _setup_styles(self):
        """Setup custom styles for the UI."""
        style = ttk.Style()
        style.configure("Connected.TLabel", foreground="green", font=("Arial", 10, "bold"))
        style.configure("Disconnected.TLabel", foreground="red", font=("Arial", 10, "bold"))
        
    def _create_ui(self):
        """Create the main UI components."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Split into left panel (peers) and right panel (chat)
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left panel - Peers list
        ttk.Label(left_panel, text="Connected Peers", font=("Arial", 12, "bold")).pack(pady=(0, 5), anchor=tk.W)
        
        # Connection status
        self.connection_frame = ttk.Frame(left_panel)
        self.connection_frame.pack(fill=tk.X, pady=(0, 10))
        self.connection_status = ttk.Label(self.connection_frame, text="Disconnected", style="Disconnected.TLabel")
        self.connection_status.pack(side=tk.LEFT)
        
        # Peers listbox with scrollbar
        peers_frame = ttk.Frame(left_panel)
        peers_frame.pack(fill=tk.BOTH, expand=True)
        
        self.peers_listbox = tk.Listbox(peers_frame, font=("Arial", 10))
        self.peers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        peers_scrollbar = ttk.Scrollbar(peers_frame, orient=tk.VERTICAL, command=self.peers_listbox.yview)
        peers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.peers_listbox.config(yscrollcommand=peers_scrollbar.set)
        
        # Bind selection event
        self.peers_listbox.bind('<<ListboxSelect>>', self._on_peer_selected)
        
        # Right panel - Chat
        # Chat history
        ttk.Label(right_panel, text="Chat", font=("Arial", 12, "bold")).pack(pady=(0, 5), anchor=tk.W)
        
        self.chat_history = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, font=("Arial", 10))
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_history.config(state=tk.DISABLED)
        
        # Message input and send button
        input_frame = ttk.Frame(right_panel)
        input_frame.pack(fill=tk.X)
        
        self.message_input = ttk.Entry(input_frame, font=("Arial", 10))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_input.bind("<Return>", self._on_send_message)
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self._on_send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        # Initially disable message input and send button
        self._update_input_state()
        
    def _on_peer_selected(self, event):
        """Handle peer selection from the listbox."""
        selection = self.peers_listbox.curselection()
        if selection:
            index = selection[0]
            peer_info = self.peers_listbox.get(index)
            
            # Extract address from peer info
            for address, name in self.peers.items():
                if f"{name} ({address[0]}:{address[1]})" == peer_info:
                    self.selected_peer = address
                    self._update_input_state()
                    return
                    
        self.selected_peer = None
        self._update_input_state()
        
    def _on_send_message(self, event=None):
        """Handle sending a message."""
        message = self.message_input.get().strip()
        if message and self.selected_peer and self.send_callback:
            # Call the send callback
            success = self.send_callback(self.selected_peer, {"type": "message", "content": message})
            
            if success:
                # Add message to chat history
                self.add_message("You", message)
                
                # Clear input
                self.message_input.delete(0, tk.END)
        
    def _update_input_state(self):
        """Update the state of input fields based on selection."""
        if self.selected_peer:
            self.message_input.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
        else:
            self.message_input.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            
    def add_peer(self, address, name=None):
        """Add a peer to the list."""
        if name is None:
            name = f"Peer-{len(self.peers) + 1}"
            
        self.peers[address] = name
        self._update_peers_list()
        
        # Update connection status
        if self.peers:
            self.connection_status.config(text="Connected", style="Connected.TLabel")
        
    def remove_peer(self, address):
        """Remove a peer from the list."""
        if address in self.peers:
            del self.peers[address]
            
            # If the removed peer was selected, clear selection
            if self.selected_peer == address:
                self.selected_peer = None
                self._update_input_state()
                
            self._update_peers_list()
            
            # Update connection status
            if not self.peers:
                self.connection_status.config(text="Disconnected", style="Disconnected.TLabel")
                
    def _update_peers_list(self):
        """Update the peers listbox."""
        self.peers_listbox.delete(0, tk.END)
        
        for address, name in self.peers.items():
            self.peers_listbox.insert(tk.END, f"{name} ({address[0]}:{address[1]})")
            
    def add_message(self, sender, content):
        """Add a message to the chat history."""
        self.chat_history.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Format and insert message
        self.chat_history.insert(tk.END, f"[{timestamp}] {sender}: ", "sender")
        self.chat_history.insert(tk.END, f"{content}\n", "message")
        
        # Auto-scroll to bottom
        self.chat_history.see(tk.END)
        
        self.chat_history.config(state=tk.DISABLED)
        
    def show_error(self, title, message):
        """Show an error message."""
        messagebox.showerror(title, message)
        
    def show_info(self, title, message):
        """Show an information message."""
        messagebox.showinfo(title, message)
        
    def start(self):
        """Start the UI main loop."""
        self.root.mainloop()
        
    def stop(self):
        """Stop the UI."""
        if self.root:
            self.root.quit()
            
    def update(self):
        """Process UI events without blocking."""
        self.root.update_idletasks()
        self.root.update()
