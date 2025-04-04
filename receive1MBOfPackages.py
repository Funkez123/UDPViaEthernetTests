import socket
import time;
import numpy as np
import matplotlib.pyplot as plt


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('', 217)  # '' means it listens on all available interfaces
sock.bind(server_address)


##create numpy array to see the milliseconds between the messages
package_latencies = []
received_values = []

amount_of_packets_to_receive = 4096

prev_unix_microseconds = 0
try:
    while True:
        # Receive data
        data, address = sock.recvfrom(4096)  # Buffer size is 4096 bytes

        ## get unix time the data was received
        current_unix_microseconds = round(time.time() * 1000000)
        current_microseconds = round(current_unix_microseconds - prev_unix_microseconds)

        ## if this is the very first package, let's save it's time
        if(len(package_latencies)==0):
            first_package_unix_time = current_unix_microseconds

        if(current_microseconds < 3000000): # packages that take more than 3 seconds count as timeout
            package_latencies.append(current_microseconds) # package_latencies array contains microsecond times inbetween packages
        prev_unix_microseconds = current_unix_microseconds
        # print(f"Received {len(data)} bytes from {address}: {data.hex()}")
        if len(package_latencies) == amount_of_packets_to_receive:
            break # if 4096 packages of size 256 Bytes are received, we are done


except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # get the latest microseconds and calculate the difference to the first package
    last_package_unix_microseconds = round(time.time() * 1000000)
    time_total = last_package_unix_microseconds - first_package_unix_time
    print(f"receiving 1 Megabyte of data 4096 * 256 Bytes took: {time_total/1000} milliseconds")
    
    fig, ax1 = plt.subplots()

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    sock.close()
    plt.hist(package_latencies, bins=100, density=False, alpha=0.7, color='blue')
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{(y / amount_of_packets_to_receive) * 100:.1f}%'))
    plt.grid()
    #plt.ylabel("probability")
    #plt.xlabel("package delay in microseconds (k=4096)")
    #plt.show()

    
