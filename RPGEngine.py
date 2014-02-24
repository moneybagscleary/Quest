"""2D RPG ENGINE by Christopher Cleary
----For overhead SNES style RPG game.
"""

import pygame, cPickle, random
from pygame.locals import *

class Background(pygame.sprite.Sprite):
    """
    Background by Christopher Cleary

    This module will create the background tiles and render them to the screen
    based on a 2d array, cameraArray[][], which will be a subset of the larger
    2d array, mapArray.  It will shift the position of each tile by the change
    in x and y + the move in x and y.  This will simulate a smooth transition
    between tile changes.  You must load files into the backTiles array, and each
    element should correspond to and integer in the mapArray (ie. the 0 element of
    in backTiles will be called by a 0 value in any of the mapArray rows and columns)

    ***This is setup for tiles that are 160px by 160px on a 1280x800 screen...

    Properties: __init__(self, startx, starty)
        backTiles[] - list containing tile filenames, each element corresponds
        mapArray[][] - 2d array of entire map, dimensions: 50 x 40
                        integers correspond to tiles in backTiles
        camArray[][] - 2d subset of entire map, dimensions: 7 x 10
        row - current row the camera should start at - CAN'T EXCEED 18
        col - current column the camera should start at - CAN'T EXCEED 30
        dx - the change in the x value of each tile
        dy - the change in the y value of each tile

    _____________
    ***METHODS***

        render (self, DISPLAY) - will draw each tile to it's corresponding spot on the screen
            PARAMETERS - DISPLAY - pass a pygame.display object

        changeCam(self, x, y) - will change the camera array based on changes to x and y
            PARAMETERS - x - movement in x value
                       - y - movement in y value
        load_tiles(self, files=[]) - load the tile images for faster performance
            PARAMETERS - files[] - list of tile image filenames
    """

    def __init__(self, startX, startY):
        """Initialize the background class, be sure to set you backTiles list!!!"""
        #initialize pygame so we can use it's features
        pygame.init()
        pygame.sprite.Sprite.__init__(self)
        self.backTiles = []
        #create the mapArray 40x25
        self.mapArray = [[0 for c in range(50)] for r in range(40)]
        self.load_array("data\mapArray.dat")
        #figure where we should start in the array
        self.row = startY / 160
        self.col = startX / 160
        #set the camArray based on row and col
        self.camArray = [[self.mapArray[(self.row+r)][(self.col+c)] for c in range(10)] for r in range(7)]
        #start with our changes in x and y = 0
        self.dx = 0
        self.dy = 0

    def render(self, DISPLAY):
        """Renders the current camArray referenced tile images to the DISPLAY"""
        #iterate through the camera array, placing tiles appropriately
        for i in range(7):
            for j in range(10):
                #set the current array element to the tile based in its image
                curTile = self.backTiles[self.camArray[i][j]]
                tileRect = curTile.get_rect()
                tileRect.topleft = [(((j-1)*160)+self.dx),(((i-1)*160)+self.dy)]
                DISPLAY.blit(curTile, (tileRect))
                
    def change_cam(self, x, y):
        """This moves the background according the x and y passed in"""
        #keep track of this change in x and y
        self.dx += x
        self.dy += y
        
        #if dx or dy >160 or <-160, they should be zero
        if (self.dx <= -160):
            self.dx = 0
            self.col += 1
        elif (self.dx >= 160):
            self.dx = 0
            self.col -= 1
        if (self.dy <= -160):
            self.dy = 0
            self.row += 1
        elif (self.dy >= 160):
            self.row -= 1
            self.dy = 0
            
        if self.row < 0:
            self.row = 0   #these limit where the camera array will be
        elif self.row > 30:
            self.row = 30
        if self.col < 0:
            self.col = 0    #these limit where the camera array will be
        elif self.col > 40:
            self.col = 40
        # change camera array appropriately
        self.camArray = [[self.mapArray[(self.row+r)][(self.col+c)] for c in range(10)] for r in range(7)]

    def load_tiles(self, files=[]):
        """Pre load all tile images for faster in-game performance"""
        #load all images for faster performance
        for f in files:
            self.backTiles.append(pygame.image.load(f))

    def save_array(self):
        """Save the map array"""
        myFile = open("data\mapArray.dat", "w")
        cPickle.dump(self.mapArray, myFile)
        myFile.close()

    def load_array(self, files):
        """Load the map array if it exists"""
        try:
            myFile = open(files, "r")
            self.mapArray = cPickle.load(myFile)
            myFile.close()
        except:
            print "FILE DOES NOT EXIST!"

