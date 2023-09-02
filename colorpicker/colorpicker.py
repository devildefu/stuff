#!/usr/bin/env python3

import math
import sys
import cairo
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Xdp", "1.0")
from gi.repository import GLib, Gtk, Gdk, Xdp, Gio

def floats_to_hex(rgb: tuple[float, float, float]) -> str:
    def convert(x):
        x *= 255
        x = max(0, min(x, 255))
        return int(round(x))

    r, g, b = rgb
    return "#{0:02X}{1:02X}{2:02X}".format(convert(r), convert(g), convert(b))

class ColorPicker(Gtk.Application):
    color_box: Gtk.DrawingArea
    hex_color: Gtk.Entry
    portal: Xdp.Portal
    color: tuple[float, float, float]
    clipboard: Gdk.Clipboard

    def __init__(self):
        super().__init__(application_id="io.github.devildefu.ColorPicker")
        GLib.set_application_name("Color Picker")
        self.portal = Xdp.Portal.new()
        self.color = (0, 0, 0)
        self.clipboard = Gdk.Display.get_default().get_clipboard()

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="Color Picker")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(5)
        box.set_margin_end(5)
        box.set_spacing(5)
        window.set_child(box)

        self.color_box = Gtk.DrawingArea()
        self.color_box.set_content_width(48)
        self.color_box.set_draw_func(self.show_color, None)
        box.append(self.color_box)

        self.hex_color = Gtk.Entry()
        self.hex_color.set_max_length(7)
        self.hex_color.set_placeholder_text("#000000")
        self.hex_color.set_editable(False)
        box.append(self.hex_color)

        pick_button = Gtk.Button.new_from_icon_name("color-select-symbolic")
        pick_button.connect('clicked', self.pick_color)
        box.append(pick_button)

        window.present()

    def pick_color(self, button):
        self.portal.pick_color(None, None, self.on_picked_color, None)

    def on_picked_color(self, source_object, res: Gio.AsyncResult, user_data):
        color = self.portal.pick_color_finish(res)
        red = color.get_child_value(0).get_double()
        green = color.get_child_value(1).get_double()
        blue = color.get_child_value(2).get_double()
        self.color = (red, green, blue)
        self.color_box.queue_draw()
        hex_color = floats_to_hex(self.color)
        self.hex_color.set_text(hex_color)
        content_provider = Gdk.ContentProvider.new_for_bytes('text/plain', GLib.Bytes.new(hex_color.encode()))
        self.clipboard.set_content(content_provider)

    def show_color(self, area: Gtk.DrawingArea, c: cairo.Context, w: int, h: int, _):
        radius = 5
        degrees = math.pi / 180
        c.new_sub_path()
        c.arc(w - radius, radius, radius, -90 * degrees, 0 * degrees)
        c.arc(w - radius, h - radius, radius, 0 * degrees, 90 * degrees)
        c.arc(radius, h - radius, radius, 90 * degrees, 180 * degrees)
        c.arc(radius, radius, radius, 180 * degrees, 270 * degrees)
        c.close_path()
        r, g, b = self.color
        c.set_source_rgb(r, g, b);
        c.fill_preserve()

def main():
    app = ColorPicker()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
