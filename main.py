# main.py
import uasyncio as asyncio  # Asynchronous I/O library
import network  # Network management library
import time  # Time-related functions
import config  # Import configuration from config.py
from machine import Pin, I2C  # Pin control, I2C
from sensor_manager import SensorManager  # Import the sensor class

LED_PIN = 2  # Assuming the internal LED is on pin 2, change if needed

class LedController:
    """Manages the LED and its blinking behavior."""
    def __init__(self, pin):
        """Initializes the LED controller with the specified pin."""
        self.led = Pin(pin, Pin.OUT)  # Set the pin as an output
        print("LED pin initialized: %s" % pin) # debug print
    
    async def start_blinking(self, on_time = 0.5, off_time = 0.5, repeats = 0):
        """Blinks the internal LED with configurable repetitions."""
        print("start_blinking function called (repeats=%d)" % (repeats,)) # debug print

        if repeats == 0:
            # Infinite loop
            while True:
                self.led.on()
                print("LED on") # debug print
                await asyncio.sleep(on_time)
                self.led.off()
                print("LED off") # debug print
                await asyncio.sleep(off_time)
        else:
            # Finite repetitions
            for _ in range(repeats):
                self.led.on()
                print("LED on") # debug print
                await asyncio.sleep(on_time)
                self.led.off()
                print("LED off") # debug print
                await asyncio.sleep(off_time)

class WifiManager:
    """Manages the WiFi connection and its status."""
    def __init__(self):
        """Initializes the WiFi manager with credentials from config.py."""
        self.ssid = config.WIFI_SSID
        self.password = config.WIFI_PASSWORD

    async def connect_wifi(self):
        """Connects to the WiFi network using credentials from config.py."""
        print("Connecting to WiFi network: %s" % self.ssid) # debug print
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            sta_if.active(True)
            sta_if.ifconfig((config.IP_ADDRESS, config.SUBNET_MASK, config.GATEWAY, config.DNS_SERVER))
            sta_if.connect(self.ssid, self.password)
            while not sta_if.isconnected():
                await asyncio.sleep(1)
            print("Successfully connected to WiFi network: %s" % self.ssid)
            print("network...", sta_if.ifconfig())

    async def check_wifi_connection(self):
        """Checks WiFi connection and reconnects if disconnected."""
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print("WiFi disconnected! Reconnecting...")
            await self.connect_wifi()
        else:
            print("network...", sta_if.ifconfig())

# Initialize LED Controller
led_controller = LedController(LED_PIN)

# Initialize Wifi Manager
wifi_manager = WifiManager()

# Initialize Sensor Manager
sensor_manager = SensorManager()

async def read_sensors():
    """Reads data from all sensors."""
    await sensor_manager.read_all()  # Read data from all sensors

async def timer_loop():
    while True:
        print("Main loop running")
        await asyncio.sleep(config.LOOP_INTERVAL)

async def periodic_wifi_check(wifi_manager, interval):
    while True:
        await wifi_manager.check_wifi_connection()
        await asyncio.sleep(interval)

async def main():
    """Main function to run the WiFi connection checker."""
    print("Starting WiFi connection checker")
    print("Before starting LED blink task") # debug print
    print("After starting LED blink task") # debug print
    sensors_read = asyncio.create_task(read_sensors())  # Start the sensor reading task
    await wifi_manager.connect_wifi()  # Initial connection with timeout
    wifi_check_task = asyncio.create_task(periodic_wifi_check(wifi_manager, 10))

    
    while True:
        print("Main loop is running", config.LOOP_INTERVAL)
        # Create and await the led_blink task within the loop
        on_time, off_time = 1, 0.25
        led_blink_task = asyncio.create_task(led_controller.start_blinking(on_time, off_time, 0))
        timer_loop_task = asyncio.create_task(timer_loop())
        await asyncio.gather(led_blink_task, timer_loop_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Run the main function
    except KeyboardInterrupt:  # Handle keyboard interrupt
        print("Exiting program")