class InputEvent:
    """this will act as a proxy for the pygame event object"""
    def __init__(self, key, down):
        self.key = key
        self.down = down
        self.up = not down

class InputManager(object):
    """
    InputManager
     ^-----code originally from http://www.nerdparadise.com/tech/python/pygame/joystickconfig/
             edited, and upgraded by Christopher Cleary

    This class object will allow input for Pygame games with either
    a joystick, if any are plugged in, or the keyboard.

    The class InputEvent(self, key, down) acts as a proxy to pygame's event object.
        ---it has three properties, key, down, and up
    
    PROPERTIES(of InputManager class):
       buttons[] - this list will store the names of each 'button' on the gamepad
       keyMap{} - this dictionary will store the names of each keyboard input
       keysPressed{} - this dictionary will store each buttons keypress state (boolean)
       joystickConfig{} - this dictionary will store the button configuration, you
                           can configure this dictionary however you choose through
                           a game menu...
       joystickName - will store the name of the joystick
       quitAttempt - boolean value used to handle a quit or exit with joystick or keyboard

    METHODS(of InputManager class):
        init_Joystick(self) - intializes the joystick state
    
        isPressed(self, button) - returns the state of the keyPressed[button] (boolean value)

        getEvents(self) - acts as a proxy for pygame.events, handling each keypress.
               ^*******  NOTE: This method MUST be called each frame or the
                                window will begin to lock up
                            
        configButton(self, button) - will configure the button pressed on the
           ^                         gampad to the element of the button list
           |                         that is passed as the parameter - button.
           *************************************************************************
           The following methods should not be called, they are used by configButton.
               isButtonUsed(self, buttonIndex)
               isHatUsed(self, hatIndex, axis, direction)
               isBallUsed(self, ballIndex, axis, direction)
               isAxisUsed(self, axisIndex, direction)        
    """

    def __init__(self):
        
        # initialize the current joystick
        numPads = pygame.joystick.get_count()
        if numPads > 0:
            self.init_Joystick()

        # HERE IS WHERE YOU WILL MAKE CHANGES BASED ON YOUR GAME NEEDS
        # The list is setup for a standard SNES or XBOX controller
        self.buttons = ["up", "down", "left", "right", "start", "select", "A", "B", "X", "Y", "L", "R"]

        # this dictionary will store the keypresses for the keyboard
        # make any changes you need here as well....
        self.keyMap = {
            K_UP : "up",
            K_DOWN : "down",
            K_LEFT : "left",
            K_RIGHT : "right",
            K_ESCAPE : "start",
            K_RETURN : "select",
            K_d : "A",
            K_f : "B",
            K_a : "X",
            K_s : "Y",
            K_q : "L",
            K_r : "R"
            }

        # this dictionary will store the info on that state of each button
        self.keysPressed = {}
        for button in self.buttons:
            self.keysPressed[button] = False

        # this is a dictionary of the joystick configuration.
        self.joystickConfig = {}

        # this boolean variable will hold the quit status
        self.quitAttempt = False

    # isPressed returns the current state of the button from the
    # string name of the list above
    def isPressed(self, button):
        return self.keysPressed[button]

    # this will run the pygame events and return a list of event proxies
    def getEvents(self):
        events = []
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.quitAttempt = True

            # this is where each keyboard event is checked
            if event.type == KEYDOWN or event.type == KEYUP:
                keyPress = event.type == KEYDOWN
                button = self.keyMap.get(event.key)
                if button != None:
                    events.append(InputEvent(button, keyPress))
                    self.keysPressed[button] = keyPress

            # this is where each configured button is checked...
            for button in self.buttons:
                config = self.joystickConfig.get(button)
                if config != None:
                    # if the button is configured to an actual button
                    if config[0] == "isButton":
                        pushed = self.joystick.get_button(config[1])
                        if pushed != self.keysPressed[button]:
                            events.append(InputEvent(button, pushed))
                            self.keysPressed[button] = pushed

                    # if the button is configured to a hat direction...
                    elif config[0] == "isHat":
                        status = self.joystick.get_hat(config[1])
                        if config[2] == "x":
                            amount = status[0]
                        else:
                            amount = status[1]
                        pushed = amount == config[3]
                        if pushed != self.keysPressed[button]:
                            events.append(InputEvent(button, pushed))
                            self.keysPressed[button] = pushed

                    # if the button is configured to a trackball direction
                    elif config[0] == "isBall":
                        status = self.joystick.get_ball(config[1])
                        if config[2] == "x":
                            amount = status[0]
                        else:
                            amount = status[1]
                        if config[3] == 1:
                            pushed = amount > 0.5
                        else:
                            pushed = amount < -0.5
                        if pushed != self.keysPressed[button]:
                            events.append(InputEvent(button,pushed))
                            self.keysPressed[button] = pushed

                    # if the button is configured to an axis direction
                    elif config[0] == "isAxis":
                        status = self.joystick.get_axis(config[1])
                        if config[2] == 1:
                            pushed = status > 0.5
                        else:
                            pushed = status < -0.5
                        if pushed != self.keysPressed[button]:
                            events.append(InputEvent(button, pushed))
                            self.keysPressed[button] = pushed

        return events
                        
    # the configButton method will set the currently pressed button
    # to the button designation passed as the "button" parameter.
    def configButton(self, button):
        js = self.joystick

        # check buttons for activity
        for buttonIndex in range(js.get_numbuttons()):
            pushed = js.get_button(buttonIndex)
            if pushed and not self.isButtonUsed(buttonIndex):
                self.joystickConfig[button] = ("isButton", buttonIndex)
                return True

        # check hats for activity
        # (hats are the basic direction pads)
        for hatIndex in range(js.get_numhats()):
            hatStatus = js.get_hat(hatIndex)
            if hatStatus[0] < -0.5 and not self.isHatUsed(hatIndex, "x", -1):
                self.joystickConfig[button] = ("isHat", hatIndex, "x", -1)
                return True
            elif hatStatus[0] > 0.5 and not self.isHatUsed(hatIndex, "x", 1):
                self.joystickConfig[button] = ("isHat", hatIndex, "x", 1)
                return True
            elif hatStatus[1] < -0.5 and not self.isHatUsed(hatIndex, "y", -1):
                self.joystickConfig[button] = ("isHat", hatIndex, "y", -1)
                return True
            elif hatStatus[1] > 0.5 and not self.isHatUsed(hatIndex, "y", 1):
                self.joystickConfig[button] = ("isHat", hatIndex, "y", 1)
                return True

        # check trackball for activity
        for ballIndex in range(js.get_numballs()):
            ballStatus = js.get_ball(ballIndex)
            if ballStatus[0] < -0.5 and not self.isBallUsed(ballIndex, "x", -1):
                self.joystickConfig[button] = ("isBall", ballIndex, "x", -1)
                return True
            elif ballStatus[0] > 0.5 and not self.isBallUsed(ballIndex, "x", 1):
                self.joystickConfig[button] = ("isBall", ballIndex, "x", 1)
                return True
            elif ballStatus[1] < -0.5 and not self.isBallUsed(ballIndex, "y", -1):
                self.joystickConfig[button] = ("isBall", ballIndex, "y", -1)
                return True
            elif ballStatus[1] > 0.5 and not self.isBallUsed(ballIndex, "y", 1):
                self.joystickConfig[button] = ("isBall", ballIndex, "y", 1)
                return True
            
        # check axes for axes for activity (that's plural of axis...)
        for axisIndex in range(js.get_numaxes()):
            axisStatus = js.get_axis(axisIndex)
            if axisStatus < -0.5 and not self.isAxisUsed(axisIndex, -1):
                self.joystickConfig[button] = ("isAxis", axisIndex, -1)
                return True
            elif axisStatus > 0.5 and not self.isAxisUsed(axisIndex, 1):
                self.joystickConfig[button] = ("isAxis", axisIndex, 1)
                return True
        return False

    def isButtonUsed(self, buttonIndex):
        for button in self.buttons:
            config = self.joystickConfig.get(button)
            if config != None and config[0] == "isButton" and config[1] == buttonIndex:
                return True
        return False

    def isHatUsed(self, hatIndex, axis, direction):
        for button in self.buttons:
            config = self.joystickConfig.get(button)
            if config != None and config[0] == "isHat":
                if config[1] == hatIndex and config[2] == axis and config[3] == direction:
                    return True
        return False

    def isBallUsed(self, ballIndex, axis, direction):
        for button in self.buttons:
            config = self.joystickConfig.get(button)
            if config != None and config[0] == "isBall":
                if config[1] == ballIndex and config[2] == axis and config[3] == direction:
                    return True
        return False

    def isAxisUsed(self, axisIndex, direction):
        for button in self.buttons:
            config = self.joystickConfig.get(button)
            if config != None and config[0] == "isAxis":
                if config[1] == axisIndex and config[2] == direction:
                    return True
        return False

    # set the joystick information
    # the joystick needs to be plugged in before calling this function
    def init_Joystick(self):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        self.joystick = joystick
        self.joystickName = joystick.get_name()

    # save the joystick configuration file
    def save_config(self):
        myFile = open("data\JoystickConfig.dat", "w")
        cPickle.dump(self.joystickConfig, myFile)
        myFile.close()

    # load the joystick configuration if it exists
    def load_config(self, DISPLAY):
        try:
            myFile = open("data\JoystickConfig.dat", "r")
            self.joystickConfig = cPickle.load(myFile)
            myFile.close()
        except:
            yPos = 350
            isConfig = False
            index = 0
            while not isConfig:
                isConfig = (index+1) >= len(self.buttons)
                myFont = pygame.font.Font(None, 32)
                button = self.buttons[index]
                text = myFont.render("Press the %s button..."%button, True, (255,255,255))
                textRect = text.get_rect()
                textRect.center = (150, yPos)
                DISPLAY.blit(text, textRect)
                pygame.display.update()
                self.getEvents()
                success = self.configButton(button)
                if success:
                    index +=1
                    yPos += 40
                    
            self.save_config()

