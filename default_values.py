# This file contains the default settings used by the program. Thus, changes can easily be made here.
# Note however, that settings under the "Settings defaults" will not come into effect if settings_file exists

settings_file = "settings.csv"
show_file = "saved.csv"
csv_delimiter = "\\"


###############################################################################
#  v v v v v v v v v v
# Settings defaults V
# v v v v v v v v v v

fontsize = 15
fonttype = "Noto Mono"
text_colors = None
# text_colors = ["#DD2222", "#303030"]
button_color = None
# button_color = "#FFFFFF"
background_color = None
# background_color = "#252525"
right_click_selected_background = "#1a5fc6"
right_click_fontsize = 10
input_background = None
# input_background = "#860213"
initialwinsize = (960, 540)
initialwinpos = (50, 50)
search_results = 7
show_amount = 32
max_title_display_len = 44
indices_visible = False
show_all = True
shorten_with_ellipsis = True
releases_visible = True
release_grace_period = 72
default_text_color = None
# default_text_color = "#f3f3f3"
default_fontsize = 11
move_recently_released_to_top = True
weight_to_add = 5
sort_by_upcoming = False
secondary_show_background = "#202020"
enable_secondary_show_background = False
send_notifications = False
show_till_release = True
display_hidden = False
purge_color_index = -1  # If purge color index is -1, then no colors will be changed
initial_show_color_index = 0
remaining_time_prioritise_precision = False


#######################################################################################
#
#  Settings not important enough to have in GUI.
#

# The number of seconds in between a change being made to a show and the change being saved. Accepts floats
delay_to_save_shows = 3
# The maximum amount of seconds inbetween checking the release state of shows.
update_release_vals_interval = 30
# The mark next to shows that are recently released.
# Copy us: ✓ 📅 ★ ✰ ⚝ ⭐ ✨
recently_released_string = "✨"
