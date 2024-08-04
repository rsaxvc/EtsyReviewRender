import csv
import json
from PIL import Image, ImageDraw, ImageFont

#Configuration
OUTWIDTH = 200 #Output image width
OUTHEIGHT = 50 #Output image height
IMWIDTH = 3 * OUTWIDTH #Temporary drawing image width
IMHEIGHT = 3 * OUTHEIGHT #...height
FONTSIZE = 50 #Roughly font height in temporary image
FONTPATH = "/usr/share/fonts/truetype/open-sans/OpenSans-Light.ttf"

with open('input.json', 'r') as jfile:
	data = json.load(jfile)

	fieldnames = set()
	for item in data:
		fieldnames = fieldnames.union(item.keys())
	print(fieldnames)

	with open('output/temp.csv', 'w', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		writer.writeheader()
		for item in data:
			writer.writerow(item)

	for item in data:
		print(item)
		reviewer = item["reviewer"]
		date = item["date_reviewed"]
		stars = item["star_rating"]
		message = item["message"]

		image = Image.new("RGB", (IMWIDTH,IMHEIGHT), (255,255,255))
		draw = ImageDraw.Draw(image)
		font = ImageFont.truetype(FONTPATH, FONTSIZE)
		draw.text((10, 0), reviewer, (0,0,0), font=font)
		draw.text((10, FONTSIZE), message, (0,0,0), font=font)
		img_resized = image.resize((OUTWIDTH, OUTHEIGHT), Image.LANCZOS)
		img_resized.save('output/' + reviewer + ".jpg", format='JPEG', subsampling=0, quality=95)
		img_resized.show()
