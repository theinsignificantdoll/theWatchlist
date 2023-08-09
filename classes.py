from typing import Union, List, Any
import csv
import os
import webbrowser
import datetime
import time
from notifypy import Notify

import default_values as val

weekday_to_int = {"mon": 0,
                  "tue": 1,
                  "wed": 2,
                  "thu": 3,
                  "fri": 4,
                  "sat": 5,
                  "sun": 6}


def parse_release_info(release_info) -> Union[tuple[int, int, int], tuple[tuple[int, int, int], int, int], bool]:
    """
    Parses release_info. Note that weekday is converted to an integer, where monday is 0 and sunday is 6.
    If no weekday is given, the integer 7 is returned.
    If no time of day is given, the time is returned as 00:00
    If neither is given, then False is returned.

    Accepted formats:
    'Monday 20:20'   #  Note that ' ' is used as a delimiter between weekday and time of day.
    '6:55 Tuesday'   #  Note also that ':' is used as a delimiter between hours and minutes.
    'Monday'         # Both weekday and time of day are not required.
    '19:10'          # Although False is returned if neither is present.
    '.24 10:10'      # Integers prefixed by '.' are returned as the day (i.e. 24th)
    '/9 .24'         # Integers prefixed by '/' are returned as the month
    '<2024 /9 .24'   # Integers prefixed by "<" are returned as the year.
                     # Also note that for dates, the previous resolution must be present. I.e. There cannot be defined
                     # a month if day is not defined. Moreover, if year is to be defined, then
                     # so must day and month also be
    'tUE 06:05' would also be accepted, as extra zeros and more than three letters is ignored.

    Both weekday and date cannot be used at the same time. Weekday is prioritised.
    If date is used, then the first item in the return tuple will be a tuple of (day, month, year)

    :return: A tuple of the release info. (weekday: int, hour: int, minute: int) or False
    """
    try:
        space_split = release_info.lower().split(" ")
        weekday = None
        hour = None
        minute = None
        day = 0
        month = 0
        year = 0
        for part in space_split:
            if part:
                if part[0].isdigit():  # For time of day
                    hour, minute = (int(num) for num in part.split(":"))
                elif part[0].isalpha():  # For weekday
                    weekday = weekday_to_int[part[:3]]
                else:  # for day, month and year.
                    if part[0] == ".":
                        day = int(part[1:])
                    elif part[0] == "/":
                        month = int(part[1:])
                    elif part[0] == "<":
                        year = int(part[1:])

        date_month_year_is_defined = day + month + year != 0
        if (year != 0 and (day == 0 or month == 0)) \
                or (month != 0 and day == 0):
            return False

        if weekday is None:
            weekday = 7
            if hour is None and not date_month_year_is_defined:
                return False

        if hour is None:
            hour = 0
            minute = 0

        if weekday != 7 or not date_month_year_is_defined:
            return weekday, hour, minute
        return (day, month, year), hour, minute
    except (IndexError, KeyError, TypeError, ValueError):  # I don't know which Errors might appear,
        return False  # and it doesn't really matter. It should just return False if release_info can't be parsed.


def hours_since_weekly(past_weekday: int, past_hour: int, past_minute: int, date_obj: datetime.datetime) -> float:
    """
    Calculates the amount of hours inbetween a certain time of day on a certain weekday and a datetime.datetime object
    Note that it doesn't calculate the time inbetween points in time, but rather reoccuring points of time in a week.

    If you'd like to use this function with two datetime objects, see hours_since_two_datetime()

    :param past_weekday: A weekday as an integer, where monday is 0 and sunday 6. 7 means - today -.
    :param past_hour: The hour on the weekday
    :param past_minute: The minute during the hour on the weekday
    :param date_obj: The future as a datetime object
    """

    future_weekday, future_hour, future_minute = date_obj.weekday(), date_obj.hour, date_obj.minute

    if past_weekday == 7:
        days_since_release = 0
    elif past_weekday > future_weekday:
        days_since_release = 7 - (past_weekday - future_weekday)
    elif past_weekday < future_weekday:
        days_since_release = future_weekday - past_weekday
    else:
        if past_hour < future_hour:
            days_since_release = 0
        elif past_hour > future_hour:
            days_since_release = 7
        else:
            if past_minute > future_minute:
                days_since_release = 7
            else:
                days_since_release = 0

    hours_since_release = days_since_release * 24 + (future_hour - past_hour)
    hours_since_release += (future_minute - past_minute) / 60
    return hours_since_release


