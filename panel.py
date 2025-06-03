from tkinter import *
import threading

class Panel:
    def __init__(self, drawing_points):
        self.drawing_points = drawing_points
        self.root = Tk()
        self.root.title("Color Selector")

        self.current_color = (255, 0, 0)  # Default color (blue)

        # Define buttons and assign their command
        Button(self.root, text="Red", bg="red", fg="white", width=10,
               command=lambda: self.set_color((0, 0, 255))).pack(pady=5)
        Button(self.root, text="Green", bg="green", fg="white", width=10,
               command=lambda: self.set_color((0, 255, 0))).pack(pady=5)
        Button(self.root, text="Blue", bg="blue", fg="white", width=10,
               command=lambda: self.set_color((255, 0, 0))).pack(pady=5)
        Button(self.root, text="Black", bg="black", fg="white", width=10,
               command=lambda: self.set_color((0, 0, 0))).pack(pady=5)
        Button(self.root, text="Clear Drawing", width=15,
               command=self.clear_drawing).pack(pady=10)

        threading.Thread(target=self.root.mainloop, daemon=True).start()
        
    def set_color(self, color):
        self.current_color = color

    def clear_drawing(self):
        self.drawing_points.clear()

    def get_color(self):
        return self.current_color
