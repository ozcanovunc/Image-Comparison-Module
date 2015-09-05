import os, re, subprocess, platform, time, sys, smtplib, getpass
from subprocess import Popen, PIPE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_fileInput = "ImageCompareInput.xml"
_fileOutput = "Log.xml"
_fileTemp = "ImageMagickTemp"

# Output xml tags
_attrResource = "ResourceImage"
_attrGenerated = "GeneratedImage"
_attrImage = "Images"

# Error logs to be sent by email
_logResource = ""
_logGenerated = ""

# Mail configurations
_mailServerGmail = "smtp.gmail.com"
_mailServerHotmail = "smtp-mail.outlook.com"
_mailPort = 587

_commandCompare = "compare -metric NCC \"image1\" \"image2\" ImageMagickTemp"
_commandCrop = "convert image -crop -0+AMOUNT image"

def setMailBody ():
	"""
	Sets the mail body due to resource and generated image existence and
	returns a detailed report
	"""
	regardMessage = "\n\nBest Regards,\nImageCompare"
	
	if _logResource == "" and _logGenerated == "":
		mailBody = "No errors were detected\n" + regardMessage

	if _logResource == "" and not _logGenerated == "":
		mailBody = "Following resource images do not exist:" \
		+ _logGenerated + regardMessage

	if not _logResource == "" and _logGenerated == "":
		mailBody = "Following generated images do not exist:" \
		+ _logResource + regardMessage

	if not _logResource == "" and not _logGenerated == "":
		mailBody = "Following resource images do not exist:" + _logResource + \
		"\n" + "Following generated images do not exist:" + _logGenerated + \
		regardMessage
		
	return mailBody

def sendMail (body, subject, attachment):
	"""
	Gets mail address and password from console and sends an e-mail to self
	Note that you can configure the settings under "Mail configurations"

	Returns True if the mail is successfully sent, False o/w

	Keyword arguments:
	body -- body of the mail
	subject -- subject of the mail
	attachment -- text file to be attached to the mail
	"""
	print ("Enter you credentials\n")
	credUsername = raw_input('Username: ')

	try:
		# Prepare the attachment to be sent
		file = open (attachment, "rb")
		xml = MIMEText (file.read())
		file.close ()	
		xml.add_header ('Content-Disposition', 'attachment', filename = attachment)

		message = MIMEMultipart ()
		message['Subject'] = subject
		message['From'] = credUsername
		message['To'] = credUsername
		message.attach (xml)
		message.attach (MIMEText (body, 'plain'))

		# Determine the server
		if credUsername.split("@")[1].startswith("gmail"):
			server = _mailServerGmail
		else:
			server = _mailServerHotmail

		s = smtplib.SMTP (server + ":" + str (_mailPort))
		s.ehlo ()
		s.starttls ()
		s.login (credUsername, getpass.getpass('Password: '))
		s.sendmail (credUsername, credUsername, message.as_string())
		s.quit ()
		return True

	except:
		return False

def initCropCommandForWindows ():
	"""
	Initialize the crop command for Windows platform
	"""
	global _commandCrop
	paths = subprocess.Popen ("where convert", stdin = PIPE, stdout = PIPE, \
	stderr = PIPE, shell = True).communicate ()[0].split ("\n")
	
	for path in paths:
		if "ImageMagick" in path:
			_commandCrop = "\"" + path.replace ("\r", "") + "\"" + \
			" image -crop -0+AMOUNT image"

def processCropCommand (image, cropAmount):
	"""
	Crops given image from top
	
	Keyword arguments:
	image -- image to be cropped
	cropAmount -- crop amount in terms of pixel
	"""
	newCommand = _commandCrop.replace ("image", image)
	newCommand = newCommand.replace ("AMOUNT", cropAmount.replace("\"", ""))
	
	subprocess.Popen (newCommand, stdin = PIPE, stdout = PIPE, \
	stderr = PIPE, shell = True).wait ()

def processCommand (image1, image2):
	"""
	Compares two images using ImageMagick command called "compare"
	and return a float between 0 and 1.
	
	Keyword arguments:
	image1 -- first image to be compared
	image2 -- second image to be compared
	"""
	newCommand = _commandCompare.replace ("image1", image1)
	newCommand = newCommand.replace ("image2", image2)
	
	return subprocess.Popen (newCommand, stdin = PIPE, stdout = PIPE, \
	stderr = PIPE, shell = True).communicate ()[1].replace ("\n", "")