def hours_since_not_weekly(past_date_tuple: int,
                           past_hour: int,
                           past_minute: int,
                           date_obj: datetime.datetime) -> float:
    """
    :param past_date_tuple: a tuple of (day, month, year) - where zero means insignificant
    :param past_hour: The hour on the weekday
    :param past_minute: The minute during the hour on the weekday
    :param date_obj: The future as a datetime object
    :return: The amount of hours before date_obj that the past date occured. Returns a negative number, if it has
    yet to occur.
    """
    past_day, past_month, past_year = past_date_tuple

    if past_month == 0:
        if past_day > date_obj.day:
            past_month = date_obj.month - 1
        elif past_day == date_obj.day:
            if past_hour > date_obj.hour:
                past_month = date_obj.month - 1
            elif past_hour == date_obj.hour:
                if past_minute >= date_obj.minute:
                    past_month = date_obj.month - 1
                else:
                    past_month = date_obj.month
            else:
                past_month = date_obj.month
        else:
            past_month = date_obj.month

    if past_year == 0:
        if past_month > date_obj.month:
            past_year = date_obj.year - 1
        elif past_month == date_obj.month:
            if past_day > date_obj.day:
                past_year = date_obj.year - 1
            elif past_day == date_obj.day:
                if past_hour > date_obj.hour:
                    past_year = date_obj.year - 1
                elif past_hour == date_obj.hour:
                    if past_minute >= date_obj.minute:
                        past_year = date_obj.year - 1
                    else:
                        past_year = date_obj.year
                else:
                    past_year = date_obj.year
            else:
                past_year = date_obj.year
        else:
            past_year = date_obj.year
    past = datetime.datetime(year=past_year, month=past_month, day=past_day, hour=past_hour, minute=past_minute)

    return hours_since_two_datetime_not_weekly(past, date_obj)


def hours_till_weekly(future_weekday: int,
                      future_hour: int,
                      future_minute: int,
                      date_obj: datetime.datetime) -> float:
    """
    Calculates the number of hours until the future parameters are fulfilled from the date_obj.
    """
    past_weekday = date_obj.weekday()
    days_to_release = 0
    if future_weekday == 7:
        pass
    elif future_weekday == past_weekday:
        if future_hour < date_obj.hour:
            days_to_release = 7
        elif future_hour > date_obj.hour:
            days_to_release = 0
        else:
            if future_minute < date_obj.minute:
                days_to_release = 7
            else:
                days_to_release = 0
    elif future_weekday < past_weekday:
        days_to_release = 7 - (past_weekday - future_weekday)
    elif future_weekday > past_weekday:
        days_to_release = future_weekday - past_weekday

    return days_to_release * 24 + future_hour - date_obj.hour + (future_minute - date_obj.minute) / 60


