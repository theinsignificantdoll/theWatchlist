import PySimpleGUI as sg
import mouse
import time
import csv
import os
import webbrowser

sg.theme("DarkBrown4")

savefile = "saved.csv"
delimiter = "\\"
fontsize = 15
search_results = 3
fonttype = "Helvetica"
txtcolor = [sg.theme_text_color(), "#404040"]
buttoncolor = txtcolor[0]
settingsfile = "settings.csv"
initialwinsize = (400, 200)
initialwinpos = (50, 50)
right_click_fontsize = 10
right_click_selected_background = "#252525"

showall = False
showamount = 32


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
        if int(s[6]) >= len(txtcolor):
            s[6] = str(len(txtcolor)-1)


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
    if loadsettings(do_return=True) == [fontsize, fonttype, txtcolor, buttoncolor, initialwinsize, initialwinpos, search_results, sg.theme_background_color(), right_click_selected_background, right_click_fontsize]:
        return
    with open(settingsfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar="|")
        writer.writerow([fontsize, fonttype, "-".join(txtcolor), buttoncolor, sg.theme_background_color(),
                         right_click_selected_background, right_click_fontsize])
        writer.writerow([*initialwinsize, *initialwinpos])
        writer.writerow([search_results])


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
    with open(settingsfile, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar="|")
        row = reader.__next__()
        tfontsize = row[0]
        tfonttype = row[1]
        ttxtcolor = row[2].split("-")
        tbuttoncolor = row[3]
        tbackground_color = row[4]
        tright_click_selected_background = row[5]
        tright_click_fontsize = row[6]

        windata = reader.__next__()
        tinitialwinsize = (windata[0], windata[1])
        tinitialwinpos = (windata[2], windata[3])

        searchdata = reader.__next__()
        tsearch_results = int(searchdata[0])
    if not do_return:
        fontsize = tfontsize
        fonttype = tfonttype
        txtcolor = ttxtcolor
        buttoncolor = tbuttoncolor
        sg.theme_background_color(tbackground_color)
        right_click_selected_background = tright_click_selected_background
        right_click_fontsize = tright_click_fontsize
        initialwinsize = tinitialwinsize
        initialwinpos = tinitialwinpos
        search_results = tsearch_results
        return
    return [tfontsize, tfonttype, ttxtcolor, tbuttoncolor, (int(tinitialwinsize[0]), int(tinitialwinsize[1])), (int(tinitialwinpos[0]), int(tinitialwinpos[1])), tsearch_results, tbackground_color, tright_click_selected_background, tright_click_fontsize]


loadsettings()


def sortshowsbyord(lst: list):
    def get_ord(show):
        try:
            return ord(show[1][0])
        except IndexError:
            return 0

    lst.sort(key=get_ord, reverse=True)
    return lst


def sortshows(lst):
    dct = {}
    for n in lst:
        if n[5] in dct:
            dct[n[5]].append(n)
            continue
        dct[n[5]] = [n]
    lt = []
    slist = []  # list of Weights used
    for n in dct:
        slist.append(int(n))
        dct[n].sort()
    slist.sort()
    for n in slist:
        lt += sortshowsbyord(dct[str(n)])
    lt.reverse()
    return lt


def gethighestid(lst):
    if len(lst) == 0:
        return -1
    return max([int(l[0]) for l in lst])


def findfromid(id, lst):
    for n in lst:
        if n[0] == id:
            return n


def stringify(lst):
    for i, item in enumerate(lst):
        lst[i] = str(item)
    return lst


def readsavefile(svfile=savefile, deli=delimiter):
    tempshows = []
    with open(svfile, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=deli, quotechar="|")
        for row in reader:
            tempshows.append([])          # ALL data is stored as strings, some merely represent other datatypes
            tempshows[-1].append(row[0])  # int    ; ID
            tempshows[-1].append(row[1])  # string ; Name
            tempshows[-1].append(row[2])  # int    ; Episode
            tempshows[-1].append(row[3])  # int    ; Season
            tempshows[-1].append(row[4])  # string ; Link to homepage
            tempshows[-1].append(row[5])  # int    ; Sorting Weight
            tempshows[-1].append(row[6])  # bool   ; Color index to use
    return tempshows


