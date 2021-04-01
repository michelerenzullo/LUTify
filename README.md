# LUTify

A very complete and simple script to resize or convert your CLUT images to CUBE format and viceversa.

**Do you like this project? Support it by donating**

- ![Paypal](https://raw.githubusercontent.com/reek/anti-adblock-killer/gh-pages/images/paypal.png) Paypal: [Donate](https://www.paypal.com/donate?hosted_button_id=XQ8QUEME5JZMN) or [paypal.me/michelerenzullo](https://paypal.me/michelerenzullo)
- ![btc](https://raw.githubusercontent.com/reek/anti-adblock-killer/gh-pages/images/bitcoin.png) Bitcoin: 1K9RF3s4aocmaRbh2Zu2FuHjrcg5BNeDxU

## FEATURES:

* Auto-detect input format
* Auto-resize not perfect square LUT size(example #33, #17...)
* Flip RGB values 
* Change size and shape of your LUT (example Spark AR LUTs to Lens Studio 1x16 LUTs)
* Generate identity CLUT
* Read all types of CLUT 
* Two type of interpolation: Tetrahedral or Nearest  
Square:  
![square](https://i.ibb.co/JcWC5Fc/Identity-HALD-square.png)  
Square one-row:  
![one-row](https://i.ibb.co/w7xVt25/Identity-HALD-square.png)  
Hald:  
![hald](https://i.ibb.co/QHPGtHG/Identity-HALD-classic.png)  


## REQUIREMENTS:
* Python 3
* Numpy
* Pillow

```Shell 
$ pip install numpy pillow
```

## USAGE:

```Shell
$ LUTify.py -h
usage: LUTify.py [-h] [--input INPUT] [--output OUTPUT]
                      [--format {hald,square}] [--identity] [--size SIZE]
                      [--method {nearest,tetrahedral}] [--rows ROWS] [--flip]
...
```
* `-i INPUT`/`-o OUTPUT` supports .CUBE, .PNG, .JPG, .TIFF 
* `-id IDENTITY` generate a CLUT identity
* `-f FORMAT` "hald" or "square", override default output:
    - if output is CUBE or "identity", default format is "hald"
    - if input is CUBE and output is image the default format is "hald"
	- if input is image and output is image default format will be automatically determinated as the opposite of the input format.
* `-s SIZE` choose your CLUT size or LUT size overriding input value.
* `-m METHOD` the method of interpolation when resizing between "tetrahedral"(default) and "nearest"
* `-r ROWS` number of rows when output is square
* `-ud FLIP` flip upside down RGB values

## TIPS:
If you would like to convert your Spark AR LUTs to Lens Studio:
```Shell
$ LUTify.py -i "SparkAR_SQUARE.png" -o "LensStudio_SQUARE.png" -s 4 -r 1 -f square --flip
```
