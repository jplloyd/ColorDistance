# Copyright (C) 2019 by Jesper Lloyd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

import distance_models as dm
import importlib
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk # noqa


def reload_module(m):
    if not hasattr(__builtins__, 'reload'):
        importlib.reload(m)
    else:
        reload(m)


class Model(object):

    def __init__(self, c1, c2, tol, dist_func=None):
        self.distance_func = dist_func
        self.cols = [c1, c2]
        self.tolerance = tol
        self.rgb_distance = None
        self.rgba_distance = None
        self.rgb_alpha = None
        self.rgba_alpha = None
        self._update_values()

    def _update_values(self):
        self.rgb_distance = self.get_rgb_distance()
        self.rgba_distance = self.get_rgba_distance()
        self.rgb_alpha = self.get_alpha(self.rgb_distance)
        self.rgba_alpha = self.get_alpha(self.rgba_distance)

    def set_col(self, index, col):
        col = tuple(col)
        self.cols[index] = col
        self._update_values()

    def set_tol(self, tol):
        self.tolerance = tol
        self.rgb_alpha = self.get_alpha(self.rgb_distance)
        self.rgba_alpha  = self.get_alpha(self.rgba_distance)

    def set_distance_func(self, func):
        self.distance_func = func
        self._update_values()

    def get_rgb_distance(self):
        if self.distance_func:
            try:
                return self.distance_func(*self.cols)
            except Exception as e:
                print("Exception when running distance function!")
                print(e)
        return None

    def get_rgba_distance(self):
        """Weighted sum of color & alpha deltas"""
        if self.rgb_distance is None:
            return None
        a1, a2 = (c[3] for c in self.cols)
        a_delta = abs(a1 - a2)
        a_avg = (a1 + a2) / 2.0
        # Unscientific heuristic
        col_factor = a_avg * (1.0 - a_delta)
        return self.rgb_distance * col_factor + a_delta * (1.0 - col_factor)

    def get_alpha(self, distance):
        """Distance -> Tolerance -> Fill alpha calculation
        Currently uses the old GIMP/MyPaint equation.
        """
        if distance is None:
            return None
        if self.tolerance >= 1.0:
            return 1.0
        if self.tolerance <= 0.0:
            return 1.0 if distance == 0.0 else 0.0
        dist = distance / self.tolerance
        if dist >= 1.0:
            return 0.0
        else:
            aa = 1.0 - dist
            if aa < 0.5:
                return aa * 2
            else:
                return 1.0


