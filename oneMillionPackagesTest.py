## This script opens a UDP Socket on Port 217 and listens for single Byte packages form the W5500 - FPGA 

import socket
import time;
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('', 217)  # '' means it listens on all available interfaces, port 217
sock.bind(server_address)

print("Listening for broadcast messages on port 217...")

##create numpy array to see the milliseconds between the messages
package_latencies = []
received_values = []
prev_microseconds = 0

amount_of_lost_packages = 0
amount_of_packages_with_wrong_payload_size = 0

amount_of_packages_to_receive = 10000

try:
    while True:
        # Receive data
        data, address = sock.recvfrom(4096)  # Buffer size is 4096 bytes
        ## get unix time the data was received
        current_unix_microseconds = round(time.time() * 1000000)
        current_microseconds = round(current_unix_microseconds - prev_microseconds)
        if(current_microseconds < 10000000): # if something takes longer than 10 milliseconds, it's not part of the histogram
            if(current_microseconds == 0): # if there is "no time in between packages aka it's 0" we just a value to 1 microsecond, so that the KDE works again
                package_latencies.append(1) 
            else:
                package_latencies.append(current_microseconds)
        prev_microseconds = current_unix_microseconds
        print(f"Received {len(data)} bytes from {address}: {data.hex()}")
        if(len(data) == 1):
            current_received_int = int(data.hex(),16)
            #Check if we've lost packages:
            if(len(received_values)==0): # we can't get a package delay for the first received value
                received_values.append(current_received_int)
            else:
                last_received_value = received_values[-1] # received_values[-1] is the last value in the array
                expected_value = (last_received_value + 1) % 256
                if(current_received_int != expected_value) : #considering the jump at 255 -> 0
                    amount_of_lost_packages += abs(current_received_int - expected_value) % 256
                received_values.append(current_received_int)
        else:
            received_values.append(0) # instead of the received number, if the package isn't exactly one byte, something went wrong. In this case replace with "0"
            amount_of_packages_with_wrong_payload_size += 1

        if len(package_latencies) == amount_of_packages_to_receive:
            break


except KeyboardInterrupt:
    print("\nExiting...")
finally:
    sock.close()
    print(f"Amount of lost packages: {amount_of_lost_packages}")
    print(f"Amount of packages with wrong payload size: {amount_of_packages_with_wrong_payload_size}")
    ##plotting results
    
    # Create a figure
    fig, ax1 = plt.subplots()

    ax1.hist(package_latencies, bins=100, density=True, alpha=0.7, color='blue')
    ax1.set_ylabel("Probability", color="blue")
    ax1.set_xlabel(f"Package delay in microseconds (k={amount_of_packages_to_receive})")
    ax1.tick_params(axis='y', labelcolor="blue")

    ax2 = ax1.twinx()  # Create a twin Axes sharing the same x-axis

    # Perform Kernel Density Estimation on the data
    kde = gaussian_kde(package_latencies, bw_method='scott')  # Adjust `bw_method` if needed
    x = np.linspace(min(package_latencies), max(package_latencies), 1000)
    kde_values = kde(x)

    color_kde = 'tab:red'
    ax2.plot(x, kde_values, color=color_kde, lw=2, label="KDE Fit")
    ax2.set_ylabel("Probability Density Function (KDE)", color=color_kde)
    ax2.tick_params(axis='y', labelcolor=color_kde)

    # Synchronize the y-axes at zero so that they're visually even
    ax2.set_ylim(0, ax2.get_ylim()[1])  
    ax1.set_ylim(0, ax1.get_ylim()[1])  
    plt.grid()
    fig.tight_layout()
    #fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.show() 

    # Plot received values over time
    xaxis = np.linspace(1.0, len(received_values), len(received_values))
    plt.plot(xaxis, received_values)
    plt.show()