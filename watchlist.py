from classes import *
import guide_strings
from default_values import delay_to_save_shows, update_release_vals_interval, recently_released_string

# noinspection PyPep8Naming
import PySimpleGUI as sg
from typing import List, Union
import mouse
import time


def is_valid_color(color: str) -> bool:
    """
    Checks whether a string is a hex color code

    :param color: A string
    :return: Returns True if the string col is a proper hex color code, such as "#FFFFFF"
    """
    if len(color) == 7 and color[0] == "#":
        for n in color[1:]:
            if (48 <= ord(n) <= 57) or (65 <= ord(n) <= 70) or (97 <= ord(n) <= 102):
                return True
            return False
    return False


def limit_string_len(string: str, length: int, use_ellipsis: bool = False) -> str:
    """
    Shortens a string so that its length doesn't exceed some integer. If the maximum length is 0 or < 0 then
    the string is returned as-is.

    :param string: The string to limit
    :param length: The maximum length of the string
    :param use_ellipsis: Whether the last three characters should be ... if the string has been shortened
    :return: A string with a maximum length of - length -
    """
    if len(string) > length > 0:
        if use_ellipsis:
            return f"{string[:length - 3].rstrip(' ')}..."
        return string[:length]
    return string


def get_suffix(string: str, splitter="-") -> str:
    """
    Retrieves the suffix from right click menu events. The standard of these events is to be suffixed by f"-{index}"
    """
    return string.split(splitter)[-1]


def get_prefix(string: str, splitter=":") -> str:
    """
    Retrieves the prefix of right click events. In these events, '::' is the delimiter between the shown and the unshown
    part of the event.
    """
    return string.split(splitter)[0]


def show_editor(title: str = "Show Editor", show: Show = None, show_purge: bool = False) -> Union[Show, bool]:
    """
    Opens a small window with all the relevant information about a show allowing these to be changed by the user.
    Then returning the show, if save was pressed and False if Cancel was pressed.
    If no show is None, then the function returns a dummy show with all the appropriate values and an id of -1.

    :param title: Title of the window
    :param show: If given, then all values will be changed in this show.
    :param show_purge: Whether to show the Purge Weight input field
    :return: True if something has been changed and False if nothing has been changed.
    """
    if show is None:  # make a dummy show.
        show = Show(color=settings.initial_show_color_index)
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
                                   [sg.B("Link")],
                                   [sg.InputText(show.get_link_string(), key="show_link", size=(15, 1))]
                               ]),
                               sg.Column([
                                   [sg.T("Weight")],
                                   [sg.InputText(show.weight, key="show_weight")]
                               ]),
                               sg.Column([
                                   [sg.T("Show Details")],
                                   [sg.Checkbox("", default=show.ep_season_relevant,
                                                key="show_ep_season_relevant")]
                               ]),
                               sg.Column([
                                   [sg.T("Hide")],
                                   [sg.Checkbox("", default=show.is_hidden,
                                                key="show_is_hidden")]
                               ])
                           ],
                           [sg.HSep()],
                           [
                            sg.Col([[sg.Column([
                               [sg.T("Release Info")],
                               [butt(show.release_info.release_string, key="show_release_info",
                                     tooltip="Press ME!",
                                     size=(19, 1))]
                           ]),
                               sg.Column([[sg.T()],
                                          [butt("Clear dismissal", key="dismiss_clear",
                                                visible=show.last_dismissal != 0)]]),
                           ]]),
                           sg.Col([
                               [sg.T("Ended")],
                               [sg.Checkbox("", key="ended_checkbox", default=show.ended)]
                           ]),
                           sg.Push(),
                           sg.Col([[
                               sg.Push(),
                               sg.Column([
                                   [sg.T("Purge Weight")],
                                   [sg.InputText(key="purge_weight",
                                                 tooltip="If a weight is written in this field,\n"
                                                         "then Release Info will be cleared\n"
                                                         "As such this field is useful for quickly discarding\n"
                                                         "shows, once they have been finished.")]
                               ]) if show_purge else sg.T()]])],
                           [sg.Button("Save", bind_return_key=True), sg.Button("Cancel")]],
                       disable_close=True,
                       auto_size_buttons=True,
                       auto_size_text=True,
                       default_element_size=(12, 1),
                       font=(settings.fonttype, settings.default_font_size),
                       keep_on_top=True)

    _link_list = show.links
    release_info = show.release_info
    last_dismissal = show.last_dismissal
    while True:
        button, data = window.read()
        if button == "show_release_info":
            release_info = get_release_info(release_info)
            window["show_release_info"].update(release_info.release_string)
        elif button == "dismiss_clear":
            last_dismissal = 0
            window["dismiss_clear"].update(visible=False)
        elif button == "Link":
            _link_list = graphical_string_list_manager(_link_list, "Links")
            temp_show = Show()
            temp_show.links = _link_list
            window["show_link"](temp_show.get_link_string())
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
        # Check whether the user given values are valid BEFORE making any changes to the show.
        data["show_ep"] = int(data["show_ep"])
        data["show_season"] = int(data["show_season"])
        data["show_weight"] = int(data["show_weight"])
    except ValueError:
        sg.popup_error(title="Couldn't convert to integer")
        return False

    do_release_update = False

    show.title = data["show_title"]
    show.ep = data["show_ep"]
    show.season = data["show_season"]
    show.set_link_string(data["show_link"])
    show.is_hidden = data["show_is_hidden"]
    show.ep_season_relevant = data["show_ep_season_relevant"]
    if show.ended != data["ended_checkbox"]:
        show.ended = data["ended_checkbox"]
        do_release_update = True

    if purge_weight is False:
        if show.release_info != release_info or show.last_dismissal != last_dismissal:
            show.last_dismissal = last_dismissal
            show.release_info = release_info
            do_release_update = True
        show.weight = data["show_weight"]
    else:
        show.ended = True
        show.weight = purge_weight
        show.last_dismissal = 0
        if settings.purge_color_index >= 0:
            show.color = settings.purge_color_index

    if do_release_update:
        shows.check_all_releases(allow_notifications=False)
    return show


