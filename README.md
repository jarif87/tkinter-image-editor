## Image Editor App with Tkinter and OpenCV

**A simple desktop application for editing images using Tkinter for the GUI and OpenCV for image processing. Features include cropping, adding text, drawing, applying filters, blurring, adjusting brightness/saturation, rotating, flipping, and saving images.**

## Features
- Upload Image: Load images (PNG, JPG, JPEG, BMP, GIF).
- Crop Image: Select and crop a region of the image.
- Add Text: Add customizable text with color and font size.
- Draw: Freehand drawing with selectable colors.
- Filters: Apply effects like negative, black-and-white, stylization, sketch, emboss, sepia, binary thresholding, erosion, and dilation.
- Blur/Smoothening: Apply averaging, Gaussian, or median blur with adjustable intensity.
- Adjust Levels: Modify brightness and saturation.
- Rotate/Flip: Rotate left/right or flip vertically/horizontally.
- Save: Save edited images with the original file extension.

## Prerequisites
- Python 3.7+
### Libraries:
```
pip install opencv-python pillow
```

- Tkinter (included with Python)
- Optional: Place a python_logo.gif in the project directory for the header logo (displays "[Logo]" if missing).

## Installation
1. **Clone or download the repository.**
2. **Install dependencies:**
```
pip install opencv-python pillow
```
3. **Save the code as app.py.**

## Usage
- Run the script:
```
python app.py
```
## Future Improvements
- Add undo/redo functionality.
- Support multiple file formats for saving.
- Include a preview window for filters.
- Enhance drawing with brush size/shape options.


