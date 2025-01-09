import socket
import time;
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm  # Import log-normal distribution
from scipy.stats import gaussian_kde


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Allow the socket to reuse the address
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('', 217)  # '' means it listens on all available interfaces
sock.bind(server_address)

print("Listening for broadcast messages on port 217...")

##create numpy array to see the milliseconds between the messages
package_latencies = []
received_values = []

prev_microseconds = 0
try:
    while True:
        # Receive data
        data, address = sock.recvfrom(4096)  # Buffer size is 4096 bytes
        ## get unix time the data was received
        current_unix_microseconds = round(time.time() * 1000000)
        current_microseconds = round(current_unix_microseconds - prev_microseconds)
        # if(current_microseconds < 3000000):
        if(current_microseconds < 10000000):
            if(current_microseconds == 0): # if there is "no time in between packages aka it's 0" we just a value to 1 microsecond, so that the gamma distribution will work again
                package_latencies.append(1) 
            else:
                package_latencies.append(current_microseconds)
        prev_microseconds = current_unix_microseconds
        print(f"Received {len(data)} bytes from {address}: {data.hex()}")
        if(len(data) == 4) :
            received_values.append(int(data.hex(),16))
        else    :
            received_values.append(0)
        if len(package_latencies) == 10000:
            break


except KeyboardInterrupt:
    print("\nExiting...")
finally:
    sock.close()
    print(package_latencies)

    ##plotting results
    
    # Create a figure
    fig, ax1 = plt.subplots()

    ax1.hist(package_latencies, bins=100, density=True, alpha=0.7, color='blue')
    ax1.set_ylabel("Probability", color="blue")
    ax1.set_xlabel("Package delay in microseconds (k=10000)")
    ax1.tick_params(axis='y', labelcolor="blue")

    ax2 = ax1.twinx()  # Create a twin Axes sharing the same x-axis

    # Fit a log-normal distribution to the filtered data
    shape, loc, scale = lognorm.fit(package_latencies, floc=0)  # Fix location to 0
    print(f"Log-normal fit: shape={shape:.2f}, scale={scale:.2f}")

    # Generate the fitted PDF
    x = np.linspace(min(package_latencies), max(package_latencies), 1000)
    pdf = lognorm.pdf(x, shape, loc=loc, scale=scale)

    # Plot the PDF (right y-axis)
    color_pdf = 'tab:red'
    ax2.plot(x, pdf, color=color_pdf, lw=2, label=f"Log-normal Fit (shape={shape:.2f}, scale={scale:.2f})")
    ax2.set_ylabel("Probability Density Function", color=color_pdf)
    ax2.tick_params(axis='y', labelcolor=color_pdf)

    # Synchronize the y-axes at zero so that they're even
    ax2.set_ylim(0, ax2.get_ylim()[1])  
    ax1.set_ylim(0, ax1.get_ylim()[1])  
    
    plt.show()

    # Add legends
    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.show() ## first plot histrogram and probability function


    # Plot received values over time
    xaxis = np.linspace(1.0, len(received_values), len(received_values))
    plt.plot(xaxis, received_values)
    plt.show()