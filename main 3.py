import board
import displayio
import terminalio
import busio
import digitalio
import adafruit_displayio_sh1107
import adafruit_imageload
import time
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20
import neopixel

from adafruit_led_animation.animation.blink import Blink

from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.triangle import Triangle

from adafruit_display_text import label


displayio.release_displays()

i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 64
BORDER = 2

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF

splash = displayio.Group()

display.show(splash)

fillscreen = displayio.Group()
Statsscreen = displayio.Group()
CIPscreen = displayio.Group()
dropleticon = displayio.Group()
bubbleicon = displayio.Group()

from adafruit_motorkit import MotorKit
from adafruit_debouncer import Debouncer


from adafruit_seesaw import seesaw

import adafruit_seesaw.digitalio
import adafruit_seesaw.neopixel
import adafruit_seesaw.rotaryio

import adafruit_pixelbuf

ow_bus = OneWireBus(board.D9)
ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

proxsensor = digitalio.DigitalInOut(board.D6)
proxsensor.direction = digitalio.Direction.INPUT

can_count = 0

kit = MotorKit()

current_program = "Monarch"
program_running = False
previous_program = "CIP"

seesawA = seesaw.Seesaw(board.I2C(), 0x3D)
encoderA = adafruit_seesaw.rotaryio.IncrementalEncoder(seesawA)
seesawA.pin_mode(24, seesawA.INPUT_PULLUP)
switchA = adafruit_seesaw.digitalio.DigitalIO(seesawA, 24)
pixelA = adafruit_seesaw.neopixel.NeoPixel(seesawA, 6, 1)
pixelA.brightness = 0.5
last_positionA = -1
pixelA.fill((255, 255, 255))
pixelA.brightness = .01

seesawB = seesaw.Seesaw(board.I2C(), 0x36)
encoderB = adafruit_seesaw.rotaryio.IncrementalEncoder(seesawB)
seesawB.pin_mode(24, seesawB.INPUT_PULLUP)
switchB = adafruit_seesaw.digitalio.DigitalIO(seesawB, 24)
pixelB = adafruit_seesaw.neopixel.NeoPixel(seesawB, 6, 1)
pixelB.brightness = 0.5
last_positionB = -1
pixelB.fill((255, 255, 255))
pixelB.brightness = .01

text_area = label.Label(terminalio.FONT, text="monarch", scale=3, color=0xFFFFFF, x=3, y=12)
splash.append(text_area)
text_area2 = label.Label(terminalio.FONT, text="FLUID SYSTEMS", scale=1, color=0xFFFFFF, x=28, y=36)
splash.append(text_area2)
text_area3 = label.Label(terminalio.FONT, text="nano MK.I", scale=1, color=0xFFFFFF, x=70, y=55)
splash.append(text_area3)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF

sm_bitmap = displayio.Bitmap(20, 12, 1)
sm_square = displayio.TileGrid(sm_bitmap, pixel_shader=color_palette, x=83, y=0)
fillscreen.append(sm_square)

sm_bitmapCIP = displayio.Bitmap(20, 12, 1)
sm_squareCIP = displayio.TileGrid(sm_bitmapCIP, pixel_shader=color_palette, x=83, y=0)
CIPscreen.append(sm_squareCIP)

triangle = Triangle(40, 18, 37, 25, 43, 25, fill=0x000000, outline=0xFFFFFF)
dropleticon.append(triangle)
circle = Circle(40, 25, 3, fill=0x000000, outline=0xFFFFFF)
dropleticon.append(circle)
rectDroplet = Rect(39, 22, 3, 1, fill=0x000000)
dropleticon.append(rectDroplet)

dropleticon.x = 27
dropleticon.y = -17

fillscreen.append(dropleticon)

