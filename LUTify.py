from PIL import Image
import numpy as np, argparse, re

parser = argparse.ArgumentParser(description="Useful script to convert your HALD images to CUBE format and viceversa")

parser.add_argument("--input", "-i", help="set input image or CUBE file", type=str, default="")
parser.add_argument("--output", "-o", help="set output image or CUBE file", type=str, default="")
parser.add_argument("--format", "-f", help="output: choose type of HALD between \"hald\" and \"square\"" ,choices = ["hald","square"])
parser.add_argument("--identity", "-id", help="optional: generate an identity HALD", action="store_true")
parser.add_argument("--size", "-s", help="optional: override default output size", type=int)
parser.add_argument("--method", "-m", help="optional: method of interpolation between \"tethraedral\" and \"nearest\"", choices = ["nearest","tetrahedral"], default = "tetrahedral")
parser.add_argument("--rows", "-r", help="optional: number of rows for square format", type = int, default = 0)
parser.add_argument("--flip", "-ud", help="optional: flip upside down RGB values", action="store_true")

args = parser.parse_args()

def nearest(to_resize,size,new_size):
 resized = np.empty((new_size,new_size,new_size,3), dtype=to_resize.dtype)
 ratio = float(size - 1.0) / float(new_size - 1.0)
 for x in range(new_size):
  for y in range(new_size):
   for z in range(new_size):
    lr = sorted((0,int(x*ratio),size-1))[1]
    ur = sorted((0,lr+1,size-1))[1]
    lg = sorted((0,int(y*ratio),size-1))[1]
    ug = sorted((0,lg+1,size-1))[1]
    lb = sorted((0,int(z*ratio),size-1))[1]
    ub = sorted((0,lb+1,size-1))[1]
    r = (lr,ur)[(ur-x*ratio)<(x*ratio-lr)]
    g = (lg,ug)[(ug-y*ratio)<(y*ratio-lg)]
    b = (lb,ub)[(ub-z*ratio)<(z*ratio-lb)]
    resized[x,y,z]=to_resize[r,g,b]
 return resized

def tetrahedral(to_resize,size,new_size):
 resized = np.empty((new_size,new_size,new_size,3), dtype=to_resize.dtype)
 ratio = float(size - 1.0) / float(new_size - 1.0)
 for x in range(new_size):
  for y in range(new_size):
   for z in range(new_size):
    lr = sorted((0,int(x*ratio),size-1))[1]
    ur = sorted((0,lr+1,size-1))[1]
    lg = sorted((0,int(y*ratio),size-1))[1]
    ug = sorted((0,lg+1,size-1))[1]
    lb = sorted((0,int(z*ratio),size-1))[1]
    ub = sorted((0,lb+1,size-1))[1]
    fR=x*ratio-lr
    fG=y*ratio-lg
    fB=z*ratio-lb
    if(fG>=fB>=fR):
     resized[x,y,z]=(1-fG)*to_resize[lr,lg,lb]+(fG-fB)*to_resize[lr,ug,lb]+(fB-fR)*to_resize[lr,ug,ub]+fR*to_resize[ur,ug,ub]
    elif(fB>fR>fG):
     resized[x,y,z]=(1-fB)*to_resize[lr,lg,lb]+(fB-fR)*to_resize[lr,lg,ub]+(fR-fG)*to_resize[ur,lg,ub]+fG*to_resize[ur,ug,ub]
    elif(fB>fG>=fR):
     resized[x,y,z]=(1-fB)*to_resize[lr,lg,lb]+(fB-fG)*to_resize[lr,lg,ub]+(fG-fR)*to_resize[lr,ug,ub]+fR*to_resize[ur,ug,ub]
    elif(fR>=fG>fB):
     resized[x,y,z]=(1-fR)*to_resize[lr,lg,lb]+(fR-fG)*to_resize[ur,lg,lb]+(fG-fB)*to_resize[ur,ug,lb]+fB*to_resize[ur,ug,ub]
    elif(fG>fR>=fB):
     resized[x,y,z]=(1-fG)*to_resize[lr,lg,lb]+(fG-fR)*to_resize[lr,ug,lb]+(fR-fB)*to_resize[ur,ug,lb]+fB*to_resize[ur,ug,ub]
    elif(fR>=fB>=fG):
     resized[x,y,z]=(1-fR)*to_resize[lr,lg,lb]+(fR-fB)*to_resize[ur,lg,lb]+(fB-fG)*to_resize[ur,lg,ub]+fG*to_resize[ur,ug,ub]  
 return resized


def array_resize(array, size, new_size): 
 if len(array.shape) != 4:
  array = array.reshape(size,size,size,3)  
 return (nearest(array,size,new_size),tetrahedral(array,size,new_size))[args.method=="tetrahedral"]

def wrapper(standard, array, size):
 if standard == "hald":
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
 standard = (args.format, "hald")[not args.format]
 Image.fromarray(wrapper(standard, identity(size), size)).save("Identity_" + standard + ".png")


if args.input.lower().endswith((".cube",".png",".jpg",".jpeg",".tiff")) and args.output.lower().endswith((".cube",".png",".jpg",".jpeg",".tiff")):    
 try:
  title = re.search("[^\\\/]+(?=\.[\w]+$)",args.input)[0]
  if args.input.lower().endswith(".cube"):
   file = open(args.input,'r').read()
   o_array = np.array([i.lower().replace(',', '').split() for i in re.findall("\n[+-]?[0-9]*[.]?[0-9]+\s[+-]?[0-9]*[.]?[0-9]+\s[+-]?[0-9]*[.]?[0-9]+",file)],dtype=float).reshape(-1)
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
    guess_format = "hald"
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
    standard = "hald"
    to_resize = not(int(lutSize**.5)**2==lutSize or (int(lutSize**.5) +1)**2==lutSize)
   else:
    standard = ("square","hald")[guess_format=="square"]

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
   o_filename = re.search("[^\/|\\\]+$",args.output)[0]
   Image.fromarray(wrapper(standard,o_array,size)).save(args.output[:-len(o_filename)] + standard + "_" + o_filename, quality=100)
   
 except FileNotFoundError:
  print("Please check input path or output path")
