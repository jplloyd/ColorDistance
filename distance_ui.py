import spectral
import math
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk # noqa
from gi.repository import Gdk # noqa

diff = spectral.diff

SUMMED_WEIGHTS = sum(spectral.sums)
N = spectral.NUM_WAVES
EPS = spectral.WGM_EPSILON


def distance_accum_diff(c1, c2):
    accum_diff = 0.0
    for i in range(N):
        accum_diff += diff(c1[i], c2[i])
    return accum_diff


def distance_euclidian(c1, c2):
    delta_sqrs = [diff(c1[i], c2[i])**2 for i in range(N)]
    return math.sqrt(sum(delta_sqrs))


def log_clamped(x):
    offs = 1.0 - EPS
    return spectral.log2(x * offs + EPS)


def distance_accum_diff_log(c1, c2):
    c1 = list(map(log_clamped, c1))
    c2 = list(map(log_clamped, c2))
    return distance_accum_diff(c1, c2)


def distance_euclidian_log(c1, c2):
    c1 = list(map(log_clamped, c1))
    c2 = list(map(log_clamped, c2))
    return distance_euclidian(c1, c2)


dist_funcs = [
    distance_accum_diff,
    distance_accum_diff_log,
    distance_euclidian,
    distance_euclidian_log,
]
func_names = [
    "Accum. difference (straight)",
    "Accum. difference (log)",
    "Euclidian distance (straight)",
    "Euclidian distance (log)",
]


class Model():

    def __init__(self, c1, c2, tol):
        self.distance_func = distance_euclidian
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
        r1, g1, b1, a1 = self.cols[0]
        r2, g2, b2, a2 = self.cols[1]
        spec1 = spectral.rgb_to_spectral(r1, g1, b1)
        spec2 = spectral.rgb_to_spectral(r2, g2, b2)
        spec1.append(a1)
        spec2.append(a2)
        return self.distance_func(spec1, spec2)

    def get_alpha(self):
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
    dist_field = Gtk.Label("0.0")
    dist_field.set_alignment(0.0, 0.5)
    alpha_label = Gtk.Label("Alpha:")
    alpha_label.set_alignment(1.0, 0.5)
    alpha_label.set_margin_right(10)
    alpha_field = Gtk.Label("1.0")
    alpha_field.set_alignment(0.0, 0.5)

    MAX_A = int(2**16 - 1)

    def update_values(*args, **kws):
        dist_field.set_markup(str(model.distance))
        alpha_field.set_markup(str(model.alpha))

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
    cp1.connect("color-changed", col_change_cb, 0)

    cp2 = Gtk.ColorSelection()
    cp2.connect("color-changed", col_change_cb, 1)
    cp2.set_has_opacity_control(True)
    cp2.set_current_alpha(MAX_A)

    dist_func_store = Gtk.ListStore(str)
    for i in range(len(dist_funcs)):
        dist_func_store.append([func_names[i]])

    func_combo = Gtk.ComboBox()
    func_combo.set_model(dist_func_store)
    cell = Gtk.CellRendererText()
    func_combo.pack_start(cell, True)
    func_combo.add_attribute(cell, "text", 0)

    def func_change_cb(combo):
        act = combo.get_active()
        if act != -1:
            model.set_distance_func(dist_funcs[act])
            update_values()

    func_combo.connect("changed", func_change_cb)

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
    grid.attach(func_combo, 0, 5, 1, fw)

    w.show_all()
    Gtk.main()


go()
