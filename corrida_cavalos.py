import pygame
import sys
import threading
import time
import random

# Inicializa o Pygame
pygame.init()

# Configurações do relógio
clock = pygame.time.Clock()
FPS = 60

# Tamanho da janela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Corrida de Cavalos")

# Configurações de fonte
font = pygame.font.SysFont('Arial', 120)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Carregamento de imagens
# Cenário
bg_width_extended = WIDTH * 1
bg_frames = [
    pygame.transform.scale(pygame.image.load("cenario/bg1.png").convert(), (bg_width_extended, HEIGHT)),
    pygame.transform.scale(pygame.image.load("cenario/bg2.png").convert(), (bg_width_extended, HEIGHT))
]

# Cavalos principais
player_frames = [
    pygame.image.load("cavalos/player1_1.png").convert_alpha(),
    pygame.image.load("cavalos/player1_2.png").convert_alpha()
]
player_frames = [pygame.transform.scale(img, (img.get_width() // 2, img.get_height() // 2)) for img in player_frames]

bot1_frames = [
    pygame.image.load("cavalos/bot1_1.png").convert_alpha(),
    pygame.image.load("cavalos/bot1_2.png").convert_alpha()
]
bot1_frames = [pygame.transform.scale(img, (img.get_width() // 2, img.get_height() // 2)) for img in bot1_frames]

bot2_frames = [
    pygame.image.load("cavalos/bot2_1.png").convert_alpha(),
    pygame.image.load("cavalos/bot2_2.png").convert_alpha()
]
bot2_frames = [pygame.transform.scale(img, (img.get_width() // 2, img.get_height() // 2)) for img in bot2_frames]

# Miniaturas para a barra de progresso (um atrás do outro)
player_mini = pygame.transform.scale(pygame.image.load("cavalos/player1_2.png").convert_alpha(), (30, 20))
bot1_mini = pygame.transform.scale(pygame.image.load("cavalos/bot1_2.png").convert_alpha(), (30, 20))
bot2_mini = pygame.transform.scale(pygame.image.load("cavalos/bot2_2.png").convert_alpha(), (30, 20))

# Posições dos cavalos
start_x = -100
finish_line = bg_width_extended - 300
player_pos = pygame.Vector2(start_x, 100)
bot1_pos = pygame.Vector2(start_x, 200)
bot2_pos = pygame.Vector2(start_x, 300)

# Variáveis de controle
bg_offset = 0
frame_index = 0
bg_index = 0
animation_timer = 0
bg_timer = 0
ANIMATION_SPEED = 200
BG_ANIMATION_SPEED = 500
step_distance = 5
race_started = False
player_running = False

# Semáforos para controle de threads
bot1_lock = threading.Semaphore()
bot2_lock = threading.Semaphore()

def move_bot_fast(pos, lock):
    while True:
        if player_running:
            current_speed = random.uniform(2, 4)
            wait_time = random.uniform(0, 0.25)
            time.sleep(wait_time)
            with lock:
                pos.x += current_speed
                if pos.x > finish_line:
                    pos.x = start_x
                    time.sleep(random.uniform(0.2, 0.8))
        else:
            time.sleep(0.1)

def move_bot_medium(pos, lock):
    while True:
        if player_running:
            current_speed = random.uniform(1.3, 2.4)
            wait_time = random.uniform(0, 0.4)
            time.sleep(wait_time)
            with lock:
                pos.x += current_speed
                if pos.x > finish_line:
                    pos.x = start_x
                    time.sleep(random.uniform(0.5, 1.2))
        else:
            time.sleep(0.1)

# Inicia as threads
threading.Thread(target=move_bot_fast, args=(bot1_pos, bot1_lock), daemon=True).start()
threading.Thread(target=move_bot_medium, args=(bot2_pos, bot2_lock), daemon=True).start()

def show_countdown():
    for i in range(3, 0, -1):
        screen.blit(bg_frames[bg_index], (-bg_offset, 0))
        count_text = font.render(str(i), True, WHITE)
        text_rect = count_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(count_text, text_rect)
        pygame.display.flip()
        time.sleep(1)
    
    screen.blit(bg_frames[bg_index], (-bg_offset, 0))
    go_text = font.render("GO!", True, GREEN)
    text_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(go_text, text_rect)
    pygame.display.flip()
    time.sleep(0.5)

def draw_progress_bar():
    total_distance = finish_line - start_x
    
    # Calcula progresso (0 a 1)
    player_progress = min(max((player_pos.x - start_x) / total_distance, 0), 1)
    bot1_progress = min(max((bot1_pos.x - start_x) / total_distance, 0), 1)
    bot2_progress = min(max((bot2_pos.x - start_x) / total_distance, 0), 1)
    
    # Configurações da barra de progresso
    bar_width = WIDTH - 100
    bar_height = 10
    bar_x = 50
    bar_y = 30
    
    # Desenha a linha de progresso (fundo)
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Desenha a linha de chegada
    pygame.draw.line(screen, WHITE, (bar_x + bar_width, bar_y - 5), (bar_x + bar_width, bar_y + bar_height + 5), 2)
    
    # Posições dos mini cavalos (todos na mesma linha, um atrás do outro)
    horse_spacing = 15  # Espaço entre os cavalos
    base_y = bar_y - 25  # Posição Y base para todos os cavalos
    
    # Desenha os mini cavalos
    screen.blit(bot1_mini, (bar_x + bot1_progress * bar_width - 15, base_y))
    screen.blit(bot2_mini, (bar_x + bot2_progress * bar_width - 15, base_y))
    screen.blit(player_mini, (bar_x + player_progress * bar_width - 15, base_y))

# Mostra a contagem regressiva
show_countdown()
race_started = True

# Loop principal
running = True
while running:
    dt = clock.tick(FPS)
    animation_timer += dt
    bg_timer += dt

    # Atualiza animações
    if animation_timer >= ANIMATION_SPEED:
        frame_index = (frame_index + 1) % len(player_frames)
        animation_timer = 0

    if bg_timer >= BG_ANIMATION_SPEED:
        bg_index = (bg_index + 1) % len(bg_frames)
        bg_timer = 0

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and race_started:
            if event.key == pygame.K_SPACE:
                player_pos.x += step_distance
                player_running = True
            elif event.key == pygame.K_LEFT:
                player_pos.x -= step_distance
                player_running = True
            elif event.key == pygame.K_RIGHT:
                player_pos.x += step_distance
                player_running = True

    # Atualiza o deslocamento do fundo
    bg_offset = player_pos.x * 0.5
    bg_offset = min(bg_offset, bg_width_extended - WIDTH)

    # Desenha o cenário
    screen.blit(bg_frames[bg_index], (-bg_offset, 0))
    
    # Desenha a barra de progresso com mini cavalos
    draw_progress_bar()
    
    # Desenha os personagens
    screen.blit(player_frames[frame_index], (player_pos.x - bg_offset, player_pos.y))
    
    with bot1_lock:
        screen.blit(bot1_frames[frame_index], (bot1_pos.x - bg_offset, bot1_pos.y))
    with bot2_lock:
        screen.blit(bot2_frames[frame_index], (bot2_pos.x - bg_offset, bot2_pos.y))

    pygame.display.flip()

pygame.quit()
sys.exit()