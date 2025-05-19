import customtkinter as ctk



root = ctk.CTk()
root.geometry("1600x1000")


canvas = ctk.CTkCanvas(root, width=200, height=250, bg="dark gray")
canvas.create_oval(110, 50, 150, 90, width=4)
canvas.create_oval(121,60, 126,65, width=4)
canvas.create_oval(134,60, 139,65, width=4)
canvas.pack()

root.mainloop()