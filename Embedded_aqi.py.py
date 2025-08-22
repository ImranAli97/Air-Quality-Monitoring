# -------  Import all necessary Libraries -------  #
import requests
import json
import time
from matplotlib import pyplot as plt
import numpy as np
import dht11
import RPi.GPIO as RPI
import thingspeak
from collections import deque
from Adafruit_LED_Backpack import SevenSegment
from luma.core.interface.serial import spi, noop
from luma.led_matrix.device import max7219
from luma.core.render import canvas

# =============== Task 3.1 ================== #



# ------- Channel id and key for Thingspeak------- #
channel_id = 2655006
write_key = 'VC0WCV4SJWJ568ZK'
read_key = 'HD5F2WJII57OJTB4'



# ------- Hardware Configuration ------------ #
# GPIO Setup
gpio_button_right = 19
gpio_button_left = 25
gpio_list_inputs = [gpio_button_left, gpio_button_right]

# Temperature sensor -- GPIO pin 4
gpio_sensor = 4

# ----------------- GPIO Channel Setup ----------------- #
RPI.setmode(RPI.BCM)  # The GPIO numbering system
RPI.setup(gpio_list_inputs, RPI.IN, pull_up_down=RPI.PUD_OFF)


# 7-Segment Display
seven_sg= SevenSegment.SevenSegment(address=0x70)
seven_sg.begin()


# LED Matrix Display
my_spi = spi(port=0, device=1, gpio=noop())
cascaded = 1
block_orientation = 90
rotate = 0
my_led = max7219(my_spi, cascaded=cascaded, block_orientation=block_orientation, rotate=rotate)


# Initial Values for the program
graph_position = 0
graph_range = 100
start_time = time.time()
last_10_sec_check = 0  # For storing the last time the 10-second function was used
last_60_sec_check = 0  # For storing the last time the 60-second function was used


# ---------- 3.1.1.Accessing ThinkSpeak Channel ---------- #
url_feed = 'https://thingspeak.com/channels/343018/feeds.json?results=100'

# Initializing arrays for each field
pm10_array = []
pm10_avg60_array = []
pm25_array = []
pm25_avg60_array = []
pm1_array = []
pm1_avg60_array = []
aqi_array = []


# =============== Task 3.2 ================== #

# Temperature values
buffer_size = 100
buffer_temp = deque([19, 16, 17, 23, 20, 21, 19, 18, 21, 20, 22, 18, 22, 21, 23, 18, 23, 23, 20, 16, 17, 23, 21, 19, 18, 20, 19, 21, 22, 20, 23, 17, 19, 18, 16, 20, 21, 22, 23, 20, 22, 23, 19, 18, 16, 23, 20, 16, 19, 23, 21, 16, 22, 18, 17, 18, 16, 23, 20, 19, 16, 20, 22, 23, 25, 21, 16, 20, 22, 23, 17, 18, 18, 23, 22, 20, 23, 16, 18, 19, 21, 22, 16, 19, 21, 23, 22, 21, 18, 19, 16, 20, 21, 22, 20, 18, 24, 23, 21, 22],
             maxlen=buffer_size)

# Humidity values
buffer_hum = deque([35, 37, 28, 40, 43, 63, 25, 31, 45, 35, 26, 27, 31, 37, 48, 57, 37, 56, 61, 65, 53, 34, 45, 53, 33, 22, 62, 74, 36, 70, 23, 21, 19, 22, 53, 21, 19, 56, 19, 20, 27, 16, 48, 35, 26, 68, 19, 35, 20, 19, 21, 20, 42, 47, 20, 63, 45, 22, 21, 24, 26, 31, 27, 37, 28, 19, 22, 25, 28, 28, 25, 24, 23, 26, 34, 55, 71, 32, 20, 30, 29, 21, 34, 25, 27, 51, 56, 58, 33, 17, 28, 30, 21, 21, 57, 25, 56, 60, 31, 57],
                 maxlen=buffer_size)

# ---------- Functions for the Program ------- #
def clear_screen():  # Function used to clear 7SD
    seven_sg.clear()
    seven_sg.write_display()

def print_number(num):  # Function used to print number on 7SD
    clear_screen()
    num = round(num, 2)
    seven_sg.print_number_str(str(num))
    seven_sg.write_display()

def list_scaling(temp_list):
    max_value = max(temp_list)
    new_list = []
    for i in temp_list:
        percent = int((i/max_value * 100))
        bars = int((percent / 100) * 6)
        new_list.append(bars)
    print(new_list)
    return new_list


def filter_list(list1):
    filtered_list = list(filter(lambda x: x is not None, list1))
    filtered_list = list(map(int, filtered_list))
    return filtered_list



# List Compression

