import math
import pygame
import numpy as np
import random
import rtmidi
import csv

# pygame setup
pygame.init()

screen = pygame.display.set_mode((715, 790))

height_meters = 100
pixels_per_meter = screen.get_height() / height_meters
width_meters = screen.get_width() / pixels_per_meter

clock = pygame.time.Clock()
running = True
dt = 0

lives = 3
score = 0
discarding = False
recovering = 0
cooldown_recover = 30
recovered = []
penalty = 0
difficulty = "Trivial"

proj_list = []

next_id = 0
class Projectile:
    id = next_id
    accel_init = pygame.Vector2(0, 9.8)
    vel_init = pygame.Vector2(0, 0)
    pos_init = pygame.Vector2((530 / 2) / pixels_per_meter, height_meters / 2)
    accel = accel_init
    vel = vel_init
    pos = pos_init
    mass = 1
    time = 0

    accel_last_tick = accel_init

proj_delay = 10
lastProjectile = 9.8

def newProjectile():
    pop_up_sound.play()
    global next_id
    proj = Projectile()
    proj.id = next_id
    next_id += 1
    proj.pos_init = pygame.Vector2((530 / 2) / pixels_per_meter + random.uniform(-20, 20), height_meters / 2 + random.uniform(-20, 0))
    proj.vel_init = pygame.Vector2(random.uniform(-16, 16), random.uniform(-32, -13))
    if(len(recovered) > 0):
        proj.mass = recovered.pop(0)
    proj_list.append(proj)

player_vel_init = 0
player_pos_init = pygame.Vector2((530/2) / pixels_per_meter, height_meters - 7)
player_accel = 0
player_vel = player_vel_init
player_pos = pygame.Vector2(player_pos_init.x, player_pos_init.y)
player_time = 0

player_accel_last_tick = 0

log_data = [['ID', 'TIME', 'POS X', 'VEL X', 'ACCEL X', 'POS X init', 'VEL X init', 'POS Y', 'VEL Y', 'ACCEL Y', 'POS Y init', 'VEL Y init']]
file_path = "Projectiles_log.csv"

def restart():
    global proj_list, lastProjectile, proj_delay, player_vel_init, player_pos_init, player_accel, player_vel, player_pos, player_time, penalty, score, lives, cooldown_recover, recovering
    proj_list = []
    lastProjectile = 9.8
    proj_delay = 10

    player_vel_init = 0
    player_pos_init = pygame.Vector2((530/2) / pixels_per_meter, height_meters - 7)
    player_accel = 0
    player_vel = player_vel_init
    player_pos = pygame.Vector2(player_pos_init.x, player_pos_init.y)
    player_time = 0

    penalty = 0
    score = 0
    lives = 3
    cooldown_recover = 30
    recovering = 0

font_gameover = pygame.font.SysFont("Calibri", 40, True)
font_score = pygame.font.SysFont("Book Antiqua", 28)
font_proj = pygame.font.SysFont("Book Antiqua", 17)
font_game_info = pygame.font.SysFont("Arial", 19, True)
font_recover = pygame.font.SysFont("Arial", 22)
colour = (255,0,0)

lost_life_sound = pygame.mixer.Sound('lostlife.wav')
lost_life_sound.set_volume(0.8)
proj_colision_sound = pygame.mixer.Sound('projcolision.wav')
proj_colision_sound.set_volume(0.25)
pop_up_sound = pygame.mixer.Sound('popup.wav')
pop_up_sound.set_volume(1.25)
bounce1_sound = pygame.mixer.Sound('BOUNCE1.wav')
bounce1_sound.set_volume(0.9)
bounce2_sound = pygame.mixer.Sound('BOUNCE2.wav')
bounce2_sound.set_volume(0.9)
bounce3_sound = pygame.mixer.Sound('BOUNCE3.wav')
bounce3_sound.set_volume(0.9)
bounce4_sound = pygame.mixer.Sound('BOUNCE4.wav')
bounce4_sound.set_volume(0.9)


midi_in = rtmidi.MidiIn()
available_ports = midi_in.get_ports()
midi_connected = False
if available_ports:
    midi_in.open_port(0) 
    midi_connected = True
else:
    midi_connected = False
    print("No se encontraron dispositivos MIDI disponibles.")

midi_accel = 0 
midi_discarding_on = False
midi_restarting_on = False
midi_recovering_on = False 

def handle_midi_message(message, data): 
    global midi_accel, midi_discarding_on, midi_restarting_on, midi_recovering_on
    #print(message)
    print("---")
    #print(message[0][0])
    #print(message[0][1])
    #print(message[0][2])

    if message[0][0] == 224 and message[0][1] == 0: #equivalente a A y D
        if message[0][2] > 64:
            accel_per_value = 130/63
            midi_accel = (message[0][2] - 63) * accel_per_value
        elif message[0][2] < 64: 
            accel_per_value = 130/64
            midi_accel = (message[0][2] - 64) * accel_per_value
        else:
            midi_accel = 0
    
    print(midi_accel)    

    if message[0][0] == 191 and message[0][1] == 117: #equivalente a S
        if message[0][2] == 0:
            midi_discarding_on = False
        else: 
            midi_discarding_on = True

    if message[0][0] == 191 and message[0][1] == 113: #equivalente a R
        if message[0][2] == 0:
            midi_restarting_on = False
        else: 
            midi_restarting_on = True

    if message[0][0] == 191 and message[0][1] == 118: #equivalente a W
        if message[0][2] == 0:
            midi_recovering_on = False
        else: 
            midi_recovering_on = True
        

