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

# The amount of seconds in between a change being made to a show and the change being saved.
delay_to_save_shows = 3


def is_valid_color(col: str):
    """
    Checks whether or not a string is a hex color code

    :param col: A string
    :return: Returns True if the string col is a proper hex color code, such as "#FFFFFF"
    """
    if len(col) == 7:
        if col[0] == "#":
            for n in col[1:]:
                if (48 <= ord(n) <= 57) or (65 <= ord(n) <= 70) or (97 <= ord(n) <= 102):
                    return True
                return False
    return False


def get_highest_id(lst: Union[ShowsFileHandler, List]):
    """
    Returns the highest id in a list of Shows

    :param lst: A list or list equivalent of Show objects.
    :type lst: ShowsFileHandler
    :return: The highest id
    """
    if len(lst) == 0:
        return -1
    return max([int(show.id) for show in lst])


def find_from_id(num_id, lst: Union[ShowsFileHandler, List]):
    """
    Returns the Show with the given id

    :param num_id: The id to search for
    :type num_id: int
    :param lst: A list or list equivalent of Show objects.
    :type lst: ShowsFileHandler
    :return: The Show with and id equivalent to num_id
    :rtype: Show
    """
    for n in lst:
        if n.id == num_id:
            return n


def limit_string_len(string: str, length: int):
    """
    Shortens a string so that its length doesn't exceed some amount

    :param string: The string to limit
    :type string: str
    :param length: The maximum length of the string
    :type length: int
    :return: A string with a maximum length of - length -
    :rtype: str
    """
    if len(string) > length != 0:
        return string[:length]
    return string


def min_string_len(string: str, length: int):
    """
    Prefixes a string with a number of spaces to reach a certain length

    :param string: The string to (possibly) prefix with spaces
    :type string: str
    :param length: The minimum length of the returned string
    :type string: int
    :return: A string with a minimum length
    :rtype: str
    """
    if len(string) > length:
        return string
    return f"{' ' * (length - len(string))}{string}"


