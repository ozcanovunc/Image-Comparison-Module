	@echo off

	setlocal enabledelayedexpansion

	rem Mail configurations
	set "_mailSubject=ImageCompare" 
	set "_mailServerGmail=smtp.gmail.com"
	set "_mailServerHotmail=smtp-mail.outlook.com"
	set "_mailPort=587"

	rem Error logs to be sent by email
	set "_logResource="
	set "_logGenerated="

	set "_fileOutput=Log.xml"
	set "_fileInput=ImageCompareInput.xml"
	set "_fileTemp=ImageMagickTemp"
	set newLine=^


	rem WARNING! Do not delete empty lines up ahead!
	
	rem exit if source xml does not exist
	if not exist %_fileInput% (
		echo Source xml %_fileInput% does not exist!
		pause
		exit /b
	)

	rem Changing the user preference for the Windows PowerShell execution policy
	set "policyCommand=& {Start-Process PowerShell -WindowStyle Hidden "
	set "policyCommand=!policyCommand!-ArgumentList 'Set-ExecutionPolicy "
	set "policyCommand=!policyCommand!Restricted -Force' -Verb RunAs}"
	PowerShell -NoProfile -ExecutionPolicy Bypass -Command "!policyCommand!"

	rem Delete pre generated files by this program if there is any 	
	if exist %_fileOutput% del "%_fileOutput%"	
	if exist %_fileTemp% del "%_fileTemp%"	

	rem Generate xml output
	set "output=<Images>"
	echo !output! >> "%_fileOutput%"

	rem Split xml file into lines
	for /f "tokens=* skip=1" %%a in (%_fileInput%) do (

		set "currentLine=%%a"
		
		rem Replace '"' with '+' in order to parse the line
		set "currentLine=!currentLine:"=+!"
		
		rem "keep track of indentation
		set /a counter=0
		<nul set /p flag=0 >nul
		
		rem c = current picture name
		for /f "delims=+ tokens=2" %%c in ("!currentLine!") do (

			rem Set pixel size to be removed from each image
			for /f "delims=+ tokens=4" %%d in ("!currentLine!") do (
				set "pixelsToDelete=%%d"
			)

			rem Determine if current image is a resource image or not
			set "prefix=!currentLine:~1,3!"
					
			rem Current image is a resource image
			if "!prefix!"=="Res" ( 

				rem Flags to determine when to print </ResourceImage>
				set /a flag=flag+1
				set /a counter=counter+1

				rem Get resource image name
				set "resPic=%%c"
				
				rem Crop the image
				convert !resPic! -crop -0+!pixelsToDelete! !resPic!

				rem Generate xml output
				if not !flag!==1 (
					if !counter!==1 ( 
						set "output=    </ResourceImage>"
						echo !output! >> "%_fileOutput%"
					)
				)

				set "output=    <ResourceImage Name="!resPic!" "
				set "output=!output!Crop="!pixelsToDelete!""
				set "output2=>"

				rem Check if resource image exists or not
				if not exist %%c (
					set "outputError=Error="%%c does not exist""
					echo !output! !outputError!!output2! >> "%_fileOutput%"
					set "_logResource=!_logResource!!newLine!    %%c"

				) else (
					echo !output!!output2! >> "%_fileOutput%"
				)
				
			rem Current image is a generated image
			) else (

				rem Generate xml output
				set "output=        <GeneratedImage Name="%%c^" Difference=^""
				set "output2="/^>"
			
				rem Crop the image
				convert %%c -crop -0+!pixelsToDelete! %%c

				rem Calculate difference between resource and generated images
				for /f "delims=" %%i in ('compare -metric NCC !resPic! %%c^
				 "%_fileTemp%"  2^>^&1 1^>nul ') do ( 
					set "number=%%i" 
				)

				rem OUTPUT TO XML

				rem Generated image does not exist
				if not exist %%c (

					rem Resource image does not exist
					if not exist !resPic! (
						set "outputError=Error="!resPic!,%%c do not exist"
						echo !output!^" !outputError!!output2!   >> "%_fileOutput%"	

					rem Resource image does exist
					) else (
						set "outputError=Error="%%c does not exist"
						echo !output!^" !outputError!!output2!   >> "%_fileOutput%"
					)

				set "_logGenerated=!_logGenerated!!newLine!    %%c"

				rem Generated image does exist
				) else (

					rem Resource image does not exist
					if not exist !resPic! (
						set "outputError=Error="!resPic! does not exist"
						echo !output!^" !outputError!!output2!  >> "%_fileOutput%"

					rem Resource image does exist
					) else (
						echo !output!!number!!output2! >> "%_fileOutput%"
					)
				)
			) 
		)
	)

	rem Finalize xml output
	set "output=    </ResourceImage>!newLine!</Images>"
	echo !output! >> "%_fileOutput%"

	rem Delete temporary file
	if exist %_fileTemp% del "%_fileTemp%"

	call:sendMail

	endlocal
	exit /b

