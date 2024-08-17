#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
from PIL import Image, ImageDraw, ImageFont

#Configuration
OUTWIDTH = 470 #Output image width
SCALE = 2 #Internal scaling for text rendering quality
IMWIDTH = SCALE * OUTWIDTH #Temporary drawing image width
HEADERFONTSIZE = 21 * SCALE #Roughly font height in temporary image
HEADERFONTPATH = "OpenSans-Light.ttf"
BODYFONTSIZE = 20 * SCALE
BODYFONTPATH = "OpenSans-Light.ttf"
STARFILE = "star.png"

#Load star-image early so we can know its dimensions
im_star = Image.open(STARFILE)

#Text Layout - these are in *SCALE coords
padding = 10
header_x = padding
header_y = 0
star_x = padding
star_y = header_y + int(1.8 * HEADERFONTSIZE)
message_x = padding
message_y = star_y + int(SCALE * 1.2 * im_star.size[1])
message_w = IMWIDTH - 2 * padding

#Draws UNDERLINEDNAME plus regular text
def draw_header_text(draw, pos, text1, text2, font, **options):
	#New, bounding-box based way
	(tleft, ttop, tright, tbottom) = draw.textbbox(pos, text1, font=font)
	twidth = tright - tleft
	theight = tbottom - ttop
	lx, ly = tleft, HEADERFONTSIZE + 3 * SCALE
	#Old, deprecated way
	#twidth, theight = draw.textsize(text1, font=font)
	#lx, ly = pos[0], pos[1] + theight
	draw.text(pos, text1 + text2, (0,0,0), font=font, **options)
	draw.line((lx, ly, lx + twidth, ly), (0,0,0), **options, width=SCALE)

#Draws N stars starting at pos and to the right
def draw_stars(im, pos, n):
	for i in range(n):
		im.paste(im_star, pos)
		pos = (pos[0] + im_star.size[0], pos[1])

#Compute text wrapping
#From: https://stackoverflow.com/a/67203353/1125660
def get_wrapped_text(text: str, font: ImageFont.ImageFont,
                     line_length: int):
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)

headerfont = ImageFont.truetype(HEADERFONTPATH, HEADERFONTSIZE)
bodyfont = ImageFont.truetype(BODYFONTPATH, BODYFONTSIZE)

#Work out the bottom of the body text, given the location
def textBottom(pos, text, font):
	image = Image.new("RGB", (1,1), (255,255,255))
	draw = ImageDraw.Draw(image)
	(tleft, ttop, tright, tbottom) = draw.textbbox(pos, text, font=font)
	return tbottom

with open('example_reviews.json', 'r') as jfile:
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
		reviewer = item["reviewer"]
		date = item["date_reviewed"]
		stars = int(item["star_rating"])
		message = item["message"]
		order_id = item["order_id"]

		#Skip unplausibly short messages
		if(len(message) < 5):
			continue

		#wrap text by breaking on lines.
		wrapped = get_wrapped_text(message, font=bodyfont, line_length=message_w)

		#Compute image height and create image
		IMHEIGHT = textBottom((message_x, message_y), wrapped, font=bodyfont) + padding * 3
		OUTHEIGHT = int((IMHEIGHT + SCALE / 2) / SCALE)
		image = Image.new("RGB", (IMWIDTH,IMHEIGHT), (255,255,255))
		draw = ImageDraw.Draw(image)

		#Render header and body text
		draw_header_text(draw, (header_x,header_y), reviewer, " on " + date, headerfont)
		draw.text((message_x,message_y), wrapped, (0,0,0), font=bodyfont)

		#Scale down to output size
		img_resized = image.resize((OUTWIDTH, OUTHEIGHT), Image.LANCZOS)

		#Draw stars in output scale
		draw_stars(img_resized, (star_x // SCALE, star_y // SCALE), stars)

		out_filename = 'output/' + str(order_id) + '_' + reviewer + ".jpg"
		img_resized.save(out_filename, format='JPEG', subsampling=0, quality=85)
		#img_resized.show()
