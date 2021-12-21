import tkinter as tk
from PIL import ImageTk, Image
import glob
import random
import os
import shutil
import argparse
import sys
from tkinter import filedialog as fd


class CreateDisplay:
    def __init__(self, master, save_dir, images, current_image, classes="good", mode="save"):
        self.master = master
        self.count = 0
        self.save_dir = save_dir
        self.current_image = current_image
        self.images = images
        self.mode = mode
        self.classes = classes

        self.col = len(self.classes)
        self.display_image()

        buttons = [tk.Button(self.master, text=self.classes[i], command=lambda i=i: self.change_image(self.classes[i])).grid(row=1, column=i) for i in range(self.col)]

    def change_image(self, class_):

        self.count += 1

        path = os.path.basename(self.current_image)

        if self.mode == "move":
            os.rename(self.current_image, self.save_dir + "/" + class_ + "/" + path)
        elif self.mode == "copy":
            shutil.copy(self.current_image, os.path.join(self.save_dir, class_, path)) 
        else:
            raise ValueError('Mode must be set to "move" or "copy"')
        
        try:
            self.current_image = self.images[self.count]
        except IndexError:
            print("No more images to process")
            sys.exit()
        
        self.display_image()

    def display_image(self):
        img = Image.open(self.current_image)
        img = img.resize((512, 512))
        self.img = ImageTk.PhotoImage(img)
        self.image = tk.Label(self.master, image=self.img)
        self.image.grid(row=0, columnspan=self.col)


class mainFrame:
    """
    First window which has a prompt for selecting a directory and setting how many classes you want and what to call them.
    """

    def __init__(self, master_frame):
        self.frame = tk.Frame(master=master_frame)
        self.classes = []
        self.src_dir = ''
        self.out_dir = ''

        # Title_frame
        title = 'Interactive labeling'
        frame_title = tk.Frame(master=self.frame)
        lbl_title = tk.Label(master=frame_title, text=title)
        lbl_title.config(font=('Georgia', 24))
        lbl_title.grid()

        # Button to select source dir
        frame_src = tk.Frame(master=self.frame)
        btn_src = tk.Button(master=frame_src,
                            text='select source dir',
                            width=24, height=2, fg='black')
        btn_src.grid(row=1, column=0)
        lbl_src = tk.Label(master=frame_src, text='no source directory')
        lbl_src.config(font=('Georgia', 24))
        lbl_src.grid(row=1, column=1)
        self.lbl_src = lbl_src
        btn_src.bind("<Button>",
                     lambda e: self.get_dir(e, 'src'))

        # Button to select output dir
        frame_out = tk.Frame(master=self.frame)
        btn_out = tk.Button(master=frame_out,
                            text='select output dir',
                            width=24, height=2, fg='black')
        btn_out.grid(row=2, column=0)
        lbl_out = tk.Label(master=frame_out, text='no output directory')
        lbl_out.config(font=('Georgia', 24))
        lbl_out.grid(row=2, column=1)
        self.lbl_out = lbl_out
        btn_out.bind("<Button>", 
                     lambda e: self.get_dir(e, 'out'))
        
        # input class names
        self.frame_classes = tk.Frame(master=self.frame)
        self.frame_subtitle = tk.Label(master=self.frame_classes, text='class names')
        self.frame_subtitle.grid(row=1, column=0, sticky='w')
        self.add_row()

        # Button add row to classes
        frame_row = tk.Frame(master=self.frame)
        btn_addrow = tk.Button(master=frame_row,
                               text='add class',
                               width=24, height=2, fg='black')
        btn_addrow.bind("<Button>", lambda e: self.add_row())
        btn_rmvrow = tk.Button(master=frame_row,
                               text='rmv class',
                               width=23, height=2, fg='black')
        btn_rmvrow.bind("<Button>", lambda e: self.rmv_row())
        btn_addrow.grid(row=0, column=0)
        btn_rmvrow.grid(row=0, column=1)

        # Button to start labelling.
        frame_start = tk.Frame(master=self.frame)
        self.btn_start = tk.Button(master=frame_start,
                                text='start labelling',
                                width=24, height=2, fg='red')
        self.btn_start.pack(side=tk.LEFT)
        self.btn_start.bind("<Button>", self.start)

        # Grid all the sub frames
        frame_title.grid(row=0, column=0)
        frame_src.grid(row=1, column=0)
        frame_out.grid(row=2, column=0)
        self.frame_classes.grid(row=3, column=0)
        frame_row.grid(row=4, column=0)
        frame_start.grid(row=5, column=0)
        self.frame.grid(row=0, column=0)


    def get_dir(self, event, attr):
        """
        open an askdirectory window and write to label the path of the directory chosen.
        """
        setattr(self, f'{attr}_dir', fd.askdirectory(mustexist=True))
        val = getattr(self, f'{attr}_dir')
        lbl = getattr(self, f'lbl_{attr}')
        lbl.config(text=f'Directory: {val}')
        if self.out_dir:
            self.btn_start.config(fg='green')


    def start(self, event):
        save_dir = self.out_dir

        all_images = [os.path.join(self.src_dir, p) for p in os.listdir(self.src_dir)]

        print("Shuffling")
        random.shuffle(all_images)
        CURR_IMG = all_images[0]

        classes = []
        for class_ent in self.classes:
            classes.append(class_ent.get())
        for c in classes:
            if not os.path.exists(save_dir + "/" + c):
                os.mkdir(save_dir + "/" + c)

        print("Creating GUI")
        
        window = tk.Toplevel(master=self.frame)
        CreateDisplay(window, save_dir, all_images, CURR_IMG, classes=classes, mode='copy')
        return window 

    def add_row(self):
        frame_class = tk.Frame(master=self.frame_classes)
        txt = tk.Entry(master=frame_class, width=50)
        txt.grid(row=1, column=0, sticky='w')
        frame_class.grid(column=0, sticky='w')
        self.classes.append(txt)
        return

    def rmv_row(self, min=2):
        if len(self.frame_classes.children) > min:
            self.frame_classes.children[
                list(self.frame_classes.children.keys())[-1]].grid_forget()
            self.frame_classes.children[
                list(self.frame_classes.children.keys())[-1]].destroy()
            to_rm = self.classes.pop()
            to_rm.destroy()
        return


def main(args):
    root = tk.Tk()
    mainFrame(root)
    root.mainloop()


if __name__ == "__main__":
    from sys import argv

    try:
        main(argv)
    except KeyboardInterrupt:
        pass
    sys.exit()
