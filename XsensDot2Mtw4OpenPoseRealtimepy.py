"""
The objective of this code is to convert Xsens Dot data into Xsens MVN data and then into a format readable by OpenSim for human modeling. Xsens MVN output data includes header timestamp, acceleration data, rotation matrix, and UT Time. Xsens Dot, on the other hand, outputs only the quaternion of the free acceleration of the header or Euler Angle. Therefore, it is necessary to convert the quaternion in Xsens Dot to the rotation matrix and supplement the header of the acceleration data with UT Time and other information.

- The 'csv' files contain data exported from Xsens Dot.
- Data in the 'OpenSenseExampleIMUData' folder represents OpenSim IMU data, exported using Xsens MVN software.
- Data in the 'Transformed_XsensDot_Data' folder is the converted Xsens Dot data, excluding the header.
"""

# Importing required libraries
import os               # Perform system operations
import re               # Extract IMU ID from file names
import numpy as np      # Perform array operations
import pandas as pd     # Read and write Excel data
from scipy.spatial.transform import Rotation as R  # Convert quaternions to Euler angles

# Show the current directory
path_cwd = os.getcwd()
print("The current path is:", path_cwd)

# Display Xsens MVN data (OpenSense IMU data)
file_example = r"MT_012005D6_009-001_00B421E6.txt" 
path_xsens_dot = os.path.join(path_cwd, "OpenSenseExampleIMUData", file_example)
df = pd.read_csv(path_xsens_dot)
print("The table header data is:\n", df.head(7))
OpenSenseExampleIMUData_df = pd.read_csv(path_xsens_dot, skiprows=5, sep="\t")
print("Xsens MVN data:\n", OpenSenseExampleIMUData_df.head())

def transformed_Xsens_dot_data_Realtime(filename):
    # Extract IMU ID from the file name
    regex = r"(.*)_(.*_.*_).*.csv"
    mysearch = re.search(regex, filename)
    IMU_ID =  mysearch.group(1) 
    prefix_IMU = mysearch.group(2)
    new_filename = "XSDot" + "_" + prefix_IMU + IMU_ID + ".txt"
    path_new_filename = os.path.join(path_new_file, new_filename)
    
    # Read the file
    df = pd.read_csv(filename, skiprows=10)
    df_quat = df[["Quat_W", "Quat_X", "Quat_Y", "Quat_Z"]]  # Select the column containing quaternions
    
    # Convert quaternions to rotation matrix
    r = R.from_quat(df_quat)
    matrix = r.as_matrix()
    (matrix_rows, b, c) = matrix.shape
    matrix_reshpae = matrix.reshape(matrix_rows, 9)
    
    # Write the converted data to Excel
    header_list = ["Mat[1][1]", "Mat[1][2]", "Mat[1][3]",
                   "Mat[2][1]", "Mat[2][2]", "Mat[2][3]",
                   "Mat[3][1]", "Mat[3][2]", "Mat[3][3]"]
    df_matrix = pd.DataFrame(matrix_reshpae, columns=header_list)
    
    # Align Xsens MVN built with Dot data
    PacketCounter = df['PacketCounter']
    SampleTimeFine = df["SampleTimeFine"]
    Acc = df[["FreeAcc_X", "FreeAcc_Y", "FreeAcc_Z"]]
    Acc.columns = ["Acc_X", "Acc_Y", "Acc_Z"]
    Year = [] 
    Month = []
    Day = []
    Second = []
    UTC_Nano = []
    UTC_Year = []
    UTC_Month = []
    UTC_Day = []
    UTC_Hour = []
    UTC_Minute = []
    UTC_Second = []
    UTC_Valid = []
    df_othercolumns = pd.DataFrame({'Year': Year, 'Month': Month, 'Day': Day, 'Second': Second,
                                    'UTC_Nano': UTC_Nano, 'UTC_Year': UTC_Year, 'UTC_Month': UTC_Month,
                                    'UTC_Day': UTC_Day, 'UTC_Hour': UTC_Hour, 'UTC_Minute': UTC_Minute,
                                    'UTC_Second': UTC_Second, 'UTC_Valid': UTC_Valid})
    
    # Concatenate the dataframes
    frame = [PacketCounter, SampleTimeFine, df_othercolumns, Acc, df_matrix]
    transformed_df = pd.concat(frame, axis=1)
    
    # Write to file
    transformed_df.to_csv(path_new_filename, index=False, sep="\t", float_format='%.6f') 
    
    # Update file header
    with open(path_new_filename, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write("// Start Time: Unknown\n// Update Rate: 100.0Hz\n//Filter Profile: human (46.1)\n// Option Flags: AHS Disabled ICC Disabled\n// Firmware Version: 4.0.2\n" + content)
    
    print(new_filename, "Done😎")
# Define the path for new files
new_file = "Transformed_XsensDot_Data_Realtime"
path_new_file = os.path.join(path_cwd, new_file)

# Change directory to access original Xsens Dot data
os.chdir(path_cwd)
path_original_Xsens_dot = os.chdir(".\\Original_XsensDot_Data_Realtime")

# Loop through each file in the directory
for file in os.listdir():
    # Skip folders and process only '.csv' files
    if ".csv" in file:
        transformed_Xsens_dot_data_Realtime(file)

print("All Xsens Dot original files have been converted😎")