class GameObjects(pygame.sprite.Sprite):
    """
    GameObjects by Christopher Cleary

    This module will store all the images and relative data (x-y position, type, etc)
    for all game objects (obstacles, deathtraps, items etc.) on a 2d RPG type game
    It will also render the images to the screen based on their position.

    Properties - __init__(self, files, startX, startY, ref, damage=0, isDeath=False, isItem=False)
    gameObject - the images to be loaded based on files passed in
    objectX - current x-position in relation to the entire map - bounds (0-6400)
    objectY - current y-position in relation to the entire map - bounds (-3200-800)
    isDeath - boolean, True if object can cause damage to player
    damageFactor - How much damage it can cause if touched
    isItem - boolean, True if object is something the player can pickup
    objRect - Rectangle around the image
    _____________
    ***METHODS***

    move(self, x, y) - moves the game object around the world
            PARAMETERS - x - how much should we change x by
                       - y - how much should we change y by
                   
    render(self, DISPLAY) - renders the current game object to the DISPLAY passed in
            PARAMETERS - DISPLAY - must be a pygame.display object
    """

    def __init__(self, files, startX, startY, damage=0, death=False, item=False, typeOf="none"):
        """This initializes the class for use"""
        pygame.init()
        # iterate through the files creating an array of images
        self.gameObject = pygame.image.load(files)
        self.objRect = self.gameObject.get_rect()
            
        # create this objects x and y position in the game
        self.objectX = startX
        self.objectY = startY

        # if it's not an obstacle then it's an item or deathtrap
        self.isDeath = death
        self.damageFactor = damage
        self.isItem = item
        self.typeOf = typeOf
        
    def move(self, x, y):
        """We need to be able to move the game objects around the world"""
        self.objectX += x
        self.objectY += y
        self.objRect.center = (self.objectX, self.objectY)
        
    def render(self, DISPLAY):
        """This will render the objects image to the DISPLAY passed in"""
        self.objRect.center = (self.objectX, self.objectY)
        DISPLAY.blit(self.gameObject, (self.objRect))