def hours_till_not_weekly(future_date_tuple: tuple[int, int, int],
                          future_hour: int,
                          future_minute: int,
                          date_obj: datetime.datetime) -> float:
    """
    Calculates the number of hours till the future parameters are fulfilled from date_obj

    :param future_date_tuple: a tuple of (day, month, year) - where zero means insignificant
    :param future_hour: The hour
    :param future_minute: The minute
    :param date_obj: The past as a datetime.datetime object
    :return: The hours from date_obj till the future parameters are met.
    """
    future_day, future_month, future_year = future_date_tuple

    if future_month == 0:
        if future_day < date_obj.day:
            future_month = date_obj.month + 1
        elif future_day == date_obj.day:
            if future_hour < date_obj.hour:
                future_month = date_obj.month + 1
            elif future_hour == date_obj.hour:
                if future_minute <= date_obj.minute:
                    future_month = date_obj.month + 1
                else:
                    future_month = date_obj.month
            else:
                future_month = date_obj.month
        else:
            future_month = date_obj.month

    if future_year == 0:
        if future_month < date_obj.month:
            future_year = date_obj.year + 1
        elif future_month == date_obj.month:
            if future_day < date_obj.day:
                future_year = date_obj.year + 1
            elif future_day == date_obj.day:
                if future_hour < date_obj.hour:
                    future_year = date_obj.year + 1
                elif future_hour == date_obj.hour:
                    if future_minute <= date_obj.minute:
                        future_year = date_obj.year + 1
                    else:
                        future_year = date_obj.year
                else:
                    future_year = date_obj.year
            else:
                future_year = date_obj.year
        else:
            future_year = date_obj.year

    future = None
    for i in range(31):  # This for loop makes it so that if a day is given, but that day is not present in the month
        # then the day will default to the maximum value.
        # Example: 31. September will be turned into 30. September.
        try:
            future = datetime.datetime(year=future_year, month=future_month, day=future_day-i,
                                       hour=future_hour, minute=future_minute)
            break
        except ValueError:
            pass
    if future is None:  # This will probably never be True, but if it is, at least nothing will crash
        return 0

    return hours_since_two_datetime_not_weekly(date_obj, future)


def hours_since_two_datetime_not_weekly(past: datetime.datetime, future: datetime.datetime) -> float:
    """
    :param past: The past-most datetime object
    :param future: The future-most datetime object
    :return: How many hours have passed between the two points in time.
    """
    delta: datetime.timedelta = future - past
    return delta.days * 24 + delta.seconds / 3600


def hours_since_two_datetime_weekly(past_date: datetime.datetime, future_date: datetime.datetime) -> float:
    """
    Note that day. month and year is ignored. The only thing that matters is weekday, hour and minute.
    """
    weekday = past_date.weekday()
    return hours_since_weekly(weekday, past_date.hour, past_date.minute, future_date)


def release_is_parseable(release_info) -> bool:
    """
    Checks whether a release follows the proper syntax.? (is that the word)
    """
    if parse_release_info(release_info):
        return True
    return False


