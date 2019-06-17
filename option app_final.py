import tkinter as tk
from tkinter import *
from tkinter import ttk
from yahoo_fin import options
import matplotlib
from matplotlib import style
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import matplotlib.animation as animation
from matplotlib import style

import urllib
import json

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt


LARGE_FONT=("Verdana",12)
NORM_FONT=("Verdana",10)
SMALL_FONT=("Verdana",8)

style.use("ggplot")

# to automatically scale the figure

f = Figure()
a=f.add_subplot(111)


# define popup masg
def popupmsg(msg):
    popup=tk.Tk()

    def leavemini():
        popup.destroy()
    
    popup.wm_title("!")
    label = ttk.Label(popup,text=msg,font=NORM_FONT)
    label.pack(side='top',fill='x',pady=10)
    B1 = ttk.Button(popup,text='Okay',command = leavemini)
    B1.pack()
    popup.mainloop()




# clean data
def clean(data):
    calls=data['calls']
    puts=data['puts']
    calls['Last Trade Date']=pd.to_datetime(calls['Last Trade Date'], infer_datetime_format=True)
    puts['Last Trade Date']=pd.to_datetime(puts['Last Trade Date'], infer_datetime_format=True)

    datestamp=[]
    for i in calls['Last Trade Date']:
        datestamp.append(i.strftime('%m-%d'))
    calls['date']=datestamp    

    datestamp2=[]
    for i in puts['Last Trade Date']:
        datestamp2.append(i.strftime('%m-%d'))
    puts['date']=datestamp2

    implied_volatility=[]
    for i in calls['Implied Volatility']:
        implied_volatility.append(float(i.strip('%')))
        
        
    calls['implied volatility']=implied_volatility


    implied_volatility2=[]
    for i in puts['Implied Volatility']:
        implied_volatility2.append(float(i.strip('%')))
        
        
    puts['implied volatility']=implied_volatility2
    return(calls,puts)






class optioncrawler(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)

        tk.Tk.iconbitmap(self,default='oreo.ico')
        tk.Tk.wm_title(self,'Option Data Searcher')
        
        container=tk.Frame(self)
        container.pack(side='top',fill='both',expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        # create menu
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar,tearoff=0)
        filemenu.add_command(label="Save settings",command = lambda:popupmsg("Not supported just yet!"))
        filemenu.add_separator()
        filemenu.add_command(label='Exit',command=quit)
        menubar.add_cascade(label='File',menu=filemenu)


        tk.Tk.config(self,menu=menubar)
        

        

        self.frames = {}

        for F in (StartPage,Summary_Page):
            
            frame = F(container,self)

            self.frames[F]=frame
            frame.grid(row=0,column=0,sticky='nsew')
            #nsew is north south east west, it will strach all window
        self.show_frame(StartPage)

    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()

def qf(stringtoprint):
    print(stringtoprint)


class StartPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text=("""ALPHA Bitcon trading application.There is no promise
                                of  warranty."""),font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        #button1=tk.Button(self,text="Visit Page 1",command=qf("yoyoyo"))
        # this action will not happen after you click it. we will use lambda instead
        button1=ttk.Button(self,text="Agree",
                          command=lambda:controller.show_frame(Summary_Page))
        button1.pack()
        button2=ttk.Button(self,text="Disagree",
                          command=quit)
        button2.pack()


class Summary_Page(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Summary_Page",font=LARGE_FONT)
        label.grid(column=3,row=0)
        button1=ttk.Button(self,text="Back to Home",
                          command=lambda:controller.show_frame(StartPage))
        button1.grid(column=4,row=1)

        lbl=Label(self,text="Option Ticker",font=NORM_FONT)
        lbl.grid(column=1,row=1)

        txt=Entry(self,width=10)
        txt.grid(column=2,row=1)
        txt.focus()

        # summary data
        def search():
            data=clean(options.get_options_chain(txt.get()))
            calls=data[0]
            puts=data[1]

            last_put_date=puts['Last Trade Date'].iloc[-1]
            last_call_date=calls['Last Trade Date'].iloc[-1]
            last_put_price=puts['Strike'].iloc[-1]
            last_call_price=calls['Strike'].iloc[-1]
            total_put_volume_three_days=sum(puts['Volume'][puts['Last Trade Date']>=puts['Last Trade Date'][0]-timedelta(days=3)])
            total_call_volume_three_days=sum(calls['Volume'][calls['Last Trade Date']>=calls['Last Trade Date'][0]-timedelta(days=3)])
            average_put_implied_volatility_three_days=str(round(np.mean(puts['implied volatility'][puts['Last Trade Date']>=puts['Last Trade Date'][0]-timedelta(days=3)]),2))+"%"
            average_call_implied_volatility_three_days=str(round(np.mean(calls['implied volatility'][calls['Last Trade Date']>=calls['Last Trade Date'][0]-timedelta(days=3)]),2))+"%"


            indexs=['Last Put Date','Last Call Date','Last Put Price','Last Call Price',
                   'Total Put Volume in Last Three days','Total Call Volume in Last Three days',
                   'Average Put Implied Volatility in Last Three days','Average Call Implied Volatility in Last Three days']
            values=[last_put_date,last_call_date,last_put_price,last_call_price,total_put_volume_three_days,
                   total_call_volume_three_days,average_put_implied_volatility_three_days,
                   average_call_implied_volatility_three_days]
            summary=pd.DataFrame()
            summary['Indexes']=indexs
            summary['Values']=values

            frame=tk.Text(self)
            frame.delete(1.0,tk.END)
            frame.insert(tk.END,summary)
            frame.grid(column=1,row=2)


        button2=ttk.Button(self,text='Search',
                           command=search)
        button2.grid(column=3,row=1,columnspan=4)

        
app=optioncrawler()
# interval indicated the interval to update graph, 1000 millieseconds = 1 second

app.mainloop()

 

        
        
    
