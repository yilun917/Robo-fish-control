# Setup
# Channel 1 is the Throttle controls tail movement, RC signal goes to BCM 17 and servo connects at BCM 12
# Channel 2 is the AILE controls body movement, RC signal goes to BCM 27 and servo connects at BCM 18
# Channel 3 is the ELEV controls tail movement speed, RC signal goes to BCM 22
# needed library to communicate with controller GPIO
import RPi.GPIO as GPIO
import time


RC_Channel1 = 8  # channel 1 connected to BCM 8 (control tail)
RC_Channel2 = 7  # channel 2 connected to BCM 7 (control body)
RC_Channel3 = 1  # channel 3 connected to BCM 1 (control tail speed)

Servo_Body_Channel = 17  # BCM 17 pin
Servo_Tail_Channel = 18  # BCM 18 pin
PWM_FREQ = 200  # PWM frequency

RC_1 = 0  # RC channel 1 index control tail
RC_2 = 1  # RC channel 2 index control body
RC_3 = 2  # RC channel 3 index control tail movement speed

START_DUTY = 0  # PWM start duty cycle


RC1_ACTIVATION = 1650  # RC channel 2 activation threshold  SUBJECT TO CHANGE
RC1_LOW = 800  # RC1 signal low value, SUBJECT TO CHANGE
RC1_HIGH = 2100
RC2_LOW = 800    # RC2 signal low value - ch1 contol body, signal high time in microseconds  SUBJECT TO CHANGE
RC2_HIGH = 1750
RC3_LOW = 650    # RC3 signal low value - ch1 contol tail   SUBJECT TO CHANGE
RC3_HIGH = 1800
TIME_LOW = 0.008    # time interval when sweeping  SUBJECT TO CHANGE
TIME_HIGH = 0.02
RIGHT_DUTY = 40  # Duty cycle at far right    SUBJECT TO CHANGE
LEFT_DUTY = 20   # Duty cycle at far left
POSSIBLE_SIGNAL_HIGH = 2800
POSSIBLE_SIGNAL_LOW = 300
SYSTEM_BREAK_TIME = 0.1  # if no signal input, break for x seconds
t = 0.02

RC_Signal = [0, 0, 0]  # set a list to store signal
start_time = [0, 0, 0]  # record signal start and end time
end_time = [0, 0, 0]

# to get rid of out of range signal, save the previous signal
RC_Pre = [0, 0, 0]
body_angle_duty = 0


GPIO.setmode(GPIO.BCM) # set mode to accept GPIO number
GPIO.setup(RC_Channel1, GPIO.IN)  # enable the pin to read in data for channel 1 ,2 and 3
GPIO.setup(RC_Channel2, GPIO.IN)
GPIO.setup(RC_Channel3, GPIO.IN)


def execute_body_servo():
    global body_angle_duty
    # execute body servo
    body_angle_duty = LEFT_DUTY + (RC2_HIGH - RC_Signal[RC_2])/(RC2_HIGH - RC2_LOW) * (RIGHT_DUTY - LEFT_DUTY)
    # Limit the angle duty cycle in range to prevent execute error signal
    if body_angle_duty < LEFT_DUTY:
        body_angle_duty = LEFT_DUTY
    elif body_angle_duty > RIGHT_DUTY:
        body_angle_duty = RIGHT_DUTY
    Servo_Body.ChangeDutyCycle(body_angle_duty)


def calc_channel1(RC1):
    if GPIO.input(RC1) == True:
        start_time[RC_1] = time.time()  # gives time in seconds
    else:
        end_time[RC_1] = time.time()
    RC_Signal[RC_1] = (end_time[RC_1] - start_time[RC_1]) * (10**6)  # signal lasting time
    # Error checking
    if not POSSIBLE_SIGNAL_LOW < RC_Signal[RC_1] < POSSIBLE_SIGNAL_HIGH:  # assign signal to previous if error signal were produced
        RC_Signal[RC_1] = RC_Pre[RC_1]
    RC_Pre[RC_1] = RC_Signal[RC_1]


