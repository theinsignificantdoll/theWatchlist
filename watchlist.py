import PySimpleGUI as sg
import mouse
import time
import csv
import os
import webbrowser

sg.theme("DarkBrown4")

savefile = "saved.csv"
settingsfile = "settings.csv"
delimiter = "\\"
initialwinsize = (400, 200)
initialwinpos = (50, 50)
right_click_fontsize = 10
right_click_selected_background = "#252525"
showall = False

# DEFAULT SETTINGS
fontsize = 15
search_results = 3
fonttype = "Helvetica"
txtcolor = [sg.theme_text_color(), "#404040"]
sg.theme_slider_color(sg.theme_background_color())
buttoncolor = txtcolor[0]
showamount = 32
max_title_display_len = 0  # max number of characters displayed in a title. Modified by settings.csv. Infinite if 0


class Show:
    def __init__(self, id, title, ep, season, link, weight, color):
        self.id = id
        self.title = title
        self.ep = ep
        self.season = season
        self.link = link
        self.weight = weight
        self.color = color

    def __repr__(self):
        return f"Show(id={self.id.__repr__()}, title={self.title.__repr__()}, ep={self.ep.__repr__()}," \
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


if not os.path.isfile(savefile):
    with open(savefile, "w") as f:
        pass

if not os.path.isfile(settingsfile):
    with open(settingsfile, "w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow([fontsize, fonttype, "-".join(txtcolor), buttoncolor, sg.theme_background_color(),
                         right_click_selected_background, right_click_fontsize])
        writer.writerow([*initialwinsize, *initialwinpos])
        writer.writerow([search_results])


def maxgreycolor():
    global shows
    global txtcolor
    for s in shows:
        if int(s.color) >= len(txtcolor):
            s.color = str(len(txtcolor)-1)


def isvalidcolor(col):
    if len(col) == 7:
        if col[0] == "#":
            for n in col[1:]:
                if (48 <= ord(n) <= 57) or (65 <= ord(n) <= 70) or (97 <= ord(n) <= 102):
                    return True
                return False
    return False


def writesettings():
    global initialwinsize
    global initialwinpos
    if loadsettings(do_return=True) == [fontsize, fonttype, txtcolor, buttoncolor, initialwinsize, initialwinpos,
                                        search_results, sg.theme_background_color(), right_click_selected_background,
                                        right_click_fontsize, showamount, max_title_display_len,
                                        sg.theme_input_background_color()]:
        return
    with open(settingsfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar="|")
        writer.writerow([fontsize, fonttype, "-".join(txtcolor), buttoncolor, sg.theme_background_color(),
                         right_click_selected_background, right_click_fontsize, sg.theme_input_background_color()])
        writer.writerow([*initialwinsize, *initialwinpos])
        writer.writerow([search_results])
        writer.writerow([showamount, max_title_display_len])


def loadsettings(do_return=False):
    global fontsize
    global fonttype
    global txtcolor
    global greyedcolor
    global buttoncolor
    global initialwinpos
    global initialwinsize
    global right_click_selected_background
    global right_click_fontsize
    global search_results
    global showamount
    global max_title_display_len
    with open(settingsfile, "r", newline="") as csvfile:
        # Values read from file and stored in temp variables. Hence the prefix "t"
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar="|")
        row = reader.__next__()
        tfontsize = row[0]
        tfonttype = row[1]
        ttxtcolor = row[2].split("-")
        tbuttoncolor = row[3]
        tbackground_color = row[4]
        tright_click_selected_background = row[5]
        tright_click_fontsize = row[6]
        tinput_background = row[7]

        windata = reader.__next__()
        tinitialwinsize = (windata[0], windata[1])
        tinitialwinpos = (windata[2], windata[3])

        searchdata = reader.__next__()
        tsearch_results = int(searchdata[0])

        displaydata = reader.__next__()
        tshow_amount = int(displaydata[0])
        tmax_title_len = int(displaydata[1])

    if not do_return:
        fontsize = tfontsize
        fonttype = tfonttype
        txtcolor = ttxtcolor
        buttoncolor = tbuttoncolor
        sg.theme_background_color(tbackground_color)
        sg.theme_input_background_color(tinput_background)
        right_click_selected_background = tright_click_selected_background
        right_click_fontsize = tright_click_fontsize
        initialwinsize = tinitialwinsize
        initialwinpos = tinitialwinpos
        search_results = tsearch_results
        showamount = tshow_amount
        max_title_display_len = tmax_title_len
        return

    return [tfontsize, tfonttype, ttxtcolor, tbuttoncolor,
            (int(tinitialwinsize[0]), int(tinitialwinsize[1])), (int(tinitialwinpos[0]), int(tinitialwinpos[1])),
            tsearch_results, tbackground_color, tright_click_selected_background, tright_click_fontsize, tshow_amount,
            tmax_title_len, tinput_background]