def compress_list(lst, num_points=8):
    # Determine the length of each segment
    segment_length = len(lst) // num_points

    # Create a new list to store the compressed values
    compressed_values = []

    # Loop through the specified number of points to calculate the average for each segment
    for i in range(num_points):
        start_index = i * segment_length
        # Adjust the end index for the last segment if the list length isn't perfectly divisible
        end_index = min((i + 1) * segment_length, len(lst))
        segment = lst[start_index:end_index]
        avg_value = sum(segment) / len(segment) if segment else 0
        compressed_values.append(int(round(avg_value)))

    # Scale the new list using the list_scaling function
    scaled_list = list_scaling(compressed_values)
    return scaled_list

def plot_position(move):  # for moving the led along with counter
    global graph_position
    if move == "right":
        graph_position = (graph_position + 1) % 5  # Moves right and wraps around to 0 after 4
    elif move == "left":
        graph_position = (graph_position - 1) % 5  # Moves left and wraps around to 4 after 0

def ssd_select():  # Select which value to display on 7SD
    arrays = [pm1_array, pm25_array, pm10_array, temp, humidity]
    ssd_value = np.mean(arrays[graph_position])
    return ssd_value

def draw_led_plot(draw_list):
    ssd_value = ssd_select()
    print_number(ssd_value)

    with canvas(my_led) as draw:
        # Draw a point at the current graph position
        draw.point((graph_position, 0), fill="white")

        # Draw the points from the draw_list
        for index, value in enumerate(draw_list):
            draw.point((index, 8 - value), fill="white")



# Extraction of last 100 readings for each field

def fetch_data():
    global pm10_array, pm10_avg60_array, pm25_array, pm25_avg60_array, pm1_array, pm1_avg60_array, aqi_array
    # Getting data from the API
    get_data = requests.get(url_feed).json()

    # ----------- 3.1.2. Decoding the cloud reading by JSON --------- #
    feed_data = get_data['feeds']

    # Clear the previous lists to retain only the most recent 100 values.
    pm10_array.clear()
    pm10_avg60_array.clear()
    pm25_array.clear()
    pm25_avg60_array.clear()
    pm1_array.clear()
    pm1_avg60_array.clear()
    aqi_array.clear()

    for entry in feed_data:
        pm10_array.append(entry['field1'])
        pm10_avg60_array.append(entry['field2'])
        pm25_array.append(entry['field3'])
        pm25_avg60_array.append(entry['field4'])
        pm1_array.append(entry['field5'])
        pm1_avg60_array.append(entry['field6'])
        aqi_array.append(entry['field7'])
    all_list_cleanup()  # Changes lists to int type

def all_list_cleanup():
    global pm10_array, pm10_avg60_array, pm25_array, pm25_avg60_array, pm1_array, pm1_avg60_array, aqi_array
    pm10_array = filter_list(pm10_array)
    pm10_avg60_array = filter_list(pm10_avg60_array)
    pm25_array = filter_list(pm25_array)
    pm25_avg60_array = filter_list(pm25_avg60_array)
    pm1_array = filter_list(pm1_array)
    pm1_avg60_array = filter_list(pm1_avg60_array)
    aqi_array = filter_list(aqi_array)

fetch_data()


# Moving and saving arrays to a separate JSON file
arrays_data = {
    "PM10": pm10_array,
    "PM10_avg60": pm10_avg60_array,
    "PM2.5": pm25_array,
    "PM2.5_avg60": pm25_avg60_array,
    "PM1": pm1_array,
    "PM1_avg60": pm1_avg60_array,
    "AQI": aqi_array
}
with open('field_arrays.json', 'w') as json_file:
    json.dump(arrays_data, json_file, indent=4)

# ----------- 3.1.3. Visualizing PM Measurements ------------ #

def show_plots():
    plt.subplots(figsize=(10, 15))
    plt.subplots_adjust(hspace=0.5)

    # Helper function to plot and adjust x-axis length dynamically
    def plot_data(x_axis, y_data, color, title):
        plt.plot(x_axis, y_data, color)
        y_mean = np.mean(y_data)
        plt.axhline(y=y_mean, color=color[0], linestyle=':', label='Mean')
        plt.xlabel('Sample')
        plt.ylabel('ATM')
        plt.title(title)

    # Data arrays for different measurements
    data_arrays = [
        (pm1_array, 'rd-', 'PM1.0'),
        (pm25_array, 'ko-', 'PM2.5'),
        (pm10_array, 'bo-', 'PM10.0'),
        (temp, 'bo-', 'Temperature'),
        (humidity, 'bo-', 'Humidity')
    ]

    # Loop through each data array and plot
    for i, (data, color, title) in enumerate(data_arrays, start=1):
        y_data = np.asarray(data, dtype=float)
        x_axis = range(len(y_data))
        plt.subplot(5, 1, i)
        plot_data(x_axis, y_data, color, title)

    plt.show()



# ---------- 3.2 Local Temperature and Humidity Measurement -------- #

