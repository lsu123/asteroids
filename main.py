import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state
from player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_clock = pygame.time.Clock()
    dt = 0
    print('Starting Asteroids with pygame version: (%s)' % pygame.version.ver)
    print('Screen width: %s' % SCREEN_WIDTH)
    print('Screen height: %s' % SCREEN_HEIGHT)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("red")
        player.draw(screen)
        pygame.display.flip()
        dt = game_clock.tick(60) / 1000  # 60 FPS cap + catch delta time and convert to seconds

if __name__ == "__main__":
    main()
