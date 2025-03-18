import os
from PIL import Image
import datetime
from typing import Tuple
import math

from p_weather.openweathermap import OpenWeatherMap, OpenWeatherMapSettings
from p_weather.sprites import Sprites
from p_weather.draw_weather import DrawWeather
from p_weather.sunrise import sun

import secrets


class WeatherLandscape:

    TMP_DIR = "tmp"
    OUT_FILENAME = "test_"
    OUT_FILEEXT = ".bmp"
    OUT_GIF_EXT = ".gif"
    TEMPLATE_FILENAME = "p_weather/template.bmp"
    SPRITES_DIR="p_weather/sprite"
    DRAWOFFSET = 65
    ANIMATION_FRAMES = 10  # Number of frames for animation
    ANIMATION_DURATION = 100  # Duration of each frame in milliseconds
    
    # Standard dimensions for all images
    WIDTH = 296
    HEIGHT = 128
    
    # Background colors
    BLACK_BG = (0, 0, 0)
    WHITE_BG = (255, 255, 255)
    DAY_BG = (135, 206, 250)  # Light blue sky
    SUNSET_BG = (65, 105, 225)  # Medium blue for sunset/sunrise
    NIGHT_BG = (0, 0, 30)  # Very dark blue for night

    # Transition times in minutes
    TRANSITION_DURATION = 90  # Minutes before/after sunset/sunrise for color transition

    # Moon phase settings
    MOON_IMG = "pic/moon.png"
    MOON_PHASE_IMG = "tmp/moon_phase.png"
    MOON_TEXT = "tmp/moon.txt"
    MOON_SIZE = 25  # Size of moon to display (25% of the original 40)
    MOON_Y_POS = 5  # Vertical position of the moon


    def __init__(self, use_dynamic_bg=True, use_black_bg=False, use_white_bg=False, show_moon_phase=False):
        """
        Initialize the weather landscape generator
        
        Parameters:
            use_dynamic_bg: bool - Use dynamic background based on time of day
            use_black_bg: bool - Force black background (overrides dynamic)
            use_white_bg: bool - Force white background (overrides dynamic and black)
            show_moon_phase: bool - Show moon phase in the generated image/GIF
        """
        assert secrets.OWM_KEY != "000000000000000000", "Set OWM_KEY variable to your OpenWeather API key in secrets.py"
        
        self.use_dynamic_bg = use_dynamic_bg
        self.use_black_bg = use_black_bg and not use_white_bg  # White overrides black
        self.use_white_bg = use_white_bg
        self.show_moon_phase = show_moon_phase
        
        # Initialize with default background - will be updated during render
        if self.use_white_bg:
            self.background_color = self.WHITE_BG
        elif self.use_black_bg:
            self.background_color = self.BLACK_BG
        else:
            self.background_color = self.DAY_BG

        # Generate moon phase if needed
        if self.show_moon_phase:
            self.process_moon_phase()


    def process_moon_phase(self):
        """Process moon phase image if moon display is enabled"""
        try:
            from p_weather.moon_func import process_moon_phase
            
            # Ensure tmp directory exists
            os.makedirs(self.TMP_DIR, exist_ok=True)
            
            # Process moon phase and save the image
            self.moon_data = process_moon_phase(
                moonpath=self.MOON_IMG,
                phasepath=self.MOON_PHASE_IMG,
                textpath=self.MOON_TEXT
            )
            
            # Load the processed moon phase image
            self.moon_phase_img = Image.open(self.MOON_PHASE_IMG).convert("RGBA")
            
            # Resize if needed (maintain aspect ratio)
            width, height = self.moon_phase_img.size
            ratio = width / height
            new_width = self.MOON_SIZE
            new_height = int(new_width / ratio)
            self.moon_phase_img = self.moon_phase_img.resize((new_width, new_height), Image.LANCZOS)
            
        except ImportError:
            print("Warning: moon_func module not found. Moon phase will not be displayed.")
            self.show_moon_phase = False
        except Exception as e:
            print(f"Error processing moon phase: {e}")
            self.show_moon_phase = False


    def get_background_color(self, current_time: datetime.datetime, sunrise_time: datetime.datetime, sunset_time: datetime.datetime) -> Tuple[int, int, int]:
        """
        Calculate background color based on time of day
        
        Parameters:
            current_time: datetime - Current time
            sunrise_time: datetime - Sunrise time
            sunset_time: datetime - Sunset time
            
        Returns:
            tuple: RGB color tuple for background
        """
        if self.use_white_bg:
            return self.WHITE_BG
        elif self.use_black_bg:
            return self.BLACK_BG
        elif not self.use_dynamic_bg:
            return self.DAY_BG
        
        # Convert transition duration to seconds
        transition_sec = self.TRANSITION_DURATION * 60
        
        def time_to_seconds(dt):
            return dt.hour * 3600 + dt.minute * 60 + dt.second
        
        current_seconds = time_to_seconds(current_time)
        sunrise_seconds = time_to_seconds(sunrise_time)
        sunset_seconds = time_to_seconds(sunset_time)
        
        # Handle case where sunset is before sunrise (next day)
        if sunset_seconds < sunrise_seconds:
            sunset_seconds += 24 * 3600
            
        # If current time is after midnight but before sunrise, adjust
        if current_seconds < sunrise_seconds:
            current_seconds += 24 * 3600
            
        # Calculate transition periods
        sunrise_start = sunrise_seconds - transition_sec
        sunrise_end = sunrise_seconds + transition_sec
        sunset_start = sunset_seconds - transition_sec
        sunset_end = sunset_seconds + transition_sec
        
        # Night period (after sunset transition ends to before sunrise transition starts)
        if current_seconds >= sunset_end or current_seconds <= sunrise_start:
            return self.NIGHT_BG
            
        # Day period (after sunrise transition ends to before sunset transition starts)
        elif current_seconds >= sunrise_end and current_seconds <= sunset_start:
            return self.DAY_BG
            
        # Sunrise transition
        elif current_seconds > sunrise_start and current_seconds < sunrise_end:
            progress = (current_seconds - sunrise_start) / (2 * transition_sec)
            return self.interpolate_color(self.NIGHT_BG, self.DAY_BG, progress)
            
        # Sunset transition
        else:  # current_seconds > sunset_start and current_seconds < sunset_end
            progress = (current_seconds - sunset_start) / (2 * transition_sec)
            return self.interpolate_color(self.DAY_BG, self.NIGHT_BG, progress)


    def interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], progress: float) -> Tuple[int, int, int]:
        """
        Interpolate between two colors
        
        Parameters:
            color1: tuple - Starting RGB color
            color2: tuple - Ending RGB color
            progress: float - Progress from 0.0 (color1) to 1.0 (color2)
            
        Returns:
            tuple: Interpolated RGB color
        """
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)


    def MakeImage(self)->Image:
        """Create a single static weather landscape image"""
        cfg = OpenWeatherMapSettings.Fill(secrets, self.TMP_DIR)
        owm = OpenWeatherMap(cfg)
        owm.FromAuto()

        # Get current time and sunrise/sunset times
        current_time = datetime.datetime.now()
        s = sun(owm.LAT, owm.LON)
        sunrise_time = s.sunrise(current_time)
        sunset_time = s.sunset(current_time)

        # Determine background color based on time of day
        bg_color = self.get_background_color(current_time, sunrise_time, sunset_time)
        
        # Create a fresh canvas with the determined background color
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=bg_color)

        # Initialize sprites
        spr = Sprites(self.SPRITES_DIR, img)
        
        # Adjust colors based on background brightness
        is_dark_bg = self.is_dark_background(bg_color)
        spr.adjust_colors_for_background(is_dark_bg)

        art = DrawWeather(img, spr)
        art.Draw(self.DRAWOFFSET, owm, animate=False, frame_num=0, show_moon_phase=self.show_moon_phase)

        # Add moon phase if enabled
        if self.show_moon_phase and hasattr(self, 'moon_phase_img'):
            # Calculate moon position based on sunset time
            t = datetime.datetime.now()
            dt = datetime.timedelta(hours=3)  # Default time step used in DrawWeather
            
            # Get x-position for sunset time
            x_offset = DrawWeather.XSTART
            sunset_pos_x = self.calculate_moon_position(t, sunset_time, dt, DrawWeather.XSTART, DrawWeather.XSTEP)
            
            # Convert img to RGBA to support transparency
            img_rgba = img.convert("RGBA")
            
            # Determine position - center the moon image at the sunset position
            moon_width = self.moon_phase_img.width
            x_pos = sunset_pos_x - (moon_width // 2)
            
            # Paste moon phase with transparency
            img_rgba.paste(self.moon_phase_img, (x_pos, self.MOON_Y_POS), self.moon_phase_img)
            
            # Convert back to RGB
            img = img_rgba.convert("RGB")

        return img

    def calculate_moon_position(self, current_time, sunset_time, time_step, x_start, x_step):
        """
        Calculate the horizontal position for the moon based on sunset time
        
        Parameters:
            current_time: datetime - Current time
            sunset_time: datetime - Sunset time
            time_step: timedelta - Time interval per step
            x_start: int - Starting x-position for drawing
            x_step: int - Horizontal step size
            
        Returns:
            int: X-position for the moon
        """
        # Calculate seconds per pixel
        forecast_hours = 3.0  # Matches the WeatherInfo.FORECAST_PERIOD_HOURS used in DrawWeather
        seconds_per_pixel = (forecast_hours * 3600) / x_step
        
        # If sunset is before current time, add a day to sunset
        if sunset_time < current_time:
            sunset_time = sunset_time + datetime.timedelta(days=1)
            
        # Calculate time difference and convert to pixels
        diff_seconds = (sunset_time - current_time).total_seconds()
        diff_pixels = int(diff_seconds / seconds_per_pixel)
        
        # Return the sunset position
        x_pos = x_start + diff_pixels
        
        # Ensure the position is within bounds
        if x_pos < x_start:
            x_pos = x_start
        elif x_pos >= self.WIDTH:
            x_pos = self.WIDTH - 1
            
        return x_pos


    def is_dark_background(self, color: Tuple[int, int, int]) -> bool:
        """
        Determine if a background color is considered dark
        
        Parameters:
            color: tuple - RGB color to evaluate
            
        Returns:
            bool: True if the color is considered dark, False otherwise
        """
        # Calculate perceived brightness using weighted RGB values
        # Formula: (0.299*R + 0.587*G + 0.114*B)
        brightness = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        return brightness < 128


    def MakeAnimatedGif(self)->list:
        """Create an animated GIF of the weather landscape with rain and wind animations"""
        cfg = OpenWeatherMapSettings.Fill(secrets, self.TMP_DIR)
        owm = OpenWeatherMap(cfg)
        owm.FromAuto()
        
        # Get current time and sunrise/sunset times
        current_time = datetime.datetime.now()
        s = sun(owm.LAT, owm.LON)
        sunrise_time = s.sunrise(current_time)
        sunset_time = s.sunset(current_time)

        # Determine background color based on time of day
        bg_color = self.get_background_color(current_time, sunrise_time, sunset_time)
        
        # Whether background is dark or light
        is_dark_bg = self.is_dark_background(bg_color)
        
        frames = []
        
        # Calculate moon position for sunset
        t = datetime.datetime.now()
        dt = datetime.timedelta(hours=3)  # Default time step
        sunset_pos_x = self.calculate_moon_position(t, sunset_time, dt, DrawWeather.XSTART, DrawWeather.XSTEP)
        
        for frame_num in range(self.ANIMATION_FRAMES):
            # Create a fresh canvas for each frame with consistent dimensions and background color
            img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=bg_color)
            
            # Initialize sprites with the current frame number for animation
            spr = Sprites(self.SPRITES_DIR, img)
            spr.current_frame = frame_num
            spr.total_frames = self.ANIMATION_FRAMES
            
            # Adjust colors based on background brightness
            spr.adjust_colors_for_background(is_dark_bg)
            
            # Draw the weather landscape
            art = DrawWeather(img, spr)
            art.Draw(self.DRAWOFFSET, owm, animate=True, frame_num=frame_num, show_moon_phase=self.show_moon_phase)
            
            # Add moon phase if enabled
            if self.show_moon_phase and hasattr(self, 'moon_phase_img'):
                # Convert img to RGBA to support transparency
                img_rgba = img.convert("RGBA")
                
                # Determine position - center the moon image at the sunset position
                moon_width = self.moon_phase_img.width
                x_pos = sunset_pos_x - (moon_width // 2)
                
                # Paste moon phase with transparency
                img_rgba.paste(self.moon_phase_img, (x_pos, self.MOON_Y_POS), self.moon_phase_img)
                
                # Convert back to RGB
                img = img_rgba.convert("RGB")
            
            frames.append(img)
        
        return frames


    def SaveImage(self)->str:
        """Save a static weather landscape image"""
        img = self.MakeImage() 
        placekey = OpenWeatherMap.MakePlaceKey(secrets.OWM_LAT, secrets.OWM_LON)
        
        # Determine filename suffix based on background mode
        if self.use_white_bg:
            bg_indicator = "white"
        elif self.use_black_bg:
            bg_indicator = "black"
        else:
            bg_indicator = "dynamic"
            
        outfilepath = self.TmpFilePath(f"{self.OUT_FILENAME}{placekey}_{bg_indicator}{self.OUT_FILEEXT}")
        img.save(outfilepath) 
        return outfilepath


    def SaveAnimatedGif(self)->str:
        """Save an animated weather landscape GIF"""
        frames = self.MakeAnimatedGif()
        placekey = OpenWeatherMap.MakePlaceKey(secrets.OWM_LAT, secrets.OWM_LON)
        
        # Determine filename suffix based on background mode
        if self.use_white_bg:
            bg_indicator = "white"
        elif self.use_black_bg:
            bg_indicator = "black"
        else:
            bg_indicator = "dynamic"
            
        # Add moon indicator if moon phase is shown
        moon_indicator = "_moon" if self.show_moon_phase else ""
            
        outfilepath = self.TmpFilePath(f"{self.OUT_FILENAME}{placekey}_{bg_indicator}{moon_indicator}{self.OUT_GIF_EXT}")
        
        # Save as animated GIF with consistent frame handling
        frames[0].save(
            outfilepath,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=self.ANIMATION_DURATION,
            loop=0,  # Loop forever
            disposal=2  # Dispose previous frame to ensure background is preserved
        )
        
        return outfilepath


    def TmpFilePath(self,filename):
        return os.path.join(self.TMP_DIR,filename)