import PySimpleGUI as sg
import csv
import os

sg.theme("DarkBrown4")

savefile = "saved.csv"
delimiter = "\\"
fontsize = 15
fonttype = "Helvetica"
settingsfile = "settings.csv"


if not os.path.isfile(savefile):
    with open(savefile, "w") as f:
        pass

if not os.path.isfile(settingsfile):
    with open(settingsfile, "w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow([10, "Comic Sans"])


def writesettings():
    with open(settingsfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar="|")
        writer.writerow([fontsize, fonttype])


def loadsettings():
    global fontsize
    global fonttype
    with open(settingsfile, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar="|")
        for row in reader:
            fontsize = row[0]
            fonttype = row[1]


loadsettings()


def sortshows(lst):
    dct = {}
    for n in lst:
        if n[-1] in dct:
            dct[n[-1]].append(n)
            continue
        dct[n[-1]] = [n]
    lt = []
    for n in dct:
        lt += dct[n]
    lt.reverse()
    return lt


def gethighestid(lst):
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
    with open(svfile, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=deli, quotechar="|")
        for row in reader:
            tempshows.append([])          # ALL data is stored as strings, some merely represent other datatypes
            tempshows[-1].append(row[0])  # int    ; ID
            tempshows[-1].append(row[1])  # string ; Name
            tempshows[-1].append(row[2])  # int    ; Episode
            tempshows[-1].append(row[3])  # int    ; Season
            tempshows[-1].append(row[4])  # string ; Link to homepage
            tempshows[-1].append(row[5])  # int    ; Sorting Weight
    return tempshows


def writesavefile(tshows, svfile=savefile, deli=delimiter):
    with open(svfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=deli, quotechar="|")
        for show in tshows:
            writer.writerow([str(data) for data in show])


def showprop(poptitle="Show Editor", popshowname="", popep="1", popseas="1", poplink="", popweight="0"):
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
                         [sg.Button("Save"), sg.Button("Cancel")]],
                        disable_close=True,
                        auto_size_buttons=True,
                        auto_size_text=True,
                        default_element_size=(12, 1)).read(close=True)

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


def butt(button_text="", key=None, tooltip=None, button_color=None, border_width=None, size=(None, None),
         mouseover_colors=sg.theme_background_color(), disabled=False):
    return sg.Button(button_text=button_text, key=key, tooltip=tooltip, button_color=button_color,
                     border_width=border_width, size=size, mouseover_colors=mouseover_colors)


shows = readsavefile()
shouldrestart = True


class openwin:
    def __init__(self):
        global shouldrestart

        self.shouldbreak = False

        delcolumn = []
        titcolumn = []
        emincolumn = []
        ecolumn = []
        scolumn = []
        linkcolumn = []
        propcolumn = []
        for show in shows:
            tshow = stringify(show)
            delcolumn.append([butt("DEL", key=f"delete:{tshow[0]}", button_color="#AA0000", mouseover_colors="#AA0000", border_width=0)])
            titcolumn.append([sg.Text(tshow[1])])
            emincolumn.append([sg.Text(f"Ep:", key=f"Eminus{tshow[0]}", enable_events=True)])
            ecolumn.append([sg.Text(f"{tshow[2]}", key=f"Eplus{tshow[0]}", enable_events=True, size=(4, 1))])
            scolumn.append([sg.Text(f"S{tshow[3]}", size=(4, 1))])
            linkcolumn.append([butt("LINK", key=f"gotolink:{tshow[4]}", tooltip=tshow[4], border_width=0)])
            propcolumn.append([butt("*", key=f"properties{tshow[0]}", border_width=0)])
        showscol = [[sg.Col([[delcolumn[ind][0], titcolumn[ind][0]] for ind in range(len(titcolumn))]),
                     sg.Col([[emincolumn[ind][0], ecolumn[ind][0], scolumn[ind][0], linkcolumn[ind][0], propcolumn[ind][0]] for ind in range(len(titcolumn))])]]

        layout = [
                  [sg.Text("Watchlist"), butt(" + ", key="AddShow", border_width=0),
                   butt(" * ", key="preferences", border_width=0)],
                  [sg.Column(showscol, vertical_scroll_only=True, scrollable=True, expand_x=True, expand_y=True)],
                 ]

        win = sg.Window(title="Watchlist", layout=layout, auto_size_text=True, auto_size_buttons=True, resizable=True,
                        size=(800, 400), font=(fonttype, int(fontsize)),  border_depth=5, finalize=True)

        win["AddShow"].block_focus()
        win["preferences"].block_focus()

        self.win = win

        while True:
            event, values = win.read()

            if event == sg.WIN_CLOSED or self.shouldbreak:
                break

            elif event[:9] == "gotolink:" and len(event) > 9:
                os.system(f"start {event[9:]}")

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
                        writesavefile(shows)
                        shouldrestart = True
                        win.close()
                        return

            elif event == "preferences":
                self.updatepreferences()

            elif event == "AddShow":
                data = showprop()
                if data == 1:
                    continue
                shows.append([gethighestid(shows)+1, data["popshowname"], data["popep"], data["popseas"], data["poplink"], data["popweight"]])
                writesavefile(shows)
                shouldrestart = True
                win.close()
                break

    def restart(self):
        global shouldrestart
        writesavefile(shows)
        shouldrestart = True
        self.shouldbreak = True
        self.win.close()

    def updatepreferences(self):
        global fontsize
        global fonttype
        col1 = [[sg.T("Font size:")],
                [sg.T("Font type:")]]
        col2 = [[sg.In(fontsize, key="fsize")],
                [sg.In(fonttype, key="ftype")]]
        twin = sg.Window("Preferences", layout=[
            [sg.Col(col1), sg.Col(col2)],
            [sg.Button("Save")]], default_element_size=(8, 1))

        while True:
            e, v = twin.read()
            if e == sg.WIN_CLOSED:
                break
            elif e == "Save":
                try:
                    int(twin["fsize"].get())
                except ValueError:
                    sg.popup_error("Couldn't convert a value to int")
                    continue
                twin.close()
                fontsize = twin["fsize"].get()
                fonttype = twin["ftype"].get()
                writesettings()
                self.restart()
                break


while shouldrestart:
    shouldrestart = False
    shows = sortshows(shows)
    openwin()

