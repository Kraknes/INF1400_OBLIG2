import pygame
import random
import math



# Screen and colour parameters
SCREEN_X = 1200
SCREEN_Y = 800
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
YELLOW = (255,255,0)
RED = (255,0,0)
GREEN = (0, 255, 0)

# Mouse pointer and main() variables
clicked = False
done = False

# How fast the game will go
FPS = 60

# Size for flying objects
BOID_SIZE = 5
HOIK_SIZE = 7

# Max and min speed for boids. Hoiks will have +1 speed of boids.
BOID_MAX_SPEED = 4
BOID_MIN_SPEED = 3

# Number of objects which will be shown on screen.
NR_OBJECTS = 4
NR_BOIDS = 70
NR_HOIKS = 3

# Inspiration from http://www.red3d.com/cwr/boids/
# Distances for each function for boid and hoik mentality. 
AVOIDANCE_DIST = 60
SEPERATION_DIST = 10
ALIGNMENT_DIST = 100
COHESION_DIST = 100

# Main class for all classes to be drawn. Draws unto screen with size and colour of said object. 
class Draw_Object(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.rect.x = random.uniform(0, SCREEN_X-self.size)
        self.rect.y = random.uniform(0, SCREEN_Y-self.size)
        
# Class for obstacles, inherits from Draw_object to get drawn to the scren. 
class Obstacle_Object(Draw_Object):
    def __init__(self):
        self.size = random.uniform(40, 200)
        self.colour = BLUE
        super().__init__()
        
        
# Class for common inhereted flying_object, inherits from Draw_Object to be drawn. Has all functions for moving a boid or hoik.      
class Flying_Object(Draw_Object):
    def __init__(self):
        super().__init__()
        self.turn_rate = 0.35
        self.speed_x = random.randrange(-3,3,2)
        self.speed_y = random.randrange(-3,3,2)
        self.neighbour_group = 0
        self.x_rate = 0
        self.y_rate = 0
        
    # -------------------- START of Functions for avoiding clipping inside obstacles or walls ----------------------#
    
    # Avoiding that a moving object flies into an obstacle
    def obstacle_clip(self, obstacle_group):
        # Fetches list of obstacles which self has collided into
        obstacle_list = pygame.sprite.spritecollide(self, obstacle_group,False)
        for obstacle in obstacle_list:
            
            # Checking every side, bounces of said side and clips outside the object to avoid going into the object
            if self.rect.centerx <= obstacle.rect.left+10:
                self.speed_x *= -1
                self.rect.centerx = obstacle.rect.left - self.size
                
            if self.rect.centerx >= obstacle.rect.right-10:
                self.speed_x *= -1
                self.rect.centerx = obstacle.rect.right + self.size
                
            if self.rect.centery <= obstacle.rect.top+10:
                self.speed_y *= -1
                self.rect.centery = obstacle.rect.top - self.size
                
            if self.rect.centery >= obstacle.rect.bottom-10:
                self.speed_y *= -1
                self.rect.centery = obstacle.rect.bottom + self.size
                
    # Avoidance of walls around the screen algorithm, turns away with turn_rate        
    def avoid_wall(self):         
        # Unngår skjerm boundries 
        if self.rect.centerx < 0 + AVOIDANCE_DIST:
            self.speed_x += self.turn_rate            
        if self.rect.centerx > SCREEN_X - AVOIDANCE_DIST:
            self.speed_x += -self.turn_rate
        if self.rect.centery < 0 + AVOIDANCE_DIST:
            self.speed_y += self.turn_rate
        if self.rect.centery > SCREEN_Y - AVOIDANCE_DIST:
            self.speed_y += -self.turn_rate
         
    # Crashing into wall algortihm. If crash in wall will put back on screen (not flying/clipping off).  
    def wall_clip(self):
        if self.rect.centerx < 0:
            self.rect.centerx = 0 + self.size
            self.speed_x *= -1
        if self.rect.centerx > SCREEN_X:
            self.rect.centerx = SCREEN_X - self.size
            self.speed_x *= -1
        if self.rect.centery < 0:
            self.rect.centery = 0 + self.size
            self.speed_y *= -1
        if self.rect.centery > SCREEN_Y:
            self.rect.centery = SCREEN_Y - 2*self.size
            self.speed_y *= -1
            
    # -------------------- END of Functions for avoiding clipping inside obstacles or walls ----------------------#      

    # ----------------------------------- START of Functions for flying objects -----------------------------------# 
            
    # Avoiding objects in a group (obstacles, each other or hoiks)
    def avoid_object(self, object_group, avoid_dist, turn_rate):
        # Checking for all objects in a group if they're in the vicinity of self.
        for object in object_group:
            if object is not self:
                if self.rect.centerx in range(object.rect.left - avoid_dist, object.rect.right + avoid_dist):
                    if self.rect.centery in range(object.rect.top - avoid_dist, object.rect.bottom + avoid_dist):
                        # Turns away from the object depending on orientation
                        if self.rect.centerx < object.rect.left:
                            self.speed_x += -turn_rate
                        if self.rect.centerx > object.rect.right:
                            self.speed_x += turn_rate
                        if self.rect.centery < object.rect.top:
                            self.speed_y += -turn_rate
                        if self.rect.centery > object.rect.bottom:
                            self.speed_y += turn_rate  
                        
      

    # Function that mover trying to get the same speed as its neighbours
    def alignment(self, fly_obj_list):
    # Checking for all objects in a group if they're in the vicinity of self (neighbours).
        for fly_obj in fly_obj_list:
            if fly_obj is not self:
                if fly_obj.rect.centerx in range(self.rect.left - ALIGNMENT_DIST, self.rect.right + ALIGNMENT_DIST):
                    if fly_obj.rect.centery in range(self.rect.top - ALIGNMENT_DIST, self.rect.bottom + ALIGNMENT_DIST):  
                        # Adding all the speed to one variable, and counts the number of neighburs.  
                        self.x_rate += fly_obj.speed_x
                        self.y_rate += fly_obj.speed_y
                        self.neighbour_group += 1
        # Calculating the mean of speed from its neighbours and adds to its own speed
        if self.neighbour_group != 0:
            avg_x = self.x_rate / self.neighbour_group
            avg_y = self.y_rate / self.neighbour_group
            self.speed_x += avg_x * 0.1
            self.speed_y += avg_y * 0.1
        self.nuller()
            
    # Function that mover trying to get the average position as its neighbours
    def cohesion(self, fly_obj_list):
        # Checking for all objects in a group if they're in the vicinity of self (neighbours).
        for fly_obj in fly_obj_list:
            if fly_obj is not self:
                if fly_obj.rect.centerx in range(self.rect.left - COHESION_DIST, self.rect.right + COHESION_DIST):
                    if fly_obj.rect.centery in range(self.rect.top - COHESION_DIST, self.rect.bottom + COHESION_DIST):   
                        # Adding all the speed to one variable, and counts the number of neighburs.
                        self.x_rate += fly_obj.rect.centerx  
                        self.y_rate += fly_obj.rect.centery
                        self.neighbour_group+= 1 
        # Calculating the mean of position from its neighbours and adds to its own speed
        if self.neighbour_group != 0:
            avg_x = self.x_rate / self.neighbour_group 
            avg_y = self.y_rate / self.neighbour_group
            self.speed_x += (avg_x - self.rect.centerx) * 0.005
            self.speed_y += (avg_y - self.rect.centery) * 0.005
        self.nuller()
        

# Speed check made by https://vanhunteradams.com/Pico/Animal_Movement/Boids-algorithm.html. 
# All creds to the author.  
    def speed_check(self):
        speed = math.sqrt(pow(self.speed_x ,2) + pow(self.speed_y,2))
        if speed > self.max_speed:
            self.speed_x = (self.speed_x/speed) * self.max_speed
            self.speed_y = (self.speed_y/speed) * self.max_speed
        if speed < self.min_speed:
            if speed == 0:
                speed = 1
            self.speed_x = (self.speed_x/speed) * self.min_speed
            self.speed_y = (self.speed_y/speed) * self.min_speed
            
        
    # A function that nulls out variables for the next function
    def nuller(self):
        self.x_rate = 0
        self.y_rate = 0
        self.neighbour_group = 0
        
    # Mouse click function to attract boids to the pointer       
    def move_click(self):
        if clicked == True: 
            self.speed_x = (click_x - self.rect.centerx) * 0.01
            self.speed_y = (click_y - self.rect.centery) * 0.01
    
# Boid class, inherits from Flying_Object class. Will go together and avoid hoiks.
class Boid(Flying_Object):
    def __init__(self):
        self.max_speed = BOID_MAX_SPEED
        self.min_speed = BOID_MIN_SPEED
        self.size = BOID_SIZE
        self.colour = GREEN
        self.group = boid_group     
        super().__init__() 
    
    
    def update(self):
        # Boid mentality functions
        self.cohesion(self.group)
        self.alignment(self.group)
        self.avoid_object(self.group, SEPERATION_DIST, 0.1 )
        self.avoid_object(hoik_group, AVOIDANCE_DIST, self.turn_rate)

        # Avoid obstacles and walls
        self.avoid_wall()
        self.avoid_object(obstacle_group, AVOIDANCE_DIST, self.turn_rate)
        self.obstacle_clip(obstacle_group)
        self.wall_clip()
        
        # Speed check and add speed to its position
        self.move_click()
        self.speed_check()
        self.rect.centerx += self.speed_x
        self.rect.centery += self.speed_y

# Hoid class, inherits from Flying_Object class. Will hunt boids and eat them.      
class Hoik(Flying_Object):
    def __init__(self):
        self.size = HOIK_SIZE
        self.colour = RED                                                                                             
        super().__init__()
        self.group = hoik_group 
        self.max_speed = BOID_MAX_SPEED+1
        self.min_speed = BOID_MIN_SPEED+1
        
    # Hoik eating boid algorithm. Checking for collision with boids, and then gain size and loses speed accordingly to the amount of eaten boid. 
    def eat(self):
        if pygame.sprite.spritecollide(self, boid_group, True):
            self.size += 1
            self.max_speed -= 0.3
            if self.max_speed < 1:
                self.max_speed = 1
            self.image = pygame.Surface([self.size, self.size])
            self.image.fill(RED)
            self.rect = self.rect
            # Adding a new boid so the number of boids stay the same
            
    def phoenix(self):
        # If growing too large, will die and be reborn.
        if self.size == 15:
            self.remove(self.group)
            hoik_group.add(Hoik())
                        
            
    
    def update(self):
        # Hoik mentality functions. Avoids other hoiks to not go on same target. 
        self.eat()
        self.alignment(boid_group)
        self.cohesion(boid_group)
        self.avoid_object(self.group, AVOIDANCE_DIST, self.turn_rate )
        
         # avoid obstacles and walls
        self.avoid_object(obstacle_group, AVOIDANCE_DIST, self.turn_rate)
        self.avoid_wall()
        self.obstacle_clip(obstacle_group)
        self.wall_clip()
        self.phoenix()
        
        # Speed check and add speed to its position
        self.speed_check()
        self.rect.centerx += self.speed_x
        self.rect.centery += self.speed_y
        
                
# Making all the groups
obstacle_group = pygame.sprite.Group()
boid_group = pygame.sprite.Group()
hoik_group = pygame.sprite.Group()
for _ in range(NR_OBJECTS):
    obstacle_group.add(Obstacle_Object())
for _ in range (NR_BOIDS):
    boid_group.add(Boid())
for _ in range (NR_HOIKS):
    hoik_group.add(Hoik())

pygame.init()
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
clock = pygame.time.Clock()
pygame.display.set_caption("Erling's Boidorama")


while not done:
    event = pygame.event.poll()
    if event.type == pygame.MOUSEBUTTONDOWN:
        clicked = True
        click_x, click_y = event.pos
    if event.type == pygame.MOUSEBUTTONUP:
        clicked = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            done = True
    if event.type == pygame.QUIT:
        done = True
    # Replenish number of boids 
    if len(boid_group) != NR_BOIDS:
        boid_group.add(Boid())
        
    screen.fill(BLACK)
    obstacle_group.update()
    obstacle_group.draw(screen)
    boid_group.update()
    boid_group.draw(screen)
    hoik_group.update()
    hoik_group.draw(screen)
    pygame.display.update()
    pygame.display.flip()
    clock.tick(FPS)
    
    
        