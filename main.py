from tkinter import *
from tkinter.filedialog import askopenfilename
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
		if n % 2 == 0 and n != 2:
			return False
		for i in range(3, floor(n ** 0.5) + 1, 2):
			if n % i == 0:
				return False
		return True
	else:
		return False

def change_thickness(event, widget, typ):
	global started
	if not started:
		if typ:
			widget.config(highlightthickness=1)
		else:
			widget.config(highlightthickness=3)

def browse_click(event):
	global started
	if not started:
		init_dir = os.path.dirname(file_ent.get())
		if not os.path.isdir(init_dir):
			init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
		selection = askopenfilename(filetypes=(("All files", ""), ("Video files", "*.mp4;*.avi;*.mpg;*.mov;*.wmv;*.mkv"), ("JPEG files", "*.jpeg;*.jpg"), ("Portable Network Graphics", "*.png"), ("Windows bitmaps", "*.bmp;*.dib"), ("WebP", "*.webp"), ("Sun rasters", "*.sr;*.ras"), ("TIFF files", "*.tiff;*.tif")), initialdir=init_dir, parent=root)
		if selection != "":
			file_ent.delete(0, END)
			file_ent.insert(0, selection.replace("/", "\\"))
			file_ent.xview_moveto(1)

def check_if_prime(n: int):
	try:
		ret = rust_check_if_prime.run(n)
	except OverflowError:
		ret = check_prime_overflow(n)
	return ret


if __name__ == '__main__':
	freeze_support()

	started = False

	root = Tk()
	root.title("Prime-Finder")
	root.resizable(False, False)
	root.iconbitmap(resource_path("Prime-Finder-icon.ico"))
	root.geometry(f"500x500+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 250}")
	root.config(background="#80C0C0")

	title = Label(root, text="Prime-Finder", font=("Helvetica", 30, "bold", "italic"), borderwidth=0, background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	title.place(x=0, y=0, width=500, height=100)

	file_lbl = Label(root, text="File:", font=("Helvetica", 12, "bold"), borderwidth=0, background="#202A44", activebackground="#202A44", foreground="#ffffff", activeforeground="#ffffff")
	file_lbl.place(x=0, y=150, width=50, height=30)
	file_ent = Entry(root, font=("Helvetica", 10), borderwidth=0, highlightthickness=1, highlightbackground="green", highlightcolor="green", disabledbackground="grey15", disabledforeground="#ffffff", background="grey15", foreground="#ffffff", justify=LEFT, insertbackground="#ffffff")
	file_ent.place(x=46, y=150, width=390, height=30)
	browse_btn = Label(root, text="Browse", font=("Helvetica", 10), highlightthickness=1, highlightbackground="green", highlightcolor="green", borderwidth=0, background="grey15", activebackground="grey15", foreground="#ffffff", activeforeground="#ffffff")
	browse_btn.place(x=435, y=150, width=65, height=30)
	browse_btn.bind("<Enter>", lambda event: change_thickness(event, browse_btn, False))
	browse_btn.bind("<Leave>", lambda event: change_thickness(event, browse_btn, True))
	browse_btn.bind("<ButtonRelease-1>", browse_click)

	root.mainloop()
