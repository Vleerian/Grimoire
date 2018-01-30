import inspect

#The ATABOX class is our 'Constants and QOL' container
class Grimoire_Config():
	#Debug_Mode enables Debug_Level print statements on the console
	Debug_Mode = True

	Database_Name = "Database"

	#Self explanatory. If Debug_Mode is on, it prints out exception messages when errors are encountered.
	def HandleErrMsg(Error):
		if Grimoire_Config.Debug_Mode:
			Caller = inspect.stack()[1][3]
			print("-----------------------------------")
			print(Caller + " EXCEPTION ENCOUNTERED:")
			print(Error)
			print("-----------------------------------")