def go():
    w = Gtk.Window()
    w.connect("delete-event", lambda w, e: Gtk.main_quit())
    w.set_title("Color distance model tester")
    w.set_size_request(600, 800)

    black = (0.0,) * 3 + (1.0,)
    model = Model(black, black, 0.0)

    # RGB distances and resulting-alpha display widgets

    rgb_dist_label = Gtk.Label("RGB Distance:")
    rgb_dist_label.set_alignment(1.0, 0.5)
    rgb_dist_label.set_margin_right(10)

    rgb_dist_field = Gtk.Label()
    rgb_dist_field.set_alignment(0.0, 0.5)

    rgb_alpha_label = Gtk.Label("RGB Fill-Alpha:")
    rgb_alpha_label.set_alignment(1.0, 0.5)
    rgb_alpha_label.set_margin_right(10)

    rgb_alpha_field = Gtk.Label()
    rgb_alpha_field.set_alignment(0.0, 0.5)

    # RGBA distances and resulting-alpha display widgets

    rgba_dist_label = Gtk.Label("RGBA Distance:")
    rgba_dist_label.set_alignment(1.0, 0.5)
    rgba_dist_label.set_margin_right(10)

    rgba_dist_field = Gtk.Label()
    rgba_dist_field.set_alignment(0.0, 0.5)

    rgba_alpha_label = Gtk.Label("RGBA Fill-Alpha:")
    rgba_alpha_label.set_alignment(1.0, 0.5)
    rgba_alpha_label.set_margin_right(10)

    rgba_alpha_field = Gtk.Label()
    rgba_alpha_field.set_alignment(0.0, 0.5)

    MAX_A = int(2**16 - 1)

    def update_values():
        if model.rgb_distance is None:
            rgb_dist_field.set_markup(" - ")
            rgba_dist_field.set_markup(" - ")
            rgb_alpha_field.set_markup(" - ")
            rgba_alpha_field.set_markup(" - ")
        else:
            rgb_dist_field.set_markup("<big>%.4f</big>" % model.rgb_distance)
            rgb_alpha_field.set_markup("<big>%.4f</big>" % model.rgb_alpha)
            rgba_dist_field.set_markup("<big>%.4f</big>" % model.rgba_distance)
            rgba_alpha_field.set_markup("<big>%.4f</big>" % model.rgba_alpha)

    update_values()

    def tol_cb(adj):
        model.set_tol(adj.get_value())
        update_values()

    def col_change_cb(col_sel, n):
        c = col_sel.get_current_rgba()
        col_sel.set_previous_rgba(c)
        col_sel.set_previous_alpha(MAX_A)
        model.set_col(n, c)
        update_values()

    tol_slider = Gtk.Scale()
    adj = Gtk.Adjustment(
        value=float(0.0), lower=0.0, upper=1.0,
        step_increment=0.01, page_increment=0.05, page_size=0
    )
    adj.connect("value-changed", tol_cb)
    tol_slider.set_draw_value(True)
    tol_slider.set_digits(4)
    tol_slider.set_hexpand(True)
    tol_slider.set_adjustment(adj)

    cp1 = Gtk.ColorSelection()
    cp1.set_has_opacity_control(True)
    cp1.set_current_alpha(MAX_A)
    cp1.set_halign(Gtk.Align.CENTER)
    cp1.connect("color-changed", col_change_cb, 0)

    cp2 = Gtk.ColorSelection()
    cp2.set_has_opacity_control(True)
    cp2.set_current_alpha(MAX_A)
    cp2.set_halign(Gtk.Align.CENTER)
    cp2.connect("color-changed", col_change_cb, 1)

    dist_func_store = Gtk.ListStore(str, object)

    func_combo = Gtk.ComboBox()

    def fill_store():
        dist_func_store.clear()
        for func, name in dm.distance_functions:
            dist_func_store.append([name, func])

    fill_store()

    func_combo.set_model(dist_func_store)
    cell = Gtk.CellRendererText()
    func_combo.pack_start(cell, True)
    func_combo.set_hexpand(True)
    func_combo.add_attribute(cell, "text", 0)

    def func_change_cb(combo):
        act = combo.get_active()
        if act != -1:
            model.set_distance_func(
                combo.get_model()[act][1]
            )
            update_values()

    func_combo.connect("changed", func_change_cb)
    if len(dist_func_store) > 0:
        func_combo.set_active(0)

    def reload_cb(_):
        old_func = func_combo.get_active()
        dist_func_store.clear()
        model.set_distance_func(None)
        reload_module(dm)
        fill_store()
        if 0 <= old_func < len(dist_func_store):
            func_combo.set_active(old_func)
        update_values()

    reload_button = Gtk.Button("Reload distance functions")
    reload_button.set_hexpand(True)
    reload_button.connect("clicked", reload_cb)

    grid = Gtk.Grid()
    grid.set_row_spacing(6)
    grid.set_margin_left(10)
    grid.set_margin_right(10)
    grid.set_margin_top(10)
    grid.set_margin_bottom(10)
    w.add(grid)
    fw = 2
    r = attach_inc_row(grid, cp1, 0, 0, fw, 1)
    r = attach_inc_row(grid, cp2, 0, r, fw, 1)
    r = attach_inc_row(grid, tol_slider, 0, r, fw, 1)

    grid.attach(rgb_dist_label, 0, r, 1, 1)
    grid.attach(rgb_dist_field, 1, r, 1, 1)
    r += 1

    grid.attach(rgb_alpha_label, 0, r, 1, 1)
    grid.attach(rgb_alpha_field, 1, r, 1, 1)
    r += 1

    grid.attach(rgba_dist_label, 0, r, 1, 1)
    grid.attach(rgba_dist_field, 1, r, 1, 1)
    r += 1

    grid.attach(rgba_alpha_label, 0, r, 1, 1)
    grid.attach(rgba_alpha_field, 1, r, 1, 1)
    r += 1

    r = attach_inc_row(grid, func_combo, 0, r, fw, 1)
    grid.attach(reload_button, 0, r, fw, 1)

    w.show_all()
    Gtk.main()


def attach_inc_row(grid, child, col, row, width, height):
    grid.attach(child, col, row, width, height)
    return row+1


go()
