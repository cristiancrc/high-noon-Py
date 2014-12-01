# -*- coding: utf-8 -*-
"""
Created on Wed Oct 01 10:42:19 2014

High Noon 2014

version 2.0

Based on a z80 spectrum computer game from the `80
The original can be played here:
http://www.freevintagegames.com/SMSarcade/newarcade/spectrum/H/3/H/High%20Noon%201983Abbex%20Electronicsa.z80.php

To do:

# game
+ use controller physics display + game time loops
+ slow down the game for focus without messing with FPS, just by game loop physics update
- log game (player and ai) for replay and relay
- problem with bullet collision and player or health overcharge
- problem with ghost carriage and bullet collision

# sound

# graphics

# physics

# a.i.
- write a fun ai

@author: Cristian Calmuschi
@version: 141026

"""
import copy
# from datetime import timedelta
import random
import sys
import webbrowser
# from pprint import pprint
import pygame
# import pygame.mixer
from pygame.locals import *

pygame.init()
pygame.mixer.init(frequency=22050, size=8, channels=2, buffer=2048)

# dictionary
# R    G    B
BLACK =      (  0,  0,  0)  #
WHITE =      (255,255,255)  #
RED =        (255,  0,  0)  #
GREEN =      (  0, 255, 0)  #
BLUE =       (  0,  0,255)
YELLOW =     (255,255,  0)
FUCHSIA =    (255,  0,255)
CYAN =       (  0,255,255)
ORANGE =     (255,128,  0)
PINK =       (255,  0,128)
LIME =       (128,255,  0)
LIGHTGREEN = (  0,255,128)
SKYBLUE =    (  0,128,255)
DARKPURPLE = (128,  0,255)
GRAY =       (100,100,100)
NAVYBLUE =   ( 60, 60,100)
REDT =       (255,  0,  0, 150)  #
BLUET =      (  0,128,255, 150)  #
NBLUE =      ( 60, 60,100, 150)  #
SAND =       (255,255,200)  #

NORMAL = 'normal'
HARD = 'hard'
FIRED = 'fired'
HIT = 'hit'
HURT = 'hurt'
DEAD = 'dead'
NOAMMO = 'noAmmo'
RELOAD = 'reload'
CONTINUOUS = 'continuous'
CARRIAGE = 'carriage'
OBSTACLE = 'obstacle'
BLOCKY = 'blocky'
LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'
FIRE = 'fire'
FOCUS = 'focus'

# ##load images
# cowboy
cowboy = pygame.image.load('./assets/cowboy.png')
imgCowboy = {}
imgCowboy[RIGHT] = {}
imgCowboy[LEFT] = {}
imgCowboy[RIGHT][NORMAL] = cowboy.subsurface(1423, 8, 116, 121)
imgCowboy[RIGHT][FIRED] = cowboy.subsurface(1664, 8, 116, 121)
imgCowboy[RIGHT][HIT] = cowboy.subsurface(1664, 506, 116, 121)
imgCowboy[LEFT][NORMAL] = cowboy.subsurface(1404, 136, 116, 121)
imgCowboy[LEFT][FIRED] = cowboy.subsurface(1664, 137, 116, 121)
imgCowboy[LEFT][HIT] = cowboy.subsurface(1664, 766, 116, 121)

# load sounds
sound = {}
sound[FIRE] = {}
sound[NOAMMO] = {}
sound[HURT] = {}
sound[DEAD] = {}

sound[FIRE][LEFT] = pygame.mixer.Sound('./assets/gunShot2.wav')
sound[FIRE][RIGHT] = pygame.mixer.Sound('./assets/gunShot3.wav')

sound[NOAMMO][LEFT] = pygame.mixer.Sound('./assets/noAmmo0.wav')
sound[NOAMMO][RIGHT] = pygame.mixer.Sound('./assets/noAmmo1.wav')

sound[HURT][LEFT] = pygame.mixer.Sound('./assets/hitHurt1.wav')
sound[HURT][RIGHT] = pygame.mixer.Sound('./assets/hitHurt0.wav')

sound[DEAD][LEFT] = pygame.mixer.Sound('./assets/dead0.wav')
sound[DEAD][RIGHT] = pygame.mixer.Sound('./assets/dead1.wav')

# sndHurt.set_volume(0.2)

sound[HIT] = {}
sound[HIT][CARRIAGE] = []
sound[HIT][CARRIAGE].append(pygame.mixer.Sound('./assets/hitCarriage0.wav'))
sound[HIT][CARRIAGE].append(pygame.mixer.Sound('./assets/hitCarriage1.wav'))

sound[HIT][OBSTACLE] = []
sound[HIT][OBSTACLE].append(pygame.mixer.Sound('./assets/hitObject0.wav'))
sound[HIT][OBSTACLE].append(pygame.mixer.Sound('./assets/hitObject1.wav'))

sound[RELOAD] = pygame.mixer.Sound('./assets/reload0.wav')

# sound[CLICK] = pygame.mixer.Sound('./assets/click0.wav')

# manually measured distances
imgTopClearance = 16  # manually measured
imgTopToGun = 46 - imgTopClearance  # manually measured
imgHealthBarOffset = 20  # manually measured
imgSideToGun = 30  # manually measured
edgeClearance = 40  # distance from players to edge
# carriage
imgCarriage = pygame.image.load('./assets/carriage.png')
# obstacle
imgObstacle = pygame.image.load('./assets/Wood_Block_Tall.png')

# default player settings
animationDelay = 250  # time to display shooting
difficulty = NORMAL  # default difficulty
# define keys
player1keys = {}
player1keys[UP] = K_a
player1keys[DOWN] = K_z
player1keys[FIRE] = K_x
player1keys[FOCUS] = K_c

player2keys = {}
player2keys[UP] = K_UP
player2keys[DOWN] = K_DOWN
player2keys[FIRE] = K_RCTRL
player2keys[FOCUS] = K_SLASH

# world settings
WINDOWWIDTH = 800  # size of window's width in pixels
WINDOWHEIGHT = 600  # size of windows' height in pixels
FPS = 60  # frames per second, the general speed of the program
FPSFOCUS = 30  # speed during focus
BGCOLOR = SAND
DRAWCOLOR = BLACK
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('High Noon')

# font
BASICFONTSIZE = 20
SMALLFONTSIZE = 10
BIGFONT = pygame.font.Font('./assets/freesansbold.ttf', 50)
BASICFONT = pygame.font.Font('./assets/freesansbold.ttf', BASICFONTSIZE)
SMALLFONT = pygame.font.Font('./assets/freesansbold.ttf', SMALLFONTSIZE)

fpsClock = pygame.time.Clock()