circle2 = Circle(68, 43, 3, fill=0x000000, outline=0xFFFFFF)
bubbleicon.append(circle2)
circle3 = Circle(64, 46, 4, fill=0x000000, outline=0xFFFFFF)
bubbleicon.append(circle3)
circle4 = Circle(70, 49, 3, fill=0x000000, outline=0xFFFFFF)
bubbleicon.append(circle4)

bubbleicon.x = 3
bubbleicon.y = -40

CIPscreen.append(bubbleicon)

rectTime = Rect(0, 29, 54, 34, outline=0xFFFFFF)
fillscreen.append(rectTime)
rectFoam = Rect(56, 29, 32, 34, outline=0xFFFFFF)
fillscreen.append(rectFoam)
rectTemp = Rect(90, 29, 38, 34, outline=0xFFFFFF)
fillscreen.append(rectTemp)

roundrectTime = RoundRect(0, 22, 54, 15, 2, fill=0xFFFFFF, stroke=1)
fillscreen.append(roundrectTime)
roundrectFoam = RoundRect(56, 22, 32, 15, 2, fill=0xFFFFFF, stroke=1)
fillscreen.append(roundrectFoam)
roundrectTemp = RoundRect(90, 22, 38, 15, 2, fill=0xFFFFFF, stroke=1)
fillscreen.append(roundrectTemp)

text_area4 = label.Label(terminalio.FONT, text="Fill Mode:", scale=1, color=0xFFFFFF, x=0, y=5)
fillscreen.append(text_area4)
text_area5 = label.Label(terminalio.FONT, text="OFF", scale=1, color=0x000000, x=85, y=5)
fillscreen.append(text_area5)
text_area6 = label.Label(terminalio.FONT, text="ON", scale=1, color=0xFFFFFF, x=110, y=5)
fillscreen.append(text_area6)
text_area7 = label.Label(terminalio.FONT, text="Time (s)", scale=1, color=0x000000, x=4, y=28)
fillscreen.append(text_area7)
text_area8 = label.Label(terminalio.FONT, text="0.0", scale=2, color=0xFFFFFF, x=4, y=47)
fillscreen.append(text_area8)
text_area9 = label.Label(terminalio.FONT, text="Foam", scale=1, color=0x000000, x=61, y=28)
fillscreen.append(text_area9)
text_area10 = label.Label(terminalio.FONT, text="0", scale=2, color=0xFFFFFF, x=67, y=47)
fillscreen.append(text_area10)
text_area9b = label.Label(terminalio.FONT, text="F", scale=1, color=0x000000, x=110, y=28)
fillscreen.append(text_area9b)
text_area9c = label.Label(terminalio.FONT, text="00", scale=1, color=0xFFFFFF, x=94, y=47)
fillscreen.append(text_area9c)
circleTemp = Circle(105, 27, 2, fill=0xFFFFFF, outline=0x000000, stroke=2)
fillscreen.append(circleTemp)


text_area11 = label.Label(terminalio.FONT, text=" CIP Mode:", scale=1, color=0xFFFFFF, x=0, y=5)
CIPscreen.append(text_area11)
text_area12 = label.Label(terminalio.FONT, text="OFF", scale=1, color=0x000000, x=85, y=5)
CIPscreen.append(text_area12)
text_area13 = label.Label(terminalio.FONT, text="ON", scale=1, color=0xFFFFFF, x=110, y=5)
CIPscreen.append(text_area13)

triangle2 = Triangle(26, 22, 6, 62, 46, 62, fill=0xFFFFFF, outline=0x000000)
CIPscreen.append(triangle2)
triangle3 = Triangle(26, 50, 24, 34, 28, 34, fill=0x000000)
CIPscreen.append(triangle3)
circle5 = Circle(26, 57, 2, fill=0x000000)
CIPscreen.append(circle5)
circle6 = Circle(26, 33, 2, fill=0x000000)
CIPscreen.append(circle6)