class Show:
    def __init__(self,
                 num_id: Union[str, int] = -1,
                 title: str = "",
                 ep: Union[str, int] = 0,
                 season: Union[str, int] = 1,
                 link: str = "",
                 weight: Union[str, int] = 0,
                 color: Union[str, int] = 0,
                 ep_season_relevant: Union[str, bool] = None,
                 release_info: str = "",
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

        self.is_recently_released = False
        self.auto_open_link_on_release = False

        if ep_season_relevant is None:
            self.ep_season_relevant = True
        else:
            self.ep_season_relevant = ep_season_relevant if isinstance(ep_season_relevant, bool)\
                else ep_season_relevant == "True"

    def __repr__(self):
        return f"Show(num_id={self.id}, title={self.title.__repr__()}, ep={self.ep}," \
               f" season={self.season}, link={self.link.__repr__()}, weight={self.weight}," \
               f" color={self.color}, ep_season_relevant={self.ep_season_relevant}," \
               f" release_info={self.release_info.__repr__()}," \
               f" last_dismissal={self.last_dismissal:.4f})"

    def open_link(self):
        """
        Opens the link of the show in a browser
        """
        if self.link:
            webbrowser.open(self.link)

    def send_release_notification(self):
        """
        Sends a notification saying the shows has just been released.
        """
        notif = Notify(default_notification_title="New Release!",
                       default_notification_message=f"'{self.title}' has just been released!",
                       default_notification_application_name="thWatchlist",
                       default_notification_icon="GenIko.ico")
        notif.send(block=False)

    def hours_to_release(self) -> float:
        """
        Calculates the number of hours until this show is released.
        Moreover, the return is rounded to three digits or, in other words, 3.6 seconds. This means
        that the returned value will mostly (way, way more often than not) be equivalent between shows
        with the same release_info, assuming that the method is called at nearly the same time.
        """
        parsed = parse_release_info(self.release_info)
        if not parsed:
            return 0

        now = datetime.datetime.now()

        round_to = 3

        if isinstance(parsed[0], tuple):
            date_tuple, hour, minute = parsed
            return round(hours_till_not_weekly(date_tuple, hour, minute, now), round_to)
        else:
            release_weekday, release_hour, release_minute = parsed
            return round(hours_till_weekly(release_weekday, release_hour, release_minute, now), round_to)

    def string_time_till_release(self) -> str:
        if not self.release_info or self.is_recently_released:
            return ""
        to_release = self.hours_to_release()
        if to_release <= 1:
            return f"{int(to_release * 60 + 0.5)}m"
        elif to_release <= 24:
            return f"{int(to_release + 0.5)}h"
        elif to_release <= 168:
            return f"{int(to_release / 24 + 0.5)}d"
        elif to_release <= 8760:
            return f"{int(to_release / 168 + 0.5)}w"
        return f"{int(to_release / 8760 + 0.5)}y"

    def check_release(self, grace_period: Union[int, float] = 24) -> bool:
        """
        Returns True if a show was released within - grace_period - hours. grace_period is ignored, if it is 0
        NOTE: Also returns False if release_info cannot be parsed, the show has been dismissed AFTER the last release
        or if the show has yet to ever be released (In the case of non-repeating releases).

        :param grace_period: The amount of hours after the release that the function should continue to return True
        :return: Whether show was released within grace_period.
        """

        if not self.release_info:
            self.is_recently_released = False
            return self.is_recently_released

        parsed = parse_release_info(self.release_info)
        if not parsed:
            self.is_recently_released = False
            return self.is_recently_released
        now = datetime.datetime.now()

        if isinstance(parsed[0], tuple):
            date_tuple, hour, minute = parsed
            hours_since_release = hours_since_not_weekly(date_tuple, hour, minute, now)
        else:
            release_weekday, release_hour, release_minute = parsed
            hours_since_release = hours_since_weekly(release_weekday, release_hour, release_minute, now)

        if self.last_dismissal > 1:
            hours_since_dismissal = hours_since_two_datetime_weekly(datetime.
                                                                    datetime.fromtimestamp(self.last_dismissal), now)
            if hours_since_dismissal < hours_since_release or hours_since_release < 0:
                self.is_recently_released = False
                return self.is_recently_released

        self.is_recently_released = hours_since_release <= grace_period or grace_period == 0
        return self.is_recently_released


class ShowsFileHandler:
    """
    Note: This class was made as a replacement to using a single list, therefore this class acts like
    a list for the sake of backwards-compatibility.
    The list in question is equivalent to the list self.shows
    """
    def __init__(self, settings, savefile=val.show_file, delimiter=val.csv_delimiter):
        self.savefile = savefile
        self.shows = []
        self.delimiter = delimiter
        self.settings: Settings = settings

        self.ensure_file_exists()

        self.read_file()

    def ensure_file_exists(self):
        """
        Checks if the save file exists. If not, the file is created.
        """
        if not os.path.isfile(self.savefile):
            with open(self.savefile, "w"):
                pass

    def read_file(self) -> List[Show]:
        """
        Reads the save file into memory and therefore updates self.shows
        """
        self.shows = []
        with open(self.savefile, newline="") as csvfile:
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
                    last_dismissal=row[9] if len(row) > 9 else 0,
                ))
        self.check_all_releases(allow_notifications=False)
        return self.shows

    def save(self):
        """
        Writes the current self.shows to disk.
        """
        with open(self.savefile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar="|")
            for show in self.shows:
                writer.writerow([show.id, show.title, show.ep, show.season, show.link, show.weight, show.color,
                                 show.ep_season_relevant, show.release_info, show.last_dismissal])

    def pop(self, __index) -> Show:
        """
        Intermediary method allowing for list-like behavior
        """
        return self.shows.pop(__index)

    def append(self, __object):
        """
        Intermediary method allowing for list-like behavior
        """
        self.shows.append(__object)

    def remove(self, __value):
        """
        Intermediary method allowing for list-like behavior
        """
        self.shows.remove(__value)

    def get_index(self, __object: Show) -> int:
        """
        Retrieves the index of a given show
        """
        return self.shows.index(__object)

    def from_index(self, __index: Union[str, int]) -> Show:
        """
        Retrieves a show from index. Notably, this function accepts strings AND integers.
        """
        return self.shows[int(__index)]

    def __getitem__(self, item):
        """
        Intermediary method allowing for list-like behavior
        """
        return self.shows[item]

    def __setitem__(self, key, value):
        """
        Intermediary method allowing for list-like behavior
        """
        self.shows[key] = value

    def __iter__(self):
        """
        Intermediary method allowing for list-like behavior
        """
        return iter(self.shows)

    def __len__(self):
        """
        Intermediary method allowing for list-like behavior
        """
        return len(self.shows)

    def check_all_releases(self, allow_notifications=True):
        for show in self.shows:
            prev_status = show.is_recently_released
            show.check_release(self.settings.release_grace_period)

            if allow_notifications and self.settings.send_notifications \
               and True is show.is_recently_released != prev_status:
                show.send_release_notification()

            if True is show.is_recently_released != prev_status and show.auto_open_link_on_release:
                show.open_link()
                show.auto_open_link_on_release = False

    def do_sorting(self, weight_to_add=0, sort_by_upcoming=False):
        """
        Sorts self.shows according firstly to their weights and secondarily according to their
        titles alphabetically. However, if sort_by_upcoming is true, the shows are secondarily sorted by time until
        release instead of alphabetically. If the release info is the same, then they are sorted alphabetically.

        :param weight_to_add: The amount of weight that should be added to a show when it is recently released.
        :param sort_by_upcoming: If True, shows of the same weight will be sorted based on when a new release is coming.
        """
        def get_sorting_weight(show: Show) -> int:
            if show.is_recently_released:
                return -show.weight - weight_to_add
            return -show.weight

        def main_key(show: Show):
            return get_sorting_weight(show), show.title

        def upcoming_key(show: Show):
            """
            Returns a key, that, when given to the .sort method, will properly sort the shows. This proper sorting is as
            follows:
            Firstly, according to the sorting weight of the shows.
            Secondly, shows that are currently released are placed at the top.
            Thirdly, According how long there is until their release. Note that shows without a release schedule are
                sorted as if they are going to be released in an infinite amount of time.
            Fourthly, alphabetically (According to show.title).
            """
            to_release = show.hours_to_release()
            if show.is_recently_released:
                return get_sorting_weight(show), 0, to_release if to_release != 0.0 else 99999999, show.title
            return get_sorting_weight(show), 1 if to_release > 0 else 2, to_release, show.title

        if sort_by_upcoming:
            self.shows.sort(key=upcoming_key)
        else:
            self.shows.sort(key=main_key)

    def new_text_colors(self, old: List[str], new: List[str]):
        """
        Changes the .color index of shows to match a new text_colors according to the following rules:

        When the possible text colors are changed, shows should keep the same color, if it has not been removed.
        Otherwise, they should keep their current text_color index - unless this index is not present in the new
        text_colors. In this case, the color index of the show should be 0.

        :param old: The old text_colors
        :param new: The new text_colors
        """
        for show in self.shows:
            try:
                show.color = new.index(old[show.color])
            except ValueError:
                if show.color < len(new):
                    continue
                show.color = 0

    def highest_id(self) -> int:
        """
        Finds the highest id held by a show in self.shows

        :return: The highest id in self.shows
        """
        if len(self.shows) == 0:
            return -1
        return max([int(show.id) for show in self.shows])

    def from_id(self, target_id: Union[str, int]) -> Show:
        """
        Finds the show with the target id and returns it

        :param target_id: id of the show to be returned
        :return: The show with an id equivalent to target_id
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

        and the default_values.py (imported as val) file.
    """
    def __init__(self, sg,
                 savefile=val.settings_file,
                 delimiter=val.csv_delimiter,
                 fontsize=val.fontsize,
                 fonttype=val.fonttype,
                 text_colors=val.text_colors,
                 button_color=val.button_color,
                 background_color=val.background_color,
                 right_click_selected_background=val.right_click_selected_background,
                 right_click_fontsize=val.right_click_fontsize,
                 input_background=val.input_background,
                 initialwinsize=val.initialwinsize,
                 initialwinpos=val.initialwinpos,
                 search_results=val.search_results,
                 show_amount=val.show_amount,
                 max_title_display_len=val.max_title_display_len,
                 indices_visible=val.indices_visible,
                 show_all=val.show_all,
                 shorten_with_ellipsis=val.shorten_with_ellipsis,
                 releases_visible=val.releases_visible,
                 release_grace_period=val.release_grace_period,
                 default_text_color=val.default_text_color,
                 default_font_size=val.default_fontsize,
                 move_recently_released_to_top=val.move_recently_released_to_top,
                 weight_to_add=val.weight_to_add,
                 sort_by_upcoming=val.sort_by_upcoming,
                 secondary_show_background=val.secondary_show_background,
                 enable_secondary_show_background=val.enable_secondary_show_background,
                 send_notifications=val.send_notifications,
                 show_till_release=val.show_till_release):

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
        self.sort_by_upcoming = sort_by_upcoming
        self.secondary_show_background = secondary_show_background
        self.enable_secondary_show_background = enable_secondary_show_background
        self.send_notifications = send_notifications
        self.show_till_release = show_till_release

        self._currently_saved_to_disk_list = []  # is initially updated when the savefile is loaded

        self.ensure_file_exists()

        self.load()

    def ensure_file_exists(self):
        """
        Checks whether the save file exists. If not, the file is created with the initital parameters used to
        create the object.
        """
        if not os.path.isfile(self.savefile):
            self.save(force_write=True)

    def represent_as_list(self) -> List[Any]:
        """
        Returns a list of all the settings. Useful when checking whether settings have been edited.
        This function is used to define ._currently_saved_to_disk_list.
        """
        return [self.fontsize, self.fonttype, self.text_colors, self.button_color, self.sg.theme_background_color(),
                self.right_click_selected_background, self.right_click_fontsize,
                self.sg.theme_input_background_color(), self.initialwinsize, self.initialwinpos, self.search_results,
                self.show_amount, self.max_title_display_len, self.indices_visible, self.show_all,
                self.shorten_with_ellpisis, self.releases_visible, self.release_grace_period, self.default_text_color,
                self.default_font_size, self.move_recently_released_to_top, self.weight_to_add, self.sort_by_upcoming,
                self.secondary_show_background, self.enable_secondary_show_background, self.send_notifications,
                self.show_till_release]

    def load(self):
        """
        Reads the settings file and reads it into memory. If any
        settings are missing from the file, it will also call .save(force_write=True).
        """
        with open(self.savefile, newline="") as csvfile:
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
                self.secondary_show_background = row[10]
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
                self.sort_by_upcoming = state_data[5] == "True"
                self.enable_secondary_show_background = state_data[6] == "True"
                self.send_notifications = state_data[7] == "True"
                self.show_till_release = state_data[8] == "True"
            except IndexError:
                missing_data = True

        if missing_data:
            self.save(force_write=True)
            return
        self._currently_saved_to_disk_list = self.represent_as_list()

    def save(self, force_write: bool = False) -> bool:
        """
        Checks if settings have changed, subsequently saving if they have.
        Returns True if something has been written to disk else False

        :param force_write: Skips the check of whether settings have been changed
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
                             self.default_font_size, self.secondary_show_background])
            writer.writerow([*self.initialwinsize, *self.initialwinpos])
            writer.writerow([self.search_results])
            writer.writerow([self.show_amount, self.max_title_display_len, self.release_grace_period,
                             self.weight_to_add])
            writer.writerow([self.indices_visible, self.show_all, self.shorten_with_ellpisis, self.releases_visible,
                             self.move_recently_released_to_top, self.sort_by_upcoming,
                             self.enable_secondary_show_background, self.send_notifications, self.show_till_release])

        self._currently_saved_to_disk_list = self.represent_as_list()
        return True

    def get_color(self, index) -> str:
        """
        Retrieves a color from index. Notably this function doesn't throw an IndexError if the index is too large.
        """
        return self.text_colors[index % len(self.text_colors)]
