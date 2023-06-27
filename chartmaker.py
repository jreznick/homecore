#Anaconda 3 Python 
from math import pi
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path

from .__env__ import PATH_CHART


class ChartMaker:
	def __init__(self, title, data, ax_labels=None, color=None):
		#Set plot settings
		fig_size = plt.rcParams["figure.figsize"]
		fig_size[0] = 10
		fig_size[1] = 8
		plt.rcParams["figure.figsize"] = fig_size
		plt.rcParams['axes.spines.left'] = False
		plt.rcParams['axes.spines.right'] = False
		plt.rcParams['axes.spines.top'] = False
		plt.rcParams['axes.spines.bottom'] = False
		self.title = title
		self.data = data
		self.labels = list(data.keys())
		self.values = list(data.values())
		file_part = title.replace(' ','').lower()
		file_name = f'{file_part}.png'
		self.chart_path = PATH_CHART / file_name
		self.fig, self.ax = plt.subplots()
		self.ax.set_title(title)
		self.color = color
		plt.ylim(0,3000)
		if ax_labels != None:
			self.xlabel = ax_labels['xlabel']
			self.ylabel = ax_labels['ylabel']
		else:
			self.xlabel = ''
			self.ylabel = ''

	def __str__(self):
		return f'<{self.__class__.__name__}:{self.title}:{self.chart_path}>'

	def plot_style(self):
		self.ax.set_facecolor("grey")
		self.ax.set_axisbelow(True)
		self.ax.yaxis.grid(linestyle='-', linewidth='0.3', color='white')
		plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=30))
		plt.gcf().autofmt_xdate()
		plt.xlabel(self.xlabel)
		plt.ylabel(self.ylabel)

	def pie(self):
		explode = (0, 0, 0, 0)
		self.ax.pie(self.values, explode=None, labels=self.labels, autopct='%1.1f%%',
				shadow=False, startangle=90)
		self.ax.axis('equal')
		self.close()

	def donut(self):
		self.fig, self.ax = plt.subplots(figsize=(10, 8), 
										subplot_kw=dict(aspect="equal"))
		wedges, texts = self.ax.pie(self.values, labels=self.labels, 
			wedgeprops={ 'linewidth' : 7, 'edgecolor' : 'white' }, startangle=90)
		my_circle = plt.Circle( (0,0), 0.7, color='white')
		p = plt.gcf()
		p.gca().add_artist(my_circle)

		self.close()

	def line(self):
		self.ax.plot(self.labels, self.values, marker=".")
		plt.xticks(rotation=45)
		plt.xlabel(self.xlabel)
		self.plot_style()
		self.close()

	def dot(self):
		self.ax.scatter(self.labels, self.values)
		self.plot_style()
		self.close()

	def bar(self):
		self.ax.bar(self.labels, self.values)
		y_pos = np.arange(len(self.labels))
		if self.color is not None:
			plt.bar(y_pos, self.values, color=self.color)
		plt.xticks(rotation=45)
		self.plot_style()
		self.close()

	def barh(self):
		#swap axes
		temp_y = self.xlabel
		temp_x = self.ylabel
		self.y_label = temp_y
		self.x_label = temp_x
		y_pos = np.arange(len(self.labels))
		self.ax.barh(self.labels, self.values)
		if self.color is not None:
			plt.barh(y_pos, self.values, color=self.color)
		self.ax.set_yticks(y_pos)
		self.ax.set_yticklabels(self.labels)
		self.ax.invert_yaxis()
		self.plot_style()
		self.close()
		#put axes back
		temp_y = self.xlabel
		self.ylabel = temp_y
		temp_x = self.ylabel
		self.xlabel = temp_x

	def close(self):
		plt.savefig(self.chart_path, bbox_inches = "tight", format='png')
		plt.clf()
		plt.close(self.fig) 
