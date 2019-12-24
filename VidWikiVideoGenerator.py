# Tkinter package for provoding graphical interface
import tkinter as tk
from tkinter import ttk

# Regex package (used it for pattern matching, splitting and cleaning data)
import re

from datetime import datetime

# Test to  speech module
import tts.sapi

# Importing moviepy package (used to produce video)
from moviepy.editor import *

# Package used for finding the durations of sound files
import soundfile as sf

# Os package to check and create directories
import os

# Packages used for obtaining get web data and do web scraping
import requests
from bs4 import BeautifulSoup

# Importing ordered dictionary module to store information in a sequential and meaningful way
from collections import OrderedDict 

# Package to apply text wrapping to a string
import textwrap

import urllib.request

import json
import math

import timeit

root = tk.Tk()

# Setting up TTS
voice = tts.sapi.Sapi()
voice.set_voice(voice.get_voices()[0])
# voice.set_rate(0)

audioClipCount = 0
overlay_image = "Resources/blackTransparentOverlay.png"

audio_list = []

clip_list = []

# Variables for fetching web page
req = ""
soup = ""

# Making an ordered dictionary object and related variables
od = OrderedDict() 
currMainHeading = ""
currSubHeading = ""

imagesUsed = []
imageClipCount = 0

mainImageFilename = ""

# Function to convert hex color to rgb tuple
def rgbFromHex(hexValue):
	hexValue = hexValue[1:]
	return tuple(int(hexValue[i:i+2], 16) for i in (0, 2, 4))

# The list of colors to use for different sections
# colorPallete = ["#05668d","#028090","#00a896","#02c39a","#f0f3bd"]
colorPallete = ["#05668d","#028090","#00a896","#02c39a"]
colorPallete = [rgbFromHex(color) for color in colorPallete]

wrapper = textwrap.TextWrapper(width=58)

logoClip = ImageClip("Resources/vidWikiLogo.png").set_pos((1125, 635))

# Function to remove substrings of the form [0-9]+ from paragraph
def makeStringCleaner(s):
	s = re.sub("\[[0-9]+\]", "", s)
	return s

# Function to remove substrings of the form \[edit\] from a heading
def makeHeadingCleaner(s):
	s = re.sub("\[edit\]", "", s)
	return s

def getImageExentsion(string):
	extension = re.search("[.][a-zA-Z]+$", string).group(0)[1:]
	return extension

# Function which cleans up and splits up a paragraph into lines
def paragraphProcessing(ph):
	ph = makeStringCleaner(ph)
	ph = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', ph)
	ph = [line for line in ph if line]
	return ph

# Function to obtain the introduction (the topmost paragraph) from a wiki page
def get_introduction():
	global soup

	Introduction = []

	p = soup.find_all('p')
	for l in p:
		if len(l.find_parents('table'))>0:
			continue
		else:
			p = l
			break
	
	while p.next_sibling:
		
		if(p.name==None):
			p = p.next_sibling
			continue

		if p.name=="p" and p.get('class')==None:
			Introduction += [paragraphProcessing(p.text)]

		if p.name=="div" and ('toc' in p.get('class')):
			break

		p = p.next_sibling

	return Introduction

# Function to create the project folder and the required subfolders
def createProjectFolders(filename):
	if not os.path.exists("Productions\\" + filename):
		os.makedirs("Productions\\" + filename + "\\images")
		os.makedirs("Productions\\" + filename + "\\audioClips")

# Function to calculate the duration of a sound clip (using the soundfile package)
def getClipDuration(clipName):
	f = sf.SoundFile(clipName)
	# return round((len(f)/f.samplerate),1)
	return math.ceil(len(f)/f.samplerate)

# Function to generate the filename of the video (using the specified URL)
def generateFileName():
	fileName = re.search(r"(/[a-zA-Z0-9-_()]+?)[.]*$" , pageUrlEntry.get())
	try:
		fileName = fileName.group(1)[1:]
		return fileName
	except:
		now = datetime.now().strftime("%H-%M-%S")
		return ("Video_" + now)

