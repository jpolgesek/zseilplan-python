#coding: utf-8
import sys

def log(text, end="\n", overwrite = False):
	if overwrite:
		sys.stdout.write('\r')
	sys.stdout.write(text)
	sys.stdout.write(end)
	sys.stdout.flush()

	return True

def step(text, state = "    "):
	if state == "    ":
		log("[{}] {}".format(state, text), end="")
	else:
		log("[{}] {}".format(state, text), overwrite=True)
	
	return True

def substep(text = ""):
	print("       - {}".format(text))

def debug(text = "", level=2):
	#TODO: check level
	#log(text)
	return True


def check_python_version():
	if sys.version_info < (3, 0):
		print("This program requires python 3.x. Exiting.")
		sys.exit(1)
	elif sys.version_info < (3, 7):
		print("This program prefers python 3.7, but will run on python 3.x.")
		print("Warning! utils.hash might work incorrectly.")
