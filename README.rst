####################
Many Doge Meme Maker
####################

Or, A Slideshow Image Numbering and Labeling Tool
=================================================

Overview
--------
 
Many Doge Meme Maker (``mdm2``) is a simple tool
that scans a directory of images and for each
image, it writes labels on the image.

The labels generally include
`Doge words
<https://en.wikipedia.org/wiki/Doge_%28meme%29#Structure>`__,
but you can also use ``mdm2`` -- and you probably should --
to process images you're preparing for a presentation.

The label text can be anything and can include special variables,
such as the image filename, the current slide number, and the
total number of slides.

Each label can be assigned its own font, size, style, and color.

The canvas can be expanded, giving the image a border, so
that labels can be placed outside the image.

Process
-------

It's assumed you've got a folder of alphabetized images.

Hint: If you're looking for a good alphabetization scheme,
prepend all your images with a long number and leaves zeros
on both ends so you can easily insert slides without the 
name having a ripple effect on other slides.
E.g.,
``0001100.My.first.slide.png``,
``0001200.My.second.slide.png``,
etc. Then if you want to add a third slide between the first two,
just name it ``0001150.Oops-I_forget_the-third.slide.png``,

Why do it this way? Because the author uses GIMP to mock up
screenshots when designing UIs, and there's a great
`GIMP plugin
<http://registry.gimp.org/node/28268>`__
that
`exports each layer as an image
<https://github.com/khalim19/gimp-plugin-export-layers>`__.

So, rather than bring the images into a presentation tool and have
to manage *all that*, I run the images through ``mdm2`` and 
then my presentation is just a stack of images that lots of programs
can easily handle, like
`Eye of GNOME
<https://wiki.gnome.org/Apps/EyeOfGnome>`__.
It's also easy to insert and modify images, and to remake the presentation.

Usage
-----

See ``./mmdm.py --help`` for command line options.

Note that ``mdm2`` is simple Bash wrapper around
`ImageMagick
<http://www.imagemagick.org>`__,
so if your system cannot find the ``convert`` command,
that's why.

Example
-------

Assume I have a folder, ``./src``, with a collection of images
that are 1123x873. I want to label each one with a title and
the slide number. The want the title above the image, on a
black border. And in the lower-right corner, also on the new
border, I want to show the image filename, the image number,
and the total number of images in the presentation.
Here's the command I might run.

.. code-block:: bash

    ./mdm2.py \
        \
        -s ./src/ \
        -t ./dst/ \
        \
        --extent "1280x1024+0+8" \
        --background black \
        \
        -f ~/.fonts/open-sans/OpenSans-Regular.ttf \
        \
        --gravity north \
        --fill white \
        --stroke white \
        --size 30 \
        -x 0 -y 20 \
        -l "My Design Presentation" \
        \
        --gravity southeast \
        --fill white \
        --stroke white \
        --size 14 \
        -x 85 -y 52 \
        -l "{filename}" \
        \
        --gravity southeast \
        --fill white \
        --stroke white \
        --size 30 \
        -x 80 -y 12 \
        -l "{slide_number} / {slide_count}"

