from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo
from multiprocessing import Process, Pool, freeze_support
import sys
import os
import rust_check_if_prime
from math import floor
import psutil

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
		selection = askopenfilename(filetypes=(("Text file", "*.txt"), ), initialdir=init_dir, parent=root)
		if selection != "":
			file_ent.delete(0, END)
			file_ent.insert(0, selection.replace("/", "\\"))
			file_ent.xview_moveto(1)

def check_if_prime(n: int, showresult=False):
	try:
		ret = rust_check_if_prime.run(n)
	except OverflowError:
		ret = check_prime_overflow(n)
	if psutil.Process(os.getpid()).parent() is not None:
		if showresult:
			if ret:
				showinfo(title="Prime Finder", message=f"{n} is a prime number!")
			else:
				showinfo(title="Prime Finder", message=f"{n} is NOT a prime number!")
		else:
			return ret

def num_prime_check(event=None):
	num = num_ent.get()
	try:
		num = int(num)
		process_num = Process(target=check_if_prime, args=(num, True))
		process_num.start()
	except ValueError:
		pass

def validate_input(full_text):
	if " " in full_text or "-" in full_text:
		return False
	elif full_text == "":
		return True
	else:
		try:
			int(full_text)
			return True
		except ValueError:
			return False


if __name__ == '__main__':
	freeze_support()

	started = False

	root = Tk()
	root.title("Prime Finder")
	root.resizable(False, False)
	root.iconbitmap(resource_path("Prime-Finder-icon.ico"))
	root.geometry(f"500x500+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 250}")
	root.config(background="#80C0C0")

	reg = root.register(validate_input)

	title = Label(root, text="Prime Finder", font=("Helvetica", 30, "bold", "italic"), borderwidth=0, background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	title.place(x=0, y=0, width=500, height=100)

	num_lbl = Label(root, text="Check number:", font=("Helvetica", 12, "bold"), borderwidth=0, background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	num_lbl.place(x=0, y=100, width=145, height=30)
	num_ent = Entry(root, font=("Helvetica", 10), justify=CENTER, validate="key", validatecommand=(reg, "%P"), borderwidth=0, highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", disabledbackground="#263939", disabledforeground="#ffffff", background="#406060", foreground="#ffffff", insertbackground="#ffffff")
	num_ent.place(x=141, y=100, width=264, height=30)
	num_btn = Label(root, text="Check", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	num_btn.place(x=420, y=100, width=65, height=30)
	num_btn.bind("<Enter>", lambda event: change_thickness(event, num_btn, False))
	num_btn.bind("<Leave>", lambda event: change_thickness(event, num_btn, True))
	num_btn.bind("<ButtonRelease-1>", num_prime_check)

	file_lbl = Label(root, text="Generate primes:", font=("Helvetica", 12, "bold"), borderwidth=0, background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	file_lbl.place(x=0, y=150, width=145, height=30)
	file_ent = Entry(root, font=("Helvetica", 10), borderwidth=0, highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", disabledbackground="#263939", disabledforeground="#ffffff", background="#406060", foreground="#ffffff", justify=LEFT, insertbackground="#ffffff")
	file_ent.place(x=141, y=150, width=264, height=30)
	browse_btn = Label(root, text="Browse", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	browse_btn.place(x=420, y=150, width=65, height=30)
	browse_btn.bind("<Enter>", lambda event: change_thickness(event, browse_btn, False))
	browse_btn.bind("<Leave>", lambda event: change_thickness(event, browse_btn, True))
	browse_btn.bind("<ButtonRelease-1>", browse_click)

	root.mainloop()