def fileExists (file):
	"""
	Return True if "file" is an existing regular file in current directory.
	
	Keyword arguments:
	file -- file to be checked if exists
	"""
	return os.path.isfile (file)

def deleteFileIfExists (file):
	"""
	Delete "file" in current directory, if deletion is successful return True
	
	Keyword arguments:
	file -- file to be deleted if exists
	"""
	if fileExists (file):
		os.remove (file)
		return True
	else:
		return False

def cropImages():
	"""
	Reads image names and crop amounts from input xml, then crops each image
	"""
	if platform.system () == "Windows":
		initCropCommandForWindows ()
		
	with open (_fileInput) as f:
		for line in f:	

			# Resource image
			if _attrResource in line and not "</" in line:

				resourceImage = re.compile ('"[^"]*"').\
				findall (line)[0].replace ("\"", "")

				crop = re.compile ('"[^"]*"').\
				findall (line)[1].replace ("\"", "")

				processCropCommand (resourceImage, crop)

			# Generated image
			if _attrGenerated in line:

				generatedImage = re.compile ('"[^"]*"').\
				findall (line)[0].replace ("\"", "")

				processCropCommand (generatedImage, crop)

def main ():
	# If the source file does not exist, terminate
	if not fileExists (_fileInput):
		print ("Source \"" + _fileInput + "\" does not exist!")
		sys.exit ()
	
	deleteFileIfExists (_fileOutput)
	deleteFileIfExists (_fileTemp)
	
	cropImages ()

	fOut = open (_fileOutput, "w")
	fOut.write ("<" + _attrImage + ">\n")
	
	# Process each line
	with open (_fileInput) as f:
		for line in f:
		
			# Line contains resource image and its name
			if _attrResource in line and not "</" in line:

				resourceImage = re.compile ('"[^"]*"')\
				.findall (line)[0].replace ("\"", "")

				# Check resource image existence
				if fileExists (resourceImage):

					output = line.replace ("\n", "")

				else:

					output = "\t<" + _attrResource + " Name=\"" + \
					resourceImage + "\"" + " Error=\"" + resourceImage + \
					" not found!\"" + ">"	

					global _logResource
					_logResource += "\n\t" + resourceImage
					
				fOut.write ("\n" + output)

			# </> Closing
			if _attrResource in line and "</" in line:
				fOut.write ("\n" + line)
				
			# Line contains generated image and its name
			if _attrGenerated in line:

				generatedImage = re.compile ('"[^"]*"').\
				findall (line)[0].replace ("\"", "")

				# Check generated image existence

				if not fileExists (generatedImage):
					
					global _logGenerated
					_logGenerated += "\n\t" + generatedImage
					
					# Generated image does not exist but the resource image does
					if fileExists (resourceImage):

						output = "\t\t<" + _attrGenerated + " Name=\"" + \
						generatedImage + "\"" + " Error=\"" + generatedImage + \
						" not found!\"" + "/>"

					# Both of the images do not exist
					if not fileExists (resourceImage):

						output = "\t\t<" + _attrGenerated + " Name=\"" + \
						generatedImage + "\"" + " Error=\"" + generatedImage + \
						" and " + resourceImage + " not found!\"" + "/>"

				if fileExists (generatedImage):

					# Both of images exist
					if fileExists (resourceImage):

						output = "\t\t<" + _attrGenerated + " Name=\"" + \
						generatedImage + "\"" + " Difference=\"" + \
						processCommand (resourceImage, generatedImage) + "\"/>"
						
					# Generated image exists but not the resource image	
					if not fileExists (resourceImage):

						output = "\t\t<" + _attrGenerated + " Name=\"" + \
						generatedImage + "\"" + " Error=\"" + resourceImage + \
						" not found!\"" + "/>"

				fOut.write ("\n" + output)

	fOut.write ("\n</" + _attrImage + ">")
	fOut.close ()
	deleteFileIfExists (_fileTemp)	
		
	if sendMail (setMailBody(), "ImageCompare", _fileOutput) == False:
		print "Mail could not be sent"

if __name__ == "__main__":
	main ()
