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

# The number of seconds in between a change being made to a show and the change being saved. Accepts floats
delay_to_save_shows = 3


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


def show_properties(title: str = "Show Editor", show: Show = None):
    """
    Opens a small window with all the relevant information about a show allowing these to be changed by the user.
    Then returning the show, if save was pressed and False if Cancel was pressed.
    If no show is None, then the function returns a dummy show with all the appropriate values and an id of -1.

    :param title: Title of the window
    :param show: If given, then all values will be changed in this show.
    :return: True if something has been changed and False if nothing has been changed.
    :rtype: Union[bool, Show]
    """
    if show is None:  # make a dummy show.
        show = Show(-1, "", 0, 1, "", 0, 0, True)
    button, data = sg.Window(title,
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
                                 [sg.Button("Save", bind_return_key=True), sg.Button("Cancel")]],
                             disable_close=True,
                             auto_size_buttons=True,
                             auto_size_text=True,
                             default_element_size=(12, 1),
                             font=(settings.fonttype, int(settings.fontsize))).read(close=True)

    if button == "Cancel":
        return False
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
    show.weight = data["show_weight"]
    show.ep_season_relevant = data["show_ep_season_relevant"]

    return show


def butt(button_text="", key=None, tooltip=None, butt_color=(False, None), border_width=None, size=(None, None),
         mouseover_colors=sg.theme_background_color(), disabled=False, right_click_menu=None):
    """
    A wrapper function for sg.Button with some different default values

    :param button_text:
    :param key:
    :param tooltip:
    :param butt_color:
    :param border_width:
    :param size:
    :param mouseover_colors:
    :param disabled:
    :param right_click_menu:
    :return: an sg.Button object
    """
    if not butt_color[0]:
        butt_color = (settings.button_color, butt_color[1])
    return sg.Button(button_text=button_text, key=key, tooltip=tooltip, button_color=butt_color,
                     border_width=border_width, size=size, mouseover_colors=mouseover_colors, disabled=disabled,
                     right_click_menu=right_click_menu)


