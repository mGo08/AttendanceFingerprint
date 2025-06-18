import tkinter as tk
from tkinter import ttk
import sv_ttk
from gui.main_window import MainWindow


def main():
    root = tk.Tk()
    sv_ttk.set_theme("dark")

    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()