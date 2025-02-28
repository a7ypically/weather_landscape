import os
import sys
from weather_landscape import WeatherLandscape

# Parse command line arguments for animation option
animated = "--animated" in sys.argv or "-a" in sys.argv

w = WeatherLandscape()

if animated:
    fn = w.SaveAnimatedGif()
    print("Saved animated GIF:", fn)
else:
    fn = w.SaveImage()
    print("Saved static image:", fn)


