import pytesseract
import cv2
import numpy as np
import re
from PIL import Image, ImageDraw
import io

class ImageContainer:
    '''Container for images of PDF pages'''

    def __init__(self, image, size=(0,0), rectangles = None):
        self.image = image
        self.size = size
        self.width_in_pt = size[0]
        self.height_in_pt = size[1]
        self.scaled_image = self.image
        self.zoom_factor = 100
        self.search_results = []  # List of (bbox, text) tuples for search results
        self.ocr_data = None  # Cached OCR data for performance

        #list of rectangles [[start_cords, end_coords, color, id], ...]
        self.rectangles = list() if rectangles == None else rectangles

    def increase_zoom(self, number=20):
        '''Zoom in image. Returns new zoom_factor'''
        self.zoom_factor += number
        if self.zoom_factor > 240:
            self.zoom_factor = 240
        else:
            self.scale_image()
        return [self.zoom_factor]

    def decrease_zoom(self, number=20):
        '''Zoom out of image. Returns new zoom_factor'''
        self.zoom_factor -= number
        if self.zoom_factor < 20:
            self.zoom_factor = 20
        else:self.scale_image()
        return [self.zoom_factor]

    def scale_image(self):
        '''Scale original size image for display in Graph element.'''
        width, height = self.image.size
        newwidth = int(width * self.zoom_factor / 100)
        newheight = int(height * self.zoom_factor / 100)
        self.scaled_image = self.image.resize((newwidth, newheight), resample=Image.LANCZOS)

    def undo(self):
        '''Go back in history. Remove last rectangle and redraw rectangles.'''
        if len(self.rectangles)>0:
            self.rectangles.pop()
        return self

    def data(self):
        '''Return bytes of scaled image.'''
        with io.BytesIO() as output:
            self.scaled_image.save(output, format='PNG')
            data = output.getvalue()
            self.datacache = data
            return data

    def jpg(self, image=None, image_quality=85, scale=1):
        '''Return bytes of compressed image'''
        with io.BytesIO() as output:
            image_to_save = image if scale==1 else image.resize((int(image.width * scale), int(image.height * scale)), resample=Image.LANCZOS)
            image_to_save.save(output, format='JPEG', quality=image_quality, optimize=True)
            data = output.getvalue()
        return data

    def refresh(self):
        '''Update the scaled image and return self'''
        self.scale_image()
        return self

    def finalized_image (self, format='PIL', image_quality=100, scale=1):
        '''Return a copy of the imported image with all the rectangles and in the requested format.'''
        final_image = self.draw_rectangles_on_image(self.image.copy())
        if format in ('JPEG','JPG'):
            return self.jpg(final_image.convert('RGB'), image_quality, scale)
        else:
            return final_image

    def draw_rectangles_on_image(self, image):
        '''Draw the rectangles in self.rectangles on image'''
        draw = ImageDraw.Draw(image)
        for rectangle in self.rectangles:
            draw.rectangle(xy=[rectangle[0],rectangle[1]], fill=rectangle[2])
        return image

    def draw_rectangle(self, start_point, end_point, fill='black'):
        '''Draw a rectangle on graph and add it to the rectangles list'''
        try:
            factor=self.zoom_factor/100

            computed_startpoint_x = int((start_point[0]) / factor)
            computed_startpoint_y = int((start_point[1]) / factor)

            computed_endpoint_x = int((end_point[0]) / factor)
            computed_endpoint_y = int((end_point[1]) / factor)

            start_point_in_original = (computed_startpoint_x ,computed_startpoint_y)
            end_point_in_original = (computed_endpoint_x ,computed_endpoint_y )

            self.rectangles.append((start_point_in_original, end_point_in_original, fill, None))

        except ValueError:
            pass
        return self

    def search_text(self, search_term):
        '''Search for text in the image using OCR and return bounding boxes'''
        self.search_results = []
        if not search_term:
            return []

        # If OCR data is not cached, perform OCR
        if self.ocr_data is None:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            # Use pytesseract to get detailed data about text locations
            self.ocr_data = pytesseract.image_to_data(opencv_image, output_type=pytesseract.Output.DICT)

        # Search for the term in the recognized text using regex
        try:
            pattern = re.compile(search_term, re.IGNORECASE)
        except re.error:
            # If regex compilation fails, fall back to literal string search
            pattern = None

        for i, text in enumerate(self.ocr_data['text']):
            match = False
            if pattern:
                # Try regex matching
                if pattern.search(text):
                    match = True
            else:
                # Fall back to simple string matching
                if search_term.lower() in text.lower():
                    match = True

            if match:
                # Get bounding box coordinates
                x, y, w, h = self.ocr_data['left'][i], self.ocr_data['top'][i], self.ocr_data['width'][i], self.ocr_data['height'][i]
                # Store the bounding box and text
                self.search_results.append(((x, y, x + w, y + h), text))

        return self.search_results

    def ocr_search_text(self, bbox):
        '''Perform OCR on a specified region of the image'''
        try:
            # Crop the image to the specified bounding box
            cropped_image = self.image.crop(bbox)

            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2BGR)

            # Use pytesseract to extract text from the cropped image
            text = pytesseract.image_to_string(opencv_image)

            return text.strip()
        except Exception as e:
            print(f"Error during OCR: {e}")
            return ""

    def clear_search_results(self):
        '''Clear all search results'''
        self.search_results = []