class Cowboy():
    objectList = []
    speed = 4.

    def __init__(self, heading = RIGHT):
        Cowboy.objectList.append(self)

        # properties
        self.name = 'Cowboy instance'
        self.debug = False
        self.controller = None # ai control, none is keyboard
        # self.damage override bullet damage
        self.state = NORMAL  # normal, fired, hit
        self.fired = False
        self.hit = False
        self.focused = False
        self.enemy = None
        self.score = 0
        self.speed = 4.  # movement speed
        self.baseHealth = 4  # player health, usually bullets needed
        self.health = self.baseHealth
        self.healthRecharge = 0.0005 #units of health regained per frame .005
        self.baseFocus = 120  # units of focus available
        self.focus = self.baseFocus
        self.focusDrain = 5  # units of focus lost per frame  10
        self.focusRecharge = 1  # units of focus regained per frame
        self.baseAmmo = 6  # bullets available
        self.ammo = self.baseAmmo

        #get correct image from sprite
        self.heading = heading
        self.image = {}
        self.image[NORMAL] = imgCowboy[self.heading][NORMAL]
        self.image[FIRED] = imgCowboy[self.heading][FIRED]
        self.image[HIT] = imgCowboy[self.heading][HIT]
        self.texture = self.image[NORMAL]

        # sound effects
        self.sound = {}
        self.sound[HURT] = sound[HURT][self.heading]
        self.sound[FIRE] = sound[FIRE][self.heading]
        self.sound[NOAMMO] = sound[NOAMMO][self.heading]
        self.sound[DEAD] = sound[DEAD][self.heading]

        # collision rectangle
        self.rect = self.image[NORMAL].get_rect()  # player is represented by collision rectangle
        self.rect.height -= imgTopClearance  # remove whitespace at top of the image
        self.rect.width /= 2  # reduce the collision area
        if RIGHT == heading:
            self.rect.left = edgeClearance  # move away from the edge
            self.imgLeft = self.rect.left - self.rect.width / 4  # rect and image are in different positions
        else:
            assert LEFT == heading
            self.rect.right = WINDOWWIDTH - edgeClearance  # move away from the edge
            self.imgLeft = self.rect.left - self.rect.width + self.rect.width /4  # move image under the collision area

        #health bar
        self.healthBarObj = Bar(self.rect.left, self.rect.top, self.rect.width, 15)

        #focus var
        self.focusBarObj = Bar(10, self.rect.top +30, self.rect.width, 5)
        self.focusBarObj.color = WHITE
        self.focusBarObj.display = False

        self.scoreObj = Score(self)

        #debug aim line
        if RIGHT == heading:
            self.shootingLine = pygame.Rect(self.rect.right + imgSideToGun, 0, WINDOWWIDTH, 2)
        else:
            self.shootingLine = pygame.Rect(0, 0, WINDOWWIDTH - self.rect.width - edgeClearance - imgSideToGun, 2)

    def reset(self):
        # print("resetting ", self.name)
        # reset info
        self.health = self.baseHealth
        self.healthBarObj.update()  # each time health is updated this should be called
        self.ammo = self.baseAmmo
        # shield
        # focus
        self.focus = self.baseFocus
        # position
        self.rect.top = random.randint(0, WINDOWHEIGHT - self.rect.height)
        self.updateDependencies()

    def moveUp(self):
        self.rect.top -= self.speed
        self.checkPosition()
        self.updateDependencies()

    def moveDown(self):
        self.rect.top += self.speed
        self.checkPosition()
        self.updateDependencies()

    def updateDependencies(self):
        self.shootingLine.top = self.rect.top + imgTopToGun
        self.healthBarObj.setPosition(self.rect.top - imgHealthBarOffset)

    def updateState(self, newState = NORMAL):
        self.state = newState
        self.texture = self.image[newState]
        self.healthBarObj.update(float(self.health) /self.baseHealth *100)

    def drawBars(self):
        self.healthBarObj.draw()
        self.focusBarObj.draw()

    def update(self):# called each frame
        #increase health and focus
        if self.health < self.baseHealth:
            self.health += self.healthRecharge
            self.healthBarObj.update(float(self.health) /self.baseHealth *100)

        if self.focused :
            self.focus -= self.focusDrain
            self.focusBarObj.update(float(self.focus) /self.baseFocus *100)
            self.focusBarObj.display = True
        else:
            if self.focus < self.baseFocus:
                self.focus += self.focusRecharge
            self.focusBarObj.display = False

        #check animation state
        if self.fired > 0 and pygame.time.get_ticks() > self.fired + animationDelay:
            self.fired = 0
            self.updateState(NORMAL)
        if self.hit > 0 and pygame.time.get_ticks() > self.hit + animationDelay:
            self.hit = 0
            self.updateState(NORMAL)

    def checkPosition(self): # keep image in screen
        if self.rect.top < 0 : self.rect.top = 0
        if self.rect.top > (WINDOWHEIGHT - self.rect.height) : self.rect.top = (WINDOWHEIGHT - self.rect.height)

    def increaseScore(self):
        self.score += 1
        self.scoreObj.update(self.score)

    def drawAmmo(self): # draw bullets at the top of the screen
        for i in range(0, self.ammo):
            if RIGHT == self.heading:
                bulletRect = pygame.Rect(10+10*i, 10, Bullet.height, Bullet.width)
            else:
                bulletRect = pygame.Rect(WINDOWWIDTH-10-(10*i), 10, Bullet.height, Bullet.width)
            pygame.draw.rect(DISPLAYSURF, DRAWCOLOR, bulletRect)

    def fire(self):
        if self.ammo > 0:
            self.ammo -= 1
            self.fired = pygame.time.get_ticks()
            self.updateState(FIRED)
            Bullet(self.heading, self.rect)
            if Game.drawScene: self.sound[FIRE].play()
        else:
            # print(self.name, 'out of ammo')
            if Game.drawScene: self.sound[NOAMMO].play()

    def actHit(self, damage):
        if Game.drawScene: self.sound[HURT].play()
        self.health -= damage
        self.hit = pygame.time.get_ticks()
        self.updateState(HIT)

    def setEnemy(self):
        for aPlayer in Cowboy.objectList:
            if self.heading == aPlayer.heading :
                continue
            else:
                self.enemy = aPlayer

class Score():
    def __init__(self, parent):
        assert parent.heading in (LEFT, RIGHT)
        if RIGHT == parent.heading :
            self.position = WINDOWWIDTH /2 -100
        else:
            self.position = WINDOWWIDTH /2 +100
        self.surface, self.rect = makeText(str(parent.score), DRAWCOLOR, BGCOLOR, self.position, 10, True)

    def update(self, value):
        self.surface, self.rect = makeText(str(value), DRAWCOLOR, BGCOLOR, self.position, 10, True)

class Bar():
    def __init__(self, left, top, width, height):
        self.display = True
        self.rect = pygame.Rect(left, top, width, height)
        self.fillWidth = self.rect.width
        self.borderWidth = 2
        self.color = None
        self.dynamicColor = True
        self.update()

    def draw(self):
        if self.display:
            DISPLAYSURF.fill(self.color, (self.rect.left, self.rect.top, self.fillWidth, self.rect.height))
            pygame.draw.rect(DISPLAYSURF, World.drawColor, self.rect, self.borderWidth)

    def setPosition(self, newYPosition): # move bar to a new position
        self.rect.top = newYPosition

    def update(self, value = 100.):
        self.fillWidth = value *self.rect.width /100
        if self.dynamicColor:
            if value > 40:
                self.color = GREEN
            elif value > 20:
                self.color = ORANGE
            else:
                self.color = RED

class Carriage():
    objectList = []

    def __init__(self):
        # rectReduction = 50 # pixels to educe the collision rectangle from the image rectangle
        Carriage.objectList.append(self)
        self.debug = False
        self.speed = 0.5
        self.lastHit = -1000 # init as -1000 to start movement immediately
        self.waitHit = 1000
        self.texture = imgCarriage
        self.rect = imgCarriage.get_rect()
        # self.rect.inflate_ip(-rectReduction, 0) # position the collision rectangle in the middle of the image
        # move the image then place the rectangle at the same coordinates
        # instead of moving the rectangle and placing the image at the same place.
        # this results in a gradual entrance and exit from the screen area
        self.imgLeft = int((WINDOWWIDTH - self.texture.get_width()) / 2)
        self.imgTop = WINDOWHEIGHT
        self.rect.left = self.imgLeft #+ rectReduction / 2 # center the collision rectangle over the image

    def reset(self): # start at the bottom
        self.imgTop = WINDOWHEIGHT

    def moveUp(self):
        now = pygame.time.get_ticks()
        if now > self.lastHit +self.waitHit: # when hit, carriage stops in place for waitHit milliseconds
            self.imgTop -= self.speed
            self.rect.top = self.imgTop
            self.checkPosition()

    def checkPosition(self):
        if self.rect.top < -self.rect.height:
            self.rect.top = WINDOWHEIGHT
            self.imgTop = WINDOWHEIGHT

    def actHit(self):
        if Game.drawScene: random.choice(sound[HIT][CARRIAGE]).play()
        self.lastHit = pygame.time.get_ticks()
        self.shoot(random.choice([LEFT, RIGHT]))

    def shoot(self, heading):
        # self.fired = pygame.time.get_ticks()
        # self.updateState(FIRED)
        Bullet(heading, self.rect)
        # self.sound[FIRE].play()