class RPG_Character(pygame.sprite.Sprite):
    """
    RPGCharacter  created by Christopher Cleary

    This module will be used as a parent class for any characters in an RPG
    type of game.  It will hold standard properties and methods that both
    player characters and enemy characters will need (ie. HP, strength, animation
    files, rendering to screen methods...etc.) RPGCharacter will inherit the
    pygame.sprite.Sprite module, so it can handle all the sprite features.
    (FOR 2D OVERHEAD RPG TYPE GAME)

    Properties: __init__(self, x, y, level=1, HP=1, strength=1, wisdom=1, defense=1, luck=1, crit=1, speed=1, gold=1, exp=1, direction="DOWN")
        x - Characters current x-position
        y - Characters current y-position
        level - Characters current level (will be used as a factor of other stats)
        curHP - Characters current health level (if <= 0 then the character is dead)
        totHP - Characters total health level (MAX HEALTH)
        strength - Characters ability to perform physical attacks
        wisdom - Characters ability to perform magic attacks 
        defense - Characters ability to defend attacks
        luck - Affects attacks(criticals), defense, and gold/items found
        criticalPerc - Characters percentage chance of a critical attack
        speed - An integer value of the characters speed (how quickly they move across the screen
        items{} - A dictionary of items the character currently holds
        gold - Integer containing number of gold the character holds
        exp - For player characters it will be experience gained,
            - For enemy characters it will be the value of experience the player will earn
        direction - Which way the character is facing
            - (For animation purposes, set to "UP","DOWN","LEFT", or "RIGHT")
        isAttacking - boolean determining whether character is in attack phase of is passive
        isCasting - boolean determing whether the character is in magic phase
        animUP[] - list of UP animation files....set these after creating an instance
        animDOWN[] - list of DOWN animation files....Set all animation files after creating
        animRIGHT[] - list of RIGHT animation files...YOU ONLY NEED TO DRAW RIGHT FACING FILES!!!
        animLEFT[] - use the pygame.transform.flip() method to flip right to left...
        animATTACK_UP[] - list of upward attack animations
        animATTACK_DOWN[] - list of downward attack animations
        animATTACK_RIGHT[] - list of right facing attack animations...ONLY CREATE THESE FILES!!!
        animATTACK_LEFT[] - use the pygame.transform.flip() method to flip right to left
        animMAGIC_UP[] - list of upward magic position...character only position...
        animMAGIC_DOWN[] - list of downward magic position...character only
        animMAGIC_RIGHT[] - list of right facing magic position...ONLY CREATE THESE FILES!!!
        animMAGIC_LEFT[] - use the pygame.transform.flip() method to flip right to left
        animDEAD[] - If we want the character to have a death animation, save the files here
        ***the following properties will be set by the set_image method***
        curImg - will be set to whatever we need it to be set to...
        charRect - the rectangle around the curImg, used for collision detection
        spellX - x location of a cast spell if there is one
        spellY - y location of a cast spell if there is one
        spellImg - current spell image
        curSpell - current spell selected for use
        spellImages[] - Images of the spells the character can cast
        spells[] - list of available spells
    _____________
    ***METHODS***

        render(self, DISPLAY) - will render the curImg to the pygame display passed as parameter DISPLAY
           PARAMETERS - DISPLAY - pass a pygame.display object

        set_image(self, image) - will change the curImg based on the image passed.
            - this will be used by the animate method.....
            PARAMETERS - image - pass an element of whatever animation list you need
    
        animate(self, pos) - will change the curImg based on the pos parameter
            PARAMETERS - pos - integer position of the element of each animation list

        attack(self, pos) - will change the curImg based on the pos parameter
            PARAMETERS - pos - integer position of the element of the attack animation list

        magic(self, pos) - will change the curImg based on the pos parameter
            PARAMETERS - pos - integer position of the element of the magic animation list

        move(self, dx, dy) - moves the charRect by x and y
            PARAMETERS - dx - the integer value you want to change the charRect's x position
                       - dy - the integer value you want to change the charRect's y position

        is_dead(self) - returns True if curHP <= 0

        load_images(self, typeOf, files=[]) - loads all images into lists for faster performance
            PARAMETERS - typeOf = "up", "down", "horizontal" - for right and left(we transform right in left)
                                  "attack-up", "attack-down", "attack-horizontal", "dead"
                                  "magic-up", "magic-down", "magic-horizontal" are all valid types...
                       - files[] - a list of filenames to be opened...PUT THESE IN ANIMATION ORDER FROM 0 to n                   
    """

    def __init__(self, x, y, level=1, HP=1, strength=1, wisdom=1, defense=1, luck=1, crit=1, speed=1, gold=1, exp=1, direction="DOWN"):
        """Initializes a new instance of RPG_Character. All values will bet set to 1 if none are passed"""
        # initialize the pygame sprite so we can draw images
        pygame.init()
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        # here we'll initialize the properties of this class, based on parameters passed into the initializer
        self.level = level
        self.curHP = HP
        self.totHP = HP
        self.strength = strength
        self.wisdom = wisdom
        self.defense = level + strength
        self.luck = luck
        self.criticalPerc = crit
        self.speed = speed
        self.items = {}
        self.gold = gold
        self.exp = exp
        self.direction = direction
        self.isAttacking = False
        self.isCasting = False
        self.spellX = x
        self.spellY = y
        self.spellDirection = "DOWN"
        self.spellImg = None
        self.spells = ["Heal", "Fireball"]
        self.spellImages = []
        self.spellRect = pygame.Rect(0,0,0,0)
        self.curSpell = "Heal"
        self.mpCost = 10
        
        # here we'll initialize the various animation lists
        self.animUP = []
        self.animDOWN = []
        self.animLEFT = []
        self.animRIGHT = []
        self.animATTACK_UP = []
        self.animATTACK_DOWN = []
        self.animATTACK_LEFT = []
        self.animATTACK_RIGHT = []
        self.animMAGIC_UP = []
        self.animMAGIC_DOWN = []
        self.animMAGIC_LEFT = []
        self.animMAGIC_RIGHT = []
        self.animDEAD = []

    def render(self, DISPLAY):
        """WARNING!!!: IMAGES MUST BE LOADED INTO LISTS, THEN SET_IMAGE, ANIMATE, ATTACK, or MAGIC SHOULD BE CALLED BEFORE RENDERING TO SCREEN!!!!"""
        #figure the percentage of the characters current hp relative the total hp
        if self.curHP > self.totHP: self.curHP = self.totHP
        if self.curHP < 0: self.curHP = 0
        HPperc = ((self.curHP*1.0) / self.totHP) * 100.0
        #draw a health meter above the character
        pygame.draw.rect(DISPLAY, (0,0,0), (self.charRect[0],(self.charRect.topleft[1]-25), 100, 20))
        pygame.draw.rect(DISPLAY, (255,0,0), (self.charRect[0],(self.charRect.topleft[1]-25), HPperc, 20))
        pygame.draw.rect(DISPLAY, (255,255,255), (self.charRect[0],(self.charRect.topleft[1]-25), 100, 20), 3)
        # render the curImg to the DISPLAY passed in
        DISPLAY.blit(self.curImg, (self.charRect))
        if self.isCasting and self.spellImg != None:
            self.spellImg = self.spellImages[self.spells.index(self.curSpell)]
            self.spellRect = self.spellImg.get_rect()
            self.spellRect.center = (self.spellX, self.spellY)
            DISPLAY.blit(self.spellImg, (self.spellX, self.spellY))
        
    def set_image(self, image):
        """Pass an image file name through the image parameter to set the curImg.
            You can call this method to set the image manually, or use the
            animate method to step through each animation file in the lists
        """
        # set the curImg and charRect accordingly
        self.curImg = image
        self.charRect = self.curImg.get_rect()
        self.charRect.centerx = self.x
        self.charRect.centery = self.y
        
    def animate(self, pos):
        """Sets the curImg based on the direction the character is facing and position of relative animation list"""
        if self.direction == "UP":
            self.set_image(self.animUP[pos])
        elif self.direction == "DOWN":
            self.set_image(self.animDOWN[pos])
        elif self.direction == "LEFT":
            self.set_image(self.animLEFT[pos])
        elif self.direction == "RIGHT":
            self.set_image(self.animRIGHT[pos])
            
    def attack(self, pos):
        """Sets the curImg based on the direction of the character and position of the attack animation list"""
        if self.direction == "UP":
            self.set_image(self.animATTACK_UP[pos])
        elif self.direction == "DOWN":
            self.set_image(self.animATTACK_DOWN[pos])
        elif self.direction == "LEFT":
            self.set_image(self.animATTACK_LEFT[pos])
        elif self.direction == "RIGHT":
            self.set_image(self.animATTACK_RIGHT[pos])
        
    def magic(self, pos):
        """Sets the curImg based on the direction of the character and position of the magic animation list"""
        if self.direction == "UP":
            self.set_image(self.animMAGIC_UP[pos])
        elif self.direction == "DOWN":
            self.set_image(self.animMAGIC_DOWN[pos])
        elif self.direction == "LEFT":
            self.set_image(self.animMAGIC_LEFT[pos])
        elif self.direction == "RIGHT":
            self.set_image(self.animMAGIC_RIGHT[pos])
        
    def move(self, dx, dy):
        """This method should be called AFTER set_image or animate/attack/magic have been called
            it will move the sprite's centerx by x and centery by y
        """
        self.x += dx
        self.y -= dy
        
    def is_dead(self):
        """This method will return True if curHP is at or below 0"""
        return self.curHP <= 0

    def load_images(self, typeOf, files=[]):
        """This method allows us to load images into the various lists"""
        for f in files:
            image = pygame.image.load(f)
            if typeOf.lower() == "up":
                #up facing images
                self.animUP.append(image)
            elif typeOf.lower() == "down":
                #down facing images
                self.animDOWN.append(image)
            elif typeOf.lower() == "horizontal":
                #left and right images....we'll flip one to the other!
                self.animRIGHT.append(image)
                self.animLEFT.append(pygame.transform.flip(image,True,False))
            elif typeOf.lower() == "attack-up":
                #load all attack images here
                self.animATTACK_UP.append(image)
            elif typeOf.lower() == "attack-down":
                #load all attack images here
                self.animATTACK_DOWN.append(image)
            elif typeOf.lower() == "attack-horizontal":
                #load all attack images here
                self.animATTACK_RIGHT.append(image)
                self.animATTACK_LEFT.append(pygame.transform.flip(image,True,False))
            elif typeOf.lower() == "magic-up":
                #load all magic images here
                self.animMAGIC_UP.append(image)
            elif typeOf.lower() == "magic-down":
                #load all magic images here
                self.animMAGIC_DOWN.append(image)
            elif typeOf.lower() == "magic-horizontal":
                #load all magic images here
                self.animMAGIC_RIGHT.append(image)
                self.animMAGIC_LEFT.append(pygame.transform.flip(image,True,False))
            elif typeOf.lower() == "dead":
                #death animations...lol
                self.animDEAD.append(image)

