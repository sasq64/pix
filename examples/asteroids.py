"""
Asteroids example for pixpy
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum

import pixpy as pix
from pixpy import Float2


@dataclass
class Sprite:
    """
    A sprite is an image that has a position on screen, and velocity.
    It also knows what to do when reaching the edge of the screen.
    """

    image: pix.Image
    "Image that represents sprite."

    pos: Float2
    "Current position of sprite."

    velocity: Float2 = field(default_factory=pix.Float2)
    "Velocity of sprite."

    rotation: float = 0
    "Rotation of sprite in radians."

    wrap: bool = True
    "True if sprite should wrap to other side when leaving screen."

    dead: bool = False
    "True if sprite should be removed."

    radius: float = 1
    "Radius of sprite, when checking collision."

    def update(self):
        self.pos += self.velocity

    def render(self, target: pix.Canvas):
        """Render the sprite to the target context."""

        # Check if position is outside screen
        d = self.pos.clip(Float2.ZERO, target.size)
        if d != Float2.ZERO:
            if self.wrap:
                self.pos -= target.size * d.sign()
            else:
                self.dead = True
        target.draw(image=self.image, center=self.pos, rot=self.rotation)

    F2 = Float2 | tuple[float, float]

    @staticmethod
    def from_lines(
        size: Float2 | tuple[float, float],
        points: list[Float2] | list[tuple[float, float]],
    ):
        """Create a sprite from lines"""
        image = pix.Image(size)
        image.clear(pix.color.TRANSP)
        image.line_width = 1
        image.lines(points + [points[0]])  # type: ignore
        return Sprite(image, pos=Float2.ZERO)


class State(Enum):
    PLAYING = 0
    "We are currently playing."

    SHIP_RESPAWN = 1
    "We have lost a life and ship is about to be respawned."

    GAME_OVER = 2
    "The game is over."


class Asteroids:
    "An Asteroids game for pixpy."

    def __init__(self, target: pix.Canvas):
        random.seed(19)
        self.target = target
        self.screen_size = target.size
        self.ship = Sprite.from_lines((32, 32), [(28, 16), (4, 8), (8, 16), (4, 24)])
        "The player ship sprite"

        self.life_image = self.ship.image
        "The image to represent lives."

        self.ship.pos = self.screen_size / 2
        self.asteroid_count = 4
        "Number of asteroids to spawn when screen is cleared."

        self.lives = 3
        self.respawn_at = -1
        self.bullet = pix.Image((4, 4))
        self.bullet.filled_circle(center=(2, 2), radius=2)
        self.bullets: list[Sprite] = []
        self.game_state: State = State.PLAYING
        self.score = 0
        self.frame_counter = 0
        self.font = pix.load_font("data/hyperspace_bold.ttf")
        self.numbers = [
            self.font.make_image(text=chr(0x30 + i), size=32, color=pix.color.YELLOW)
            for i in range(10)
        ]
        "Array of digit images used to render numbers."

        self.game_over = self.font.make_image("GAME_OVER", 48)
        self.asteroids: list[Sprite] = []
        "Current active asteroid sprites"

        self.spawn_asteroids()

    def render(self):
        """Render and update the game."""
        screen = self.target
        self.render_number(Float2(10, 10), self.score)
        for i in range(self.lives):
            screen.draw(
                image=self.life_image,
                center=(i * 40 + 500, 30),
                size=self.life_image.size * 2,
                rot=-math.pi / 2,
            )

        if self.game_state == State.GAME_OVER:
            screen.draw(image=self.game_over, center=self.screen_size / 2)
        elif self.game_state == State.SHIP_RESPAWN:
            if self.respawn_at == self.frame_counter:
                self.game_state = State.PLAYING
        else:
            self.update_player()
            self.ship.render(screen)

        for a in self.asteroids:
            a.update()
            a.render(screen)
        for b in self.bullets:
            b.update()
            b.render(screen)

        if self.game_state == State.PLAYING:
            self.collide_asteroids()

        self.bullets[:] = [b for b in self.bullets if not b.dead]
        self.asteroids[:] = [b for b in self.asteroids if not b.dead]

        if len(self.asteroids) == 0:
            self.asteroid_count += 1
            self.spawn_asteroids()
        self.frame_counter += 1

    def render_number(self, pos: Float2, value: int, digits: int = 5):
        """Render a number on the screen."""
        pos += (self.numbers[0].size.x * digits, 0)
        for _ in range(digits):
            img = self.numbers[value % 10]
            value //= 10
            self.target.draw(image=img, top_left=pos)
            pos -= (img.size.x, 0)

    def create_asteroid(self, radius: float) -> Sprite:
        """Create a new asteroid with the given radius."""
        s = 10
        z = radius * 2 + radius / 1.5
        points = [
            Float2.from_angle(i * math.pi * 2 / s)
            * (radius + ((i % 2) - 0.5) * random.random() * radius / 1.5)
            + (z / 2, z / 2)
            for i in range(s)
        ]
        asteroid = Sprite.from_lines((z, z), points)

        asteroid.velocity = Float2.from_angle(random.random() * math.pi * 2)
        r = Float2(random.random(), random.random())
        pos = self.screen_size * r
        # Clamp position to screen edge
        i = random.randint(0, 1)
        asteroid.pos = pos * (i, 1 - i)
        asteroid.radius = radius
        return asteroid

    def fire_bullet(self):
        """Fire a bullet in the same direction the ship is rotated."""
        vel = Float2.from_angle(self.ship.rotation) * 5.0
        self.bullets.append(Sprite(self.bullet, self.ship.pos, vel, 0, False))

    def update_player(self):
        """Read the keyboard and update the player ship."""
        ship = self.ship
        if pix.is_pressed(pix.key.LEFT):
            ship.rotation -= 0.05
        elif pix.is_pressed(pix.key.RIGHT):
            ship.rotation += 0.05
        if pix.was_pressed("x"):
            self.fire_bullet()

        speed = 0.1
        if pix.is_pressed("z"):
            v = ship.velocity + Float2.from_angle(ship.rotation) * speed
            m = v.mag()
            if m > 2.2:
                v = v / m * 2.2
            ship.velocity = v

        self.ship.update()

    def spawn_asteroids(self):
        """Spawn new asteroids when all asteroids are destroyed."""
        self.asteroids = [self.create_asteroid(40) for _ in range(self.asteroid_count)]

    def break_apart(self, sprite: Sprite):
        """Break sprite into two new sprites"""
        s = sprite.velocity.mag() * 2
        angle = sprite.velocity.angle()
        s0 = self.create_asteroid(sprite.radius / 2)
        s0.velocity = Float2.from_angle(angle + 0.2) * s
        s0.pos = sprite.pos + s0.velocity * sprite.radius / 4
        s1 = self.create_asteroid(sprite.radius / 2)
        s1.velocity = Float2.from_angle(angle - 0.2) * s
        s1.pos = sprite.pos + s1.velocity * sprite.radius / 4
        return [s0, s1]

    def collide_asteroids(self) -> None:
        """
        Iterate over all asteroids and see if they have collided with
        a bullet or the player ship.
        """
        new_asteroids: list[Sprite] = []
        for a in self.asteroids:
            if (self.ship.pos - a.pos).mag() < (a.radius + 10):
                a.dead = True
                self.lives -= 1
                if self.lives == 0:
                    self.game_state = State.GAME_OVER
                else:
                    self.game_state = State.SHIP_RESPAWN
                    self.respawn_at = self.frame_counter + 60
            for b in self.bullets:
                if (b.pos - a.pos).mag() < a.radius:
                    b.dead = True
                    a.dead = True
                    self.score += int(a.radius)
                    if a.radius > 10:
                        new_asteroids += self.break_apart(a)
        self.asteroids += new_asteroids


def main():
    screen = pix.open_display(size=(1280, 1024))
    game = Asteroids(screen)

    print(screen.size)
    while pix.run_loop():
        screen.clear()
        game.render()
        screen.swap()


if __name__ == "__main__":
    main()
