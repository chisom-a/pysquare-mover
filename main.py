# Copyright 2025 Chisom Anaemeribe
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pygame, random, schedule
from pygame.locals import *

BKG_COLOR = (188, 230, 170) # Color: #BCE6AA (Green Thumb)

TEXT_COLOR = (0, 0, 128) # Color: Blue
TEXT_BKG_COLOR = None

SCORE_TEXT_COLOR = (255, 255, 255) # Color: White
SCORE_TEXT_BKG_COLOR = (0, 0, 128) # Color: Blue

ENEMY_COLOR = (255, 0, 0) # Color: Red
PLAYER_COLOR = (0, 0, 255) # Color: Dark Blue

# Window's resolution
WINDOW_X = 600
WINDOW_Y = 600

TITLE = 'PySquare Mover'

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
# Orginated from https://www.pygame.org/wiki/TextWrap
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top
    lineSpacing = -1

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            #image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

# Initialize Pygame
pygame.init()

# Loads the game's icon and window's title
try:
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
except (FileNotFoundError):
    pass
pygame.display.set_caption(TITLE)


# Set up the game window
screen = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
screen.fill(BKG_COLOR)

# Set up a font object to render the text on screen
try:
    font = pygame.font.Font('font/PressStart2P-Regular.ttf', 16)
    titleFont = pygame.font.Font('font/PressStart2P-Regular.ttf', 40)
except (FileNotFoundError):
    font = pygame.font.SysFont('freesansbold', 32)
    titleFont = pygame.font.SysFont('freesansbold', 50)

# Show the title screen with the instructions
titleText = titleFont.render(TITLE, True, TEXT_COLOR, TEXT_BKG_COLOR)
titleTextRect = titleText.get_rect()
titleTextRect.centerx = (screen.get_width() // 2)
titleTextRect.top = 5
screen.blit(titleText, titleTextRect)

instructions = 'Move the blue suqare with your cursor to avoid the falling red squares and increase your score.' \
' But watch out! The game gets only difficult as the score increases!'
instructionTextRect = Rect(250, 100, 500, 120)
instructionTextRect.centerx = (screen.get_width() // 2)
instructionTextRect.top = (150)
drawText(screen, instructions, TEXT_COLOR, instructionTextRect, font, False, TEXT_BKG_COLOR)

startText = font.render('Click the window to start!', True, TEXT_COLOR, TEXT_BKG_COLOR)
startTextRect = startText.get_rect()
startTextRect.centerx = (screen.get_width() // 2)
startTextRect.top = (300)
screen.blit(startText, startTextRect)

pygame.display.update()

running = True
while running:
    # Checks if the window closes and ends the program if so
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            running = False
        
        if event.type == pygame.QUIT:
            # Quit Pygame
            pygame.quit()
            exit()

# Set up the game's clock for managing fps
clock = pygame.time.Clock()

# Score counter
score = 0

# Set up the score counter to be shown on screen
scoreText = font.render('Score: ' + str(score), True, SCORE_TEXT_COLOR, SCORE_TEXT_BKG_COLOR)
scoreTextRect = scoreText.get_rect()
scoreTextRect.left = 0
scoreTextRect.bottom = 600

squareSize = 40 # Size of the player's square and enemy's squares
movingSpeed = 0.04 # Moving speed of the other squares (in seconds)

# List of enemy rectangles that will appear on screen
enemyRect = [Rect(random.randint(0, (WINDOW_X - squareSize)), 0, squareSize, squareSize),
             Rect(random.randint(0, (WINDOW_X - squareSize)), 50, squareSize, squareSize),
             Rect(random.randint(0, (WINDOW_X - squareSize)), 100, squareSize, squareSize),
             Rect(random.randint(0, (WINDOW_X - squareSize)), 100, squareSize, squareSize)]


def updateScore():
    # Updates the score
    global score, scoreText, enemyRect, movingSpeed, updateRectsJob
    score = score + 1
    scoreText = font.render('Score: ' + str(score), True, SCORE_TEXT_COLOR, SCORE_TEXT_BKG_COLOR)
    
    # Add a new enemy square every time the score increases by 10 up until the score reaches 200
    if score <= 200 and score % 10 == 0:
        enemyRect.append(Rect(random.randint(0, (WINDOW_X - squareSize)), -squareSize, squareSize, squareSize))
    
    # After the score reaches 200, the moving speed of the enemy squares increases
    # every time the score increases by 50 up until the score reaches 400
    elif score > 200 and score <= 400 and score % 50 == 0:
        movingSpeed = movingSpeed - 0.005
        updateRectsJob.interval = movingSpeed
        
# Function to move the enemy sqaures down. If an enemy square reaches the bottom of the window,
# the sqaure loops back to the top. 
def updateRects():
    global enemyRect
    for rect in enemyRect:
        pygame.Rect.move_ip(rect, 0, 10)
        if rect[1] > WINDOW_Y:
            pygame.Rect.update(rect, random.randint(0, (WINDOW_X - squareSize)), -squareSize, squareSize, squareSize)

# These schedule jobs run the updateScore & updateRects functions at a certain rate
updateScoreJob = schedule.every(0.5).seconds.do(updateScore)
updateRectsJob = schedule.every(movingSpeed).seconds.do(updateRects)

# Game loop
running = True
while running:
    schedule.run_pending()

    # Limits the FPS to 240fps max
    clock.tick(240)
    
    # Gets the cursor x- & y-coordinates and sets the center of the 
    # player's square to it
    mousePos = pygame.mouse.get_pos()
    playerRect = Rect(mousePos[0] - (squareSize // 2), mousePos[1] - (squareSize // 2), 
                      squareSize, squareSize)

    # Resets the screen
    screen.fill(BKG_COLOR)
    
    # Checks if the player's square collides with any enemy squares and ends the game if so
    collidedRectIndex = pygame.Rect.collidelist(playerRect, enemyRect)
    if collidedRectIndex > -1:
        schedule.cancel_job(updateScoreJob)
        schedule.cancel_job(updateRectsJob)
        running = False
    
    
    # Draws the squares into the screen
    for rect in enemyRect:
        pygame.draw.rect(screen, ENEMY_COLOR, rect, 0)
    pygame.draw.rect(screen, PLAYER_COLOR, playerRect, 0)
    
    # Draws the score into the screen
    screen.blit(scoreText, scoreTextRect)

    # Updates the screen with the updated graphics
    pygame.display.update()

    # Checks if the window closes and ends the program if so
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit Pygame
            pygame.quit()
            exit()

    # print("FPS: " + str(clock.get_fps())) <--- For Debug Purposes (Can enable if you want FPS in terminal)

# Shows the game over screen with the score
gameOverScreen = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
gameOverScreen.fill(BKG_COLOR)

gameOverText = titleFont.render('Game Over!', True, TEXT_COLOR, TEXT_BKG_COLOR)
gameOverTextRect = gameOverText.get_rect()
gameOverTextRect.centerx = (gameOverScreen.get_width() // 2)
gameOverTextRect.top = 5
gameOverScreen.blit(gameOverText, gameOverTextRect)

finalScoreText = font.render('Score: ' + str(score), True, TEXT_COLOR, TEXT_BKG_COLOR)
finalScoreTextRect = finalScoreText.get_rect()
finalScoreTextRect.center = ((gameOverScreen.get_width() // 2, gameOverScreen.get_height() // 2))
gameOverScreen.blit(finalScoreText, finalScoreTextRect)

pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit Pygame
            running = False

pygame.quit()

exit()
