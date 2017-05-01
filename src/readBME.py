from machine import I2C
import bme280

i2c = I2C(0,)

bme = bme280.BME280(i2c=i2c)

print(bme.temperature, bme.pressure, bme.humidity)
