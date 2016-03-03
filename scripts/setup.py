from setuptools import setup

setup(
    name='esp8266-leds',
    version='0.1.0',
    description='Utilities for controlling WS1812 LED strips with an Espressif ESP8266.',
    url='https://github.com/jmechnich/esp8266-leds',
    author='Joerg Mechnich',
    author_email='joerg.mechnich@gmail.com',
    license='MIT',
    packages=[
        'esp8266leds',
    ],
    scripts=[
        'ledclient.py',
    ],
)
