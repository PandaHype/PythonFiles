import customtkinter as ctk
import random
import string

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

root = ctk.CTk()
root.geometry("1600x1000")
root.title("Hangman")
root.configure(fg_color='#242424')

class HangmanCanvas:
    def __init__(self, master):
        self.canvas = ctk.CTkCanvas(master, width=200, height=250, bg="dark gray")
        self.canvas.pack(pady=50)
        self.steps = [
            self.draw_base,
            self.draw_post,
            self.draw_beam,
            self.draw_rope,
            self.draw_head,
            self.draw_body,
            self.draw_left_arm,
            self.draw_right_arm,
            self.draw_left_leg,
            self.draw_right_leg,
        ]
        self.stage = 0
    def draw_next(self):
        if self.stage < len(self.steps):
            self.steps[self.stage]()
            self.stage += 1

    def reset(self):
        self.canvas.delete("all")
        self.stage = 0

    def draw_base(self):
        self.canvas.create_line(20, 230, 180, 230, width=5)

    def draw_post(self):
        self.canvas.create_line(50, 230, 50, 20, width=4)

    def draw_beam(self):
        self.canvas.create_line(50, 20, 130, 20, width=4)

    def draw_rope(self):
        self.canvas.create_line(130, 20, 130, 50, width=3)

    def draw_head(self):
        self.canvas.create_oval(110, 50, 150, 90, width=4)

    def draw_body(self):
        self.canvas.create_line(130, 90, 130, 150, width=4)

    def draw_left_arm(self):
        self.canvas.create_line(130, 100, 100, 120, width=4)

    def draw_right_arm(self):
        self.canvas.create_line(130, 100, 160, 120, width=4)

    def draw_left_leg(self):
        self.canvas.create_line(130, 150, 110, 190, width=4)

    def draw_right_leg(self):
        self.canvas.create_line(130, 150, 150, 190, width=4)

    def draw_happy_smile(self):
        hangman.reset()
        hangman.draw_next()
        self.canvas.create_oval(80, 60, 120, 100, width=4)
        self.canvas.create_line(100, 100, 100, 160, width=4)
        self.canvas.create_line(100, 110, 70, 130, width=4)
        self.canvas.create_line(100, 110, 130, 130, width=4)
        self.canvas.create_line(100, 160, 80, 200, width=4)
        self.canvas.create_line(100, 160, 120, 200, width=4)
        self.canvas.create_line(90,85, 100,95, 110,85, width=4, smooth=1)
        self.canvas.create_oval(91,70, 96,75, width=3)
        self.canvas.create_oval(104,70, 109,75, width=3)
    def draw_sad_smile(self):
        self.canvas.create_line(120,80, 130,75, 140,80, width=4, smooth=1)
        self.canvas.create_oval(121,60, 126,65, width=3)
        self.canvas.create_oval(134,60, 139,65, width=3) 


class letterbuttons:
    def __init__(self, master, command):
        self.buttons = {}
        self.frame = ctk.CTkFrame(master, fg_color='#242424')
        self.frame.pack()
    
        for i, letter in enumerate(string.ascii_uppercase):
            button = ctk.CTkButton(
                self.frame,
                text=letter,
                width=70,
                height=70,
                command=lambda l=letter: command(l, self.buttons[l])
            )
            button.grid(row=i // 9, column=i % 9, padx=2, pady=2)
            self.buttons[letter] = button

def guess_letter(letter, button):
    global word, hanged, lives, won
    match_found = False
    
    guessed_letters.add(letter)
    if not hanged and not won:
        for x in word:
            if x == letter:
                match_found = True
                button.configure(state="disabled",fg_color="#07BD1C")
                display_var.set(' '.join([l if l in guessed_letters else "_" for l in word]))
        if match_found == False:
            button.configure(state="disabled",fg_color="#CE0F0F")
            hangman.draw_next()
            lives -= 1
            if lives < 1 and not hanged:
                hanged = True
    if set(word) <= guessed_letters:
        won = True
    if hanged or won:
        if won:
            display_result(won,)
        if hanged:
            display_result(hanged)
               
    match_found = False

def display_result(result):
    if result == won:
        for x in range(10): 
            hangman.draw_next()
        hangman.draw_happy_smile()
        
        result_label = ctk.CTkLabel(root,height=30,text="YOU WIN", font=("Arial", 100), text_color="white")
        result_label.place(relx=0.22, rely=0.15, anchor="center")

    if result == hanged:
        for x in range(10): 
            hangman.draw_next()
        hangman.draw_sad_smile()

        result_label = ctk.CTkLabel(root,height=30,text="YOU LOST", font=("Arial", 100), text_color="white")
        result_label.place(relx=0.22, rely=0.15, anchor="center")


hangman = HangmanCanvas(root)

word = random.choice(list(words.values()))
lives = 10
won = False
hanged = False

guessed_letters = set()
length = len(word)

display_var = ctk.StringVar(root, value="_ " * length)

word_box = ctk.CTkLabel(root, textvariable=display_var, font=("Arial", 48), text_color="white")
word_box.pack(pady=50)

letters = letterbuttons(root, guess_letter)

root.mainloop()