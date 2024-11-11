import RPi.GPIO as GPIO
import time

# Define GPIO pins for MSB and LSB
MSB_PIN = 27  # Most significant bit
LSB_PIN = 17  # Least significant bit

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MSB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LSB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Helper function to read Gray code state
def read_encoder():
    msb = GPIO.input(MSB_PIN)
    lsb = GPIO.input(LSB_PIN)
    return (msb << 1) | lsb  # Combine MSB and LSB into a 2-bit binary number

# Initialize variables
prev_state = read_encoder()

try:
    print("Rotary encoder test - turn clockwise or counter-clockwise")

    while True:
        current_state = read_encoder()

        # Only act if there's a state change
        if current_state != prev_state:
            # Gray code transitions for 12-step encoder
            if (prev_state == 0b00 and current_state == 0b01) or \
               (prev_state == 0b01 and current_state == 0b11) or \
               (prev_state == 0b11 and current_state == 0b10) or \
               (prev_state == 0b10 and current_state == 0b00):
                print("Clockwise")
            elif (prev_state == 0b00 and current_state == 0b10) or \
                 (prev_state == 0b10 and current_state == 0b11) or \
                 (prev_state == 0b11 and current_state == 0b01) or \
                 (prev_state == 0b01 and current_state == 0b00):
                print("Counter-clockwise")

            # Update previous state
            prev_state = current_state

        # Small delay to avoid excessive CPU usage
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting program")

finally:
    GPIO.cleanup()

