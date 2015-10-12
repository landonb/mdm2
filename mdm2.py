#!/usr/bin/env python3

# See README.rst for usage and examples, or just read the code.

# For help on Imagemagick CLI commands and options, see:
#  http://www.imagemagick.org/script/command-line-options.php

SCRIPT_VERSION = 0.1
SCRIPT_DESCRIPTION = 'Many Doge Meme Maker'

import os
import sys

import argparse
import re
import subprocess
import time

try:
	import time_util
except ImportError:
	pass

SCRIPT_NAME = os.path.basename(__file__)

class MDM2_CLI(argparse.ArgumentParser):

	def __init__(self, script_version=None, description=None, **kwargs):
		super(MDM2_CLI, self).__init__(
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

		# *** Source image directory.

		self.add_argument('-s', '--source', dest='source_dir',
			type=str, metavar='SOURCE_DIR', default='.',
			help='The source directory containing the images you want to enhance.')

		# *** Destination image directory.

		self.add_argument('-t', '--target', dest='target_dir',
			type=str, metavar='TARGET_DIR', required=True,
			help='The empty or nonexistant path to the target directory to save the new files.')

		# *** Configuring the font and indicating what text to write.

		# NOTE: You can specify the same options multiple times to setup
		#       multiple texts to write.

		self.add_argument('-l', '--label', dest='text_label',
			type=str, metavar='LABEL_TYPE', action='append', required=True,
			help='The label text with may include {filename}, {slide_number}, {slide_count}.')

		# Text defaults.

		# The author is partial to the Google-sponsored open source sans font.
		# Check for that first in the user's home directory.
		def_font_path = os.path.join(
			# I.e., ~/.fonts/open-sans/OpenSans-Regular.ttf
			os.path.expanduser('~'), '.fonts', 'open-sans', 'OpenSans-Regular.ttf',
		)
		# The auther also runs Linux Mint (Ubuntu), so fallback on the system sans.
		if not os.path.exists(def_font_path):
			def_font_path = os.path.join(
				# I.e., /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
				os.sep, 'usr', 'share', 'fonts', 'truetype', 'dejavu', 'DejaVuSans.ttf',
			)
		# If there's no basic font found, force the user to specify it.
		if not os.path.exists(def_font_path):
			def_font_path = None
		# NOTE: For a list of fonts, try
		#         convert -list font

		self.text_defaults = {
			'font_path': def_font_path,
			'font_style': 'Normal',
			'font_weight': 'Normal',
			'font_size': 20,
			'font_fill': 'black',
			'font_stroke': 'none',
			'offset_gravity': 'center',
			'offset_x': 0,
			'offset_y': 0,
		}

		# Text options.

		self.add_argument('-f', '--font', dest='font_path',
			type=str, metavar='FONT_PATH', action='append',
			help='The path to the font file (OTF, TTF, etc.) to use.')
		# See related font settings: -family, -stretch, -style, and -weight.
		# * 'convert -family' can be used to specify a more general font,
		#   like '-family "Arial"'.
		# * stretch is used to condense or extend the font width.

		self.add_argument('--style', dest='font_style',
			type=str.lower, metavar='FONT_STYLE', action='append',
			choices=['any', 'italic', 'normal', 'oblique',],
			help='The font style used to render text.')

		# The manual says, for a list of weights, try convert -list weight, but
		# [lb]'s convert is complaining that that's an unrecognized list type.
		# NOTE: You can use a friendly name or a positive integer, at least in
		#       the range from 100 (thin) to 900 (heavy), with 500 being medium.
		self.add_argument('--weight', dest='font_weight',
			type=str.lower, metavar='FONT_WEIGHT', action='append',
			## MEH: Using choices precludes the user from being able to use ints.
			#choices=[
			#	'thin', 'extralight', 'light', 'normal', 'medium',
			#	'demibold', 'bold', 'extrabold', 'heavy',
			#],
			help='The font weight used to render text. Either a friendly name or integer weight')

		self.add_argument('-S', '--size', dest='font_size',
			type=int, metavar='POINTSIZE', action='append',
			help='The font size, or, as convert calls it, -pointsize.')

		# Fill and stroke color.

		# There are 3 color formats, e.g.,
		#   (a) "blue", (b) "#0000ff", or (c) "rgb(0,0,255)"
		# For a list of common colors and their names, try
		#   convert -list color
		self.add_argument('--fill', dest='font_fill',
			type=str, metavar='FONT_FILL', action='append',
			help='The font fill used to render text.')

		# NOTE: The stroke applies to the font border.
		#       Set it to get a bolder looking font.
		# Note: The 'none' color is srgb(0,0,0), a/k/a black,
		#       a/k/a: freeze, gray0, grey0, matter, opaque, and transparent.p
		self.add_argument('--stroke', dest='font_stroke',
			type=str, metavar='FONT_STROKE', action='append',
			help='The font stroke used to render text.')

		# The gravity specifies from where the offset is calculated.
		# It defaults to NorthWest, i.e., the upper-left of the image.
		# See: convert -list gravity.
		self.add_argument('--gravity', dest='offset_gravity',
			type=str.lower, metavar='OFFSET_GRAVITY', action='append',
			choices=[
				'none', 'center', 'east', 'forget', 'northeast', 'north',
				'northwest', 'southeast', 'south', 'southwest', 'west',
			], help='From whence to calculate the x,y offset for the start of the text.')

		# NOTE: If you specify one of the center gravities, like center, or
		#       north or south, thankfully your text is centered, too, so the
		#       x-offset can be left at 0.
		self.add_argument('-x', '--x-offset', dest='offset_x',
			type=int, metavar='X_OFFSET', action='append',
			help='The x-offset of the text.')
		self.add_argument('-y', '--y-offset', dest='offset_y',
			type=int, metavar='Y_OFFSET', action='append',
			help='The y-offset of the text.')

		# *** Resizing the canvas.

		# You can resize the canvas if you want images larger than your source
		# images, say, for borders or so you can write your text off the image.
		self.add_argument('--extent', dest='extent_geom',
			type=str, metavar='EXTENT_GEOM', default='100%',
			help='Set the new image size without scaling.')
		# Set the gravity used when resizing the canvas. Use center to keep
		# the image centered, or you can anchor it to an edge or corner.
		self.add_argument('--extent-gravity', dest='extent_gravity',
			type=str.lower, metavar='EXTENT_GRAVITY', default='center',
			choices=[
				'none', 'center', 'east', 'forget', 'northeast', 'north',
				'northwest', 'southeast', 'south', 'southwest', 'west',
			], help='If resizing, where to fix the original image.')
		# Specify a background color to fill in the new space created by an
		# extent. You can also use background color if you want to fill in
		# the alpha channels of your source images.
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

		# If we didn't figure out the font, use the first as the default.
		for font_path in self.args.font_path:
			if not os.path.isfile(font_path):
				print(
					'%s: error: a font path does not exist or is not a file: "%s"'
					% (SCRIPT_NAME, font_path,)
				)
				ok = False
		if not self.text_defaults['font_path']:
			if self.args.font_path:
				self.text_defaults['font_path'] = self.args.font_path[0]
			else:
				print('%s: error: specify at least font face: -f/--font' % (SCRIPT_NAME,))
				ok = False

		# Verify the text label option lists.
		# MEH: We could verify the 'convert' tool options, like --stroke,
		#      or we could just let the convert tool fail and bark at us.

		# Make the text label option sets.

		# We use defaults for options whose lists aren't as long as
		# text_label, but we complain if there are more settings for
		# one option than there are labels.
		for arg_key in self.text_defaults.keys():
			arg_opts = getattr(self.args, arg_key) or []
			if len(arg_opts) > len(self.args.text_label):
				print(
					'%s: error: there are more options for arg "%s" than there are labels'
					% (SCRIPT_NAME, arg_key,)
				)
				ok = False

		self.text_labels = []
		for label_i in range(len(self.args.text_label)):
			label_def = {}
			label_def['label'] = self.args.text_label[label_i]
			for arg_key, arg_default in self.text_defaults.items():
				arg_list = getattr(self.args, arg_key) or []
				try:
					# The last value the user specifies is the default.
					# E.g., if there four labels and the user configures
					# the first two labels on the CLI, the third and
					# fourth will use the same setting as number two.
					label_def[arg_key] = arg_list[label_i]
				except IndexError:
					label_def[arg_key] = arg_default
			self.text_labels.append(label_def)

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
		self.slide_count = len(source_files)
		largest_num = self.slide_count
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
		slide_index_text = self.slide_num_fmt % (curr_index + 1,)
		print(
			'Creating slide for index %s: file: "%s"...' % (
				slide_index_text, os.path.basename(src_file),
			),
			end="",
			flush=True,
		)

		source_path = os.path.join(self.args.source_dir, src_file)

		target_path = os.path.join(self.args.target_dir, os.path.basename(src_file))

		# Create the text layer(s).
		label_opts = []
		for label_def in self.text_labels:
			#draw_text_posit = '%s,%s' % (label_def['offset_x'], label_def['offset_y'],)
			annotate_posit = '+%s+%s' % (label_def['offset_x'], label_def['offset_y'],)

			# MAGIC_VALUES: ${filename}, ${slide_number}, and ${slide_count}.
			#         NOTE: str.format() consumes starting $ or doesn't care.
			label_text = label_def['label'].format(
				filename=src_file,
				slide_number=slide_index_text,
				slide_count=self.slide_count,
			)

			label_opts += [
				'-font', '"%s"' % (label_def['font_path'],),
				'-style', label_def['font_style'],
				'-weight', label_def['font_weight'],
				'-fill', label_def['font_fill'],
				'-stroke', label_def['font_stroke'],
				'-pointsize', str(label_def['font_size']),
				'-gravity', label_def['offset_gravity'],
				# [lb] thinks -draw 'text x,y "string"' is an archaic command; also
				#  '-draw', 'text %s "%s"' % (draw_text_posit, label_text,),
				# works the same as:
				'-annotate', annotate_posit, label_text,
			]

		cmd_merge = [
			# Oh ho ho it's imagemagick ya know.
			'convert',

			# Resize (but don't stretch) the image (if extent_geom is set).
			'-background', self.args.background_color,
			'-size', self.args.extent_geom,
			'-gravity', self.args.extent_gravity,
			# NOTE: Order matters. If -resize comes before -extent, the
			#       image is stretched.
			'-extent', self.args.extent_geom,
			'-resize', self.args.extent_geom,

			# One or more sets of label options.
			] + label_opts + [

			# The source image we're manipulating.
			source_path,

			# Our target image we're creating.
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
	numbrr_cli = MDM2_CLI()
	numbrr_cli.main()

