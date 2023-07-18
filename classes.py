import csv
import copy
import os


class Show:
    def __init__(self, num_id, title, ep, season, link, weight, color):
        self.id = num_id
        self.title = title
        self.ep = ep
        self.season = season
        self.link = link
        self.weight = weight
        self.color = color

    def __repr__(self):
        return f"Show(num_id={self.id.__repr__()}, title={self.title.__repr__()}, ep={self.ep.__repr__()}," \
               f" season={self.season.__repr__()}, link={self.link.__repr__()}, weight={self.weight.__repr__()}," \
               f" color={self.color.__repr__()})"

    def stringify(self):
        self.id = str(self.id)
        self.title = str(self.title)
        self.ep = str(self.ep)
        self.season = str(self.season)
        self.link = str(self.link)
        self.weight = str(self.weight)
        self.color = str(self.color)


def sort_shows_alphabetically(lst: list):
    def get_title(show):
        return show.title

    lst.sort(key=get_title, reverse=True)
    return lst


class ShowsFileHandler:
    def __init__(self, savefile="saved.csv", delimiter="\\"):
        self.savefile = savefile
        self.shows = []
        self.original_shows = []
        self.delimiter = delimiter

        self.ensure_file_exists()

        self.read_file()

    def ensure_file_exists(self):
        if not os.path.isfile(self.savefile):
            with open(self.savefile, "w"):
                pass

    def read_file(self):
        self.shows = []
        with open(self.savefile, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar="|")
            for row in reader:
                self.shows.append(Show(
                    num_id=row[0],
                    title=row[1],
                    ep=row[2],
                    season=row[3],
                    link=row[4],
                    weight=row[5],
                    color=row[6],
                ))
        self.original_shows = copy.deepcopy(self.shows)
        return self.shows

    def pop(self, __index):
        return self.shows.pop(__index)

    def append(self, __object):
        self.shows.append(__object)

    def __getitem__(self, item):
        return self.shows[item]

    def __setitem__(self, key, value):
        self.shows[key] = value

    def __iter__(self):
        return iter(self.shows)

    def __len__(self):
        return len(self.shows)

    def do_sorting(self):
        dct = {}
        for n in self.shows:
            if n.weight in dct:
                dct[n.weight].append(n)
                continue
            dct[n.weight] = [n]
        lt = []
        slist = []  # list of Weights used
        for n in dct:
            slist.append(int(n))
            dct[n].sort(key=lambda x: x.id)
        slist.sort()
        for n in slist:
            lt += sort_shows_alphabetically(dct[str(n)])
        lt.reverse()
        self.shows = lt

    def save(self):
        if self.shows == self.original_shows:
            return

        with open(self.savefile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar="|")
            for show in self.shows:
                writer.writerow([show.id, show.title, show.ep, show.season, show.link, show.weight, show.color])


class Settings:
    def __init__(self, sg, savefile="settings.csv", delimiter="\\", fontsize=15, fonttype="Helvetica", text_colors=None,
                 button_color=None, background_color=None, right_click_selected_background="#252525",
                 right_click_fontsize=10, input_background=None, initialwinsize=(400, 200),
                 initialwinpos=(50, 50), search_results=3, show_amount=32,
                 max_title_display_len=0, indices_visible=True, show_all=False):
        self.sg = sg

        self.savefile = savefile
        self.delimiter = delimiter

        self.fontsize = fontsize
        self.fonttype = fonttype
        self.text_colors = text_colors if text_colors is not None else [sg.theme_text_color(), "#404040"]
        self.button_color = button_color if button_color is not None else self.text_colors[0]

        self.sg.theme_background_color(background_color)
        self.sg.theme_slider_color(self.sg.theme_background_color())

        self.right_click_selected_background = right_click_selected_background
        self.right_click_fontsize = right_click_fontsize

        self.sg.theme_input_background_color(input_background)

        self.initialwinsize = initialwinsize
        self.initialwinpos = initialwinpos
        self.search_results = search_results
        self.show_amount = show_amount
        self.max_title_display_len = max_title_display_len
        self.indices_visible = indices_visible
        self.show_all = show_all

        self.ensure_file_exists()

        self.load()

        self.initial_list = self.represent_as_list()

    def ensure_file_exists(self):
        if not os.path.isfile(self.savefile):
            self.save(force_write=True)

    def represent_as_list(self):
        return [self.fontsize, self.fonttype, self.text_colors, self.button_color, self.sg.theme_background_color(),
                self.right_click_selected_background, self.right_click_fontsize,
                self.sg.theme_input_background_color(), self.initialwinsize, self.initialwinpos, self.search_results,
                self.show_amount, self.max_title_display_len, self.indices_visible, self.show_all]

    def load(self):
        with open(self.savefile, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar="|")
            row = reader.__next__()
            self.fontsize = row[0]
            self.fonttype = row[1]
            self.text_colors = row[2].split("-")
            self.button_color = row[3]
            self.sg.theme_background_color(row[4])
            self.sg.theme_slider_color(self.sg.theme_background_color())
            self.right_click_selected_background = row[5]
            self.right_click_fontsize = int(row[6])
            self.sg.theme_input_background_color(row[7])

            windata = reader.__next__()
            self.initialwinsize = (int(windata[0]), int(windata[1]))
            self.initialwinpos = (int(windata[2]), int(windata[3]))

            searchdata = reader.__next__()
            self.search_results = int(searchdata[0])

            displaydata = reader.__next__()
            self.show_amount = int(displaydata[0])
            self.max_title_display_len = int(displaydata[1])

            state_data = reader.__next__()
            self.indices_visible = state_data[0] == "True"
            self.show_all = state_data[1] == "True"

    def save(self, force_write=False):
        if not force_write and self.initial_list == self.represent_as_list():
            return False

        with open(self.savefile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar="|")
            writer.writerow([self.fontsize, self.fonttype, "-".join(self.text_colors),
                             self.button_color, self.sg.theme_background_color(),
                             self.right_click_selected_background, self.right_click_fontsize,
                             self.sg.theme_input_background_color()])
            writer.writerow([*self.initialwinsize, *self.initialwinpos])
            writer.writerow([self.search_results])
            writer.writerow([self.show_amount, self.max_title_display_len])
            writer.writerow([self.indices_visible, self.show_all])
        return True
