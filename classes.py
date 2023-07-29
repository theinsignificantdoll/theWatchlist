from typing import Union, List, Any
import csv
import os
import webbrowser
import datetime
import time


class Show:
    weekday_to_int = {"mon": 0,
                      "tue": 1,
                      "wed": 2,
                      "thu": 3,
                      "fri": 4,
                      "sat": 5,
                      "sun": 6}

    def __init__(self, num_id: Union[str, int] = -1,
                 title: str = "",
                 ep: Union[str, int] = 0,
                 season: Union[str, int] = 1,
                 link: str = "",
                 weight: Union[str, int] = 0,
                 color: Union[str, int] = 0,
                 ep_season_relevant: Union[str, bool] = None,
                 release_info: str = "",
                 ongoing: Union[str, bool] = None,
                 last_dismissal: Union[str, float] = 0):

        self.id: int = int(num_id)
        self.title: str = title
        self.ep: int = int(ep)
        self.season: int = int(season)
        self.link: str = link
        self.weight: int = int(weight)
        self.color: int = int(color)
        self.release_info: str = release_info
        self.last_dismissal = float(last_dismissal)
        if ep_season_relevant is None:
            self.ep_season_relevant = True
        else:
            self.ep_season_relevant = ep_season_relevant if isinstance(ep_season_relevant, bool)\
                else ep_season_relevant == "True"
        if ongoing is None:
            self.ongoing = False
        else:
            self.ongoing = ongoing if isinstance(ongoing, bool) else ongoing == "True"

    def __repr__(self):
        return f"Show(num_id={self.id}, title={self.title.__repr__()}, ep={self.ep}," \
               f" season={self.season}, link={self.link.__repr__()}, weight={self.weight}," \
               f" color={self.color}, ep_season_relevant={self.ep_season_relevant}," \
               f" release_info={self.release_info.__repr__()}, ongoing={self.ongoing}," \
               f" last_dismissal={self.last_dismissal:.4f})"

    def open_link(self):
        webbrowser.open(self.link)

    def release_is_parseable(self):
        if self.parse_release_info():
            return True
        return False

    def check_release(self, grace_period: Union[int, float] = 24) -> bool:
        """
        Returns True if a show was released within - grace_period - hours
        NOTE: Returns False if not ongoing or release_info cannot be parsed.

        :param grace_period: The amount of hours after the release that the function should continue to return True
        :return: Whether or not show was released within grace_period.
        """
        if not self.ongoing\
           or self.last_dismissal + grace_period * 60 * 60 > time.time():
            return False

        parsed = self.parse_release_info()
        if not parsed:
            return False
        release_weekday, release_hour, release_minute = parsed
        now = datetime.datetime.now()
        current_weekday, current_hour, current_minute = now.weekday(), now.hour, now.minute

        if release_weekday == 7:
            days_since_release = 0
        elif release_weekday > current_weekday:
            days_since_release = 7 - (release_weekday - current_weekday)
        else:
            days_since_release = current_weekday - release_weekday

        hours_since_release = days_since_release * 24 + (current_hour - release_hour)
        hours_since_release += (current_minute - release_minute) / 60
        return hours_since_release <= grace_period

    def parse_release_info(self) -> Union[tuple[int, int, int], bool]:
        """
        Parses release_info. Note that weekday is converted to an integer, where monday is 0 and sunday is 6.
        If no weekday is given, the integer 7 is returned.
        If no time of day is given, the time is returned as 00:00

        Accepted formats:
        'Monday 20:20'   #  Note that ' ' is used as a delimiter between weekday and time of day.
        '6:55 Tuesday'   #  Note also that ':' is used as a delimiter between hours and minutes.
        'Monday'     # Both weekday and time of day are not required.
        '19:10'      # Although False is returned if neither is present.


        :return: A tuple of the release info. (weekday: int, hour: int, minute: int)
        """
        try:
            space_split = self.release_info.lower().split(" ")
            weekday = None
            hour = None
            minute = None
            for part in space_split:
                if part:
                    if part[0].isdigit():  # For time of day
                        hour, minute = (int(num) for num in part.split(":"))
                    else:  # For weekday
                        weekday = self.weekday_to_int[part[:3]]
            if weekday is None:
                weekday = 7
                if hour is None:
                    return False
            if hour is None:
                hour = 0
                minute = 0
            return weekday, hour, minute
        except (IndexError, KeyError, TypeError, ValueError):  # I don't know
            return False


def sort_list_of_shows_alphabetically(lst: List[Show], reverse=False) -> List[Show]:
    def get_title(show):
        return show.title

    lst.sort(key=get_title, reverse=reverse)
    return lst