def graphical_string_list_manager(initial_list: list[str], list_name="Strings") -> list[str]:
    layout = [
        [sg.T(list_name)],
        [sg.Listbox(initial_list, key="LIST", size=(48, 10))],
        [sg.HSep()],
        [sg.Input(key="NEW_ELEMENT")],
        [sg.Button("Delete")],
        [sg.Button("Add before"), sg.Button("Add after")],
        [sg.HSep()],
        [sg.Button("SAVE"), sg.Button("CANCEL")]
    ]

    new_list = initial_list.copy()

    window = sg.Window(f"{list_name} Editor", layout=layout)
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "CANCEL":
            window.close()
            return initial_list
        elif event == "SAVE":
            window.close()
            return new_list
        elif len(event) > 3 and event[:3] == "Add":
            index = new_list.index(values["LIST"][0]) if values["LIST"] else 0
            if event.removeprefix("Add ") == "after":
                try:
                    new_list = new_list[:index + 1] + [values["NEW_ELEMENT"]] + new_list[index + 1:]
                except IndexError:
                    new_list = new_list[:index] + [values["NEW_ELEMENT"]] + new_list[index:]
            else:
                new_list = new_list[:index] + [values["NEW_ELEMENT"]] + new_list[index:]
            window["LIST"](values=new_list)
        elif event == "Delete":
            if not values["LIST"]:
                continue
            selected = values["LIST"][0]
            new_list.remove(selected)
            window["LIST"](values=new_list)


def butt(button_text="", key=None, tooltip=None, butt_color=(False, None), border_width=None, size=(None, None),
         mouseover_colors=sg.theme_background_color(), disabled=False, right_click_menu=None,
         bind_return_key=False, visible=True) -> sg.Button:
    """
    A wrapper function for sg.Button with some different default values
    """
    if not butt_color[0]:
        butt_color = (settings.button_color, butt_color[1])
    return sg.Button(button_text=button_text, key=key, tooltip=tooltip, button_color=butt_color,
                     border_width=border_width, size=size, mouseover_colors=mouseover_colors, disabled=disabled,
                     right_click_menu=right_click_menu, bind_return_key=bind_return_key, visible=visible)


def get_date_wise_release_string(initial_release_string: str = "") -> str:
    """
    Retrieves a release string from the user using a GUI window. This release string is defined by day, month, year.
    Therefore, it is also repeating every month, year or never.
    """
    parsed = parse_release_string(initial_release_string)
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    if parsed:
        if isinstance(parsed[0], tuple):
            day, month, year = parsed[0]
        hour = parsed[1]
        minute = parsed[2]

    layout = [
        [sg.Push(), sg.CalendarButton("Calendar", target="HIDDEN"), sg.Push(), sg.In(visible=False, key="HIDDEN")],
        [sg.Text("Day:"), sg.Text(day if day else "", key="day"),
         sg.Text("Month:"), sg.Text(month if month else "", key="month"),
         sg.Text("Year:"), sg.Text(year if year else "", key="year")],
        [sg.Radio("Never Repeat", "Repetition", enable_events=True, key="never")],
        [sg.Radio("Repeat Yearly", "Repetition", enable_events=True, key="yearly")],
        [sg.Radio("Repeat Monthly", "Repetition", True, enable_events=True, key="monthly")],
        [sg.In(hour, key="hour", enable_events=True, justification="e"),
         sg.T(":"),
         sg.In(minute, key="minute", enable_events=True)],
        [sg.T("Current String:"), sg.T(f"{f'.{day}' if day else ''}", key="current", size=(19, 1))],
        [sg.B("Save", bind_return_key=True), sg.B("Cancel")]
    ]

    window = sg.Window("Pick a Date", layout=layout, keep_on_top=True,
                       font=(settings.fonttype, settings.default_font_size),
                       default_element_size=(9, 1))

    def get_current_string() -> str:
        """
        Returns the currently defined release info string.
        """
        if window["never"].get():
            return f".{day} /{month} <{year} {min(60, hour)}:{min(60, minute)}"
        if window["yearly"].get():
            return f".{day} /{month} {hour}:{minute}"
        if window["monthly"].get():
            return f".{day} {hour}:{minute}"

    def set_upper_strings():
        """
        Displays the relevant user values on the window
        """
        window["day"].update(value=day if day else 'N/A')
        window["month"].update(value=month if month and window["never"].get() or window["yearly"].get() else 'N/A')
        window["year"].update(value=year if year and window["never"].get() else 'N/A')

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            window.close()
            return initial_release_string
        elif event == "__TIMEOUT__":
            if values["HIDDEN"]:
                dat = datetime.datetime.fromisoformat(values["HIDDEN"])
                day, month, year = dat.day, dat.month, dat.year
                window["current"].update(value=get_current_string())
                set_upper_strings()
                window["HIDDEN"].update(value="")
        elif event in ("monthly", "yearly", "never"):
            window["current"].update(value=get_current_string())
            set_upper_strings()
        elif event == "hour":
            try:
                hour = int(values["hour"])
            except ValueError:
                hour = 0
            window["current"].update(value=get_current_string())
            set_upper_strings()
        elif event == "minute":
            try:
                minute = int(values["minute"])
            except ValueError:
                minute = 0
            window["current"].update(value=get_current_string())
            set_upper_strings()
        elif event == "Cancel":
            window.close()
            return initial_release_string
        elif event == "Save":
            window.close()
            return get_current_string()


