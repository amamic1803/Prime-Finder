from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo
from multiprocessing import Process, Pool, freeze_support, Value
from threading import Thread
import sys
import os
import rust
from math import floor
import psutil
import ctypes


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except AttributeError:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def check_prime_overflow(n: int):
	if n < 2:
		return False
	elif n == 2:
		return True
	else:
		if n % 2 == 0:
			return False
		for i in range(3, floor(n ** 0.5) + 1, 2):
			if n % i == 0:
				return False
		return True

def change_thickness(event, widget, typ):
	global disabled
	if not disabled:
		if typ:
			widget.config(highlightthickness=1)
		else:
			widget.config(highlightthickness=3)

def browse_click(event):
	global started
	if not disabled:
		init_dir = os.path.dirname(file_ent.get())
		if not os.path.isdir(init_dir):
			init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
		selection = askopenfilename(filetypes=(("Text file", "*.txt"), ), initialdir=init_dir, parent=root)
		if selection != "":
			file_ent.delete(0, END)
			file_ent.insert(0, selection.replace("/", "\\"))
			file_ent.xview_moveto(1)

def generate_click(event):
	global disabled
	if not disabled:
		pass

def validate_click(event):
	global disabled
	if not disabled:
		path = file_ent.get()
		if os.path.isfile(path):
			num_of_cpus = os.cpu_count()
			with open(file=path, mode="r", encoding="utf-8") as file, Pool(processes=num_of_cpus) as pool:
				queue = []
				good = True
				ended = False
				while True:
					if len(queue) < 2 * num_of_cpus and not ended:
						line = file.readline()
						if line != "":
							try:
								line = int(line.rstrip("\n"))
							except ValueError:
								good = False
								break
							queue.append(pool.apply_async(check_if_prime, args=(line, )))
						else:
							ended = True
					elif len(queue) == 0 and ended:
						break
					else:
						if not queue[0].get():
							good = False
							break
						queue.pop(0)
				curr_pos = file.tell()
				file.seek(0, os.SEEK_END)
				if good and file.tell() == curr_pos and get_last_line(path)[-1] == "\n":
					showinfo(title="Validation", message="The file is valid!")
				else:
					showerror(title="Validation", message="The file is not valid!")
		else:
			showerror(title="File error!", message="Invalid file selected!")

def check_click(event=None):
	global disabled, check_var, check_num, check_process
	if not disabled:
		num = num_ent.get()
		try:
			num = int(num)
			check_num = num
			toggle_gui()
			num_btn.config(text="Checking")
			check_process = Process(target=check_if_prime, args=(num, True, check_var))
			check_process.start()
			waiting_thread = Thread(target=wait_check_to_end)
			waiting_thread.start()
		except ValueError:
			pass

def get_last_line(file_path):
	with open(file_path, "rb") as file:
		try:
			file.seek(-2, os.SEEK_END)
			while file.read(1) != b'\n':
				file.seek(-2, os.SEEK_CUR)
		except OSError:
			file.seek(0)
		return file.readline().decode()

def check_if_prime(n: int, showresult=False, check=None):
	try:
		ret = rust.check_if_prime_u128(n)
	except OverflowError:
		ret = check_prime_overflow(n)
	if psutil.Process(os.getpid()).parent() is not None:
		if showresult:
			if ret:
				check.value = True
			else:
				check.value = False
		else:
			return ret

def wait_check_to_end():
	global check_var, check_num, check_process
	try:
		check_process.join()
		check_process.close()
		toggle_gui()
		num_btn.config(text="Check")
		if check_var.value:
			showinfo(title="Prime Finder", message=f"{check_num} is a prime number!", parent=root)
		else:
			showinfo(title="Prime Finder", message=f"{check_num} is NOT a prime number!", parent=root)
	except (ValueError, RuntimeError, OSError):
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

def toggle_gui():
	global disabled
	if disabled:
		disabled = False
		num_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", background="#406060", activeforeground="#406060")
		browse_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", background="#406060", activeforeground="#406060")
		validate_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", background="#406060", activeforeground="#406060")
		generate_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", background="#406060", activeforeground="#406060")
		num_ent.config(state="normal", highlightcolor="#ffffff", highlightbackground="#ffffff")
		file_ent.config(state="normal", highlightcolor="#ffffff", highlightbackground="#ffffff")
	else:
		disabled = True
		num_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000", background="#263939", activeforeground="#263939")
		browse_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000", background="#263939", activeforeground="#263939")
		validate_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000", background="#263939", activeforeground="#263939")
		generate_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000", background="#263939", activeforeground="#263939")
		num_ent.config(state="disabled", highlightcolor="#000000", highlightbackground="#000000")
		file_ent.config(state="disabled", highlightcolor="#000000", highlightbackground="#000000")


if __name__ == '__main__':
	freeze_support()

	disabled = False
	check_var = Value(ctypes.c_bool)
	check_num = 0
	check_process = None

	root = Tk()
	root.title("Prime Finder")
	root.resizable(False, False)
	root.iconbitmap(resource_path("Prime-Finder-icon.ico"))
	root.geometry(f"500x240+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 120}")
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
	num_btn.bind("<ButtonRelease-1>", check_click)

	file_lbl = Label(root, text="Generate primes:", font=("Helvetica", 12, "bold"), borderwidth=0, background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	file_lbl.place(x=0, y=155, width=145, height=30)
	file_ent = Entry(root, font=("Helvetica", 10), borderwidth=0, highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", disabledbackground="#263939", disabledforeground="#ffffff", background="#406060", foreground="#ffffff", justify=LEFT, insertbackground="#ffffff")
	file_ent.place(x=141, y=155, width=264, height=30)
	browse_btn = Label(root, text="Browse", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	browse_btn.place(x=420, y=155, width=65, height=30)
	browse_btn.bind("<Enter>", lambda event: change_thickness(event, browse_btn, False))
	browse_btn.bind("<Leave>", lambda event: change_thickness(event, browse_btn, True))
	browse_btn.bind("<ButtonRelease-1>", browse_click)

	validate_btn = Label(root, text="Validate", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	validate_btn.place(x=340, y=195, width=65, height=30)
	validate_btn.bind("<Enter>", lambda event: change_thickness(event, validate_btn, False))
	validate_btn.bind("<Leave>", lambda event: change_thickness(event, validate_btn, True))
	validate_btn.bind("<ButtonRelease-1>", validate_click)

	generate_btn = Label(root, text="Generate", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	generate_btn.place(x=420, y=195, width=65, height=30)
	generate_btn.bind("<Enter>", lambda event: change_thickness(event, generate_btn, False))
	generate_btn.bind("<Leave>", lambda event: change_thickness(event, generate_btn, True))
	generate_btn.bind("<ButtonRelease-1>", generate_click)

	root.mainloop()

	try:
		check_process.kill()
		check_process.join()
		check_process.close()
	except (AttributeError, ValueError):
		pass