loadsettings()


def sortshowsbyord(lst: list):
    def get_ord(show):
        try:
            return ord(show.title[0])
        except IndexError:
            return 0

    lst.sort(key=get_ord, reverse=True)
    return lst


def sortshows(lst):
    dct = {}
    for n in lst:
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
        lt += sortshowsbyord(dct[str(n)])
    lt.reverse()
    return lt


def gethighestid(lst):
    if len(lst) == 0:
        return -1
    return max([int(l.id) for l in lst])


def findfromid(id, lst):
    for n in lst:
        if n.id == id:
            return n


def stringify(lst):
    for i, item in enumerate(lst):
        lst[i] = str(item)
    return lst


def limit_string_len(string: str, length: int):
    if len(string) > length != 0:
        return string[:length]
    return string


def min_string_len(string: str, length: int):
    if len(string) > length:
        return string
    return f"{' ' * (length - len(string))}{string}"


def readsavefile(svfile=savefile, deli=delimiter):
    tempshows = []
    with open(svfile, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=deli, quotechar="|")
        for row in reader:
            tempshows.append(Show(
                id=row[0],
                title=row[1],
                ep=row[2],
                season=row[3],
                link=row[4],
                weight=row[5],
                color=row[6],
            ))
    return tempshows


def writesavefile(tshows, svfile=savefile, deli=delimiter):
    print("saving")
    if tshows == readsavefile():
        return
    with open(svfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=deli, quotechar="|")
        for show in tshows:
            writer.writerow([show.id, show.title, show.ep, show.season, show.link, show.weight, show.color])


def showprop(poptitle="Show Editor", popshowname="", popep="0", popseas="1", poplink="", popweight="0"):
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
                        font=(fonttype, int(fontsize))).read(close=True)

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


def butt(button_text="", key=None, tooltip=None, button_color=(False, None), border_width=None, size=(None, None),
         mouseover_colors=sg.theme_background_color(), disabled=False, right_click_menu=None):
    if not button_color[0]:
        button_color = (buttoncolor, button_color[1])
    return sg.Button(button_text=button_text, key=key, tooltip=tooltip, button_color=button_color,
                     border_width=border_width, size=size, mouseover_colors=mouseover_colors, disabled=disabled,
                     right_click_menu=right_click_menu)


shows = readsavefile()
shouldrestart = True


def open_link_from_show(show):
    webbrowser.open(show.link)


