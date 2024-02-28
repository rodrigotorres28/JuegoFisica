import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((700, 790))
clock = pygame.time.Clock()
running = True
dt = 0

gamespeed = 1
proj_list = []

class Projectile:
    accel_init = pygame.Vector2(0, 75)
    vel_init = pygame.Vector2(0, -150)
    pos_init = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    accel = accel_init
    vel = vel_init
    pos = pos_init
    time = 0

def newProjectile():
    proj = Projectile()
    proj.vel_init = pygame.Vector2(random.uniform(-100, 100), random.uniform(-250, -100))
    proj_list.append(proj)

lastProjectile = 0

player_vel_init = 0
player_pos_init = pygame.Vector2(screen.get_width() / 2, screen.get_height() - 50)
player_accel = 0
player_vel = player_vel_init
player_pos = pygame.Vector2(player_pos_init.x, player_pos_init.y)
player_time = 0

player_accel_last_tick = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if lastProjectile >= 1:
        newProjectile()
        lastProjectile = 0

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    pygame.draw.rect(screen, "darkgray", pygame.Rect((screen.get_width() / 2) - 270 - 5, 0, 10, 999999))
    pygame.draw.rect(screen, "darkgray", pygame.Rect((screen.get_width() / 2) + 270 - 5, 0, 10, 999999))

    pygame.draw.rect(screen, "blue", pygame.Rect(player_pos.x - 60, player_pos.y, 120, 10))

    for proj in proj_list:
        pygame.draw.circle(screen, "red", proj.pos, 10)
        proj.pos = (proj.accel/2) * (proj.time**2) + proj.vel_init * proj.time + proj.pos_init
        proj.time += dt * gamespeed

    player_vel = player_accel_last_tick * player_time + player_vel_init

    #Jugador acelera izquierda o derecha con velocidad maxima + frenado al no presionar ninguna tecla
    keys = pygame.key.get_pressed()
    if ((keys[pygame.K_a] or keys[pygame.K_LEFT])):
        if player_vel > -500:
            if player_vel <= 0:
                player_accel = -950
            else:
                player_accel = -1600
        else:
            player_accel = 0

    elif ((keys[pygame.K_d] or keys[pygame.K_RIGHT])):
        if player_vel < 500:
            if player_vel >= 0:
                player_accel = 950
            else:
                player_accel = 1600
        else:
            player_accel = 0

    else:
        if(player_vel < -1):
            player_accel = 650
        elif(player_vel > 1):
            player_accel = -650
        else:
            player_accel = 0
            player_vel_init = 0
            

    if (player_accel != player_accel_last_tick):
        player_vel_init = player_vel
        player_pos_init = pygame.Vector2(player_pos.x, player_pos.y)
        player_time = 0

    print("-------------------------------------")
    print("accel:" + str(player_accel))
    print("vel:" + str(player_vel))
    print("pos:" + str(player_pos))

    player_pos.x = (player_accel/2) * (player_time**2) + player_vel_init * player_time + player_pos_init.x
    player_accel_last_tick = player_accel

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 120
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(120) / 1000
    player_time += dt
    lastProjectile += dt

pygame.quit()