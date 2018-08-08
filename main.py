import os, sys, numpy, gameplay
from psychopy import core, event, visual, sound, gui

gui = gui.Dlg()
gui.addField("Participant Number:")
gui.addField("Name:")
gui.show()

subject_id = gui.data[0]
subject_name = gui.data[1]

n_blocks = 10

# win = visual.Window([1200,800], fullscr=True,  color=[-1,-1,-1])
win = visual.Window([1200,800], color=[-1,-1,-1])

stars = visual.DotStim(win, dir=1, nDots=100, fieldSize=(2,2))

ship = visual.ImageStim(win, image='resources/images/ship.png', size = 0.4)
asteroid = visual.ImageStim(win, 'resources/images/asteroid.png', pos=(0,1), size = 0.2)
laser = visual.ImageStim(win, image='resources/images/beams.png', size = 0.3, pos = (-0.15, 0.1))
splash_title = visual.ImageStim(win, image="resources/images/splash.png", opacity = 0)

score = visual.TextStim(win, text='0', pos=(0.8,0.8), color='white', font='Eight-bit Madness')
instructions_text = visual.TextStim(win, text='', color='white', font='Eight-bit Madness', height=0.2)
press_to_continue = visual.TextStim(win, text='Press SPACE BAR to continue.', color='yellow', font='Eight-bit Madness')
level_text = visual.TextStim(win, text='', pos=(0,0.4), color='yellow', font='Eight-bit Madness')

health = visual.Rect(win, width=0.4, height=0.03, pos=(-0.7,0.8), fillColor='red')
fuel = visual.Rect(win, width=0.4, height=0.03, pos=(-0.7,0.75), fillColor='blue')

music = sound.Sound('music.wav')

def ship_sway(counter):
    
    if counter % 2 == 0:
        ship.pos += (0.005, 0.005)
    else:
        ship.pos += (-0.005, -0.005)

    if counter % 100 == 0:
        sway = numpy.random.choice(['left', 'right'])
        if sway == 'left' and ship.pos[0] > -0.1:
            ship.pos += (-0.01, 0)
        elif sway == 'right' and ship.pos[0] < 0.1:
            ship.pos += (0.01, 0)

def arrange_bars(health_points=5, fuel_points=30, base_health=5, base_fuel=30, base_width=0.4, base_x=-0.7):

    health.width = base_width * (health_points/base_health) if health_points >= 0 else 0
    fuel.width = base_width * (fuel_points/base_fuel) if fuel_points >= 0 else 0

    health.pos[0] = base_x + (health.width / 2) - (base_width/2)
    fuel.pos[0] = base_x + (fuel.width / 2) - (base_width/2)

def get_ready(frequency='high', block=1):

    if block == -1 or block == 0:
        level_text.text = 'Practice: Listen to the {0} sounds'.format(frequency.upper())
    else:
        level_text.text = 'Level {0}: Listen to the {1} sounds'.format(block, frequency.upper())

    for frameN in range(2000):
        
        ship_sway(frameN)

        stars.draw()
        ship.draw()
        level_text.draw()
        score.draw()
        health.draw()
        fuel.draw()

        win.flip()

