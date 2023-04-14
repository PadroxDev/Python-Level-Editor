import pygame, sys
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.key import get_pressed as key_pressed
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
from settings import *

import pygame.display as display
import pygame.draw as draw

from random import randint

class Editor:
    def __init__(self):
        
        # Main setup
        self.displaySurface = display.get_surface()
        
        # Navigation
        self.origin = vector()
        self.panActive = False
        self.panOffset = vector()
        
        # Support lines
        self.supportLinesSurf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.supportLinesSurf.set_colorkey('green')
        self.supportLinesSurf.set_alpha(30)
        
        self.squares = {}
        self.tiles = {}
    
    def getCell(self, pos):
        distanceToOrigin = vector(pos) - self.origin
        
        if distanceToOrigin.x > 0:
            col = int(distanceToOrigin.x / TILE_SIZE)
        else:
            col = int(distanceToOrigin.x / TILE_SIZE) - 1
        if distanceToOrigin.y > 0:
            row = int(distanceToOrigin.y / TILE_SIZE)
        else:
            row = int(distanceToOrigin.y / TILE_SIZE) - 1
    
        return col, row
    
    def getCurrentCell(self):
        return self.getCell(mouse_pos())
    
    # Tiling
    def tileWasDrawnOn(self, pos):
        return pos in self.squares.keys() or pos in self.tiles.keys()
    
    # Input
    def eventLoop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.panInput(event)
            self.draw()
    
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
    def drawTileBorders(self):
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
        
        self.displaySurface.blit(self.supportLinesSurf, (0,0))
    
    def drawSelectionClue(self):
        pass
    
    def draw(self):
        if mouse_buttons()[0]:
            self.tiles[self.getCurrentCell()] = load('graphics/placeholders/capybara.png').convert_alpha()
        if mouse_buttons()[2]:
            self.squares[self.getCurrentCell()] = pygame.Color(randint(0, 255),randint(0, 255),randint(0, 255))
        if key_pressed()[pygame.K_c]: # WITH ???
            currentCell = self.getCurrentCell()
            if currentCell in self.squares.keys():
                del self.squares[currentCell]
            if currentCell in self.tiles.keys():
                del self.tiles[currentCell]
    
    def drawTiles(self):
        for key, value in self.squares.items():
            rect = pygame.Rect((self.origin + vector(key) * TILE_SIZE),(TILE_SIZE,TILE_SIZE))
            draw.rect(self.displaySurface, value, rect)
            
        for key, value in self.tiles.items():
            pos = self.origin + vector(key) * TILE_SIZE
            self.displaySurface.blit(value, pos)
    
    def run(self, dt):
        self.displaySurface.fill('white')
        
        # drawing
        self.eventLoop()
        self.drawTileBorders()
        self.drawSelectionClue()
        self.drawTiles()
        draw.circle(self.displaySurface, 'red', self.origin, 10)