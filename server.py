import socket
import threading
import time
import joblib


CONNECTION_LIMIT = 20
WINDOW_SIZE_SECONDS = 10
connections = []

knn = joblib.load(r'C:\Users\gudis\Downloads\1st_Signal\KNN.joblib')
lr = joblib.load(r'C:\Users\gudis\Downloads\1st_Signal\LogisticRegression.joblib')
rf = joblib.load(r'C:\Users\gudis\Downloads\1st_Signal\Random_Forest.joblib')
svc = joblib.load(r'C:\Users\gudis\Downloads\1st_Signal\SVC.joblib')


def detect_ddos():
    while True:
        time.sleep(WINDOW_SIZE_SECONDS)
        current_time = time.time()
        # Filter connections within the time window
        active_connections = [conn_time for conn_time in connections if current_time - conn_time < WINDOW_SIZE_SECONDS]
        if len(active_connections) > CONNECTION_LIMIT:
            print(f"Possible DDoS attack detected: {len(active_connections)} connections within {WINDOW_SIZE_SECONDS} seconds")

def start_server(port):
    # Start DDoS detection thread
    ddos_thread = threading.Thread(target=detect_ddos)
    ddos_thread.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', port))
    server.listen(100)  

    print(f"Server listening on port {port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        # Record connection time for DDoS detection
        connections.append(time.time())

        # Check for DDoS attacks
        current_time = time.time()
        active_connections = [conn_time for conn_time in connections if current_time - conn_time < WINDOW_SIZE_SECONDS]
        if len(active_connections) > CONNECTION_LIMIT:
            print(f"Possible KEYFRA attack detected: {len(active_connections)} connections within {WINDOW_SIZE_SECONDS} seconds")

        # Send response to the client
        response = b"Hello, World!\n"
        client_socket.send(response)

        client_socket.close()

if __name__ == "__main__":
    port_number = 8080  
    start_server(port_number)