midi_in.set_callback(handle_midi_message)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open(file_path, "w", newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerows(log_data)
            running = False

    keys = pygame.key.get_pressed()
    if ((keys[pygame.K_r]) or midi_restarting_on):
        restart()

    if lives <= 0:
        screen.fill("white")

        gameover_text = font_gameover.render("GAME OVER", True, (255, 0, 0))
        screen.blit(gameover_text, (((screen.get_width() / 2) - (gameover_text.get_width() / 2)), (screen.get_height() / 2) - 80))

        score_text = font_score.render("SCORE: " + str(score), True, (0, 0, 0))
        screen.blit(score_text, (((screen.get_width() / 2) - (score_text.get_width() / 2)), screen.get_height()/ 2))

        score_text = font_score.render("PRESS R TO RESTART", True, "grey")
        screen.blit(score_text, (((screen.get_width() / 2) - (score_text.get_width() / 2)), (screen.get_height() - 50)))

        pygame.display.flip()
        dt = clock.tick(120) / 1000
        continue

    if lastProjectile >= proj_delay:
        newProjectile()
        lastProjectile = 0

    if proj_delay <= 1:
        difficulty = "MAX"
    elif proj_delay <= 3:
        difficulty = "Insane"
    elif proj_delay <= 5:
        difficulty = "Hard"
    elif proj_delay <= 7:
        difficulty = "Medium"
    elif proj_delay <= 9:
        difficulty = "Easy"
    else:
        difficulty = "Trivial"


    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    #Dibujar paredes y techo
    pygame.draw.rect(screen, (77, 77, 77), pygame.Rect(0, 0, 10, 999999))
    pygame.draw.rect(screen, (77, 77, 77), pygame.Rect(520, 0, 10, 999999))
    pygame.draw.rect(screen, (77, 77, 77), pygame.Rect(0, 0, 520, 10))

    #Dibujar jugador
    pygame.draw.rect(screen, "blue", pygame.Rect((player_pos.x * pixels_per_meter) - 60, (player_pos.y * pixels_per_meter), 120, 10))

    #Descartar proyectil con S o ABAJO
    if (((keys[pygame.K_s] or keys[pygame.K_DOWN])) or midi_discarding_on):
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(10, screen.get_height() - 20, 510, 6))
        penalty = 5
        discarding = True
    elif discarding == True:
        discarding = False

    if (((keys[pygame.K_w] or keys[pygame.K_UP])) or midi_recovering_on):
        if (cooldown_recover <= 0):
            cooldown_recover = 30
            recovering = 5
    if (recovering > 0):
        pygame.draw.rect(screen, (0, 170, 0), pygame.Rect(10, screen.get_height() - 20, 510, 6))


    for proj in proj_list:

        proj.vel = proj.accel_last_tick * proj.time + proj.vel_init

        #Se prepara un nuevo MRUA al cambiar la aceleración
        if (proj.accel != proj.accel_last_tick):
            proj.vel_init = proj.vel
            proj.pos_init = proj.pos
            proj.time = 0

        #MRUA proyectiles (en ambos ejes aunque aceleración pueda ser 0 y ser solo MRU)
        proj.pos = (proj.accel/2) * (proj.time**2) + proj.vel_init * proj.time + proj.pos_init

        log_data.append([proj.id, proj.time, proj.pos.x, proj.vel.x, proj.accel.x, proj.pos_init.x, proj.vel_init.x, proj.pos.y, proj.vel.y, proj.accel.y, proj.pos_init.y, proj.vel_init.y])

        proj.accel_last_tick = proj.accel
        proj.time += dt

        #Dibujar cada proyectil
        match proj.mass:
            case  1 | 2 | 3 | 4 | 5:
                colour = (111, 213, 227)
            case 6 | 7 | 8 | 9 | 10:
                colour = (111, 155, 227)
            case 11 | 12 | 13 | 14 | 15:
                colour = (171, 111, 227)
            case _: 
                colour = (212, 111, 227)

        pygame.draw.circle(screen, colour, proj.pos * pixels_per_meter, 12)


        #Se prepara un nuevo MRUA con velocidad opuesta en Y al colisionar contra el jugador
        #Se suman puntos si la penalización no está activa
        if proj.pos.x + (12 / pixels_per_meter) >= player_pos.x - (60 / pixels_per_meter) and proj.pos.x - (12 / pixels_per_meter) <= player_pos.x + (60 / pixels_per_meter) and proj.pos.y + (12 / pixels_per_meter) >= player_pos.y and proj.pos.y + (12 / pixels_per_meter) <= player_pos.y + 2 and proj.vel.y > 0:
            if(proj.mass >= 16):
                bounce4_sound.play()
            elif(proj.mass >= 11):
                bounce3_sound.play()
            elif(proj.mass >= 6):
                bounce2_sound.play()
            else:
                bounce1_sound.play()

            proj.vel_init = pygame.Vector2(proj.vel.x, -abs(proj.vel.y))
            proj.pos_init = proj.pos
            proj.time = 0
            if penalty <= 0:
                score += proj.mass

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

        #Descartar proyectil con S o ABAJO
        if discarding == True and proj.pos.y >= height_meters - 2.5:
            proj_list.remove(proj)
            continue

        if recovering >= 0 and proj.pos.y >= height_meters - 2.5:
            recovered.append(proj.mass)
            proj_list.remove(proj)
            continue

        #Perder una vida al caer 1 proyectil
        if proj.pos.y >= height_meters:
            lost_life_sound.play()
            lives -= 1
            proj_list.remove(proj)
            continue

         #if Colison de proyectiles
        
        for proj_col in proj_list:
            if  proj_col != proj and np.sqrt((proj_col.pos.x - proj.pos.x) ** 2 + (proj_col.pos.y - proj.pos.y) ** 2) <= 24 / pixels_per_meter:
                proj_colision_sound.play()
                vel_f = ((proj.mass * proj.vel) + (proj_col.mass * proj_col.vel)) / (proj.mass + proj_col.mass)
                pos_new_proj = pygame.Vector2((proj.pos.x + proj_col.pos.x) / 2, (proj.pos.y + proj_col.pos.y) / 2)
                proj.vel_init = vel_f
                proj.pos_init = pos_new_proj
                proj.time = 0
                proj.mass = proj.mass + proj_col.mass
                proj.id = next_id
                next_id += 1
                proj_list.remove(proj_col)
                break
        
        #Dibujar texto alineado dentro de cada proyectil
        proj_text = font_proj.render(str(proj.mass), True, (0, 0, 0))
        proj_text_rect = proj_text.get_rect()
        proj_text_rect.center = (proj.pos.x * pixels_per_meter, (proj.pos.y) * pixels_per_meter)
        screen.blit(proj_text, proj_text_rect.topleft)


    #INICIO LOGICA JUGADOR
    player_vel = player_accel_last_tick * player_time + player_vel_init

    #Jugador acelera izquierda o derecha con velocidad maxima y frenado
    
    if not midi_connected: 
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

    else: 
        if midi_accel < 0 and player_vel < 0: 
            player_accel = midi_accel
        if midi_accel < 0 and player_vel >= 0:
            player_accel = midi_accel - 82
        if midi_accel > 0 and player_vel > 0:
            player_accel = midi_accel 
        if midi_accel > 0 and player_vel <= 0:
            player_accel = midi_accel + 82
        if midi_accel == 0:
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
        

    #MRUA jugador
    player_pos.x = (player_accel/2) * (player_time**2) + player_vel_init * player_time + player_pos_init.x
    player_accel_last_tick = player_accel
    
    #FIN LOGICA JUGADOR

    #Dibujar el texto del score e información del juego
    if penalty > 0:
        if not font_score.get_strikethrough():
            font_score.set_strikethrough(True)
        score_text = font_score.render(str(score), True, (255, 0, 0))
    elif penalty <= 0:
        if font_score.get_strikethrough():
            font_score.set_strikethrough(False)
        score_text = font_score.render(str(score), True, (0, 0, 0))

    screen.blit(score_text, (screen.get_width() - score_text.get_width() - 5, 50))

    font_score.set_strikethrough(False)
    score_text = font_score.render("SCORE:", True, (0, 0, 0))
    screen.blit(score_text, (screen.get_width() - score_text.get_width() - 80, 50))

    lives_text = font_game_info.render("LIVES: " + str(lives), True, (0,0,0))
    screen.blit(lives_text, (screen.get_width() - 178, 170))

    difficulty_text = font_game_info.render("DIFFICULTY: " + difficulty, True, (0,0,0))
    screen.blit(difficulty_text, (screen.get_width() - 178, 200))

    recovered_text = font_game_info.render("RECOVERED BALLS: " + str(len(recovered)), True, (0,0,0))
    screen.blit(recovered_text, (screen.get_width() - 178, 230))

    if (cooldown_recover > 0):
        recovery_text = font_recover.render("COOLDOWN: " + str(math.ceil(cooldown_recover)), True, (255, 132, 0))
        screen.blit(recovery_text, (screen.get_width() - 162, 680))
    else:
        recovery_text = font_recover.render("RECOVERY READY", True, (0, 170, 0))
        screen.blit(recovery_text, (screen.get_width() - 175, 680))

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 120
    # dt is delta time in seconds since last frame, used for framerate
    dt = clock.tick(120) / 1000
    player_time += dt
    lastProjectile += dt
    penalty -= dt
    cooldown_recover -= dt
    recovering -= dt
    if proj_delay >= 5:
        proj_delay -= dt * 0.05
    elif proj_delay >= 1:
        proj_delay -= dt * 0.02

pygame.quit()