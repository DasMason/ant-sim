import math, pygame
from pygame.locals import *
from pygame.math import Vector2
import random, time

pygame.init()

fps = 60
clock = pygame.time.Clock()

# Variables
antAmt = 50
antSpeed = 2
olfactionSize = 50
antC = (0,0,0)
antCWF = (255, 0, 0)
numFood = 20
foodRadius = 7.5
screensize = (1000, 1000)
antsize = (50,50)
nestRadius = 15
nestposition = (500, 500)
screen = pygame.display.set_mode(screensize)
font = pygame.font.SysFont(None, 55)

# Restart Button
button = pygame.Rect(450, 450, 100, 50)
button_color = (0, 255, 0)

foodpiles = []
ants = []

class Ant:
    def __init__(self, x, y, speed, olfaction):
        self.x = x
        self.y = y
        self.speed = speed
        self.olfaction = olfaction
        self.hasFood = False
        self.scent_trail = None
        angle = random.uniform(0, 2 * math.pi)
        self.direction = Vector2(math.cos(angle), math.sin(angle))
        self.id = id(self)

    def update(self, scents, removable_scents):
        if not self.hasFood:
            self.check_overlap(scents, removable_scents)
        self.move()
        self.checkForFood()
        self.checkNest()

    def move(self):
        turn_rate = random.uniform(-0.1, 0.1) 
        angle = math.atan2(self.direction.y, self.direction.x) + turn_rate
        self.direction = Vector2(math.cos(angle), math.sin(angle)).normalize()
        
        self.x += self.direction.x * self.speed
        self.y += self.direction.y * self.speed

        if self.hasFood: 
            nestPos = Vector2(nestposition) 
            antPos = Vector2(self.x, self.y) 
            self.direction = (nestPos - antPos).normalize()

        if self.x <= 0 or self.x >= 1000:
            self.direction.x *= -1 * random.uniform(0.8, 1.2)
        self.x = max(0, min(self.x, screensize[0]))

        if self.y <= 0 or self.y >= 1000:
            self.direction.y *= -1 * random.uniform(0.8, 1.2)
        self.y = max(0, min(self.y, screensize[1]))

        if self.hasFood:
            self.createScent()
    
    def check_overlap(self, scents, removable_scents):
        antpos = Vector2(self.x, self.y)
        for scent in scents:
            scentPos = Vector2(scent['x'], scent['y'])
            if antpos.distance_to(scentPos) < 5:
                if scent['antId'] != self.id:
                    removable_scents.append(scent)
                    self.direction = Vector2(-scent['direction'].x, -scent['direction'].y).normalize()
                    return
        self.random_move()

    def random_move(self):
        angle_change = random.uniform(-0.3, 0.3)
        current_angle = math.atan2(self.direction.y, self.direction.x)
        new_angle = current_angle + angle_change
        self.direction = Vector2(math.cos(new_angle), math.sin(new_angle)).normalize()

    def createScent(self):
        self.scent_trail = {
            'x': self.x,
            'y': self.y,
            'time': time.time(),
            'antId': self.id,
            'direction': self.direction.copy()
        }

    def checkForFood(self):
        if not self.hasFood:
            antPos = Vector2(self.x, self.y)
            for food in foodpiles:
                foodPos = Vector2(food.x, food.y)
                if antPos.distance_to(foodPos) < foodRadius:
                    self.hasFood = True
                    foodpiles.remove(food)

                    nestPos = Vector2(nestposition)
                    self.direction = (nestPos - antPos).normalize()
                    break

    def checkNest(self):
        if self.hasFood:
            antPos = Vector2(self.x, self.y)
            nestPos = Vector2(nestposition)
            if antPos.distance_to(nestPos) < nestRadius:
                self.hasFood = False
                self.scent_trail = None
                angle = random.uniform(0, 2 * math.pi)
                self.direction = Vector2(math.cos(angle), math.sin(angle)).normalize()

    def draw(self):
        antColor = antC if not self.hasFood else antCWF
        pygame.draw.circle(screen, antColor, (int(self.x), int(self.y)), 6)

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), foodRadius)

class Nest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self):
        pygame.draw.circle(screen, (255,0,255), (int(self.x), int(self.y)), nestRadius)

def init_ants_and_food():
    global ants, foodpiles
    ants = []
    for _ in range(antAmt):
        ants.append(Ant(random.randint(nestposition[0] - 10, nestposition[0] + 10),
                        random.randint(nestposition[1] - 10, nestposition[1] + 10),
                        antSpeed, olfactionSize))
    
    foodpiles = []
    while len(foodpiles) < numFood:
        x = random.randint(50, 1000 - 50)
        y = random.randint(50, 1000 - 50)
        if Vector2(x, y).distance_to(Vector2(nestposition)) > nestRadius + 100:
            foodpiles.append(Food(x, y))

# Init ants, food, and nest
init_ants_and_food()
nest = Nest(*nestposition)

running = True
scents = []
game_over = False

# Restart Button
button_width = 200
button_height = 50
button = pygame.Rect((screensize[0] - button_width) // 2, (screensize[1] - button_height) // 2, button_width, button_height)
button_color = (0, 255, 0)

def draw_button():
    pygame.draw.rect(screen, button_color, button)
    button_text = font.render("Restart", True, (255, 255, 255))
    
    # Center text rendering
    text_rect = button_text.get_rect(center=button.center)
    screen.blit(button_text, text_rect)

# Drawing the button
while running:
    clock.tick(fps)
    screen.fill((209, 190, 168))
    removableScents = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if button.collidepoint(event.pos):
                game_over = False
                init_ants_and_food()
                scents = []

    if not foodpiles:
        game_over = True

    if not game_over:
        for ant in ants:
            ant.update(scents, removableScents)
            ant.draw()
            if ant.scent_trail is not None:
                scents.append(ant.scent_trail)

        scents = [scent for scent in scents if time.time() - scent['time'] < 10 and scent not in removableScents]

        for food in foodpiles:
            food.draw()

        nest.draw()
        for scent in scents:
            pygame.draw.circle(screen, (0, 0, 255), (int(scent['x']), int(scent['y'])), 2)
    else:
        screen.fill((209, 190, 168))
        text = font.render("Simulation over", True, (255, 0, 0))
        screen.blit(text, (350, 400))
        draw_button()
    
    pygame.display.flip()

pygame.quit()
