import os
from PIL import Image, ImageDraw
from io import BytesIO
import discord
from utils.load_json import json_data

GACHA = json_data['GACHA']
CARD_IMAGE_UTILS = json_data['CARD_IMAGE_UTILS']

# 全域緩存
# 全域快取字典，用來儲存已載入的卡片圖片 (key: 卡片安全名稱, value: PIL Image 物件)
card_images_cache = {}

# 尋找處理後的 JPG 卡圖檔案
# 將角色名稱對應的處理後圖檔路徑（assets/processed_cards/xxx.jpg）做存在性檢查
def find_processed_image_path(base_name):
  path = os.path.join(CARD_IMAGE_UTILS["merged_cards_folder"], base_name + ".jpg")
  if os.path.exists(path):
    return path
  return None

# 找圖片路徑函式（自動嘗試副檔名與變體）
def find_image_path(base_name):
  for ext in CARD_IMAGE_UTILS["extensions"]:
    path = os.path.join(CARD_IMAGE_UTILS["cards_folder"], base_name + ext)
    if os.path.exists(path):
      return path
  return None

# 預載圖片並快取
def cache_card_images():
  if not CARD_IMAGE_UTILS["enable"]:
    return

  # 成功從處理後圖片載入的數量
  loaded_count = 0  
  # 經過處理並儲存的圖片數量   
  generated_count = 0  

  # 確保資料夾存在
  os.makedirs(CARD_IMAGE_UTILS["merged_cards_folder"], exist_ok=True)
  # 收集所有出現在 GACHA_POOL 的角色名稱
  card_names = set(name for group in GACHA['pool'].values() for name in group)

  for name in card_names:
    # 移除尾端多餘的點，避免路徑錯誤
    safe_name = name.rstrip('.')

    # 利用 find_processed_image_path 找以處理圖片實際路徑
    processed_path = find_processed_image_path(safe_name)
    if processed_path:
      try:
        img = Image.open(processed_path).convert("RGB")
        card_images_cache[safe_name] = img
        loaded_count += 1
        # 成功讀取，略過原圖處理
        continue
      except Exception as e:
        print(f"find_processed_image_path error {e}")    

    # 利用 find_image_path 找圖片實際路徑
    raw_path = find_image_path(safe_name)  
    if raw_path:
      try:
        # 使用 PIL 開啟圖片，並調整大小為 CARD_IMAGE_UTILS["card_size"]
        raw_img = Image.open(raw_path).convert("RGBA").resize(CARD_IMAGE_UTILS["card_size"])

        if name.endswith('.'):
          rarity = "R"
        elif safe_name in GACHA['pool']["r"]:
          rarity = "R"
        elif safe_name in GACHA['pool']["sr"]:
          rarity = "SR"
        else:
          rarity = "SSR"

        # 合成背景、標籤，並轉為 RGB 格式
        processed_img = image_merging(raw_img, rarity)

        save_path = os.path.join(CARD_IMAGE_UTILS["merged_cards_folder"], safe_name + ".jpg")
        # 儲存處理後圖片至磁碟（JPG 格式）
        processed_img.save(save_path, format="JPEG")

        # 同時放入記憶體快取
        card_images_cache[safe_name] = processed_img
        generated_count += 1

      except Exception as e:
        print(f"cache_card_images error {e}")
    else:
      # 若原始圖檔不存在，印出警告
      print(f"image not found: assets/cards/{safe_name}.png(or ..png)")

  # 結束訊息，顯示載入成功數量
  print(f"{loaded_count} loaded, {generated_count} generated, "
    f"{len(card_images_cache)} card images completely loaded.")




# 增加圖片底層背景，並將最終圖片轉為 JPG 並暫存在 PIL
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
    #return lambda ratio: (61, 157, 246) # 藍
  elif rarity == "SR":
    return sr_color
    #return lambda ratio: (168, 108, 247) # 紫
  else: # SSR
    return ssr_color
    #return lambda ratio: tuple(min(int(c * 1.0), 255) for c in (255, 200, 0)) # 215

