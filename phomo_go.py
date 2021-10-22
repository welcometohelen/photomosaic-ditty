"""Return num_rows*num_cols png exports. All exports are RGB modifications of image2, based on specifications derived from image1. Target RGBs determined from the center pixel of each image1 tile specified by num_rows, num_cols."""

import PIL as pil
from PIL import Image
import time

#determine runtime
t_start = time.time()
# enable variable definition from command line
import sys
image1_filepath = sys.argv[1]
image2_filepath = sys.argv[2]
export_filepath = sys.argv[3]
num_rows = int(sys.argv[4])
num_cols = int(sys.argv[5])
sat_thresh = float(sys.argv[6])

# target RGBs from image1
pic1 = pil.Image.open(image1_filepath).convert('RGB')
width1, height1 = pic1.size

def variable_steps(max_pixels, row_or_col):
    px_per_dim = max_pixels/row_or_col #not rounded
    tups = []
    start = 0
    end = start + px_per_dim #not rounded
    
    for i in range(0,max_pixels+1):
        tups.append( ( int(round(start,0)), int(round(end,0)) ) ) #round nearest int here
        start = end
        end = start + px_per_dim

        if tups[-1][1] >= max_pixels:
            break
    
    return tups


chunk_it_up_cols = variable_steps(width1, num_cols)
chunk_it_up_rows = variable_steps(height1, num_rows)

col_centers = [int(round((i[0]+i[1])/2,0)) for i in chunk_it_up_cols]
row_centers = [int(round((i[0]+i[1])/2,0)) for i in chunk_it_up_rows]

center_px_coords = [(x,y) for x in col_centers for y in row_centers]

p1_centerpx_rgbs = [list(pic1.getpixel(i)) for i in center_px_coords]


# overall average RGB, defining for reuse in iterative image generation
def total_avg(img_path=False, local_object=False):
    if local_object:
        width, height = local_object.size
        img = local_object
        
    elif img_path:
        img = pil.Image.open(img_path).convert('RGB')
        width, height = img.size
    
    total_rgb = [0, 0, 0]
    
    for x in range(width):
        for y in range(height):
            for i in range(3): #rgb channels
                total_rgb[i] += img.getpixel((x,y))[i]
                
    return [i / (height*width) for i in total_rgb]


# adapt image2 so new average RGB equal to that of each image1 tile
total = 1
col_counter = 1
row_counter = 1 #for export filenames

for i in p1_centerpx_rgbs:
    Rf, Gf, Bf = i 
    Ri, Gi, Bi = total_avg(img_path = image2_filepath, local_object = False)
    Rmod, Gmod, Bmod = Rf-Ri, Gf-Gi, Bf-Bi

    pic2 = pil.Image.open(image2_filepath).convert('RGB')
    p2_pixelmap = pic2.load()
    width2, height2 = pic2.size

    while (abs(Rmod) > sat_thresh) or (abs(Gmod) > sat_thresh) or (abs(Bmod) > sat_thresh):

        for x in range(width2):
            for y in range(height2):
                p2_pixelmap[x,y] = (int(round(p2_pixelmap[x,y][0] + Rmod,0)),
                int(round(p2_pixelmap[x,y][1] + Gmod,0)),
                int(round(p2_pixelmap[x,y][2] + Bmod,0)) )

        Ri2, Gi2, Bi2 = total_avg(img_path = False, local_object = pic2)
        Rmod, Gmod, Bmod = Rf-Ri2, Gf-Gi2, Bf-Bi2

    pic2.save(f'{export_filepath}/{total}_col{col_counter}row{row_counter}.png')
    total += 1
    row_counter += 1
    if (row_counter-1) % num_rows == 0:
        row_counter = 1
        col_counter += 1

print(f'Pau. There are {num_rows*num_cols} new images in your output directory')
print('Execution time: ', time.strftime('%H:%M:%S', time.gmtime((time.time() - t_start))))