def get_release_info(initial_release_info: ReleaseInfo = ReleaseInfo()) -> ReleaseInfo:
    """
    Opens a GUI which allows the user to define a ReleaseInfo object. This Object is then returned. If, however,
    the user cancels, then the initial object is returned
    """
    if initial_release_info.is_defined():
        weekday = initial_release_info.weekday
        hour = initial_release_info.hour
        minute = initial_release_info.minute
    else:
        hour = 0
        minute = 0
        weekday = 7
    layout = [
        [sg.Push(), butt("MON"), butt("TUE"), butt("WED"), butt("THU"), butt("FRI"), butt("SAT"), butt("SUN"),
         sg.Push()],
        [sg.Push(), sg.I(hour, key="hour", enable_events=True, justification="e"), sg.T(":"),
         sg.I(minute, key="minute", enable_events=True), sg.Push()],
        [butt("Save", bind_return_key=True), butt("Cancel"), sg.Push(), sg.B("DATE"), sg.Push(), sg.Button("CLEAR"),
         sg.T(initial_release_info.release_string, key="release_string", size=(19, 1))]
    ]

    weekday_as_string = ""
    if weekday != 7:
        for i in weekday_to_int:
            if weekday_to_int[i] == weekday:
                weekday_as_string = i.upper()

    rel_win = sg.Window("Release Picker", layout=layout, default_element_size=(9, 1),
                        font=(settings.fonttype, settings.default_font_size), keep_on_top=True)

    def write_release_string():
        """
        Writes the release string on the window.
        """
        if not weekday_as_string and not hour and not minute:
            rel_win["release_string"].update(value="")
            return
        rel_win["release_string"].update(value=f"{weekday_as_string} {min(60, hour)}:"
                                               f"{0 if minute < 10 else ''}{min(60, minute)}")

    while True:
        event, values, = rel_win.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            rel_win.close()
            return initial_release_info
        elif event == "Save":
            rel_win.close()
            return ReleaseInfo(rel_win["release_string"].get())
        elif event == "DATE":
            rel_win["release_string"].update(value=get_date_wise_release_string())
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
        elif event in ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"):
            weekday_as_string = event
            write_release_string()
        elif event == "CLEAR":
            weekday_as_string = ""
            hour = 0
            minute = 0
            write_release_string()
            rel_win["hour"].update(value="0")
            rel_win["minute"].update(value="0")


def get_existing_weights(shows_obj: ShowsFileHandler):
    """
    Returns a dict with the used weights as keys and the amount of shows using them as weights as their value.
    """
    weight_dict = {}
    for show in shows_obj:
        if show.weight in weight_dict:
            weight_dict[show.weight] += 1
            continue
        weight_dict[show.weight] = 1
    return weight_dict


def change_weights(change_dict: dict[int, int]):
    shows_changed = []
    for weight in change_dict:
        for show in shows:
            if show.weight == weight and show.id not in shows_changed:
                show.weight = change_dict[weight]
                shows_changed.append(show.id)


def weight_control_panel():
    """
    Opens a window which allows the user to modify the weights of shows on a large scale.
    """
    weight_dict = get_existing_weights(shows)
    original_weights = weight_dict.copy()
    layout = [
        [sg.Col([[sg.Text("Weight"), sg.Text("Amount")]])],
        [sg.Col([
            [sg.Text(f"{key}", key=f"weight_{ind}", size=(5, 1), justification="e"),
             sg.Push(),
             sg.Text(f" -> "),
             sg.Push(),
             sg.Text(f"{weight_dict[key]}", size=(4, 1)),
             sg.Push(),
             sg.Button("↑", key=f"up_{ind}"),
             sg.Push(),
             sg.Button(f"↓", key=f"down_{ind}")] for ind, key in enumerate(weight_dict)
        ]),
        ],
        [sg.Button("SAVE"), sg.Button("CANCEL")]
    ]
    window = sg.Window("Weight Control Panel", layout=layout, font=(settings.fonttype, settings.default_font_size))

    def write_weights():
        for ind, key in enumerate(weight_dict):
            window[f"weight_{ind}"](key)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "CANCEL":
            window.close()
            break
        elif event.startswith("up_"):
            index = int(event.removeprefix("up_"))
            new_weights = {}
            for ind, key in enumerate(weight_dict):
                if ind <= index:
                    new_weights[key+1] = weight_dict[key]
                    continue
                new_weights[key] = weight_dict[key]
            weight_dict = new_weights
            write_weights()
        elif event.startswith("down_"):
            index = int(event.removeprefix("down_"))
            new_weights = {}
            for ind, key in enumerate(weight_dict):
                if ind >= index:
                    new_weights[key-1] = weight_dict[key]
                    continue
                new_weights[key] = weight_dict[key]
            weight_dict = new_weights
            write_weights()
        elif event == "SAVE":
            new_weights_list = [key for key in weight_dict]
            change_dict = {}
            for ind, key in enumerate(original_weights):
                change_dict[key] = new_weights_list[ind]
            change_weights(change_dict)
            window.close()
            break


def guide():
    """
    Opens a non-interactive window showing some user guides.
    """
    layout = [
        [sg.TabGroup([[sg.Tab("Introduction", [[sg.T(guide_strings.introduction)]]),
                       sg.Tab("Important", [[sg.T(guide_strings.important)]]),
                       sg.Tab("Settings I", [[sg.T(guide_strings.settings_i)]]),
                       sg.Tab("Settings II", [[sg.T(guide_strings.settings_ii)]]),
                       sg.Tab("Settings III", [[sg.T(guide_strings.settings_iii)]]),
                       sg.Tab("Show Editor", [[sg.T(guide_strings.show_editor)]]),
                       sg.Tab("Release", [[sg.T(guide_strings.release)]]),
                       sg.Tab("Search", [[sg.T(guide_strings.search)]]),
                       sg.Tab("Quick Menus", [[sg.T(guide_strings.quick_menus)]]),
                       ]])]
    ]
    window = sg.Window("Guide", layout=layout, font=(settings.fonttype, settings.default_font_size))
    while True:
        e, v = window.read()
        if e == sg.WIN_CLOSED:
            window.close()
            break


