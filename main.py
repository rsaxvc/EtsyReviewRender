#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
import json
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument("--width", help="pixel-width of rendered images",
                    type=int, default=470)
parser.add_argument("--headerFontSize", help="pixel-height of header-font",
                    type=int, default=21)
parser.add_argument("--headerFontTtf", help="path to TTF file for header-font",
                    type=str, default="OpenSans-Light.ttf")
parser.add_argument("--bodyFontSize", help="pixel-height of body-font",
                    type=int, default=20)
parser.add_argument("--bodyFontTtf", help="path to TTF file for body-font",
                    type=str, default="OpenSans-Light.ttf")
parser.add_argument("--minMsgLen", help="minimum message length to keep",
                    type=int, default=5)
parser.add_argument("--starFile", help="path to a star image",
                    type=str, default="star.png")
parser.add_argument("inputFile", help="input JSON file, exported from Etsy",
                    type=str, default="example_reviews.json")
args = parser.parse_args()


#Configuration
SCALE = 2 #Internal scaling for text rendering quality
IMWIDTH = SCALE * args.width #Temporary drawing image width
HEADERFONTSIZE = args.headerFontSize * SCALE #Roughly font height in temporary image
BODYFONTSIZE = args.bodyFontSize * SCALE

#Load star-image early so we can know its dimensions
im_star = Image.open(args.starFile)

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

headerfont = ImageFont.truetype(args.headerFontTtf, HEADERFONTSIZE)
bodyfont = ImageFont.truetype(args.bodyFontTtf, BODYFONTSIZE)

#Work out the bottom of the body text, given the location
def textBottom(pos, text, font):
	image = Image.new("RGB", (1,1), (255,255,255))
	draw = ImageDraw.Draw(image)
	(tleft, ttop, tright, tbottom) = draw.textbbox(pos, text, font=font)
	return tbottom

with open(args.inputFile, 'r') as jfile:
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
		if(len(message) < args.minMsgLen):
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
		img_resized = image.resize((args.width, OUTHEIGHT), Image.LANCZOS)

		#Draw stars in output scale
		draw_stars(img_resized, ((star_x + SCALE//2)// SCALE, (star_y + SCALE//2)// SCALE), stars)

		out_filename = 'output/' + str(order_id) + '_' + reviewer + ".jpg"
		img_resized.save(out_filename, format='JPEG', subsampling=0, quality=85)
		#img_resized.show()
