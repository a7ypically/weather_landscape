#!/usr/bin/python3

import ephem
import math
from PIL import Image

def process_moon_phase(moonpath="moon.png", phasepath="phase.png", textpath="moon.txt"):
    """
    Processes a full-moon image to simulate the moon phase effect,
    writes the processed image and moon parameters to files,
    and returns the computed values.

    Parameters:
        moonpath (str): Path to the input full-moon image.
        phasepath (str): Path where the output phase image will be saved.
        textpath (str): Path where the output text file will be saved.

    Returns:
        dict: A dictionary containing:
            - age: Moon age in percent (new moon=0%, full moon=50%).
            - illumination: Illumination in percent (new moon=0%, full moon=100%).
            - distance: Moon distance in Km.
            - next_full_moon: Next full moon date and local time as a formatted string.
    """
    # Compute moon parameters using ephem.
    m = ephem.Moon()
    s = ephem.Sun()
    m.compute()
    s.compute()
    sun_glon = ephem.degrees(s.hlon + math.pi).norm
    moon_glon = m.hlon
    age = ephem.degrees(moon_glon - sun_glon).norm
    age = age / (2 * math.pi) * 100  # new moon=0%, full moon=50%
    
    au = ephem.meters_per_au
    m_au = m.earth_distance
    dist = m_au * au / 1000         # Moon distance in Km
    
    a = m.elong
    dt = ephem.next_full_moon(ephem.now())
    dtlocal = ephem.localtime(dt)
    fullmoon = dtlocal.strftime('%d %b, %H:%M')
    
    phase = m.moon_phase
    illum = phase * 100             # Illumination: new moon=0%, full moon=100%
    phase = 1 - phase
    if a > 0:
        phase = -phase

    # Open the image using PIL and ensure it has an alpha channel.
    img = Image.open(moonpath).convert("RGBA")
    width, height = img.size
    radius = height // 2

    # Access the pixel data for modifications.
    pixels = img.load()

    # Process the image based on the phase.
    if phase < 0:
        phase = abs(phase)
        for y in range(radius):
            # Calculate x-offset using the circle equation.
            x_offset = round(math.sqrt(radius**2 - y**2))
            X = radius - x_offset
            Y_top = radius - y
            Y_bottom = radius + y
            moon_width = 2 * (radius - X)
            clear_width = round(moon_width * phase)
            x_clear = X + clear_width
            # Set alpha=0 for pixels in the dark region.
            for cx in range(X, x_clear):
                r, g, b, _ = pixels[cx, Y_top]
                pixels[cx, Y_top] = (r, g, b, 0)
                if Y_top != Y_bottom and Y_bottom < height:
                    r, g, b, _ = pixels[cx, Y_bottom]
                    pixels[cx, Y_bottom] = (r, g, b, 0)
    elif phase > 0:
        phase = abs(phase)
        for y in range(radius):
            x_offset = round(math.sqrt(radius**2 - y**2))
            X = radius + x_offset
            Y_top = radius - y
            Y_bottom = radius + y
            moon_width = 2 * (radius - X)
            clear_width = round(moon_width * phase)
            x_clear = X + clear_width  # x_clear is less than X.
            for cx in range(x_clear, X):
                r, g, b, _ = pixels[cx, Y_top]
                pixels[cx, Y_top] = (r, g, b, 0)
                if Y_top != Y_bottom and Y_bottom < height:
                    r, g, b, _ = pixels[cx, Y_bottom]
                    pixels[cx, Y_bottom] = (r, g, b, 0)

    # Save the modified image.
    img.save(phasepath)

    # Write the computed data to the text file.
    with open(textpath, "w") as file:
        file.write("{:.2f}\n".format(age))
        file.write("{:.2f}\n".format(illum))
        file.write("{:.0f}\n".format(dist))
        file.write("{}\n".format(fullmoon))

    # Return the computed moon parameters.
    return {
        "age": age,
        "illumination": illum,
        "distance": dist,
        "next_full_moon": fullmoon
    }

if __name__ == "__main__":
    # For testing when running this file directly.
    results = process_moon_phase()
    print("Moon Phase Results:")
    print(results)

