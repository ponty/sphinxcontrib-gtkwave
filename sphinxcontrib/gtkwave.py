from docutils.parsers.rst import directives
from easyprocess import EasyProcess
from pyvirtualdisplay.smartdisplay import SmartDisplay, DisplayTimeoutError
from PIL import ImageFilter
import docutils.parsers.rst.directives.images
import logging
import os
import path
import tempfile

"""
    sphinxcontrib.gtkwave
    ================================

    This extension provides a directive to include the screenshot of GtkWave as
    image while building the docs.

"""

__version__ = '0.0.6'

log = logging.getLogger(__name__)
log.debug('sphinxcontrib.gtkwave (version:%s)' % __version__)


class GtkwaveError(Exception):
    pass

tcl = r'''
set clk48 [list]

set nfacs [ gtkwave::getNumFacs ]
for {set i 0} {$i < $nfacs } {incr i} {
set facname [ gtkwave::getFacName $i ]

# set fields [split $facname "\\"]
# set sig [ lindex $fields 1 ]
set fields [split $facname "\\"]
set sig1 [ lindex $fields 0 ]
set sig2 [ lindex $fields 1 ]
if {[llength $fields]  == 2} {
set sig "$sig2"
} else {
set sig "$sig1"
}

lappend clk48 "$sig"
}

set num_added [ gtkwave::addSignalsFromList $clk48 ]

set max_time [ gtkwave::getMaxTime ]
set min_time [ gtkwave::getMinTime ]

gtkwave::setZoomRangeTimes $min_time $max_time
'''

rc = r'''
hide_sst 1
splash_disable 1
enable_vert_grid 0

'''


def get_src(self):
    return self.state_machine.get_source(self.lineno)


def get_black_box(im):
    im3 = im.point(lambda x: 255 * bool(x))
    im2 = im3.filter(ImageFilter.MaxFilter(3))
    im5 = im2.point(lambda x: 255 * bool(not x))
    bbox = im5.getbbox()
    # ignore_black_parts
    im6 = im.crop(bbox)
    bbox2 = im6.getbbox()
    if bbox and bbox2:
        bbox3 = (bbox[0] + bbox2[0],
                 bbox[1] + bbox2[1],
                 bbox[0] + bbox2[2],
                 bbox[1] + bbox2[3],

                 )
        return bbox3


def prog_shot(cmd, f, wait, timeout, screen_size, visible, bgcolor):
    '''start process in headless X and create screenshot after 'wait' sec.
    Repeats screenshot until it is not empty if 'repeat_if_empty'=True.

    wait: wait at least N seconds after first window is displayed,
    it can be used to skip splash screen

    :param wait: int
    '''
    disp = SmartDisplay(visible=visible, size=screen_size, bgcolor=bgcolor)
    proc = EasyProcess(cmd)

    def cb_imgcheck(img):
        """accept img if height > minimum."""
        rec = get_black_box(img)
        if not rec:
            return False
        left, upper, right, lower = rec
        accept = lower - upper > 30  # pixel
        log.debug('cropped img size=' + str(
            (left, upper, right, lower)) + ' accepted=' + str(accept))
        return accept

    def func():
        if wait:
            proc.sleep(wait)
        try:
            img = disp.waitgrab(timeout=timeout, cb_imgcheck=cb_imgcheck)
        except DisplayTimeoutError, e:
            raise DisplayTimeoutError(str(e) + ' ' + str(proc))
        return img

    img = disp.wrap(proc.wrap(func))()
    if img:
        bbox = get_black_box(img)
        assert bbox
        # extend to the left side
        bbox = (0, bbox[1], bbox[2], bbox[3])
        img = img.crop(bbox)

        img.save(f)
    return (proc.stdout, proc.stderr)


parent = docutils.parsers.rst.directives.images.Image
images_to_delete = []
image_id = 0


class GtkwaveDirective(parent):
    option_spec = parent.option_spec.copy()
    option_spec.update(dict(
                       #                       prompt=directives.flag,
                       screen=directives.unchanged,
                       wait=directives.nonnegative_int,
                       #                       stdout=directives.flag,
                       #                       stderr=directives.flag,
                       visible=directives.flag,
                       timeout=directives.nonnegative_int,
                       bgcolor=directives.unchanged,
                       ))

    def run(self):
        screen = self.options.get('screen', '1024x768')
        screen = tuple(map(int, screen.split('x')))
        wait = self.options.get('wait', 0)
        timeout = self.options.get('timeout', 12)
        bgcolor = self.options.get('bgcolor', 'white')
        visible = 'visible' in self.options

        vcd = str(self.arguments[0])

        tclfile = tempfile.NamedTemporaryFile(
            prefix='gtkwave', suffix='.tcl', delete=0)
        tclfile.write(tcl)
        tclfile.close()

        rcfile = tempfile.NamedTemporaryFile(
            prefix='gtkwave', suffix='.rc', delete=0)
        rcfile.write(rc)
        rcfile.close()

        cmd = ['gtkwave',
               vcd,
               '--tcl_init',
               tclfile.name,
               '--rcfile',
               rcfile.name,
               '--nomenu',
               ]

        global image_id
        f = 'gtkwave_id%s.png' % (str(image_id))
        image_id += 1
        fabs = path.path(get_src(self)).dirname() / (f)
        images_to_delete.append(fabs)

        prog_shot(cmd, fabs, screen_size=screen, wait=wait,
                  timeout=timeout, visible=visible, bgcolor=bgcolor)

        os.remove(tclfile.name)
        os.remove(rcfile.name)

        self.arguments[0] = f
        x = parent.run(self)

#        output = ''
#        if 'stdout' in self.options:
#            output += o[0]
#            if o[0]:
#                output += '\n'

#        if 'stderr' in self.options:
#            output += o[1]
#            if o[1]:
#                output += '\n'

#        if 'prompt' in self.options:
            # TODO:
            # if app.config.programoutput_use_ansi:
            # enable ANSI support, if requested by config
            #    from sphinxcontrib.ansi import ansi_literal_block
            #    node_class = ansi_literal_block
            # else:
            #    node_class = nodes.literal_block

            # TODO: get app
            # tmpl = app.config.programoutput_prompt_template
#            tmpl = '$ %(command)s\n%(output)s'
#            output = tmpl % dict(command=cmd, output=output)

#        node_class = nodes.literal_block
#        if output:
#            x = [node_class(output, output)] + x

        return x


def cleanup(app, exception):
    for x in images_to_delete:
        f = path.path(x)
        if f.exists():
            log.debug('removing image:' + x)
            f.remove()


def setup(app):
    # app.add_config_value('programoutput_use_ansi', False, 'env')
    # app.add_config_value('gtkwave_prompt_template',
    #                     '$ %(command)s\n%(output)s', 'env')
    app.add_directive('gtkwave', GtkwaveDirective)
    app.connect('build-finished', cleanup)
