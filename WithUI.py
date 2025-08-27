# Import modules from Pyfirmata
from pyfirmata import Arduino, util, INPUT, OUTPUT, PWM
# Import inbuilt time module
import time
# Import inbuilt random module
import random

import threading
from uiCode import *

app = MainApp()
kivy_thread = threading.Thread(target=app.run)
kivy_thread.start()

from kivy.clock import Clock

def update_gui_choice(player1_choice, player2_choice):
    Clock.schedule_once(lambda dt: app.change_gesture_images(player1_choice, player2_choice), 0)
    Clock.schedule_once(lambda dt: app.change_imgtxt(player1_choice, player2_choice), 0)

def update_gui(img1, img2):
    Clock.schedule_once(lambda dt: app.change_images(img1, img2), 0)

# Create an Arduino board instance
board = Arduino("COM7")

# Define custom commands
START_TONE = 0x01  # Replace with the command byte you defined
TIME_UP = 0x02  # Replace with the command byte you defined
DRAW = 0x03
WIN = 0x04
DEFEAT = 0x05

# pin numbers
player1_LED1 = board.get_pin('d:2:o')
player1_LED2 = board.get_pin('d:3:o')
player1_LED4 = board.get_pin('d:4:o')
player2_LED1 = board.get_pin('d:5:o')
player2_LED2 = board.get_pin('d:6:o')
player2_LED4 = board.get_pin('d:7:o')
choice_LED1 = board.get_pin('d:8:o')
choice_LED2 = board.get_pin('d:9:o')
choice_LED4 = board.get_pin('d:10:o')
indicator_LED = board.get_pin('d:13:o')
button0 = board.get_pin('d:12:i')
button1 = board.get_pin('a:1:i')
button2 = board.get_pin('a:2:i')
button3 = board.get_pin('a:3:i')
button4 = board.get_pin('a:4:i')
button5 = board.get_pin('a:0:i')
#buzzer = board.digital[11]

# Start iterator to receive input data
it = util.Iterator(board)
it.start()

# Setup
#buzzer.mode = PWM

previous_button_state = 0
game_state = 0

player1_marks = 0 # user
player2_marks = 0 # computer

def buzzer_tone(tone):
    global buzzer
    if tone == "start_tone":
        board.send_sysex(START_TONE,[])
        time.sleep(0.01)
    elif tone == "time_up":
        board.send_sysex(TIME_UP,[])
        time.sleep(0.01)
    elif tone == "draw":
        board.send_sysex(DRAW,[])
        time.sleep(3)
    elif tone == "win":
        board.send_sysex(WIN,[])
        time.sleep(3)
    elif tone == "defeat":
        board.send_sysex(DEFEAT,[])
        time.sleep(3)


def led_pattern(pattern):
    global choice_LED4, choice_LED2, choice_LED1
    if pattern == "draw":
        '''choice_LED4.write(1)
        choice_LED2.write(1)
        choice_LED1.write(1)
        time.sleep(1)
        choice_LED4.write(0)
        choice_LED2.write(0)
        choice_LED1.write(0)'''
    elif pattern == "win":
        '''choice_LED4.write(1)
        choice_LED2.write(1)
        choice_LED1.write(1)
        time.sleep(1)
        choice_LED4.write(0)
        choice_LED2.write(0)
        choice_LED1.write(0)'''
    elif pattern == "defeat":
        '''choice_LED4.write(1)
        choice_LED2.write(1)
        choice_LED1.write(1)
        time.sleep(1)
        choice_LED4.write(0)
        choice_LED2.write(0)
        choice_LED1.write(0)'''


def indicator(state):
    global indicator_LED
    if state == "blink":
        indicator_LED.write(1)
        time.sleep(0.33)
        indicator_LED.write(0)
    elif state == "off":
        indicator_LED.write(0)

def led_off():
    player1_LED4.write(0)
    player1_LED2.write(0)
    player1_LED1.write(0)

    player2_LED4.write(0)
    player2_LED2.write(0)
    player2_LED1.write(0)

    time.sleep(0.09)

def display_marks():
    global player1_LED4, player1_LED2, player1_LED1
    global player2_LED4, player2_LED2, player2_LED1
    global player1_marks, player2_marks
    global app
    app.change_score(player1_marks, player2_marks)
    led_off()

    time.sleep(0.09)

    setup = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1))

    player1_LED4.write(setup[player1_marks][0])
    player1_LED2.write(setup[player1_marks][1])
    player1_LED1.write(setup[player1_marks][2])

    player2_LED4.write(setup[player2_marks][0])
    player2_LED2.write(setup[player2_marks][1])
    player2_LED1.write(setup[player2_marks][2])

def display_gesture(gesture):
    global choice_LED4, choice_LED2, choice_LED1
    choice_LED4.write(0)
    choice_LED4.write(0)
    choice_LED4.write(0)

    time.sleep(0.05)

    gestures = {
        "rock": (0, 0, 1),
        "paper": (0, 1, 0),
        "scissors": (1, 0, 0),
        "lizard": (0, 1, 1),
        "spock": (1, 0, 1)
    }
    choice_values = gestures[gesture]
    choice_LED4.write(choice_values[0])
    choice_LED2.write(choice_values[1])
    choice_LED1.write(choice_values[2])

