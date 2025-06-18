import os
from PIL import Image, ImageDraw
from io import BytesIO
import discord
from utils.load_json import json_data

GACHA = json_data['GACHA']
CARD_IMAGE_UTILS = json_data['CARD_IMAGE_UTILS']


card_images_cache = {}


def find_processed_image_path(base_name):
  path = os.path.join(CARD_IMAGE_UTILS["merged_cards_folder"], base_name + ".jpg")
  if os.path.exists(path):
    return path
  return None

def find_image_path(base_name):
  for ext in CARD_IMAGE_UTILS["extensions"]:
    path = os.path.join(CARD_IMAGE_UTILS["cards_folder"], base_name + ext)
    if os.path.exists(path):
      return path
  return None


def cache_card_images():
  if not CARD_IMAGE_UTILS["enable"]:
    return


  loaded_count = 0  
  generated_count = 0  

  
  os.makedirs(CARD_IMAGE_UTILS["merged_cards_folder"], exist_ok=True)
  card_names = set(name for group in GACHA['pool'].values() for name in group)

  for name in card_names:
    safe_name = name.rstrip('.')

    processed_path = find_processed_image_path(safe_name)
    if processed_path:
      try:
        img = Image.open(processed_path).convert("RGB")
        card_images_cache[safe_name] = img
        loaded_count += 1
        continue
      except Exception as e:
        print(f"find_processed_image_path error {e}")    

    raw_path = find_image_path(safe_name)  
    if raw_path:
      try:
        raw_img = Image.open(raw_path).convert("RGBA").resize(CARD_IMAGE_UTILS["card_size"])

        if name.endswith('.'):
          rarity = "R"
        elif safe_name in GACHA['pool']["r"]:
          rarity = "R"
        elif safe_name in GACHA['pool']["sr"]:
          rarity = "SR"
        else:
          rarity = "SSR"

        processed_img = image_merging(raw_img, rarity)

        save_path = os.path.join(CARD_IMAGE_UTILS["merged_cards_folder"], safe_name + ".jpg")
        processed_img.save(save_path, format="JPEG")

        card_images_cache[safe_name] = processed_img
        generated_count += 1

      except Exception as e:
        print(f"cache_card_images error {e}")
    else:
      print(f"image not found: assets/cards/{safe_name}.png(or ..png)")

  print(f"{loaded_count} loaded, {generated_count} generated, "
    f"{len(card_images_cache)} card images completely loaded.")




def ssr_color(ratio):
  r = int(255 - (52 * ratio))
  g = int(230 - (70 * ratio))
  b = int(160 - (110 * ratio))
  return (r, g, b)

def sr_color(ratio):
  r = int(240 - (100 * ratio))
  g = int(200 - (120 * ratio))
  b = int(255 - (75 * ratio))
  return (r, g, b)

def r_color(ratio):
  r = int(200 - (100 * ratio))
  g = int(210 - (90 * ratio))
  b = int(250 - (70 * ratio))
  return (r, g, b)

def foreground_color(rarity):
  if rarity == "R":
    return r_color
  elif rarity == "SR":
    return sr_color
  else:
    return ssr_color

def image_merging(card_img, rarity):
  width, height = card_img.size
  bottom_color_height = 60 #45        
  top_color_height = 0

  if rarity == "SR":
    top_color_height = 5  
  elif rarity == "SSR":
    top_color_height = 15  

  bottom_color = Image.new('RGBA', (width, bottom_color_height), (0, 0, 0, 0))
  draw_bottom = ImageDraw.Draw(bottom_color)
  rarity_color = foreground_color(rarity)
  for y in range(bottom_color_height):
    alpha = int(255 * (y / bottom_color_height))
    r, g, b = rarity_color(y / bottom_color_height)
    draw_bottom.line([(0, y), (width, y)], fill=(r, g, b, alpha))

  top_color = None
  if top_color_height > 0:
    top_color = Image.new('RGBA', (width, top_color_height), (0, 0, 0, 0))
    draw_top = ImageDraw.Draw(top_color)
    for y in range(top_color_height):
      ratio = 1 - (y / top_color_height)  
      alpha = int(255 * ratio)
      r, g, b = rarity_color(1 - ratio)
      draw_top.line([(0, y), (width, y)], fill=(r, g, b, alpha))

  try:
    N_image_path = f"{CARD_IMAGE_UTILS['N_folder']}/{rarity.lower()}.png"
    N_image = Image.open(N_image_path).convert("RGBA").resize(CARD_IMAGE_UTILS["card_size"])
  except Exception as e:
    print(f"N_image error {e}")
    N_image = Image.new("RGBA", (128, 256), (0, 0, 0, 0)) 


  base = N_image.copy()
  

  base.paste(card_img, (0, 0), card_img)


  base.paste(bottom_color, (0, height - bottom_color_height), bottom_color)

  if top_color:
    base.paste(top_color, (0, 0), top_color)

  try:
    label_img_path = f"{CARD_IMAGE_UTILS['label_folder']}/{rarity.lower()}.png"
    label_img = Image.open(label_img_path).convert("RGBA").resize(CARD_IMAGE_UTILS["card_size"])
    base.paste(label_img, (0, 0), label_img)
  except Exception as e:
    print(f"label_img error {e}")

  return base.convert("RGB")


async def compose_cards(results, embed):

  global card_images_cache  
  global find_image_path     

  if not CARD_IMAGE_UTILS['enable']:
    return

  try:
    card_images = []
    cols = 5

    for _, img_name in results:
    
      safe_name = img_name.rstrip('.')
      path = find_image_path(safe_name)
      
      img = card_images_cache.get(safe_name)
      if img is None:
        if not path:
          img = Image.new("RGB", CARD_IMAGE_UTILS["card_size"], (255, 255, 255))
        else:
          img = Image.open(path)
          if img.size != CARD_IMAGE_UTILS["card_size"]:
            img = img.resize(CARD_IMAGE_UTILS["card_size"])
          if img.mode != "RGB":
            img = img.convert("RGB")
        card_images_cache[safe_name] = img

      card_images.append(img)

    if not card_images:
      raise ValueError("no images to combine")

    rows = (len(card_images) + cols - 1) // cols
    combined = Image.new(
      "RGB",
      (CARD_IMAGE_UTILS["card_size"][0] * cols, CARD_IMAGE_UTILS["card_size"][1] * rows),
      (255, 255, 255)
    )
    for i, img in enumerate(card_images):
      x = (i % cols) * CARD_IMAGE_UTILS["card_size"][0]
      y = (i // cols) * CARD_IMAGE_UTILS["card_size"][1]
      combined.paste(img, (x, y))

    buffer = BytesIO()
    combined.save(buffer, format="JPEG", quality=95, subsampling=0, optimize=True)
    buffer.seek(0)

    file = discord.File(fp=buffer, filename="result.jpg")
    embed.set_image(url="attachment://result.jpg")

  except Exception as e:
    print(f"compose_cards error {e}")
    file = None

  return file, embed