temp = list(buffer_temp)
humidity = list(buffer_hum)

def read_dht():
    global temp, humidity
    instance = dht11.DHT11(pin=gpio_sensor)
    result = instance.read()
    while not result.is_valid():
        result = instance.read()
    print("Temperature: %-3.1f C" % result.temperature)
    print("Humidity: %-3.1f %%" % result.humidity)
    buffer_temp.append(result.temperature)
    buffer_hum.append(result.humidity)
    temp = list(buffer_temp)
    humidity = list(buffer_hum)


# ---------------- 3.3. AQI Calculation --------------- #

PM25_range = [
    (0.0, 12.0, 0, 50),         # (C_low, C_high, I_low, I_high)
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500)
]

# Define PM10 breakpoints
PM10_range = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 604, 301, 500)
]

def AQI_Calculator(concentration, breakpoints):
    concentration = float(concentration)
    for C_low, C_high, I_low, I_high in breakpoints:
        if C_low <= concentration <= C_high:
            return I_low + (I_high - I_low) * (concentration - C_low) / (C_high - C_low)
    return None


#  -------------------------------------  FOR LOOP FOR aqi CALCULATE -----------------------------------------
AQI_PM25_Array = []
AQI_PM10_Array = []
AQI_MAX_Array = []

def AQI_function():
    global AQI_PM25_Array, AQI_PM10_Array, AQI_MAX_Array
    for value_pm25, value_pm10 in zip(pm25_array, pm10_array):  # Assuming pm25_array and pm10_array are defined and contain data
        # Calculate AQI for PM2.5 and PM10
        AQI_PM25 = AQI_Calculator(value_pm25, PM25_range)
        AQI_PM10 = AQI_Calculator(value_pm10, PM10_range)

        # Append AQI values to their respective arrays
        AQI_PM25_Array.append(AQI_PM25)
        AQI_PM10_Array.append(AQI_PM10)

        # Determine the maximum AQI and append to the max array
        max_AQI = max(AQI_PM25, AQI_PM10)
        AQI_MAX_Array.append(max_AQI)

        # Print results
        print(AQI_PM25_Array)
        print(AQI_PM10_Array)
        print(AQI_MAX_Array)
        print("-------")


def send_to_thingspeak():
    global AQI_PM25_Array,AQI_PM10_Array, AQI_MAX_Array
    # ----------- 3.3.2. Transfer AQI levels to a new cloud channel ------------ #
    # Prepare data for ThingSpeak
    thingspeak_url = "https://api.thingspeak.com/update"
    thingspeak_write_key = "VC0WCV4SJWJ568ZK"  # Your write API key for the public channel

    # Loop through the arrays and send the data to ThingSpeak
    for i in range(len(AQI_PM25_Array)):  # Assuming all arrays have the same length (100)
        # Prepare the payload
        payload = {
            'api_key': thingspeak_write_key,  # ThingSpeak API key for authorization
            'field1': AQI_PM25_Array[i],  # i-th entry from PM2.5 array
            'field2': AQI_PM10_Array[i],  # i-th entry from PM10 array
            'field3': AQI_MAX_Array[i]  # i-th entry from max_AQI array
        }

        # Send the request to ThingSpeak
        response = requests.post(thingspeak_url, params=payload)




plots = []

def draw_sensors_plots():
    global plots
    plot_list_pm1 = compress_list(pm1_array)
    plot_list_pm25 = compress_list(pm25_array)
    plot_list_pm10 = compress_list(pm10_array)
    plot_list_temp = compress_list(temp)
    plot_list_hum = compress_list(humidity)
    plots = [plot_list_pm1, plot_list_pm25, plot_list_pm10, plot_list_temp, plot_list_hum]

draw_sensors_plots()
# ---------------------- Forever Loop ------------------- #


while True:
    duration = int(time.time() - start_time)

    # Check every 10 seconds
    if duration % 10 == 0 and duration != last_10_sec_check:
        # Perform actions every 10 seconds
        read_dht()
        compress_list(temp)
        compress_list(humidity)
        #show_plots()
        last_10_sec_check = duration


        # Check every 60 seconds
        if duration % 60 == 0 and duration != last_60_sec_check:
            fetch_data()
            AQI_function()
            send_to_thingspeak()
            draw_sensors_plots()
            last_60_sec_check = duration

    # Iterate through all input pins to check button states
    for gpio_pin in gpio_list_inputs:
        state = RPI.input(gpio_pin)
        time.sleep(0.2)  # Check button state every 0.2 seconds

        # If button is pressed
        if not state:
            if gpio_pin == gpio_button_right:
                plot_position("right")
            elif gpio_pin == gpio_button_left:
                plot_position("left")

    # Draw LED plot based on the current graph position
    draw_led_plot(plots[graph_position])

# The overall framework of the code was developed in a group of four people, with our fellow classmate Umar Bin Ghayas contributing the most.