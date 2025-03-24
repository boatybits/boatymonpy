import uasyncio as asyncio  # Asynchronous I/O library
from machine import Pin, I2C  # Pin and I2C control
from lib.bme280_float import BME280  # BME280 sensor library

class Sensor:
    """Base class for sensors."""
    def __init__(self, name):
        """Initializes the sensor with a name."""
        self.name = name  # Sensor name
        self.data = {}  # Sensor data

    async def read(self):
        """Reads sensor data. Must be implemented by subclasses."""
        raise NotImplementedError  # Abstract method

class BME280Sensor(Sensor):
    """Class for the BME280 sensor."""
    def __init__(self, scl_pin=22, sda_pin=21):
        """Initializes the BME280 sensor with the specified I2C pins."""
        super().__init__("BME280")  # Call the superclass constructor
        self.i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin))  # Initialize I2C
        try:
            self.bme = BME280(i2c=self.i2c)  # Initialize BME280 sensor
            self.initialized = True  # Set initialized flag
        except OSError as e:
            print("Error initializing BME280 sensor:", e)
            self.bme = None  # Set BME280 sensor to None
            self.initialized = False  # Set initialized flag to False

    async def read(self):
        """Reads temperature, pressure, and humidity from the BME280 sensor."""
        if self.initialized:  # Check if the sensor is initialized
            try:
                temperature = self.bme.temperature  # Read temperature
                pressure = self.bme.pressure  # Read pressure
                humidity = self.bme.humidity  # Read humidity
                self.data = {  # Store the data in a dictionary
                    "temperature": temperature,
                    "pressure": pressure,
                    "humidity": humidity,
                }
                print("Temperature: {:.2f} °C, Pressure: {:.2f} hPa, Humidity: {:.2f} %".format(temperature, pressure, humidity))
            except Exception as e:
                print("Error reading BME280 sensor:", e)
                self.data = {}  # Clear the data
        else:
            print("BME280 sensor not initialized")
            self.data = {}  # Clear the data

class SensorManager:
    """Manages all sensors."""
    def __init__(self):
        """Initializes the sensor manager."""
        self.sensors = {}  # Dictionary to store sensors
        self.bme280_sensor = BME280Sensor()  # Create a BME280 sensor
        self.sensors["bme280"] = self.bme280_sensor  # Add the BME280 sensor to the dictionary

    async def read_all(self):
        """Reads data from all sensors."""
        for sensor in self.sensors.values():  # Iterate through all sensors
            await sensor.read()  # Read data from the sensor