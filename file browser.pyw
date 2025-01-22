from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.messagebox import askyesno
from tkinter import Tk
import shutil
import os
import ctypes
import pathlib
import time
import subprocess
import sys
import logging
import traceback
import cv2


logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Increases Dots Per inch so it looks sharper
ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
# set a title for our file explorer main window
root.title('Simple File Explorer')

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)
root.geometry("1400x793")
root.state("zoomed")

sWidth = root.winfo_screenwidth()
sHeight = root.winfo_screenheight()


SHOW_ERRORS = True

def disable_exit():
    pass

def center(win, w=1, h=1):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = w
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = h
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def on_crash(exctype, excvalue, exctraceback):
    if SHOW_ERRORS:
        if issubclass(exctype, KeyboardInterrupt):
            sys.__excepthook__(exctype, excvalue, exctraceback)
            return
        # Create a traceback string
        tb_lines = traceback.format_exception(exctype, excvalue, exctraceback)

        # Remove the raise line (the raise exception line)
        if "raise" in tb_lines[-2]:
            tb_lines.pop(-2)  # This removes the raise line of the traceback

        # Log the modified traceback
        logging.error(''.join(tb_lines))
    else:
        pass
sys.excepthook = on_crash

class Error(Exception):
    """Exception raised for custom error in the application."""
    def __init__(self, message=None, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"

def wError(message="An error occurred"):
    messagebox.showerror('Simple File Explorer', "Error: " + str(message), parent=top)

def check_directory_permissions(directory_path):
   try:
       permissions = os.stat(directory_path).st_mode
       test = os.listdir(directory_path)
       del test
       return (True if permissions & 0o400 else False) # read
   except Exception:
       return False

def check_file_permissions(directory_path):
   try:
       permissions = os.stat(directory_path).st_mode
       return (True if permissions & 0o400 else False) # read
   except Exception:
       return False

def check_write_permissions(directory_path):
    try:
        permissions = os.stat(directory_path).st_mode
        f = open(os.path.join(directory_path, "dgug1vkahrfa0fugrfegfy1grea.txt"), "w")
        f.close()
        os.remove(os.path.join(directory_path, "dgug1vkahrfa0fugrfegfy1grea.txt"))
        del f
        return (True if permissions & 0o200 else False) # write
    except Exception:
        try:
           del f
        except Exception:
           pass
        return False

def pathChange(*event):
    try:
        directory = os.listdir(currentPath.get()) # Get all Files and Folders from the given Directory
        if sort == 1:
            directory = sorted(directory, key=str.lower, reverse=True)
        elif sort == 2:
            directory = sorted(directory, key=str.lower)
        else:
            directory = sorted(directory, key=str.lower, reverse=True)
        pdirect = "/"
        fdirect = "/"
        for file in directory:  # Inserting the files and directories into the list
            path = os.path.join(currentPath.get(), file)
            if os.path.isfile(path):
                if pdirect == "/":
                    pdirect = [file]
                else:
                    pdirect = pdirect + [file]
            else:
                if fdirect == "/":
                    del fdirect
                    fdirect = [file]
                else:
                    fdirect = fdirect + [file]
        if fdirect == "/":
            directory = pdirect
        elif pdirect == "/":
            directory = fdirect
        else:
            if sort == 1:
                directory = pdirect + fdirect
            elif sort == 2:
                directory = fdirect + pdirect
            else:
                directory = pdirect + fdirect
        del fdirect
        del pdirect
        alist.delete(0, END) # Clearing the list
        for file in directory:  # Inserting the files and directories into the list
            alist.insert(0, file)
        num = alist.index("end")
        scrollbar.grid_forget()
        if num >= 37:
            scrollbar.grid(row=1,column=2,sticky='ns')
    except Exception as i:
        print(i)
        alist.delete(0, END)

def changePathByClick(event=None):
    # Get clicked item.
    picked = alist.get(alist.curselection()[0])
    # get the complete path by joining the current path with the picked item
    path = os.path.join(currentPath.get(), picked)
    if os.path.isfile(path):
        print('Opening: '+path)
        try:
            os.startfile(path)
        except Exception:
            messagebox.showerror('Simple File Explorer', "Error: You are not allowed to open this file")
    else: # Set new path, will trigger pathChange function.
        if check_directory_permissions(str(path)) == True:
            currentPath.set(path)
        else:
            messagebox.showerror('Simple File Explorer', "Error: You don't have read permissions to view this directory")

def goBack(event=None):
    # get the new path
    newPath = pathlib.Path(currentPath.get()).parent
    # set it to currentPath
    currentPath.set(newPath)
    # simple message
    print('Going Back')

def open_popup():
    global top
    top = Toplevel(root)
    w = int(round(0.18301610541 * sWidth))
    h = int(round(0.1953125 * sHeight))
    top.geometry(str(w) + "x" + str(h))
    top.resizable(False, False)
    top.title("Create")
    top.columnconfigure(0, weight=1)
    Label(top, text='Enter File or Folder name').grid(pady=6)
    Entry(top, textvariable=newFileName).grid(row=1, padx=20, pady=10, sticky='NSEW')
    frame1 = Frame(top)
    frame1.grid(row=2, column=0)
    A = Checkbutton(frame1,
                    text='File',
                    variable=TYPE,
                    onvalue=1,
                    offvalue=0)

    B = Checkbutton(frame1,
                    text='Folder',
                    variable=TYPE,
                    onvalue=2,
                    offvalue=0)
    A.grid(column=0, row=2, sticky='NSEW')
    B.grid(column=1, row=2, sticky='NSEW')
    Button(top, text="Create", command=newFileOrFolder).grid(row=3,padx=10, pady=10, sticky='NSEW')
    top.grab_set()

def rightClick(event):
    global selected
    try:
        del selected
    except Exception:
        pass
    alist.selection_clear(0,END)
    alist.selection_set(alist.nearest(event.y))
    alist.activate(alist.nearest(event.y))
    selected = alist.get(alist.curselection()[0])
    # print(list.index("end"))
    try:
        rm.tk_popup(event.x_root, event.y_root)
    finally:
        rm.grab_release()

def fdelete():
   if os.path.isfile(os.path.join(currentPath.get(), selected)):
       answer = confirm(1, selected)
       if answer == True:
           try:
               os.remove(os.path.join(currentPath.get(), selected))
               pathChange('')
           except Exception:
               messagebox.showerror('Simple File Explorer', "Error: Cannot delete " + selected)
   else:
       answer = confirm(2, selected)
       if answer == True:
           try:
               os.rmdir(os.path.join(currentPath.get(), selected))
               pathChange('')
           except Exception:
               messagebox.showerror('Simple File Explorer', "Error: Cannot delete the " + selected + " folder")
def frename():
    global rename
    global reFileName
    try:
        del reFileName
    except:
        pass
    reFileName = StringVar(root, selected, 're_name')
    rename = Toplevel(root)
    w = int(round(0.18301610541 * sWidth))
    h = int(round(0.1953125 * sHeight))
    rename.geometry(str(w) + "x" + str(h))
    rename.resizable(False, False)
    rename.title("Rename")
    rename.columnconfigure(0, weight=1)
    Label(rename, text='Enter File or Folder name').grid()
    Entry(rename, textvariable=reFileName).grid(column=0, pady=10, sticky='NSEW')
    Button(rename, text="Rename", command=renameFileOrFolder).grid(pady=10, sticky='NSEW')
    rename.grab_set()

def fcopy():
    os.popen("@powershell Add-Type -AssemblyName System.Windows.Forms ; $files = [System.Collections.Specialized.StringCollection]::new() ; $files.Add('" + os.path.join(currentPath.get(), selected + "') ; [System.Windows.Forms.Clipboard]::SetFileDropList($files)"))

def fpaste():
    print(root.clipboard_get())
    if os.path.isfile(root.clipboard_get()):
        shutil.copy2(root.clipboard_get(), currentPath.get())
    else:
        folder = os.path.basename(root.clipboard_get())
        temp1 = r"\a"
        temp1 = temp1.replace("a", '')
        shutil.copytree(root.clipboard_get(), currentPath.get()+ temp1 + folder, dirs_exist_ok=True)
    pathChange()

def charCheck(string):
    slist = []
    for i in string:
        if i not in slist:
             slist = slist + [i]
    return sorted(slist)

def renameFileOrFolder():
    check = charCheck(reFileName.get())
    temp1 = r"\a"
    temp1 = temp1.replace("a", '')
    if temp1 in check or '/' in check or ':' in check or '*' in check or '?' in check or '"' in check or '<' in check  or '>' in check  or '|' in check:
        messagebox.showerror('Simple File Explorer', "Error: Invalid file name.")
    elif check_write_permissions(currentPath.get()) == True:
        # check if it is a file name or a folder
        if os.path.isfile(os.path.join(currentPath.get(), selected)):
            os.rename(os.path.join(currentPath.get(), selected),os.path.join(currentPath.get(), reFileName.get()))
            rename.destroy()
        else:
            os.rename(os.path.join(currentPath.get(), selected),os.path.join(currentPath.get(), reFileName.get()))
            rename.destroy()
        pathChange()
    else:
       messagebox.showerror('Simple File Explorer', "Error: You don't have write permissions in this directory.")

def newFileOrFolder():
    check = charCheck(newFileName.get())
    temp1 = r"\a"
    temp1 = temp1.replace("a", '')
    if temp1 in check or '/' in check or ':' in check or '*' in check or '?' in check or '"' in check or '<' in check  or '>' in check  or '|' in check:
        wError("Invalid file name.")
    elif check_write_permissions(currentPath.get()) == True:
        # check if it is a file name or a folder
        if TYPE.get() == 1:
            if not charCheck(newFileName.get()) == ['.']:
                open(os.path.join(currentPath.get(), newFileName.get()), 'w').close()
            else:
                wError("Invalid file name.")
                return
        elif TYPE.get() == 2:
            os.mkdir(os.path.join(currentPath.get(), newFileName.get()))
        else:
            wError("You must select type.")
            return
        # destroy the top
        top.destroy() # check write perms
        pathChange()
    else:
       messagebox.showerror('Simple File Explorer', "Error: You don't have write permissions in this directory.")

def confirm(ty = 0, string = ""):
    temp = 0
    try:
        ty = int(ty)
    except Exception:
        temp = 1
    if temp == 1:
        raise Error(str(ty) + " is not a int.", 400)
    del temp
    if string == "":
        ty = 0
    if ty == 1:
        answer = askyesno(title='Delete file', message='Are you sure that you want delete ' + string + '?')
    elif ty == 2:
        answer = askyesno(title='Delete folder', message='Are you sure that you want delete the ' + string + ' folder?')
    else:
        answer = askyesno(title='Confirmation', message='Are you sure?')
    return answer

def ASort():
    global sort
    sort = 1
    SortOption.entryconfigure(3,command='', image=tick)
    SortOption.entryconfigure(4,command=BSort, image='')
    pathChange()

def BSort():
    global sort
    sort = 2
    SortOption.entryconfigure(3,command=ASort, image='')
    SortOption.entryconfigure(4,command='', image=tick)
    pathChange()

top = ''
sort = 1  # default
TYPE = IntVar()

# String variables
newFileName = StringVar(root, "File.dot", 'new_name')
currentPath = StringVar(
    root,
    name='currentPath',
    value=pathlib.Path.cwd()
)
# Bind changes in this variable to the pathChange function
currentPath.trace('w', pathChange)

Button(root, text='Folder Up', command=goBack).grid(
    sticky='NSEW', column=0, row=0
)
# Keyboard shortcut for going up
root.bind("<Alt-Up>", goBack)
Entry(root, textvariable=currentPath).grid(
    sticky='NSEW', column=1, row=0, ipady=10, ipadx=10
)
scrollbar = ttk.Scrollbar(root, orient= 'vertical')
# List of files and folder
alist = Listbox(root, yscrollcommand = scrollbar.set) # height = 4)
alist.grid(sticky='NSEW', column=1, row=1, ipady=10, ipadx=10)
# List Accelerators
alist.bind('<Double-1>', changePathByClick)
alist.bind('<Return>', changePathByClick)
alist.bind('<Button-3>', rightClick)
scrollbar.config(command= alist.yview)


# Menu
menubar = Menu(root)
# Adding a new File button
menubar.add_command(label="Home", command=open_popup)
# menubar.entryconfigure(1,label='mododia',command=open_popup, image=new_file_img)  # changes first menu option

# do this for item selected stuff

SettingsOption = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Settings", menu=SettingsOption)
SettingsOption.add_command(label="Help", command=None)
SettingsOption.add_command(label="Documentation", command=None)
SettingsOption.add_separator()
SortOption = Menu(SettingsOption, tearoff=False)
SettingsOption.add_cascade(label="Sort", menu=SortOption)

# Load the image
tick = PhotoImage(file="tick.png")
w = int(round(0.01098096632 * sWidth))
h = int(round(0.01953125 * sHeight))
print(sWidth, sHeight)
print(w,h)

SortOption.add_command(label="Name")
SortOption.add_command(label="Type")
SortOption.add_separator()
SortOption.add_command(label="Accending", command='', image=tick, compound='left')
SortOption.add_command(label="Descending", command=BSort, compound='left')

menubar.add_command(label="Add File or Folder", command=open_popup)
menubar.add_command(label="Refresh", command=pathChange)
# Adding a quit button to the Menubar
menubar.add_command(label="Quit", command=quit) # root.quit
# Make the menubar the Main Menu
root.config(menu=menubar)

rm = Menu(root, tearoff=0)
rm.add_command(label="Cut")
rm.add_command(label="Copy", command=fcopy)
rm.add_command(label="Paste", command=fpaste)
rm.add_command(label="Refresh", command=pathChange)
rm.add_separator()
rm.add_command(label="Delete", command=fdelete)
rm.add_command(label="Rename", command=frename)
rm.add_separator()
rm.add_command(label="Properties")

# Call the function so the list displays
pathChange('')
# run the main program
Label(root, text='').grid(pady=6)
root.mainloop()