def winner(player1_choice, player2_choice):

    print(player1_choice.capitalize(), "VS", player2_choice.capitalize())

    default = (
        ("rock", "paper", "spock"),
        ("paper", "scissors", "lizard"),
        ("scissors", "rock", "spock"),
        ("lizard", "rock", "scissors"),
        ("spock", "paper", "lizard"),
    )
    if player1_choice == player2_choice:
        return "draw"
    else:
        for i in range(5):
            if player1_choice == default[i][0] and (player2_choice == default[i][1] or player2_choice == default[i][2]):
                return "computer"
        return "user"

def take_choice():
    start_time = time.time()
    previous_button_states = [0, 0, 0, 0, 0, 0]
    choices = ("rock", "paper", "scissors", "lizard", "spock")
    while time.time() - start_time <= 3:
        indicator_LED.write(1)
        time.sleep(0.3)
        indicator_LED.write(0)
        time.sleep(0.01)
        button_states = [button0.read(), button1.read(), button2.read(), button3.read(), button4.read(), button5.read()]
        if button_states[0] == True:
            return "end"
        else:
            for i in range(0, 5):
                if button_states[i+1] > 0.5:
                    return choices[i]

    return "none"

def Game(state):
    global button0, button1, button2, button3, button4, button5
    global player1_marks, player2_marks
    global app
    if state == 1:
        # start the game
        print("-----------------------Welcome to Rock, Paper, Scissors, Lizard, Spock Game----------------------\n"
              "  ______________________________________________________________________________________\n"
              "  |* You can choose your gesture using buttons                                          |\n"
              "  |* You only have 3 seconds to choose your gesture. Otherwise computer will get 1 mark |\n"
              "  |* Winner will be chosen after 7 rounds                                               |\n"
              "  |* Marks and computer's gestures will be indicated using corresponding LEDs           |\n"
              "  |* To end the game press the button start/end                                         |\n"
              "  ______________________________________________________________________________________")
        print(" ")
        app.change_label("Game Started")
        led_off()
        player1_marks = 0  # user
        player2_marks = 0  # computer
        app.change_score(player1_marks, player2_marks)
        time.sleep(3)

        game_round = 1

        # Game rounds

        while game_round <=7 and state == 1 :
            print("ROUND :", game_round)
            app.change_round(game_round)
            print(" ")
            print(" * Choose your gesture after buzzer sound")
            app.change_label("Choose your gesture after buzzer sound")
            print("")
            time.sleep(2)

            buzzer_tone("start_tone")
            indicator("blink")
            start_time = time.time()
            choices = ("toggle", "rock", "paper", "scissors", "lizard", "spock")
            choice = "none"
            global button0_state, game_state
            previous_button_states = [button0_state, 0, 0, 0, 0, 0]

            choice = take_choice()
            buzzer_tone("time_up")
            indicator("off")

            # Player1_marks, Player2_marks

            if choice == "end":
                break
            elif choice == "none":
                player2_marks = player2_marks + 1
                print("    ------Timeout--------")
                print(" ")
                app.change_label("Timeout!")
                print("       ~ Computer got 1 mark ")
                print(" ")
                display_marks()
                time.sleep(1)
                game_round = game_round + 1
                continue
            else:
                player1_choice = choice
                player2_choice = choices[random.randint(1, 5)]
                display_gesture(player2_choice)
                result = winner(player1_choice, player2_choice)
                update_gui_choice(player1_choice, player2_choice)

                if result == "draw":
                    print("")
                    print("        ~ Same gestures")
                    print("")
                    app.change_label("Same gestures")
                    game_round = game_round + 1
                    time.sleep(1)
                    continue

                elif result == "computer":
                    player2_marks = player2_marks + 1
                    print(" ")
                    print("       ~ Computer got 1 mark")
                    print(" ")
                    app.change_label("Computer got 1 mark")
                    display_marks()
                    game_round = game_round + 1
                    time.sleep(1)
                    continue

                elif result == "user":
                    player1_marks = player1_marks + 1
                    print(" ")
                    print("       ~ You got 1 mark")
                    print(" ")
                    app.change_label("You got 1 mark")
                    display_marks()
                    game_round = game_round + 1
                    time.sleep(1)
                    continue
        Game(0)


    if state == 0:
        app.change_label("Game End")
        app.change_imgtxt("", "")
        print(" ")
        print("................|GAME END|...................")
        print("     Player's_marks   : ", player1_marks, )
        print("     Computer's_marks : ", player2_marks)
        print(" ")
        print("             ", player1_marks, "VS", player2_marks)
        print(" ")

        # Winner
        if player1_marks == player2_marks:
            print("~ Same Marks")
            print(" ")
            app.change_label("Both got same marks")
            update_gui("game_over", "draw")
            buzzer_tone("draw")
            time.sleep(1)
            #led_pattern("draw")

        elif player1_marks > player2_marks:
            print("   ++++++++ YOU WIN ++++++++++")
            print("   ")
            app.change_label("You win")
            update_gui("game_over", "user")
            buzzer_tone("win")
            time.sleep(1)
            #led_pattern("win")

        else:
            print("   ++++++++ COMPUTER WIN ++++++++++")
            print("   ")
            app.change_label("Computer win")
            update_gui("game_over", "computer")
            buzzer_tone("defeat")
            time.sleep(1)
            #led_pattern("defeat")

        global game_state
        game_state = 0
        return print(" * Press start button to play again"),time.sleep(3)

while True:
    time.sleep(0.01)

    # Get button current state
    button0_state = button0.read()

    # Check if button has been released
    if button0_state != previous_button_state:
        if button0_state == 0:
            # toggle LED
            game_state ^= 1
            Game(game_state)

    # Save current button state as previous
    # for the next loop iteration
    previous_button_state = button0_state