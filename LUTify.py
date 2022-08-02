from PIL import Image
import numpy as np, argparse, re

parser = argparse.ArgumentParser(description="Useful script to resize, combine luts, or convert your HALD images to CUBE format and viceversa")

parser.add_argument("--input", "-i", help="set input image or CUBE file", type=str, default="")
parser.add_argument("--combine", "-c", help="set 2nd lut to combine with input", type=str, default="")
parser.add_argument("--mixer", "-x", help="optional: mix amount from lut1(0) to lut2(100)", type=int, default=50)
parser.add_argument("--preserve", "-p", help="optional: preserve max size when combining luts", action="store_true")
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
 
def combine(lut1, lut2, size, mixer):
 alpha = ((sorted((0.0,mixer/100.0, 1.0))[1] - 0.5) * 2)
 
 #blend lut2 with identity
 if (alpha < 0):
  for x in range(size):
   for y in range(size):
    for z in range(size):
     lut2[x,y,z][0] = (1 + alpha) * lut2[x,y,z][0] - alpha * z / (size - 1.0)
     lut2[x,y,z][1] = (1 + alpha) * lut2[x,y,z][1] - alpha * y / (size - 1.0)
     lut2[x,y,z][2] = (1 + alpha) * lut2[x,y,z][2] - alpha * x / (size - 1.0)
                
 for x in range(size):
  for y in range(size):
   for z in range(size):
    #blend lut1 with identity
    if (alpha > 0):
     lut1[x,y,z][0] = (1 - alpha) * lut1[x,y,z][0] + alpha * z / (size - 1.0)
     lut1[x,y,z][1] = (1 - alpha) * lut1[x,y,z][1] + alpha * y / (size - 1.0)
     lut1[x,y,z][2] = (1 - alpha) * lut1[x,y,z][2] + alpha * x / (size - 1.0)
   
    lr = sorted((0,int(lut1[x,y,z][2]*(size-1)), size-1))[1]
    ur = sorted((0,lr + 1, size-1))[1]
    lg = sorted((0,int(lut1[x,y,z][1]*(size-1)), size-1))[1]
    ug = sorted((0,lg + 1, size-1))[1]
    lb = sorted((0,int(lut1[x,y,z][0]*(size-1)), size-1))[1]
    ub = sorted((0,lb + 1, size-1))[1]
    fR=lut1[x,y,z][2]*(size-1)-lr
    fG=lut1[x,y,z][1]*(size-1)-lg
    fB=lut1[x,y,z][0]*(size-1)-lb
    if(fG>=fB>=fR):
     lut1[x,y,z]=(1-fG)*lut2[lr,lg,lb]+(fG-fB)*lut2[lr,ug,lb]+(fB-fR)*lut2[lr,ug,ub]+fR*lut2[ur,ug,ub]
    elif(fB>fR>fG):
     lut1[x,y,z]=(1-fB)*lut2[lr,lg,lb]+(fB-fR)*lut2[lr,lg,ub]+(fR-fG)*lut2[ur,lg,ub]+fG*lut2[ur,ug,ub]
    elif(fB>fG>=fR):
     lut1[x,y,z]=(1-fB)*lut2[lr,lg,lb]+(fB-fG)*lut2[lr,lg,ub]+(fG-fR)*lut2[lr,ug,ub]+fR*lut2[ur,ug,ub]
    elif(fR>=fG>fB):
     lut1[x,y,z]=(1-fR)*lut2[lr,lg,lb]+(fR-fG)*lut2[ur,lg,lb]+(fG-fB)*lut2[ur,ug,lb]+fB*lut2[ur,ug,ub]
    elif(fG>fR>=fB):
     lut1[x,y,z]=(1-fG)*lut2[lr,lg,lb]+(fG-fR)*lut2[lr,ug,lb]+(fR-fB)*lut2[ur,ug,lb]+fB*lut2[ur,ug,ub]
    elif(fR>=fB>=fG):
     lut1[x,y,z]=(1-fR)*lut2[lr,lg,lb]+(fR-fB)*lut2[ur,lg,lb]+(fB-fG)*lut2[ur,lg,ub]+fG*lut2[ur,ug,ub]  
 return lut1

def luts_combine(lut1, lut2, size, mixer):
 if len(lut1.shape) != 4:
  lut1 = lut1.reshape(size,size,size,3)
 if len(lut2.shape) != 4:
  lut2 = lut2.reshape(size,size,size,3) 
 if lut1.dtype == "uint8":
  lut1 = lut1/255
 if lut2.dtype == "uint8":
  lut2 = lut2/255
 combine(lut1,lut2,size,mixer)
 
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
  
  if args.combine.lower().endswith((".cube",".png",".jpg",".jpeg",".tiff")):
   title2 = re.search("[^\\\/]+(?=\.[\w]+$)",args.combine)[0]
   if args.combine.lower().endswith(".cube"):
    file = open(args.combine,'r').read()
    o_array2 = np.array([i.lower().replace(',', '').split() for i in re.findall("\n[+-]?[0-9]*[.]?[0-9]+\s[+-]?[0-9]*[.]?[0-9]+\s[+-]?[0-9]*[.]?[0-9]+",file)],dtype=float).reshape(-1)
    lutSize2 = int(re.search("_SIZE.*?(\d+)",file).group(1))
    input_title2 = re.search("TITLE.?[\"'](.*?)[\"']",file)
    del file
    if input_title2:
     title2 = input_title2.group(1)
    size2 = int((len(o_array2)/3)**(1/6)+.5)
   else:
    o_array2 = np.array(Image.open(args.combine,'r').convert('RGB'), dtype=np.uint8)
    size2 = int((o_array2.shape[0]*o_array2.shape[1])**(1/6)+.5)
    lutSize2 = size2**2
    if o_array2[0,0,1] > o_array2[size-1,0,1]:
     o_array2 = np.flipud(o_array2)
    if not o_array2[0,0,1] < o_array2[size-1,0,1] > o_array2[size,0,1]:   
     o_array2 = square_unwrap(o_array2,size2)
   if lutSize is not lutSize2:
    if (bool(lutSize < lutSize2 and args.preserve) ^ bool(lutSize > lutSize2 and not args.preserve)):
     o_array = array_resize(o_array, lutSize, lutSize2)
     lutSize = lutSize2
     size = size2
    else:
     o_array2 = array_resize(o_array2, lutSize2, lutSize)
   luts_combine(o_array, o_array2, lutSize, args.mixer)
   title = "LUTs combined " + title + " and " + title2
     
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
  print("Please check paths")