class Enemy(RPG_Character):
    """
    Enemy  created by Christopher Cleary

    This module will handle all the enemies in my overhead 2d RPG game. It will
    inherit all the properties and methods of the RPGCharacter module, and will
    add some new properties and methods needed by the enemies only.

    Properties: __init__(self, x, y, level=1, HP=1, strength=1, wisdom=1, defense=1, luck=1, crit=1, speed=1, gold=1, exp=1, direction="DOWN", awareness=1, motionType=1)
        RPG_Character.__init__(self,.....everything above)
        awareness - the enemies ability to detect the player...used in detectPlayer method
        motionType - integer determining what type of motion the enemy follows
        movements - keeps track of each movement performed (just a counter)
    _____________
    ***METHODS***
        detect_player(self, playerRect) - will detect if the player is near the enemy
                - Then the enemy will "attack" the player...
            PARAMETERS - playerRect - a rectangle onject relating to the player image

        determine_motion(self) - will move the enemy based on their motionType
    """
    def __init__(self, x, y, level=1, HP=1, strength=1, wisdom=1, defense=1, luck=1, crit=1, speed=1, gold=1, exp=1, direction="DOWN", awareness=1, motionType=1):
        """Initialize the enemy class"""
        RPG_Character.__init__(self, x, y, level, HP, strength, wisdom, defense, luck, crit, speed, gold, exp, direction="DOWN")

        # initialize properties
        self.awareness = awareness
        self.motionType = motionType
        self.movements = 0

    def detect_player(self, playerRect, testRect):
        """Will check to see if enemy is within range of players."""
        #create a larger rectangle centered where the player is
        testRect.inflate_ip((10*self.awareness), (10*self.awareness))
        #if the enemy is withing this bounds
        if (self.charRect.colliderect(testRect)):
            if ((playerRect.centery) >= (self.charRect.centery)):
                #move down towards the player
                self.direction = "DOWN"
                if (self.charRect.colliderect(playerRect)):
                    self.move(0,-self.speed)
            else:
                #move up towards the player
                self.direction = "UP"
                if (self.charRect.colliderect(playerRect)):
                    self.move(0,self.speed)
            if ((playerRect.centerx) >= (self.charRect.centerx)):
                if (playerRect.centery <= (self.charRect.centery + 200)) and (playerRect.centery >= (self.charRect.centery - 200)):
                    if (playerRect.centerx <= self.charRect.centerx + 100) and (playerRect.centerx >= self.charRect.centerx - 100):
                        pass
                    else:
                        # only face right when within certain x-y coordinates
                        self.direction = "RIGHT"
                if (self.charRect.colliderect(playerRect)):
                    self.move(self.speed, 0)
            else:
                if (playerRect.centery <= (self.charRect.centery + 200)) and (playerRect.centery >= (self.charRect.centery - 200)):
                    if (playerRect.centerx <= self.charRect.centerx + 50) and (playerRect.centerx >= self.charRect.centerx - 50):
                        pass
                    else:
                        #only face left when within certain x-y coordinates
                        self.direction = "LEFT"
                if (self.charRect.colliderect(playerRect)):
                    self.move(-self.speed,0)
                    
    def determine_motion(self):
        """Will move the enemy based on the motiotype"""
        if (self.motionType == 1):
            self.movements +=1
            # move the enemy based on their current direction
            if self.direction == "UP" and self.movements < 35:
                self.move(0,self.speed)
            elif self.direction == "DOWN" and self.movements < 35:
                self.move(0,-self.speed)
            elif self.direction == "RIGHT" and self.movements < 35:
                self.move(self.speed,0)
            elif self.direction == "LEFT" and self.movements < 35:
                self.move(-self.speed,0)
            # this will pause the enemy before changing directions randomly
            if self.movements > 50:
                self.movements = 0
                newDir = (random.randint(25,124))/25
                # insure that the enemy moves in different direction.
                if newDir == 1 and self.direction != "UP":
                    self.direction = "UP"
                if newDir == 1 and self.direction == "UP":
                    self.direction = "DOWN"
                if newDir == 2 and self.direction != "DOWN":
                    self.direction = "DOWN"
                if newDir == 2 and self.direction == "DOWN":
                    self.direction = "UP"
                if newDir == 3 and self.direction != "LEFT":
                    self.direction = "LEFT"
                if newDir == 3 and self.direction == "LEFT":
                    self.direction = "RIGHT"
                if newDir == 4 and self.direction != "RIGHT":
                    self.direction = "RIGHT"
                if newDir == 4 and self.direction == "RIGHT":
                    self.direction = "LEFT"
                
