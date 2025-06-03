from PIL import Image, ImageDraw, ImageFont
import io

def create_card(atk, hp, x, ability_text, description_text):
    base_image = Image.open(rf"Art\Card_art\{x}_Card.png").convert("RGBA")
    stats_font = ImageFont.truetype(r"Art\Fonts\TT Rounds Neue Trial Compressed ExtraBold.ttf", size=35)
    abilities_font = ImageFont.truetype(r"Art\Fonts\TT Rounds Neue Trial Condensed Bold.ttf", size=27)
    description_font = ImageFont.truetype(r"Art\Fonts\TT Rounds Neue Trial Condensed Bold.ttf", size=8)

    draw = ImageDraw.Draw(base_image)

    hp_position = (89, 471)
    atk_text_bbox = draw.textbbox((0, 0), f"{atk}", font=stats_font)
    atk_text_width = atk_text_bbox[2] - atk_text_bbox[0]
    atk_position = (max(288 - ((len(str(atk)) - 3) * 10) + 4 - atk_text_width // 2, 200), 471)

    draw.text(atk_position, f"{atk}", font=stats_font, fill=(255, 170, 51))
    draw.text(hp_position, f"{hp}", font=stats_font, fill=(255, 77, 77))
    
    max_title_width = 370  
    title_font_size = 49
    title_text = x.replace("_", " ")
    
    while True:
        title_font = ImageFont.truetype(r"Art\Fonts\ArsenicaTrial-Extrabold.ttf", size=title_font_size)
        title_width = draw.textlength(title_text, font=title_font)
        if title_width <= max_title_width or title_font_size <= 10:  # Minimum font size guard
            break
        title_font_size -= 1

    draw.text((15, 7 + ((48 - title_font.getbbox("A")[3]) / 2)), title_text, font=title_font, fill="white")

    ability_text = f"ABILITY: {ability_text}"
    max_width = 330

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            line_width = draw.textlength(test_line, font=font)
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    wrapped_ability_text = wrap_text(ability_text, abilities_font, max_width)
    line_height = abilities_font.getbbox("A")[3]

    for i, line in enumerate(wrapped_ability_text):
        draw.text((27, 297 + i * line_height), line, font=abilities_font, fill=(231, 225, 226))
    
    wrapped_description_text = wrap_text(description_text, description_font, 110)

    for i, line in enumerate(wrapped_description_text):
        draw.text((27, 356 + i * line_height), line, font=abilities_font, fill=(200, 200, 200))

    image_binary = io.BytesIO()
    base_image.save(image_binary, 'PNG')
    image_binary.seek(0)

    return image_binary