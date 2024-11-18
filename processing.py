import cv2
import numpy as np
from rembg import remove
from PIL import Image, ImageEnhance, ExifTags, ImageFile

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

def load_image(input_path):
    """Loads an image from the given path, converts it to RGBA format, and applies orientation corrections based on EXIF data."""
    with open(input_path, 'rb') as f:
        img = Image.open(input_path)
        
        # Correct orientation based on EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation = exif.get(orientation, None)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # If there's no EXIF data or an error occurs, skip orientation handling
            pass

        # next 3 lines strip exif
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        image_without_exif.save(input_path)
        img = image_without_exif

    # Convert to RGBA
    # img = img.convert('RGBA')
    return img

# def load_image(input_path):
#     image = cv2.imread(input_path)
#     return image


def remove_background(image):
    """Removes the background from the given image."""
    # img_bytes = image.tobytes()
    image = remove(image)
    return image

def image_to_rgb(image):
    return image.convert('RGBA')

def resize_and_center(image, size, min_padding=0.1):
    """
    Resizes the image to the specified size, centers the object, and applies padding.
    
    Parameters:
    - image: PIL Image object with the object to be inscribed.
    - size: Target size for the square output image.
    - min_padding: Fractional padding around the object (0.0 means no padding; 0.5 means object fully disappears).
    """
    # Get bounding box of the non-transparent area (after background removal)
    bbox = image.getbbox()
    if not bbox:
        # If no bounding box, return a blank transparent image
        new_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        return new_image

    # Crop the image to the bounding box
    image = image.crop(bbox)

    # Calculate new size with padding
    width, height = image.size
    max_dim = max(width, height)
    padding = size * min_padding  # Calculate padding in pixels
    new_dim = max_dim + 2 * padding  # Total dimension including padding

    # Resize the image while preserving aspect ratio
    scale = (size - 2 * padding) / max_dim
    new_width = int(width * scale)
    new_height = int(height * scale)
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create a new image with a transparent background
    new_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # Center the resized image with padding
    x_offset = (size - new_width) // 2
    y_offset = (size - new_height) // 2
    new_image.paste(image, (int(x_offset), int(y_offset)), image)

    return new_image

def adjust_brightness(image, brightness_level):
    def brightness_rescaler(bl):
        return (5+bl)/(5-(4/5)*bl)
    
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness_level)
    return image

def add_logo(image, logo_path, padding=0.05):
    logo = Image.open(logo_path).convert('RGBA')
    # Resize logo if necessary
    logo.thumbnail((image.width // 5, image.height // 5))
    # Position logo at the top-right corner
    position = (
        int(image.width - logo.width - image.width*padding), 
        int(image.width*padding)
        )
    image.paste(logo, position, logo)
    return image

def process_image(
        input_path, 
        output_path, 
        size, 
        brightness, 
        logo_path, 
        image_padding, 
        logo_padding, 
        ):
    def brightness_rescaler(x):
        return (5+x)/(5-(4/5)*x)
    def padding_rescaler(x):
        return x/20
    # Load the image
    image = load_image(input_path)
    # Remove the background
    image = remove_background(image)    
    # Resize and center
    image = image_to_rgb(image)
    image = resize_and_center(image, size, min_padding=padding_rescaler(image_padding))
    # Adjust brightness
    image = adjust_brightness(image, brightness_rescaler(brightness))
    # Add logo
    image = add_logo(image, logo_path, padding=padding_rescaler(logo_padding))
    # Save processed image
    image.save(output_path, format='PNG')

if __name__ == "__main__":
    input_path = "./static/uploads/original/DSC_7869.JPG"
    output_path = "./out_test/test.PNG"
    logo_path = "./static/logo/logo.png"
    brightness = 1
    logo_padding = 0.05
    image_padding = 0.15

    # Load the image
    image = load_image(input_path)
    # Remove the background
    image = remove_background(image)    
    # Resize and center
    image = image_to_rgb(image)
    image = resize_and_center(image, 750, min_padding=image_padding)
    # Adjust brightness
    image = adjust_brightness(image, brightness)
    # Add logo
    image = add_logo(image, logo_path, padding=logo_padding)

    image.save(output_path, format='PNG')