def update_preferences():
    """
    Opens a GUI that allows the user to change the settings.
    """
    col1 = [[sg.T("Font size:")],
            [sg.T("Font type:")],
            [sg.Col([[sg.T("Text colors:"), sg.Push(),
                      sg.Button(" + ", key="text_add"),
                      sg.Button(" - ", key="text_remove")]])],
            [sg.ColorChooserButton("Background color:", target="bg_color")],
            [sg.ColorChooserButton("Menu background color:", target="menu_bg_color")],
            [sg.T("Menu font size:")],
            [sg.ColorChooserButton("Button Color", target="buttoncolor")],
            [sg.T("Search Results")],
            [sg.T("Title Length")],
            [sg.T("Show Cut-off")],
            [sg.T("Purge Show Color")],
            [sg.T("Initial Show Color")]]
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
                           " of shows on display.\nCan be toggled by the '^' button")],
            [sg.Combo([n for n in settings.text_colors],
                      default_value=settings.text_colors[settings.purge_color_index]
                      if settings.purge_color_index != -1
                      else "",
                      key="purge_show_color")],
            [sg.Combo([n for n in settings.text_colors],
                      default_value=settings.text_colors[settings.initial_show_color_index],
                      key="initial_show_color")]]
    col3 = [[sg.ColorChooserButton("Field Background Color:", target="field_bg_color")],
            [sg.T("Shorten With Ellipsis:")],
            [sg.T("Release Grace Period:")],
            [sg.ColorChooserButton("Default Text Color:", target="default_text_color")],
            [sg.T("Default Font Size:")],
            [sg.T("Recent Releases To Top:")],
            [sg.T("Recent Release Weight Add:")],
            [sg.T("Sort by Upcoming:")],
            [sg.T("Alternate Show Background:")],
            [sg.ColorChooserButton("Alternate Show Bg Color:", target="secondary_show_background")],
            [sg.T("Send Notifications:")],
            [sg.T("Precise Time Left:")],
            ]
    col4 = [[sg.In(sg.theme_input_background_color(), k="field_bg_color",
                   tooltip="The background color of the input fields",
                   background_color=sg.theme_background_color())],
            [sg.Checkbox(default=settings.shorten_with_ellpisis, k="shorten_with_ellipsis", text="",
                         text_color=settings.button_color, tooltip='Whether or not to end shortened titles'
                                                                   ' with "..."')],
            [sg.In(settings.release_grace_period, k="release_grace_period",
                   tooltip="The number of hours after a show has been released that the show should be marked\n"
                           "as having recently been released.")],
            [sg.In(settings.default_text_color, k="default_text_color",
                   tooltip="The text color to be used in subwindows.",
                   background_color=sg.theme_background_color())],
            [sg.In(settings.default_font_size, key="default_font_size", tooltip="The font size in subwindows")],
            [sg.Checkbox("", key="move_recently_released_to_top", default=settings.move_recently_released_to_top)],
            [sg.In(settings.weight_to_add, key="weight_to_add", tooltip="The weight that will be added to a show"
                                                                        "when it is newly released.")],
            [sg.Checkbox("", key="sort_by_upcoming", default=settings.sort_by_upcoming)],
            [sg.Checkbox("", key="enable_secondary_show_background",
                         default=settings.enable_secondary_show_background)],
            [sg.In(settings.secondary_show_background, k="secondary_show_background",
                   background_color=sg.theme_background_color())],
            [sg.Checkbox("", key="send_notifications",
                         default=settings.send_notifications)],
            [sg.Checkbox("", key="remaining_time_prioritise_precision",
                         default=settings.remaining_time_prioritise_precision)],
            ]
    pref_win = sg.Window("Preferences", layout=[
        [sg.Col([[col1[i][0], sg.Push(), col2[i][0]] for i in range(len(col1))]),
         sg.VSep(),
         sg.Col([[col3[i][0], sg.Push(), col4[i][0]] for i in range(len(col3))],
                expand_y=True, element_justification="n")],
        [sg.Button("Save", bind_return_key=True), sg.Button("Cancel")]], default_element_size=(16, 1),
                         font=(settings.fonttype, settings.default_font_size))
    temp_text_colors = settings.text_colors.copy()

    while True:
        e, v = pref_win.read()
        if e == sg.WIN_CLOSED or e == "Cancel":
            pref_win.close()
            break
        elif e == "text_add":
            _, hex_color = sg.askcolor()
            if hex_color:
                temp_text_colors.append(hex_color)
            pref_win["txtcolor"].update("-".join(temp_text_colors))
        elif e == "text_remove":
            _e, _v = sg.Window("Choose one to delete", layout=[[sg.Combo(temp_text_colors, k="combo")],
                                                               [sg.Button("Save", bind_return_key=True),
                                                                sg.Button("Cancel")]]).read(close=True)
            if _e == "Save" and _v["combo"]:
                temp_text_colors.remove(_v["combo"])
            pref_win["txtcolor"].update("-".join(temp_text_colors))
        elif e == "Save":
            try:
                int(pref_win["fsize"].get())
                int(pref_win["menu_font_size"].get())
                int(pref_win["sresults"].get())
                int(pref_win["title_length"].get())
                int(pref_win["showamount"].get())
                int(pref_win["release_grace_period"].get())
                int(pref_win["default_font_size"].get())
                int(pref_win["weight_to_add"].get())
                if not is_valid_color(pref_win["buttoncolor"].get()):
                    raise ValueError

                if not is_valid_color(pref_win["menu_bg_color"].get()):
                    raise ValueError

                if not is_valid_color(pref_win["bg_color"].get()):
                    raise ValueError

                if not is_valid_color(pref_win["field_bg_color"].get()):
                    raise ValueError

                if not is_valid_color(pref_win["default_text_color"].get()):
                    raise ValueError

                if not is_valid_color(pref_win["secondary_show_background"].get()):
                    raise ValueError

                if not v["purge_show_color"] in settings.text_colors:
                    raise ValueError

                if not v["initial_show_color"] in settings.text_colors:
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

            written_text_colors = pref_win["txtcolor"].get().split("-")
            if settings.text_colors != written_text_colors:
                shows.new_text_colors(settings.text_colors, written_text_colors)
                settings.text_colors = written_text_colors

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
            settings.default_text_color = pref_win["default_text_color"].get()
            settings.default_font_size = int(pref_win["default_font_size"].get())
            settings.move_recently_released_to_top = pref_win["move_recently_released_to_top"].get()
            settings.weight_to_add = int(pref_win["weight_to_add"].get())
            settings.sort_by_upcoming = pref_win["sort_by_upcoming"].get()
            settings.enable_secondary_show_background = pref_win["enable_secondary_show_background"].get()
            settings.secondary_show_background = pref_win["secondary_show_background"].get()
            settings.send_notifications = pref_win["send_notifications"].get()
            settings.purge_color_index = settings.text_colors.index(v["purge_show_color"])
            settings.initial_show_color_index = settings.text_colors.index(v["initial_show_color"])
            settings.remaining_time_prioritise_precision = pref_win["remaining_time_prioritise_precision"].get()

            return settings.save()