:getMailBody
::
::	Sets the mail body due to resource and generated image existence and
::	returns it
::
	set "regardMessage=!newLine!!newLine!Best Regards,!newLine!ImageCompare"

	rem All resource images exist
	if "!_logResource!" == "" (

		rem All generated images exist
		if "!_logGenerated!" == "" (
			set "mailBody=No errors were detected!newLine!!regardMessage!"

		) else (
			set "mailBody=Following generated images do not exist:"
			set "mailBody=!mailBody!!_logGenerated!!regardMessage!"
		)

	rem Some of the resource images do not exist
	) else (

		rem All generated images exist
		if "!_logGenerated!" == "" (
			set "mailBody=Following resource images do not exist:"
			set "mailBody=!mailBody!!_logResource!!regardMessage!"
			
		) else (
			set "mailBody=Following resource images do not exist:!_logResource!"
			set "mailBody=!mailBody!!newLine!Following generated images do not"
			set "mailBody=!mailBody! exist:!_logGenerated!!regardMessage!"
		)
	)

	set "%~1=!mailBody!"
	exit /b

:sendMail
::
:: Gets mail address and password from console and sends an e-mail to self
::
:: Following global variables must be initialized before calling this method
:: _mailSubject, _mailServerGmail, _mailServerHotmail, _mailPort
::
	call:checkInternetConnection connection

	if not !connection!==1 (
		call:getMailBody mailBody
		set "sendMailCmd=$credential = Get-Credential;"
		set "sendMailCmd=!sendMailCmd!if($credential.Username.Split('@')[1]."
		set "sendMailCmd=!sendMailCmd!StartsWith('gmail')) {Send-MailMessage "
		set "sendMailCmd=!sendMailCmd!-From $credential.Username -to "
		set "sendMailCmd=!sendMailCmd!$credential.Username -Subject"
		set "sendMailCmd=!sendMailCmd! '!_mailSubject!' -Body '!mailBody!'"
		set "sendMailCmd=!sendMailCmd! -SmtpServer !_mailServerGmail! -port "
		set "sendMailCmd=!sendMailCmd!!_mailPort! -UseSsl -Credential "
		set "sendMailCmd=!sendMailCmd!$credential -Attachments !_fileOutput!}"
		set "sendMailCmd=!sendMailCmd!else{Send-MailMessage "
		set "sendMailCmd=!sendMailCmd!-From $credential.Username -to "
		set "sendMailCmd=!sendMailCmd!$credential.Username -Subject"
		set "sendMailCmd=!sendMailCmd! '!_mailSubject!' -Body '!mailBody!'"
		set "sendMailCmd=!sendMailCmd! -SmtpServer !_mailServerHotmail! -port "
		set "sendMailCmd=!sendMailCmd!!_mailPort! -UseSsl -Credential "
		set "sendMailCmd=!sendMailCmd!$credential -Attachments !_fileOutput!}"
		powershell -command "!sendMailCmd!"
	)

	if !connection!==1 (
		echo "Check your internet connection, mail could not be sent!"
	)

	exit /b

:checkInternetConnection
::
:: Checks internet connection availability
::
:: Returns 0 if internet is available, 1 o/w
::
	PING -n 1 www.google.com | find "Reply from " >nul
	set "%~1=!errorlevel!"
	exit /b