class MainWin:
    def __init__(self, main_loop=False):
        """
        Initialises the main PySimpleGUI window

        :param main_loop: Calls self.main_loop() if true
        :type main_loop: bool
        """
        global should_restart

        self.shouldbreak = False
        self.number_of_displayed_shows = 0

        sg.theme_text_color(settings.text_colors[0])
        sg.theme_element_text_color(settings.button_color)
        sg.theme_element_background_color(sg.theme_background_color())
        sg.theme_text_element_background_color(sg.theme_background_color())
        sg.theme_slider_color(sg.theme_background_color())
        sg.theme_button_color((settings.button_color, sg.theme_background_color()))

        delcolumn = []
        title_column = []
        emincolumn = []
        ecolumn = []
        smincolumn = []
        scolumn = []
        linkcolumn = []
        propcolumn = []
        index_col = []

        max_txt_color_index = len(settings.text_colors) - 1
        for ind, show in enumerate(shows if settings.show_all else shows[:min(len(shows), settings.show_amount)]):
            # Iterates the entirety of show if showall is true and otherwise only
            # the first {show_amount} of shows
            color = settings.text_colors[min(int(show.color), max_txt_color_index)]

            delcolumn.append([butt("DEL", key=f"delete:{ind}", mouseover_colors="#AA0000",
                                   border_width=0)])

            title_column.append([sg.Text(limit_string_len(show.title, settings.max_title_display_len,
                                                          use_ellipsis=settings.shorten_with_ellpisis),
                                         key=f"title:{ind}",
                                         enable_events=True, text_color=f"{color}",
                                         right_click_menu=["",
                                                           [f"{m}::tit_color-{ind}" for m in
                                                            settings.text_colors]])])

            emincolumn.append([sg.Text(f"Ep:" if show.ep_season_relevant else "",
                                       size=(3, 1),
                                       key=f"Eminus:{ind}",
                                       enable_events=True if show.ep_season_relevant else False,
                                       text_color=f"{color}")])

            ecolumn.append([sg.Text(f"{show.ep}" if show.ep_season_relevant else "",
                                    key=f"Eplus:{ind}",
                                    enable_events=True if show.ep_season_relevant else False,
                                    size=(4, 1),
                                    text_color=f"{color}")])

            smincolumn.append([sg.Text(f"S:" if show.ep_season_relevant else "",
                                       size=(2, 1),
                                       key=f"Sminus:{ind}",
                                       enable_events=True if show.ep_season_relevant else False,
                                       text_color=f"{color}")])

            scolumn.append([sg.Text(f"{show.season}" if show.ep_season_relevant else "",
                                    size=(4, 1),
                                    key=f"Splus:{ind}",
                                    text_color=f"{color}",
                                    enable_events=True if show.ep_season_relevant else False)])

            linkcolumn.append([butt("LINK",
                                    key=f"gotolink:{ind}",
                                    tooltip=show.link,
                                    border_width=0,
                                    right_click_menu=["",
                                                      [f"Open all links with the same color::multi_links-{ind}"]])])

            propcolumn.append([butt("⛭",
                                    key=f"properties:{ind}",
                                    border_width=0)])

            index_col.append([sg.Text(str(ind + 1),
                                      key=f"index:{ind}",
                                      text_color=color,
                                      visible=settings.indices_visible)])

            self.number_of_displayed_shows = ind + 1

        showscol = [[sg.Col([[delcolumn[ind][0], title_column[ind][0]] for ind in range(len(title_column))]),
                     sg.Col([[emincolumn[ind][0], ecolumn[ind][0], smincolumn[ind][0], scolumn[ind][0],
                              linkcolumn[ind][0],
                              propcolumn[ind][0], index_col[ind][0]] for ind in range(len(title_column))])]]

        topcol = [[butt(" + ", key="add_show", border_width=0, tooltip="Add a show to the list"),
                   butt(" ⛭ ", key="preferences", border_width=0, tooltip="Preferences"),
                   butt(" ⮝ " if settings.show_all else " ⮟ ", key="show_all", border_width=0,
                        tooltip="Show less (faster)" if settings.show_all else "Show more (slower)"),
                   butt(" 🔍 ", key="search_button", border_width=0, tooltip="Search"),
                   sg.Checkbox(" ", key="index_checkbox", text_color=settings.button_color,
                               tooltip="Enables or disables the showing of indices",
                               default=settings.indices_visible, enable_events=True)]]

        layout = [
            [sg.Col(topcol)],
            [sg.Column(showscol, vertical_scroll_only=True, scrollable=True, expand_x=True, expand_y=True)],
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

        for e in linkcolumn:
            e[0].set_cursor("hand2")
        # noinspection PyTypeChecker
        for e in ecolumn + emincolumn + scolumn + smincolumn + title_column + delcolumn + propcolumn:
            try:
                if e[0].get() == "":
                    continue
            except AttributeError:
                pass
            e[0].set_cursor("plus")

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

            # if event != "__TIMEOUT__":
            #    print(event)

            if event == "__TIMEOUT__":
                if last_show_change != 0 and time.time() - last_show_change > delay_to_save_shows:
                    shows.save()
                    last_show_change = 0
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
                show.ep = int(show.ep) + 1
                self.win[event](value=show.ep)

                last_show_change = time.time()

            elif event.startswith("Eminus:"):
                show_index = event.removeprefix("Eminus:")
                show = shows.from_index(show_index)
                show.ep = int(show.ep) - 1
                self.win[f"Eplus:{show_index}"](value=show.ep)

                last_show_change = time.time()

            elif event.startswith("title:"):
                show_index = event.removeprefix("title:")
                show = shows.from_index(show_index)
                self.update_show_color(show,
                                       0 if show.color + 1 >= len(settings.text_colors) else show.color + 1,
                                       show_index=show_index)

                last_show_change = time.time()

            elif event.startswith("Splus:"):
                show = shows.from_index(event.removeprefix("Splus:"))
                show.season = str(int(show.season) + 1)
                self.win[event].update(value=show.season)

                last_show_change = time.time()

            elif event.startswith("Sminus:"):
                show_index = event.removeprefix("Sminus:")
                show = shows.from_index(show_index)
                show.season = str(int(show.season) - 1)
                self.win[f"Splus:{show_index}"].update(value=show.season)

                last_show_change = time.time()

            elif event == "index_checkbox":
                settings.indices_visible = self.win["index_checkbox"].get()
                for show_index in range(len(shows)) if settings.show_all else range(min(len(shows),
                                                                                        settings.show_amount)):
                    self.win[f"index:{show_index}"].update(visible=settings.indices_visible)

            elif event.startswith("properties:"):
                show = shows.from_index(event.removeprefix("properties:"))
                did_something = show_properties(show=show)
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

    def sort_shows_and_display(self):
        if settings.show_all or settings.show_amount > self.number_of_displayed_shows >= len(shows):
            self.restart()
            return

        shows.do_sorting()

        for ind, show in enumerate(shows if settings.show_all else shows[:min(len(shows), settings.show_amount)]):
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

        index_col = [sg.Text(f"{' ' * (index_len - 1)}{n + 1}", key=f"s_index_{n}",
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
                        search_win[f"s_index_{n}"].update(" "*index_len)
                    for n in range(results):
                        if isinstance(found[n], Show):
                            search_win[f"s_title_{n}"].update(found[n].title)
                            search_win[f"s_index_{n}"].update(f"{found_indices[n] + 1: >{index_len}}")
                            search_win[f"s_title_{n}"]\
                                .update(text_color=settings.text_colors[min(int(found[n].color),
                                                                            len(settings.text_colors) - 1)])
                            search_win[f"s_index_{n}"]\
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
                did_something = show_properties(show=show)
                if not did_something:
                    continue
                search_win.close()
                self.sort_shows_and_display()
                return

    def update_preferences(self):
        col1 = [[sg.T("Font size:")],
                [sg.T("Font type:")],
                [sg.T("Text color:")],
                [sg.T("Background color:")],
                [sg.T("Menu background color:")],
                [sg.T("Menu font size:")],
                [sg.T("Button Color")],
                [sg.T("Search Results")],
                [sg.T("Title Length")],
                [sg.T("Show Cut-off")]]
        col2 = [[sg.In(settings.fontsize, key="fsize", tooltip="Any integer")],
                [sg.In(settings.fonttype, key="ftype",
                       tooltip="Any font name, as one might use in word or libreOffice Writer")],
                [sg.In("-".join(settings.text_colors), key="txtcolor",
                       tooltip="Ex: '#ff0000-#404040' or '#ff0000-#404040-#878787'")],
                [sg.In(sg.theme_background_color(), k="bg_color", tooltip="The background color")],
                [sg.In(settings.right_click_selected_background, k="menu_bg_color",
                       tooltip="The background color of the right click menu")],
                [sg.In(settings.right_click_fontsize, k="menu_font_size",
                       tooltip="The font size of the right click menu")],
                [sg.In(settings.button_color, key="buttoncolor", tooltip="A single color, Ex: '#e0e0e0'")],
                [sg.In(settings.search_results, key="sresults",
                       tooltip="The number of results shown when searching. Default:3")],
                [sg.In(settings.max_title_display_len, key="title_length",
                       tooltip="The amount of characters that should be displayed\n"
                               "in titles. 0 to display all characters")],
                [sg.In(settings.show_amount, key="showamount",
                       tooltip="For performance reasons not all shows are displayed by default. This is the amount"
                               " of shows on display.\nCan be toggled by the '^' button")]]
        col3 = [[sg.T("Field Background Color:")],
                [sg.T("Shorten With Ellipsis:")]]
        col4 = [[sg.In(sg.theme_input_background_color(), k="field_bg_color",
                       tooltip="The background color of the input fields")],
                [sg.Checkbox(default=settings.shorten_with_ellpisis, k="shorten_with_ellipsis", text="",
                             text_color=settings.button_color, tooltip='Whether or not to end shortened titles'
                                                                       ' with "..."')]]
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

                if settings.save():
                    self.restart()
                break


if __name__ == '__main__':
    settings = Settings(sg, savefile=settingsfile, delimiter=delimiter)
    shows = ShowsFileHandler(savefile=savefile, delimiter=delimiter)

    should_restart = True
    while should_restart:
        should_restart = False

        shows.do_sorting()
        MainWin(main_loop=True)

        settings.save()
        shows.save()