def show_properties(poptitle="Show Editor", popshowname="", popep="0", popseas="1", poplink="", popweight="0"):
    """
    Opens a small window with all the relevant information about a show allowing these to be changed by the user.
    Then returning the new values - unless the button "Cancel" is pressed.

    :param poptitle: title of the window
    :type poptitle: str
    :param popshowname: initital Title of the Show
    :type popshowname: str
    :param popep: initital Episode of the Show
    :type popep: str
    :param popseas: initital Season of the Show
    :type popseas: str
    :param poplink: initital Link of the Show
    :type poplink: str
    :param popweight: initital Weight of the Show
    :type popweight: str
    :return: A dictionary of the user submitted values or 1 if canceled.
    :rtype: dict or int
    """
    button, data = sg.Window(poptitle,
                             [
                                 [sg.Column([
                                     [sg.T("Title")],
                                     [sg.InputText(popshowname, key="popshowname")]
                                 ]),
                                     sg.Column([
                                         [sg.T("Episode")],
                                         [sg.InputText(popep, key="popep", size=(8, 1))]
                                     ]),
                                     sg.Column([
                                         [sg.T("Season")],
                                         [sg.InputText(popseas, key="popseas", size=(8, 1))]
                                     ]),
                                     sg.Column([
                                         [sg.T("Link")],
                                         [sg.InputText(poplink, key="poplink", size=(15, 1))]
                                     ]),
                                     sg.Column([
                                         [sg.T("Weight")],
                                         [sg.InputText(popweight, key="popweight")]
                                     ])
                                 ],
                                 [sg.Button("Save", bind_return_key=True), sg.Button("Cancel")]],
                             disable_close=True,
                             auto_size_buttons=True,
                             auto_size_text=True,
                             default_element_size=(12, 1),
                             font=(settings.fonttype, int(settings.fontsize))).read(close=True)

    if button == "Cancel":
        return 1
    try:
        data["popep"] = str(int(data["popep"]))
        data["popseas"] = str(int(data["popseas"]))
        data["popweight"] = str(int(data["popweight"]))
    except ValueError:
        sg.popup_error(title="Couldn't convert to integer")
        return 1
    return data


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
    def __init__(self):
        global should_restart

        self.shouldbreak = False

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
        scolumn = []
        linkcolumn = []
        propcolumn = []
        index_col = []

        max_txt_color_index = len(settings.text_colors) - 1
        for ind, show in enumerate(shows if settings.show_all else shows[:min(len(shows), settings.show_amount)]):
            # Note that it will iterate the entire list show if showall is true and otherwise only
            # the first {show_amount} of shows
            show.stringify()
            color = settings.text_colors[min(int(show.color), max_txt_color_index)]

            delcolumn.append([butt("DEL", key=f"delete:{show.id}", mouseover_colors="#AA0000",
                                   border_width=0)])

            title_column.append([sg.Text(limit_string_len(show.title, settings.max_title_display_len),
                                         key=f"title:{show.id}",
                                         enable_events=True, text_color=f"{color}",
                                         right_click_menu=["",
                                                           [f"{m}::tit_color-{show.id}" for m in
                                                            settings.text_colors]])])

            emincolumn.append([sg.Text(f"Ep:", key=f"Eminus{show.id}", enable_events=True,
                                       text_color=f"{color}")])

            ecolumn.append([sg.Text(f"{show.ep}", key=f"Eplus{show.id}", enable_events=True, size=(4, 1),
                                    text_color=f"{color}")])

            scolumn.append([sg.Text(f"S: {show.season}", size=(4, 1), key=f"season:{show.id}",
                                    text_color=f"{color}", enable_events=True)])

            linkcolumn.append([butt("LINK", key=f"gotolink:{show.id}", tooltip=show.link, border_width=0,
                                    right_click_menu=["",
                                                      [f"Open all links with the same color::multi_links-{show.id}"]])])

            propcolumn.append([butt("⛭", key=f"properties{show.id}", border_width=0)])

            index_col.append([sg.Text(str(ind + 1), key=f"index:{show.id}",
                                      text_color=color, visible=settings.indices_visible)])

        showscol = [[sg.Col([[delcolumn[ind][0], title_column[ind][0]] for ind in range(len(title_column))]),
                     sg.Col([[emincolumn[ind][0], ecolumn[ind][0], scolumn[ind][0], linkcolumn[ind][0],
                              propcolumn[ind][0], index_col[ind][0]] for ind in range(len(title_column))])]]

        topcol = [[butt(" + ", key="AddShow", border_width=0, tooltip="Add a show to the list"),
                   butt(" ⛭ ", key="preferences", border_width=0, tooltip="Preferences"),
                   butt(" ⮝ " if settings.show_all else " ⮟ ", key="toggleshowall", border_width=0,
                        tooltip="Show less (faster)" if settings.show_all else "Show more (slower)"),
                   butt(" 🔍 ", key="searchbutton", border_width=0, tooltip="Search"),
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
        for e in ecolumn:
            e[0].set_cursor("plus")
        for e in emincolumn:
            e[0].set_cursor("plus")
        for e in title_column:
            e[0].set_cursor("plus")
        for e in delcolumn:
            e[0].set_cursor("plus")
        for e in propcolumn:
            e[0].set_cursor("plus")

        self.win["AddShow"].block_focus()
        self.win["AddShow"].set_cursor("plus")
        self.win["preferences"].block_focus()
        self.win["preferences"].set_cursor("plus")

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

            elif event[:9] == "gotolink:" and len(event) > 9:
                s_id = event[9:]
                for ind, n in enumerate(shows):
                    if n.id == s_id:
                        n.open_link()
                        break

            elif event[:7] == "delete:":
                delme = -1

                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                for ind, n in enumerate(shows):
                    if n.id == event[7:]:
                        delme = ind
                        break
                if delme != -1:
                    shows.pop(delme)
                self.restart()
                break

            elif event[:5] == "Eplus":
                for s in shows:
                    if s.id == event[5:]:
                        s.ep = str(int(s.ep) + 1)
                        last_show_change = time.time()
                        self.win[event](value=s.ep)
                        break

            elif event[:6] == "Eminus":
                for s in shows:
                    if s.id == event[6:]:
                        s.ep = str(int(s.ep) - 1)
                        last_show_change = time.time()
                        self.win["Eplus" + event[6:]](value=s.ep)
                        break

            elif event[:6] == "title:":
                show_id = event[6:]
                for ind, n in enumerate(shows):
                    if n.id == show_id:
                        shows[ind].color = str(int(shows[ind].color) + 1)
                        if int(shows[ind].color) >= len(settings.text_colors):
                            shows[ind].color = 0
                        self.win[event].update(text_color=settings.text_colors[int(n.color)])
                        self.win[f"index:{show_id}"].update(text_color=settings.text_colors[int(n.color)])
                        self.win[f"Eplus{show_id}"].update(text_color=settings.text_colors[int(n.color)])
                        self.win[f"Eminus{show_id}"].update(text_color=settings.text_colors[int(n.color)])
                        self.win[f"season:{show_id}"].update(text_color=settings.text_colors[int(n.color)])
                        break

                last_show_change = time.time()
            elif event[:7] == "season:":
                for s in shows:
                    if s.id == event[7:]:
                        first_mouse = mouse.get_position()[1]
                        time.sleep(0.050)
                        second_mouse = mouse.get_position()[1]
                        if first_mouse < second_mouse:
                            s.season = str(int(s.season) - 1)  # Increase season counter
                        elif first_mouse > second_mouse:
                            s.season = str(int(s.season) + 1)  # Decrease season counter
                        last_show_change = time.time()
                        self.win["season:" + event[7:]](value=f"S: {s.season}")
                        break

            elif event == "index_checkbox":
                indices_visible = self.win["index_checkbox"].get()
                for show in shows if settings.show_all else shows[:min(len(shows), settings.show_amount)]:
                    self.win[f"index:{show.id}"].update(visible=indices_visible)

            elif event[:10] == "properties":
                show = find_from_id(event[10:], shows)
                data = show_properties(popshowname=show.title, popep=show.ep, popseas=show.season, poplink=show.link,
                                       popweight=show.weight)
                if data == 1:
                    continue
                for ind, tshow in enumerate(shows):
                    if tshow.id == show.id:
                        shows[ind].title = data["popshowname"]
                        shows[ind].ep = data["popep"]
                        shows[ind].season = data["popseas"]
                        shows[ind].link = data["poplink"]
                        shows[ind].weight = data["popweight"]
                        self.restart()
                        return

            elif event == "h":  # Move self.win to mouse
                mouse_pos = mouse.get_position()
                self.win.move(*mouse_pos)

            elif event == "preferences":
                self.update_preferences()

            elif event == "toggleshowall":
                self.toggle_show_all()

            elif event == "searchbutton":
                self.search(results=settings.search_results)

            elif event == "AddShow":
                data = show_properties()
                if data == 1:
                    continue
                shows.append(Show(str(get_highest_id(shows) + 1), data["popshowname"], data["popep"],
                                  data["popseas"], data["poplink"], data["popweight"], "0"))
                self.restart()
                break

            elif "::multi_links-" in event:
                num_id = -1
                for ind in range(0, -len(event), -1):
                    if event[ind] == "-":
                        num_id = event[ind + 1:]
                        break
                if num_id != -1:
                    ref_show = find_from_id(num_id, shows)

                    for show in shows:
                        if ref_show.color == show.color:
                            show.open_link()

            elif "::tit_color-" in event:
                col = ""
                num_id = -1
                for ind, s in enumerate(event):
                    if s == ":":
                        col = event[:ind]
                        break
                for ind in range(0, -len(event), -1):
                    if event[ind] == "-":
                        num_id = event[ind + 1:]
                        break
                if col != "" and num_id != -1:
                    col_index = settings.text_colors.index(col)
                    show = find_from_id(num_id, shows)
                    show.color = col_index
                    self.win[f"index:{num_id}"].update(text_color=settings.text_colors[col_index])
                    self.win[f"title:{num_id}"].update(text_color=settings.text_colors[col_index])
                    self.win[f"Eminus{num_id}"].update(text_color=settings.text_colors[col_index])
                    self.win[f"Eplus{num_id}"].update(text_color=settings.text_colors[col_index])
                    self.win[f"season:{num_id}"].update(text_color=settings.text_colors[col_index])

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

    def search(self, results=3):
        index_len = 4  # The number in the "index" column. Used for the sake of alignment

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

        s_win = sg.Window("Search", layout=layout, finalize=True, font=(settings.fonttype, int(settings.fontsize)))

        found: Union[List[Show], List[str]] = [""] * results

        while True:
            e, v = s_win.read()
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
                        s_win[f"s_title_{n}"].update(" ")
                        s_win[f"s_index_{n}"].update(" "*index_len)
                    for n in range(results):
                        if isinstance(found[n], Show):
                            s_win[f"s_title_{n}"].update(found[n].title)
                            s_win[f"s_index_{n}"].update(min_string_len(str(found_indices[n] + 1), index_len))
                            s_win[f"s_title_{n}"]\
                                .update(text_color=settings.text_colors[min(int(found[n].color),
                                                                            len(settings.text_colors) - 1)])
                            s_win[f"s_index_{n}"]\
                                .update(text_color=settings.text_colors[min(int(found[n].color),
                                                                            len(settings.text_colors) - 1)])
                except IndexError:
                    pass

            elif e[:8] == "s_delete":
                k = int(e[-1])

                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                delme = -1
                for ind, n in enumerate(shows):
                    if n.id == found[k].id:
                        delme = ind
                        break
                if delme != -1:
                    shows.pop(delme)
                s_win.close()
                self.restart()
                return

            elif e[:12] == "s_properties":
                k = int(e[-1])

                show = find_from_id(found[k].id, shows)
                data = show_properties(popshowname=show.title, popep=show.ep, popseas=show.season, poplink=show.link,
                                       popweight=show.weight)
                if data == 1:
                    continue

                for ind, tshow in enumerate(shows):
                    if tshow.id == show.id:
                        shows[ind].title = data["popshowname"]
                        shows[ind].ep = data["popep"]
                        shows[ind].season = data["popseas"]
                        shows[ind].link = data["poplink"]
                        shows[ind].weight = data["popweight"]
                        s_win.close()
                        self.restart()
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
                ]
        col4 = [[sg.In(sg.theme_input_background_color(), k="field_bg_color",
                       tooltip="The background color of the input fields")],
                ]
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
        window = MainWin()
        window.main_loop()

        settings.save()
        shows.save()
