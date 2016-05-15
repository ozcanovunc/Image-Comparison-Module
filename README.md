# IMAGE COMPARISON MODULE

- This software gets image name's and crop amount in terms of pixel from an *xml* file, and compares them using ImageMagick software  (with *compare* command) by given format and generates an *xml* file.
- Each <ResourceImage> is compared by each <GeneratedImage> belong to that block. Comparison process returns a number between 0 and 1. (1 means given two images are exactly the same) 
- After the program is done with cropping and comparing, an e-mail is sent to a predefined email address with a detailed report, and the output file attached. *(Works with gmail and hotmail only)*

**Input xml attributes**
- **Name:** Name of the image file to be compared. ```<ResourceImage>``` and ```<GeneratedImage>``` have this.
- **Crop:** Crop amount in terms of pixel. **Only** ```<ResourceImage>``` has this. ```<ResourceImage>``` and each ```<GeneratedImage>``` will be cropped by given pixel amount from top. (**Warning:** Make sure that **none** of the ```<GeneratedImage>```'s have that attribute )

**Output xml attributes**
- **Difference:** Comparison results assigned to that attribute. **Only** ```<GeneratedImage>``` has this.
- **Error:** If one of the source image does not exist, an error output's assigned into an attribute called *Error*. ```<ResourceImage>``` or ```<GeneratedImage>``` may have this.

PREREQUISITES
----------
- ImageMagick and Python 2.7.x **must be** installed on your system. You can find detailed information on installation guide below.
- This program, all image files and the input xml file **must be** in the same directory.
- In each ```<ResourceImage>``` block, ```<ResourceImage>``` and ```<GeneratedImage>```'s extensions and dimensions **must be** the same.
- Input xml file **must be** in given strict format.

INSTALLATION GUIDE
----------

**IMAGEMAGICK**

- If you are running Windows, you can go [here](http://www.imagemagick.org/script/binary-releases.php) and under *Windows Binary Release* section, download the first *.exe* file and install it.
- If you are running Unix based OS, open the command line and run the following commands in order:
```
	sudo apt-get -y update
	sudo apt-get install -y imagemagick
```
**PYTHON 2.7.x**

- If you are running Windows, you can download and install Python 2.7.x to 
your ```C:\Python27``` folder from [here](https://www.python.org/downloads/).
- If you are running Unix based OS, download *.tgz* file from [here](https://www.python.org/downloads/release/python-2710/) to your desktop, open 
your command line and run the following commands in order:
```
	cd ~/Desktop
	sudo apt-get install -y build-essential checkinstall
	sudo apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
	tar -xvf ".tgz file name"
	cd "Python-2.7.x directory name"
	./configure
	make
```
SAMPLE FILES
----------
**INPUT XML**
```
<Images>
	<ResourceImage Name="a.jpg" Crop="25">
		<GeneratedImage Name="b.jpg"/>			
		<GeneratedImage Name="c.jpg"/>
	</ResourceImage>
	<ResourceImage Name="d.jpg" Crop="50">
		<GeneratedImage Name="e.jpg"/>
	</ResourceImage>
</Images>
```
**OUTPUT XML**
```
<Images>
	<ResourceImage Name="a.jpg" Crop="25">
		<GeneratedImage Name="b.jpg" Difference="0.992813"/>			
		<GeneratedImage Name="c.jpg" Difference="0.724813"/>
	</ResourceImage>
	<ResourceImage Name="d.jpg" Crop="50">
		<GeneratedImage Name="e.jpg" Difference="1"/>
	</ResourceImage>
</Images>
```
