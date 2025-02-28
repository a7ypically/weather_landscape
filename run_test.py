import os
import sys
import argparse
from weather_landscape import WeatherLandscape

# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate weather landscape images')
parser.add_argument('--animated', '-a', action='store_true', help='Generate an animated GIF')
parser.add_argument('--white-bg', '-w', action='store_true', help='Use white background')
parser.add_argument('--black-bg', '-b', action='store_true', help='Use black background')
parser.add_argument('--dynamic-bg', '-d', action='store_true', help='Use dynamic background that changes with time of day (default)')
args = parser.parse_args()

# If no background option is specified, use dynamic background by default
if not (args.white_bg or args.black_bg or args.dynamic_bg):
    args.dynamic_bg = True

# Create WeatherLandscape with appropriate background settings
w = WeatherLandscape(
    use_dynamic_bg=args.dynamic_bg,
    use_black_bg=args.black_bg,
    use_white_bg=args.white_bg
)

# Generate either static image or animated GIF
if args.animated:
    fn = w.SaveAnimatedGif()
    print("Saved animated GIF:", fn)
else:
    fn = w.SaveImage()
    print("Saved static image:", fn)