def gameplay(frequency='high', block=1):

    sequence = sound.Sound('resources/stimuli/{0}_{1}_stream.wav'.format(frequency, block))

    with open('resources/stimuli/{0}_{1}_targets.txt'.format(frequency, block)) as f:
        targets = [tuple(map(float, i.split(','))) for i in f]

    counter, counter_correct, counter_incorrect, counter_missed, laser_counter, asteroid_counter = int(), int(), int(), int(), int(), int()

    responses = []

    target_window, last_target_window, fired, dodged, missed, asteroid_boolean = False, False, False, False, False, False

    get_ready(frequency, block)

    sequence.play()
    clock = core.Clock()
    
    while clock.getTime() < (sequence.getDuration() + 1):
        
        counter += 1

        keys = event.getKeys(keyList=["space"], timeStamped=clock)

        # STEP 1: check to see if we're in a target window
        target_window = False
        for pair in targets: 
            if pair[0] < clock.getTime() < pair[1]:
                target_window = True
                break

        # STEP 2: now check to see if we just left a target window
        if target_window == False and last_target_window == True:
            if dodged:
                dodged = False
            else:
                counter_missed += 1
                missed = True
                print('Missed!')
        
        last_target_window = target_window
        
        # STEP 3: handle button presses
        if len(keys):
            
            fired = True

            if target_window:
                keys[0].append('correct')
                if dodged == False: # this makes sure you can only score once per window
                    counter_correct += 1 
                dodged = True
            else:
                keys[0].append('incorrect')
                counter_incorrect += 1
                dodged = False

            responses.append(keys)

        # STEP 4: draw the laser
        if fired and laser_counter < 20:

            laser_counter += 1

            laser.pos += (0, 0.05)

        elif fired:

            laser_counter = 0
            fired = False

            laser_side = numpy.random.choice(['left','right'])
            if laser_side == 'left':
                laser.pos = (ship.pos[0]-0.15,0.1)
            else:
                laser.pos = (ship.pos[0]+0.15,0.1)

        # STEP 5: draw the asteroid
        if missed:
            asteroid_boolean = True

        if asteroid_boolean and asteroid_counter < 100:
            
            asteroid_counter += 1

            asteroid.pos[0] = ship.pos[0]
            asteroid.pos += (0, -0.1)
        
        elif asteroid_boolean:

            asteroid_counter = 0
            asteroid_boolean = False
            missed = False

            asteroid.pos = (0, 1)

        # STEP 6: draw the health bar
        arrange_bars(health_points=5-counter_missed,fuel_points=30-counter_incorrect)

        score.text = (counter_correct * 20) - (counter_missed * 10) - (counter_incorrect * 5)

        ship_sway(counter)

        stars.draw()
        ship.draw()
        if fired:
            laser.draw()
        if asteroid_boolean:
            asteroid.draw()
        score.draw()
        health.draw()
        fuel.draw()

        win.flip()
    
    savefile_name = '{0}_{1}_{2}'.format(subject_id, frequency, block)
    savefile = open('data/{0}_data.txt'.format(savefile_name), 'w')
    savefile.write(str(responses) + '\n')

# start background music
music.play()

# title screen
counter = int()
while event.getKeys(keyList=['space']) == []:
    
    # set opacity to increase with each iteration up to maximum
    if counter < 5000:
        counter += 1
    stars.opacity = counter/5000
    splash_title.opacity = counter/5000
    
    # draw each layer in turn
    stars.draw()
    splash_title.draw()

    win.flip()

for frameN in range(1000):

    # set opacity to decrease with each iteration
    splash_title.opactity = 1 - frameN/1000
    stars.opactity = 1 - frameN/1000

    # draw each layer in turn
    stars.draw()
    splash_title.draw()

    win.flip()
stars.opacity = 1

# instructions
instructions_text.text = subject_name + ', we need your help!'
press_to_continue.pos = (0,-0.8)
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'We have escaped capture and stolen a spacecraft from the alien fleet. Now we must fly back to Earth.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'Asteroids block our path to safety. The only way to avoid them is to use the ship\'s radar system.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'The radar system is made with alien technology. You need to use your ears to hear the warnings.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'You will hear three beeps every time the radar system searches for an asteroid. Each beep sounds like a musical note.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'When you hear the same three beeps twice in a row, that means an asteroid is approaching. You need to act fast!'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'Use the SPACE BAR to fire the ship\'s laser cannon when an asteroid is in range.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'Be careful when firing the laser. If you use it too much, the ship will run out of fuel and crash.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'If asteroids are not shot down quickly, the ship will be damaged. Try to respond as soon as your hear the repeated beeps.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

music.fadeOut(2000)

instructions_text.text = 'Are you ready to start?'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

gameplay(frequency='high', block=-1)

instructions_text.text = 'The radar is tuning in to a LOW frequency. Keep listening!'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

gameplay(frequency='low', block=-1)

instructions_text.text = 'The radar seems to be malfunctioning. Now you will hear both radar frequencies at the same time.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

instructions_text.text = 'You only need to listen to one radar frequency. Pay attention to messages which say HIGH or LOW.'
while event.getKeys(keyList=['space']) == []:
    instructions_text.draw()
    press_to_continue.draw()
    win.flip()

gameplay(frequency='high', block=0)
gameplay(frequency='low', block=0)

for block in range(n_blocks):
    gameplay(frequency='high', block=block)

for block in range(n_blocks):
    gameplay(frequency='high', block=block)