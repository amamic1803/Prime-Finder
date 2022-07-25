from tkinter import *
from multiprocessing import Pool, freeze_support
import sys
import os
import rust_check_if_prime
from math import floor


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except AttributeError:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def check_prime_overflow(n: int):
	if n >= 2:
		for i in range(2, floor(n ** 0.5) + 1):
			if n % i == 0:
				return False
		return True
	else:
		return False


if __name__ == '__main__':
	freeze_support()

	root = Tk()
	root.title("Prime-Finder")
	root.resizable(False, False)
	root.iconbitmap(resource_path("Prime-Finder-icon.ico"))
	root.geometry(f"500x500+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 250}")

	root.mainloop()
