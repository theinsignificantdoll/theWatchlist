from typing import List, Union
from classes import Show, ShowsFileHandler, Settings

# noinspection PyPep8Naming
import PySimpleGUI as sg
import mouse
import time

sg.theme("DarkBrown4")

savefile = "saved.csv"
settingsfile = "settings.csv"
delimiter = "\\"

recently_released_string = "✓"

# The number of seconds in between a change being made to a show and the change being saved. Accepts floats
delay_to_save_shows = 3

# The maximum amount of seconds inbetween checking the release state of shows.
update_release_vals_interval = 15 * 60


def is_valid_color(color: str):
    """
    Checks whether or not a string is a hex color code

    :param color: A string
    :return: Returns True if the string col is a proper hex color code, such as "#FFFFFF"
    """
    if len(color) == 7:
        if color[0] == "#":
            for n in color[1:]:
                if (48 <= ord(n) <= 57) or (65 <= ord(n) <= 70) or (97 <= ord(n) <= 102):
                    return True
                return False
    return False


def limit_string_len(string: str, length: int, use_ellipsis: bool = False):
    """
    Shortens a string so that its length doesn't exceed some integer. If the maximum length is 0, nothing is shortened.

    :param string: The string to limit
    :param length: The maximum length of the string
    :param use_ellipsis: Whether or not the last three characters should be ... if the string has been shortened
    :return: A string with a maximum length of - length -
    :rtype: str
    """
    if len(string) > length != 0:
        if use_ellipsis:
            return f"{string[:length - 3].rstrip(' ')}..."
        return string[:length]
    return string


def show_properties(title: str = "Show Editor", show: Show = None, show_purge: bool = False):
    """
    Opens a small window with all the relevant information about a show allowing these to be changed by the user.
    Then returning the show, if save was pressed and False if Cancel was pressed.
    If no show is None, then the function returns a dummy show with all the appropriate values and an id of -1.

    :param title: Title of the window
    :param show: If given, then all values will be changed in this show.
    :param show_purge: Whether or not to show the Purge Weight input field
    :return: True if something has been changed and False if nothing has been changed.
    :rtype: Union[bool, Show]
    """
    if show is None:  # make a dummy show.
        show = Show(ep_season_relevant=True, ongoing=True)
    window = sg.Window(title,
                       [
                           [sg.Column([
                               [sg.T("Title")],
                               [sg.InputText(show.title, key="show_title")]
                           ]),
                               sg.Column([
                                   [sg.T("Episode")],
                                   [sg.InputText(show.ep, key="show_ep", size=(8, 1))]
                               ]),
                               sg.Column([
                                   [sg.T("Season")],
                                   [sg.InputText(show.season, key="show_season", size=(8, 1))]
                               ]),
                               sg.Column([
                                   [sg.T("Link")],
                                   [sg.InputText(show.link, key="show_link", size=(15, 1))]
                               ]),
                               sg.Column([
                                   [sg.T("Weight")],
                                   [sg.InputText(show.weight, key="show_weight")]
                               ]),
                               sg.Column([
                                   [sg.T("Show Details")],
                                   [sg.Checkbox("", default=show.ep_season_relevant,
                                                key="show_ep_season_relevant")]
                               ])
                           ],
                           [sg.HSep()],
                           [sg.Column([
                               [sg.T("Release Info")],
                               [butt(show.release_info, key="show_release_info",
                                     tooltip="Expected format example: 'MON-20:00'",
                                     size=(9, 1))]
                           ]),
                               sg.Column([
                                   [sg.T("Ongoing")],
                                   [sg.Checkbox("", default=show.ongoing,
                                                key="show_ongoing")]
                               ]),
                               sg.Push(),
                               sg.Column([
                                   [sg.T("Purge Weight")],
                                   [sg.InputText(key="purge_weight",
                                                 tooltip="If a weight is written in this field, then ongoing\n"
                                                         "WILL be set to False and Release Info will be cleared\n"
                                                         "As such this field is useful for quickly discarding\n"
                                                         "shows, once they have been finished.")]
                               ]) if show_purge else sg.T()
                           ],
                           [sg.Button("Save", bind_return_key=True), sg.Button("Cancel")]],
                       disable_close=True,
                       auto_size_buttons=True,
                       auto_size_text=True,
                       default_element_size=(12, 1),
                       font=(settings.fonttype, int(settings.fontsize)))

    release_info = show.release_info
    while True:
        button, data = window.read()
        if button == "show_release_info":
            release_info = get_release_string(show.release_info)
            window["show_release_info"].update(release_info)
        else:
            break
    window.close()

    if button == "Cancel":
        return False

    purge_weight = False
    if "purge_weight" in data and data["purge_weight"]:
        try:
            purge_weight = int(data["purge_weight"])
        except TypeError:
            sg.popup_error(title="Purge not an integer")

    try:
        # Check whether or not the user given values are valid BEFORE making any changes to the show.
        data["show_ep"] = int(data["show_ep"])
        data["show_season"] = int(data["show_season"])
        data["show_weight"] = int(data["show_weight"])
    except ValueError:
        sg.popup_error(title="Couldn't convert to integer")
        return False

    show.title = data["show_title"]
    show.ep = data["show_ep"]
    show.season = data["show_season"]
    show.link = data["show_link"]
    show.ep_season_relevant = data["show_ep_season_relevant"]

    if purge_weight is False:
        show.release_info = release_info
        show.ongoing = data["show_ongoing"]
        show.weight = data["show_weight"]
    else:
        show.release_info = ""
        show.ongoing = False
        show.weight = purge_weight

    return show


