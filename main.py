import ctypes
import os
import sys
import tkinter as tk
from multiprocessing import Process, freeze_support, Value
from threading import Thread
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo

import primes


class App:
	def __init__(self):
		self.running = False
		self.worker_process = None

		self.root = tk.Tk()
		self.root.title("Prime Finder")
		self.root.resizable(False, False)
		self.root.iconbitmap(self.resource_path("resources/Prime-Finder-icon.ico"))
		self.root.geometry(f"500x240"
		                   f"+{self.root.winfo_screenwidth() // 2 - 250}"
		                   f"+{self.root.winfo_screenheight() // 2 - 120}")
		self.root.config(background="#80C0C0")

		self.title = tk.Label(self.root, text="Prime Finder", font=("Helvetica", 30, "bold", "italic"),
		                      borderwidth=0, background="#80C0C0", activebackground="#80C0C0",
		                      foreground="#ffffff", activeforeground="#ffffff")
		self.title.place(x=0, y=0, width=500, height=100)

		self.num_lbl = tk.Label(self.root, text="Check number:", font=("Helvetica", 12, "bold"),
		                        borderwidth=0, background="#80C0C0", activebackground="#80C0C0",
		                        foreground="#ffffff", activeforeground="#ffffff")
		self.num_lbl.place(x=0, y=100, width=145, height=30)

		self.reg = self.root.register(self.validate_int)
		self.num_ent = tk.Entry(self.root, font=("Helvetica", 10), justify=tk.CENTER,
		                        validate="key", validatecommand=(self.reg, "%P"),
		                        borderwidth=0, highlightthickness=1, highlightbackground="#ffffff",
		                        highlightcolor="#ffffff", disabledbackground="#263939", disabledforeground="#ffffff",
		                        background="#406060", foreground="#ffffff", insertbackground="#ffffff")
		self.num_ent.place(x=141, y=100, width=264, height=30)

		self.num_btn = tk.Label(self.root, text="Check", font=("Helvetica", 10), cursor="hand2",
		                        highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff",
		                        borderwidth=0, background="#406060", activebackground="#406060",
		                        foreground="#ffffff", activeforeground="#ffffff")
		self.num_btn.place(x=420, y=100, width=65, height=30)
		self.num_btn.bind("<Enter>", lambda event: self.num_btn.config(highlightthickness=3) if not self.running else None)
		self.num_btn.bind("<Leave>", lambda event: self.num_btn.config(highlightthickness=1) if not self.running else None)
		self.num_btn.bind("<ButtonRelease-1>", lambda event: self.check_click())

		self.file_lbl = tk.Label(self.root, text="Generate primes:", font=("Helvetica", 12, "bold"),
		                         borderwidth=0, background="#80C0C0", activebackground="#80C0C0",
		                         foreground="#ffffff", activeforeground="#ffffff")
		self.file_lbl.place(x=0, y=155, width=145, height=30)

		self.file_ent = tk.Entry(self.root, font=("Helvetica", 10), borderwidth=0, highlightthickness=1,
		                         highlightbackground="#ffffff", highlightcolor="#ffffff",
		                         disabledbackground="#263939", disabledforeground="#ffffff", background="#406060",
		                         foreground="#ffffff", justify=tk.LEFT, insertbackground="#ffffff")
		self.file_ent.place(x=141, y=155, width=264, height=30)

		self.browse_btn = tk.Label(self.root, text="Browse", font=("Helvetica", 10), highlightthickness=1, cursor="hand2",
		                           highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0,
		                           background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
		self.browse_btn.place(x=420, y=155, width=65, height=30)
		self.browse_btn.bind("<Enter>", lambda event: self.browse_btn.config(highlightthickness=3) if not self.running else None)
		self.browse_btn.bind("<Leave>", lambda event: self.browse_btn.config(highlightthickness=1) if not self.running else None)
		self.browse_btn.bind("<ButtonRelease-1>", lambda event: self.browse_click())

		self.generate_btn = tk.Label(self.root, text="Generate", font=("Helvetica", 10), highlightthickness=1, cursor="hand2",
		                             highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=0,
		                             background="#406060", activebackground="#406060", foreground="#ffffff", activeforeground="#ffffff")
		self.generate_btn.place(x=420, y=195, width=65, height=30)
		self.generate_btn.bind("<Enter>", lambda event: self.generate_btn.config(highlightthickness=3) if not self.running else None)
		self.generate_btn.bind("<Leave>", lambda event: self.generate_btn.config(highlightthickness=1) if not self.running else None)
		self.generate_btn.bind("<ButtonRelease-1>", lambda event: self.generate_click())

		self.status_lbl = tk.Label(self.root, text="Ready", font=("Helvetica", 10, "bold"), borderwidth=0,
		                           background="#80C0C0", activebackground="#80C0C0",
		                           foreground="#ffffff", activeforeground="#ffffff")
		self.status_lbl.place(x=0, y=195, width=415, height=30)

		self.root.mainloop()

		try:
			self.worker_process.kill()
			self.worker_process.join()
			self.worker_process.close()
		except (AttributeError, ValueError):
			pass

	def toggle_gui(self):
		if self.running:
			self.num_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff",
			                    background="#406060", activeforeground="#406060")
			self.browse_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff",
			                       background="#406060", activeforeground="#406060")
			self.generate_btn.config(highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff",
			                         background="#406060", activeforeground="#406060")
			self.num_ent.config(state="normal", highlightcolor="#ffffff", highlightbackground="#ffffff")
			self.file_ent.config(state="normal", highlightcolor="#ffffff", highlightbackground="#ffffff")
		else:
			self.num_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000",
			                    background="#263939", activeforeground="#263939")
			self.browse_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000",
			                       background="#263939", activeforeground="#263939")
			self.generate_btn.config(highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000",
			                         background="#263939", activeforeground="#263939")
			self.num_ent.config(state="disabled", highlightcolor="#000000", highlightbackground="#000000")
			self.file_ent.config(state="disabled", highlightcolor="#000000", highlightbackground="#000000")
		self.running = not self.running

	def browse_click(self):
		if self.running:
			return

		init_dir = os.path.dirname(self.file_ent.get())
		if not os.path.isdir(init_dir):
			init_dir = os.path.dirname(sys.executable)
		if not os.path.isdir(init_dir):
			init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')

		selection = askopenfilename(filetypes=(("Text file", "*.txt"),), initialdir=init_dir, parent=self.root)
		if selection != "":
			self.file_ent.delete(0, tk.END)
			self.file_ent.insert(0, selection.replace("/", "\\"))
			self.file_ent.xview_moveto(1)

	def check_click(self):
		if self.running:
			return

		try:
			num = int(self.num_ent.get())
		except ValueError:
			showerror(title="Invalid input!", message="Please enter a valid number!", parent=self.root)
			return

		check_result = Value(ctypes.c_bool)
		check_result_set = Value(ctypes.c_bool, False)

		def wait_check():
			try:
				self.worker_process.join()
				self.worker_process.close()
				self.toggle_gui()
				self.status_lbl.config(text="Ready")
				if check_result_set.value:
					showinfo(title="Prime Finder", message=f"{num} is{" " if check_result.value else " NOT "}a prime number!", parent=self.root)
			except (AttributeError, ValueError, RuntimeError, OSError):
				pass

		self.toggle_gui()
		self.status_lbl.config(text="Checking")
		self.worker_process = Process(target=check, args=(num, check_result, check_result_set), daemon=True)
		self.worker_process.start()
		wait_check_thread = Thread(target=wait_check, daemon=True)
		wait_check_thread.start()

	def generate_click(self):
		if self.running:
			try:
				self.worker_process.kill()
				self.worker_process.join()
				self.worker_process.close()
			except (AttributeError, ValueError):
				pass
			return

		path = self.file_ent.get()

		if os.path.isfile(path) and os.path.getsize(path) > 0:
			showerror(title="File error!", message="The file is not empty!", parent=self.root)
			return
		elif os.path.isdir(path):
			showerror(title="File error!", message="The file is a directory!", parent=self.root)
			return

		try:
			open(path, "w", encoding="utf-8").close()
		except PermissionError:
			showerror(title="File error!", message="You do not have the necessary permissions to open the file!", parent=self.root)
			return
		except OSError as e:
			showerror(title="File error!", message="OS error: " + e.strerror, parent=self.root)
			return

		limit_number = 0

		select_window = tk.Toplevel(self.root)
		select_window.title("Set a number up to which the primes will be generated!")
		select_window.iconbitmap(self.resource_path("resources/Prime-Finder-icon.ico"))
		select_window.resizable(False, False)
		select_window.geometry(f"385x50"
		                       f"+{self.root.winfo_screenwidth() // 2 - (385 // 2)}"
		                       f"+{self.root.winfo_screenheight() // 2 - 25}")
		select_window.config(background="#80C0C0")
		select_window.grab_set()
		select_window.focus_force()
		select_window.transient(self.root)

		num_lbl_temp = tk.Label(select_window, text="Upper limit:", font=("Helvetica", 12, "bold"), borderwidth=0,
		                        background="#80C0C0", activebackground="#80C0C0", foreground="#ffffff", activeforeground="#ffffff")
		num_lbl_temp.place(x=0, y=10, width=115, height=30)

		reg2 = select_window.register(self.validate_int)
		num_ent_temp = tk.Entry(select_window, font=("Helvetica", 10), justify=tk.CENTER, validate="key", validatecommand=(reg2, "%P"),
		                        borderwidth=0, highlightthickness=1, highlightbackground="#ffffff", highlightcolor="#ffffff",
		                        disabledbackground="#263939", disabledforeground="#ffffff", background="#406060",
		                        foreground="#ffffff", insertbackground="#ffffff")
		num_ent_temp.place(x=111, y=10, width=200, height=30)

		num_btn_temp = tk.Label(select_window, text="Enter", font=("Helvetica", 10), highlightthickness=1, highlightbackground="#ffffff",
		                        highlightcolor="#ffffff", borderwidth=0, background="#406060", activebackground="#406060",
		                        foreground="#ffffff", activeforeground="#ffffff")
		num_btn_temp.place(x=315, y=10, width=65, height=30)
		num_btn_temp.bind("<Enter>", lambda event: num_btn_temp.config(highlightthickness=3))
		num_btn_temp.bind("<Leave>", lambda event: num_btn_temp.config(highlightthickness=1))

		def set_limit():
			nonlocal limit_number
			try:
				limit_number = int(num_ent_temp.get())
			except ValueError:
				showerror(title="Invalid input!", message="Please enter a valid number!", parent=select_window)
				return
			select_window.destroy()
		num_btn_temp.bind("<ButtonRelease-1>", lambda event: set_limit())

		select_window.wait_window()
		if limit_number < 2:
			return

		def wait_generate():
			try:
				self.worker_process.join()
				self.worker_process.close()
				self.toggle_gui()
				self.status_lbl.config(text="Ready")
			except (AttributeError, ValueError, RuntimeError, OSError):
				pass

		self.toggle_gui()
		self.status_lbl.config(text="Generating")
		self.worker_process = Process(target=generate, args=(limit_number, path), daemon=True)
		self.worker_process.start()
		generate_thread = Thread(target=wait_generate, daemon=True)
		generate_thread.start()

	@staticmethod
	def resource_path(relative_path):
		""" Get absolute path to resource, works for dev and for PyInstaller """
		try:
			# PyInstaller creates a temp folder and stores path in _MEIPASS
			base_path = sys._MEIPASS
		except AttributeError:
			base_path = os.path.abspath(".")
		return os.path.join(base_path, relative_path)

	@staticmethod
	def validate_int(full_text: str) -> bool:
		"""Validate if the input is an integer."""
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


def check(num, check_result, check_result_set):
	check_result.value = primes.is_prime(num)
	check_result_set.value = True

def generate(limit, path):
	prime_numbers = primes.sieve_of_eratosthenes(limit)
	with open(file=path, mode="w", encoding="utf-8") as file:
		file.write("\n".join(map(str, prime_numbers)))


if __name__ == '__main__':
	freeze_support()
	App()
