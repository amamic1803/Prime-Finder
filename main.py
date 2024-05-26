import ctypes
import os
import sys
import threading
from multiprocessing import Process, Pool, freeze_support, Value
from threading import Thread
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo, askyesno

from lib.rust import is_prime_big  # string input
from lib.rust import is_prime_u128  # u128 input
from lib.rust import sieve_of_atkin  # usize input


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except AttributeError:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def change_thickness(event, widget, typ):
	global disabled
	if not disabled:
		if typ:
			widget.config(highlightthickness=1)
		else:
			widget.config(highlightthickness=3)

def change_thickness_generate(event, typ):
	global sieve_running
	if not sieve_running:
		if typ:
			generate_btn.config(highlightthickness=1)
		else:
			generate_btn.config(highlightthickness=3)

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

def enter_limit_click(event=None):
	global limit_number, num_ent_temp, select_window
	limit_number = int(num_ent_temp.get())
	select_window.destroy()

def sieve_thrd(limit, path):
	global sieve_running
	global sieve_process
	try:
		sieve_process = Process(target=generation_sieve, args=(limit, path))
		sieve_process.start()
		sieve_process.join()
	except Exception:
		pass
	toggle_gui()
	generation_running.value = False
	sieve_running = False

def generate_click(event):
	global generation_running, generation_num, sieve_running
	if sieve_running:
		pass
	elif generation_running.value:
		generation_running.value = False
		val = generation_num.value + 1
		if val == 256:
			generation_num.value = 0
		else:
			generation_num.value = val
		toggle_gui()
		generate_btn.config(text="Generate")
	else:
		generation_running.value = True
		path = file_ent.get()
		if os.path.isfile(path) and os.path.splitext(path)[1] == ".txt":
			try:
				last_num = get_last_line(path)
				if last_num == "":
					yes_no_result = askyesno(title="Generation method?", message="Do you want to set a limit to calculate primes up to it fast?", parent=root)
					if yes_no_result:
						global limit_number, num_ent_temp, select_window

						limit_number = 0

						select_window = Toplevel(root)
						select_window.title("Set number up to which primes will be generated!")
						select_window.resizable(False, False)
						select_window.iconbitmap(resource_path("resources/Prime-Finder-icon.ico"))
						select_window.geometry(f"385x50+{root.winfo_screenwidth() // 2 - (385 // 2)}+{root.winfo_screenheight() // 2 - 25}")
						select_window.config(background="#80C0C0")
						select_window.grab_set()
						select_window.focus_force()

						reg2 = select_window.register(validate_input)

						num_lbl_temp = Label(select_window, text="Upper limit:", font=("Helvetica", 12, "bold"), borderwidth=0,
						                background="#80C0C0",
						                activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
						num_lbl_temp.place(x=0, y=10, width=115, height=30)
						num_ent_temp = Entry(select_window, font=("Helvetica", 10), justify=CENTER, validate="key",
						                validatecommand=(reg2, "%P"),
						                borderwidth=0, highlightthickness=1, highlightbackground="#ffffff",
						                highlightcolor="#ffffff",
						                disabledbackground="#263939", disabledforeground="#ffffff",
						                background="#406060",
						                foreground="#ffffff", insertbackground="#ffffff")
						num_ent_temp.place(x=111, y=10, width=200, height=30)
						num_btn_temp = Label(select_window, text="Enter", font=("Helvetica", 10), highlightthickness=1,
						                highlightbackground="#ffffff",
						                highlightcolor="#ffffff", borderwidth=0, background="#406060",
						                activebackground="#406060",
						                foreground="#ffffff", activeforeground="#ffffff")
						num_btn_temp.place(x=315, y=10, width=65, height=30)
						num_btn_temp.bind("<Enter>", lambda event: change_thickness(event, num_btn_temp, False))
						num_btn_temp.bind("<Leave>", lambda event: change_thickness(event, num_btn_temp, True))
						num_btn_temp.bind("<ButtonRelease-1>", enter_limit_click)

						select_window.wait_window()

						if limit_number >= 10:
							sieve_running = True
							toggle_gui()
							sieve_thread = threading.Thread(target=sieve_thrd, args=(limit_number, path))
							sieve_thread.start()
							return

					with open(file=path, mode="w", encoding="utf-8") as file:
						file.write("2\n")
				last_num = int(get_last_line(path))
				if check_if_prime(last_num):
					if last_num == 2:
						last_num = 3
					else:
						last_num += 2

					generate_proc = Process(target=generation, args=(path, last_num, generation_running, generation_num, generation_num.value))
					generate_proc.start()
					toggle_gui()
					generate_btn.config(text="Stop", highlightcolor="red", highlightbackground="red")
				else:
					raise ValueError
			except ValueError:
				showerror(title="File error!", message="The file is not valid!", parent=root)
				generation_running.value = False
		else:
			showerror(title="File error!", message="Invalid file selected!", parent=root)
			generation_running.value = False

def generation(path, number, running, run_value, running_num):
	num_of_cpus = os.cpu_count()
	with open(file=path, mode="a", encoding="utf-8") as file, Pool(processes=num_of_cpus) as pool:
		queue_results = []
		queue_numbers = []
		result = ""
		while run_value.value == running_num and running.value:
			if len(queue_results) < 2 * num_of_cpus:
				queue_numbers.append(number)
				queue_results.append(pool.apply_async(check_if_prime, args=(number,)))
				number += 2
			else:
				if queue_results[0].get():
					result += f"{queue_numbers[0]}\n"
					if len(result) > 8_500_000:
						file.write(result)
						file.flush()
						os.fsync(file.fileno())
						result = ""
				queue_results.pop(0)
				queue_numbers.pop(0)
		file.write(result)

def generation_sieve(limit, path):
	with open(file=path, mode="w", encoding="utf-8") as file:
		file.write("\n".join(map(str, sieve_of_atkin(limit))))

def validate_click(event):
	global disabled
	if not disabled:
		path = file_ent.get()
		if os.path.isfile(path) and os.path.splitext(path) == ".txt":
			valid_thrd = Thread(target=validation, args=(path, ))
			valid_thrd.start()
			toggle_gui()
			validate_btn.config(text="Validating")
		else:
			showerror(title="File error!", message="Invalid file selected!", parent=root)

def validation(path):
	global validation_running
	validation_running = True
	num_of_cpus = os.cpu_count()
	with open(file=path, mode="r", encoding="utf-8") as file, Pool(processes=num_of_cpus) as pool:
		queue = []
		good = True
		ended = False
		while validation_running:
			if len(queue) < 2 * num_of_cpus and not ended:
				line = file.readline()
				if line != "":
					try:
						line = int(line.rstrip("\n"))
					except ValueError:
						good = False
						break
					queue.append(pool.apply_async(check_if_prime, args=(line,)))
				else:
					ended = True
			elif len(queue) == 0 and ended:
				break
			else:
				if not queue[0].get():
					good = False
					break
				queue.pop(0)
		if validation_running:
			toggle_gui()
			validate_btn.config(text="Validate")
			curr_pos = file.tell()
			file.seek(0, os.SEEK_END)
			try:
				if good and file.tell() == curr_pos and get_last_line(path)[-1] == "\n":
					raise IndexError
				else:
					showerror(title="Validation", message="The file is not valid!", parent=root)
			except IndexError:
				showinfo(title="Validation", message="The file is valid!", parent=root)

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
		ret = is_prime_u128(n)
	except OverflowError:
		ret = is_prime_big(str(n))
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
	except (AttributeError, ValueError, RuntimeError, OSError):
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

def main():
	global check_var, check_num, check_process
	global disabled
	global generate_btn, browse_btn
	global started
	global file_ent
	global root
	global generation_running, generation_num
	global validate_btn
	global validation_running
	global num_ent
	global num_btn
	global sieve_running
	global sieve_process

	sieve_running = False

	disabled = False

	check_var = Value(ctypes.c_bool)
	check_num = 0
	check_process = None

	validation_running = False

	generation_running = Value(ctypes.c_bool)
	generation_running.value = False
	generation_num = Value(ctypes.c_uint64)
	generation_num.value = 0

	root = Tk()
	root.title("Prime Finder")
	root.resizable(False, False)
	root.iconbitmap(resource_path("resources/Prime-Finder-icon.ico"))
	root.geometry(f"500x240+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 120}")
	root.config(background="#80C0C0")

	reg = root.register(validate_input)

	title = Label(root, text="Prime Finder", font=("Helvetica", 30, "bold", "italic"), borderwidth=0,
	              background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	title.place(x=0, y=0, width=500, height=100)

	num_lbl = Label(root, text="Check number:", font=("Helvetica", 12, "bold"), borderwidth=0, background="#80C0C0",
	                activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	num_lbl.place(x=0, y=100, width=145, height=30)
	num_ent = Entry(root, font=("Helvetica", 10), justify=CENTER, validate="key", validatecommand=(reg, "%P"),
	                borderwidth=0, highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff",
	                disabledbackground="#263939", disabledforeground="#ffffff", background="#406060",
	                foreground="#ffffff", insertbackground="#ffffff")
	num_ent.place(x=141, y=100, width=264, height=30)
	num_btn = Label(root, text="Check", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff",
	                highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060",
	                foreground="#ffffff", activeforeground="#ffffff")
	num_btn.place(x=420, y=100, width=65, height=30)
	num_btn.bind("<Enter>", lambda event: change_thickness(event, num_btn, False))
	num_btn.bind("<Leave>", lambda event: change_thickness(event, num_btn, True))
	num_btn.bind("<ButtonRelease-1>", check_click)

	file_lbl = Label(root, text="Generate primes:", font=("Helvetica", 12, "bold"), borderwidth=0, background="#80C0C0",
	                 activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
	file_lbl.place(x=0, y=155, width=145, height=30)
	file_ent = Entry(root, font=("Helvetica", 10), borderwidth=0, highlightthickness=1, highlightbackground="#ffffff",
	                 highlightcolor="#ffffff", disabledbackground="#263939", disabledforeground="#ffffff",
	                 background="#406060", foreground="#ffffff", justify=LEFT, insertbackground="#ffffff")
	file_ent.place(x=141, y=155, width=264, height=30)
	browse_btn = Label(root, text="Browse", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff",
	                   highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060",
	                   foreground="#ffffff", activeforeground="#ffffff")
	browse_btn.place(x=420, y=155, width=65, height=30)
	browse_btn.bind("<Enter>", lambda event: change_thickness(event, browse_btn, False))
	browse_btn.bind("<Leave>", lambda event: change_thickness(event, browse_btn, True))
	browse_btn.bind("<ButtonRelease-1>", browse_click)

	validate_btn = Label(root, text="Validate", font=("Helvetica", 10), highlightthickness=1,
	                     highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060",
	                     activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	validate_btn.place(x=340, y=195, width=65, height=30)
	validate_btn.bind("<Enter>", lambda event: change_thickness(event, validate_btn, False))
	validate_btn.bind("<Leave>", lambda event: change_thickness(event, validate_btn, True))
	validate_btn.bind("<ButtonRelease-1>", validate_click)

	generate_btn = Label(root, text="Generate", font=("Helvetica", 10), highlightthickness=1,
	                     highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0, background="#406060",
	                     activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
	generate_btn.place(x=420, y=195, width=65, height=30)
	generate_btn.bind("<Enter>", lambda event: change_thickness_generate(event, False))
	generate_btn.bind("<Leave>", lambda event: change_thickness_generate(event, True))
	generate_btn.bind("<ButtonRelease-1>", generate_click)

	root.mainloop()

	try:
		check_process.kill()
		check_process.join()
		check_process.close()
	except (AttributeError, ValueError):
		pass

	try:
		sieve_process.kill()
		sieve_process.join()
		sieve_process.close()
	except (AttributeError, ValueError):
		pass

	validation_running = False
	generation_running.value = False


if __name__ == '__main__':
	freeze_support()

	main()