class ShowsFileHandler:
    """
    Note: This class was made as a replacement to using a single list. Therefore this class acts like
    a list for the sake of backwards-compatibility.
    The list in question is equivalent to the list self.shows
    """
    def __init__(self, savefile="saved.csv", delimiter="\\"):
        self.savefile = savefile
        self.shows = []
        self.delimiter = delimiter

        self.ensure_file_exists()

        self.read_file()

    def ensure_file_exists(self):
        if not os.path.isfile(self.savefile):
            with open(self.savefile, "w"):
                pass

    def read_file(self) -> List[Show]:
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
                    ep_season_relevant=row[7] if len(row) > 7 else None,
                    release_info=row[8] if len(row) > 8 else "",
                    ongoing=row[9] if len(row) > 9 else None,
                    last_dismissal=row[10] if len(row) > 10 else 0,
                ))
        return self.shows

    def save(self):
        with open(self.savefile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar="|")
            for show in self.shows:
                writer.writerow([show.id, show.title, show.ep, show.season, show.link, show.weight, show.color,
                                 show.ep_season_relevant, show.release_info, show.ongoing, show.last_dismissal])

    def pop(self, __index) -> Show:
        return self.shows.pop(__index)

    def append(self, __object):
        self.shows.append(__object)

    def remove(self, __value):
        self.shows.remove(__value)

    def get_index(self, __object: Show) -> int:
        return self.shows.index(__object)

    def from_index(self, __index: Union[str, int]) -> Show:
        """
        Accepts strings
        """
        return self.shows[int(__index)]

    def __getitem__(self, item):
        return self.shows[item]

    def __setitem__(self, key, value):
        self.shows[key] = value

    def __iter__(self):
        return iter(self.shows)

    def __len__(self):
        return len(self.shows)

    def do_sorting(self, release_grace_period=0, weight_to_add=0):
        """
        Sorts self.shows according firstly to their weights and secondarily according to their
        titles alphabetically.

        :param release_grace_period: If this value is not 0, then recently released shows will have their weight
         increased by weight_to_add
        :param weight_to_add: The amount of weight that should be added to a show, when it is recently released.
        """

        def get_sorting_weight(show: Show) -> int:
            if release_grace_period and show.check_release(release_grace_period):
                return show.weight + weight_to_add
            return show.weight

        dct = {}
        for n in self.shows:
            weight = get_sorting_weight(n)
            if weight in dct:
                dct[weight].append(n)
                continue
            dct[weight] = [n]
        lt = []
        slist = []  # list of Weights used
        for n in dct:
            slist.append(int(n))
            dct[n].sort(key=lambda x: x.id)
        slist.sort()
        for n in slist:
            lt += sort_list_of_shows_alphabetically(dct[n], reverse=True)
        lt.reverse()

        self.shows = lt

    def highest_id(self) -> int:
        """
        Finds the highest id held by a show in self.shows

        :return: The highest id in self.shows
        :rtype: int
        """
        if len(self.shows) == 0:
            return -1
        return max([int(show.id) for show in self.shows])

    def from_id(self, target_id: Union[str, int]) -> Show:
        """
        Finds the show with the target id and returns it

        :param target_id: id of the show to be returned
        :return: The show with an id equivalent to target_id
        :rtype: Show
        """
        target_id = int(target_id)
        for show in self.shows:
            if show.id == target_id:
                return show
        raise KeyError


