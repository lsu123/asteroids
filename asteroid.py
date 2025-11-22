import pygame
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from circleshape import CircleShape
import random
from logger import log_event

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        from asteroidfield import AsteroidField  # Import here to avoid circular dependency
        log_event("asteroid_split")
        self.kill()
        if self.radius < ASTEROID_MIN_RADIUS:
            return
        else:
            kind = self.radius // ASTEROID_MIN_RADIUS
            for _ in range(2):
                new_radius = ASTEROID_MIN_RADIUS * (kind - 1)
                new_asteroid = Asteroid(self.position.x, self.position.y, new_radius)
                new_velocity = self.velocity.rotate(random.randint(-45, 45)) * 1.2
                new_asteroid.velocity = new_velocity
                AsteroidField().spawn(new_radius, self.position, new_velocity)