class MainWin:
    def __init__(self, main_loop=False):
        """
        Initialises the main PySimpleGUI window

        :param main_loop: Calls self.main_loop() if true
        :type main_loop: bool
        """
        global should_restart

        self.shouldbreak = False

        sg.theme_text_color(settings.default_text_color)
        sg.theme_element_text_color(settings.button_color)
        sg.theme_element_background_color(sg.theme_background_color())
        sg.theme_text_element_background_color(sg.theme_background_color())
        sg.theme_slider_color(sg.theme_background_color())
        sg.theme_button_color((settings.button_color, sg.theme_background_color()))

        self.time_till_release_len = 4

        self.delete_elements = []
        self.title_elements = []
        self.time_till_release_elements = []
        self.ep_minus_elements = []
        self.ep_plus_elements = []
        self.season_minus_elements = []
        self.season_plus_elements = []
        self.link_elements = []
        self.properties_elements = []
        self.index_elements = []
        self.release_elements = []
        self.column_elements = []

        self.number_of_displayed_shows = len(shows) if settings.show_all else min(len(shows), settings.show_amount)

        self.shows_col = sg.Col([[self.column_element(ind)] for ind in range(self.number_of_displayed_shows)],
                                vertical_scroll_only=True,
                                scrollable=True,
                                expand_x=True,
                                expand_y=True)
        self.shows_col_contents_changed = False
        self.number_of_invisible_rows = 0
        self.last_release_update = 0
        self.last_show_change = 0

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
                               default=settings.releases_visible, enable_events=True),
                   sg.Checkbox("", key="till_release_checkbox", text_color=settings.button_color,
                               tooltip="Enables or disables the showing of time till release",
                               default=settings.show_till_release, enable_events=True),
                   sg.Checkbox("", key="display_hidden_checkbox", text_color=settings.button_color,
                               tooltip="Enables or disables the showing of hidden shows",
                               default=settings.display_hidden, enable_events=True),
                   butt(" 📖 ", key="open_guide", border_width=0, tooltip="Open guide"),
                   butt(" 🏋 ", key="open_weight_control_panel", border_width=0, tooltip="Open Weight Control Panel")]
                  ]

        layout = [
            [sg.Col(topcol)],
            [self.shows_col],
        ]

        # noinspection PyTypeChecker
        self.win = sg.Window(title="Watchlist",
                             layout=layout,
                             auto_size_text=True,
                             auto_size_buttons=True,
                             resizable=True,
                             size=settings.initialwinsize,
                             font=(settings.fonttype, int(settings.fontsize)),
                             border_depth=0,
                             finalize=True,
                             location=settings.initialwinpos,
                             titlebar_background_color=sg.theme_background_color(),
                             margins=(0, 0),
                             element_padding=(3, 1),
                             use_custom_titlebar=False,
                             titlebar_text_color=settings.text_colors[0],
                             return_keyboard_events=True,
                             right_click_menu_font=(settings.fonttype, settings.right_click_fontsize),
                             right_click_menu_background_color=sg.theme_background_color(),
                             right_click_menu_text_color=settings.button_color,
                             right_click_menu_selected_colors=(settings.button_color,
                                                               settings.right_click_selected_background),
                             icon="GenIko.ico")

        self.sort_shows_and_display()

        for key in ("add_show", "preferences", "show_all", "search_button", "index_checkbox", "release_checkbox",
                    "open_guide", "open_weight_control_panel"):
            self.win[key].block_focus()
            self.win[key].set_cursor("plus")

        if main_loop:
            self.main_loop()

    def main_loop(self):
        """
        Main loop of the PySimpleGUI window
        """
        while not self.shouldbreak:
            settings.initialwinpos = self.win.CurrentLocation()
            settings.initialwinsize = self.win.Size
            event, values = self.win.read(timeout=100)

            # The methods called within the if-statement below are intended to update the scrollable area of the
            # .show_col column. However, it seems that this might be a bit inconsistent - i won't look further into
            # right now. BUT if there are problems, they probably stem from here.
            if self.shows_col_contents_changed:
                self.shows_col_contents_changed = False
                self.win.visibility_changed()
                self.shows_col.contents_changed()

            # if event != "__TIMEOUT__":
            #    print(event)

            if event == sg.WIN_CLOSED or self.shouldbreak or event == "Close":
                self.close()
                break
            elif event.startswith("Mouse"):  # Ignore MouseWheel:Up and MouseWheel:Down events
                pass
            elif event == "__TIMEOUT__":
                now = time.time()
                if self.last_show_change != 0 and now - self.last_show_change > delay_to_save_shows:
                    shows.save()
                    self.last_show_change = 0

                if self.last_release_update + update_release_vals_interval < now:
                    self.last_release_update = time.time()
                    self.sort_shows_and_display()

                continue

            elif event.startswith("link:"):
                self.get_show_from_visual_index(int(event.removeprefix("link:"))).open_link()

            elif event.startswith("delete:"):
                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                show = self.get_show_from_visual_index(event.removeprefix("delete:"))
                shows.remove(show)
                self.sort_shows_and_display()

            elif event.startswith("Eplus:"):
                show = self.get_show_from_visual_index(event.removeprefix("Eplus:"))
                if show.ep_season_relevant:
                    show.ep = int(show.ep) + 1
                    self.win[event](value=show.ep)
                    self.update_last_show_change()

            elif event.startswith("Eminus:"):
                show_index = event.removeprefix("Eminus:")
                show = self.get_show_from_visual_index(show_index)
                if show.ep_season_relevant:
                    show.ep = int(show.ep) - 1
                    self.win[f"Eplus:{show_index}"](value=show.ep)
                    self.update_last_show_change()

            elif event.startswith("title:"):
                show_index = event.removeprefix("title:")
                show = self.get_show_from_visual_index(show_index)
                self.update_show_color(show,
                                       0 if show.color + 1 >= len(settings.text_colors) else show.color + 1,
                                       show_index=show_index)

            elif event.startswith("Splus:"):
                show = self.get_show_from_visual_index(event.removeprefix("Splus:"))
                if show.ep_season_relevant:
                    show.season = str(int(show.season) + 1)
                    self.win[event].update(value=show.season)
                    self.update_last_show_change()

            elif event.startswith("Sminus:"):
                show_index = event.removeprefix("Sminus:")
                show = self.get_show_from_visual_index(show_index)
                if show.ep_season_relevant:
                    show.season = str(int(show.season) - 1)
                    self.win[f"Splus:{show_index}"].update(value=show.season)
                    self.update_last_show_change()

            elif event == "index_checkbox":
                settings.indices_visible = self.win["index_checkbox"].get()
                for show_index in range(self.number_of_displayed_shows):
                    self.win[f"index:{show_index}"].update(visible=settings.indices_visible)

            elif event == "release_checkbox":
                settings.releases_visible = self.win["release_checkbox"].get()
                self.update_release_column()

            elif event == "till_release_checkbox":
                settings.show_till_release = self.win["till_release_checkbox"].get()
                self.update_till_release_column()

            elif event == "display_hidden_checkbox":
                settings.display_hidden = self.win["display_hidden_checkbox"].get()
                self.sort_shows_and_display()

            elif event.startswith("properties:"):
                show = self.get_show_from_visual_index(event.removeprefix("properties:"))
                did_something = show_editor(show=show, show_purge=True)
                if not did_something:
                    continue
                self.sort_shows_and_display()

            elif event == "h":  # Move self.win to mouse
                mouse_pos = mouse.get_position()
                self.win.move(*mouse_pos)

            elif event == "open_guide":
                guide()

            elif event == "open_weight_control_panel":
                weight_control_panel()

            elif event == "preferences":
                if update_preferences():
                    self.restart()
                    break

            elif event == "show_all":
                self.toggle_show_all()

            elif event == "search_button":
                self.search(results=settings.search_results)

            elif event == "add_show":
                show = show_editor()
                if not show:
                    continue
                show.id = shows.highest_id() + 1
                shows.append(show)
                self.sort_shows_and_display(allow_release_notifications=False)

            elif "::multi_links-" in event:
                ref_show = self.get_show_from_suffix(event)
                for show in shows:
                    if ref_show.color == show.color:
                        show.open_link()

            elif "::auto_open_on_release-" in event:
                show = self.get_show_from_suffix(event)
                show.auto_open_link_on_release = not show.auto_open_link_on_release
                self.update_link_color()

            elif "::tit_color-" in event:
                col = event.split(":")[0]
                show, show_index = self.get_show_and_index_from_suffix(event)
                col_index = settings.text_colors.index(col)
                self.update_show_color(show, col_index, show_index)

            elif "::tit_color_mass-" in event:
                col = event.split(":")[0]
                clicked_show = self.get_show_from_suffix(event)
                match_color = clicked_show.color
                col_index = settings.text_colors.index(col)
                for show in shows:
                    if show.color == match_color and show.weight == clicked_show.weight:
                        show.color = col_index
                self.sort_shows_and_display()

            elif "::hide_show-" in event:
                show = self.get_show_from_suffix(event)
                show.is_hidden = not show.is_hidden
                self.sort_shows_and_display()

            elif "::weight-" in event:
                add_weight = int(get_prefix(event))
                show = self.get_show_from_suffix(event)
                show.weight += add_weight
                self.sort_shows_and_display()

            elif "::show_details-" in event:
                show = self.get_show_from_suffix(event)
                show.ep_season_relevant = not show.ep_season_relevant
                self.sort_shows_and_display()

            elif "::dismissal-" in event:
                show = self.get_show_from_suffix(event)
                show.last_dismissal = time.time()
                self.sort_shows_and_display()

            elif "::dismissal+ep+1-" in event:
                show = self.get_show_from_suffix(event)
                show.last_dismissal = time.time()
                if show.ep_season_relevant:
                    show.ep += 1
                self.sort_shows_and_display()

            elif "::open_released-" in event:
                for show in shows:
                    if show.is_recently_released:
                        show.open_link()

    def get_show_and_index_from_suffix(self, string: str, splitter: str = None) -> tuple[Show, int]:
        """
        Retrieves the show and index from a right click event.
        """
        if splitter is None:
            index = int(get_suffix(string))
        else:
            index = int(get_suffix(string, splitter))
        return self.get_show_from_visual_index(index), index

    def get_show_from_suffix(self, string: str, splitter: str = None) -> Show:
        """
        Retrieves the show from a right click event
        """
        return self.get_show_and_index_from_suffix(string, splitter)[0]

    @staticmethod
    def num_of_shows_to_display() -> int:
        """
        Returns how many shows should currently be displayed
        """
        if settings.show_all:
            if settings.display_hidden:
                return len(shows)
            return shows.get_num_of_shown()
        return min(settings.show_amount, shows.get_num_of_shown())

    def update_last_show_change(self):
        """
        Updates when the last time the data of a show was changed. This is used for determining when shows should
        be saved to disk
        """
        self.last_show_change = time.time()

    @staticmethod
    def get_show_from_visual_index(__index):
        """
        Returns the corresponding show object to a visual index. (This means settings.display_hidden and hidden shows
        are taken into account)
        """
        if settings.display_hidden:
            return shows.from_index(__index)
        return shows.from_index_ignore_hidden(__index)

    def sort_shows_and_display(self, allow_release_notifications=True):
        """
        Sorts and displays all shows. This function effectively updates the GUI.
        """
        shows.check_all_releases(allow_notifications=allow_release_notifications)
        shows.do_sorting(
            weight_to_add=settings.weight_to_add if settings.move_recently_released_to_top else 0,
            sort_by_upcoming=settings.sort_by_upcoming,
        )

        to_display = self.num_of_shows_to_display()
        if to_display < self.number_of_displayed_shows:
            self.shorten_by_x_rows(self.number_of_displayed_shows - to_display)
        if to_display > self.number_of_displayed_shows:
            self.extend_by_x_rows(to_display - self.number_of_displayed_shows)

        self.update_link_color()
        for ind in range(self.number_of_displayed_shows):
            show = self.get_show_from_visual_index(ind)
            color = settings.get_color(show.color)

            self.win[f"title:{ind}"].update(value=limit_string_len(show.title, settings.max_title_display_len,
                                                                   use_ellipsis=settings.shorten_with_ellpisis),
                                            text_color=color)
            self.win[f"till_release:{ind}"].update(value=show.string_time_till_release(
                precise_time_left=settings.remaining_time_prioritise_precision
            ),
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

        self.update_release_column()
        self.update_till_release_column()
        self.update_last_show_change()

    def update_link_color(self):
        """
        Ensures that the color of all link buttons is correct
        """
        for index, show in enumerate(shows[:self.number_of_displayed_shows]):
            if show.auto_open_link_on_release:
                self.win[f"link:{index}"] \
                    .update(button_color=(settings.get_color(show.color), None))
                continue
            self.win[f"link:{index}"] \
                .update(button_color=(settings.button_color, None))

    def update_release_column(self):
        """
        Ensures that the .is_recently_released is correctly shown on the GUI
        Note that this function does not update the release status of shows, it merely displays it.
        """
        for index, show in enumerate(shows[:self.number_of_displayed_shows]):
            self.win[f"release:{index}"] \
                .update(visible=settings.releases_visible and show.is_recently_released)

    def update_till_release_column(self):
        """
        Ensures that the visibility of the time_till_release columns is correct
        """
        for index, show in enumerate(shows[:self.number_of_displayed_shows]):
            self.win[f"till_release:{index}"] \
                .update(visible=settings.show_till_release)

    def update_show_color(self, show: Show, new_color_id: int, show_index=None):
        """
        Changes the color of a single show. Both updates the show and updates the GUI
        """
        show.color = new_color_id
        if show_index is None:
            show_index = shows.get_index(show)
        color = settings.get_color(new_color_id)
        self.win[f"index:{show_index}"].update(text_color=color)
        self.win[f"title:{show_index}"].update(text_color=color)
        self.win[f"till_release:{show_index}"].update(text_color=color)
        self.win[f"Eminus:{show_index}"].update(text_color=color)
        self.win[f"Eplus:{show_index}"].update(text_color=color)
        self.win[f"Splus:{show_index}"].update(text_color=color)
        self.win[f"Sminus:{show_index}"].update(text_color=color)
        self.win[f"release:{show_index}"].update(text_color=color)
        self.update_last_show_change()

    def close(self):
        """
        Closes the main window
        """
        self.shouldbreak = True
        self.win.close()

    def restart(self):
        """
        Closes the main window and restarts thereafter.
        """
        global should_restart
        should_restart = True
        self.close()

    def toggle_show_all(self):
        """
        Toggles the show_all setting.
        """
        settings.show_all = not settings.show_all
        self.restart()

    def search(self, results):
        """
        Opens a small GUI that allows the user to search through shows and access the properties of these shows. Or
        delete them.
        """
        index_len = 4  # The minimum length of the Text element in the index column. Used for alignment

        delcol = [butt("DEL", key=f"s_delete_{n}", mouseover_colors="#AA0000", border_width=0) for n in range(results)]

        titcol = [sg.Text(shows[n].title, key=f"s_title_{n}", enable_events=True,
                          text_color=settings.get_color(shows[n].color),
                          size=(37, 1)) for n in range(results)]

        index_col = [sg.Text(f"{n + 1: >{index_len}}", key=f"s_index_{n}",
                             text_color=settings.get_color(shows[n].color))
                     for n in range(results)]

        propcol = [butt("⛭", key=f"s_properties_{n}", border_width=0) for n in range(results)]

        rescol = [[delcol[n], titcol[n], index_col[n], propcol[n]] for n in range(results)]

        layout = [[sg.T("Search:"), sg.In(key="search", enable_events=True, size=(40, 1))],
                  [sg.Col(rescol)]]

        search_win = sg.Window("Search", layout=layout, finalize=True, font=(settings.fonttype,
                                                                             settings.default_font_size))

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
                                .update(text_color=settings.get_color(int(found[n].color)))
                            search_win[f"s_index_{n}"] \
                                .update(text_color=settings.get_color(int(found[n].color)))
                except IndexError:
                    pass

            elif e.startswith("s_delete_"):
                k = int(e.removeprefix("s_delete_"))
                if not found[k] or sg.popup_yes_no("Are you sure?") == "No":
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
                if not found[k]:
                    continue
                show = shows.from_id(found[k].id)
                did_something = show_editor(show=show, show_purge=True)
                if not did_something:
                    continue
                search_win.close()
                self.sort_shows_and_display()
                return

    def delete_element(self, index) -> sg.Button:
        """
        Returns a new DEL button element
        """
        self.delete_elements.append(butt("DEL",
                                         key=f"delete:{index}",
                                         mouseover_colors="#AA0000",
                                         border_width=0,
                                         butt_color=(False, self.get_background_color_to_use(index))))
        return self.delete_elements[-1]

    def title_element(self, index) -> sg.Text:
        """
        Returns a new title text element
        """
        self.title_elements.append(sg.Text(key=f"title:{index}",
                                           size=(abs(settings.max_title_display_len), 1),
                                           enable_events=True,
                                           right_click_menu=["",
                                                             [f"{m}::tit_color-{index}" for m in
                                                              settings.text_colors] + [
                                                                 "All with this weight and color",
                                                                 [f"{m}::tit_color_mass-{index}" for m in
                                                                  settings.text_colors],
                                                                 f"Hide::hide_show-{index}"]],
                                           background_color=self.get_background_color_to_use(index)))
        return self.title_elements[-1]

    def time_till_release_element(self, index) -> sg.Text:
        """
        Returns a new time_till_release element
        """
        self.time_till_release_elements.append(sg.Text(key=f"till_release:{index}",
                                                       size=(self.time_till_release_len, 1),
                                                       background_color=self.get_background_color_to_use(index)))
        return self.time_till_release_elements[-1]

    def ep_minus_element(self, index) -> sg.Text:
        """
        Returns a new ep_minus element
        """
        self.ep_minus_elements.append(sg.Text(size=(3, 1),
                                              enable_events=True,
                                              key=f"Eminus:{index}",
                                              background_color=self.get_background_color_to_use(index)))
        return self.ep_minus_elements[-1]

    def ep_plus_element(self, index) -> sg.Text:
        """
        returns a new ep_plus element
        """
        self.ep_plus_elements.append(sg.Text(key=f"Eplus:{index}",
                                             enable_events=True,
                                             size=(4, 1),
                                             background_color=self.get_background_color_to_use(index)))
        return self.ep_plus_elements[-1]

    def season_minus_element(self, index) -> sg.Text:
        """
        returns a nre season_minus element
        """
        self.season_minus_elements.append(sg.Text(size=(2, 1),
                                                  enable_events=True,
                                                  key=f"Sminus:{index}",
                                                  background_color=self.get_background_color_to_use(index)))
        return self.season_minus_elements[-1]

    def season_plus_element(self, index) -> sg.Text:
        """
        returns a new season_plus element
        """
        self.season_plus_elements.append(sg.Text(size=(3, 1),
                                                 enable_events=True,
                                                 key=f"Splus:{index}",
                                                 background_color=self.get_background_color_to_use(index)))
        return self.season_plus_elements[-1]

    def link_element(self, index) -> sg.Button:
        """
        returns a new LINK button element
        """
        self.link_elements.append(butt("LINK",
                                       key=f"link:{index}",
                                       border_width=0,
                                       right_click_menu=["",
                                                         [f"Open all links with this color::multi_links-{index}",
                                                          f"Open on release::auto_open_on_release-{index}"]],
                                       butt_color=(False, self.get_background_color_to_use(index))))
        return self.link_elements[-1]

    def properties_element(self, index) -> sg.Button:
        """
        Returns a new properties button element
        """
        self.properties_elements.append(butt("⛭",
                                             key=f"properties:{index}",
                                             border_width=0,
                                             right_click_menu=["",
                                                               ["Weight", [f"+2::weight-{index}",
                                                                           f"+1::weight-{index}",
                                                                           f"-1::weight-{index}",
                                                                           f"-2::weight-{index}"],
                                                                f"Show Details::show_details-{index}",
                                                                f"Hide::hide_show-{index}"]],
                                             butt_color=(False, self.get_background_color_to_use(index))))
        return self.properties_elements[-1]

    def index_element(self, index) -> sg.Text:
        """
        Returns a new index element
        """
        self.index_elements.append(sg.Text(str(index + 1),
                                           key=f"index:{index}",
                                           visible=settings.indices_visible,
                                           background_color=self.get_background_color_to_use(index)))
        return self.index_elements[-1]

    def release_element(self, index) -> sg.Text:
        """
        Returns a new release element
        """
        self.release_elements.append(sg.Text(recently_released_string,
                                             key=f"release:{index}",
                                             visible=False,
                                             right_click_menu=["", [f"Dismiss::dismissal-{index}",
                                                                    f"Dismiss Ep++::dismissal+ep+1-{index}",
                                                                    f"Open Released::open_released-{index}"]],
                                             background_color=self.get_background_color_to_use(index)))
        return self.release_elements[-1]

    def column_element(self, index) -> sg.Column:
        """
        Returns a new column element within which an entire row of the GUI is contained
        """
        self.column_elements.append(sg.Col([[self.delete_element(index),
                                             self.title_element(index),
                                             # copied from sg.pin. If sg.pin (and alternating background)
                                             # is used a visual anomaly occurs, so instead
                                             # i copied part of sg.pin, which allows the background color to be set.
                                             sg.Col([[self.time_till_release_element(index), sg.Col([[]], pad=(0, 0))]],
                                                    background_color=self.get_background_color_to_use(index),
                                                    pad=(0, 0)),
                                             self.ep_minus_element(index),
                                             self.ep_plus_element(index),
                                             self.season_minus_element(index),
                                             self.season_plus_element(index),
                                             self.link_element(index),
                                             self.properties_element(index),
                                             self.index_element(index),
                                             self.release_element(index)]],
                                           key=f"column:{index}",
                                           background_color=self.get_background_color_to_use(index),
                                           expand_x=True))
        return self.column_elements[-1]

    @staticmethod
    def get_background_color_to_use(index) -> str:
        """
        Figures out what the background color of a row should be and returns it.
        """
        if settings.enable_secondary_show_background and index % 2 == 1:
            return settings.secondary_show_background
        return sg.theme_background_color()

    def set_cursors(self, index):
        """
        Sets the proper cursors across one row of the GUI
        """
        self.delete_elements[index].set_cursor("plus")
        self.title_elements[index].set_cursor("plus")
        relevant = self.get_show_from_visual_index(index).ep_season_relevant

        self.ep_minus_elements[index].set_cursor("@down.cur" if relevant else "arrow")
        self.ep_plus_elements[index].set_cursor("@up.cur" if relevant else "arrow")
        self.season_minus_elements[index].set_cursor("@down.cur" if relevant else "arrow")
        self.season_plus_elements[index].set_cursor("@up.cur" if relevant else "arrow")
        self.properties_elements[index].set_cursor("plus")
        self.link_elements[index].set_cursor("hand2")

    def shorten_by_x_rows(self, x):
        """
        Hides x number of rows from the GUI
        """
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
        """
        Changes the visibility of a given row
        """
        self.win[f"column:{index}"].update(visible=visibility)
        self.shows_col_contents_changed = True

    def extend_by_x_rows(self, x):
        """
        Extends the usable rows in the GUI by x
        """
        for _ in range(x):
            self.extend_by_one_row()

    def extend_by_one_row(self):
        """
        Extends the number of usable rows in the GUI by one. If there are hidden rows, these are unhidden first.
        """
        index = self.number_of_displayed_shows
        if self.number_of_invisible_rows > 0:
            self.change_visibility_of_row(index, True)
            self.number_of_invisible_rows -= 1
        else:
            self.win.extend_layout(self.shows_col, [[self.column_element(index)]])

        self.shows_col_contents_changed = True  # This causes self.shows_col.contents_changed() to be called
        # immediately after self.win.read(). Why this needs to be the case, I cannot fathom. (BUT IT WORKS!)
        self.number_of_displayed_shows += 1


if __name__ == '__main__':
    # Setting a default theme is exlusively used on the first system startup.
    # All settings should otherwise be defined in the settings savefile.
    sg.theme("DarkBrown4")

    settings = Settings(sg)
    shows = ShowsFileHandler(settings)

    should_restart = True
    while should_restart:
        should_restart = False

        MainWin(main_loop=True)

    settings.save()
    shows.save()