class Player(RPG_Character):
    """
    Player  created by Christopher Cleary

    This module will inherit the properties and methods of RPGCharacter
    and will add more properties and methods that are specific to the
    player character.

    Properties: __init__(self, x, y, level=1, HP=1, strength=1, wisdom=1, defense=1, luck=1, crit=1, speed=1, gold=1, exp=1, direction="DOWN")
        RPG_Character.__init__(self,.....everything above)
        nextLev - the value of experience needed to levelup
        levelUp - boolean, True while exp > nextLev...

    _____________
    ***METHODS***

        update_stats(self): updates stats the the user can't change
    """

    def __init__(self, x, y, level=1, HP=1, strength=1, wisdom=1, defense=1, luck=1, crit=1, speed=1, gold=0, exp=0, direction="DOWN"):
        """Initialize the player for an overhead 2d RPG game"""
        RPG_Character.__init__(self, x, y, level, HP, strength, wisdom, defense, luck, crit, speed, gold, exp, direction="DOWN")

        #add some new properties for a player
        self.nextLevel = self.exp + ((level * (100 + self.strength + self.wisdom)) + (HP*self.level))
        self.levelUp = False
        self.totMP = wisdom * 10
        self.curMP = self.totMP
        self.interact = False
        
    def updateStats(self):
        """Updates stats that the user can't"""
        self.level += 1
        self.totHP += 100
        self.curHP = self.totHP
        self.defense = self.level + self.strength
        self.nextLevel = self.exp + ((self.level * (100 + self.strength + self.wisdom)) + (self.totHP*self.level))
        self.totMP = self.wisdom * 10
        self.curMP = self.totMP
