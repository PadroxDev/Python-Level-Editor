import pygame, sys
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.key import get_pressed as key_pressed
from pygame.mouse import get_pos as mouse_pos
from settings import *

import pygame.display as display
import pygame.draw as draw

class Editor:
    def __init__(self):
        
        # Main setup
        self.display_surface = display.get_surface()
        
        # Navigation
        self.origin = vector()
        self.panActive = False
        self.panOffset = vector()
        
        # Support lines
        self.supportLinesSurf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.supportLinesSurf.set_colorkey('green')
        self.supportLinesSurf.set_alpha(30)
    
    # Input
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.panInput(event)
    
    def panInput(self, event):
        
        # Middle mouse button pressed / released
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
            self.panActive = True
            self.panOffset = vector(mouse_pos()) - self.origin
        if not mouse_buttons()[1]:
            self.panActive = False
        
        # Mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if key_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * 50
            else:
                self.origin.x -= event.y * 50
        
        # Panning update
        if self.panActive:
            self.origin = vector(mouse_pos()) - self.panOffset
    
    # Drawing
    def draw_tile_borders(self):
        cols = WINDOW_WIDTH // TILE_SIZE
        rows = WINDOW_HEIGHT // TILE_SIZE
        
        originOffset = vector(
            x = self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
            y = self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE
        )
        
        self.supportLinesSurf.fill('green')
        
        for col in range(cols+1):
            x = originOffset.x + col * TILE_SIZE
            draw.line(self.supportLinesSurf, LINE_COLOR, (x,0), (x,WINDOW_HEIGHT))
            
        for row in range(rows+1):
            y = originOffset.y + row * TILE_SIZE
            draw.line(self.supportLinesSurf, LINE_COLOR, (0,y), (WINDOW_WIDTH,y))
        
        self.display_surface.blit(self.supportLinesSurf, (0,0))
    
    def run(self, dt):
        self.event_loop()
        
        # drawing
        self.display_surface.fill('white')
        self.draw_tile_borders()
        draw.circle(self.display_surface, 'red', self.origin, 10)