class Obstacle():
    objectList = []

    def __init__(self, position = LEFT):
        Obstacle.objectList.append(self)
        self.debug = False
        self.position = position
        self.texture = imgObstacle
        self.rect = imgObstacle.get_rect()
        self.rect.top = random.randint(0, WINDOWHEIGHT - self.rect.height)
        self.rectPieces = []
        self.rectPiecesHit = []
        # obstacle is split in six parts, hitting one makes it disappear
        self.reset()

    def reset(self):
        if LEFT == self.position:
            # random between right position of left player to left position of carriage
            self.rect.left = random.randint(edgeClearance +Cowboy.objectList[0].rect.width +imgSideToGun, WINDOWWIDTH /2 -Carriage.objectList[0].texture.get_rect().width /2 -self.rect.width)
        else:
            assert RIGHT == self.position
            # random between right position of carriage to left position of right player
            self.rect.left = random.randint(WINDOWWIDTH /2 +Carriage.objectList[0].rect.width / 2, WINDOWWIDTH -edgeClearance -Carriage.objectList[0].texture.get_rect().width -imgSideToGun -self.rect.width)
        self.rectPieces = []
        self.rectPiecesHit = []
        for i in range(self.rect.top, self.rect.bottom -self.rect.height /3 , self.rect.height /3):
            self.rectPieces.append(pygame.Rect(self.rect.left, i, self.rect.width/2, self.rect.height/3 +1))
            self.rectPieces.append(pygame.Rect(self.rect.left +self.rect.width/2, i, self.rect.width/2, self.rect.height/3 +1))

class Bullet():
    objectList = []
    objectDict = {}
    objectDict[RIGHT] = []#bullets heading right
    objectDict[LEFT] = []
    width = 10
    height = 2
    damage = 1
    speed = 10

    def __init__(self, heading, player):
        Bullet.objectList.append(self)
        Bullet.objectDict[heading].append(self)
        if RIGHT == heading:
            self.rect = pygame.Rect(player.right + imgSideToGun, player.top + imgTopToGun, self.width, self.height)
            self.heading = 1
        else:
            assert LEFT == heading
            self.rect = pygame.Rect(player.left - imgSideToGun, player.top + imgTopToGun, self.width, self.height)
            self.heading = -1

    def updatePosition(self):
        self.rect.left += self.speed * self.heading

    def remove(self):
        for heading in Bullet.objectDict:
            for key, bullet in enumerate(Bullet.objectDict[heading]):
                if bullet == self:
                    Bullet.objectList.remove(bullet)
                    del Bullet.objectDict[heading][key]

    @staticmethod
    def cleanUp():
        for heading in Bullet.objectDict:
            for key, bullet in enumerate(Bullet.objectDict[heading]):
                if bullet.rect.right < 0 or bullet.rect.left > WINDOWWIDTH:
                    Bullet.objectList.remove(bullet)
                    del Bullet.objectDict[heading][key]

    @staticmethod
    def checkCollisions():
        for bullet in Bullet.objectList:
            # carriage
            if bullet.rect.colliderect(Carriage.objectList[0].rect):
                Carriage.objectList[0].actHit()
                bullet.remove()
                break
            # player
            for player in Cowboy.objectList:
                if bullet.rect.colliderect(player.rect):
                    player.actHit(bullet.damage)
                    bullet.remove()
                    break
            # obstacles
            for obstacle in Obstacle.objectList:
                if bullet.rect.colliderect(obstacle.rect):
                    obsHit = bullet.rect.collidelist(obstacle.rectPieces)
                    if -1 != obsHit and obsHit not in obstacle.rectPiecesHit:
                        obstacle.rectPiecesHit.append(obstacle.rectPieces[obsHit]) # mark piece as hit
                        del obstacle.rectPieces[obsHit] # remove the visible piece and its collision rectangle
                        if Game.drawScene: random.choice(sound[HIT][OBSTACLE]).play()
                        bullet.remove()
                        break

    @staticmethod
    def reset():
        Bullet.objectList = []
        Bullet.objectDict[LEFT] = []
        Bullet.objectDict[RIGHT] = []

class Sand():
    sandList = []
    def __init__(self, countParticles):
        # fill with sand
        for i in range(0, countParticles):
            sand_x = random.randint(0, WINDOWWIDTH)
            sand_y = random.randint(0, WINDOWHEIGHT)
            self.sandList.append( [sand_x, sand_y] )

