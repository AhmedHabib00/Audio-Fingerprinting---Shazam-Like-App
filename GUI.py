# IMPORTS
import functools
import os
from tkinter import *
from tkinter import Button, ttk
import tkinter as tk
from tkinter.filedialog import askopenfilename
from SongClass import SongClass,all_songs_data,processed_songs
from tkinter import messagebox

# ~ IMPORTS
width=height=0

counter=0
songs = []

directory = 'Songs'
for filename in os.scandir(directory):
    if filename.is_file():
        all_songs_data.append(filename)
        songs.append(SongClass(counter))
        songs[counter].fingerprint()
        counter+=1
        print(len(processed_songs))

# ------------------------------------------------------------------------------------------------
class GUI:
    def __init__(self,window):

        self.framesong1 = tk.Frame(master=window,highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.frameoutput = tk.Frame(master=self.framesong1,highlightbackground="black", highlightcolor="black", highlightthickness=2)


        self.add_song_img = PhotoImage(file='addsong.png')
        self.mixer_img = PhotoImage(file='mixer.png')
        self.browse = PhotoImage(file='addsong.png')

        self.addimgres = self.add_song_img.subsample(15, 15)
        self.mixerimgres = self.mixer_img.subsample(15, 15)
        self.open_file = self.browse.subsample(15, 15)

        window.title('Audio Fingerprint')

        self.framesong1.place(height=590, width=1090, x=5, y=5)
        self.framesong1.config(background="white")

        self.frameoutput.place(height=150, width=600, x=200, y=60)
        self.frameoutput.config(background="white")

        # GUI
        self.songlistlabel = Label(self.framesong1, text='Song List', fg='black', underline=True, font=(30))
        self.songlistlabel.place(x=500, y=5)
        ##########################Song 1 Info###################################
        self.Browsebutton1 = Button(self.framesong1, text='Open',command=functools.partial(self.load,x=0)) #image=self.addimgres
        self.Browsebutton1.place(x=450, y=300)
        ##########################Song 2 Info###################################
        self.Browsebutton2 = Button(self.framesong1,text='Open' ,command=functools.partial(self.load,x=1)) #image=self.addimgres
        self.Browsebutton2.place(x=500, y=300)

        ##########################Mixer info###################################
        self.mixer_button = Button(self.framesong1,text='Mix' ,command=self.search) #image=self.mixerimgres
        self.mixer_button.place(x=600, y=300)

        self.slider = Scale(self.framesong1, from_=0, to=100, background='white', orient=HORIZONTAL, length=300)
        self.slider.place(x=350, y=240)
        self.similarity = []
        ##########################Frame Output###################################
        self.c = 0


    def clear_tree(self):
        self.my_tree.delete(*self.my_tree.get_children())
    def load(self,x):

        filename = askopenfilename()
        all_songs_data.append(filename)
        if x==0:
            self.song1 = SongClass(-1)
            self.c+=1
            self.selected = 1
        if x==1:
            self.song2 = SongClass(-1)
            self.c+=1
            self.selected = 2
        all_songs_data.pop(-1)

    def search(self):
        self.frameoutput.destroy()
        if self.c <1:
            messagebox.showerror("Error!", "Please select two images first.")
        else:
            if self.selected ==1:
                self.Songs = self.song1.mix(self.song2,self.slider.get())
            elif self.selected ==2:
                self.Songs = self.song2.mix(self.song1,self.slider.get())
            print('songs: ',self.Songs)
            self.display(self.Songs)
    def display(self,df):
        self.frameoutput = tk.Frame(master=self.framesong1,highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.frameoutput.place(height=150, width=600, x=200, y=60)
        self.frameoutput.config(background="white")
        columns = ('#1','#2','#3')
        self.my_tree = ttk.Treeview(self.frameoutput,columns=columns,show='headings')
        data = df
        self.total_rows = df.shape[0]
        self.total_columns = df.shape[1]
        c=1
        for col in list(data.columns.values):
            self.my_tree.heading(f'#{c}', text = col)
            c+=1

        data_rows = data.to_numpy().tolist()
        for row in data_rows:
            self.my_tree.insert("", "end", values = row)
        self.frameoutput.update()
        self.my_tree.pack()
        self.my_tree = None
