from tkinter import ttk, Tk, PhotoImage, Canvas, filedialog, colorchooser, messagebox, RIDGE, GROOVE, ROUND, Scale, HORIZONTAL
import cv2
from PIL import ImageTk, Image
import numpy as np

class FrontEnd:
    def __init__(self, master):
        self.master = master
        self.original_image = None
        self.edited_image = None
        self.filtered_image = None
        self.filename = None
        self.ratio = 1
        self.color_code = ((255, 0, 0), '#ff0000')  # Default color: red
        self.text_extracted = "hello"  # Default text
        self.font_size = 2  # Default font size
        self.menu_initialisation()

    def menu_initialisation(self):
        self.master.geometry('800x700+250+10')
        self.master.title('Image Editor App with Tkinter and OpenCV')

        # Header
        self.frame_header = ttk.Frame(self.master)
        self.frame_header.pack(pady=10)
        try:
            self.logo = PhotoImage(file='python_logo.gif').subsample(3, 3)
            ttk.Label(self.frame_header, image=self.logo).grid(row=0, column=0, rowspan=2, padx=10)
        except:
            ttk.Label(self.frame_header, text="[Logo]").grid(row=0, column=0, rowspan=2, padx=10)
        ttk.Label(self.frame_header, text='Welcome to the Image Editor App!', font=('Arial', 14, 'bold')).grid(row=0, column=1, padx=10)
        ttk.Label(self.frame_header, text='Upload, edit, and save your images easily!', font=('Arial', 10)).grid(row=1, column=1, padx=10)

        # Main Menu
        self.frame_menu = ttk.Frame(self.master)
        self.frame_menu.pack(pady=10)
        self.frame_menu.config(relief=RIDGE, padding=(50, 15))

        buttons = [
            ("Upload An Image", self.upload_action),
            ("Crop Image", self.crop_action),
            ("Add Text", self.text_action_1),
            ("Draw Over Image", self.draw_action),
            ("Apply Filters", self.filter_action),
            ("Blur/Smoothening", self.blur_action),
            ("Adjust Levels", self.adjust_action),
            ("Rotate", self.rotate_action),
            ("Flip", self.flip_action),
            ("Save As", self.save_action)
        ]
        for i, (text, command) in enumerate(buttons):
            ttk.Button(self.frame_menu, text=text, command=command).grid(row=i, column=0, padx=5, pady=5, sticky='sw')

        self.canvas = Canvas(self.frame_menu, bg="gray", width=300, height=400)
        self.canvas.grid(row=0, column=1, rowspan=10, padx=10)

        # Footer Menu
        self.apply_and_cancel = ttk.Frame(self.master)
        self.apply_and_cancel.pack(pady=10)
        ttk.Button(self.apply_and_cancel, text="Apply", command=self.apply_action).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.apply_and_cancel, text="Cancel", command=self.cancel_action).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.apply_and_cancel, text="Revert All Changes", command=self.revert_action).grid(row=0, column=2, padx=5, pady=5)

        # Status Label
        self.status_label = ttk.Label(self.master, text="No image loaded", relief=GROOVE)
        self.status_label.pack(fill='x', pady=5)

    # Main Menu Actions
    def upload_action(self):
        self.canvas.delete("all")
        self.filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if self.filename:
            self.original_image = cv2.imread(self.filename)
            if self.original_image is None:
                messagebox.showerror("Error", "Failed to load image. Please select a valid image file.")
                self.status_label.config(text="No image loaded")
                return
            self.edited_image = self.original_image.copy()
            self.filtered_image = self.original_image.copy()
            self.display_image(self.edited_image)
            self.status_label.config(text=f"Loaded: {self.filename.split('/')[-1]}")
        else:
            self.status_label.config(text="No image loaded")

    def text_action_1(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        ttk.Label(self.side_frame, text="Enter the text").grid(row=0, column=2, padx=5, pady=5, sticky='sw')
        self.text_on_image = ttk.Entry(self.side_frame)
        self.text_on_image.grid(row=1, column=2, padx=5, sticky='sw')
        ttk.Button(self.side_frame, text="Pick A Font Color", command=self.choose_color).grid(row=2, column=2, padx=5, pady=5, sticky='sw')
        ttk.Label(self.side_frame, text="Font Size").grid(row=3, column=2, padx=5, pady=5, sticky='sw')
        self.font_size_slider = Scale(self.side_frame, from_=0.5, to=5, resolution=0.1, orient=HORIZONTAL, command=self.update_font_size)
        self.font_size_slider.set(self.font_size)
        self.font_size_slider.grid(row=4, column=2, padx=5, sticky='sw')
        self.text_action()

    def update_font_size(self, value):
        self.font_size = float(value)

    def crop_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.rectangle_id = 0
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_end_x = 0
        self.crop_end_y = 0
        self.canvas.bind("<ButtonPress>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.crop)
        self.canvas.bind("<ButtonRelease>", self.end_crop)

    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y

    def crop(self, event):
        if self.rectangle_id:
            self.canvas.delete(self.rectangle_id)
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        self.rectangle_id = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y, width=1)

    def end_crop(self, event):
        if self.crop_start_x <= self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x > self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x <= self.crop_end_x and self.crop_start_y > self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)
        else:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)
        x = slice(start_x, end_x, 1)
        y = slice(start_y, end_y, 1)
        self.filtered_image = self.edited_image[y, x]
        self.display_image(self.filtered_image)

    def text_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.rectangle_id = 0
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_end_x = 0
        self.crop_end_y = 0
        self.canvas.bind("<ButtonPress>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.crop)
        self.canvas.bind("<ButtonRelease>", self.end_text_crop)

    def end_text_crop(self, event):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        if self.crop_start_x <= self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x > self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x <= self.crop_end_x and self.crop_start_y > self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)
        else:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)
        self.text_extracted = self.text_on_image.get() or "hello"
        start_font = (start_x, start_y)
        r, g, b = tuple(map(int, self.color_code[0]))
        self.filtered_image = cv2.putText(
            self.edited_image.copy(), self.text_extracted, start_font, cv2.FONT_HERSHEY_SIMPLEX, self.font_size, (b, g, r), 5)
        self.display_image(self.filtered_image)

    def draw_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        self.canvas.bind("<ButtonPress>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.draw_color_button = ttk.Button(self.side_frame, text="Pick A Color", command=self.choose_color)
        self.draw_color_button.grid(row=0, column=2, padx=5, pady=5, sticky='sw')

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose color")
        if color[1]:  # Only update if a color was selected
            self.color_code = color

    def start_draw(self, event):
        self.x = event.x
        self.y = event.y
        self.draw_ids = []

    def draw(self, event):
        self.draw_ids.append(self.canvas.create_line(self.x, self.y, event.x, event.y, width=2,
                                                    fill=self.color_code[1], capstyle=ROUND, smooth=True))
        cv2.line(self.filtered_image, (int(self.x * self.ratio), int(self.y * self.ratio)),
                 (int(event.x * self.ratio), int(event.y * self.ratio)),
                 tuple(map(int, self.color_code[0])), thickness=int(self.ratio * 2), lineType=cv2.LINE_AA)
        self.x = event.x
        self.y = event.y

    # Filter Menu
    def refresh_side_frame(self):
        try:
            self.side_frame.grid_forget()
        except:
            pass
        self.canvas.unbind("<ButtonPress>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease>")
        if self.edited_image is not None:
            self.display_image(self.edited_image)
        self.side_frame = ttk.Frame(self.frame_menu)
        self.side_frame.grid(row=0, column=2, rowspan=10)
        self.side_frame.config(relief=GROOVE, padding=(50, 15))

    def filter_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        filters = [
            ("Negative", self.negative_action),
            ("Black And White", self.bw_action),
            ("Stylisation", self.stylisation_action),
            ("Sketch Effect", self.sketch_action),
            ("Emboss", self.emb_action),
            ("Sepia", self.sepia_action),
            ("Binary Thresholding", self.binary_threshold_action),
            ("Erosion", self.erosion_action),
            ("Dilation", self.dilation_action)
        ]
        for i, (text, command) in enumerate(filters):
            ttk.Button(self.side_frame, text=text, command=command).grid(row=i, column=2, padx=5, pady=5, sticky='sw')

    # Blur Menu
    def blur_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        ttk.Label(self.side_frame, text="Averaging Blur").grid(row=0, column=2, padx=5, sticky='sw')
        self.average_slider = Scale(self.side_frame, from_=0, to=256, orient=HORIZONTAL, command=self.averaging_action)
        self.average_slider.grid(row=1, column=2, padx=5, sticky='sw')
        ttk.Label(self.side_frame, text="Gaussian Blur").grid(row=2, column=2, padx=5, sticky='sw')
        self.gaussian_slider = Scale(self.side_frame, from_=0, to=256, orient=HORIZONTAL, command=self.gaussian_action)
        self.gaussian_slider.grid(row=3, column=2, padx=5, sticky='sw')
        ttk.Label(self.side_frame, text="Median Blur").grid(row=4, column=2, padx=5, sticky='sw')
        self.median_slider = Scale(self.side_frame, from_=0, to=256, orient=HORIZONTAL, command=self.median_action)
        self.median_slider.grid(row=5, column=2, padx=5, sticky='sw')

    # Rotate and Flip Menu
    def rotate_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        ttk.Button(self.side_frame, text="Rotate Left", command=self.rotate_left_action).grid(row=0, column=2, padx=5, pady=5, sticky='sw')
        ttk.Button(self.side_frame, text="Rotate Right", command=self.rotate_right_action).grid(row=1, column=2, padx=5, pady=5, sticky='sw')

    def flip_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        ttk.Button(self.side_frame, text="Vertical Flip", command=self.vertical_action).grid(row=0, column=2, padx=5, pady=5, sticky='sw')
        ttk.Button(self.side_frame, text="Horizontal Flip", command=self.horizontal_action).grid(row=1, column=2, padx=5, pady=5, sticky='sw')

    # Adjust Menu
    def adjust_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.refresh_side_frame()
        ttk.Label(self.side_frame, text="Brightness").grid(row=0, column=2, padx=5, pady=5, sticky='sw')
        self.brightness_slider = Scale(self.side_frame, from_=0, to_=2, resolution=0.1, orient=HORIZONTAL, command=self.brightness_action)
        self.brightness_slider.grid(row=1, column=2, padx=5, sticky='sw')
        self.brightness_slider.set(1)
        ttk.Label(self.side_frame, text="Saturation").grid(row=2, column=2, padx=5, pady=5, sticky='sw')
        self.saturation_slider = Scale(self.side_frame, from_=-200, to=200, resolution=0.5, orient=HORIZONTAL, command=self.saturation_action)
        self.saturation_slider.grid(row=3, column=2, padx=5, sticky='sw')
        self.saturation_slider.set(0)

    def save_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        original_file_type = self.filename.split('.')[-1]
        filename = filedialog.asksaveasfilename(defaultextension=f".{original_file_type}", filetypes=[("Image files", f"*.{original_file_type}")])
        if filename:
            cv2.imwrite(filename, self.edited_image)
            self.filename = filename
            self.status_label.config(text=f"Saved as: {filename.split('/')[-1]}")
            messagebox.showinfo("Success", "Image saved successfully!")
        else:
            self.status_label.config(text="Save cancelled")

    # Filter Actions
    def negative_action(self):
        self.filtered_image = cv2.bitwise_not(self.edited_image)
        self.display_image(self.filtered_image)

    def bw_action(self):
        self.filtered_image = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2GRAY)
        self.filtered_image = cv2.cvtColor(self.filtered_image, cv2.COLOR_GRAY2BGR)
        self.display_image(self.filtered_image)

    def stylisation_action(self):
        self.filtered_image = cv2.stylization(self.edited_image, sigma_s=150, sigma_r=0.25)
        self.display_image(self.filtered_image)

    def sketch_action(self):
        ret, self.filtered_image = cv2.pencilSketch(self.edited_image, sigma_s=60, sigma_r=0.5, shade_factor=0.02)
        self.display_image(self.filtered_image)

    def emb_action(self):
        kernel = np.array([[0, -1, -1], [1, 0, -1], [1, 1, 0]])
        self.filtered_image = cv2.filter2D(self.original_image, -1, kernel)
        self.display_image(self.filtered_image)

    def sepia_action(self):
        kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        self.filtered_image = cv2.filter2D(self.original_image, -1, kernel)
        self.display_image(self.filtered_image)

    def binary_threshold_action(self):
        ret, self.filtered_image = cv2.threshold(self.edited_image, 127, 255, cv2.THRESH_BINARY)
        self.display_image(self.filtered_image)

    def erosion_action(self):
        kernel = np.ones((5, 5), np.uint8)
        self.filtered_image = cv2.erode(self.edited_image, kernel, iterations=1)
        self.display_image(self.filtered_image)

    def dilation_action(self):
        kernel = np.ones((5, 5), np.uint8)
        self.filtered_image = cv2.dilate(self.edited_image, kernel, iterations=1)
        self.display_image(self.filtered_image)

    # Blur Actions
    def averaging_action(self, value):
        value = int(value)
        if value % 2 == 0:
            value += 1
        self.filtered_image = cv2.blur(self.edited_image, (value, value))
        self.display_image(self.filtered_image)

    def gaussian_action(self, value):
        value = int(value)
        if value % 2 == 0:
            value += 1
        self.filtered_image = cv2.GaussianBlur(self.edited_image, (value, value), 0)
        self.display_image(self.filtered_image)

    def median_action(self, value):
        value = int(value)
        if value % 2 == 0:
            value += 1
        self.filtered_image = cv2.medianBlur(self.edited_image, value)
        self.display_image(self.filtered_image)

    # Adjust Actions
    def brightness_action(self, value):
        self.filtered_image = cv2.convertScaleAbs(self.edited_image, alpha=float(value))
        self.display_image(self.filtered_image)

    def saturation_action(self, value):
        self.filtered_image = cv2.convertScaleAbs(self.edited_image, beta=float(value))
        self.display_image(self.filtered_image)

    # Rotate and Flip Actions
    def rotate_left_action(self):
        self.filtered_image = cv2.rotate(self.filtered_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.display_image(self.filtered_image)

    def rotate_right_action(self):
        self.filtered_image = cv2.rotate(self.filtered_image, cv2.ROTATE_90_CLOCKWISE)
        self.display_image(self.filtered_image)

    def vertical_action(self):
        self.filtered_image = cv2.flip(self.filtered_image, 0)
        self.display_image(self.filtered_image)

    def horizontal_action(self):
        self.filtered_image = cv2.flip(self.filtered_image, 1)
        self.display_image(self.filtered_image)

    # Footer Actions
    def apply_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.edited_image = self.filtered_image.copy()
        self.display_image(self.edited_image)
        self.status_label.config(text="Changes applied")

    def cancel_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.display_image(self.edited_image)
        self.status_label.config(text="Changes cancelled")

    def revert_action(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        self.edited_image = self.original_image.copy()
        self.filtered_image = self.original_image.copy()
        self.display_image(self.original_image)
        self.status_label.config(text="All changes reverted")

    def display_image(self, image=None):
        self.canvas.delete("all")
        if image is None:
            if self.edited_image is not None:
                image = self.edited_image.copy()
            else:
                return
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        ratio = height / width
        new_width = width
        new_height = height
        if height > 400 or width > 300:
            if ratio < 1:
                new_width = 300
                new_height = int(new_width * ratio)
            else:
                new_height = 400
                new_width = int(new_height / ratio)
        self.ratio = height / new_height
        self.new_image = cv2.resize(image, (new_width, new_height))
        self.new_image = ImageTk.PhotoImage(Image.fromarray(self.new_image))
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(new_width / 2, new_height / 2, image=self.new_image)

if __name__ == "__main__":
    root = Tk()
    app = FrontEnd(root)
    root.mainloop()