import random
import sys
import time
from colorama import init, Fore, Style

init()
indicators = '\\|/-'
options = ["ROCK", "PAPER", "SCISSORS"]
winning_combinations = {
    ("PAPER", "ROCK"): "PAPER",
    ("SCISSORS", "PAPER"): "SCISSORS",
    ("ROCK", "SCISSORS"): "ROCK"
}

def thinking():
    """Display a thinking animation"""
    for _ in range(5):
        for indicator in indicators:
            print(f"\r[{indicator}] Thinking...", end="")
            time.sleep(0.1)
    print("\r\033[K", end="")

while True:
    # Get user input for their choice
    c_you = input(Fore.YELLOW + "Choose ROCK, PAPER or SCISSORS: " + Style.RESET_ALL + Fore.LIGHTMAGENTA_EX).upper()
    c_ai = random.choice(options)

    if c_you == c_ai: # It's a draw
        thinking() # Display thinking animation
        print(Fore.CYAN + f"Draw! you chose: {c_you}, computer chose: {c_ai}")


    elif c_you in options: # It's a valid choice

        thinking() # Display thinking animation

        if (c_you, c_ai) in winning_combinations:
            print(Fore.GREEN + f"You win! you chose: {c_you}, computer chose: {c_ai}")

        else: 
            print(Fore.LIGHTRED_EX + f"You lose! you chose: {c_you}, computer chose: {c_ai}")


    else: print(Fore.WHITE + "Please enter ROCK, PAPER or SCISSORS")
    print()
