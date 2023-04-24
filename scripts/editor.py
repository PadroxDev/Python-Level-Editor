import pygame, sys, os
import json
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.key import get_pressed as key_pressed
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
from settings import *
from saving import SaveHandler

from helpers import clamp

import pygame.display as display
import pygame.draw as draw

from random import randint

from components.button import Button

working_save = "Preview Save #1.json"

save = SaveHandler()
save.load()


class Editor:
    def __init__(self)->None:
        
        # Main setup
        self.displaySurface = display.get_surface()
        
        # Navigation
        self.origin = vector()
        self.panActive = False
        self.panOffset = vector()
        
        # Support lines
        self.supportLinesSurf = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.supportLinesSurf.set_colorkey('green')
        self.supportLinesSurf.set_alpha(30)
        
        # tileSize
        self.tileSize = 64
        self.zoomFactor = 1
        
        self.squares = {}
        self.tiles = {}
        
        self.physicsEnabled = False
        self.physicsPoints = [[]]
        self.physicsDrawIndex = 0
        
        # Buttons
        self.saveButton = Button("graphics/buttons/save_button.png", (30,50))
        self.saveButton.bind(self.performSave)
        
        self.loadButton = Button("graphics/buttons/load_button.png", (30, 125))
        self.loadButton.bind(self.loadSave)
        
        self.physicsEnabledButton = Button("graphics/buttons/physics_button.png", (30,200))
        self.physicsEnabledButton.bind(self.enablePhysics)
        
        self.loadSave(working_save)
    
    def enablePhysics(self):
        self.physicsEnabled = not self.physicsEnabled
        print(self.physicsEnabled)
    
    ### Tiling ###
    # pos: the gridbased x and y coordinates
    
    def getScaledTileSize(self, tileSize=DEFAULT_TILE_SIZE)->float:
        return int(tileSize * self.zoomFactor)
    
    def getCell(self, pos:tuple)->tuple:
        distanceToOrigin = vector(pos) - self.origin
        scaledTileSize = self.getScaledTileSize(self.tileSize)
        
        if distanceToOrigin.x > 0:
            col = int(distanceToOrigin.x / scaledTileSize)
        else:
            col = int(distanceToOrigin.x / scaledTileSize) - 1
        if distanceToOrigin.y > 0:
            row = int(distanceToOrigin.y / scaledTileSize)
        else:
            row = int(distanceToOrigin.y / scaledTileSize) - 1
    
        return col, row
    
    def getCurrentCell(self)->tuple:
        return self.getCell(mouse_pos())
    

    def tileWasDrawnOn(self, pos:tuple)->bool:
        return pos in self.squares.keys() or pos in self.tiles.keys()
    
    # Input
    def eventLoop(self)->None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.panInput(event)
            self.draw()
    
    def panInput(self, event:pygame.event.Event)->None:
        # Middle mouse button pressed / released
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[1]:
            self.panActive = True
            self.panOffset = vector(mouse_pos()) - self.origin
        if not mouse_buttons()[1]:
            self.panActive = False
        
        # Mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if key_pressed()[pygame.K_LCTRL]:
                self.tileSize = int(clamp(self.tileSize + event.y * (self.tileSize / 2), MIN_TILE_SIZE, MAX_TILE_SIZE))
            else:
                self.zoomFactor = clamp(self.zoomFactor + event.y * ZOOM_STEP, MIN_ZOOM, MAX_ZOOM)
        
        # Panning update
        if self.panActive:
            self.origin = vector(mouse_pos()) - self.panOffset
    
    # Saving
    def loadSave(self, saveName:str=working_save)->None:
        path = os.path.join("saves/", saveName)
        self.tiles.clear()
        
        if not os.path.exists(path):
            print("The save file wasn't found!")
            return
        
        with open(path, 'r') as f:
            data = json.load(f)
            
        for key, value in data['tiles'].items():
            # Formatting & converting coords to int
            coords = key.split(',')
            coords[0], coords[1] = int(coords[0]), int(coords[1])
            
            if value['type'] == 'sprite':
                self.tiles[tuple(coords)] = {
                    'surf': load(value['sprite_surf']).convert_alpha(),
                    'path': value['sprite_surf'],
                    'tiling': value['tiling']
                }
            else:
                print("Unsupported tile data")
        
        self.physicsPoints = []
        for pointCloud in data['physics']:
            tempPhysics = []
            for point in pointCloud:
                splittedPoint = point.split(',')
                tempPhysics.append((int(splittedPoint[0]), int(splittedPoint[1])))
            self.physicsPoints.append(tempPhysics)
    
    def performSave(self, saveName:str=working_save, name:str="Save #1")->None:
        path = path = os.path.join("saves/", saveName)
        
        with open(path, 'w') as f:
            save = {
                "name": name,
                "tiles": {},
                "physics": []
            }
            
            for key, value in self.tiles.items():
                coords = str(key[0]) + ',' + str(key[1])
                save['tiles'][coords] = {
                    'type': "sprite",
                    'sprite_surf': value['path'],
                    'tiling': value['tiling']
                }
            
            for i in range(len(self.physicsPoints)):
                pointCloud = []
                for point in self.physicsPoints[i]:
                    pointCloud.append(str(point[0])+ ',' + str(point[1]))
                save["physics"].append(pointCloud)
            
            json.dump(save, f, indent=6)
            print("Successfully saved!")
    
    # Drawing
    def drawTileBorders(self)->None:
        scaledTileSize = self.getScaledTileSize(self.tileSize)
        cols = WINDOW_WIDTH // scaledTileSize
        rows = WINDOW_HEIGHT // scaledTileSize
        
        originOffset = vector(
            x = self.origin.x - int(self.origin.x / scaledTileSize) * scaledTileSize,
            y = self.origin.y - int(self.origin.y / scaledTileSize) * scaledTileSize
        )
        
        self.supportLinesSurf.fill('green')
        
        for col in range(cols+1):
            x = originOffset.x + col * scaledTileSize
            draw.line(self.supportLinesSurf, LINE_COLOR, (x,0), (x,WINDOW_HEIGHT))
            
        for row in range(rows+1):
            y = originOffset.y + row * scaledTileSize
            draw.line(self.supportLinesSurf, LINE_COLOR, (0,y), (WINDOW_WIDTH,y))
        
        self.displaySurface.blit(self.supportLinesSurf, (0,0))
    
    def drawSelectionClue(self)->None:
        currentCell = self.getCurrentCell()
        
        # If the tile was drawn on, then return out
        if self.tileWasDrawnOn(currentCell): return
        
    def physicsDraw(self):
        if mouse_buttons()[0]:
            self.physicsPoints[self.physicsDrawIndex].append(mouse_pos())
        if mouse_buttons()[2] and len(self.physicsPoints[self.physicsDrawIndex]) > 2:
            self.physicsDrawIndex += 1
            self.physicsPoints.append([])
    
    def defaultDraw(self):
        if mouse_buttons()[0]:
            self.tiles[self.getCurrentCell()] = {
                'surf': load('graphics/placeholders/nezuko.png').convert_alpha(),
                'path': 'graphics/placeholders/nezuko.png',
                'tiling': self.tileSize
            }
        if mouse_buttons()[2]:
            self.squares[self.getCurrentCell()] = {
                'color': pygame.Color(randint(0, 255),randint(0, 255),randint(0, 255)),
                'tiling': self.tileSize
            }
        if key_pressed()[pygame.K_c]: # WITH ???
            currentCell = self.getCurrentCell()
            if currentCell in self.squares.keys():
                del self.squares[currentCell]
            if currentCell in self.tiles.keys():
                del self.tiles[currentCell]
    
    def draw(self)->None:
        if self.saveButton.rect.collidepoint(mouse_pos()) or self.loadButton.rect.collidepoint(mouse_pos()) or self.physicsEnabledButton.rect.collidepoint(mouse_pos()):
            return
        
        if self.physicsEnabled:
            self.physicsDraw()
        else:
            self.defaultDraw()
    
    def drawTiles(self)->None:
        if self.physicsEnabled:
            for pointCloud in self.physicsPoints:
                if len(pointCloud) > 2:
                    draw.polygon(self.displaySurface, pygame.Color(255,0,0), pointCloud)
        
        for key, value in self.squares.items():
            scaledTileSize = self.getScaledTileSize(value['tiling'])
            rect = pygame.Rect((self.origin + vector(key) * scaledTileSize),(scaledTileSize,scaledTileSize))
            draw.rect(self.displaySurface, value['color'], rect)
            
        for key, value in self.tiles.items():
            scaledTileSize = self.getScaledTileSize(value['tiling'])
            pos = self.origin + vector(key) * scaledTileSize
            surf = pygame.transform.scale(value['surf'], (scaledTileSize,scaledTileSize))
            self.displaySurface.blit(surf, pos)
    
    def run(self, dt:float)->None:
        self.displaySurface.fill('white')
                
        # drawing
        self.eventLoop()
        self.drawTileBorders()
        self.drawSelectionClue()
        self.drawTiles()
        self.saveButton.draw()
        self.loadButton.draw()
        self.physicsEnabledButton.draw()
        draw.circle(self.displaySurface, 'red', self.origin, 10)