class openwin:
    def __init__(self):
        global shouldrestart
        global initialwinsize
        global initialwinpos
        global showall
        global showamount

        self.shouldbreak = False

        sg.theme_text_color(txtcolor[0])
        sg.theme_element_text_color(buttoncolor)
        sg.theme_element_background_color(sg.theme_background_color())
        sg.theme_text_element_background_color(sg.theme_background_color())
        sg.theme_button_color((buttoncolor, sg.theme_background_color()))

        delcolumn = []
        titcolumn = []
        emincolumn = []
        ecolumn = []
        scolumn = []
        linkcolumn = []
        propcolumn = []

        max_txt_color_index = len(txtcolor)-1

        for show in shows if showall else shows[:min(len(shows), showamount)]:  # uses the raw shows list if showall is
            #  True, otherwise shortening it to the -showamount- index.
            show.stringify()
            color = txtcolor[min(int(show.color), max_txt_color_index)]

            delcolumn.append([butt("DEL", key=f"delete:{show.id}", mouseover_colors="#AA0000",
                                   border_width=0)])
            titcolumn.append([sg.Text(limit_string_len(show.title, max_title_display_len), key=f"title:{show.id}",
                                      enable_events=True, text_color=f"{color}",
                                      right_click_menu=["",
                                                        [f"{m}::tit_color-{show.id}" for m in txtcolor]])])
            emincolumn.append([sg.Text(f"Ep:", key=f"Eminus{show.id}", enable_events=True,
                                       text_color=f"{color}")])
            ecolumn.append([sg.Text(f"{show.ep}", key=f"Eplus{show.id}", enable_events=True, size=(4, 1),
                                    text_color=f"{color}")])
            scolumn.append([sg.Text(f"S{show.season}", size=(4, 1), key=f"season:{show.id}",
                                    text_color=f"{color}", enable_events=True)])
            linkcolumn.append([butt("LINK", key=f"gotolink:{show.id}", tooltip=show.link, border_width=0,
                                    right_click_menu=["", [f"Open all links with the same color::multi_links-{show.id}"]])])
            propcolumn.append([butt("*", key=f"properties{show.id}", border_width=0)])

        showscol = [[sg.Col([[delcolumn[ind][0], titcolumn[ind][0]] for ind in range(len(titcolumn))]),
                     sg.Col([[emincolumn[ind][0], ecolumn[ind][0], scolumn[ind][0], linkcolumn[ind][0], propcolumn[ind][0]] for ind in range(len(titcolumn))])]]

        topcol = [[butt(" + ", key="AddShow", border_width=0, tooltip="Add a show to the list"),
                   butt(" * ", key="preferences", border_width=0, tooltip="Preferences"),
                   butt(" ^ ", key="toggleshowall", border_width=0, tooltip="Toggle showAll"),
                   butt(" ? ", key="searchbutton", border_width=0, tooltip="Search")]]

        layout = [
                  [sg.Col(topcol)],
                  [sg.Column(showscol, vertical_scroll_only=True, scrollable=True, expand_x=True, expand_y=True)],
                 ]

        win = sg.Window(title="Watchlist", layout=layout, auto_size_text=True, auto_size_buttons=True, resizable=True,
                        size=initialwinsize, font=(fonttype, int(fontsize)),  border_depth=0, finalize=True,
                        location=initialwinpos, titlebar_background_color=sg.theme_background_color(), margins=(0, 0),
                        element_padding=(3, 1), use_custom_titlebar=False,
                        titlebar_text_color=txtcolor[0], return_keyboard_events=True,
                        right_click_menu_font=(fonttype, right_click_fontsize),
                        right_click_menu_background_color=sg.theme_background_color(),
                        right_click_menu_text_color=buttoncolor,
                        right_click_menu_selected_colors=(buttoncolor, right_click_selected_background),
                        icon="GenIko.ico")

        for e in linkcolumn:
            e[0].set_cursor("hand2")
        for e in ecolumn:
            e[0].set_cursor("plus")
        for e in emincolumn:
            e[0].set_cursor("plus")
        for e in titcolumn:
            e[0].set_cursor("plus")
        for e in delcolumn:
            e[0].set_cursor("plus")
        for e in propcolumn:
            e[0].set_cursor("plus")

        win["AddShow"].block_focus()
        win["AddShow"].set_cursor("plus")
        win["preferences"].block_focus()
        win["preferences"].set_cursor("plus")

        self.win = win

        while not self.shouldbreak:
            initialwinpos = win.CurrentLocation()
            initialwinsize = win.Size
            event, values = win.read(timeout=200)

            #if event != "__TIMEOUT__":
            #    print(event)

            if event == "__TIMEOUT__":
                continue
            elif event == sg.WIN_CLOSED or self.shouldbreak or event == "Close":
                self.close()
                break

            elif event[:9] == "gotolink:" and len(event) > 9:
                print(event)
                s_id = event[9:]
                for ind, n in enumerate(shows):
                    if n.id == s_id:
                        open_link_from_show(n)
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
                writesavefile(shows)
                shouldrestart = True
                win.close()
                break

            elif event[:5] == "Eplus":
                for s in shows:
                    if s.id == event[5:]:
                        s.ep = str(int(s.ep) + 1)
                        writesavefile(shows)
                        win[event](value=s.ep)
                        break
            elif event[:6] == "Eminus":
                for s in shows:
                    if s.id == event[6:]:
                        s.ep = str(int(s.ep) - 1)
                        writesavefile(shows)
                        win["Eplus" + event[6:]](value=s.ep)
                        break

            elif event[:6] == "title:":
                tID = event[6:]
                for ind, n in enumerate(shows):
                    if n.id == tID:
                        shows[ind].color = str(int(shows[ind].color)+1)
                        if int(shows[ind].color) >= len(txtcolor):
                            shows[ind].color = 0
                        win[event].update(text_color=txtcolor[int(n.color)])
                        win[f"Eplus{tID}"].update(text_color=txtcolor[int(n.color)])
                        win[f"Eminus{tID}"].update(text_color=txtcolor[int(n.color)])
                        win[f"season:{tID}"].update(text_color=txtcolor[int(n.color)])
                        break

                writesavefile(shows)
            elif event[:7] == "season:":
                for s in shows:
                    if s.id == event[7:]:
                        first_mouse = mouse.get_position()[1]
                        time.sleep(0.050)
                        second_mouse = mouse.get_position()[1]
                        print(s.season)
                        if first_mouse < second_mouse:
                            s.season = str(int(s.season) - 1)  # Increase season counter
                        elif first_mouse > second_mouse:
                            s.season = str(int(s.season) + 1)  # Decrease season counter
                        print(s.season)
                        writesavefile(shows)
                        win["season:" + event[7:]](value=f"S{s.season}")
                        break

            elif event[:10] == "properties":
                show = findfromid(event[10:], shows)
                data = showprop(popshowname=show.title, popep=show.ep, popseas=show.season, poplink=show.link, popweight=show.weight)
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

            elif event == "h":  # Move win to mouse
                mouse_pos = mouse.get_position()
                win.move(*mouse_pos)

            elif event == "preferences":
                self.updatepreferences()

            elif event == "toggleshowall":
                self.toggleshowall()

            elif event == "searchbutton":
                self.search(results=search_results)

            elif event == "AddShow":
                data = showprop()
                if data == 1:
                    continue
                shows.append(Show(str(gethighestid(shows)+1), data["popshowname"], data["popep"],
                              data["popseas"], data["poplink"], data["popweight"], "0"))
                self.restart()
                break

            elif "::multi_links-" in event:
                for ind in range(0, -len(event), -1):
                    if event[ind] == "-":
                        id = event[ind+1:]
                        break

                ref_show = findfromid(id, shows)
                print(ref_show)

                for show in shows:
                    if ref_show.color == show.color:
                        open_link_from_show(show)

            elif "::tit_color-" in event:
                for ind, s in enumerate(event):
                    if s == ":":
                        col = event[:ind]
                        break
                for ind in range(0, -len(event), -1):
                    if event[ind] == "-":
                        id = event[ind+1:]
                        break
                col_index = txtcolor.index(col)
                show = findfromid(id, shows)
                show.color = col_index
                win[f"title:{id}"].update(text_color=txtcolor[col_index])
                win[f"Eminus{id}"].update(text_color=txtcolor[col_index])
                win[f"Eplus{id}"].update(text_color=txtcolor[col_index])
                win[f"season:{id}"].update(text_color=txtcolor[col_index])

    def close(self):
        global initialwinsize
        global initialwinpos
        writesavefile(shows)
        writesettings()
        self.shouldbreak = True
        self.win.close()

    def restart(self):
        global shouldrestart
        shouldrestart = True
        self.close()

    def toggleshowall(self):
        global showall
        showall = not showall
        self.restart()

    def search(self, results=3):
        delcol = [butt("DEL", key=f"s_delete_{n}", mouseover_colors="#AA0000", border_width=0) for n in range(results)]

        titcol = [sg.Text(shows[n].title, key=f"s_title_{n}", enable_events=True,
                          text_color=txtcolor[min(int(shows[n].color), len(txtcolor)-1)],
                          size=(37, 1)) for n in range(results)]

        index_col = [sg.Text(f"   {n+1}", key=f"s_index_{n}",
                             text_color=txtcolor[min(int(shows[n].color), len(txtcolor)-1)]) for n in range(results)]

        propcol = [butt("*", key=f"s_properties_{n}", border_width=0) for n in range(results)]

        rescol = [[delcol[n], titcol[n], index_col[n], propcol[n]] for n in range(results)]

        layout = [[sg.T("Search:"), sg.In(key="search", enable_events=True, size=(40, 1))],
                  [sg.Col(rescol)]]

        swin = sg.Window("Search", layout=layout, finalize=True, font=(fonttype, int(fontsize)))

        found = [""]*results

        while True:
            e, v = swin.read()
            if e == sg.WIN_CLOSED:
                break
            elif e == "search":
                found_indices = [-1]*results
                found = [""]*results
                search_query = v["search"].lower()
                for show_index, s in enumerate(shows):
                    if search_query in s.title.lower():
                        for ind, n in enumerate(found):
                            if n == "":
                                found[ind] = s
                                found_indices[ind] = show_index
                                break
                try:
                    for n in range(results):
                        swin[f"s_title_{n}"].update(" ")
                        swin[f"s_index_{n}"].update("    ")
                    for n in range(results):
                        swin[f"s_title_{n}"].update(found[n].title)
                        swin[f"s_index_{n}"].update(min_string_len(str(found_indices[n] + 1), 4))
                        swin[f"s_title_{n}"].update(text_color=txtcolor[min(int(found[n].color), len(txtcolor) - 1)])
                        swin[f"s_index_{n}"].update(text_color=txtcolor[min(int(found[n].color), len(txtcolor) - 1)])

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
                writesavefile(shows)
                swin.close()
                self.restart()
                return

            elif e[:12] == "s_properties":
                k = int(e[-1])

                show = findfromid(found[k].id, shows)
                data = showprop(popshowname=show[1], popep=show.ep, popseas=show.season, poplink=show.link, popweight=show.weight)
                if data == 1:
                    continue

                for ind, tshow in enumerate(shows):
                    if tshow.id == show.id:
                        shows[ind].title = data["popshowname"]
                        shows[ind].ep = data["popep"]
                        shows[ind].season = data["popseas"]
                        shows[ind].link = data["poplink"]
                        shows[ind].weight = data["popweight"]
                        swin.close()
                        self.restart()
                        return

    def updatepreferences(self):
        global fontsize
        global fonttype
        global txtcolor
        global buttoncolor
        global search_results
        global right_click_selected_background
        global right_click_fontsize
        global max_title_display_len
        global showamount
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
        col2 = [[sg.In(fontsize, key="fsize", tooltip="Any integer")],
                [sg.In(fonttype, key="ftype", tooltip="Any font name, as one might use in word or libreOffice Writer")],
                [sg.In("-".join(txtcolor), key="txtcolor", tooltip="Ex: '#ff0000-#404040' or '#ff0000-#404040-#878787'")],
                [sg.In(sg.theme_background_color(), k="bg_color", tooltip="The background color")],
                [sg.In(right_click_selected_background, k="menu_bg_color", tooltip="The background color of the right click menu")],
                [sg.In(right_click_fontsize, k="menu_font_size", tooltip="The font size of the right click menu")],
                [sg.In(buttoncolor, key="buttoncolor", tooltip="A single color, Ex: '#e0e0e0'")],
                [sg.In(search_results, key="sresults", tooltip="The number of results shown when searching. Default:3")],
                [sg.In(max_title_display_len, key="title_length", tooltip="The amount of characters that should be displayed\nin titles. 0 to display all characters")],
                [sg.In(showamount, key="showamount", tooltip="For performance reasons not all shows are displayed by default. This is the amount of shows on display.\nCan be toggled by the '^' button")]]
        col3 = [[sg.T("Field Background Color:")],
                ]
        col4 = [[sg.In(sg.theme_input_background_color(), k="field_bg_color", tooltip="The background color of the input fields")],
                ]
        twin = sg.Window("Preferences", layout=[
            [sg.Col(col1),
             sg.Col(col2),
             sg.Col(col3, expand_y=True, element_justification="n"),
             sg.Col(col4, expand_y=True, element_justification="n")],
            [sg.Button("Save")]], default_element_size=(16, 1), font=(fonttype, fontsize))

        while True:
            e, v = twin.read()
            if e == sg.WIN_CLOSED:
                break
            elif e == "Save":
                try:
                    int(twin["fsize"].get())
                    if not isvalidcolor(twin["buttoncolor"].get()):
                        raise ValueError

                    if not isvalidcolor(twin["menu_bg_color"].get()):
                        raise ValueError

                    if not isvalidcolor(twin["bg_color"].get()):
                        raise ValueError

                    if not isvalidcolor(twin["field_bg_color"].get()):
                        raise ValueError

                    gotcolors = twin["txtcolor"].get().split("-")
                    if len(gotcolors) <= 0:
                        raise ValueError
                    for col in gotcolors:
                        if not isvalidcolor(col):
                            raise ValueError

                except ValueError:
                    sg.popup_error("Unreadable value")
                    continue
                twin.close()
                fontsize = twin["fsize"].get()
                fonttype = twin["ftype"].get()
                txtcolor = twin["txtcolor"].get().split("-")
                sg.theme_background_color(twin["bg_color"].get())
                sg.theme_input_background_color(twin["field_bg_color"].get())
                right_click_selected_background = twin["menu_bg_color"].get()
                right_click_fontsize = int(twin["menu_font_size"].get())
                maxgreycolor()
                buttoncolor = twin["buttoncolor"].get()
                search_results = int(twin["sresults"].get())
                max_title_display_len = int(twin["title_length"].get())
                showamount = int(twin["showamount"].get())

                writesettings()
                self.restart()
                break


while shouldrestart:
    shouldrestart = False
    shows = sortshows(shows)
    openwin()

