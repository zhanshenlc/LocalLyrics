from gi.repository import GObject, Gtk, Peas, RB, Gdk, GLib
import os
import urllib
import pylrc
import codecs


LocalLyrics_UI = """
<ui>
    <toolbar name="ToolBar">
        <toolitem name="LocalLyrics" action="LocalLyrics" />
    </toolbar>
</ui>
"""

class LocalLyrics(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'LocalLyrics'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(LocalLyrics, self).__init__()
        GObject.threads_init()
        Gdk.threads_init()

    def do_activate(self):
        self.shell = self.object
        self.sp = self.object.props.shell_player
        self.init_gui()
        self.shell.add_widget(self.vbox, RB.ShellUILocation.MAIN_BOTTOM, expand=True, fill=True)

        self.lrc_content = None
        
        #self.pc_id = self.sp.connect('playing-changed', self.show_Lyrics)
        self.psc_id = self.sp.connect('playing-song-changed', self.show_Lyrics)
        #self.ec_id = self.sp.connect('elapsed-changed', self.show_Lyrics)
        #self.psp_id = self.sp.connect('playing-song-property-changed', self.show_Lyrics)
    
    def do_deactivate(self):
        self.shell.remove_widget(self.vbox, RB.ShellUILocation.MAIN_BOTTOM)
        #self.sp.disconnect(self.pc_id)
        self.sp.disconnect(self.psc_id)
        #self.sp.disconnect(self.ec_id)
        #self.sp.disconnect(self.psp_id)

    def show_Lyrics(self, sp, _):
        song = self.sp.get_playing_entry()
        songFile = song.get_playback_uri()
        index = songFile.rfind('.')
        songFile = songFile[7:index] + ".lrc"
        songFile = urllib.parse.unquote(songFile, 'utf-8')

        if os.path.isfile(songFile):
            lrcFile = open(songFile, 'r', encoding='utf-16')
            lrc = ''.join(lrcFile.readlines())
            lrcFile.close()
            self.lrc_content = pylrc.parse(lrc)

            self.newest_index = 0
            self.line_index = 0
            #self.need_change = True
            self.line_num = len(self.lrc_content)
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.idle_showLyrics)
        else:
            self.lrc_content = None
            for i in range(3):
                self.lineBoxes[i].set_markup("")

    def idle_showLyrics(self):
        if self.line_index == self.line_num:
            return False
        if self.sp.props.playing:
            current_time = self.sp.get_playing_time()[1]
            if self.line_index == 0:
                for i in range(3):
                    self.lineBoxes[i].set_markup("<span foreground=\"Yellow\" size=\"large\">" + self.lrc_content[i].text + "</span>")
                self.line_index = 2
            
            if current_time > self.lrc_content[self.line_index].time:
                self.line_index += 1
                self.lineBoxes[self.newest_index].set_markup("<span foreground=\"Yellow\" size=\"large\">" + self.lrc_content[self.line_index].text + "</span>")
                if self.newest_index == 2:
                    self.newest_index = 0
                else:
                    self.newest_index += 1
        return True

    def init_gui(self):
        self.vbox = Gtk.VBox()
        self.labelBox = Gtk.HBox()
        self.line0Box = Gtk.HBox()
        self.line1Box = Gtk.HBox()
        self.line2Box = Gtk.HBox()

        self.lryicsLabel = Gtk.Label()
        self.lryicsLabel.set_markup("<span foreground=\"Green\" size=\"xx-large\">Lyrics Plugin</span><span foreground=\"Cyan\" size=\"small\">\tby zhanshenlc</span>")
        self.line0 = Gtk.Label()
        self.line1 = Gtk.Label()
        self.line2 = Gtk.Label()

        '''# create a TextView for displaying lyrics
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_left_margin(10)
        self.textview.set_right_margin(10)
        self.textview.set_pixels_above_lines(5)
        self.textview.set_pixels_below_lines(5)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = Gtk.TextBuffer()
        self.textview.set_buffer(self.textbuffer)'''
        

        self.labelBox.pack_start(self.lryicsLabel, expand=True, fill=True, padding=20)
        self.line0Box.pack_start(self.line0, expand=True, fill=True, padding=20)
        self.line1Box.pack_start(self.line1, expand=True, fill=True, padding=20)
        self.line2Box.pack_start(self.line2, expand=True, fill=True, padding=20)
        self.vbox.pack_start(self.labelBox, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.line0Box, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.line1Box, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.line2Box, expand=True, fill=True, padding=0)
        #self.vbox.pack_start(self.textview, expand=True, fill=True, padding=0)
        self.vbox.show_all()

        self.lineBoxes = [self.line0, self.line1, self.line2]
