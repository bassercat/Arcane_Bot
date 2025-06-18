from PIL import Image, ImageDraw, ImageFont
import os
import re
import io
import discord
from utils.load_json import json_data

AFFIX_IMAGE_UTILS = json_data['AFFIX_IMAGE_UTILS']

def affix_image_utils(
  text_list: list,
  tier_list: list,
  embed: discord.Embed = None,
  background_folder = AFFIX_IMAGE_UTILS['background_folder'],
  word_font_path = AFFIX_IMAGE_UTILS['word_font_path'],
  number_font_path = AFFIX_IMAGE_UTILS['number_font_path'],
  ):

  if not AFFIX_IMAGE_UTILS['enable']:
    return

  # 位置與初始框色設定
  coordinate = AFFIX_IMAGE_UTILS['coordinate']
  fields_color = []

  # 判斷每一行的框色
  for tag in tier_list:
    fields_color.append('1' if tag == '15' else '0')
  
  img_name = ''.join(fields_color) + '.png'
  img_path = os.path.join(background_folder, img_name)
  base = Image.open(img_path).convert('RGB')

  # 建立繪圖物件
  draw = ImageDraw.Draw(base)

  # 載入字型並設定字型大小
  word_font = ImageFont.truetype(word_font_path, 16)
  number_font = ImageFont.truetype(number_font_path, 18)


  # text: text_list 中第 i 個文字
  # tag: tier_list 中第 i 個對應標籤
  for i, (text, tag) in enumerate(zip(text_list, tier_list)):
    x, y = coordinate[i]

    # 預設顏色
    munber_color = tuple(AFFIX_IMAGE_UTILS['default_color'])
    word_color = tuple(AFFIX_IMAGE_UTILS['default_color'])

    if text == '未獲得效果':
      draw.text(
        (x, y), text, font=word_font,
        fill=word_color, anchor="mm"
      )
      continue

    if tag in ['12', '13', '14']:
      munber_color = tuple(AFFIX_IMAGE_UTILS['blue_color'])
      text = re.sub(r'\([^\)]*\)', '', text)
      text = re.sub(r'^\[(.*)\]$', r'\1', text)

    if tag == '15':
      munber_color = tuple(AFFIX_IMAGE_UTILS['blue_color'])
      word_color = tuple(AFFIX_IMAGE_UTILS['white_color'])
      text = text.strip('`')

    # 解析文字
    # 找中括號詞條
    word = re.search(r'\[(.*?)\]', text)
    word = word.group(1) if word else ''

    # 找百分比數字
    number = re.search(r'(\d+\.?\d*%)', text)
    number = number.group(1) if number else ''

    # 處理格式
    if word:
      word = f'【{word}】'
    # 因字體關係零0改成歐O
    if number:
      number = number.replace('0', 'O')

    # 字與數字之間的間距寬度
    space_width = 20
    word_width = draw.textlength(word, font=word_font)
    number_width = draw.textlength(number, font=number_font)
    total_width = word_width + space_width + number_width
    x_start = 254 - total_width / 2 - 6

    # 畫 word
    draw.text(
      (x_start, y), word, font=word_font,
      fill=word_color, anchor="lm"
    )

    # 畫 number
    x_num = x_start + word_width + space_width
    draw.text(
      (x_num, y), number, font=number_font,
      fill=munber_color, anchor="lm"
    )  

  # 轉成 JPG: RGBA → RGB（否則無法存成 JPG）
  buffer = io.BytesIO()
  base.save(buffer, format='JPEG')
  buffer.seek(0)

  file = discord.File(fp=buffer, filename="result.jpg")
  embed.set_image(url="attachment://result.jpg")
  return file, embed
