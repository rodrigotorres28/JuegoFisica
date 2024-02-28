import pygame
import random

# pygame setup
pygame.init()

screen = pygame.display.set_mode((715, 790))

height_meters = 100
pixels_per_meter = screen.get_height() / height_meters
width_meters = screen.get_width() / pixels_per_meter

clock = pygame.time.Clock()
running = True
dt = 0

gamespeed = 1
proj_list = []

class Projectile:
    accel_init = pygame.Vector2(0, 9.8)
    vel_init = pygame.Vector2(0, 0)
    pos_init = pygame.Vector2(width_meters / 2, height_meters / 2)
    accel = accel_init
    vel = vel_init
    pos = pos_init
    time = 0

    accel_last_tick = accel_init

def newProjectile():
    proj = Projectile()
    proj.vel_init = pygame.Vector2(random.uniform(-13, 13), random.uniform(-32, -13))
    proj_list.append(proj)

lastProjectile = 999

player_vel_init = 0
player_pos_init = pygame.Vector2((530/2) / pixels_per_meter, height_meters - 7)
player_accel = 0
player_vel = player_vel_init
player_pos = pygame.Vector2(player_pos_init.x, player_pos_init.y)
player_time = 0

player_accel_last_tick = 0

font_score = pygame.font.SysFont("Book Antiqua", 30)
font_proj = pygame.font.SysFont("Book Antiqua", 17)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if lastProjectile >= 15:
        newProjectile()
        lastProjectile = 0

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    #Dibujar paredes y techo
    pygame.draw.rect(screen, (77, 77, 77), pygame.Rect(0, 0, 10, 999999))
    pygame.draw.rect(screen, (77, 77, 77), pygame.Rect(520, 0, 10, 999999))
    pygame.draw.rect(screen, (77, 77, 77), pygame.Rect(0, 0, 520, 10))

    #Dibujar jugador
    pygame.draw.rect(screen, "blue", pygame.Rect((player_pos.x * pixels_per_meter) - 60, (player_pos.y * pixels_per_meter), 120, 10))

    for proj in proj_list:

        proj.vel = proj.accel_last_tick * proj.time + proj.vel_init

        #Se prepara un nuevo MRUA al cambiar la aceleración
        if (proj.accel != proj.accel_last_tick):
            proj.vel_init = proj.vel
            proj.pos_init = proj.pos
            proj.time = 0

        #MRUA proyectiles (en ambos ejes aunque aceleración pueda ser 0 y ser solo MRU)
        proj.pos = (proj.accel/2) * (proj.time**2) + proj.vel_init * proj.time + proj.pos_init
        proj.accel_last_tick = proj.accel
        proj.time += dt * gamespeed

        #Dibujar cada proyectil
        pygame.draw.circle(screen, "red", proj.pos * pixels_per_meter, 12)

        #Se prepara un nuevo MRUA con velocidad opuesta en Y al colisionar contra el jugador
        if proj.pos.x + (12 / pixels_per_meter) >= player_pos.x - (60 / pixels_per_meter) and proj.pos.x - (12 / pixels_per_meter) <= player_pos.x + (60 / pixels_per_meter) and proj.pos.y + (12 / pixels_per_meter) >= player_pos.y and proj.pos.y + (12 / pixels_per_meter) <= player_pos.y + 2 and proj.vel.y > 0:
            proj.vel_init = pygame.Vector2(proj.vel.x, -abs(proj.vel.y))
            proj.pos_init = proj.pos
            proj.time = 0

        #Se prepara un nuevo MRUA con velocidad opuesta en X al colisionar contra una pared o techo
        if proj.pos.x - (12 / pixels_per_meter) <= 10 / pixels_per_meter and proj.vel.x < 0:
            proj.vel_init = pygame.Vector2(abs(proj.vel.x), proj.vel.y)
            proj.pos_init = proj.pos
            proj.time = 0

        if proj.pos.x + (12 / pixels_per_meter) >= 520 / pixels_per_meter and proj.vel.x > 0:
            proj.vel_init = pygame.Vector2(-abs(proj.vel.x), proj.vel.y)
            proj.pos_init = proj.pos
            proj.time = 0

        if proj.pos.y - (12 / pixels_per_meter) <= 10 / pixels_per_meter and proj.vel.y < 0:
            proj.vel_init = pygame.Vector2(proj.vel.x, abs(proj.vel.y))
            proj.pos_init = proj.pos
            proj.time = 0

        #TEMPORAL Eliminar proyectiles pos >= height
        if proj.pos.y >= height_meters:
            proj_list.remove(proj)

        #Dibujar texto alineado dentro de cada proyectil
        proj_text = font_proj.render("1", True, (0, 0, 0))
        proj_text_rect = proj_text.get_rect()
        proj_text_rect.center = (proj.pos.x * pixels_per_meter, (proj.pos.y) * pixels_per_meter)
        screen.blit(proj_text, proj_text_rect.topleft)

    player_vel = player_accel_last_tick * player_time + player_vel_init

    #INICIO LOGICA JUGADOR

    #Jugador acelera izquierda o derecha con velocidad maxima y frenado
    keys = pygame.key.get_pressed()
    if ((keys[pygame.K_a] or keys[pygame.K_LEFT])):
        if player_vel > -63:
            if player_vel <= 0:
                player_accel = -120
            else:
                player_accel = -202
        else:
            player_accel = 0

    elif ((keys[pygame.K_d] or keys[pygame.K_RIGHT])):
        if player_vel < 63:
            if player_vel >= 0:
                player_accel = 120
            else:
                player_accel = 202
        else:
            player_accel = 0

    else:
        if(player_vel < -1):
            player_accel = 82
        elif(player_vel > 1):
            player_accel = -82
        else:
            player_accel = 0
            player_vel_init = 0
            
    #Se prepara un nuevo MRUA al cambiar la aceleración
    if (player_accel != player_accel_last_tick):
        player_vel_init = player_vel
        player_pos_init = pygame.Vector2(player_pos.x, player_pos.y)
        player_time = 0

    #Se prepara un nuevo MRUA con velocidad opuesta al colisionar contra una pared
    if player_pos.x * pixels_per_meter - 60 <= 10 and player_vel < 0:
        player_vel_init = abs(player_vel)
        player_pos_init = pygame.Vector2(player_pos.x, player_pos.y)
        player_time = 0

    if player_pos.x * pixels_per_meter + 60 >= 520 and player_vel > 0:
        player_vel_init = -abs(player_vel)
        player_pos_init = pygame.Vector2(player_pos.x, player_pos.y)
        player_time = 0
    #520: distancia entre paredes, 10: ancho paredes, 120: largo jugador
        
    print("-------------------------------------")
    print("accel:" + str(player_accel))
    print("vel:" + str(player_vel))
    print("pos:" + str(player_pos))

    #MRUA jugador
    player_pos.x = (player_accel/2) * (player_time**2) + player_vel_init * player_time + player_pos_init.x
    player_accel_last_tick = player_accel
    
    #FIN LOGICA JUGADOR

    #Dibujar el texto del score e información del juego
    score_text = font_score.render("1234567890", True, (0, 0, 0))
    screen.blit(score_text, (screen.get_width() - score_text.get_width() - 15, 50))


    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 120
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(120) / 1000
    player_time += dt
    lastProjectile += dt

pygame.quit()