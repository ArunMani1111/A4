#! /usr/bin/env python3

from numpy import linalg
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import numpy as np
import logging
from collections import OrderedDict
import os
import pickle
import json

import config
from utils import xy_array
from segmentation import Segmentation


def interface():

    root = Tk()
    frame = Frame(root)

    # Choose image
    img_path = askopenfilename(parent=root, title='Select an image.')
    img_name = os.path.splitext(os.path.basename(img_path))[0]
    print(f'opening image {img_path}')
    image = Image.open(img_path)
    wd, ht = image.size
    resized_img = image.resize((int(config.MAX_INTERFACE_h*wd/ht), config.MAX_INTERFACE_h))

    tk_image = ImageTk.PhotoImage(resized_img)
    ht, wd = tk_image.ht(), tk_image.wd()

    # Build canvas
    canvas = Canvas(frame, wd=wd+100, ht=ht+100)
    canvas.grid()
    frame.pack()
    beta_entry = Entry(root)
    beta_entry.pack()
    beta_entry.insert(0, 'Beta parameter')

    canvas.create_image(0, 0, image=tk_image, anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))

    img_arr = xy_array(np.array(resized_img))

    save_segmentation = IntVar()
    save_segmentation_button = Checkbutton(
        root, text="Save segmentation", var=save_segmentation)
    save_segmentation_button.pack()

    draw_cont = IntVar()
    draw_contours_button = Checkbutton(
        root, text="Draw contours", var=draw_cont)
    draw_contours_button.pack()

    # Button-called functions

    def on_solve():
        beta_parameter = float(beta_entry.get())
        segmentation = Segmentation(
            img_arr, beta_parameter, seeds, img_name)

        segmentation.solve()

        if save_segmentation.get():
            segmentation.build_segmentation_image()
            segmentation.save_seg_img()

        if draw_cont.get():
            segmentation.plot_contours()

        segmentation.build_segmentation_image()
        segmentation.plot_colours()

    def save_seeds():
        seeds_file_name = f'{img_name}_{len(seeds.keys())}_seeds.pickle'
        seeds_file_path = os.path.join(config.SEEDS_PATH, seeds_file_name)
        print(f'Saving seeds to {seeds_file_path}')
        with open(seeds_file_path, 'wb') as pickle_file:
            pickle.dump(seeds, pickle_file)

    # Set buttons
    
    solve_button = Button(root, text="Solve", command=on_solve)
    solve_button.pack()

    save_seeds_button = Button(root, text="Save seeds", command=save_seeds)
    save_seeds_button.pack()

    solve_button.pack()

    colours_list = Listbox(root)
    colours_list.pack()
    for col in config.COLOURS_DIC.keys():
        colours_list.insert(END, col)

    # Initialize variables
    seeds = OrderedDict()
    CURRENT_COLOUR = StringVar()
    seed_ovals = []

    # Interface operations
    def add_seed(event):
        if not CURRENT_COLOUR.get():
            print('No colour selected!')
            return
        x, y = canvas_coords(event, canvas)
        seeds.update({
            (x, y): CURRENT_COLOUR.get()
        })
        last_seed = canvas.create_oval(x-config.OVAL_SIZE/2, y-config.OVAL_SIZE/2, x+config.OVAL_SIZE/2, y +
                                       config.OVAL_SIZE/2, wd=2, fill=CURRENT_COLOUR.get())
        seed_ovals.append(last_seed)
        print(f'New {CURRENT_COLOUR.get()} seed added : {[x,y]}')

    def rem_seed(event):
        seeds.pop(next(reversed(seeds)))
        canvas.delete(seed_ovals.pop(len(seed_ovals) - 1))

    def sel_col(event):
        CURRENT_COLOUR.set(colours_list.get(colours_list.curselection()))
        print(f'current colour = {CURRENT_COLOUR.get()}')

    canvas.bind("<ButtonPress-1>", add_seed)
    canvas.bind("<ButtonPress-2>", rem_seed)
    colours_list.bind("<<ListboxSelect>>", sel_col)
    solve_button.bind

    root.mainloop()

# Transform event coordinates into canvas coordinates
def canvas_coords(event, canvas):
    return (canvas.canvasx(event.x), canvas.canvasy(event.y))


if __name__ == "__main__":
    interface()
