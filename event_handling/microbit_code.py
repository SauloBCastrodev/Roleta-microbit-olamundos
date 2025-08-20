from microbit import *

while True:
    events = []
    if button_a.was_pressed():
        events.append("btna")

    if button_b.was_pressed():
        events.append("btnb")


    if len(events) > 0:
        print(",".join(events))
    else:
        print("")