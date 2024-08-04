#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
from PIL import Image, ImageDraw, ImageFont

#Configuration
OUTWIDTH = 470 #Output image width
OUTHEIGHT = 200 #Output image height
SCALE = 2 #Internal scaling for text rendering quality
IMWIDTH = SCALE * OUTWIDTH #Temporary drawing image width
IMHEIGHT = SCALE * OUTHEIGHT #...height
HEADERFONTSIZE = 35 * SCALE #Roughly font height in temporary image
HEADERFONTPATH = "/usr/share/fonts/truetype/open-sans/OpenSans-Light.ttf"
BODYFONTSIZE = 20 * SCALE
BODYFONTPATH = "/usr/share/fonts/truetype/open-sans/OpenSans-Light.ttf"
STARFILE = "star.png"

#Load star-image early so we can know its dimensions
im_star = Image.open(STARFILE)

#Text Layout
header_x = 10
header_y = 0
star_x = header_x
star_y = header_y + int(1.8 * HEADERFONTSIZE)
message_x = star_x
message_y = star_y + int(SCALE * 1.2 * im_star.size[1])

#Draws UNDERLINEDNAME plus regular text
def draw_header_text(draw, pos, text1, text2, font, **options):
	print(text1 + text2)
	twidth, theight = draw.textsize(text1, font=font)
	lx, ly = pos[0], pos[1] + theight
	draw.text(pos, text1 + text2, (0,0,0), font=font, **options)
	draw.line((lx, ly, lx + twidth, ly), (0,0,0), **options, width=SCALE)

#Draws N stars starting at pos and to the right
def draw_stars(im, pos, n):
	for i in range(n):
		im.paste(im_star, pos)
		pos = (pos[0] + im_star.size[0], pos[1])

with open('reviews.json', 'r') as jfile:
	data = json.load(jfile)

	fieldnames = set()
	for item in data:
		fieldnames = fieldnames.union(item.keys())

	with open('output/temp.csv', 'w', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		writer.writeheader()
		for item in data:
			writer.writerow(item)

	for item in data:
		print(item)
		reviewer = item["reviewer"]
		date = item["date_reviewed"]
		stars = int(item["star_rating"])
		message = item["message"]

		#Create an image larger than needed for text rendering
		image = Image.new("RGB", (IMWIDTH,IMHEIGHT), (255,255,255))
		draw = ImageDraw.Draw(image)
		headerfont = ImageFont.truetype(HEADERFONTPATH, HEADERFONTSIZE)
		bodyfont = ImageFont.truetype(BODYFONTPATH, BODYFONTSIZE)

		#Render out text
		draw_header_text(draw, (header_x,header_y), reviewer, " on " + date, headerfont)
		draw.text((message_x,message_y), message, (0,0,0), font=bodyfont)

		#Scale down to output size
		img_resized = image.resize((OUTWIDTH, OUTHEIGHT), Image.LANCZOS)

		#Draw stars in output scale
		draw_stars(img_resized, (star_x // SCALE, star_y // SCALE), stars)

		img_resized.save('output/' + reviewer + ".jpg", format='JPEG', subsampling=0, quality=85)
		img_resized.show()