text_area15 = label.Label(terminalio.FONT, text="WARNING:", scale=1, color=0xFFFFFF, x=64, y=25)
CIPscreen.append(text_area15)
text_area16 = label.Label(terminalio.FONT, text="Valve will", scale=1, color=0xFFFFFF, x=58, y=41)
CIPscreen.append(text_area16)
text_area17 = label.Label(terminalio.FONT, text="stay open!", scale=1, color=0xFFFFFF, x=59, y=53)
CIPscreen.append(text_area17)

rectCans = Rect(22, 29, 54, 34, outline=0xFFFFFF)
Statsscreen.append(rectCans)
rectCases = Rect(81, 29, 42, 34, outline=0xFFFFFF)
Statsscreen.append(rectCases)

roundrectCans = RoundRect(22, 22, 54, 15, 2, fill=0xFFFFFF, stroke=1)
Statsscreen.append(roundrectCans)
roundrectCases = RoundRect(81, 22, 42, 15, 2, fill=0xFFFFFF, stroke=1)
Statsscreen.append(roundrectCases)

text_area18 = label.Label(terminalio.FONT, text="Canning Run Stats:", scale=1, color=0xFFFFFF, x=0, y=5)
Statsscreen.append(text_area18)
text_area21 = label.Label(terminalio.FONT, text="Cans", scale=1, color=0x000000, x=38, y=28)
Statsscreen.append(text_area21)
text_area22 = label.Label(terminalio.FONT, text="0", scale=2, color=0xFFFFFF, x=26, y=47)
Statsscreen.append(text_area22)
text_area23 = label.Label(terminalio.FONT, text="Cases", scale=1, color=0x000000, x=87, y=28)
Statsscreen.append(text_area23)
text_area24 = label.Label(terminalio.FONT, text="0", scale=2, color=0xFFFFFF, x=85, y=47)
Statsscreen.append(text_area24)

roundrectTab = RoundRect(0, 28, 15, 27, 7, fill=0xFFFFFF, stroke=1)
Statsscreen.append(roundrectTab)
circleTab = Circle(7, 35, 5, fill=0x000000)
Statsscreen.append(circleTab)
rectTab = Rect(2, 37, 11, 7, fill=0xFFFFFF)
Statsscreen.append(rectTab)
roundrectTab2 = RoundRect(2, 34, 11, 5, 2, fill=0x000000)
Statsscreen.append(roundrectTab2)
circleTab2 = Circle(7, 46, 5, fill=0x000000)
Statsscreen.append(circleTab2)
circleTab3 = Circle(7, 46, 2, fill=0xFFFFFF)
Statsscreen.append(circleTab3)
rectTab2 = Rect(6, 48, 3, 5, fill=0xFFFFFF)
Statsscreen.append(rectTab2)
rectTab3 = Rect(5, 50, 5, 5, fill=0xFFFFFF)
Statsscreen.append(rectTab3)
rectTab4 = Rect(3, 54, 9, 2, fill=0x000000)
Statsscreen.append(rectTab4)

TEMPERATURE_DELAY = 1
ds18_next = time.monotonic()
ds18_do_read = False
ds18_async_delay = 1

switchB_held = False
switchA_held = False
z = 0

BLUE = (0,0,255)
RED = (255,0,0)

MIN = 33
MID = 37
MAX = 124
CLEAN = 125

zf = 0

# blinking animation
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.pulse import Pulse

blinkermid = Blink(pixelA, speed=0.5, color=BLUE)

#pulsermid = Pulse(pixelA, speed=0.5, color=BLUE) #period=3)

blinkermax = Blink(pixelA, speed=0.2, color=RED)

