"""Return num_rows*num_cols png exports. All exports are RGB modifications of image2, based on specifications derived from image1. Target RGBs determined from the center pixel of each image1 tile specified by num_rows, num_cols."""

import PIL as pil
from PIL import Image
import math

# enable variable definition from command line
import sys

image1_filepath = sys.argv[1]
image2_filepath = sys.argv[2]
export_filepath = sys.argv[3]
num_rows = int(sys.argv[4])
num_cols = int(sys.argv[5])


# target RGBs from image1
pic1 = pil.Image.open(image1_filepath).convert('RGB')
width1, height1 = pic1.size

px_per_col = math.ceil(width1/num_cols)
px_per_row = math.ceil(height1/num_rows)

chunk_it_up_cols = [(i, i+px_per_col) for i in range(0, width1, px_per_col)]
chunk_it_up_cols[-1] = (chunk_it_up_cols[-1][0], width1-1)
chunk_it_up_rows = [(i, i+px_per_row) for i in range(0, height1, px_per_row)]
chunk_it_up_rows[-1] = (chunk_it_up_rows[-1][0], height1-1)

col_centers = [(i[0]+i[1])//2 for i in chunk_it_up_cols]
row_centers = [(i[0]+i[1])//2 for i in chunk_it_up_rows]

center_px_coords = [(x,y) for x in col_centers for y in row_centers]

p1_centerpx_rgbs = [list(pic1.getpixel(i)) for i in center_px_coords]


# overall average RGB of image2
pic2 = pil.Image.open(image2_filepath).convert('RGB')
width2, height2 = pic2.size
total_rgb = [0, 0, 0]

for x in range(width2):
    for y in range(height2):
        for i in range(3): #rgb channels
            total_rgb[i] += pic2.getpixel((x,y))[i]

Ri, Gi, Bi = [int(i / (height2*width2)) for i in total_rgb] #initial R,G,B for image2

# adapt image2 so new average RGB equal to that of each image1 tile
col_counter = 1
row_counter = 1 #for export filenames

for i in p1_centerpx_rgbs:
    Rf, Gf, Bf = i 
    Rmod, Gmod, Bmod = Rf-Ri, Gf-Gi, Bf-Bi

    pic2 = pil.Image.open(image2_filepath).convert('RGB')
    p2_pixelmap = pic2.load()
    width2, height2 = pic2.size

    for x in range(width2):
        for y in range(height2):
            p2_pixelmap[x,y] = (p2_pixelmap[x,y][0] + Rmod, p2_pixelmap[x,y][1] + Gmod, p2_pixelmap[x,y][2] + Bmod)

    pic2.save(f'{export_filepath}/col{col_counter}row{row_counter}.png')
    row_counter += 1
    if (row_counter-1) % num_rows == 0:
        row_counter = 1
        col_counter += 1

print(f'All pau. There are {num_rows*num_cols} new images in your output directory')