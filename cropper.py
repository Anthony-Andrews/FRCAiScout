import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

scaleFactor = 2

outlineColor = 'blue'

class ImageCroppingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk image cropper")

        # Create a menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Create a "File" menu
        self.file_menu = tk.Menu(self.menu_bar)

        self.menu_bar.add_cascade(label="Open Directory", command=self.open_directory)

        self.menu_bar.add_cascade(label="Crop & Save", command=self.crop_image)

        self.menu_bar.add_cascade(label="Next Image", command=self.next_image)
        self.menu_bar.add_cascade(label="Previous Image", command=self.previous_image)

        self.menu_bar.add_cascade(label="About", command=self.show_info)

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.current_image = None
        self.scaled_image = None
        self.image_path = None
        self.crop_rect = None
        self.image_files = []  # List to store image files in the directory
        self.current_index = 0  # Index of the currently displayed image

        # List to store references to cursor lines
        self.cursor_lines = []

        # Binding Ctrl+S (or Command+S on macOS) to save the crop
        self.root.bind("<Control-s>", self.save_cropped_image)

    def open_directory(self):
        self.root.title("Select image directory:")
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
            if self.image_files:
                self.current_index = 0
                self.load_current_image(directory_path)

    def load_current_image(self, directory_path):
        self.image_path = os.path.join(directory_path, self.image_files[self.current_index])
        self.current_image = Image.open(self.image_path)
        self.root.title(self.image_path)
        self.scaled_image = self.current_image.copy()
        self.scaled_image.thumbnail((self.current_image.width // scaleFactor, self.current_image.height // scaleFactor))
        self.display_image()

        # Resize the window to match the image resolution
        self.root.geometry(f"{self.current_image.width // scaleFactor}x{self.current_image.height // scaleFactor}")

    def display_image(self):
        if self.scaled_image:
            self.photo = ImageTk.PhotoImage(self.scaled_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            self.canvas.bind("<ButtonPress-1>", self.start_crop)
            self.canvas.bind("<B1-Motion>", self.draw_crop_rect)
            self.canvas.bind("<Motion>", self.draw_cursor_lines)

    def start_crop(self, event):
        self.crop_start_x, self.crop_start_y = event.x, event.y
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = None

    def draw_cursor_lines(self, event):
        x, y = event.x, event.y
        # Delete old cursor lines
        for line in self.cursor_lines:
            self.canvas.delete(line)
        self.cursor_lines.clear()
        # Draw vertical and horizontal lines at the cursor position
        self.cursor_lines.append(self.canvas.create_line(x, 0, x, self.current_image.height, fill=outlineColor))
        self.cursor_lines.append(self.canvas.create_line(0, y, self.current_image.width, y, fill=outlineColor))

    def draw_crop_rect(self, event):
        x, y = event.x, event.y
        if self.crop_rect:
            self.canvas.coords(self.crop_rect, self.crop_start_x, self.crop_start_y, x, y)
        else:
            self.crop_rect = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, x, y, outline=outlineColor)

    def crop_image(self):
        if self.image_path and self.crop_rect:
            x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
            x1, y1, x2, y2 = int(x1 * 2), int(y1 * 2), int(x2 * 2), int(y2 * 2)  # Scale up coordinates for cropping
            cropped_image = self.current_image.crop((x1, y1, x2, y2))
            cropped_image.save(self.image_path)  # Save the cropped image with the same filename
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
            self.next_image()  # Move to the next image


    def save_cropped_image(self, event):
        if self.image_path and self.crop_rect:
            self.crop_image()

    def next_image(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.load_current_image(os.path.dirname(self.image_path))

    def previous_image(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.load_current_image(os.path.dirname(self.image_path))

    def show_info(self):
        info_text = "Shortcuts:\n"
        info_text += "CTRL+S - save and move to the next image in the directory\n" 
        info_text += " \n"
        info_text += "https://github.com/Anthony-Andrews/bulk-cropper/"
        messagebox.showinfo("About", info_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCroppingApp(root)
    root.mainloop()