from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def create_modern_logo():
    # Create a new image with a transparent background
    width, height = 400, 400
    logo = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Modern color scheme
    primary_color = '#2E7D32'  # Darker green
    secondary_color = '#4CAF50'  # Primary green
    accent_color = '#8BC34A'  # Light green
    
    # Draw a modern truck icon
    # Truck body
    draw.rounded_rectangle([120, 200, 320, 280], radius=15, fill=primary_color)
    
    # Truck cabin
    draw.polygon([(200, 160), (320, 160), (320, 200), (240, 200)], fill=secondary_color)
    
    # Windows
    draw.rectangle([260, 170, 300, 190], fill='#B2DFDB')
    draw.rectangle([210, 170, 250, 190], fill='#B2DFDB')
    
    # Wheels
    wheel_color = '#212121'
    wheel_outline = '#000000'
    wheel_size = 40
    
    # Back wheel
    draw.ellipse([140, 260, 140+wheel_size, 260+wheel_size], fill=wheel_color, outline=wheel_outline, width=2)
    draw.ellipse([150, 270, 150+20, 270+20], fill='#424242', outline=wheel_outline, width=1)
    
    # Front wheel
    draw.ellipse([260, 260, 260+wheel_size, 260+wheel_size], fill=wheel_color, outline=wheel_outline, width=2)
    draw.ellipse([270, 270, 270+20, 270+20], fill='#424242', outline=wheel_outline, width=1)
    
    # Add some subtle effects
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([120, 200, 320, 280], radius=15, fill=100)
    mask_draw.polygon([(200, 160), (320, 160), (320, 200), (240, 200)], fill=150)
    
    # Apply gradient
    for y in range(height):
        for x in range(width):
            r, g, b, a = logo.getpixel((x, y))
            if a > 0:
                factor = 0.9 + (y / height) * 0.2
                r = min(255, int(r * factor))
                g = min(255, int(g * factor))
                b = min(255, int(b * factor))
                logo.putpixel((x, y), (r, g, b, a))
    
    # Add a subtle shadow
    shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle([125, 205, 325, 285], radius=15, fill=(0, 0, 0, 50))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    
    # Composite the shadow and logo
    final_logo = Image.alpha_composite(Image.new('RGBA', (width, height), (0, 0, 0, 0)), shadow)
    final_logo = Image.alpha_composite(final_logo, logo)
    
    return final_logo

# Create assets directory if it doesn't exist
os.makedirs('assets', exist_ok=True)

# Create and save the logo
logo = create_modern_logo()
logo_path = os.path.join('assets', 'truck_logo.png')
logo.save(logo_path, 'PNG')

print(f"Modern logo created at: {logo_path}")
