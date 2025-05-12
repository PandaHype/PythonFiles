import customtkinter as ctk
import random

words = {
    0: "APPLE", 1: "BANANA", 2: "GRAPES", 3: "ORANGE", 4: "PEACH",
    5: "LEMON", 6: "MELON", 7: "BERRY", 8: "KIWI", 9: "MANGO",
    10: "PIRATE", 11: "PLANET", 12: "GALAXY", 13: "COMET", 14: "ROCKET",
    15: "SPACE", 16: "ALIEN", 17: "STAR", 18: "SATURN", 19: "METEOR",
    20: "CASTLE", 21: "DRAGON", 22: "SWORD", 23: "WIZARD", 24: "MAGIC",
    25: "SHIELD", 26: "KNIGHT", 27: "KINGDOM", 28: "CROWN", 29: "THRONE",
    30: "FOREST", 31: "JUNGLE", 32: "DESERT", 33: "ISLAND", 34: "OCEAN",
    35: "RIVER", 36: "MOUNTAIN", 37: "VALLEY", 38: "VOLCANO", 39: "GLACIER",
    40: "PENGUIN", 41: "GIRAFFE", 42: "MONKEY", 43: "TIGER", 44: "ZEBRA",
    45: "RABBIT", 46: "CHICKEN", 47: "DONKEY", 48: "PARROT", 49: "KITTEN",
    50: "BUTTON", 51: "WINDOW", 52: "PENCIL", 53: "BACKPACK", 54: "SCISSORS",
    55: "MIRROR", 56: "TUNNEL", 57: "LADDER", 58: "BUCKET", 59: "BOTTLE",
    60: "CAMERA", 61: "FOLDER", 62: "PILLOW", 63: "BLANKET", 64: "HAMMER",
    65: "GARDEN", 66: "SHOVEL", 67: "GALAXY", 68: "CLOUD", 69: "STORM",
    70: "THUNDER", 71: "LIGHTNING", 72: "SUNSHINE", 73: "BREEZE", 74: "SNOWMAN",
    75: "NUMBER", 76: "SNOWBALL", 77: "HOLIDAY", 78: "VACATION", 79: "TRAVEL",
    80: "TICKET", 81: "AIRPORT", 82: "LUGGAGE", 83: "TRAIN", 84: "SUBWAY",
    85: "BUS", 86: "BICYCLE", 87: "SKATE", 88: "HELMET", 89: "SCOOTER",
    90: "PYTHON", 91: "ROBOT", 92: "GIANT", 93: "GHOST", 94: "ZOMBIE",
    95: "NINJA", 96: "VIKING", 97: "DETECTIVE", 98: "SPY", 99: "MONSTER"
}

# word = random.choice(list(words.values()))
word = words[0]
length = len(word)
pos = 1

def letter_guess(letter,button):
    global word, word_box
    for x in word:
        if letter == x:
            print(f"Word contained: {letter}")
            button.configure(state="disabled", fg_color="light green")
            

    if letter not in word:
        button.configure(state="disabled", fg_color="red")


root = ctk.CTk()
root.title("My Test Enviorment")
root.geometry("500x400")

word_box = ctk.CTkLabel(root, text="_ " * length)
word_box.pack()

a_button = ctk.CTkButton(root, text="A", width=30, fg_color="blue")
a_button.configure(command=lambda: letter_guess("A", a_button))
a_button.pack()


root.mainloop()

