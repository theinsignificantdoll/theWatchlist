introduction =\
    """INTRODUCTION
This program is intended to alleviate some of the pains that one might encounter when
watching shows in more than one place. And so, instead of remembering to check a bunch
of websites each day, you can just write down all the shows in this program.

To get started press the "+" button in the top left of the main window. This button
will open another window, wherein information about the show can be entered.
Some of these are self-explanatory - but not all of them.

One of these outliers is the weight of a show. This value is used for
sorting the shows. The shows with the heighest weight, and therefore the
most important, are displayed at the top. Note that weights can be negative."""

important =\
    """IMPORTANT
Before really using this program, there are some things that you shold know.

First of all, by clicking on the title of a show, you can change its color.

Second of all, the episode and season counter can be adjusted simply by clicking
on the counter itself. It will go up and down depending on where you click it.

Third of all, in the top-left corner there is an arrow button. This button is one of those
"Show more/less" buttons. This button exists for the sake of performance.
When displaying hundreds of shows, the program can become slow (I mean, that is a lot of
stuff to display, right?). How many shows are being displayed in show-less-mode is
configurable in the settings.
"""

settings_i =\
    """SETTINGS I
The first two settings are simple. Font size is the size of the font.
Font type is just a simple, simply write the name of a font, just like you'd find it
in Word or LibreOffice Writer!

The next one is a bit more complicated. "Text color" covers all the colors that shows can be
it also covers the default cover of text in other windows. This setting is a list of
hex color codes, seperated by "-". If you have a hard time finding hex color codes, you can
use a color picker. Just a remember to seperate all codes by "-"!

Next is the background color. To pick a new one, just press "Background Color".
You can pick the menu background color in much the same way, but what it does is a bit different.
It changes the background color of the right-click menu (Try right-clicking "LINK" or
one of the titles).
Menu font size is simply the size of the font in the right click menu.

Button color is the color of the text on buttons.
"""

settings_ii =\
    """SETTINGS II
Search results is how many results should be displayed when searching (magnifying glass in the top-left)

Title length is the maximum amount of characters to be displayed in a title. This is useful,
if you'd like to avoid one really long title pushing all the other things away! Other than that,
if the value is negative, then the length of titles will not be altered. However, the size
of the fields that themselves display the titles will still be limited.

Show Cut-off is the number of shows, which will be displayed when "Show Less" is updated (see Important)

Field background color is the background color of the fields, wherin the user can write. (Like the
ones in the settings window)

Shorten with ellipsis will, if activated, make it so that the last three characters in a title
that has been shortened is "...".

Release Grace Period is a bit advanced. Moreover, it isn't needed quite yet, therefore it will
be covered in another tab.

Default text color is the text color used within subwindows like this one (Or settings itself)
In the same way, default font size is the font size used within subwindows.
"""

settings_iii =\
    """SETTINGS III
Search results is how many results should be displayed when searching (magnifying glass in the top-left)

Recent Releases To Top will, if enabled, change the weight of recent releases when sorting, so that
they can be made to appear at the top.
Recent Release Weight Add is how much weight should be added to recent releases. With this you can
adjust exactly -how- far up you want the shows to move, when it's just been released.
"""

show_editor =\
    """SHOW EDITOR
The show editor is opened when either adding a new show or editing an existing one. You can find it by
pressing the gear to the right of the "LINK" button.
It is only within the show editor that the weight of a show can be changed.

More important to explain is the function of the "Show Details" checkbox. If this checkbox is unchecked,
the program will not display the episode or season.
Moreover, "Purge Weight" might also require explanation. This field is intended to be used once a show
has been finished. That is to say, when it should be moved out of the way.

The field works like this: When a numerical value is entered into it, and the changes are saved
the weight of the show will be set to the value of the "Purge Weight" field. Other than that, it
will also clear the "Release Info" and uncheck the "Ongoing" checkbox.

In other words, in order to 'dismiss' a show, a low weight should be entered in the "Purge Field" field
and the rest will automatically happen.

Release Info and Ongoing is described in Release
"""

release =\
    """RELEASE
Manually checking whether or not a new episode has come out is a tedious task. Therefore, it is only
proper that the computer does it for you.

Firstly, the computer must learn when a new episode is released. In order for it to do this,
enter the Show Editor (The gear symbol left of "LINK"). Once there, press on the button beneath
"Release Info". This will open a window. In order to choose at weekday, simply press the
corresponding button. If you'd like set a time of day as well, simply type it in the two
input fields. Then, press save.
With that done, the "Ongoing" checkbox must also be checked. Once you've exited the Show Editor, you
should also make sure that the second checkbox in the top-left has been checked.
When the time of release is within some amount of hours, there will be a checkmark right of the Show Editor button.
To specify how many hours after release this checkmark should remain, enter settings and edit the value
in "Release Grace Period". The value is given in hours after release.
"""

search =\
    """SEARCH
To enter the searching window press the magnifying glass in the top-left.

Write your search query in the search bar and search! But, beware that the searching algorithm
is extraordinarily rudimentary. The search functions in such a way, that it merely checks whether
or not your search query is contained within the title of the show (ignoring case). Moreover,
the shows found after the search are displayed in their ordinary order.

Other than that, it is useful to know that the right most numbers are the indices of the shows. These indices
can also be displayed in the main window. This is done by checking the left most checkbox in the top-left
of the main window.

Note also that the number of search results can be adjusted. Simply open settings and change the value
of "Search Results".
"""

quick_menus =\
    """RIGHT CLICK MENUS
By right clicking on certain parts of the window you can quickly adjust certain things. An example of this,
is that by right clicking the title of a show, you can pick its color. That way, you don't have to cycle
through all of them!

Other than that, you can also open all the links of shows with the same color. This is done by simply right-clicking
the "LINK" button. Moreover, you can quickly adjust some settings by right clicking on the show editor button!

And, if you've set up releases, you can also dismiss shows. This way, you can temporarily remove the checkmark
(and added weight during sorting) from a show. Simply right click the checkmark and choose "Dismiss". The show
will no longer be registered as recently released in the "Release Grace Period" amount of hours!
"""