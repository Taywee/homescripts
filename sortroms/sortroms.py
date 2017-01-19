#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

from os.path import splitext
import argparse
import os
import re

BADCHARS = re.compile(r'[^\-\w]')
REGIONSET = re.compile(r'\(([A-Z]+)\)')
TAG = re.compile(r'[\(\[]([^\)\]]+)[\]\)]')
VERSION = re.compile(r'[vV](\d+(:?\.\d+)*)')
HACK = re.compile(r'\bhack\b', flags=re.IGNORECASE)
GOODTAG = '[!]'

class RomFile(object):
	def __init__(self, filename):
		self.filename = filename
		self.dirname = os.path.dirname(filename)
		self.basename = os.path.basename(filename)

		root, ext = splitext(self.basename)
		self.root = root
		self.ext = ext

		self.title = TAG.sub('', REGIONSET.sub('', root)).replace(GOODTAG, '').strip()

		regionmatch = REGIONSET.search(root)
		self.regions = frozenset(regionmatch.group(1)) if regionmatch else frozenset()

		versionmatch = VERSION.search(root)
		self.version = tuple(int(number) for number in versionmatch.group(1).split('.') if number) if versionmatch else tuple()

		self.hack = bool(HACK.search(root))
		self.tags = frozenset(TAG.findall(root))
		self.good = GOODTAG in root
	
	def rename(self):
		goodname = BADCHARS.sub('', self.title)
		newfilename = os.path.join(self.dirname, goodname + self.ext)
		print("renaming »{old}« to »{new}«".format(old=self.filename, new=newfilename))
		os.rename(self.filename, newfilename)
		self.filename = newfilename
		self.basename = os.path.basename(newfilename)

	def delete(self):
		print("DELETING »{file}«".format(file=self.filename))
		os.remove(self.filename)

def main():
	parser = argparse.ArgumentParser(description='Rename relevant roms and delete unwanted ones from other regions')
	parser.add_argument('-g', '--only-good', action='store_true', help='Only keep good roms')
	parser.add_argument('-H', '--keep-hacks', action='store_true', help='Keep hacks roms')
	parser.add_argument('-e', '--ext', help='The file extension to process.  Other files are ignored.')
	parser.add_argument('-r', '--regions', help='Preferred region order.  Top order will be most likely to be kept.', default='UEJ')
	parser.add_argument('dir', help='The directory to scan for rom files')
	args = parser.parse_args()

	ext = args.ext.strip('.').lower() if args.ext else None
	regionorder = args.regions

	games = dict()

	for filename in os.listdir(args.dir):
		if ext:
			root, gext = splitext(filename)
			if gext.strip('.').lower() != ext:
				continue
		file = RomFile(filename)

		if not file.title in games:
			games[file.title] = []

		games[file.title].append(file)
	
	for title, gamelist in games.items():
		# Key sort for 
		def regionsort(game):
			for region in regionorder:
				if region in game.regions:
					return regionorder.find(region)
			return len(regionorder)

		# Sorts are done by least important to most important
		# sort by version
		gamelist.sort(key=lambda game: game.version, reverse=True)
		# sort by region
		gamelist.sort(key=regionsort)
		# Then sort by hackiness
		gamelist.sort(key=lambda game: 1 if game.hack else 0)
		# Then sort by goodness
		gamelist.sort(key=lambda game: 0 if game.good else 1)

		first = gamelist[0]
		if args.only_good and not first.good:
			first.delete()
		elif first.hack and not args.keep_hacks:
			first.delete()
		else:
			first.rename()

		for game in gamelist[1:]:
			game.delete()

if __name__ == '__main__':
	main()
