from PIL import Image
import numpy as np, argparse, re

parser = argparse.ArgumentParser(description="Useful script to convert your HALD images to CUBE format and viceversa")

parser.add_argument("--input", "-i", help="set input image or CUBE file", type=str, default="")
parser.add_argument("--output", "-o", help="set output image or CUBE file", type=str, default="")
parser.add_argument("--format", "-f", help="output: choose type of HALD between \"classic\" and \"square\"" ,choices = ["classic","square"])
parser.add_argument("--identity", "-id", help="optional: generate an identity HALD", action="store_true")
parser.add_argument("--size", "-s", help="optional: override default output size", type=int)
parser.add_argument("--quality", "-q", help="optional: quality for resize from 0 to 5", choices = range(0,6), type = int, default = 3)
parser.add_argument("--rows", "-r", help="optional: number of rows for square format", type = int, default = 0)
parser.add_argument("--flip", "-ud", help="optional: flip upside down RGB values", action="store_true")

args = parser.parse_args()

def need_resize(n):
 c = int(n**.5)  
 return not (c**2==n or (c+1)**2==n )

def array_resize(array, size, new_size):
 from skimage.transform import resize
 if len(array.shape) != 4:
  array = array.reshape(size,size,size,3)  
 return resize(array,(new_size,new_size,new_size,3),order=args.quality)

def wrapper(standard, array, size):
 if standard == "classic":
  array = array.reshape(size**3, size**3, 3)
 else:
  rows = size
  if 0 < args.rows < size and size%args.rows==0:
   rows = args.rows
  array = array.reshape((rows,int(size**2/rows+.5),size**2,size**2, 3))
  array = np.concatenate([np.concatenate(array[row], axis=1) for row in range(rows)])
 return (array,np.flipud(array))[args.flip]

def identity(size):
 return np.mgrid[ 0 : 255 : size**2*1j, 0 : 255 : size**2*1j, 0 : 255 : size**2*1j ].astype(np.uint8).transpose() #transpose because bgr->rgb

def square_unwrap(array,size):
 lutSize=size**2
 LUT = np.empty((lutSize,lutSize,lutSize,3), dtype=np.uint8)
 cubeIndex = 0        
 for y in range(array.shape[0]):
  for x in range(array.shape[1]):
   iR = cubeIndex % lutSize
   iG = y % lutSize
   iB = int(x/lutSize)+(int(y/lutSize)*int(array.shape[0]/lutSize))
   LUT[iB,iG,iR]=array[y,x]
   cubeIndex+=1
 return LUT

if args.identity:
 size = (args.size, 8)[not args.size]
 standard = (args.format, "classic")[not args.format]
 Image.fromarray(wrapper(standard, identity(size), size)).save("Identity_HALD_" + standard + ".png")


if args.input.lower().endswith((".cube",".png",".jpg",".jpeg",".tiff")) and args.output.lower().endswith((".cube",".png",".jpg",".jpeg",".tiff")):    
 try:
  title = re.search("[^\\\/]+(?=\.[\w]+$)",args.input)[0]
  if args.input.lower().endswith(".cube"):
   file = open(args.input,'r').read()
   o_array = np.array(re.findall("\d+\.\d\d+",file),dtype=float)
   lutSize = int(re.search("_SIZE.*?(\d+)",file).group(1))
   input_title = re.search("TITLE.?[\"'](.*?)[\"']",file)
   del file
   if input_title:
    title = input_title.group(1)
   size = int((len(o_array)/3)**(1/6)+.5)
  else:
   o_array = np.array(Image.open(args.input,'r').convert('RGB'), dtype=np.uint8)
   size = int((o_array.shape[0]*o_array.shape[1])**(1/6)+.5)
   lutSize = size**2
   if o_array[0,0,1] > o_array[size-1,0,1]:
    args.flip = (True,False)[args.flip]
    o_array = np.flipud(o_array)
   if o_array[0,0,1] < o_array[size-1,0,1] > o_array[size,0,1]:   
    guess_format = "classic"
   else:
    guess_format = "square"
    o_array = square_unwrap(o_array,size)  
   
     
  if args.output.lower().endswith(".cube"):   
   if args.size:
    if 3 < args.size != lutSize:
     o_array = array_resize(o_array,lutSize,args.size)
     lutSize = args.size     
   if o_array.dtype == "uint8":
    o_array = o_array/255
   np.savetxt(args.output,o_array.reshape((-1,3)), fmt="%.9f", header="TITLE \"" + title + "\"\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\nLUT_3D_SIZE " + str(lutSize), comments="")
   
  else:      
   to_resize = None
   if args.input.lower().endswith(".cube"):         
    standard = "classic"
    to_resize = need_resize(lutSize)
   else:
    standard = ("square","classic")[guess_format=="square"]

   if args.format:
    standard = args.format                             
    
   if args.size or to_resize:
    if args.size and 1 < args.size != size:                          
     size = args.size
     o_array = array_resize(o_array,lutSize,size**2)
    elif to_resize:
     o_array = array_resize(o_array,lutSize,size**2)
    
   if o_array.dtype == "float64":
    o_array = (o_array*255+.5).astype(np.uint8)
   Image.fromarray(wrapper(standard,o_array,size)).save(standard + "_" + args.output, quality=100)
   
 except FileNotFoundError:
  print("Input error")
  