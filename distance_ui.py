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
from gi.repository import Gdk # noqa


def reload_module(m):
    if not hasattr(__builtins__, 'reload'):
        importlib.reload(m)
    else:
        reload(m)


class Model():

    def __init__(self, c1, c2, tol, dist_func=None):
        self.distance_func = dist_func
        self.cols = [c1, c2]
        self.distance = self.get_distance()
        self.tolerance = tol
        self.alpha = self.get_alpha()

    def set_col(self, index, col):
        self.cols[index] = col
        self.distance = self.get_distance()
        self.alpha = self.get_alpha()

    def set_tol(self, tol):
        self.tolerance = tol
        self.alpha = self.get_alpha()

    def set_distance_func(self, func):
        self.distance_func = func
        self.distance = self.get_distance()
        self.alpha = self.get_alpha()

    def get_distance(self):
        if self.distance_func:
            return self.distance_func(*self.cols)
        else:
            return float('NaN')

    def get_alpha(self):
        if self.distance == float('NaN'):
            return float('NaN')
        if self.tolerance >= 1.0:
            return 1.0
        if self.tolerance <= 0.0:
            return 1.0 if self.distance == 0.0 else 0.0
        dist = self.distance
        dist = dist / self.tolerance
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
    w.set_title("This is the window title")
    w.set_size_request(600, 600)

    black = (0.0,) * 4
    model = Model(black, black, 0.0)

    dist_label = Gtk.Label("Distance:")
    dist_label.set_alignment(1.0, 0.5)
    dist_label.set_margin_right(10)
    dist_field = Gtk.Label()
    dist_field.set_alignment(0.0, 0.5)
    alpha_label = Gtk.Label("Alpha:")
    alpha_label.set_alignment(1.0, 0.5)
    alpha_label.set_margin_right(10)
    alpha_field = Gtk.Label()
    alpha_field.set_alignment(0.0, 0.5)

    MAX_A = int(2**16 - 1)

    def update_values(*args, **kws):
        dist_field.set_markup("<big>%.4f</big>" % model.distance)
        alpha_field.set_markup("<big>%.4f</big>" % model.alpha)

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

    def reload_cb(button):
        old_func = func_combo.get_active()
        dist_func_store.clear()
        model.set_distance_func(None)
        reload_module(dm)
        fill_store()
        if old_func >= 0 and old_func < len(dist_func_store):
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
    grid.attach(cp1, 0, 0, fw, 1)
    grid.attach(cp2, 0, 1, fw, 1)

    grid.attach(tol_slider, 0, 2, fw, 1)

    grid.attach(dist_label, 0, 3, 1, 1)
    grid.attach(dist_field, 1, 3, 1, 1)

    grid.attach(alpha_label, 0, 4, 1, 1)
    grid.attach(alpha_field, 1, 4, 1, 1)
    grid.attach(func_combo, 0, 5, fw, 1)
    grid.attach(reload_button, 0, 6, fw, 1)

    w.show_all()
    Gtk.main()


go()
