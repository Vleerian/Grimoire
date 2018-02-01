import inspect

#The ATABOX class is our 'Constants and QOL' container
class Grimoire_Config():
	#Debug_Mode enables Debug_Level print statements on the console
	Debug_Mode 			= True

	#Port controls... what port it runs on.
	Port				= 8000

	#Controls the name of the database file
	Database_Name 		= "Database"

	#Controls if Markdown is enabled or disabled. WARNING: DISABLING THIS REMOVES FIELDS
	Enable_Markdown 	= True

	#Controls if potential pages and books will appear
	Enable_Potential 	= True

	#Controls if prompts will be given
	Enable_Prompts		= True

	#Self explanatory. If Debug_Mode is on, it prints out exception messages when errors are encountered.
	def HandleErrMsg(Error):
		if Grimoire_Config.Debug_Mode:
			Caller = inspect.stack()[1][3]
			print("-----------------------------------")
			print(Caller + " EXCEPTION ENCOUNTERED:")
			print(Error)
			print("-----------------------------------")
