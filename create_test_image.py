from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple test image with sample text
def create_test_image():
    # Create a white background image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Use default font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add sample text
    text = """STUDENT ID: S12345678
    
    Last Name: Doe
    First Name: John
    
    Date of Birth: 1990-01-15
    
    This is a test document for OCR validation.
    """
    
    # Draw text on image
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save the image
    image.save('test_document.jpg')
    print("Test image created: test_document.jpg")

if __name__ == "__main__":
    create_test_image()
