import pygame
import sys
import time
import random
import threading

# Inicializa o Pygame
pygame.init()

# Configurações do relógio e FPS
clock = pygame.time.Clock()
FPS = 60  # Frames por segundo

# Configurações da janela
WIDTH, HEIGHT = 800, 600  # Nova resolução visível
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Corrida de Cavalos")

# Configurações de fonte
font = pygame.font.SysFont('Arial', 120)
small_font = pygame.font.SysFont('Arial', 30)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)

# Largura real do fundo (para corrida estendida)
bg_width_extended = 1639

# Carregamento de imagens de fundo com rolagem horizontal
bg1_frames = [
    pygame.transform.scale(pygame.image.load("cenario/bg1_1.png").convert(), (bg_width_extended, HEIGHT)),
    pygame.transform.scale(pygame.image.load("cenario/bg1_2.png").convert(), (bg_width_extended, HEIGHT))
]
bg2_frames = [
    pygame.transform.scale(pygame.image.load("cenario/bg2_1.png").convert(), (bg_width_extended, HEIGHT)),
    pygame.transform.scale(pygame.image.load("cenario/bg2_2.png").convert(), (bg_width_extended, HEIGHT))
]
bg3_frames = [
    pygame.transform.scale(pygame.image.load("cenario/bg3_1.png").convert(), (bg_width_extended, HEIGHT)),
    pygame.transform.scale(pygame.image.load("cenario/bg3_2.png").convert(), (bg_width_extended, HEIGHT))
]
bg4_frames = [
    pygame.transform.scale(pygame.image.load("cenario/bg4_1.png").convert(), (bg_width_extended, HEIGHT)),
    pygame.transform.scale(pygame.image.load("cenario/bg4_2.png").convert(), (bg_width_extended, HEIGHT))
]

# Cenário inicial
bg_set_index = 0
bg_current_frames = bg1_frames

# Transição
transition_interval = 20  # segundos entre cada transição
last_transition_time = time.time()
next_bg_frames = None

# Carregamento de imagens dos cavalos
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

# Miniaturas para barra de progresso
player_mini = pygame.transform.scale(pygame.image.load("cavalos/player1_2.png").convert_alpha(), (30, 20))
bot1_mini = pygame.transform.scale(pygame.image.load("cavalos/bot1_2.png").convert_alpha(), (30, 20))
bot2_mini = pygame.transform.scale(pygame.image.load("cavalos/bot2_2.png").convert_alpha(), (30, 20))

start_x = -100
finish_line = bg_width_extended - 200
player_pos = pygame.Vector2(start_x, 100)
bot1_pos = pygame.Vector2(start_x, 200)
bot2_pos = pygame.Vector2(start_x, 300)

bg_offset = 1  # Alterado para 1 conforme solicitado
frame_index = 0
bg_index = 0
animation_timer = 0
bg_timer = 0
ANIMATION_SPEED = 200
BG_ANIMATION_SPEED = 500
step_distance = 3
race_started = False
player_running = False
start_time = 0

transitioning = False
transition_start_time = 0
transition_duration = 3

# Semáforos para bots
bot1_lock = threading.Semaphore()
bot2_lock = threading.Semaphore()

# Movimento dos bots
def move_bot_fast(pos, lock):
    while True:
        if player_running:
            time.sleep(random.uniform(0, 0.25))
            with lock:
                pos.x += random.uniform(2, 4)
                if pos.x > finish_line:
                    pos.x = start_x
                    time.sleep(random.uniform(0.2, 0.8))
        else:
            time.sleep(0.1)

def move_bot_medium(pos, lock):
    while True:
        if player_running:
            time.sleep(random.uniform(0, 0.4))
            with lock:
                pos.x += random.uniform(1.3, 2.4)
                if pos.x > finish_line:
                    pos.x = start_x
                    time.sleep(random.uniform(0.5, 1.2))
        else:
            time.sleep(0.1)

threading.Thread(target=move_bot_fast, args=(bot1_pos, bot1_lock), daemon=True).start()
threading.Thread(target=move_bot_medium, args=(bot2_pos, bot2_lock), daemon=True).start()