def butt(button_text="", key=None, tooltip=None, butt_color=(False, None), border_width=None, size=(None, None),
         mouseover_colors=sg.theme_background_color(), disabled=False, right_click_menu=None, bind_return_key=False):
    """
    A wrapper function for sg.Button with some different default values

    :rtype: sg.Button
    """
    if not butt_color[0]:
        butt_color = (settings.button_color, butt_color[1])
    return sg.Button(button_text=button_text, key=key, tooltip=tooltip, button_color=butt_color,
                     border_width=border_width, size=size, mouseover_colors=mouseover_colors, disabled=disabled,
                     right_click_menu=right_click_menu, bind_return_key=bind_return_key)


def get_release_string(initial_release_string=""):
    temp_show = Show(release_info=initial_release_string)
    parsed = temp_show.parse_release_info()
    if parsed:
        weekday, hour, minute = parsed
    else:
        weekday = 0
        hour = 0
        minute = 0
    layout = [
        [sg.Push(), butt("MON"), butt("TUE"), butt("WED"), butt("THU"), butt("FRI"), butt("SAT"), butt("SUN"),
         sg.Push()],
        [sg.Push(), sg.I(hour, key="hour", enable_events=True), sg.T(":"),
         sg.I(minute, key="minute", enable_events=True), sg.Push()],
        [butt("Save", bind_return_key=True), butt("Cancel"), sg.Push(),
         sg.T(initial_release_string, key="release_string")]
    ]

    weekday_as_string = ""

    rel_win = sg.Window("Release Picker", layout=layout, default_element_size=(9, 1),
                        font=(settings.fonttype, settings.fontsize))

    def write_release_string():
        rel_win["release_string"].update(value=f"{weekday_as_string} {hour}:{0 if minute < 10 else ''}{minute}")

    while True:
        event, values, = rel_win.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            rel_win.close()
            return initial_release_string
        elif event == "Save":
            rel_win.close()
            return rel_win["release_string"].get()
        elif event == "hour":
            try:
                hour = int(values["hour"])
            except ValueError:
                hour = 0
            write_release_string()
        elif event == "minute":
            try:
                minute = int(values["minute"])
            except ValueError:
                minute = 0
            write_release_string()
        elif event == "MON":
            weekday_as_string = "MON"
            write_release_string()
        elif event == "TUE":
            weekday_as_string = "TUE"
            write_release_string()
        elif event == "WED":
            weekday_as_string = "WED"
            write_release_string()
        elif event == "THU":
            weekday_as_string = "THU"
            write_release_string()
        elif event == "FRI":
            weekday_as_string = "FRI"
            write_release_string()
        elif event == "SAT":
            weekday_as_string = "SAT"
            write_release_string()
        elif event == "SUN":
            weekday_as_string = "SUN"
            write_release_string()


