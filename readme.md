# LNChat - Local Network Chat Application

LNChat is a cross-platform chat application that enables communication between computers on a local network (same Wi-Fi or Ethernet network). The application automatically discovers other computers on the network, displays a "Connected" message, and allows users to send and receive text messages in real-time.

## Features

- **Automatic Network Discovery**: Automatically detects other computers on the local network using mDNS (Bonjour)
- **Real-time Messaging**: Send and receive text messages in real-time
- **Cross-Platform Compatibility**: Runs on Windows, macOS, and Linux operating systems
- **User-Friendly Interface**: Simple and intuitive user interface
- **Connection Status**: Displays a green "Connected" message when a connection is established

## Requirements

- Python 3.6 or higher
- Required packages (install using `pip install -r requirements.txt`):
  - tkinter (usually comes with Python)
  - zeroconf

## Installation

1. Clone this repository or download the source code
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Optionally, you can specify a custom port:
   ```
   python main.py 5001
   ```

3. The application will automatically discover other instances of LNChat on the local network
4. Select a peer from the list on the left to start chatting
5. Type your message in the input field and press Enter or click Send

## Project Structure

- `main.py`: Main application entry point
- `network_discovery.py`: Handles automatic network discovery using mDNS
- `network_communication.py`: Manages network communication using TCP/IP sockets
- `chat_ui.py`: Implements the user interface using Tkinter

## Security Considerations

This application is intended for use on local networks only. It is not suitable for communication over the internet as it does not implement encryption or authentication mechanisms.

## Future Enhancements

- File sharing capabilities
- Group chat functionality
- User authentication
- Message encryption
- Custom user names and avatars