# Class to monitor a rotary encoder and update a value.  You can either read the value when you need it, by calling getValue(), or
# you can configure a callback which will be called whenever the value changes.

import mido                     # MIDI Library
import RPi.GPIO as GPIO         # To access LCD & Rotary Encoder Pins
from time import sleep, time    # For delay, button timing & debouncing
from FP90_Instruments import instruments

value = 1
global menu

class Encoder:
    global value
    global menu
    # Define PINS & BUTTON Constants
    RED_LED_PIN   = 22 # ( 15 Physical Pin / 22 BCM Pin)
    GREEN_LED_PIN = 27 # ( 13 Physical Pin / 27 BCM Pin)
    BLUE_LED_PIN  = 17 # ( 11 Physical Pin / 17 BCM Pin)

    SWITCH_PIN   = 10 # ( 19 Physical Pin / 10 BCM Pin)

    BUTTON_SHORT_PRESS = 1000   # Values for Push Button Callback
    BUTTON_LONG_PRESS = 2000

    def __init__(self, leftPin, rightPin, buttonPin, callback=None):
        self.leftPin = leftPin
        self.rightPin = rightPin
        self.buttonPin = buttonPin
        self.value = 0
        self.state = '00'
        self.direction = None
        self.callback = callback
        # self.push_event = BUTTON_RELEASED
        self.stop = 0 # for Button press timer
        # SLP: Added to make sure using the right GPIO PIN (BCM/Broadcom)
        GPIO.setmode(GPIO.BCM)

        # Initializing Rotary Encoder Directions Pins A, B & PUSH BUTTON
        # SLP: Replaced PUD_DOWN with PUD_UP for A & B since my ROTARY ENCODER expects UP
        GPIO.setup(self.leftPin,   GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Rotary A
        GPIO.setup(self.rightPin,  GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Rotary B
        GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Push Button

       # SLP: Initialize RGB LEDs - turn BLUE (R & G are left OFF)
        GPIO.setup(self.RED_LED_PIN,   GPIO.OUT, initial=GPIO.HIGH)   # Set LED pins to be Output pins and initial value: high (off)
        GPIO.setup(self.GREEN_LED_PIN, GPIO.OUT, initial=GPIO.HIGH)   # Set LED pins to be Output pins and initial value: high (off)
        GPIO.setup(self.BLUE_LED_PIN,  GPIO.OUT, initial=GPIO.LOW)    # Set LED pins to be Output pins and initial value: LOW (ON)

        # Initializing Interrupts for Rotary Directions Pins A, B & PUSH BUTTON
        # GPIO.add_event_detect(self.leftPin,   GPIO.BOTH, callback=self.transitionOccurred) #, bouncetime=300)  
        # GPIO.add_event_detect(self.rightPin,  GPIO.BOTH, callback=self.transitionOccurred) #, bouncetime=300) 

        #GPIO.add_event_detect(self.buttonPin, GPIO.RISING, callback=self.button_event, bouncetime=300)
        #GPIO.add_event_detect(self.buttonPin, GPIO.RISING, callback=buttonEvent, bouncetime=300)

         # SLP: Added LED Actions
    def led_red(self, active = False):
        if active == False:
            GPIO.output(self.RED_LED_PIN, GPIO.HIGH) # Turn RED LED OFF
        else:
            GPIO.output(self.RED_LED_PIN, GPIO.LOW) # Turn RED LED ON
            self.active = True

    def led_green(self, active = False):
        if active == False:
            GPIO.output(self.GREEN_LED_PIN, GPIO.HIGH) # Turn GREEN LED OFF
        else:
            GPIO.output(self.GREEN_LED_PIN, GPIO.LOW) # Turn GREEN LED ON
            self.active = True

    def led_blue(self, active = False):
        if active == False:
            GPIO.output(self.BLUE_LED_PIN, GPIO.HIGH) # Turn BLUE LED OFF
        else:
            GPIO.output(self.BLUE_LED_PIN, GPIO.LOW) # Turn BLUE LED ON
            self.active = True

    # Button Events - PUSHED & RELEASED + DEBOUNCE using TIMER

    def button_event(self,buttonPin):
        global menu
        # CALLBACK for BUTTON : SHORT PRESS = Select Instrument, LONG = Back to 1st MENU Item

        # print("BUTTON _value_", menu)
        
        """ 
            NEED TO FIND A WAY TO CALL MENU CLASS FROM HERE
            in order to FORCE REFRESH OF 1st MENU ITEM
            when BUTTON is LONG PRESSED...
            But...MENU/LCD Methods are in another CLASS
        """

        #  global value
        self.start = time() #start timer to test SHORT / LONG PUSH
        self.stop  = self.start
        # BUTTON is PRESSED - TURNED RED
        self.led_blue(False)    # Turn off BLUE Light
        self.led_red(True)      # BUTTON is RED when SHORT PUSH
        # sleep(0.20)
        while ((GPIO.input(buttonPin) == 1) and (self.stop - self.start < 1)): #always loop if button pressed
        # sleep(0.04)
            self.stop = time()  # Stop Timer when BUTTON is Released
        # When BUTTON is RELEASED, Turn OFF RED Light
        self.led_red(False) 

        # If BUTTON was SHORT PRESSED, set Light back to BLUE
        if (self.stop - self.start) < 1:    # SHORT PRESS if Pressed < 1 second
            self.led_blue(True)
            print("SHORT PRESS: %.2f ms" % (self.stop - self.start))
            print("\tMENU SELECTED: ", instruments[self.value][0].ljust(17)) #    instr.get_item(self.value))
            self.push_event = self.BUTTON_SHORT_PRESS # Attribute in callback returning Push Button Event type 

        # If BUTTON was LONG PRESSED, set Light to YELLOW (Green + Red))
        else:
            self.push_event = self.BUTTON_LONG_PRESS # Attribute in callback returning Push Button Event type 
            # value = 1   
            # Go to MENU Page 1 (item 1)
            self.value = 1
            self.page  = 0 # Force display of 1st Page of Menu Items

            self.led_red(True)
            self.led_green(True)
            print("LONG PRESS: %.2f ms" % (self.stop - self.start))
            print("\tBACK to MENU Page 1 (item %d)" % value)
            sleep(2)
            self.led_red(False)
            self.led_green(False)
        return self.push_event

    def button_event_old(self,buttonPin):
        # buttonState = GPIO.input(buttonPin) 
        #if buttonState == 1:
            # event = BTN_RELEASED # self.BUTTONUP
        # else:
        #    print("BUTTON is RELEASED:", buttonState)
       
        self.start = time() #start timer
        # print("last:", self.stop, "now:", start, "delta:", start - self.stop)

        # If BOUNCE CALL, then RETURN
        if (self.start - self.stop) < 0.24:
            print("SKIPPING Bounce call - delta: ", self.start - self.stop )
            self.push_event = self.BUTTON_RELEASED # Attribute in callback returning Push Button Event type 
            # return
        else:
            # BUTTON starts as SHORT PUSH - TURNED GREEN
            self.led_blue(False) # Turn off BLUE Light
            self.led_red(True) # BUTTON is RED when SHORT PUSH
            sleep(0.20)
            while((GPIO.input(buttonPin) == 1) and (time() - self.start < 1)): #always loop if button pressed
                sleep(0.04)
                self.stop = time() #stop timer
            # AFTER SHORT PRESS, TURN BUTTON back to BLUE
            self.led_red(False) 
            if (time() - self.start) < 1:
                self.led_blue(True)
                print("SHORT PRESS: %.2f ms" % (time() - self.start))
                print("MENU SELECTED: ", instruments[self.value][0].ljust(17)) #    instr.get_item(self.value))
                self.push_event = self.BUTTON_SHORT_PUSH # Attribute in callback returning Push Button Event type 
            # AFTER LONG PRESS, TURN BUTTON to YELLOW (GREEN + RED)
            else:
                print("BACK to MENU Page 1 / Item 1")
                self.push_event = self.BUTTON_LONG_PUSH # Attribute in callback returning Push Button Event type 
                self.led_red(True)
                self.led_green(True)
                print("LONG PRESS: %.2f ms" % (time() - self.start))
                sleep(2)
                self.led_red(False)
                self.led_green(False)
                # If Button is LONG PRESS, Return EVENT to CALLBACK 
                # if self.callback is not None:
                #    self.callback(self.value)

    def transitionOccurred(self, channel):
        # global value
        p1 = GPIO.input(self.rightPin)
        p2 = GPIO.input(self.leftPin)
        newState = "{}{}".format(p1, p2)

        if self.state == "00": # Resting position
            if newState == "01": # Turned right 1
                self.direction = "R"
            elif newState == "10": # Turned left 1
                self.direction = "L"

        elif self.state == "01": # R1 or L3 position
            if newState == "11": # Turned right 1
                self.direction = "R"
            elif newState == "00": # Turned left 1
                if self.direction == "L":
                    if self.value > 1:
                        self.value = self.value - 1
                    # if self.callback is not None:
                        self.callback(self.value)

        elif self.state == "10": # R3 or L1
            if newState == "11": # Turned left 1
                self.direction = "L"
            elif newState == "00": # Turned right 1
                if self.direction == "R":
                    self.value = self.value + 1
                    #if self.callback is not None:
                    self.callback(self.value)

        else: # self.state == "11"
            if newState == "01": # Turned left 1
                self.direction = "L"
            elif newState == "10": # Turned right 1
                self.direction = "R"
            elif newState == "00": # Skipped an intermediate 01 or 10 state, but if we know direction then a turn is complete
                if self.direction == "L":
                    if self.value > 1:
                        self.value = self.value - 1
                    # if self.callback is not None:
                        self.callback(self.value)
                elif self.direction == "R":
                    self.value = self.value + 1
                    # if self.callback is not None:
                    self.callback(self.value)
                
        self.state = newState

#    def getValue(self):
#        return self.value