class World():
    objectList = []
    gameNo = 0
    bgColor = BGCOLOR
    drawColor = DRAWCOLOR
    gameSpeed = FPS
    survivalMode = False

    def __init__(self, playerCount, AiLeft = None, AiRight = None):
        World.objectList.append(self)
        self.gameNo += 1
        self.saveScreen = False
        if Game.drawScene: Sand(150)
        # init players
        self.player1 = Cowboy(RIGHT)
        self.player1.name = "p left"
        self.player2 = Cowboy(LEFT)
        self.player2.name = "p right"

        #set enemy
        self.player1.setEnemy()
        self.player2.setEnemy()

        if 0 == playerCount:
            # run ai vs ai
            self.assignAi(AiLeft, self.player1)
            self.assignAi(AiRight, self.player2)

        if 1 == playerCount:
            # ai controls p2
            self.assignAi(AiRight, self.player2)
        if 2 == playerCount:
            # no ai
            pass
        if 3 == playerCount:
            # ai controls p1
            self.assignAi(AiLeft, self.player1)

        # set carriage
        self.carriage = Carriage()
        # init obstacles
        self.box1 = Obstacle(LEFT)
        # self.box1.debug = True
        self.box2 = Obstacle(RIGHT)
        # self.box2.debug = True

        # reset positions
        self.reset()

        #force one update on positions to set health bars at correct position
        self.player1.updateDependencies()
        self.player2.updateDependencies()

        print("p1 ",self.player1.controller)
        print("p2 ",self.player2.controller)

    @staticmethod
    def assignAi(Ai, player):
        if 0 == Ai:
            AiControl(player) # random
        if 1 == Ai:
            AiGreedy(player) # greedy
        if 2 == Ai:
            AiMirror(player) # mirror
        if 3 == Ai:
            AiSimple(player) # simple
        if 4 == Ai:
            AiLegacyBasic(player) # legacy basic
        if 5 == Ai:
            AiLegacyBasicReversed(player) # legacy basic reversed bullet list
        if 6 == Ai:
            AiLegacyAdvanced(player) # legacy advanced

    def control(self):
        ###CONTROL
        key = pygame.key.get_pressed()

        if self.player1.controller:# AI control
            self.player1.controller.update()
        else:##player control
            #continuous control
            if key[player1keys[UP]]: self.player1.moveUp()
            if key[player1keys[DOWN]]: self.player1.moveDown()
        if self.player2.controller:
            self.player2.controller.update()
        else:
            if key[player2keys[UP]]: self.player2.moveUp()
            if key[player2keys[DOWN]]: self.player2.moveDown()
        #discrete control (holding the key down results in just one action, release key and press again)
        for event in pygame.event.get():
            if QUIT == event.type:
                terminate()
            if KEYDOWN == event.type and K_ESCAPE == event.key:
                # terminate()
                main_menu()
            ##firing
            if not self.player1.controller and \
            KEYDOWN == event.type and\
            player1keys[FIRE] == event.key:
                self.player1.fire()
            if not self.player2.controller and\
            KEYDOWN == event.type and\
            player2keys[FIRE] == event.key:
                self.player2.fire()
            #screenshot
            if KEYDOWN == event.type and K_PRINT == event.key:
                self.saveScreen = True #save must take place after scene is drawn
            #debug
            if KEYDOWN == event.type and K_LSHIFT == event.key:
                if key[K_r]:
                    self.refill_ammo()  # secret

            #p1 focus
            if KEYDOWN == event.type and player1keys[FOCUS] == event.key and self.player1.focus >=self.player1.focusDrain:
                print('starting p1 focus')
                self.player1.focused = True
                self.focusOn()
                self.player1.speed = self.player1.speed *FPS / FPSFOCUS # fps drops, keep player speed normal
            if KEYUP == event.type and player1keys[FOCUS] == event.key or self.player1.focus <=5:
                print('stopping p1 focus')
                self.player1.focused = False
                self.focusOff()
                self.player1.speed = Cowboy.speed # get player speed back to normal
            #p2 focus
            if KEYDOWN == event.type and player2keys[FOCUS] == event.key and self.player2.focus >=self.player2.focusDrain:
                print('starting p2 focus')
                self.player2.focused = True
                self.focusOn()
                self.player2.speed = self.player2.speed *FPS / FPSFOCUS
            if KEYUP == event.type and player2keys[FOCUS] == event.key or self.player2.focus <=5:
                print('stopping p2 focus')
                self.focusOff()
                self.player2.speed = Cowboy.speed
                self.player2.focused = False

    def update(self):
        # world model
        self.checkState()
        self.checkAmmo()
        ###PHYSICS
        # advance carriage
        self.carriage.moveUp()
        # advance bullets and collision detection
        Bullet.cleanUp()
        for bullet in Bullet.objectList:
            bullet.updatePosition()
        Bullet.checkCollisions()
        self.player1.update()
        self.player2.update()

    def render(self):
        # draw frame
        DISPLAYSURF.fill(self.bgColor)

        #draw sand
        for sand in Sand.sandList:
            pygame.draw.line(DISPLAYSURF, self.drawColor, (sand[0], sand[1]), (sand[0], sand[1]) )

        # draw scene
        DISPLAYSURF.blit(self.carriage.texture, (self.carriage.imgLeft, self.carriage.imgTop))
        DISPLAYSURF.blit(self.box1.texture, (self.box1.rect.left, self.box1.rect.top))
        DISPLAYSURF.blit(self.box1.texture, (self.box2.rect.left, self.box2.rect.top))

        # draw broken pieces
        for piece in self.box1.rectPiecesHit:
            pygame.draw.rect(DISPLAYSURF, self.bgColor, piece)
        for piece in self.box2.rectPiecesHit:
            pygame.draw.rect(DISPLAYSURF, self.bgColor, piece)

        #draw live bullets
        for bullet in Bullet.objectList:
            pygame.draw.rect(DISPLAYSURF, self.drawColor, bullet.rect)

        #draw dead bullets
        self.player1.drawAmmo()
        self.player2.drawAmmo()

        #draw health and focus bars
        self.player1.drawBars()
        self.player2.drawBars()

        #draw score
        DISPLAYSURF.blit(self.player1.scoreObj.surface, self.player1.scoreObj.rect)
        DISPLAYSURF.blit(self.player2.scoreObj.surface, self.player2.scoreObj.rect)

        #draw players
        DISPLAYSURF.blit(self.player1.texture, (self.player1.imgLeft, self.player1.rect.top - imgTopClearance))
        DISPLAYSURF.blit(self.player2.texture, (self.player2.imgLeft, self.player2.rect.top - imgTopClearance))

        #debug draw collision rectangles
        ALPHASURF = DISPLAYSURF.convert_alpha()
        if self.carriage.debug:
            pygame.draw.rect(ALPHASURF, NBLUE, self.carriage.rect)
        for obj in Obstacle.objectList:
            if obj.debug:
                pygame.draw.rect(ALPHASURF, REDT, obj.rect)
        for obj in Cowboy.objectList:
            if obj.debug:
                pygame.draw.rect(ALPHASURF, REDT, obj.rect)
                pygame.draw.rect(ALPHASURF, REDT, obj.shootingLine)
        DISPLAYSURF.blit(ALPHASURF, (0, 0))

        pygame.display.update()

        if self.saveScreen:
            self.saveScreenShot()

    def saveScreenShot(self):
        if self.saveScreen:
            pygame.image.save(DISPLAYSURF, "screen" + str(pygame.time.get_ticks()) + ".png")
            self.saveScreen = False
            print('saved screen')

    def checkAmmo(self):
        # check ammo
        if 0 == self.player1.ammo and 0 == self.player2.ammo:
            self.refill_ammo()

    def refill_ammo(self):  # only called when both ammo lists are empty
        # print("reload")
        print("."),
        self.player1.ammo = self.player1.baseAmmo
        self.player2.ammo = self.player2.baseAmmo
        if Game.drawScene: sound[RELOAD].play()

    def reset(self , winner = None):
        """
        resets the whole world
        sending a winner Player object will only reset its enemy
        """
        # print ("."),
        print ("[" +str(self.gameNo) +"] " +str(self.player1.score) +" : " +str(self.player2.score))
        self.gameNo +=1
        # print "world reset"
        # refill health and ammo
        if winner:
            # print("reset: ", winner.enemy.name)
            winner.enemy.reset()
        else:
            # print("both players")
            self.player1.reset()
            self.player2.reset()
        # reset carriage
        self.carriage.reset()
        # stop bullets
        Bullet.reset()
        # refill obstacles
        self.box1.reset()
        self.box2.reset()

        # print("p1 ",self.player1.controller)
        # print("p2 ",self.player2.controller)

    def focusOn(self):
        self.gameSpeed = FPSFOCUS
        self.bgColor = BLACK
        self.drawColor = GREEN

    def focusOff(self):
        self.gameSpeed = FPS
        self.bgColor = SAND
        self.drawColor = BLACK

    def checkState(self):
        """
        check win condition and if needed reset game
        """
        resetGame = False
        winner = None
        if self.player1.health <= 0:
            # print("p1 out")
            self.player2.increaseScore()
            if self.survivalMode: winner = self.player2
            if Game.drawScene: self.player1.sound[DEAD].play()
            resetGame = True
        if self.player2.health <= 0:
            # print("p2 out")
            self.player1.increaseScore()
            if self.survivalMode: winner = self.player1
            if Game.drawScene: self.player2.sound[DEAD].play()
            resetGame = True
        if resetGame:
            if Game.drawScene: pygame.time.delay(1000)
            for _ in pygame.event.get():
                pass
            self.reset(winner)


class Game():
    showFPS = True
    drawScene = None
    def __init__(self, playerCount = 2, drawScene = True, AiLeft = None, AiRight = None, matches = 100):
        # init world
        Game.drawScene = drawScene
        world = World(playerCount, AiLeft, AiRight)

        frames = 0
        baseTime = pygame.time.get_ticks()
        while True:  # the main game loop
            if world.gameNo == matches:
                print ("[" +str(world.gameNo) +"] " +str(world.player1.score) +" : " +str(world.player2.score))
                print 10*"-"
                break

            if self.showFPS:
                nowTime = pygame.time.get_ticks()
                deltaTime = nowTime - baseTime
                if deltaTime >= 1000:
                    baseTime = nowTime
                    # print ("fps", frames)
                    frames = 0
                frames += 1
        # DISPLAYSURF.fill(world.bgColor) #something about ai debug, is this needed?

            ###CONTROL
            world.control()

            ###PHYSICS
            world.update()

            ###GRAPHICS
            if self.drawScene:
                world.render()
                fpsClock.tick(world.gameSpeed) # fast draw

