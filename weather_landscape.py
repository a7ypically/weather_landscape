import os
from PIL import Image


from p_weather.openweathermap import OpenWeatherMap,OpenWeatherMapSettings
from p_weather.sprites import Sprites
from p_weather.draw_weather import DrawWeather

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


    def __init__(self):
        assert secrets.OWM_KEY != "000000000000000000", "Set OWM_KEY variable to your OpenWeather API key in secrets.py"
        pass


    def MakeImage(self)->Image:
        """Create a single static weather landscape image"""
        cfg = OpenWeatherMapSettings.Fill(secrets, self.TMP_DIR)
        owm = OpenWeatherMap(cfg)
        owm.FromAuto()

        # Open the template image and convert it to RGB mode to support colors
        img = Image.open(self.TEMPLATE_FILENAME).convert("RGB")

        spr = Sprites(self.SPRITES_DIR, img)

        art = DrawWeather(img, spr)
        art.Draw(self.DRAWOFFSET, owm)

        return img
        
        
    def MakeAnimatedGif(self)->list:
        """Create an animated GIF of the weather landscape with rain and wind animations"""
        cfg = OpenWeatherMapSettings.Fill(secrets, self.TMP_DIR)
        owm = OpenWeatherMap(cfg)
        owm.FromAuto()
        
        frames = []
        
        for frame_num in range(self.ANIMATION_FRAMES):
            # Create a fresh canvas for each frame
            img = Image.open(self.TEMPLATE_FILENAME).convert("RGB")
            
            # Initialize sprites with the current frame number for animation
            spr = Sprites(self.SPRITES_DIR, img)
            spr.current_frame = frame_num
            spr.total_frames = self.ANIMATION_FRAMES
            
            # Draw the weather landscape
            art = DrawWeather(img, spr)
            art.Draw(self.DRAWOFFSET, owm, animate=True, frame_num=frame_num)
            
            frames.append(img)
        
        return frames


    def SaveImage(self)->str:
        """Save a static weather landscape image"""
        img = self.MakeImage() 
        placekey = OpenWeatherMap.MakePlaceKey(secrets.OWM_LAT,secrets.OWM_LON)
        outfilepath = self.TmpFilePath(self.OUT_FILENAME+placekey+self.OUT_FILEEXT)
        img.save(outfilepath) 
        return outfilepath
        
    
    def SaveAnimatedGif(self)->str:
        """Save an animated weather landscape GIF"""
        frames = self.MakeAnimatedGif()
        placekey = OpenWeatherMap.MakePlaceKey(secrets.OWM_LAT,secrets.OWM_LON)
        outfilepath = self.TmpFilePath(self.OUT_FILENAME+placekey+self.OUT_GIF_EXT)
        
        # Save as animated GIF
        frames[0].save(
            outfilepath,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=self.ANIMATION_DURATION,
            loop=0  # Loop forever
        )
        
        return outfilepath
        

    def TmpFilePath(self,filename):
        return os.path.join(self.TMP_DIR,filename)