def calc_channel2(RC2):
    if GPIO.input(RC2) == True:
        start_time[RC_2] = time.time()  # gives time in seconds
    else:
        end_time[RC_2] = time.time()
    RC_Signal[RC_2] = (end_time[RC_2] - start_time[RC_2]) * (10**6)  # signal lasting time
    # Error checking
    if not POSSIBLE_SIGNAL_LOW < RC_Signal[RC_2] < POSSIBLE_SIGNAL_HIGH:  # assign signal to previous if error signal were produced
        RC_Signal[RC_2] = RC_Pre[RC_2]
    RC_Pre[RC_2] = RC_Signal[RC_2]


def calc_channel3(RC3):
    if GPIO.input(RC3) == True:
        start_time[RC_3] = time.time()  # gives time in seconds
    else:
        end_time[RC_3] = time.time()
    RC_Signal[RC_3] = (end_time[RC_3] - start_time[RC_3]) * (10**6)  # signal lasting time
    # Error checking
    if not POSSIBLE_SIGNAL_LOW < RC_Signal[RC_3] < POSSIBLE_SIGNAL_HIGH:  # assign signal to previous if error signal were produced
        RC_Signal[RC_3] = RC_Pre[RC_3]
    RC_Pre[RC_3] = RC_Signal[RC_3]

    # calculate tail movement speed according to RC channel 3
    global t
    t = TIME_LOW + (RC3_HIGH - RC_Signal[RC_3])/(RC3_HIGH - RC3_LOW) * (TIME_HIGH - TIME_LOW)
    if t < TIME_LOW:
        t = TIME_LOW
    elif t > TIME_HIGH:
        t = TIME_HIGH


# PWM on Servo Motor
GPIO.setup(Servo_Body_Channel, GPIO.OUT)  # initialize servo channel as an output.
GPIO.setup(Servo_Tail_Channel, GPIO.OUT)

Servo_Body = GPIO.PWM(Servo_Body_Channel, PWM_FREQ)  # Body as PWM output, with PWM_FREQ frequency
Servo_Tail = GPIO.PWM(Servo_Tail_Channel, PWM_FREQ)   # tail channel as PWM output, with PWM_FREQ frequency
Servo_Body.start(START_DUTY)  # generate PWM signal with start duty cycle
Servo_Tail.start(START_DUTY)  # generate PWM signal with start duty cycle

# add interrupt, when hardware detects signal change, recalculate the signal
GPIO.add_event_detect(RC_Channel1, GPIO.BOTH, callback=calc_channel1)
GPIO.add_event_detect(RC_Channel2, GPIO.BOTH, callback=calc_channel2)
GPIO.add_event_detect(RC_Channel3, GPIO.BOTH, callback=calc_channel3)



# Main running loop
while True:  # execute loop forever
    print("RC_1", RC_Signal[RC_1])  # print the signal for error checking
    print("RC_2", RC_Signal[RC_2])
    print("RC_3", RC_Signal[RC_3])
    print("Body Servo Angle Duty is:", body_angle_duty)
    print("Sleep time:", t)

    # execute tail servo, sweep the tail
    if RC_Signal[RC_1] >= RC1_ACTIVATION:
        for i in range(LEFT_DUTY, RIGHT_DUTY + 1):  # sweep right
            Servo_Tail.ChangeDutyCycle(i)
            time.sleep(t)   # delay for t seconds
        for i in range(RIGHT_DUTY, LEFT_DUTY-1, -1):  # sweep back to left
            Servo_Tail.ChangeDutyCycle(i)
            time.sleep(t)  # delay for t seconds
    else:
        Servo_Tail.ChangeDutyCycle((LEFT_DUTY + RIGHT_DUTY)/2.0)  # return to mid position when no signal

    # Change Body Angle
    execute_body_servo()
    # Give a small break to prevent system crash
    time.sleep(SYSTEM_BREAK_TIME)
    print("\n")