class AiControl():
    """
    template for AI classes
    contains basic methods
    """
    debug = False
    player = None
    enemy = None
    # shootingLine = None #line where bullets will be shot from, if centerY is not enough
    def __init__(self, playerControlled):
        self.player = playerControlled
        self.enemy = playerControlled.enemy
        self.lastFired = 0
        playerControlled.controller = self
        # print("AI init: ", self.player.name)

    def update(self):# override this
        self.randomWalk()
        self.fireRandom()

    ####fire
    def inSight(self, targetObject, tolerance =0):
        """
        self center is inside target rect
        self targets object
        """
        # print ("target", targetObject.rect.bottom)
        # print ("player", self.player.rect.centery)
        if targetObject.rect.bottom + tolerance >= self.player.rect.centery >= targetObject.rect.top - tolerance:
            return True
        else:
            return False

    # to do : test full comparison

    def inSightFull(self, targetObject):
        """
        upper and lower bound comparison for collision
        """
        # print ("target", targetObject.rect.bottom)
        # print ("player", self.player.rect.centery)
        if self.player.rect.bottom > targetObject.rect.bottom > self.player.rect.top \
        or self.player.rect.bottom > targetObject.rect.top > self.player.rect.top \
        or targetObject.rect.bottom > self.player.rect.bottom > targetObject.rect.top \
        or targetObject.rect.bottom > self.player.rect.top > targetObject.rect.top :
            return True
        else:
            return False

    def inSightReversed(self, targetObject, tolerance =0):
        """
        target center is inside self rect
        object targets self
        """
        # print ("target", targetObject.rect.centery)
        # print ("player", self.player.rect.bottom, self.player.rect.top)
        if self.player.rect.bottom + tolerance >= targetObject.rect.centery >= self.player.rect.top - tolerance:
            return True
        else:
            return False

    # to do: test by overlap, time and compare
    def inSightByCollision(self, targetObject):
        copyTarget = copy.deepcopy(targetObject)
        copySelf = copy.deepcopy(self)

        #align both objects
        copySelf.rect.left = 0
        copyTarget.rect.left = 0
        if copySelf.rect.colliderect(copyTarget.rect):
            print("colliding")
            return True
        else:
            print("not colliding")
            return False


    def fireRandom(self, chancePerSecond = 1.):
        chance = random.randint(0, 100)
        chancePerFrame = chancePerSecond / World.gameSpeed
        if chance > 100 -chancePerFrame:
            self.player.fire()

    def fireByTime(self, waitTime =1000):
        now = pygame.time.get_ticks()
        if self.lastFired +waitTime < now:
            self.lastFired = now
            self.player.fire()

    def fireInSight(self, targetObj):
        if self.inSight(targetObj):
            self.player.fire()

    def fireInSightByTime(self, targetObject, time =1000):
        if self.inSight(targetObject):
            self.fireByTime(time)

    def fireInSightByChance(self, targetObject, chancePerFrame):
        if self.inSight(targetObject):
            chancePerSecond = chancePerFrame * World.gameSpeed
            self.fireRandom(chancePerSecond)

    ####move
    def randomWalk(self):
        chance = random.randint(0,10)
        if  1 > chance:
            self.player.moveUp()
        elif 9 > chance:
            pass
        else:
            self.player.moveDown()

    def seek(self, targetLine, toleranceMin = 1, toleranceMax = 1):
        """
        go to targetLine
        tolerance stops jerky movement, high tolerance 50+ makes moves in blocks
        tolerance simulates some wander behaviour
        """
        tolerance = random.randint(toleranceMin,toleranceMax)
        if int(self.player.rect.centery /tolerance) *tolerance < int(targetLine /tolerance) *tolerance:
            self.player.moveDown()
        elif int(self.player.rect.centery /tolerance) *tolerance > int(targetLine /tolerance) *tolerance: #int(targetLine.rect.centery /tolerance) *tolerance:
            self.player.moveUp()

    def follow(self, targetObject):
        """
        keep targetObject in shooting line
        """
        tolerance = (random.randint(0, int(targetObject.rect.height)))
        if self.player.rect.centery > targetObject.rect.bottom - tolerance:
            self.player.moveUp()
        if self.player.rect.centery < targetObject.rect.top + tolerance:
            self.player.moveDown()

    def avoid(self, targetObject):
        """
        when a bullet will hit self, flee
        """
        if self.inSightReversed(targetObject):
            self.flee(targetObject)

    def flee(self, targetObject):
        """
        run in the other half of the screen
        """
        if targetObject.rect.centery > WINDOWHEIGHT / 2:
            self.seek(0)
        else:
            self.seek(WINDOWHEIGHT)

class AiGreedy(AiControl):
    def update(self):
        self.seek(self.enemy.rect.centery)
        self.fireInSightByChance(self.enemy, 10)

class AiMirror(AiControl):
    def update(self):
        self.seek(self.enemy.rect.centery)
        if self.enemy.fired:
            self.fireByTime()
        else:
            self.fireRandom(0.0001)

class AiSimple(AiControl):
    def update(self):
        self.fireRandom(0.0001)
        # self.fireInSightByTime(self.enemy, 1000)
        if len(Bullet.objectDict[self.enemy.heading]) > 0:
            self.avoid(Bullet.objectDict[self.enemy.heading][0])
        else:
            self.seek(self.enemy.rect.centery)

class AiFSM(AiControl):
    def update(self):
        raise NotImplemented

class AiLegacyBasic(AiControl):
    """
    adapted from version 1.0
    a very simple FSM
    """
    debug = False
    def update(self):
        self.fireInSightByChance(self.enemy, 5)
        if len(Bullet.objectDict[self.enemy.heading]) > 0:
            self.basicAvoidBullets()
        else:
            if self.player.ammo > 0:
                self.seek(self.enemy.rect.centery)
            else:
                self.flee(self.enemy)

    def basicAvoidBullets(self):#easy
        enemyHeading = self.enemy.heading
        player = self.player
        # moves off bullet line as soon as bullet is detected, takes edge into account
        # does not take into account distance to bullet, firing two bullets one above half one below half generates a hit
        if self.debug: print("--> simple bullet avoidance")
        for bullet in Bullet.objectDict[enemyHeading]:
            if player.rect.top <= bullet.rect.centery <= player.rect.bottom:
                if self.debug:
                    print "*"*5
                    print("bottom:", player.rect.bottom)
                    print("higher limit:", WINDOWHEIGHT)
                    print("top:",player.rect.top)
                    print("lower limit:",0)
                    print("height:",player.rect.height / 2)
                    print("avoiding ",bullet.rect)
                # decide direction
                if bullet.rect.centery >= player.rect.top + player.rect.height / 2:#lower half
                    #print("lower half")
                    #world margin
                    if bullet.rect.centery <= player.rect.height:#0 being worldy bottom (up)
                        #print("#no room to move up")
                        player.moveDown()
                    else:
                        player.moveUp()
                elif bullet.rect.centery < player.rect.top + player.rect.height / 2:#higher half
                    #print("higher half")
                    if bullet.rect.centery >= WINDOWHEIGHT - player.rect.height:
                        #print("#no room to move down")
                        player.moveUp()
                    else:
                        player.moveDown()
                else: print("#######################rabbit")