while True:

    case_count = (can_count//24)
    now = time.monotonic()

    if not switchA.value and not switchA_held:
        switchA_held = True

    if not switchB.value and not switchB_held:
        switchB_held = True



    if now > ds18_next:
        if ds18_do_read:
            temperature = ds18.read_temperature()
            z = int(temperature) #00.0 readout
            zf = int(temperature * (9/5) +32) #00.0 readout
            ds18_next = ds18_next - ds18_async_delay + TEMPERATURE_DELAY
            ds18_do_read = False
            text_area9c.text = str(z * (9/5) + 32)
            #text_area9c.text = str(z) #00. readout

        if not ds18_do_read and now > ds18_next:
            max_read_delay = ds18.start_temperature_read()
            ds18_async_delay = max_read_delay * 1.01
            ds18_next = now + ds18_async_delay
            ds18_do_read = True

    if zf <= MIN:
        pixelA.fill(BLUE)
        pixelA.brightness = .5
        pixelA.show()
    if zf > MIN and zf <= MID:
        pixelA.brightness = .5
        speed = 0.7
        blinkermid.speed = speed
        blinkermid.animate()
        #pulsermid.speed = speed
        #pulsermid.period = period
        #pulsermid.animate()

    if zf > MID and zf <= MAX:
        pixelA.brightness = .5
        speed = 0.15
        blinkermax.speed = speed
        blinkermax.animate()
    if zf >= CLEAN:
        pixelA.fill(RED)
        pixelA.brightness = 1.0
        pixelA.show()

    if current_program != "Fill" and switchA_held and previous_program == "CIP":
        display.show(fillscreen)
        current_program = "Fill"
        previous_program = "Fill"
        switchA_held = False

    if current_program == "Fill" and not program_running:
        positionA = -encoderA.position
        lastA_position = positionA
        timingA_value = 0.1*-encoderA.position
        if timingA_value < 0.0:
            timingA_value = 0.0
        text_area8.text = str(timingA_value)
        positionB = -encoderB.position
        lastB_position = positionB
        timingB_value = -encoderB.position
        if timingB_value > 9:
            timingB_value = 9
        if timingB_value < 0:
            timingB_value = 0
        text_area10.text = str(timingB_value)
        pixelB.fill((255, 255, 255))
        pixelB.brightness = .01

    if current_program == "Fill" and switchB_held and not program_running:
        program_running = True
        switchB_held = False

    if current_program == "Fill" and program_running:
        positionA = -encoderA.position
        lastA_position = positionA
        timingA_value = 0.1*-encoderA.position
        if timingA_value < 0.0:
            timingA_value = 0.0
        sm_square.x = 106
        text_area5.color = 0xFFFFFF
        text_area6.color = 0x000000
        text_area8.text = str(timingA_value)
        triangle.fill = 0xFFFFFF
        triangle.outline = 0xFFFFFF
        circle.fill = 0xFFFFFF
        circle.outline = 0xFFFFFF
        rectDroplet.fill = 0xFFFFFF
        positionB = -encoderB.position
        lastB_position = positionB
        timingB_value = -encoderB.position
        if timingB_value > 9:
            timingB_value = 9
        if timingB_value < 0:
            timingB_value = 0
        text_area10.text = str(timingB_value)
        pixelB.fill((255, 255, 255))
        pixelB.brightness = .1

    if current_program == "Fill" and switchB_held or switchA_held == "true" and program_running:
        sm_square.x = 83
        text_area5.color = 0x000000
        text_area6.color = 0xFFFFFF
        program_running = False
        triangle.outline = 0xFFFFFF
        triangle.fill = 0x000000
        circle.outline = 0xFFFFFF
        circle.fill = 0x000000
        rectDroplet.fill = 0x000000
        #program_running = False
        pixelB.fill((255, 255, 255))
        pixelB.brightness = .01
        switchB_held = False
        #how do i set this one up here since its an either or situation on the button?

    if current_program == "Fill" and program_running and proxsensor.value == True:
        time.sleep(1)
        kit.motor4.throttle = 1.0       # Load can 90deg
        time.sleep(1)
        kit.motor4.throttle = 0
        time.sleep(1)                   # need for can to fall into chute
        kit.motor1.throttle = 1.0       # Push can down chute
        time.sleep(1)
        kit.motor1.throttle = 0         # Push can down chute
        kit.motor2.throttle = 1.0       # Drop lift piston !!! Lower lift arm and preload with sidecan
        time.sleep(.60)
        kit.motor3.throttle = 1.0       # Start Fill and open can purging but raised means scraper purging
        time.sleep(timingA_value)       # Hold for set time
        kit.motor3.throttle = 0         # End fill
        for _ in range(timingB_value):
            time.sleep(0.05)                # Hold for set time
            kit.motor3.throttle = 1.0       # Start Foam Pulse
            time.sleep(0.05)                # Hold for set time
            kit.motor3.throttle = 0         # End Foam Pulse
        kit.motor2.throttle = 0             # Raise lift !!! Raise Can into chute
        time.sleep(.75)
        can_count += 1

    if current_program != "Stats" and switchA_held and previous_program == "Fill":
        display.show(Statsscreen)
        text_area22.text = str(can_count)
        text_area24.text = str(case_count)
        current_program = "Stats"
        previous_program = "Stats"
        program_running = False
        switchA_held = False

    if current_program != "CIP" and switchA_held and previous_program == "Stats":
        display.show(CIPscreen)
        time.sleep(.20)
        triangle2.fill = 0xFFFFFF
        triangle2.outline = 0x000000
        triangle3.fill = 0x000000
        circle5.fill = 0x000000
        circle6.fill = 0x000000
        pixelB.fill((255, 255, 0))
        pixelB.brightness = .5
        time.sleep(.20)
        triangle2.fill = 0x000000
        triangle2.outline = 0xFFFFFF
        triangle3.fill = 0xFFFFFF
        circle5.fill = 0xFFFFFF
        circle6.fill = 0xFFFFFF
        pixelB.fill((255, 255, 0))
        pixelB.brightness = .1
        time.sleep(.20)
        triangle2.fill = 0xFFFFFF
        triangle2.outline = 0x000000
        triangle3.fill = 0x000000
        circle5.fill = 0x000000
        circle6.fill = 0x000000
        pixelB.fill((255, 255, 0))
        pixelB.brightness = .5
        time.sleep(.20)
        triangle2.fill = 0x000000
        triangle2.outline = 0xFFFFFF
        triangle3.fill = 0xFFFFFF
        circle5.fill = 0xFFFFFF
        circle6.fill = 0xFFFFFF
        pixelB.fill((255, 255, 0))
        pixelB.brightness = .1
        kit.motor4.throttle = 0.0
        kit.motor3.throttle = 0.0
        current_program = "CIP"
        program_running = False
        previous_program = "CIP"
        switchA_held = False

    if current_program == "CIP" and switchB_held and not program_running:
        sm_squareCIP.x = 106
        text_area12.color = 0xFFFFFF
        text_area13.color = 0x000000
        circle2.fill = 0xFFFFFF
        circle2.outline = 0xFFFFFF
        circle3.fill = 0xFFFFFF
        circle3.outline = 0xFFFFFF
        circle4.fill = 0xFFFFFF
        circle4.outline = 0xFFFFFF
        pixelB.fill((255, 255, 0))
        pixelB.brightness = .5
        kit.motor4.throttle = 1.0
        time.sleep(.5)
        kit.motor3.throttle = 1.0
        current_program = "CIP"
        program_running = True
        switchB_held = False

    if current_program == "CIP" and switchB_held and program_running:
        sm_squareCIP.x = 83
        text_area12.color = 0x000000
        text_area13.color = 0xFFFFFF
        circle2.fill = 0x000000
        circle2.outline = 0xFFFFFF
        circle3.fill = 0x000000
        circle3.outline = 0xFFFFFF
        circle4.fill = 0x000000
        circle4.outline = 0xFFFFFF
        pixelB.fill((255, 255, 0))
        pixelB.brightness = .1
        kit.motor4.throttle = 0.0
        kit.motor3.throttle = 0.0
        current_program = "CIP"
        program_running = False
        switchB_held = False
