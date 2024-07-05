import socket
import threading
import networkx as nx
import matplotlib.pyplot as plt

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)
        print(f"Received data from client: {data.decode()}")
        response = b"Hello, World!\n"
        client_socket.send(response)
    except ConnectionResetError:
        print("Connection forcibly closed by the remote host")
    finally:
        client_socket.close()

def create_topology_image(graph, filename):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_size=1000, node_color='skyblue')
    plt.savefig(filename, format="PNG")
    plt.show()

def start_topology(port):
    G = nx.Graph()

    G.add_node('Controller')

    root_switch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    root_switch.bind(('localhost', port))
    root_switch.listen(100)
    print(f"Root switch listening on port {port}")

    controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controller_socket.connect(('localhost', port))
    G.add_edge('Controller', 'Root')

    threads = []

    def handle_switch(child_switch, parent_node):
        try:
            data = child_switch.recv(1024)
            print(f"Received data from switch: {data.decode()}")
        except ConnectionResetError:
            print("Connection forcibly closed by the remote host")
        finally:
            child_switch.close()

    for i in range(3):
        child_switch, addr = root_switch.accept()
        print(f"Accepted connection from child switch {addr}")
        child_name = f'Child_{i+1}'
        G.add_edge('Root', child_name)
        threads.append(threading.Thread(target=handle_switch, args=(child_switch, child_name)))

        for j in range(2):
            host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host_socket.connect(('localhost', 8080))
            host_name = f'Host_{i+1}_{j+1}'
            G.add_edge(child_name, host_name)
            threads.append(threading.Thread(target=handle_client, args=(host_socket,)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    create_topology_image(G, 'complex_topology.png')

if __name__ == "__main__":
    start_topology(8080)
