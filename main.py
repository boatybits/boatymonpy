# main.py
import uasyncio as asyncio  # Asynchronous I/O library
import network  # Network management library
import time  # Time-related functions
import config  # Import configuration from config.py
from machine import Pin  # Pin control
from sensor_manager import SensorManager  # Import the sensor class

LED_PIN = 2  # Assuming the internal LED is on pin 2, change if needed

class LedController:
    """Manages the LED and its blinking behavior."""
    def __init__(self, pin):
        """Initializes the LED controller with the specified pin."""
        self.led = Pin(pin, Pin.OUT)  # Set the pin as an output
        print("LED pin initialized: %s" % pin) # debug print

    async def blink_led(self, on_time, off_time, repeats=1):
        """Blinks the internal LED with a specified on and off time for a given number of repeats."""
        print("blink_led function called") # debug print
        for _ in range(repeats):  # Repeat the blinking pattern
            self.led.on()  # Turn the LED on
            print("LED on") # debug print
            await asyncio.sleep(on_time)  # Wait for the specified on time
            self.led.off()  # Turn the LED off
            print("LED off") # debug print
            await asyncio.sleep(off_time)  # Wait for the specified off time

class WifiManager:
    """Manages the WiFi connection and its status."""
    def __init__(self):
        """Initializes the WiFi manager."""
        self.sta_if = network.WLAN(network.STA_IF)  # Station interface
        self.sta_if.active(True)  # Activate the interface

    async def connect_wifi(self):
        """Connects to the specified WiFi network."""
        if self.sta_if.isconnected():  # Check if already connected
            print("WiFi already connected")
            return True

        print("Attempting to connect to WiFi: {}".format(config.WIFI_SSID))
        # Set static IP address
        print(config.WIFI_SSID, config.WIFI_PASSWORD)
        self.sta_if.ifconfig((config.IP_ADDRESS, config.SUBNET_MASK, config.GATEWAY, config.DNS_SERVER))  # IP, Subnet, Gateway, DNS
        self.sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)  # Connect to the WiFi network
        # Wait for connection with a timeout
        if self.sta_if.status() == network.STAT_GOT_IP:  # Check if connection was successful
            print("WiFi connected")
            ip, subnet, gateway, dns = self.sta_if.ifconfig()  # Get network configuration
            print('network config:', self.sta_if.ifconfig())
            # Flash LED rapidly for 2 seconds
            await led_controller.blink_led(0.2, 0.2, 5)  # Flash 5 times (0.2s on, 0.2s off) = 2 seconds
            return True
        else:
            print("Connection attempt failed")
        return False

    async def check_wifi_connection(self):
        """Checks the WiFi connection status and reconnects if necessary."""
        while True:  # Run indefinitely
            if self.sta_if.isconnected():  # Check if connected
                print("WiFi is connected")
            else:
                print("WiFi is disconnected, attempting to reconnect")
                if not await self.connect_wifi():  # Attempt to reconnect
                    print("Failed to connect to {}, sleeping for {} seconds".format(config.WIFI_SSID, config.NETWORK_SLEEP))
                    await asyncio.sleep(config.NETWORK_SLEEP)  # Sleep before retrying
                    continue
            await asyncio.sleep(config.CHECK_INTERVAL)  # Wait before checking again

# Initialize LED Controller
led_controller = LedController(LED_PIN)

# Initialize Wifi Manager
wifi_manager = WifiManager()

# Initialize Sensor Manager
sensor_manager = SensorManager()

async def read_sensors():
    """Reads data from all sensors."""
    while True:  # Run indefinitely
        await sensor_manager.read_all()  # Read data from all sensors
        await asyncio.sleep(5)  # Read sensor data every 5 seconds

async def main():
    """Main function to run the WiFi connection checker."""
    print("Starting WiFi connection checker")
    asyncio.create_task(read_sensors())  # Start the sensor reading task
    wifi_manager.connect_wifi() #remove await so main continues
    asyncio.create_task(wifi_manager.check_wifi_connection())
    while True:
        asyncio.create_task(led_controller.blink_led(0.5, 1.5))  # Start the LED blinking task with default values
        await asyncio.sleep(1)  # Keep the main loop running

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Run the main function
    except KeyboardInterrupt:  # Handle keyboard interrupt
        print("Exiting program")