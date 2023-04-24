import pygame
import pygame.draw as draw
from pygame.mouse import get_pressed as mouse_buttons
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load

class Button:
    def __init__(self, imgPath:str, dest:tuple=(0,0))->None:
        self.displaySurf = pygame.display.get_surface()
        self.sprite = pygame.transform.scale(load(imgPath), (256/2,128/2))
        self.dest = dest
        self.on_click = None
        self.previously_clicked = False
        self.rect = pygame.Rect(0,0,0,0)
        
    def bind(self, to)->None:
        self.on_click = to
        
    def draw(self)->None:
        if not self.displaySurf:
            print("No surface found on button initialization!")
            return
        
        self.rect = self.displaySurf.blit(self.sprite, self.dest)
        if self.rect.collidepoint(mouse_pos()) and mouse_buttons()[0]:
            if self.on_click and not self.previously_clicked:
                self.previously_clicked = True
                self.on_click()
        else:
            self.previously_clicked = False