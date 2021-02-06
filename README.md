# LUTify

A very complete and simple script to resize or convert your HALD images to CUBE format and viceversa.

**Do you like this project? Support it by donating**

- ![Paypal](https://raw.githubusercontent.com/reek/anti-adblock-killer/gh-pages/images/paypal.png) Paypal: [Donate](https://www.paypal.com/donate?hosted_button_id=XQ8QUEME5JZMN) or [paypal.me/michelerenzullo](https://paypal.me/michelerenzullo)
- ![btc](https://raw.githubusercontent.com/reek/anti-adblock-killer/gh-pages/images/bitcoin.png) Bitcoin: 1K9RF3s4aocmaRbh2Zu2FuHjrcg5BNeDxU

## FEATURES:

* Auto-detect input format
* Auto-resize not perfect square LUT size(example #33, #17...)
* Flip RGB values 
* Change size and shape of your LUT (example Spark AR LUTs to Lens Studio 1x16 LUTs)
* Generate identity HALD
* Read all types of HALD  
Square:  
![square](https://i.ibb.co/JcWC5Fc/Identity-HALD-square.png)  
Square one-row:  
![one-row](https://i.ibb.co/w7xVt25/Identity-HALD-square.png)  
Classic:  
![classic](https://i.ibb.co/QHPGtHG/Identity-HALD-classic.png)  


## REQUIREMENTS:
* Python 3
* Numpy
* Pillow
* Scikit-image only if you need to resize

```Shell 
$ pip install numpy scikit-image pillow
```

## USAGE:

```Shell
$ LUTify.py -h
usage: LUTify.py [-h] [--input INPUT] [--output OUTPUT]
                      [--format {classic,square}] [--identity] [--size SIZE]
                      [--quality {0,1,2,3,4,5}] [--rows ROWS] [--flip]
...
```
* `-i INPUT`/`-o OUTPUT` supports .CUBE, .PNG, .JPG, .TIFF 
* `-id IDENTITY` generate an HALD identity
* `-f FORMAT` "classic" or "square", override default output:
    - if output is CUBE or "identity", default format is "classic"
    - if input is CUBE and output is image the default format is "classic"
	- if input is image and output is image default format will be automatically determinated as the opposite of the input format.
* `-s SIZE` choose your HALD size or LUT size overriding input value.
* `-q QUALITY` the order of spline interpolation when resizing from 0 to 5
* `-r ROWS` number of rows when output is square HALD
* `-ud FLIP` flip upside down RGB values

## TIPS:
If you would like to convert your Spark AR LUTs to Lens Studio:
```Shell
$ LUTify.py -i "SparkAR_HALD.png" -o "LensStudio_HALD.png" -s 4 -r 1 -f square --flip
```

## TODO LIST:
- add support for .xmp by Adobe COMING SOON!!
- avoid scikit-image, and write manually spline interpolation function
- add support for .3dl
- cpp (SOON)
- possible web-version