class MainWin:
    def __init__(self, main_loop=False):
        """
        Initialises the main PySimpleGUI window

        :param main_loop: Calls self.main_loop() if true
        :type main_loop: bool
        """
        global should_restart

        self.shouldbreak = False

        sg.theme_text_color(settings.text_colors[0])
        sg.theme_element_text_color(settings.button_color)
        sg.theme_element_background_color(sg.theme_background_color())
        sg.theme_text_element_background_color(sg.theme_background_color())
        sg.theme_slider_color(sg.theme_background_color())
        sg.theme_button_color((settings.button_color, sg.theme_background_color()))

        self.delete_elements = []
        self.title_elements = []
        self.ep_minus_elements = []
        self.ep_plus_elements = []
        self.season_minus_elements = []
        self.season_plus_elements = []
        self.link_elements = []
        self.properties_elements = []
        self.index_elements = []
        self.release_elements = []

        self.number_of_displayed_shows = len(shows) if settings.show_all else min(len(shows), settings.show_amount)

        self.shows_col = sg.Col([[self.delete_element(ind),
                                  self.title_element(ind),
                                  self.ep_minus_element(ind),
                                  self.ep_plus_element(ind),
                                  self.season_minus_element(ind),
                                  self.season_plus_element(ind),
                                  self.link_element(ind),
                                  self.properties_element(ind),
                                  self.index_element(ind),
                                  self.release_element(ind)] for ind in range(self.number_of_displayed_shows)],
                                vertical_scroll_only=True,
                                scrollable=True,
                                expand_x=True,
                                expand_y=True)
        self.shows_col_contents_changed = False
        self.number_of_invisible_rows = 0
        self.last_release_update = 0

        topcol = [[butt(" + ", key="add_show", border_width=0, tooltip="Add a show to the list"),
                   butt(" ⛭ ", key="preferences", border_width=0, tooltip="Preferences"),
                   butt(" ⮝ " if settings.show_all else " ⮟ ", key="show_all", border_width=0,
                        tooltip="Show less (faster)" if settings.show_all else "Show more (slower)"),
                   butt(" 🔍 ", key="search_button", border_width=0, tooltip="Search"),
                   sg.Checkbox(" ", key="index_checkbox", text_color=settings.button_color,
                               tooltip="Enables or disables the showing of indices",
                               default=settings.indices_visible, enable_events=True),
                   sg.Checkbox(" ", key="release_checkbox", text_color=settings.button_color,
                               tooltip="Enables or disables the showing of release info",
                               default=settings.releases_visible, enable_events=True)
                   ]]

        layout = [
            [sg.Col(topcol)],
            [self.shows_col],
        ]

        # noinspection PyTypeChecker
        self.win = sg.Window(title="Watchlist", layout=layout, auto_size_text=True, auto_size_buttons=True,
                             resizable=True,
                             size=settings.initialwinsize, font=(settings.fonttype, int(settings.fontsize)),
                             border_depth=0, finalize=True,
                             location=settings.initialwinpos,
                             titlebar_background_color=sg.theme_background_color(), margins=(0, 0),
                             element_padding=(3, 1), use_custom_titlebar=False,
                             titlebar_text_color=settings.text_colors[0], return_keyboard_events=True,
                             right_click_menu_font=(settings.fonttype, settings.right_click_fontsize),
                             right_click_menu_background_color=sg.theme_background_color(),
                             right_click_menu_text_color=settings.button_color,
                             right_click_menu_selected_colors=(settings.button_color,
                                                               settings.right_click_selected_background),
                             icon="GenIko.ico")

        self.sort_shows_and_display()

        for key in ("add_show", "preferences", "show_all", "search_button", "index_checkbox"):
            self.win[key].block_focus()
            self.win[key].set_cursor("plus")

        if main_loop:
            self.main_loop()

    def main_loop(self):
        last_show_change = 0

        while not self.shouldbreak:
            settings.initialwinpos = self.win.CurrentLocation()
            settings.initialwinsize = self.win.Size
            event, values = self.win.read(timeout=200)

            # The methods called within the if-statement below are intended to update the scrollable area of the
            # .show_col column. However, it seems that this might be a bit inconsistent - i won't look further into
            # right now. BUT if there are problems, they probably stem from here.
            if self.shows_col_contents_changed:
                self.shows_col_contents_changed = False
                self.win.visibility_changed()
                self.shows_col.contents_changed()

            # if event != "__TIMEOUT__":
            #    print(event)

            if event == "__TIMEOUT__":
                now = time.time()
                if last_show_change != 0 and now - last_show_change > delay_to_save_shows:
                    shows.save()
                    last_show_change = 0

                if self.last_release_update + update_release_vals_interval < now:
                    self.display_release()

                continue
            elif event == sg.WIN_CLOSED or self.shouldbreak or event == "Close":
                self.close()
                break

            elif event.startswith("gotolink:"):
                shows.from_index(int(event.removeprefix("gotolink:"))).open_link()

            elif event.startswith("delete:"):
                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                show = shows.from_index(event.removeprefix("delete:"))
                shows.remove(show)
                self.sort_shows_and_display()

            elif event.startswith("Eplus:"):
                show = shows.from_index(event.removeprefix("Eplus:"))
                if show.ep_season_relevant:
                    show.ep = int(show.ep) + 1
                    self.win[event](value=show.ep)

                    last_show_change = time.time()

            elif event.startswith("Eminus:"):
                show_index = event.removeprefix("Eminus:")
                show = shows.from_index(show_index)
                if show.ep_season_relevant:
                    show.ep = int(show.ep) - 1
                    self.win[f"Eplus:{show_index}"](value=show.ep)

                    last_show_change = time.time()

            elif event.startswith("title:"):
                show_index = event.removeprefix("title:")
                show = shows.from_index(show_index)
                if show.ep_season_relevant:
                    self.update_show_color(show,
                                           0 if show.color + 1 >= len(settings.text_colors) else show.color + 1,
                                           show_index=show_index)

                    last_show_change = time.time()

            elif event.startswith("Splus:"):
                show = shows.from_index(event.removeprefix("Splus:"))
                if show.ep_season_relevant:
                    show.season = str(int(show.season) + 1)
                    self.win[event].update(value=show.season)

                    last_show_change = time.time()

            elif event.startswith("Sminus:"):
                show_index = event.removeprefix("Sminus:")
                show = shows.from_index(show_index)
                if show.ep_season_relevant:
                    show.season = str(int(show.season) - 1)
                    self.win[f"Splus:{show_index}"].update(value=show.season)

                    last_show_change = time.time()

            elif event == "index_checkbox":
                settings.indices_visible = self.win["index_checkbox"].get()
                for show_index in range(self.number_of_displayed_shows):
                    self.win[f"index:{show_index}"].update(visible=settings.indices_visible)

            elif event == "release_checkbox":
                settings.releases_visible = self.win["release_checkbox"].get()
                self.display_release()

            elif event.startswith("properties:"):
                show = shows.from_index(event.removeprefix("properties:"))
                did_something = show_properties(show=show, show_purge=True)
                if not did_something:
                    continue
                self.sort_shows_and_display()

            elif event == "h":  # Move self.win to mouse
                mouse_pos = mouse.get_position()
                self.win.move(*mouse_pos)

            elif event == "preferences":
                self.update_preferences()

            elif event == "show_all":
                self.toggle_show_all()

            elif event == "search_button":
                self.search(results=settings.search_results)

            elif event == "add_show":
                show = show_properties()
                if not show:
                    continue
                show.id = shows.highest_id() + 1
                shows.append(show)
                self.sort_shows_and_display()

            elif "::multi_links-" in event:
                show_index = -1
                for ind in range(0, -len(event), -1):
                    if event[ind] == "-":
                        show_index = event[ind + 1:]
                        break
                ref_show = shows.from_index(show_index)

                for show in shows:
                    if ref_show.color == show.color:
                        show.open_link()

            elif "::tit_color-" in event:
                col = ""
                show_index = -1
                for ind, s in enumerate(event):
                    if s == ":":
                        col = event[:ind]
                        break
                for ind in range(0, -len(event), -1):
                    if event[ind] == "-":
                        show_index = event[ind + 1:]
                        break
                col_index = settings.text_colors.index(col)
                show = shows.from_index(show_index)
                self.update_show_color(show, col_index, show_index)

    @staticmethod
    def num_of_shows_to_display():
        """
        Returns how many shows should currently be displayed
        """
        if settings.show_all:
            return len(shows)
        return min(settings.show_amount, len(shows))

    def sort_shows_and_display(self):
        to_display = self.num_of_shows_to_display()
        if to_display < self.number_of_displayed_shows:
            self.shorten_by_x_rows(self.number_of_displayed_shows - to_display)
        if to_display > self.number_of_displayed_shows:
            self.extend_by_x_rows(to_display - self.number_of_displayed_shows)

        shows.do_sorting()

        for ind, show in enumerate(shows[:self.number_of_displayed_shows]):
            color = settings.text_colors[show.color]
            self.win[f"title:{ind}"].update(value=limit_string_len(show.title, settings.max_title_display_len,
                                                                   use_ellipsis=settings.shorten_with_ellpisis),
                                            text_color=color)
            self.win[f"Eminus:{ind}"].update(value="Ep:" if show.ep_season_relevant else "",
                                             text_color=color)
            self.win[f"Eplus:{ind}"].update(value=show.ep if show.ep_season_relevant else "",
                                            text_color=color)
            self.win[f"Sminus:{ind}"].update(value="S:" if show.ep_season_relevant else "",
                                             text_color=color)
            self.win[f"Splus:{ind}"].update(value=show.season if show.ep_season_relevant else "",
                                            text_color=color)
            self.win[f"index:{ind}"].update(text_color=color)
            self.win[f"release:{ind}"].update(text_color=color)
            self.set_cursors(ind)
        self.display_release()

    def display_release(self, index: int = None, show: Show = None):
        if index is None or show is None:
            self.last_release_update = time.time()
            for _index, _show in enumerate(shows[:self.number_of_displayed_shows]):
                self.win[f"release:{_index}"].update(visible=settings.releases_visible
                                                             and _show.check_release(settings.release_grace_period))
            return
        self.win[f"release:{index}"].update(visible=settings.releases_visible
                                                    and show.check_release(settings.release_grace_period))

    def update_show_color(self, show: Show, new_color_id: int, show_index=None):
        show.color = new_color_id
        if show_index is None:
            show_index = shows.get_index(show)
        color = settings.text_colors[new_color_id]
        self.win[f"index:{show_index}"].update(text_color=color)
        self.win[f"title:{show_index}"].update(text_color=color)
        self.win[f"Eminus:{show_index}"].update(text_color=color)
        self.win[f"Eplus:{show_index}"].update(text_color=color)
        self.win[f"Splus:{show_index}"].update(text_color=color)
        self.win[f"Sminus:{show_index}"].update(text_color=color)

    def close(self):
        self.shouldbreak = True
        self.win.close()

    def restart(self):
        global should_restart
        should_restart = True
        self.close()

    def toggle_show_all(self):
        settings.show_all = not settings.show_all
        self.restart()

    def search(self, results):
        index_len = 4  # The minimum length of the Text element in the index column. Used for alignment

        delcol = [butt("DEL", key=f"s_delete_{n}", mouseover_colors="#AA0000", border_width=0) for n in range(results)]

        titcol = [sg.Text(shows[n].title, key=f"s_title_{n}", enable_events=True,
                          text_color=settings.text_colors[min(int(shows[n].color), len(settings.text_colors) - 1)],
                          size=(37, 1)) for n in range(results)]

        index_col = [sg.Text(f"{n + 1: >{index_len}}", key=f"s_index_{n}",
                             text_color=settings.text_colors[min(int(shows[n].color), len(settings.text_colors) - 1)])
                     for n in range(results)]

        propcol = [butt("⛭", key=f"s_properties_{n}", border_width=0) for n in range(results)]

        rescol = [[delcol[n], titcol[n], index_col[n], propcol[n]] for n in range(results)]

        layout = [[sg.T("Search:"), sg.In(key="search", enable_events=True, size=(40, 1))],
                  [sg.Col(rescol)]]

        search_win = sg.Window("Search", layout=layout, finalize=True, font=(settings.fonttype, int(settings.fontsize)))

        found: Union[List[Show], List[str]] = [shows[ind] for ind in range(results)]

        while True:
            e, v = search_win.read()
            if e == sg.WIN_CLOSED:
                break
            elif e == "search":
                found_indices = [-1] * results
                found = [""] * results
                search_query = v["search"].lower()
                for show_index, s in enumerate(shows):
                    if search_query in s.title.lower():
                        for ind, n in enumerate(found):
                            if n == "":
                                # noinspection PyTypeChecker
                                found[ind] = s
                                found_indices[ind] = show_index
                                break
                try:
                    for n in range(results):
                        search_win[f"s_title_{n}"].update(" ")
                        search_win[f"s_index_{n}"].update(" " * index_len)
                    for n in range(results):
                        if isinstance(found[n], Show):
                            search_win[f"s_title_{n}"].update(found[n].title)
                            search_win[f"s_index_{n}"].update(f"{found_indices[n] + 1: >{index_len}}")
                            search_win[f"s_title_{n}"] \
                                .update(text_color=settings.text_colors[min(int(found[n].color),
                                                                            len(settings.text_colors) - 1)])
                            search_win[f"s_index_{n}"] \
                                .update(text_color=settings.text_colors[min(int(found[n].color),
                                                                            len(settings.text_colors) - 1)])
                except IndexError:
                    pass

            elif e.startswith("s_delete_"):
                k = int(e.removeprefix("s_delete_"))

                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                delme = -1
                for ind, n in enumerate(shows):
                    if n.id == found[k].id:
                        delme = ind
                        break
                if delme != -1:
                    shows.pop(delme)
                search_win.close()
                self.sort_shows_and_display()
                return

            elif e.startswith("s_properties_"):
                k = int(e.removeprefix("s_properties_"))
                show = shows.from_id(found[k].id)
                did_something = show_properties(show=show, show_purge=True)
                if not did_something:
                    continue
                search_win.close()
                self.sort_shows_and_display()
                return

    def update_preferences(self):
        col1 = [[sg.T("Font size:")],
                [sg.T("Font type:")],
                [sg.T("Text color:")],
                [sg.ColorChooserButton("Background color:", target="bg_color")],
                [sg.ColorChooserButton("Menu background color:", target="menu_bg_color")],
                [sg.T("Menu font size:")],
                [sg.ColorChooserButton("Button Color", target="buttoncolor")],
                [sg.T("Search Results")],
                [sg.T("Title Length")],
                [sg.T("Show Cut-off")]]
        col2 = [[sg.In(settings.fontsize, key="fsize", tooltip="Any integer")],
                [sg.In(settings.fonttype, key="ftype",
                       tooltip="Any font name, as one might use in Word or libreOffice Writer")],
                [sg.In("-".join(settings.text_colors), key="txtcolor",
                       tooltip="Ex: '#ff0000-#404040' or '#ff0000-#404040-#878787'")],
                [sg.In(sg.theme_background_color(), k="bg_color", tooltip="The background color",
                       background_color=sg.theme_background_color())],
                [sg.In(settings.right_click_selected_background, k="menu_bg_color",
                       background_color=sg.theme_background_color(),
                       tooltip="The background color of the right click menu")],
                [sg.In(settings.right_click_fontsize, k="menu_font_size",
                       tooltip="The font size of the right click menu")],
                [sg.In(settings.button_color, key="buttoncolor", tooltip="A single color, Ex: '#e0e0e0'",
                       background_color=sg.theme_background_color())],
                [sg.In(settings.search_results, key="sresults",
                       tooltip="The number of results shown when searching. Default:3")],
                [sg.In(settings.max_title_display_len, key="title_length",
                       tooltip="The amount of characters that should be displayed\n"
                               "in titles. 0 to display all characters")],
                [sg.In(settings.show_amount, key="showamount",
                       tooltip="For performance reasons not all shows are displayed by default. This is the amount"
                               " of shows on display.\nCan be toggled by the '^' button")]]
        col3 = [[sg.ColorChooserButton("Field Background Color:", target="field_bg_color")],
                [sg.T("Shorten With Ellipsis:")],
                [sg.T("Release Grace Period:")]]
        col4 = [[sg.In(sg.theme_input_background_color(), k="field_bg_color",
                       tooltip="The background color of the input fields",
                       background_color=sg.theme_background_color())],
                [sg.Checkbox(default=settings.shorten_with_ellpisis, k="shorten_with_ellipsis", text="",
                             text_color=settings.button_color, tooltip='Whether or not to end shortened titles'
                                                                       ' with "..."')],
                [sg.In(settings.release_grace_period, k="release_grace_period",
                       tooltip="The number of hours after a show has been released that the show should be marked\n"
                               "as having recently been released.")]]
        pref_win = sg.Window("Preferences", layout=[
            [sg.Col(col1),
             sg.Col(col2),
             sg.Col(col3, expand_y=True, element_justification="n"),
             sg.Col(col4, expand_y=True, element_justification="n")],
            [sg.Button("Save", bind_return_key=True)]], default_element_size=(16, 1),
                             font=(settings.fonttype, settings.fontsize))

        while True:
            e, v = pref_win.read()
            if e == sg.WIN_CLOSED:
                break
            elif e == "Save":
                try:
                    int(pref_win["fsize"].get())
                    if not is_valid_color(pref_win["buttoncolor"].get()):
                        raise ValueError

                    if not is_valid_color(pref_win["menu_bg_color"].get()):
                        raise ValueError

                    if not is_valid_color(pref_win["bg_color"].get()):
                        raise ValueError

                    if not is_valid_color(pref_win["field_bg_color"].get()):
                        raise ValueError

                    gotcolors = pref_win["txtcolor"].get().split("-")
                    if len(gotcolors) <= 0:
                        raise ValueError
                    for col in gotcolors:
                        if not is_valid_color(col):
                            raise ValueError

                except ValueError:
                    sg.popup_error("Unreadable value")
                    continue
                pref_win.close()

                settings.fontsize = pref_win["fsize"].get()
                settings.fonttype = pref_win["ftype"].get()
                settings.text_colors = pref_win["txtcolor"].get().split("-")
                sg.theme_background_color(pref_win["bg_color"].get())
                sg.theme_input_background_color(pref_win["field_bg_color"].get())
                settings.right_click_selected_background = pref_win["menu_bg_color"].get()
                settings.right_click_fontsize = int(pref_win["menu_font_size"].get())
                settings.button_color = pref_win["buttoncolor"].get()
                settings.search_results = int(pref_win["sresults"].get())
                settings.max_title_display_len = int(pref_win["title_length"].get())
                settings.show_amount = int(pref_win["showamount"].get())
                settings.shorten_with_ellpisis = pref_win["shorten_with_ellipsis"].get()
                settings.release_grace_period = int(pref_win["release_grace_period"].get())

                if settings.save():
                    self.restart()
                break

    def delete_element(self, index):
        self.delete_elements.append(butt("DEL",
                                         key=f"delete:{index}",
                                         mouseover_colors="#AA0000",
                                         border_width=0))
        return self.delete_elements[-1]

    def title_element(self, index):
        self.title_elements.append(sg.Text(key=f"title:{index}",
                                           size=(settings.max_title_display_len, 1),
                                           enable_events=True,
                                           right_click_menu=["",
                                                             [f"{m}::tit_color-{index}" for m in
                                                              settings.text_colors]]))
        return self.title_elements[-1]

    def ep_minus_element(self, index):
        self.ep_minus_elements.append(sg.Text(size=(3, 1),
                                              enable_events=True,
                                              key=f"Eminus:{index}"))
        return self.ep_minus_elements[-1]

    def ep_plus_element(self, index):
        self.ep_plus_elements.append(sg.Text(key=f"Eplus:{index}",
                                             enable_events=True,
                                             size=(4, 1)))
        return self.ep_plus_elements[-1]

    def season_minus_element(self, index):
        self.season_minus_elements.append(sg.Text(size=(2, 1),
                                                  enable_events=True,
                                                  key=f"Sminus:{index}"))
        return self.season_minus_elements[-1]

    def season_plus_element(self, index):
        self.season_plus_elements.append(sg.Text(size=(4, 1),
                                                 enable_events=True,
                                                 key=f"Splus:{index}"))
        return self.season_plus_elements[-1]

    def link_element(self, index):
        self.link_elements.append(butt("LINK",
                                       key=f"gotolink:{index}",
                                       border_width=0,
                                       right_click_menu=["",
                                                         [f"Open all links with the same color::multi_links-{index}"]]))
        return self.link_elements[-1]

    def properties_element(self, index):
        self.properties_elements.append(butt("⛭",
                                             key=f"properties:{index}",
                                             border_width=0))
        return self.properties_elements[-1]

    def index_element(self, index):
        self.index_elements.append(sg.Text(str(index + 1),
                                           key=f"index:{index}",
                                           visible=settings.indices_visible))
        return self.index_elements[-1]

    def release_element(self, index):
        self.release_elements.append(sg.Text(recently_released_string,
                                             key=f"release:{index}",
                                             visible=False))
        return self.release_elements[-1]

    def set_cursors(self, index):
        self.delete_elements[index].set_cursor("plus")
        self.title_elements[index].set_cursor("plus")
        relevant = shows.from_index(index).ep_season_relevant

        self.ep_minus_elements[index].set_cursor("sb_down_arrow" if relevant else "arrow")
        self.ep_plus_elements[index].set_cursor("based_arrow_up" if relevant else "arrow")
        self.season_minus_elements[index].set_cursor("based_arrow_down" if relevant else "arrow")
        self.season_plus_elements[index].set_cursor("based_arrow_up" if relevant else "arrow")
        self.properties_elements[index].set_cursor("plus")
        self.link_elements[index].set_cursor("hand2")

    def shorten_by_x_rows(self, x):
        for _ in range(x):
            self.shorten_by_one_row()

    def shorten_by_one_row(self):
        """
        Doesn't actually remove a row of elements. Instead, it makes them invisible.
        """
        index = self.number_of_displayed_shows - 1
        self.change_visibility_of_row(index, False)
        self.number_of_displayed_shows -= 1
        self.number_of_invisible_rows += 1

    def change_visibility_of_row(self, index, visibility):
        self.win[f"delete:{index}"].update(visible=visibility)
        self.win[f"title:{index}"].update(visible=visibility)
        self.win[f"Eminus:{index}"].update(visible=visibility)
        self.win[f"Eplus:{index}"].update(visible=visibility)
        self.win[f"Sminus:{index}"].update(visible=visibility)
        self.win[f"Splus:{index}"].update(visible=visibility)
        self.win[f"gotolink:{index}"].update(visible=visibility)
        self.win[f"properties:{index}"].update(visible=visibility)
        self.win[f"index:{index}"].update(visible=visibility)
        self.shows_col_contents_changed = True

    def extend_by_x_rows(self, x):
        for _ in range(x):
            self.extend_by_one_row()

    def extend_by_one_row(self):
        index = self.number_of_displayed_shows
        if self.number_of_invisible_rows > 0:
            self.change_visibility_of_row(index, True)
            self.number_of_invisible_rows -= 1
        else:
            self.win.extend_layout(self.shows_col, [[self.delete_element(index),
                                                     self.title_element(index),
                                                     self.ep_minus_element(index),
                                                     self.ep_plus_element(index),
                                                     self.season_minus_element(index),
                                                     self.season_plus_element(index),
                                                     self.link_element(index),
                                                     self.properties_element(index),
                                                     self.index_element(index)]])
        self.shows_col_contents_changed = True  # This causes self.shows_col.contents_changed() to be called
        # immediately after self.win.read(). Why this needs to be the case, I cannot fathom. (BUT IT WORKS!)
        self.number_of_displayed_shows += 1


if __name__ == '__main__':
    settings = Settings(sg, savefile=settingsfile, delimiter=delimiter)
    shows = ShowsFileHandler(savefile=savefile, delimiter=delimiter)

    should_restart = True
    while should_restart:
        should_restart = False

        MainWin(main_loop=True)

        settings.save()
        shows.save()
