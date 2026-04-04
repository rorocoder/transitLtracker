# transitLtracker

## Brainstorming:

### Architecture

It should be one call, that will get me times. Then just have to 

### Trackers:

- 55 Bus Line
    - Garfield Red Line
    - Garfield Green Line
- (Optional) Metra 57th Stop

### Decisions:

Should tell me when I need to leave in order to catch the 55 bus. 
Should tell me if I should wait at home so I'm not stuck waiting on the 55 bus

Once on the 55 bus, it should tell me whether I should take the green line or red line
Tell me which will require the least amount of waiting time based off estimated drop off time and train arrival time

(Optional): If there's no trains arriving for this current 55 bus, then you can wait for the next 55 bus (or next applicable one) that will drop you off. 
If the next possible train is AFTER the next (not current) 55 bus then you shoudl wait for that one so you're not stuck waiting

Prefer the Red line over the green because its faster? BUT I hate waiting at the red line. 

Calculate which is the faster route to the loop? 

Find out if there's delays? 

### Timings:

RL -> Loop = 20 min
GL -> Loop = 25 min (+5)

RL -> Lincoln Park = 36 min
GL -> Lincoln Park = 48 min (+12)

55 -> RL = 11 min
55 -> GL = 7 min

To loop, RL and GL are actually very close equal with the extra time on bus.


## Todo

- see if we can estimate an arrival time to the loop
- metra stuff
- output to stderr or something to differentiate from stdout
    - make a output schema to be read by shortcut
- automate shortcut
- add parameters? ways to say i want times for GL or RL or bus times (can add menus in shortcut)
- automation - constant looping