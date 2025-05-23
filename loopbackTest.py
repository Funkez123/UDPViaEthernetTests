import socket
import time
import numpy as np
import matplotlib.pyplot as plt

# Target IP and Port
TARGET_IP = "192.168.2.100"
TARGET_PORT = 217

# Number of packets to send
NUM_PACKETS = 4096

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)  # Set a timeout of 100 milliseconds

# Storage for round-trip times (RTTs)
round_trip_times = []

test_data = b"Ping"  # 4-byte test message

sock.bind(("0.0.0.0", 217))  # Bind to all interfaces on port 217

try:
    for _ in range(NUM_PACKETS):
        send_time = time.time() * 1_000_000  # Convert to microseconds  
        sock.sendto(test_data, (TARGET_IP, TARGET_PORT))
        
        try:
            data, _ = sock.recvfrom(4096)  # Buffer size is 4096 bytes
            recv_time = time.time() * 1_000_000  # Convert to microseconds
            round_trip_times.append(recv_time - send_time)
        except socket.timeout:
            print("Packet timeout")

except KeyboardInterrupt:
    print("\nTest interrupted")
finally:
    sock.close()
    
    # Plot histogram
    plt.hist(round_trip_times, bins=100, density=False, alpha=0.7, color='blue')

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Convert Y-axis to percentage
    #ax.set_ylabel("Percentage")
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{(y / NUM_PACKETS) * 100:.1f}%'))
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    #plt.ylabel("Probability")
    plt.grid()
    #plt.xlabel("Loopback delay in microseconds (k=4096)")
    plt.show()
