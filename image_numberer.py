#!/usr/bin/env python3

# USAGE: E.g.,
#  ./image_numberer.py -s . -t new_slides -f ~/.fonts/open-sans/OpenSans-Regular.ttf

__usage_eg__ = """
./image_numberer.py -s ./src/ -t ./dst/ -f ~/.fonts/open-sans/OpenSans-Regular.ttf


convert \
	-fill black \
	-font "/home/landonb/.fonts/open-sans/OpenSans-Regular.ttf" \
	-stroke None \
	-pointsize 20 \
	-style Normal \
	-draw "text 100,100 \'0\'" \
	./src/003.01110.png ./dst/003.01110.png


"""

SCRIPT_VERSION = 0.1
SCRIPT_DESCRIPTION = 'Slideshow Image Numberer and Namerer'

import os
import sys

import argparse
import re
#import shutil
import subprocess
import time

try:
	import time_util
except ImportError:
	pass

SCRIPT_NAME = os.path.basename(__file__)

class Image_Numberer_CLI(argparse.ArgumentParser):

	def __init__(self, script_version=None, description=None, **kwargs):
		super(Image_Numberer_CLI, self).__init__(
			description=description or SCRIPT_DESCRIPTION,
			**kwargs)
		self.script_version = script_version or SCRIPT_VERSION
		# args is the namespace returned by ArgumentParser.parse.
		self.args = None
		# Time the whole task.
		self.time_0 = time.time()

	def done(self):
		try:
			print(
				'Finished. Your task ran in %s'
				% (time_util.time_format_elapsed(self.time_0),)
			)
		except:
			print(
				'Finished. Your task ran in %.2f secs.'
				% (time.time() - self.time_0,)
			)

	# CLI boilerplate.

	def parser_run(self):
		# Prepare the parser and parse and validate the CLI args.
		self.parser_prepare()
		self.parser_parse()
		self.arguments_validate()

	def parser_parse(self):
		# If we're a daemon, the option parser wouldn't look
		# past a double-dash, so deal with it before parsing.
		try:
			if (sys.argv[1] == '--'):
				del sys.argv[1]
		except IndexError:
			pass

		self.args = self.parse_args()
		# NOTE: parse_args halts execution if user specifies:
		#       (a) '-h', (b) '-v', or (c) unknown option.

	def arguments_validate(self):
		# Verify the args -- we need the db connection to check the stream.
		ok = self.parser_verify()
		if not ok:
			#print('Unrecoverable errors detected. See prior log output.')
			#print('Type "%s --help" for usage.' % (sys.argv[0],))
			#raise Exception('Unrecoverable errors. See prior log output.')
			sys.exit(1)

	# Program CLI options.

	def parser_prepare(self):
		self.add_argument('-s', '--source', dest='source_dir',
			type=str, metavar='SOURCE_DIR', default='.',
			help='The source directory containing the images you want to enhance.')

		self.add_argument('-t', '--target', dest='target_dir',
			type=str, metavar='TARGET_DIR', required=True,
			help='The empty or nonexistant path to the target directory to save the new files.')

		# The author is partial to the Google-sponsored open source sans font.
		# Check for that first in the user's home directory.
		font_path_def = os.path.join(
			# I.e., ~/.fonts/open-sans/OpenSans-Regular.ttf
			os.path.expanduser('~'), '.fonts', 'open-sans', 'OpenSans-Regular.ttf',
		)
		# The auther also runs Linux Mint (Ubuntu), so fallback on the system sans.
		if not os.path.exists(font_path_def):
			font_path_def = os.path.join(
				# I.e., /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
				os.sep, 'usr', 'share', 'fonts', 'truetype', 'dejavu', 'DejaVuSans.ttf',
			)
		# If there's no basic font found, force the user to specify it.
		font_path_req = False
		if not os.path.exists(font_path_def):
			font_path_def = ''
			font_path_req = True
		# NOTE: For a list of fonts, try
		#         convert -list font
		self.add_argument('-f', '--font', dest='font_path',
			type=str, metavar='FONT_PATH', default=font_path_def, required=font_path_req,
			help='The path to the font file (OTF, TTF, etc.) to use.')
		# See related font settings: -family, -stretch, -style, and -weight.
		# * 'convert -family' can be used to specify a more general font,
		#   like '-family "Arial"'.
		# * stretch is used to condense or extend the font width.

		# For help on CLI commands and options, see:
		#  http://www.imagemagick.org/script/command-line-options.php
		self.add_argument('--style', dest='font_style',
			type=str.lower, metavar='FONT_STYLE', default='Normal',
			choices=['any', 'italic', 'normal', 'oblique',],
			help='The font style used to render text.')

		# The manual says, for a list of weights, try convert -list weight, but
		# [lb]'s convert is complaining that that's an unrecognized list type.
		# NOTE: You can use a friendly name or a positive integer, at least in
		#       the range from 100 (thin) to 900 (heavy), with 500 being medium.
		self.add_argument('--weight', dest='font_weight',
			type=str.lower, metavar='FONT_WEIGHT', default='Normal',
			# MEH: Using choices precludes the user from being able to use ints.
			choices=[
				'thin', 'extralight', 'light', 'normal', 'medium',
				'demibold', 'bold', 'extrabold', 'heavy',
			], help='The font weight used to render text.')

		self.add_argument('-S', '--font-size', dest='font_size',
			type=int, metavar='POINTSIZE', required=False, default=20,
			help='The font size, or, as convert calls it, -pointsize.')

		# Fill and stroke color.

		# There are 3 color formats, e.g.,
		#   (a) "blue", (b) "#0000ff", or (c) "rgb(0,0,255)"
		# For a list of common colors and their names, try
		#   convert -list color
		self.add_argument('--fill', dest='font_fill',
			type=str, metavar='FONT_FILL', default='black',
			help='The font fill used to render text.')

		# EXPLAIN: Does stroke even matter for text? Or is this the border/outline?
		# Note: The 'none' color is srgb(0,0,0), a/k/a black,
		#       a/k/a: freeze, gray0, grey0, matter, opaque, and transparent.p
		self.add_argument('--stroke', dest='font_stroke',
			type=str, metavar='FONT_STROKE', default='None',
			help='The font stroke used to render text.')

		# The gravity specifies from where the offset is calculated.
		# It defaults to NorthWest, i.e., the upper-left of the image.
		# See: convert -list gravity.
		self.add_argument('--gravity', dest='offset_gravity',
			type=str.lower, metavar='OFFSET_GRAVITY', default='NorthWest',
			# MEH: Using choices precludes the user from being able to use ints.
			choices=[
				'none', 'center', 'east', 'forget', 'northeast', 'north',
				'northwest', 'southeast', 'south', 'southwest', 'west',
			], help='From whence to calculate the x,y offset for the start of the text.')

		self.add_argument('-x', '--x-offset', dest='offset_x',
			type=int, metavar='X_OFFSET', required=False, default=1,
			help='The x-offset of the text.')
		self.add_argument('-y', '--y-offset', dest='offset_y',
			type=int, metavar='Y_OFFSET', required=False, default=1,
			help='The y-offset of the text.')

		# If you want an images larger than your source images, or if
		# your source images contain alpha channels, you can specify a
		# background color.
		self.add_argument('--background', dest='background_color',
			type=str, metavar='BACKGROUND_COLOR', default='None',
			help='The background color to use for enlargements and alphaed sources.')

	def parser_verify(self):
		ok = True

		# Check that imagemagick is installed.
		try:
			ret = subprocess.check_output(['convert', '-version',], stderr=subprocess.STDOUT)
		except FileNotFoundError:
			print(
				'%s: error: Have you installed imagemagick? try: `sudo apt-get install imagemagick`'
				% (SCRIPT_NAME,)
			)
			ok = False

		#curr_path = os.path.dirname(os.path.abspath(__file__))

		if not self.args.source_dir:
			print('%s: error: the following argument is required: -s/--source' % (SCRIPT_NAME,))
			ok = False
		elif not os.path.isdir(self.args.source_dir):
			print(
				'%s: error: the source path does not exist or is not a directory: "%s"'
				% (SCRIPT_NAME, self.args.source_dir,)
			)
			ok = False

		if not self.args.target_dir:
			assert(False) # We marked this argument 'required' so this is a dead if.
			print('%s: error: the following argument is required: -t/--target' % (SCRIPT_NAME,))
			ok = False
		# MAYBE: Allow existing directory if empty.
		elif os.path.exists(self.args.target_dir):
			# MAYBE: Move the existing directory for the user.
			print(
				'%s: error: the target path already exists: please rename (move) or remove: "%s"'
				% (SCRIPT_NAME, self.args.target_dir,)
			)
			ok = False

		if (
			self.args.source_dir
			and (os.path.abspath(self.args.source_dir) == os.path.abspath(self.args.target_dir))
		):
			print(
				'%s: error: the source and target path should not be the same directory: "%s"'
				% (SCRIPT_NAME, self.args.source_dir,)
			)
			ok = False

		if not self.args.font_path:
			print('%s: error: the following argument is required: -f/--font' % (SCRIPT_NAME,))
			ok = False
		if not os.path.isfile(self.args.font_path):
			print(
				'%s: error: the font path does not exist or is not a file: "%s"'
				% (SCRIPT_NAME, self.args.font_path,)
			)
			ok = False

		# MEH: Verify the 'convert' tool options, like --stroke.

		return ok

	# Program runtime.

	def process_images(self):
		# Create the output directory.
		try:
			os.mkdir(self.args.target_dir, mode=0o775)
		except OSError:
			assert(False) # We know the directory already exists.
			raise

		# Get a list of files in the source directory.
		try:
			source_files = os.listdir(self.args.source_dir)
		except FileNotFoundError:
			assert(False) # We know the directory already exists.
			raise

		if not source_files:
			print(
				'%s: error: the source directory does not contain any files: "%s"'
				% (SCRIPT_NAME, self.args.source_dir,)
			)
			sys.exit(1)

		# Determine how many digits the final number will be.
		num_digits = 0
		largest_num = len(source_files)
		while largest_num > 0:
			largest_num = int(largest_num / 10)
			num_digits += 1
		# Make the format symbol, e.g., '%04d' % 12 ==> 0012.
		self.slide_num_fmt = '%%0%dd' % (num_digits,)

		# Walk the files in the top-level source directory in alphabetical order.
		source_files.sort()
		curr_index = 0
		for src_file in source_files:
			self.convert_image(src_file, curr_index)
			curr_index += 1

	def convert_image(self, src_file, curr_index):
		slide_index_text = self.slide_num_fmt % (curr_index,)
		print(
			'Creating slide for index %s: file: "%s"...' % (
				slide_index_text, os.path.basename(src_file),
			),
			end="",
			flush=True,
		)

		source_path = os.path.join(self.args.source_dir, src_file)
		target_path = os.path.join(self.args.target_dir, os.path.basename(src_file))

		#draw_text_posit = '%s,%s' % (self.args.offset_x, self.args.offset_y,)
		annotate_posit = '+%s+%s' % (self.args.offset_x, self.args.offset_y,)

		cmd_merge = [
			'convert',
#'-resize', self.args.resize_geom,
			'-background', self.args.background_color,
			'-font', '"%s"' % (self.args.font_path,),
			'-style', self.args.font_style,
			'-weight', self.args.font_weight,
			'-fill', self.args.font_fill,
			'-stroke', self.args.font_stroke,
			'-pointsize', str(self.args.font_size),
			'-gravity', self.args.offset_gravity,
			# [lb] thinks -draw 'text x,y "string"' is an archaic command; also
			#  '-draw', 'text %s "%s"' % (draw_text_posit, slide_index_text,),
			# works the same as:
			'-annotate', annotate_posit, slide_index_text,
			#'-layers', 'merge',
			source_path,
			target_path,
		]

		try:
			ret = subprocess.check_output(cmd_merge, stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as err:
			print(
				'%s: error: the "convert" command failed: "%s" (%s) on file "%s"'
				% (SCRIPT_NAME, err.output, err.returncode, src_file,)
			)
			sys.exit(1)

		print(" ok.")

	# Main app wrapper.

	def main(self):
		self.parser_run()
		self.process_images()
		self.done()

if __name__ == '__main__':
	numbrr_cli = Image_Numberer_CLI()
	numbrr_cli.main()

