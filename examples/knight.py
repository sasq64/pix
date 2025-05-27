# Sprite example for pixpy
# Displays a knight character that animates, and can move left/right and attack

import os
import pixpy as pix

screen = pix.open_display(size=(640, 360))

animations: dict[str, list[pix.Image]] = {}

# Load every png image in the `data/knight` folder
with os.scandir('data/knight') as it:
    for entry in it:
        if entry.name.endswith(".png") and entry.is_file():
            name = os.path.splitext(entry.name)[0]
            """?
            We use the file name (without extension) as the animation name, and we
            assume that every png file contains a set of 120x80 images layed out
            side by side (check for yourself).
            """
            animations[name] = pix.load_png(entry.path).split(width=120, height=80)

run_anim = animations["Run"]
attack_anim = animations["Attack"]
pos = pix.Int2(200,280)
scale = pix.Float2(2,2)

attack_counter = 0

while pix.run_loop():
    screen.clear()
    if pix.is_pressed(pix.key.LEFT):
        """?
        We negate the scale to flip the sprite along the Y axis
        so he faces the right way.
        """
        scale = pix.Float2(-2, 2)
        pos -= (2,0)
    elif pix.is_pressed(pix.key.RIGHT):
        scale = pix.Float2(2, 2)
        pos += (2,0)
    if pix.is_pressed(pix.key.ENTER):
        attack_counter = 40

    if attack_counter > 0:
        """?
        If we are attacking, we calculate which of the 4 attack frames to
        show from the counter value (which goes from 40 down to 0)
        """
        img = attack_anim[(40-attack_counter)//10]
        attack_counter -= 1
    else:
        """?
        We calculate the current animation frame from the sprites
        X-position. This makes it so it actually looks like the
        knight is using his feet to move
        """
        frame = (pos.x // 10) % 10
        img = run_anim[frame]
    screen.draw(image=img, center=pos, size=img.size*scale)
    screen.swap()
