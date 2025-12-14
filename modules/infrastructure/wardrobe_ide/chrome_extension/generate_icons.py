"""
Generate Chrome Extension icons for Wardrobe Recorder
"""
from PIL import Image, ImageDraw
from pathlib import Path

# Create icons directory
icons_dir = Path(__file__).parent / 'icons'
icons_dir.mkdir(exist_ok=True)

# Icon sizes needed
sizes = [16, 48, 128]

# Colors - purple gradient theme matching the widget
bg_color = (102, 126, 234)  # #667eea
circle_color = (220, 53, 69)  # Recording red #dc3545

for size in sizes:
    # Create new image with purple background
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw recording circle in center
    padding = size // 4
    circle_bbox = [padding, padding, size - padding, size - padding]
    draw.ellipse(circle_bbox, fill=circle_color)

    # Add white ring around circle (recording indicator)
    if size >= 48:
        ring_width = max(2, size // 32)
        ring_bbox = [
            padding - ring_width,
            padding - ring_width,
            size - padding + ring_width,
            size - padding + ring_width
        ]
        draw.ellipse(ring_bbox, outline='white', width=ring_width)

    # Save icon
    output_path = icons_dir / f'icon{size}.png'
    img.save(output_path, 'PNG')
    print(f'[OK] Created {output_path}')

print('\n[SUCCESS] All icons generated!')
print(f'[INFO] Icons location: {icons_dir}')