class AiLegacyBasicReversed(AiLegacyBasic):
    """
    bullet checking order is reversed, closest bullet is taken into account
    """
    def basicAvoidBullets(self):#easy
        enemyHeading = self.enemy.heading
        player = self.player
        # moves off bullet line as soon as bullet is detected, takes edge into account
        # does not take into account distance to bullet, firing two bullets one above half one below half generates a hit
        if self.debug: print("--> simple bullet avoidance")
        for bullet in Bullet.objectDict[enemyHeading][::-1]: # run the bullet list backwards to avoid the simple trick of shooting second bullet and make ai dodge into the first
            if player.rect.top <= bullet.rect.centery <= player.rect.bottom:
                if self.debug:
                    print "*"*5
                    print("bottom:", player.rect.bottom)
                    print("higher limit:", WINDOWHEIGHT)
                    print("top:",player.rect.top)
                    print("lower limit:",0)
                    print("height:",player.rect.height / 2)
                    print("avoiding ",bullet.rect)
                # decide direction
                if bullet.rect.centery >= player.rect.top + player.rect.height / 2:#lower half
                    if self.debug: print("lower half")
                    #world margin
                    if bullet.rect.centery <= player.rect.height:#0 being worldy bottom (up)
                        if self.debug: print("#no room to move up")
                        player.moveDown()
                    else:
                        player.moveUp()
                elif bullet.rect.centery < player.rect.top + player.rect.height / 2:#higher half
                    if self.debug: print("higher half")
                    if bullet.rect.centery >= WINDOWHEIGHT - player.rect.height:
                        if self.debug: print("#no room to move down")
                        player.moveUp()
                    else:
                        player.moveDown()
                else: print("#######################rabbit")

class AiLegacyAdvanced(AiControl):
    """
    adapted from version 1.0
    a very simple FSM
    bullet avoidance is done at the very last moment (which is really frustrating for the player)
    """
    debug = False
    def update(self):
        self.fireInSightByChance(self.enemy, 5)
        if Bullet.objectDict[self.enemy.heading]:
            self.avoidBullets()
        else:
            if self.player.ammo > 0:
                self.seek(self.enemy.rect.centery)
            else:
                self.seek(Carriage.objectList[0].rect.centery)

    def avoidBullets(self):
        #dodges bullets at the last possible moment
        #shooting multiple bullets quickly will still go through
        if self.debug: print("--> bullet avoidance")
        if self.debug: print("targets", 'p1ammoFired')
        # player.Height-1 max distance
        # speedPlayer speed
        #t = d / v
        #speedBullet speed
        #d = v * t
        #avoids bullets at the last possible second, except when near margin when it doesn't work
        enemyHeading = self.enemy.heading
        player = self.player
        for bullet in Bullet.objectDict[enemyHeading]:
            if player.rect.bottom >= bullet.rect.centery >= player.rect.top:
                if self.debug:
                    print("bottom:", player.bottom)
                    print("higher limit:", WINDOWHEIGHT)
                    print("top:",player.top)
                    print("lower limit:",0)
                    print("height:",player.height / 2)
                onRight = onLeft = False
                #latest point when bullet can be dodged is on the right of the left player and vice versa
                if player.rect.centerx > bullet.rect.centerx:
                    onRight = True
                    goDown = player.rect.centerx - int(player.rect.width / 2) - int((bullet.rect.centery - player.rect.top) / player.speed * bullet.speed) - 2 * bullet.rect.width
                    goUp = player.rect.centerx - int(player.rect.width / 2) - int((player.rect.bottom - bullet.rect.centery) / player.speed * bullet.speed)- 2 * bullet.rect.width
                else:
                    onLeft = True
                    goDown = player.rect.centerx + int(player.rect.width / 2) + int((bullet.rect.centery - player.rect.top) / player.speed * bullet.speed) + 2 * bullet.rect.width
                    goUp = player.rect.centerx + int(player.rect.width / 2) + int((player.rect.bottom - bullet.rect.centery) / player.speed * bullet.speed)+ 2 * bullet.rect.width

                if self.debug:
                    pygame.draw.rect(DISPLAYSURF, RED, (goDown, bullet.rect.centery, 2, 20),2)
                    pygame.draw.rect(DISPLAYSURF, SKYBLUE, (goUp, bullet.rect.centery, 2, 20),2)
                    print("y avoiding ",bullet.rect.centery)
                #decide direction
                if  bullet.rect.centery <= player.rect.height :#upper border
                    if self.debug: print("x dodging at ",goDown, " now at ", bullet.rect.centerx)
                    if onRight and bullet.rect.centerx >= goDown or onLeft and bullet.rect.centerx <= goDown :
                        if self.debug: print("border - moving down")
                        player.moveDown()
                elif bullet.rect.centery >= WINDOWHEIGHT - player.rect.height :#lower border
                    if self.debug: print("x dodging at ", goUp, " now at ", bullet.rect.centerx)
                    if onRight and bullet.rect.centerx >= goUp or onLeft and bullet.rect.centerx <= goUp:
                        if self.debug: print("border - moving up")
                        player.moveUp()
                elif bullet.rect.centery <= player.rect.top + player.rect.height / 2:#upper half
                    if self.debug: print("x dodging at ",goDown, " now at ", bullet.rect.centerx)
                    if onRight and bullet.rect.centerx >= goDown or onLeft and bullet.rect.centerx <= goDown:
                        if self.debug: print("moving down")
                        player.moveDown()
                elif bullet.rect.centery > player.rect.top + player.rect.height / 2:#lower half
                    if self.debug: print("x dodging at ", goUp, " now at ", bullet.rect.centerx)
                    if onRight and bullet.rect.centerx >= goUp or onLeft and bullet.rect.centerx <= goUp:
                        if self.debug: print("moving up")
                        player.moveUp()
                else: print("#####################rabbit")#somehow no condition was valid, agent is sitting

# from Al Sweigart
def makeText(text, color, bgcolor, top, left, small = False, title = False):
    # create the Surface and Rect objects for some text.
    if title:
        textSurf = BIGFONT.render(text, True, color, bgcolor)
    elif small:
        textSurf = SMALLFONT.render(text, True, color, bgcolor)
    else:
        textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return textSurf, textRect

def terminate():
    pygame.quit()
    sys.exit()

def checkForQuit():
    for _ in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
# endfrom