# Functions to divide paragraphs into appropriate sized chunks for proper presentation
def giveNumbers(number):
	lst = []
	while number>0:
		if number<=5:
			lst.append(number)
			number = 0
		elif number==6:
			lst.append(3)
			lst.append(3)
			number = 0
		elif number==7:
			lst.append(4)
			lst.append(3)
			number = 0
		elif number>7:
			lst.append(5)
			number -= 5
	return lst

def paragraphsOrganisation(data):
	newData = []
	for splittedPh in data:
		lst = giveNumbers(len(splittedPh))
		pos = 0
		for number in lst:
			newData += [' '.join(splittedPh[pos:pos+number])]
			pos += number
	return newData

def imagesOrganisation(noOfParas, imagesList):
	imagesToUse = []
	try:
		lenImages = len(imagesList)
		lst = [noOfParas // lenImages + (1 if x < noOfParas % lenImages else 0)  for x in range (lenImages)]
		for i in range(len(lst)):
			imagesToUse += [imagesList[i]]*lst[i]
	except:
		pass
	return imagesToUse

def saveImageFromUrlAndReturnFileName(url, filename):
	global imageClipCount
	imagesUsed.append(url)
	# filename = str(imageClipCount) + "." + getImageExentsion(url)
	filePath = "Productions\\{}\\images\\image{}.{}".format(filename, str(imageClipCount), getImageExentsion(url))
	urllib.request.urlretrieve(url, filePath)
	imageClipCount += 1
	return filePath

# Function to produce audio clip from the provided text using the Sapi TTS package
def createAudioFile(text, filename):
	global audioClipCount
	filePath = "Productions\\{}\\audioClips\\clip{}.wav".format(filename, str(audioClipCount))
	voice.create_recording(filePath, text)
	audioClipCount += 1
	return filePath

def cleanWikipediaImageURL(url):
	url = "http:" + url[:url.rfind('/')]
	url = url.replace("/thumb",'')
	return url

def scrapeDataFromWikiPageAndStoreIt(pageName):
	global soup
	global imageClipCount
	global mainImageFilename

	req = requests.get(pageUrlEntry.get())
	soup = BeautifulSoup(req.text, "lxml")

	od["Introduction"] = OrderedDict()
	od["Introduction"]["text"] = get_introduction()
	h = soup.find_all('h2')
	curr = h[1]

	try:
		infobox = soup.find_all("table", {"class": "infobox"})[0]
		infoboxImageURL = cleanWikipediaImageURL((infobox.find_all("img")[0]).get("src"))
		mainImageFilename = saveImageFromUrlAndReturnFileName(infoboxImageURL, pageName)
		od["Introduction"]["image"] = [mainImageFilename]
	except:
		od["Introduction"]["image"] = []
		print("No infobox")

	currMainHeading = makeHeadingCleaner(curr.text)

	od[currMainHeading] = OrderedDict()
	currSubHeading = "Introduction"
	od[currMainHeading][currSubHeading] = OrderedDict()
	od[currMainHeading][currSubHeading]["text"] = []
	od[currMainHeading][currSubHeading]["images"] = []

	# Storing the main content in an Ordered Dictionary  
	while curr.next_sibling:

		curr = curr.next_sibling

		if(curr.name==None):
			continue

		if curr.get('class')!=None:
			if('thumb' in curr.get('class')):
				try:
					containedImageURL = cleanWikipediaImageURL((curr.find_all("img")[0]).get("src"))
					imageFileName = saveImageFromUrlAndReturnFileName(containedImageURL, pageName)
					od[currMainHeading][currSubHeading]["images"].append(imageFileName)
				except Exception as e:
					print(e, "No image inside thumb div found.")

		if(curr.name=="h2"):
			currMainHeading = makeHeadingCleaner(curr.text)
			od[currMainHeading] = OrderedDict()
			currSubHeading = "Introduction"
			od[currMainHeading][currSubHeading] = OrderedDict()
			od[currMainHeading][currSubHeading]["text"] = []
			od[currMainHeading][currSubHeading]["images"] = []

		if(curr.name=="h3"):
			currSubHeading = makeHeadingCleaner(curr.text)
			od[currMainHeading][currSubHeading] = OrderedDict()
			od[currMainHeading][currSubHeading]["text"] = []
			od[currMainHeading][currSubHeading]["images"] = []

		if(curr.name=="p"):
			od[currMainHeading][currSubHeading]["text"] += [paragraphProcessing(curr.text)]

def makeSlideClip(bodyText, head_clip, background_clip, filename, imgs):
	global logoClip
	counter = 0

	for fPara in bodyText:

		fPara = wrapper.fill(text=fPara)
		txt_clip = TextClip(fPara, fontsize = 22, font="Montserrat-Regular", color = 'white', method="label", align="West").set_pos((40,150))

		audioFileCompletePath = createAudioFile(fPara.replace("\n"," "), filename)
		audioFileDuration = getClipDuration(audioFileCompletePath)

		try:
			if audioFileDuration!=None and audioFileDuration>0:
				head_clip.set_duration(audioFileDuration)
				background_clip.set_duration(audioFileDuration)
				txt_clip.set_duration(audioFileDuration)
				logoClip.set_duration(audioFileDuration)
				if len(imgs)>0:
					imgClip = ImageClip(imgs[counter]).set_pos((800,40)).resize(width=380)
					composite_clip = CompositeVideoClip([background_clip, head_clip, txt_clip, imgClip, logoClip], size=(1280,720)).set_duration(audioFileDuration)
				else:
					composite_clip = CompositeVideoClip([background_clip, head_clip, txt_clip, logoClip], size=(1280,720)).set_duration(audioFileDuration)
				composite_clip.audio = AudioFileClip(audioFileCompletePath)
				clip_list.append(composite_clip)
				counter += 1
				print("Successful")
		except Exception as e:
			print(e)
			print(len(bodyText),len(imgs),"There is an issue!")

def videoCoverClip(filename):
	# Making the video cover clip
	try:
		global mainImageFilename
		global logoClip

		videoTitle = filename.replace("_"," ")
		videoTitle = videoTitle.upper()
		
		print(videoTitle, filename)
		audioFileCompletePath = createAudioFile(videoTitle, filename)
		audioFileDuration = getClipDuration(audioFileCompletePath)

		wrapperForHeading = textwrap.TextWrapper(width=10)
		videoTitle = wrapperForHeading.fill(text=videoTitle)

		sideBox = ImageClip("Resources/sideBox.png").set_duration(3)
		# logoClip = logoClip.set_opacity(0.5)

		coverHeadingClip = TextClip(videoTitle, fontsize=72, font="Barlow-Black", color = 'white', method="label")
		xPos = (528-coverHeadingClip.w)/2
		coverHeadingClip = coverHeadingClip.set_pos((xPos,"center"))

		coverImage = ImageClip(mainImageFilename).set_pos((528,0)).set_duration(3)

		req = 1280-528

		if coverImage.w/coverImage.h <= (req/720):
			coverImage = coverImage.resize(width=req)
		else:
			coverImage = coverImage.resize(height=720)

		coverClip = CompositeVideoClip([coverImage,sideBox,coverHeadingClip,logoClip], size=(1280,720)).set_duration(3)
		coverClip.audio = AudioFileClip(audioFileCompletePath)
		clip_list.append(coverClip)
	except:
		print("Issue in making the cover clip")

# Main function which produces the video	
def produceVideo():

	start = timeit.default_timer()

	global audioClipCount
	global logoClip

	audioClipCount = 0
	subHeadingCounter = 0

	filename = generateFileName()
	print(filename)
	createProjectFolders(filename)
	scrapeDataFromWikiPageAndStoreIt(filename)

	videoCoverClip(filename)

	print("Done")

	for k,v in od.items():
		if k=="See also" or k=="Notes" or k=="References":
			break

		colorTuple = colorPallete[subHeadingCounter%4]
		background_clip = ColorClip(size=(1280,720), color=colorTuple)

		audioFileCompletePath = createAudioFile(k, filename)
		audioFileDuration = getClipDuration(audioFileCompletePath)

		wrapperForSectionHeading = textwrap.TextWrapper(width=20)
		sectionHeadingText = wrapperForSectionHeading.fill(text=k.upper())
		sectionHeadingClip = TextClip(sectionHeadingText, font="Montserrat-SemiBold", fontsize = 72, color = 'white', method="label").set_pos(("center","center")).set_duration(audioFileDuration)

		logoClip.set_duration(audioFileDuration)
		sectionHeadingFinalClip = CompositeVideoClip([background_clip, logoClip, sectionHeadingClip], size=(1280,720)).set_duration(audioFileDuration)
		sectionHeadingFinalClip.audio = AudioFileClip(audioFileCompletePath)

		clip_list.append(sectionHeadingFinalClip)

		try:
			
			for a, f in v.items():
				
				wrapperForSubHeading = textwrap.TextWrapper(width=35)
				subHeadingFinal = (" / ".join([k,a])).upper()
				subHeadingFinal = wrapperForSubHeading.fill(text=subHeadingFinal)
				head_clip = TextClip(subHeadingFinal, fontsize = 32, font="Montserrat-SemiBold", color = 'white', method="label", align="West").set_pos((40,40))
				subHeadingCounter += 1

				b = paragraphsOrganisation(f["text"])

				imgsClips = 0
				imgs = imagesOrganisation(len(b), f["images"])

				makeSlideClip(b, head_clip, background_clip, filename, imgs)

		except Exception as e:
			head_clip = TextClip("INTRODUCTION", fontsize = 32, font="Montserrat-SemiBold", color = 'white', method="label", align="West").set_pos((40,40))
			vText = paragraphsOrganisation(v["text"])
			imgs = imagesOrganisation(len(vText), v["image"])
			makeSlideClip(vText, head_clip, background_clip, filename, imgs)
			print(e)

	# Attributions Clip
	mediaAttributionsHeading = TextClip("MEDIA ATTRIBUTIONS", fontsize = 32, font="Montserrat-SemiBold", color = 'white', method="label", align="West").set_pos((40,40)).set_duration(3)
	textContentHeading = TextClip("Text:", fontsize = 28, font="Montserrat-SemiBold", color = 'white', method="label", align="West").set_pos((40,150)).set_duration(3)
	wikipediaLink = TextClip(pageUrlEntry.get(), fontsize = 20, font="Montserrat-Regular", color = 'white', method="label", align="West").set_pos((40,185)).set_duration(3)

	imagesHeading = TextClip("Images:", fontsize = 28, font="Montserrat-SemiBold", color = 'white', method="label", align="West").set_pos((40,215)).set_duration(3)
	
	for n in range(len(imagesUsed)):
		imagesUsed[n] = str(n+1) + ". " + imagesUsed[n]
	imagesLinkText = "\n".join(imagesUsed)
	imagesLink = TextClip(imagesLinkText, fontsize = 20, font="Montserrat-Regular", color = 'white', method="label", align="West").set_pos((40,250)).set_duration(3)

	attributionsClip = CompositeVideoClip([background_clip, mediaAttributionsHeading, textContentHeading, wikipediaLink, imagesHeading, imagesLink], size=(1280,720)).set_duration(3)
	clip_list.append(attributionsClip)
	# ------------------

	final_clip = concatenate(clip_list, method = "compose")
	final_clip.write_videofile("Productions\\{}\\{}.mp4".format(filename, filename+"_fVideo"), fps = 1, preset="ultrafast")
	
	# final_clip.write_videofile("{}\\{}.mp4".format(filename, filename+"_fVideo"), fps = 24, codec = 'libx264', threads=4)

	stop = timeit.default_timer()
	print('Time: ', stop - start)  

# Statements to make the GUI 
mainLabel = tk.Label(text="VidWiki Video Generator")
mainLabel.pack(padx=20, pady=(10,2.5))
pageUrlEntry = ttk.Entry(width=75)
pageUrlEntry.pack(padx=20, pady=5)
produceButton = ttk.Button(text="Produce Video", command=produceVideo)
produceButton.pack(padx=20, pady=(2.5,10))

root.mainloop()