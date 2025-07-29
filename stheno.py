import logging
import frida
import threading
import socketserver
import socket
import os
import argparse
from colorama import init, Fore, Style
import time
from lamda.client import * 

logo ="""
 ░▒▓███████▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░  
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
 ░▒▓██████▓▒░   ░▒▓█▓▒░   ░▒▓████████▓▒░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
       ░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
       ░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░   ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░                                                    
"""

agent_script = "agent.js"
init(autoreset=True)  
logger = logging.getLogger()

class LoggerConsoleOutputFormat(logging.Formatter):
    COLORS = {
        logging.INFO: Fore.GREEN,       # Green color for INFO
        logging.WARNING: Fore.YELLOW,   # Yellow color for WARNING
        logging.ERROR: Fore.RED,        # Red color for ERROR
        logging.CRITICAL: Fore.RED + Style.BRIGHT  # Bright red color for CRITICAL
    }

    def format(self, record):
        log_level = record.levelno
        color_prefix = self.COLORS.get(log_level, '')
        color_suffix = Style.RESET_ALL
        
        formatted_time_level = f"{color_prefix}[{self.formatTime(record)} - {record.levelname}] - {color_suffix}"
        return f"{formatted_time_level} {record.getMessage()}"

    def formatTime(self, record, datefmt=None):
        """
        Override formatTime to customize the time formatting if needed.
        """
        if datefmt:
            s = logging.Formatter.formatTime(self, record, datefmt)
        else:
            s = logging.Formatter.formatTime(self, record, self.datefmt)
        return s

class Numeric:
	def __init__(self, message, base=10, lbound=None, ubound=None):
		self.message = message
		self.base = base
		self.lbound = lbound
		self.ubound = ubound

	def ask(self):
		try:
			answer = int(input(self.message + ' '), self.base)
			if self.lbound is not None:
				if answer < self.lbound:
					return self.ask()
			if self.ubound is not None:
				if answer > self.ubound:
					return self.ask()
			return answer
		except ValueError:
			return self.ask()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(1.0) 
        self.server.register_client(self.request)
        try:
            while True:
                try:
                    self.data = self.request.recv(1024).strip()
                    if not self.data or "close" in self.data.decode('utf-8'):
                        break
                    logger.debug(f"Received data from {self.client_address[0]}:{self.client_address[1]}")
                    logger.debug(f"Data: {self.data}")
                except socket.timeout:
                    continue
        finally:
            self.server.unregister_client(self.request)
            self.request.close()

class TCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, host="localhost", port=1711):
        self.server_address = (host, port)
        super().__init__(self.server_address, MyTCPHandler)
        self.clients = []
        self.server_thread = None

    def register_client(self, client):
        self.clients.append(client)

    def unregister_client(self, client):
        self.clients.remove(client)

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.sendall(message.encode('utf-8'))
            except BrokenPipeError:
                self.unregister_client(client)

    def start(self):
        if not self.server_thread or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(target=self.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            logger.info(f"Listening at {self.server_address[0]}:{self.server_address[1]}")

    def stop(self):
        if self.server_thread and self.server_thread.is_alive():
            self.shutdown()
            self.server_close()
            self.server_thread.join()
            logger.info("Server stopped")

class Stheno():

    device = None
    detached = False
    server = None
    pid = -1
    base_directory = os.path.dirname(__file__)
	
    def start_server(self, host: str, port: int) -> None:
        try:
            self.server = TCPServer(host, port)
            self.server.start()
        except Exception as e:
            logger.error(f"Error starting server: {e}")

    def stop_server(self) -> None:
        try:
            if self.server:
                self.server.stop()
        except Exception as e:
            logger.error(f"Error stoping server: {e}")     

    def run(self, target_package: str, force: bool, host="localhost", port=1711, remote_host=None, remote_port=None) -> None:
        print(logo)
        self.start_server(host, port)
        self.load_device(remote_host, remote_port)
        logger.info("We are ready to go... make sure that the monitor is running!")
        self.run_frida(force, target_package, self.device)

    def on_message(self, message, payload) -> None:
        if message["type"] == "send":
            data = message["payload"].split(":")[0].strip()
            if "IntentMsg" in data:
                if self.server:
                    self.server.broadcast(message["payload"].split("|")[1]+"\n")

    def on_detached(self, reason) -> None:
        logger.info("Session is over")
        self.detached = True

    def load_device(self, remote_host=None, remote_port=None) -> None:
        try:
            if remote_host and remote_port:
                # Connect to remote Frida server with token authentication
                if remote_port == '65000':
                    # Use custom Device class for token authentication
                    d = Device(remote_host)
                    token = d._get_session_token()
                    self.device = frida.get_device_manager() \
                        .add_remote_device(f'{remote_host}:{remote_port}', token=token)
                    logger.info(f"Connected to remote device: {self.device} with token authentication")
                else:
                    # Regular remote connection without token
                    self.device = frida.get_device_manager() \
                        .add_remote_device(f'{remote_host}:{remote_port}')
                    logger.info(f"Connected to remote device: {self.device}")
            else:
                # Use local device enumeration
                devices = frida.enumerate_devices()
                logger.info("Available devices:")
                for device in range(len(devices)):
                    print(f'{device}) {devices[device]}')
                self.device = devices[int(Numeric('\nEnter the index of the device to use:', lbound=0, ubound=len(devices) - 1).ask())]
                logger.info(f"Device: {self.device}")
        except Exception as e:
              logger.error(e)
    
    def run_frida(self, force: bool, package_name: str, device) -> None:
        try:
            self.detached = False
            session = self.frida_session_handler(force, device, package_name)
            with open(os.path.join(self.base_directory, agent_script)) as f:
                self.script = session.create_script(f.read())
            
            session.on('detached', self.on_detached)
            self.script.on("message", self.on_message)  # register the message handler
            self.script.load()
            if force:
                self.device.resume(self.pid)
            s = ""
            while (s != 'e') and (not self.detached):
                s = input("(enter 'e' to exit)>")

            if self.script:
                self.script.unload()

            self.stop_server()
        except Exception as e:
             logger.error(e)
          
    def frida_session_handler(self, force: bool, con_device, pkg: str, pid=-1):
        time.sleep(1)
        try:
            if not force:
                if pid == -1:
                    logger.info(f"Device ID: {con_device.id}")
                    # Check if this is a remote device (not USB/local)
                    if hasattr(con_device, 'type') and con_device.type in ['remote', 'tether']:
                        # For remote devices, try to find the process using Frida's enumerate_processes
                        processes = con_device.enumerate_processes()
                        logger.info(f"Available processes on remote device:")
                        for process in processes:
                            logger.info(f"  PID: {process.pid}, Name: {process.name}")
                        
                        target_pid = None
                        for process in processes:
                            if pkg in process.name:
                                target_pid = process.pid
                                logger.info(f"Found target process: {process.name} (PID: {process.pid})")
                                break
                        if target_pid:
                            self.pid = target_pid
                        else:
                            logger.error(f"Could not find process with name containing '{pkg}'")
                            logger.info(f"Available processes: {[p.name for p in processes]}")
                            return None
                    else:
                        # For USB/local devices, use ADB
                        self.pid = os.popen(f"adb -s {con_device.id} shell pidof {pkg}").read().strip()
                else:
                    self.pid = pid
                
                if self.pid == '' or self.pid is None:
                    logger.error("Could not find process with this name.")
                    return None
                
                frida_session = con_device.attach(int(self.pid))
                if frida_session:
                    logger.info("Attaching frida session to PID - {0}".format(frida_session._impl.pid))
                else:
                    logger.error("Could not attach the requested process")
                    return None
            elif force:
                self.pid = con_device.spawn(pkg)
                if self.pid:
                    frida_session = con_device.attach(self.pid)
                    logger.info("Spawned package : {0} on pid {1}".format(pkg, frida_session._impl.pid))
                else:
                    logger.error("Could not spawn the requested package")
                    return None
            else:
                return None
                
            return frida_session
        except Exception as e:
            logger.error(f"Error in frida_session_handler: {e}")
            return None

def setup_logging():
    formatter = LoggerConsoleOutputFormat()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

if __name__=="__main__":
    parser = argparse.ArgumentParser(
            prog='Stetho',
            description='A lightweight medusa....')
    parser.add_argument('-t', '--target-name', type=str, help='target package', required=True)
    parser.add_argument('-a', '--address', type=str, default="localhost", help='address to listen to (default is localhost)')
    parser.add_argument('-p', '--port', type=str, default=1711, help='port to listen to (default is 1711)')
    parser.add_argument('-f', '--force', help='force start the target package', action='store_true', default=False, required=False)
    parser.add_argument('--remote-host', type=str, help='remote Frida server host (e.g., 192.168.1.6)')
    parser.add_argument('--remote-port', type=str, help='remote Frida server port (e.g., 65000)')
    args = parser.parse_args()
    try:
        setup_logging()
        stetho = Stheno()
        stetho.run(args.target_name, args.force, args.address, args.port, args.remote_host, args.remote_port)
    except KeyboardInterrupt:
        pass







    