def image_merging(card_img, rarity):
  width, height = card_img.size
  bottom_color_height = 60 #45        
  top_color_height = 0

  # SR 上方一點漸層
  if rarity == "SR":
    top_color_height = 5  
  # SSR 上方更多漸層
  elif rarity == "SSR":
    top_color_height = 15  

  # 建立下方漸層圖層
  bottom_color = Image.new('RGBA', (width, bottom_color_height), (0, 0, 0, 0))
  draw_bottom = ImageDraw.Draw(bottom_color)
  rarity_color = foreground_color(rarity)
  for y in range(bottom_color_height):
    alpha = int(255 * (y / bottom_color_height))
    r, g, b = rarity_color(y / bottom_color_height)
    draw_bottom.line([(0, y), (width, y)], fill=(r, g, b, alpha))

  # 建立上方漸層圖層（如果需要）
  top_color = None
  if top_color_height > 0:
    top_color = Image.new('RGBA', (width, top_color_height), (0, 0, 0, 0))
    draw_top = ImageDraw.Draw(top_color)
    for y in range(top_color_height):
      # 上方是從深到淺
      ratio = 1 - (y / top_color_height)  
      alpha = int(255 * ratio)
      r, g, b = rarity_color(1 - ratio)
      draw_top.line([(0, y), (width, y)], fill=(r, g, b, alpha))

  # 嘗試載入背景圖（N）N_image
  try:
    N_image_path = f"{CARD_IMAGE_UTILS['N_folder']}/{rarity.lower()}.png"
    N_image = Image.open(N_image_path).convert("RGBA").resize(CARD_IMAGE_UTILS["card_size"])
  except Exception as e:
    print(f"N_image error {e}")
    # 空白底圖
    N_image = Image.new("RGBA", (128, 256), (0, 0, 0, 0)) 

  # 合成：底圖 > 卡圖 > 上漸層 > 下漸層 > 標籤
  # 複製底圖，避免改到原始底圖
  base = N_image.copy()
  
  # 把卡片圖片貼到底圖左上角 (0, 0)
  # 第三個參數 card_img 是透明遮罩，確保透明部分不會蓋掉底圖
  base.paste(card_img, (0, 0), card_img)

  # 把下方漸層圖層貼到底圖的底部位置，y座標是整張圖高度減去漸層高度
  # 這樣漸層就會貼在卡片底部，並帶透明遮罩
  base.paste(bottom_color, (0, height - bottom_color_height), bottom_color)

  # 如果有上方漸層圖層，就貼到左上角，帶透明遮罩
  if top_color:
    base.paste(top_color, (0, 0), top_color)

  # 疊上 R/SR/SSR 標籤圖
  try:
    label_img_path = f"{CARD_IMAGE_UTILS['label_folder']}/{rarity.lower()}.png"
    label_img = Image.open(label_img_path).convert("RGBA").resize(CARD_IMAGE_UTILS["card_size"])
    base.paste(label_img, (0, 0), label_img)
  except Exception as e:
    print(f"label_img error {e}")

  # 轉為 RGB 以便儲存為 JPG
  return base.convert("RGB")


#多張卡圖合成 合成抽卡圖片，並設定 embed 的圖片附件
async def compose_cards(results, embed):

  # 使用全域快取
  global card_images_cache  
  # 使用全域函式
  global find_image_path     

  if not CARD_IMAGE_UTILS['enable']:
    return

  try:
    # 儲存 PIL 圖片物件
    card_images = []
    cols = 5

    for _, img_name in results:
      # 去掉可能的點號結尾
      safe_name = img_name.rstrip('.')
      # 嘗試取得圖片檔案路徑
      path = find_image_path(safe_name)
      
      # 先從快取取圖
      img = card_images_cache.get(safe_name)
      if img is None:
        if not path:
          img = Image.new("RGB", CARD_IMAGE_UTILS["card_size"], (255, 255, 255))
        else:
          # 讀取圖片並縮放成標準尺寸，轉為 RGB
          img = Image.open(path)
          if img.size != CARD_IMAGE_UTILS["card_size"]:
            img = img.resize(CARD_IMAGE_UTILS["card_size"])
          if img.mode != "RGB":
            img = img.convert("RGB")
        # 存入快取
        card_images_cache[safe_name] = img

      card_images.append(img)

    if not card_images:
      raise ValueError("no images to combine")

    # 動態計算所需行數
    rows = (len(card_images) + cols - 1) // cols
    combined = Image.new(
      "RGB",
      (CARD_IMAGE_UTILS["card_size"][0] * cols, CARD_IMAGE_UTILS["card_size"][1] * rows),
      # 白底
      (255, 255, 255)
    )

    # 根據卡片寬度計算橫縱向位置
    for i, img in enumerate(card_images):
      x = (i % cols) * CARD_IMAGE_UTILS["card_size"][0]
      y = (i // cols) * CARD_IMAGE_UTILS["card_size"][1]
      combined.paste(img, (x, y))

    # 將圖片寫入 BytesIO buffer
    buffer = BytesIO()
    #JPG品質
    combined.save(buffer, format="JPEG", quality=95, subsampling=0, optimize=True)
    buffer.seek(0)

    # 包裝為 Discord File 對象，並設定 embed 的圖片連結
    file = discord.File(fp=buffer, filename="result.jpg")
    embed.set_image(url="attachment://result.jpg")

  except Exception as e:
    print(f"compose_cards error {e}")
    # 表示失敗
    file = None

  # 回傳圖片檔案與 embed 物件
  return file, embed