# Tela inicial
def mostrar_tela_inicial():
    imagem_original = pygame.image.load("cenario/tela_inicial.png").convert()
    tela_inicial = pygame.transform.scale(imagem_original, (WIDTH, HEIGHT))
    botao_jogar = pygame.Rect(290, 240, 220, 50)

    while True:
        screen.blit(tela_inicial, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(event.pos):
                    return
        pygame.display.update() 

def show_countdown():
    for i in range(3, 0, -1):
        screen.blit(bg_current_frames[bg_index], (-bg_offset, 0))
        count_text = font.render(str(i), True, WHITE)
        screen.blit(count_text, count_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()
        time.sleep(1)
    screen.blit(bg_current_frames[bg_index], (-bg_offset, 0))
    go_text = font.render("GO!", True, GREEN)
    screen.blit(go_text, go_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pygame.display.flip()
    time.sleep(0.5)

# Barra de progresso
def draw_progress_bar():
    total_distance = finish_line - start_x
    player_progress = min(max((player_pos.x - start_x) / total_distance, 0), 1)
    bot1_progress = min(max((bot1_pos.x - start_x) / total_distance, 0), 1)
    bot2_progress = min(max((bot2_pos.x - start_x) / total_distance, 0), 1)
    bar_width = WIDTH - 100
    bar_height = 10
    bar_x = 50
    bar_y = 30
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    pygame.draw.line(screen, WHITE, (bar_x + bar_width, bar_y - 5), (bar_x + bar_width, bar_y + bar_height + 5), 2)
    screen.blit(bot1_mini, (bar_x + bot1_progress * bar_width - 15, bar_y - 25))
    screen.blit(bot2_mini, (bar_x + bot2_progress * bar_width - 15, bar_y - 25))
    screen.blit(player_mini, (bar_x + player_progress * bar_width - 15, bar_y - 25))

mostrar_tela_inicial()
show_countdown()
race_started = True
player_running = True
start_time = time.time()

running = True
while running:
    dt = clock.tick(FPS)
    animation_timer += dt
    bg_timer += dt
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    milliseconds = int((elapsed_time % 1) * 1000)
    time_text = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    if animation_timer >= ANIMATION_SPEED:
        frame_index = (frame_index + 1) % len(player_frames)
        animation_timer = 0

    if bg_timer >= BG_ANIMATION_SPEED:
        bg_index = (bg_index + 1) % len(bg_current_frames)  # Alterna entre os frames do cenário atual
        bg_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and race_started:
            if event.key in [pygame.K_SPACE, pygame.K_RIGHT]:
                player_pos.x += step_distance
                player_running = True
            elif event.key == pygame.K_LEFT:
                player_pos.x -= step_distance
                player_running = True

    bg_offset = player_pos.x * 0.8
    bg_offset = min(bg_offset, bg_width_extended - WIDTH)

    # Verifica se é hora de mudar de cenário (a cada 20 segundos)
    current_time = time.time()
    if current_time - last_transition_time >= transition_interval:
        if not transitioning:
            transitioning = True
            transition_start_time = current_time
            last_transition_time = current_time
            
            # Cicla entre os cenários (agora temos 4 cenários)
            bg_set_index = (bg_set_index + 1) % 4
            if bg_set_index == 0:
                next_bg_frames = bg1_frames
            elif bg_set_index == 1:
                next_bg_frames = bg2_frames
            elif bg_set_index == 2:
                next_bg_frames = bg3_frames
            elif bg_set_index == 3:
                next_bg_frames = bg4_frames

    if transitioning:
        t = (current_time - transition_start_time) / transition_duration
        if t >= 1:
            transitioning = False
            bg_current_frames = next_bg_frames
            bg_index = 0  # Reseta o índice para começar com o primeiro frame do novo cenário
        else:
            surf1 = bg_current_frames[bg_index].copy()
            surf2 = next_bg_frames[bg_index].copy()
            surf2.set_alpha(int(255 * t))
            surf1.blit(surf2, (0, 0))
            screen.blit(surf1, (-bg_offset, 0))
    else:
        # Desenha o frame atual do cenário (alternando entre bgX_1 e bgX_2)
        screen.blit(bg_current_frames[bg_index], (-bg_offset, 0))

    draw_progress_bar()
    time_surface = small_font.render(time_text, True, BLACK)
    screen.blit(time_surface, (WIDTH - time_surface.get_width() - 50, 50))

    screen.blit(player_frames[frame_index], (player_pos.x - bg_offset, player_pos.y))
    with bot1_lock:
        screen.blit(bot1_frames[frame_index], (bot1_pos.x - bg_offset, bot1_pos.y))
    with bot2_lock:
        screen.blit(bot2_frames[frame_index], (bot2_pos.x - bg_offset, bot2_pos.y))

    pygame.display.flip()

pygame.quit()
