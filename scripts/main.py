import pygame
from settings import *

import pygame.display as display
from pygame.image import load

from editor import Editor

class Main:
    def __init__(self):
        pygame.init()
        self.displaySurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.editor = Editor()
        
        # Cursor
        surf = load('graphics/cursors/mouse.png').convert_alpha()
        cursor = pygame.cursors.Cursor((0,0), surf)
        pygame.mouse.set_cursor(cursor)
        
    def run(self):
        while True:
            dt = self.clock.tick(MAX_FRAMERATE) / 1000
            
            self.editor.run(dt)
            display.update()
            
if __name__ == '__main__':
    main = Main()
    main.run()