def main_menu():
    global player1keys, player2keys
    colorNormal = GRAY
    colorSelected = RED
    leftAi = 0
    rightAi = 0
    leftAiColor = []
    rightAiColor = []
    for i in range(0,10):
        leftAiColor.append(colorNormal)
        rightAiColor.append(colorNormal)

    GAMESPEED = 20
    bigDistance = 40  # from top, including text size
    while True:
        checkForQuit()
        DISPLAYSURF.fill(BGCOLOR)
        # set text color based on current selection
        for i in range(0,10):
            rightAiColor[i] = colorNormal
            leftAiColor[i] = colorNormal

            rightAiColor[rightAi] = colorSelected
            leftAiColor[leftAi] = colorSelected

        title_SURF, title_RECT = makeText('High Noon', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 -130, 40, False, True)
        start1_SURF, start1_RECT = makeText('1 - SINGLEPLAYER', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 -100, WINDOWHEIGHT /2 -120)
        start2_SURF, start2_RECT = makeText('2 - PLAYER VS PLAYER', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 -100, start1_RECT.top + bigDistance)
        redef_SURF, redef_RECT = makeText('R - REDEFINE KEYS', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 -100, start2_RECT.top + bigDistance)  # not yet
        demo_SURF, demo_RECT = makeText('D - DEMO', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 -100, redef_RECT.top + bigDistance)
        quit_SURF, quit_RECT = makeText('EXIT', DRAWCOLOR, BGCOLOR, WINDOWWIDTH /2 -100, demo_RECT.top + bigDistance)
        small = True

        pl1_text_SURF, pl1_text_RECT = makeText('Player 1', DRAWCOLOR, BGCOLOR, 20, 20, small)
        pl1_up_SURF, pl1_up_RECT = makeText(pygame.key.name(player1keys[UP]) + ' - up', DRAWCOLOR, BGCOLOR, 20, 40, small)
        pl1_down_SURF, pl1_down_RECT = makeText(pygame.key.name(player1keys[DOWN]) + ' - down', DRAWCOLOR, BGCOLOR, 20, 60, small)
        pl1_fire_SURF, pl1_fire_RECT = makeText(pygame.key.name(player1keys[FIRE]) + ' - fire', DRAWCOLOR, BGCOLOR, 20, 80, small)
        pl1_focus_SURF, pl1_focus_RECT = makeText(pygame.key.name(player1keys[FOCUS]) + ' - focus', DRAWCOLOR, BGCOLOR, 20, 100, small)
        pl2_text_SURF, pl2_text_RECT = makeText('Player 2', DRAWCOLOR, BGCOLOR, WINDOWWIDTH - 100, 20, small)
        pl2_up_SURF, pl2_up_RECT = makeText(pygame.key.name(player2keys[UP]) + ' - up', DRAWCOLOR, BGCOLOR, WINDOWWIDTH -100, 40, small)
        pl2_down_SURF, pl2_down_RECT = makeText(pygame.key.name(player2keys[DOWN]) + ' - down', DRAWCOLOR, BGCOLOR, WINDOWWIDTH -100, 60, small)
        pl2_fire_SURF, pl2_fire_RECT = makeText(pygame.key.name(player2keys[FIRE]) + ' - fire', DRAWCOLOR, BGCOLOR, WINDOWWIDTH -100, 80, small)
        pl2_focus_SURF, pl2_focus_RECT = makeText(pygame.key.name(player2keys[FOCUS]) + ' - focus', DRAWCOLOR, BGCOLOR, WINDOWWIDTH -100, 100, small)
        madeby_SURF, madeby_RECT = makeText("remake by Cristian Calmuschi cristian.calmuschi@gmail.com", DRAWCOLOR, BGCOLOR, 50, WINDOWHEIGHT - 120, small)
        thanks0_SURF, thanks0_RECT = makeText("thanks to:", DRAWCOLOR, BGCOLOR, 50, WINDOWHEIGHT - 100, small)
        thanks1_SURF, thanks1_RECT = makeText("Al Sweigart for the book, the cat and the box images (http)", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT - 80, small)
        thanks2_SURF, thanks2_RECT = makeText("Zac Zidik for the cowboy http", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT -60, small)
        thanks3_SURF, thanks3_RECT = makeText("Analytic for Bfxr http", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT -40, small)
        clone_SURF, clone_RECT = makeText("inspired by Abbex Electronics' 1983 High Noon (http)", DRAWCOLOR, BGCOLOR, 70, WINDOWHEIGHT - 20, small)

        left_ai_SURF , left_ai_RECT  = makeText('Left Ai:', DRAWCOLOR, BGCOLOR, 20, 200, small)
        left_ai0_SURF, left_ai0_RECT = makeText('random', leftAiColor[0], BGCOLOR, left_ai_RECT.left , left_ai_RECT.top + 20, small)
        left_ai1_SURF, left_ai1_RECT = makeText('greedy', leftAiColor[1], BGCOLOR, left_ai_RECT.left, left_ai0_RECT.top + 20, small)
        left_ai2_SURF, left_ai2_RECT = makeText('mirror', leftAiColor[2], BGCOLOR, left_ai_RECT.left, left_ai1_RECT.top + 20, small)
        left_ai3_SURF, left_ai3_RECT = makeText('simple', leftAiColor[3], BGCOLOR, left_ai_RECT.left, left_ai2_RECT.top + 20, small)
        left_ai4_SURF, left_ai4_RECT = makeText('legacyBasic', leftAiColor[4], BGCOLOR, left_ai_RECT.left, left_ai3_RECT.top + 20, small)
        left_ai5_SURF, left_ai5_RECT = makeText('legacyBasicR', leftAiColor[5], BGCOLOR, left_ai_RECT.left, left_ai4_RECT.top + 20, small)
        left_ai6_SURF, left_ai6_RECT = makeText('legacyAdv', leftAiColor[6], BGCOLOR, left_ai_RECT.left, left_ai5_RECT.top + 20, small)

        right_ai_SURF , right_ai_RECT  = makeText('Right Ai:', DRAWCOLOR, BGCOLOR, WINDOWWIDTH -100, 200, small)
        right_ai0_SURF, right_ai0_RECT = makeText('random', rightAiColor[0], BGCOLOR, right_ai_RECT.left , right_ai_RECT.top + 20, small)
        right_ai1_SURF, right_ai1_RECT = makeText('greedy', rightAiColor[1], BGCOLOR, right_ai_RECT.left, right_ai0_RECT.top + 20, small)
        right_ai2_SURF, right_ai2_RECT = makeText('mirror', rightAiColor[2], BGCOLOR, right_ai_RECT.left, right_ai1_RECT.top + 20, small)
        right_ai3_SURF, right_ai3_RECT = makeText('simple', rightAiColor[3], BGCOLOR, right_ai_RECT.left, right_ai2_RECT.top + 20, small)
        right_ai4_SURF, right_ai4_RECT = makeText('legacyBasic', rightAiColor[4], BGCOLOR, right_ai_RECT.left, right_ai3_RECT.top + 20, small)
        right_ai5_SURF, right_ai5_RECT = makeText('legacyBasicR', rightAiColor[5], BGCOLOR, right_ai_RECT.left, right_ai4_RECT.top + 20, small)
        right_ai6_SURF, right_ai6_RECT = makeText('legacyAdv', rightAiColor[6], BGCOLOR, right_ai_RECT.left, right_ai5_RECT.top + 20, small)

        DISPLAYSURF.blit(left_ai_SURF , left_ai_RECT)
        DISPLAYSURF.blit(left_ai0_SURF, left_ai0_RECT)
        DISPLAYSURF.blit(left_ai1_SURF, left_ai1_RECT)
        DISPLAYSURF.blit(left_ai2_SURF, left_ai2_RECT)
        DISPLAYSURF.blit(left_ai3_SURF, left_ai3_RECT)
        DISPLAYSURF.blit(left_ai4_SURF, left_ai4_RECT)
        DISPLAYSURF.blit(left_ai5_SURF, left_ai5_RECT)
        DISPLAYSURF.blit(left_ai6_SURF, left_ai6_RECT)

        DISPLAYSURF.blit(right_ai_SURF , right_ai_RECT)
        DISPLAYSURF.blit(right_ai0_SURF, right_ai0_RECT)
        DISPLAYSURF.blit(right_ai1_SURF, right_ai1_RECT)
        DISPLAYSURF.blit(right_ai2_SURF, right_ai2_RECT)
        DISPLAYSURF.blit(right_ai3_SURF, right_ai3_RECT)
        DISPLAYSURF.blit(right_ai4_SURF, right_ai4_RECT)
        DISPLAYSURF.blit(right_ai5_SURF, right_ai5_RECT)
        DISPLAYSURF.blit(right_ai6_SURF, right_ai6_RECT)

        DISPLAYSURF.blit(title_SURF, title_RECT)
        DISPLAYSURF.blit(start1_SURF, start1_RECT)
        DISPLAYSURF.blit(start2_SURF, start2_RECT)
        DISPLAYSURF.blit(redef_SURF, redef_RECT)
        DISPLAYSURF.blit(demo_SURF, demo_RECT)
        DISPLAYSURF.blit(quit_SURF, quit_RECT)
        DISPLAYSURF.blit(pl1_text_SURF, pl1_text_RECT)
        DISPLAYSURF.blit(pl1_up_SURF, pl1_up_RECT)
        DISPLAYSURF.blit(pl1_down_SURF, pl1_down_RECT)
        DISPLAYSURF.blit(pl1_fire_SURF, pl1_fire_RECT)
        DISPLAYSURF.blit(pl1_focus_SURF, pl1_focus_RECT)
        DISPLAYSURF.blit(pl2_text_SURF, pl2_text_RECT)
        DISPLAYSURF.blit(pl2_up_SURF, pl2_up_RECT)
        DISPLAYSURF.blit(pl2_down_SURF, pl2_down_RECT)
        DISPLAYSURF.blit(pl2_fire_SURF, pl2_fire_RECT)
        DISPLAYSURF.blit(pl2_focus_SURF, pl2_focus_RECT)
        DISPLAYSURF.blit(madeby_SURF, madeby_RECT)
        DISPLAYSURF.blit(thanks0_SURF, thanks0_RECT)
        DISPLAYSURF.blit(thanks1_SURF, thanks1_RECT)
        DISPLAYSURF.blit(thanks2_SURF, thanks2_RECT)
        DISPLAYSURF.blit(thanks3_SURF, thanks3_RECT)
        DISPLAYSURF.blit(clone_SURF, clone_RECT)
        for event in pygame.event.get():  # event handling loop
            if MOUSEBUTTONDOWN == event.type:
                if start1_RECT.collidepoint(event.pos):
                    Game(1, True, None, rightAi)
                elif start2_RECT.collidepoint(event.pos):
                    Game(2)
                elif redef_RECT.collidepoint(event.pos):
                    redefine_keys()
                elif demo_RECT.collidepoint(event.pos):
                    Game(0, True, leftAi, rightAi)
                elif quit_RECT.collidepoint(event.pos):
                    terminate()
            if KEYDOWN == event.type:
                if K_1 == event.key:
                    Game(1, True, None, rightAi)
                elif K_2 == event.key:
                    Game(2)
                elif K_d == event.key:
                    Game(0, True, leftAi, rightAi)
                elif K_r == event.key:
                    redefine_keys()
            elif MOUSEBUTTONUP == event.type:
                mousex, mousey = event.pos  # syntactic sugar
                if pygame.Rect(left_ai0_RECT).collidepoint(mousex, mousey):
                    leftAi = 0
                elif pygame.Rect(left_ai1_RECT).collidepoint(mousex, mousey):
                    leftAi = 1
                elif pygame.Rect(left_ai2_RECT).collidepoint(mousex, mousey):
                    leftAi = 2
                elif pygame.Rect(left_ai3_RECT).collidepoint(mousex, mousey):
                    leftAi = 3
                elif pygame.Rect(left_ai4_RECT).collidepoint(mousex, mousey):
                    leftAi = 4
                elif pygame.Rect(left_ai5_RECT).collidepoint(mousex, mousey):
                    leftAi = 5
                elif pygame.Rect(left_ai6_RECT).collidepoint(mousex, mousey):
                    leftAi = 6

                
                if pygame.Rect(right_ai0_RECT).collidepoint(mousex, mousey):
                    rightAi = 0
                elif pygame.Rect(right_ai1_RECT).collidepoint(mousex, mousey):
                    rightAi = 1
                elif pygame.Rect(right_ai2_RECT).collidepoint(mousex, mousey):
                    rightAi = 2
                elif pygame.Rect(right_ai3_RECT).collidepoint(mousex, mousey):
                    rightAi = 3
                elif pygame.Rect(right_ai4_RECT).collidepoint(mousex, mousey):
                    rightAi = 4
                elif pygame.Rect(right_ai5_RECT).collidepoint(mousex, mousey):
                    rightAi = 5
                elif pygame.Rect(right_ai6_RECT).collidepoint(mousex, mousey):
                    rightAi = 6


                elif pygame.Rect(thanks1_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://inventwithpython.com/pygame/')
                elif pygame.Rect(thanks2_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://www.flagamengine.com/blog/')
                elif pygame.Rect(thanks3_RECT).collidepoint(mousex, mousey):
                    webbrowser.open('http://www.bfxr.net/')
                elif pygame.Rect(clone_RECT).collidepoint(mousex, mousey):
                    webbrowser.open(
                        'http://www.freevintagegames.com/SMSarcade/newarcade/spectrum/H/3/H/High%20Noon%201983Abbex%20Electronicsa.z80.php')

        pygame.display.update()
        fpsClock.tick(GAMESPEED)

def redefine_keys():
    global player1keys, player2keys
    player1keys = {}
    player2keys = {}
    GAMESPEED = 20
    bigDistance = 60
    while True:
        checkForQuit()
        DISPLAYSURF.fill(BGCOLOR)
        start1_SURF, start1_RECT = makeText('Player 1', DRAWCOLOR, BGCOLOR, WINDOWWIDTH / 2 - 170, WINDOWHEIGHT / 2 - 150)
        pl1_up_SURF, pl1_up_RECT = makeText('up', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start1_RECT.top + bigDistance)
        pl1_down_SURF, pl1_down_RECT = makeText('down', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start1_RECT.top + bigDistance)
        pl1_fire_SURF, pl1_fire_RECT = makeText('fire', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start1_RECT.top + bigDistance)
        pl1_focus_SURF, pl1_focus_RECT = makeText('focus', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start1_RECT.top + bigDistance)

        start2_SURF, start2_RECT = makeText('Player 2', DRAWCOLOR, BGCOLOR, WINDOWWIDTH / 2 - 170, WINDOWHEIGHT / 2 - 150)
        pl2_up_SURF, pl2_up_RECT = makeText('up', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start2_RECT.top + bigDistance)
        pl2_down_SURF, pl2_down_RECT = makeText('down', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start2_RECT.top + bigDistance)
        pl2_fire_SURF, pl2_fire_RECT = makeText('fire', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start2_RECT.top + bigDistance)
        pl2_focus_SURF, pl2_focus_RECT = makeText('focus', BLACK, BGCOLOR, WINDOWWIDTH / 2 - 170, start2_RECT.top + bigDistance)

        if not (UP in player1keys):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_up_SURF, pl1_up_RECT)
        elif not (DOWN in player1keys):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_down_SURF, pl1_down_RECT)
        elif not (FIRE in player1keys):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_fire_SURF, pl1_fire_RECT)
        elif not (FOCUS in player1keys):
            DISPLAYSURF.blit(start1_SURF, start1_RECT)
            DISPLAYSURF.blit(pl1_focus_SURF, pl1_focus_RECT)
        elif not (UP in player2keys):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_up_SURF, pl2_up_RECT)
        elif not (DOWN in player2keys):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_down_SURF, pl2_down_RECT)
        elif not (FIRE in player2keys):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_fire_SURF, pl2_fire_RECT)
        elif not (FOCUS in player2keys):
            DISPLAYSURF.blit(start2_SURF, start2_RECT)
            DISPLAYSURF.blit(pl2_focus_SURF, pl2_focus_RECT)

        for event in pygame.event.get():  # event handling loop
            if KEYDOWN == event.type and (K_ESCAPE != event.key):
                if not (UP in player1keys):
                    player1keys[UP] = event.key
                elif not (DOWN in player1keys):
                    player1keys[DOWN] = event.key
                elif not (FIRE in player1keys):
                    player1keys[FIRE] = event.key
                elif not (FOCUS in player1keys):
                    player1keys[FOCUS] = event.key
                elif not (UP in player2keys):
                    player2keys[UP] = event.key
                elif not (DOWN in player2keys):
                    player2keys[DOWN] = event.key
                elif not (FIRE in player2keys):
                    player2keys[FIRE] = event.key
                elif not (FOCUS in player2keys):
                    player2keys[FOCUS] = event.key
        print(player1keys, player2keys)
        if FOCUS in player2keys: main_menu()
        pygame.display.update()
        fpsClock.tick(GAMESPEED)

if __name__ == '__main__':
    main_menu()

    # Game(0, True, 0, 5)

    ### AI competition
    # for left in range(0, 7):
    #     for right in range(0, 7):
    #         print (left, right)
    #         Game(0, True, left, right, 5)