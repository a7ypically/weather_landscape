import os
from PIL import Image, ImageOps, ImageEnhance
import random
import math

class Sprites():

    DISABLED = -999999

    Black = 0
    White = 1

    BLACK=0
    WHITE=1
    RED=2
    TRANS=3

    # Define new colors - these will be indices into our color_palette
    BLUE = 4
    GREEN = 5
    YELLOW = 6
    ORANGE = 7
    PURPLE = 8
    CYAN = 9
    BROWN = 10
    PINK = 11
    GRAY = 12
    
    PLASSPRITE = 10
    MINUSSPRITE = 11
    
    EXT = ".png"
    

    def __init__(self, spritesdir, canvas):
        self.img = canvas
        self.pix = self.img.load()
        self.dir = spritesdir
        self.ext = self.EXT
        self.w, self.h = self.img.size
        # Animation properties
        self.current_frame = 0
        self.total_frames = 1
        # Define RGB colors for each color index
        self.color_palette = {
            self.BLACK: (0, 0, 0),       # Black
            self.WHITE: (255, 255, 255), # White
            self.RED: (255, 0, 0),       # Red
            self.BLUE: (0, 0, 255),      # Blue
            self.GREEN: (0, 175, 0),     # Green
            self.YELLOW: (255, 255, 0),  # Yellow
            self.ORANGE: (255, 165, 0),  # Orange
            self.PURPLE: (128, 0, 128),  # Purple
            self.CYAN: (0, 255, 255),    # Cyan
            self.BROWN: (139, 69, 19),   # Brown
            self.PINK: (255, 192, 203),  # Pink
            self.GRAY: (128, 128, 128)   # Gray
        }
        # Initialize rain animation data
        self.rain_drops = []
        
        # Store positions of static elements to keep them consistent across frames
        self.cloud_positions = {}  # key: (xpos, ypos, width) -> value: list of positions
        self.wind_positions = {}   # key: (speed, direction, xpos) -> value: positions, mirror states, etc.


    def Dot(self, x, y, color):
        if (y>=self.h) or (x>=self.w) or (y<0) or (x<0):
            return
        
        # If color is an index, convert it to RGB color
        if isinstance(color, int) and color in self.color_palette:
            self.pix[x,y] = self.color_palette[color]
        else:
            self.pix[x,y] = color

    def get_color_by_name(self, name, index):
        """Determine appropriate color based on sprite name"""
        if name == "sun":
            return self.YELLOW
        elif name == "moon":
            return self.CYAN
        elif name == "cloud":
            return self.GRAY
        elif name == "flower":
            return self.PINK if index % 2 == 0 else self.PURPLE
        elif name == "house":
            return self.BROWN
        elif name == "tree":
            return self.GREEN
        elif name == "pine":
            return self.GREEN
        elif name == "palm":
            return self.GREEN
        elif name == "east":
            return self.GREEN
        elif name == "temp":
            return self.RED
        elif name == "digit":
            return self.BLACK
        else:
            return self.BLACK

    def Draw(self, name, index, xpos, ypos, ismirror=False):
        if (xpos<0) or (ypos<0):
            return 0
    
        imagefilename = "%s_%02i%s" % (name, index, self.ext)
        imagepath = os.path.join(self.dir, imagefilename) 
        img = Image.open(imagepath)
        
        # Get appropriate color for this sprite
        color_id = self.get_color_by_name(name, index)
        color = self.color_palette[color_id]
        
        if (ismirror):
            img = ImageOps.mirror(img)
        w, h = img.size
        pix = img.load()
        ypos -= h
        for x in range(w):
            for y in range(h):
                if (xpos+x>=self.w) or (xpos+x<0):
                    continue
                if (ypos+y>=self.h) or (ypos+y<0):
                    continue
                if (pix[x,y]==self.BLACK):
                    self.pix[xpos+x, ypos+y] = color  # Use the RGB color directly
                elif (pix[x,y]==self.WHITE):
                    self.pix[xpos+x, ypos+y] = self.color_palette[self.WHITE]
                elif (pix[x,y]==self.RED):
                    self.pix[xpos+x, ypos+y] = self.color_palette[self.RED]

        return w


    DIGITPLAS = 10
    DIGITMINUS = 11
    DIGITSEMICOLON = 12

    def DrawInt(self,n,xpos,ypos,issign=True,mindigits=1):
        n = round(n)
        if (n<0):
            sign = self.DIGITMINUS
        else:
            sign = self.DIGITPLAS
        n = round(n)
        n = abs(n)
        n0 = int( n / 100 )
        n1 = int( (n % 100) / 10 )
        n2 = n % 10
        dx = 0
        if (issign) or (sign == self.DIGITMINUS):
            w = self.Draw("digit",sign,xpos+dx,ypos)
            dx+=w+1
        if (n0!=0) or (mindigits>=3):
            w = self.Draw("digit",n0,xpos+dx,ypos)
            dx+=w
            if (n0!=1):
                dx+=1
        if (n1!=0) or (n0!=0)  or (mindigits>=2):
            if (n1==1):
                dx -=1
            w = self.Draw("digit",n1,xpos+dx,ypos)
            dx+=w
            if (n1!=1):
                dx+=1
        if (n2==1):
            dx -=1                
        w = self.Draw("digit",n2,xpos+dx,ypos)
        dx+=w
        if (n2!=1):
            dx +=1                
        return dx

    def DrawClock(self,xpos,ypos,h,m):
        dx=0
        w = self.DrawInt(h,xpos+dx,ypos,False,2)
        dx+=w
        w = self.Draw("digit",self.DIGITSEMICOLON,xpos+dx,ypos)
        dx+=w
        dx = self.DrawInt(m,xpos+dx,ypos,False,2)
        dx+=w+1
        return dx

    CLOUDWMAX = 32
    CLOUDS = [2,3,5,10,30,50]
    CLOUDK = 0.5

    def DrawCloud(self, persent, xpos, ypos, width, height, animate=False):
        """Draw clouds with consistent positions across animation frames"""
        if (persent<2):
            return
        elif (persent<5):
            cloudset = [2]
        elif (persent<10):
            cloudset = [3,2]
        elif (persent<20):
            cloudset = [5,3,2]
        elif (persent<30):
            cloudset = [10,5]
        elif (persent<40):
            cloudset = [10,10]
        elif (persent<50):
            cloudset = [10,10,5]
        elif (persent<60):
            cloudset = [30,5]
        elif (persent<70):
            cloudset = [30,10]
        elif (persent<80):
            cloudset = [30,10,5,5]
        elif (persent<90):
            cloudset = [30,10,10]
        else:
            cloudset = [50,30,10,10,5]

        # Generate a unique key for this cloud configuration
        cloud_key = (xpos, ypos, width, persent)
        
        # If we haven't stored positions for these clouds yet, generate and save them
        if cloud_key not in self.cloud_positions:
            positions = []
            for c in cloudset:
                pos_x = xpos + random.randrange(width)
                positions.append((c, pos_x))
            self.cloud_positions[cloud_key] = positions
        
        # Use pre-generated positions to ensure consistency across frames
        for c, pos_x in self.cloud_positions[cloud_key]:
            self.Draw("cloud", c, pos_x, ypos)
        
    HEAVYRAIN = 5.0
    RAINFACTOR = 20

    def DrawRain(self, value, xpos, ypos, width, tline, animate=False):
        """Draw rain with optional animation"""
        ypos += 1
        r = 1.0 - (value / self.HEAVYRAIN) / self.RAINFACTOR
        blue_color = self.color_palette[self.BLUE]
        
        # If we're animating, initialize rain drops on first frame
        if animate and not self.rain_drops:
            # Generate rain drops
            drop_count = int(width * value * 2)  # Number of drops based on rain intensity
            for _ in range(drop_count):
                # Random position and animation timing
                drop_x = xpos + random.randrange(width)
                drop_y_start = ypos + random.randrange(20)  # Start position varies
                drop_length = random.randint(1, 3)  # Raindrop length
                # Speed varies slightly between frames
                speed = random.uniform(0.8, 1.2)
                # Each raindrop gets a random start frame
                start_frame = random.randrange(self.total_frames)
                
                self.rain_drops.append({
                    'x': drop_x,
                    'y': drop_y_start,
                    'length': drop_length,
                    'speed': speed,
                    'start_frame': start_frame
                })
                
        if animate:
            # Draw animated raindrops
            for drop in self.rain_drops:
                # Only draw if raindrop is active in this frame
                frame_offset = (self.current_frame - drop['start_frame']) % self.total_frames
                # Calculate position based on current frame
                drop_y = drop['y'] + (frame_offset * drop['speed'] * 10)
                
                # Loop the raindrop if it goes below the terrain line
                if drop_y >= tline[drop['x']]:
                    # Create splash effect
                    if random.random() > 0.5:
                        self.Dot(drop['x'] - 1, tline[drop['x']] - 1, blue_color)
                        self.Dot(drop['x'] + 1, tline[drop['x']] - 1, blue_color)
                    continue
                    
                # Draw the raindrop
                for i in range(drop['length']):
                    self.Dot(drop['x'], int(drop_y - i), blue_color)
        else:
            # Draw static rain (original implementation)
            for x in range(xpos, xpos + width):
                for y in range(ypos, tline[x], 2):
                    if (x >= self.w) or (y >= self.h): 
                        continue
                    if (random.random() > r):
                        self.pix[x, y] = blue_color
                        self.pix[x, y-1] = blue_color
        
    HEAVYSNOW = 5.0
    SNOWFACTOR = 10
    
    def DrawSnow(self, value, xpos, ypos, width, tline):
        ypos+=1
        r = 1.0 - (value / self.HEAVYSNOW) / self.SNOWFACTOR 
        cyan_color = self.color_palette[self.CYAN]

        for x in range(xpos, xpos + width):
            for y in range(ypos, tline[x], 2):
                if (x >= self.w): 
                    continue
                if (y >= self.h): 
                    continue
                if (random.random() > r):
                    self.pix[x, y] = cyan_color

    def DrawWind_degdist(self, deg1, deg2):
        h = max(deg1, deg2)
        l = min(deg1, deg2)
        d = h - l
        if (d > 180):
            d = 360 - d
        return d

    def DrawWind_dirsprite(self, dir, dir0, name, list):
        count = [4, 3, 3, 2, 2, 1, 1]
        step = 11.25  # degrees
        dist = self.DrawWind_degdist(dir, dir0)
        n = int(dist / step)
        if (n < len(count)):
            for i in range(0, count[n]):
                list.append(name)

    def DrawWind(self, speed, direction, xpos, tline, animate=False):
        """Draw wind with consistent tree positions across animation frames"""
        wind_key = (speed, direction, xpos)
        
        # If this is the first time drawing this wind or not animating, generate positions
        if wind_key not in self.wind_positions:
            list = []
            self.DrawWind_dirsprite(direction, 0, "pine", list)
            self.DrawWind_dirsprite(direction, 90, "east", list)
            self.DrawWind_dirsprite(direction, 180, "palm", list)
            self.DrawWind_dirsprite(direction, 270, "tree", list)

            # Set the random seed based on the wind parameters for consistent shuffling
            random_seed = int(speed * 1000 + direction)
            random.seed(random_seed)
            random.shuffle(list)

            windindex = None
            if (speed <= 0.4):
                windindex = []
            elif (speed <= 0.7):
                windindex = [0]
            elif (speed <= 1.7):
                windindex = [1, 0, 0]
            elif (speed <= 3.3):
                windindex = [1, 1, 0, 0]
            elif (speed <= 5.2):
                windindex = [1, 2, 0, 0]
            elif (speed <= 7.4):
                windindex = [1, 2, 2, 0]
            elif (speed <= 9.8):
                windindex = [1, 2, 3, 0]
            elif (speed <= 12.4):
                windindex = [2, 2, 3, 0]            
            else:
                windindex = [3, 3, 3, 3]
                
            if windindex is None:
                return
                
            random.shuffle(windindex)
            
            # Store all positioning data for trees
            tree_data = []
            ix = int(xpos)
            j = 0
            
            for i in windindex:
                # Use deterministic "random" offsets based on wind parameters
                random.seed(ix * 1000 + j + int(speed * 100))
                xx = ix + random.randint(-1, 1)
                ismirror = random.random() < 0.5
                offset = xx + 5

                if (offset >= len(tline)):
                    break
                
                if (ismirror):
                    xx -= 16

                tree_data.append({
                    'type': list[j],
                    'index': i,
                    'x': xx,
                    'y': tline[offset] + 1,
                    'mirror': ismirror
                })
                ix += 9
                j += 1
            
            self.wind_positions[wind_key] = tree_data
        
        # Draw trees using stored positions for consistent placement
        for tree in self.wind_positions[wind_key]:
            self.Draw(
                tree['type'], 
                tree['index'], 
                tree['x'], 
                tree['y'], 
                tree['mirror']
            )

    SMOKE_R_PX = 30
    PERSENT_DELTA = 4
    SMOKE_SIZE = 60

    def DrawSmoke_makeline(self, angle_deg):
        a = (math.pi * angle_deg) / 180
        r = self.SMOKE_R_PX
        k = r * math.sin(a) / (math.sqrt((r * math.cos(a)))) 
        yp = 0
        dots = []
        for x in range(0, self.w):
            y = int(k * math.sqrt(x))
            if (y > self.h):
                y = self.h
            yi = yp
            while(True):
                rr = math.sqrt(x*x + yi*yi)
                dots.append([x, yi, rr])
                if (rr > self.SMOKE_SIZE):
                    return dots
                yi += 1
                if (yi >= y):
                    yp = y
                    break

    def DrawSmoke(self, x0, y0, persent, animate=False):
        """Draw smoke with optional animation"""
        gray_color = self.color_palette[self.GRAY]
        
        # If animating, adjust the angle slightly based on the frame
        if animate:
            # Add a slight wave effect to the smoke angle
            angle_adjustment = math.sin(self.current_frame / self.total_frames * 2 * math.pi) * 5
            dots = self.DrawSmoke_makeline(persent + angle_adjustment)
            
            # Use consistent randomization across frames
            random.seed(x0 * 1000 + y0)
            offset_x = int(math.sin(self.current_frame / self.total_frames * 2 * math.pi) * 3)
        else:
            dots = self.DrawSmoke_makeline(persent)
            offset_x = 0
            
        # Store the random state to restore it later
        if animate:
            random_state = random.getstate()
        
        for d in dots:
            x = d[0]
            y = d[1]
            r = d[2]
            
            # Use frame number to determine which parts of smoke to render in this frame
            if animate:
                # Different parts of smoke appear in different frames
                smoke_phase = (x + y + self.current_frame) % self.total_frames
                if smoke_phase > self.total_frames / 2:
                    continue
                    
            # Use consistent random seed for each dot's position
            if animate:
                # Consistent random seed for each position
                random.seed(x * 1000 + y * 1000 + int(persent * 100))
                
            if random.random()*1.3 > (r/self.SMOKE_SIZE):
                if random.random()*1.2 < (r/self.SMOKE_SIZE):
                    dx = random.randint(-1, 1)
                    dy = random.randint(-1, 1)
                else:
                    dx = 0
                    dy = 0
                
                # Apply the animated horizontal offset if animating
                if animate:
                    dx += offset_x
                
                self.Dot(x0+x+dx, self.h-(y0+y)+dy, gray_color)
                
        # Restore the random state
        if animate:
            random.setstate(random_state)

if __name__ == "__main__":  
    img = Image.open('../test.bmp')
    s = Sprites('../sprite',img)
    s.Draw("house",0,100,100)
    img.save("../tmp/sprites_test.bmp")

