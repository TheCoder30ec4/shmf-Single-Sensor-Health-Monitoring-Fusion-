import socket
import csv
import keyboard
import json
from tqdm import tqdm

UDP_IP = "192.168.160.187"
UDP_PORT = 3002

# Initialize packet counter
packet_counter = 0

# Open CSV file for writing
with open('data.csv', 'w', newline='') as csvfile:
    fieldnames = ['Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z', 'FreeAcc_X', 'FreeAcc_Y', 'FreeAcc_Z', 'PacketCounter']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write headers to CSV file
    writer.writeheader()

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sock.bind((UDP_IP, UDP_PORT))

    print("UDP server started")
    print("Press spacebar to stop receiving data.")

    # Continuously receive and process UDP data until spacebar is pressed
    with tqdm(desc="Receiving Data", unit=" packets", unit_scale=True) as progress_bar:
        while True:
            # Check if spacebar is pressed
            if keyboard.is_pressed(' '):
                print("\nSpacebar pressed. Stopping data reception.")
                break

            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            decoded_data = data.decode()

            # Attempt to parse JSON data
            try:
                json_data = json.loads(decoded_data)
                quat_w, quat_x, quat_y, quat_z = map(float, [json_data.get('quaternion', {}).get('W', 0), json_data.get('quaternion', {}).get('X', 0), json_data.get('quaternion', {}).get('Y', 0), json_data.get('quaternion', {}).get('Z', 0)])
                acc_x, acc_y, acc_z = map(float, [json_data.get('accelerometer', {}).get('Acc_x', 0), json_data.get('accelerometer', {}).get('Acc_y', 0), json_data.get('accelerometer', {}).get('Acc_z', 0)])
            except ValueError as e:
                print("Error parsing JSON:", e)
                print("Received data:", decoded_data)
                continue
            
            # Increment packet counter
            packet_counter += 1

            # Write data to CSV file
            writer.writerow({'Quat_W': quat_w, 'Quat_X': quat_x, 'Quat_Y': quat_y, 'Quat_Z': quat_z,
                             'FreeAcc_X': acc_x, 'FreeAcc_Y': acc_y, 'FreeAcc_Z': acc_z, 'PacketCounter': packet_counter})
            
            # Update progress bar
            progress_bar.update(1)

            print("Received message:", decoded_data)
 
print("Data reception stopped.")
