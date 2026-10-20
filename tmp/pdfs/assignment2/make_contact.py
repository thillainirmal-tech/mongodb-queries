from pathlib import Path
import sys
from PIL import Image, ImageDraw

folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
pages = sorted(folder.glob("page-*.png"))
thumb_w = 390
gap = 18
label_h = 26

for sheet_no, start in enumerate(range(0, len(pages), 6), 1):
    subset = pages[start:start + 6]
    thumbs = []
    for page in subset:
        image = Image.open(page).convert("RGB")
        thumb_h = round(image.height * thumb_w / image.width)
        image = image.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        thumbs.append((page, image))

    cell_h = max(image.height for _, image in thumbs) + label_h
    sheet = Image.new("RGB", (2 * thumb_w + 3 * gap, 3 * cell_h + 4 * gap), "#d9dde2")
    draw = ImageDraw.Draw(sheet)
    for index, (page, image) in enumerate(thumbs):
        col = index % 2
        row = index // 2
        x = gap + col * (thumb_w + gap)
        y = gap + row * (cell_h + gap)
        draw.rectangle((x, y, x + thumb_w, y + cell_h), fill="white")
        draw.text((x + 8, y + 6), page.stem, fill="#16324f")
        sheet.paste(image, (x, y + label_h))
    sheet.save(folder / f"contact-{sheet_no}.png")