def writesavefile(tshows, svfile=savefile, deli=delimiter):
    if tshows == readsavefile():
        return
    with open(svfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=deli, quotechar="|")
        for show in tshows:
            writer.writerow([str(data) for data in show])


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
            tshow = stringify(show)
            color = txtcolor[min(int(tshow[6]), max_txt_color_index)]

            delcolumn.append([butt("DEL", key=f"delete:{tshow[0]}", mouseover_colors="#AA0000",
                                   border_width=0)])
            titcolumn.append([sg.Text(tshow[1], key=f"title:{tshow[0]}", enable_events=True,
                                      text_color=f"{color}")])
            emincolumn.append([sg.Text(f"Ep:", key=f"Eminus{tshow[0]}", enable_events=True,
                                       text_color=f"{color}")])
            ecolumn.append([sg.Text(f"{tshow[2]}", key=f"Eplus{tshow[0]}", enable_events=True, size=(4, 1),
                                    text_color=f"{color}")])
            scolumn.append([sg.Text(f"S{tshow[3]}", size=(4, 1), key=f"season:{tshow[0]}",
                                    text_color=f"{color}", enable_events=True)])
            linkcolumn.append([butt("LINK", key=f"gotolink:{tshow[0]}", tooltip=tshow[4], border_width=0,
                                    right_click_menu=["", [f"Open links:{color}"]])])
            propcolumn.append([butt("*", key=f"properties{tshow[0]}", border_width=0)])

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
                        right_click_menu_selected_colors=(buttoncolor, right_click_selected_background))

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
                    if n[0] == s_id:
                        self.open_link(n)
                        break

            elif event[:7] == "delete:":
                delme = -1

                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                for ind, n in enumerate(shows):
                    if n[0] == event[7:]:
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
                    if s[0] == event[5:]:
                        s[2] = str(int(s[2]) + 1)
                        writesavefile(shows)
                        win[event](value=s[2])
                        break
            elif event[:6] == "Eminus":
                for s in shows:
                    if s[0] == event[6:]:
                        s[2] = str(int(s[2]) - 1)
                        writesavefile(shows)
                        win["Eplus" + event[6:]](value=s[2])
                        break

            elif event[:6] == "title:":
                tID = event[6:]
                for ind, n in enumerate(shows):
                    if n[0] == tID:
                        shows[ind][6] = str(int(shows[ind][6])+1)
                        if int(shows[ind][6]) >= len(txtcolor):
                            shows[ind][6] = 0
                        win[event].update(text_color=txtcolor[int(n[6])])
                        win[f"Eplus{tID}"].update(text_color=txtcolor[int(n[6])])
                        win[f"Eminus{tID}"].update(text_color=txtcolor[int(n[6])])
                        win[f"season:{tID}"].update(text_color=txtcolor[int(n[6])])
                        break

                writesavefile(shows)
            elif event[:7] == "season:":
                for s in shows:
                    if s[0] == event[7:]:
                        first_mouse = mouse.get_position()[1]
                        time.sleep(0.050)
                        second_mouse = mouse.get_position()[1]
                        print(s[3])
                        if first_mouse < second_mouse:
                            s[3] = str(int(s[3]) - 1)  # Increase season counter
                        elif first_mouse > second_mouse:
                            s[3] = str(int(s[3]) + 1)  # Decrease season counter
                        print(s[3])
                        writesavefile(shows)
                        win["season:" + event[7:]](value=f"S{s[3]}")
                        break

            elif event[:11] == "Open links:":
                color = event[11:]
                for show in shows:
                    show_color = txtcolor[min(int(show[6]), max_txt_color_index)]
                    if color == show_color:
                        self.open_link(show)

            elif event[:10] == "properties":
                show = findfromid(event[10:], shows)
                data = showprop(popshowname=show[1], popep=show[2], popseas=show[3], poplink=show[4], popweight=show[5])
                if data == 1:
                    continue
                for ind, tshow in enumerate(shows):
                    if tshow[0] == show[0]:
                        shows[ind][1] = data["popshowname"]
                        shows[ind][2] = data["popep"]
                        shows[ind][3] = data["popseas"]
                        shows[ind][4] = data["poplink"]
                        shows[ind][5] = data["popweight"]
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
                shows.append([str(gethighestid(shows)+1), data["popshowname"], data["popep"], data["popseas"], data["poplink"], data["popweight"], "0"])
                self.restart()
                break

    def open_link(self, show):
        webbrowser.open(show[4])

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

        titcol = [sg.Text(shows[n][1], key=f"s_title_{n}", enable_events=True, text_color=f"{txtcolor[0]}", size=(37, 1)) for n in range(results)]

        propcol = [butt("*", key=f"s_properties_{n}", border_width=0) for n in range(results)]

        rescol = [[delcol[n], titcol[n], propcol[n]] for n in range(results)]

        layout = [[sg.T("Search:"), sg.In(key="search", enable_events=True, size=(40, 1))],
                  [sg.Col(rescol)]]

        swin = sg.Window("Search", layout=layout, finalize=True, font=(fonttype, int(fontsize)))

        found = [""]*results

        while True:
            e, v = swin.read()
            if e == sg.WIN_CLOSED:
                break
            elif e == "search":
                found = [""]*results
                for s in shows:
                    if v["search"].lower() in s[1].lower():
                        for ind, n in enumerate(found):
                            if n == "":
                                found[ind] = s
                                break
                try:
                    for n in range(results):
                        swin[f"s_title_{n}"].update(" ")
                    for n in range(results):
                        swin[f"s_title_{n}"].update(found[n][1])
                except IndexError:
                    pass
            elif e[:8] == "s_delete":
                k = int(e[-1])

                if sg.popup_yes_no("Are you sure?") == "No":
                    continue

                delme = -1
                for ind, n in enumerate(shows):
                    if n[0] == found[k][0]:
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

                show = findfromid(found[k][0], shows)
                data = showprop(popshowname=show[1], popep=show[2], popseas=show[3], poplink=show[4], popweight=show[5])
                if data == 1:
                    continue

                for ind, tshow in enumerate(shows):
                    if tshow[0] == show[0]:
                        shows[ind][1] = data["popshowname"]
                        shows[ind][2] = data["popep"]
                        shows[ind][3] = data["popseas"]
                        shows[ind][4] = data["poplink"]
                        shows[ind][5] = data["popweight"]
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
        col1 = [[sg.T("Font size:")],
                [sg.T("Font type:")],
                [sg.T("Text color:")],
                [sg.T("Menu background color:")],
                [sg.T("Menu font size:")],
                [sg.T("Button Color")],
                [sg.T("Search Results")]]
        col2 = [[sg.In(fontsize, key="fsize", tooltip="Any integer")],
                [sg.In(fonttype, key="ftype", tooltip="Any font name, as one might use in word or libreOffice Writer")],
                [sg.In("-".join(txtcolor), key="txtcolor", tooltip="Ex: '#ff0000-#404040' or '#ff0000-#404040-#878787'")],
                [sg.In(right_click_selected_background, k="menu_bg_color", tooltip="The background color of the right click menu")],
                [sg.In(right_click_fontsize, k="menu_font_size", tooltip="The font size of the right click menu")],
                [sg.In(buttoncolor, key="buttoncolor", tooltip="A single color, Ex: '#e0e0e0'")],
                [sg.In(search_results, key="sresults", tooltip="The number of results shown when searching. Default:3")]]
        twin = sg.Window("Preferences", layout=[
            [sg.Col(col1), sg.Col(col2)],
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
                right_click_selected_background = twin["menu_bg_color"].get()
                right_click_fontsize = int(twin["menu_font_size"].get())
                maxgreycolor()
                buttoncolor = twin["buttoncolor"].get()
                search_results = int(twin["sresults"].get())

                writesettings()
                self.restart()
                break


while shouldrestart:
    shouldrestart = False
    shows = sortshows(shows)
    openwin()

