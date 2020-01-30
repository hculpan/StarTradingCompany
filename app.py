import pygame
import random
from StarTradingCompany import MainScene, GameState
import logging
import traceback
import sys
import os

logging.basicConfig(
    filename='/Users/harryculpan/src/StarTradingCompany/myapp.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


class MainApp:
    def main_loop(self, width, height, fps):
        random.seed()

        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode(
            (width, height), pygame.SCALED)
        pygame.display.set_caption("Star Trading Company")
        clock = pygame.time.Clock()

        no_keys_pressed = pygame.key.get_pressed()
        for key in no_keys_pressed:
            key = False

        active_scene = MainScene.MainScene(width, height)

        while active_scene != None:
            # Event filtering
            filtered_events = []
            for event in pygame.event.get():
                pressed_keys = no_keys_pressed

                quit_attempt = False
                if event.type == pygame.QUIT:
                    quit_attempt = True
                elif event.type == pygame.KEYDOWN:
                    pressed_keys = pygame.key.get_pressed()
                    alt_pressed = pressed_keys[pygame.K_LALT] or \
                        pressed_keys[pygame.K_RALT]
                    if event.key == pygame.K_ESCAPE:
                        quit_attempt = True
                    elif event.key == pygame.K_F4 and alt_pressed:
                        quit_attempt = True

                if quit_attempt and active_scene.Terminate():
                    pygame.quit()

                filtered_events.append(event)

                active_scene.ProcessInput(filtered_events, pressed_keys)
            active_scene.Update()
            active_scene.Render(screen)

            active_scene = active_scene.next

            pygame.display.flip()
            clock.tick(fps)


try:
    app = MainApp()
    app.main_loop(1200, 871, 30)
except:
    logging.error(traceback.format_exc())
