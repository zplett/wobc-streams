# WOBC stream recording script - Zac Plett 01/24/2019

# Python libraries
import urllib.request, json, time, os, datetime
from multiprocessing import Process

# Local libraries
from shows import show

def main():
    schedule = "https://radiant-ravine-50175.herokuapp.com/schedule?Period=2&Year=2019"
    json_schedule = load_json(schedule)
    show_dict = load_shows(json_schedule)
    first_show = find_first(show_dict)
    # MARK : Need to come up with a way to have a stop time for the recording process but for now
    # will have it run on a constant loop
    record_shows(show_dict, first_show)

# Loads the schedule information into Python's JSON class
def load_json(schedule):
    with urllib.request.urlopen(schedule) as url:
        data = json.loads(url.read().decode())

    return data

# Creates a dictionary with days of the week (numbers 1 - 7 representing Sun - Sat) as keys and a
# list of show objects as values
def load_shows(json_schedule):
    show_dict = {1 : [],
                 2 : [],
                 3 : [],
                 4 : [],
                 5 : [],
                 6 : [],
                 7 : []}

    for json_show in json_schedule:
        curr_show = show(json_show)
        show_dict[curr_show.day].append(curr_show)

    return show_dict

# Finds which show to start the recording process at
def find_first(show_dict):
    # The Python datetime module loads the days of the week as 0 - 6 representing Mon - Sun but the
    # current schema from WOBC sends JSON with shows where 1 - 7 represent Sun - Sat as mentioned
    # above so need to adjust that locally until that's changed.
    current_day = datetime.datetime.today().weekday() + 2
    if current_day > 7:
        current_day = current_day - 7
    current_shows = show_dict[current_day]
    # Similarly, the python datetime module stores hours of the day as 1 - 24, and the current
    # schema from WOBC sends JSON with hours stored as 100 - 2400 so adjusting that accordingly
    # below. 
    now = datetime.datetime.now().hour * 100
    for show in current_shows:
        if show.start > now:
            first = show
            break

    return first

# Show recording process makes use of the Python multiprocessing library so that we can call
# curl commands that record two shows with intersecting time intervals. We add 5 minutes of padding
# around the start and end time of each show to prevent any recording being cut off. 
def record_shows(show_dict, first_show):
    current_show = first_show
    next_show = find_next(show_dict, current_show)
    date = datetime.datetime.now()
    now = (date.hour * 100) + date.minute
    while now < current_show.start - 5:
        time.sleep(300)
    # Change to while find_next != null once find_next returns null on an empty day 
    while true:
        p1 = Process(target = record_current_show, args=(current_show,))
        p1.start()
        if current_show.time == 100:
            time.sleep(3300)
        else:
            time.sleep(6900)
        p2 = Process(target = record_next_show, args=(next_show,))
        p2.start()
        if next_show.time == 100:
            time.sleep(3300)
        else:
            time.sleep(6900)
        current_show = find_next(show_dict, next_show)
        next_show = find_next(show_dict, current_show)
        # Have this process conclude with uploading the shows to firebase 


# Finds the next show to play
def find_next(show_dict, current_show):
    index = show_dict[current_show.day].index(current_show)
    # If we aren't at the last show of the day, find the show following this one
    if index < len(show_dict[current_show.day]) - 1:
        next_show = show_dict[current_show.day][index + 1]
    # Otherwise, if we are at the end of the day and not the last day of the week, get the first
    # show the following day 
    elif current_show.day < 7:
        next_show = show_dict[current_show.day + 1][0]
    # Else, if we are at the end of the day and the last day of the week, reset with the first show
    # in the schedule. 
    else:
        next_show = show_dict[1][0]

    return next_show

# Process for recording the current show
def record_current_show(current_show):
    if current_show.time == 100:
        length = "4200"
    else:
        length = "7800"
    address = "http://132.162.36.191:8000/"
    title = current_show.title
    directory = "/Users/zacplett/desktop/work/stream_tests/streams"
    destination = directory + title + ".mp3"
    system_call = "curl -m " + length + " " + address + " > " + destination
    os.system(system_call)

# Process for recording the next show
def record_next_show(next_show):
    if next_show.time == 100:
        length = "4200"
    else:
        length = "7800"
    address = "http://132.162.36.191:8000/"
    title = next_show.title
    directory = "/Users/zacplett/desktop/work/stream_tests/streams"
    destination = directory + title + ".mp3"
    system_call = "curl -m " + length + " " + address + " > " + destination
    os.system(system_call)

if __name__=='__main__':
    main()