class Settings:
    """
    When adding new settings remember to update the following methods:
        .save
        .load
        .__init__
        .represent_as_list
    """
    def __init__(self, sg, savefile="settings.csv", delimiter="\\", fontsize=15, fonttype="Helvetica", text_colors=None,
                 button_color=None, background_color=None, right_click_selected_background="#252525",
                 right_click_fontsize=10, input_background=None, initialwinsize=(400, 200),
                 initialwinpos=(50, 50), search_results=3, show_amount=32,
                 max_title_display_len=0, indices_visible=True, show_all=False, shorten_with_ellipsis=True,
                 releases_visible=True, release_grace_period=24, default_text_color=None, default_font_size=11,
                 move_recently_released_to_top=True, weight_to_add=5):

        self.sg = sg
        # Note that some settings are not stored as attributes of this class, but are instead
        # written and read directly from the PySimpleGUI module

        self.savefile = savefile
        self.delimiter = delimiter

        self.fontsize = fontsize
        self.fonttype = fonttype
        self.text_colors = text_colors if text_colors is not None else [sg.theme_text_color(), "#404040"]
        self.button_color = button_color if button_color is not None else self.text_colors[0]

        self.sg.theme_background_color(background_color)

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
        self.shorten_with_ellpisis = shorten_with_ellipsis
        self.releases_visible = releases_visible
        self.release_grace_period = release_grace_period
        self.default_text_color = self.text_colors[0] if default_text_color is None else default_text_color
        self.default_font_size = default_font_size

        self.weight_to_add = weight_to_add
        self.move_recently_released_to_top = move_recently_released_to_top

        self._currently_saved_to_disk_list = []  # is initially updated when the savefile is loaded

        self.ensure_file_exists()

        self.load()

    def ensure_file_exists(self):
        if not os.path.isfile(self.savefile):
            self.save(force_write=True)

    def represent_as_list(self) -> List[Any]:
        """
        Returns a list of all the settings. Useful when checking whether or not settings have been edited.
        This function is used to define ._currently_saved_to_disk_list.
        """
        return [self.fontsize, self.fonttype, self.text_colors, self.button_color, self.sg.theme_background_color(),
                self.right_click_selected_background, self.right_click_fontsize,
                self.sg.theme_input_background_color(), self.initialwinsize, self.initialwinpos, self.search_results,
                self.show_amount, self.max_title_display_len, self.indices_visible, self.show_all,
                self.shorten_with_ellpisis, self.releases_visible, self.release_grace_period, self.default_text_color,
                self.default_font_size, self.move_recently_released_to_top, self.weight_to_add]

    def load(self):
        """
        Reads the settings file and reads it into memory. If any
        settings are missing from the file, it will also call .save(force_write=True).
        """
        with open(self.savefile, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar="|")

            missing_data = False

            row = reader.__next__()
            try:
                self.fontsize = row[0]
                self.fonttype = row[1]
                self.text_colors = row[2].split("-")
                self.button_color = row[3]
                self.sg.theme_background_color(row[4])
                self.right_click_selected_background = row[5]
                self.right_click_fontsize = int(row[6])
                self.sg.theme_input_background_color(row[7])
                self.default_text_color = row[8]
                self.default_font_size = row[9]
            except IndexError:
                missing_data = True

            windata = reader.__next__()
            try:
                self.initialwinsize = (int(windata[0]), int(windata[1]))
                self.initialwinpos = (int(windata[2]), int(windata[3]))
            except IndexError:
                missing_data = True

            searchdata = reader.__next__()
            try:
                self.search_results = int(searchdata[0])
            except IndexError:
                missing_data = True

            displaydata = reader.__next__()
            try:
                self.show_amount = int(displaydata[0])
                self.max_title_display_len = int(displaydata[1])
                self.release_grace_period = int(displaydata[2])
                self.weight_to_add = int(displaydata[3])
            except IndexError:
                missing_data = True

            state_data = reader.__next__()
            try:
                self.indices_visible = state_data[0] == "True"
                self.show_all = state_data[1] == "True"
                self.shorten_with_ellpisis = state_data[2] == "True"
                self.releases_visible = state_data[3] == "True"
                self.move_recently_released_to_top = state_data[4] == "True"
            except IndexError:
                missing_data = True

        if missing_data:
            self.save(force_write=True)
            return
        self._currently_saved_to_disk_list = self.represent_as_list()

    def save(self, force_write=False) -> bool:
        """
        Checks if settings have changed, subsequently saving if they have.
        Returns True if something has been written to disk else False

        :param force_write: Skips the check of whether or not settings have been changed
        :type force_write: bool
        :return: True if something was written to the disk
        """
        if not force_write and self._currently_saved_to_disk_list == self.represent_as_list():
            return False

        with open(self.savefile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar="|")
            writer.writerow([self.fontsize, self.fonttype, "-".join(self.text_colors),
                             self.button_color, self.sg.theme_background_color(),
                             self.right_click_selected_background, self.right_click_fontsize,
                             self.sg.theme_input_background_color(), self.default_text_color,
                             self.default_font_size])
            writer.writerow([*self.initialwinsize, *self.initialwinpos])
            writer.writerow([self.search_results])
            writer.writerow([self.show_amount, self.max_title_display_len, self.release_grace_period,
                             self.weight_to_add])
            writer.writerow([self.indices_visible, self.show_all, self.shorten_with_ellpisis, self.releases_visible,
                             self.move_recently_released_to_top])

        self._currently_saved_to_disk_list = self.represent_as_list()
        return True

    def get_color(self, index) -> str:
        return self.text_colors[index % len(self.text_colors)]
