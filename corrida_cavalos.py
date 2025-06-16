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
result_font = pygame.font.SysFont('Arial', 72)
record_font = pygame.font.SysFont('Arial', 40) ### NOVO ###

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0) ### NOVO ###

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
bg5_frames = [
    pygame.transform.scale(pygame.image.load("cenario/bg5_1.png").convert(), (bg_width_extended, HEIGHT)),
    pygame.transform.scale(pygame.image.load("cenario/bg5_2.png").convert(), (bg_width_extended, HEIGHT))
]

# Cenário inicial
bg_set_index = 0
bg_current_frames = bg1_frames
last_scenario = False  # Flag para indicar quando chegamos no último cenário

# Transição
transition_interval = 10  # segundos entre cada transição
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

bg_offset = 1
frame_index = 0
bg_index = 0
animation_timer = 0
bg_timer = 0
ANIMATION_SPEED = 200
BG_ANIMATION_SPEED = 500
step_distance = 4.5
race_started = False
player_running = False
start_time = 0
elapsed_time = 0 ### NOVO ###
time_text = "00:00.000" ### NOVO ###


transitioning = False
transition_start_time = 0
transition_duration = 3

# Variáveis de controle do jogo
game_over = False
result_text = ""

# ### NOVO ### - Variáveis de recorde
RECORDE_FILE = "recorde.txt"
record_time = float('inf')
final_time_str = ""
new_record_achieved = False

# ### NOVO ### - Função para carregar o recorde
def load_record_time():
    try:
        with open(RECORDE_FILE, 'r') as f:
            return float(f.read())
    except (FileNotFoundError, ValueError):
        return float('inf')

# ### NOVO ### - Função para salvar o recorde
def save_record_time(new_time):
    with open(RECORDE_FILE, 'w') as f:
        f.write(str(new_time))

# ### NOVO ### - Função para formatar o tempo
def format_time(t):
    if t == float('inf'):
        return "Nenhum"
    minutes = int(t // 60)
    seconds = int(t % 60)
    milliseconds = int((t % 1) * 1000)
    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

# Carrega o recorde no início do jogo
record_time = load_record_time()

# Semáforos para bots
bot1_lock = threading.Semaphore()
bot2_lock = threading.Semaphore()

# Movimento dos bots
def move_bot_fast(pos, lock):
    while True:
        if player_running and not game_over:
            time.sleep(random.uniform(0, 0.25))
            with lock:
                pos.x += random.uniform(2, 4)
                if pos.x > finish_line and last_scenario and not game_over:
                    pos.x = finish_line + 10  # Garante que passou da linha
        else:
            time.sleep(0.1)

def move_bot_medium(pos, lock):
    while True:
        if player_running and not game_over:
            time.sleep(random.uniform(0, 0.4))
            with lock:
                pos.x += random.uniform(1.3, 2.4)
                if pos.x > finish_line and last_scenario and not game_over:
                    pos.x = finish_line + 10  # Garante que passou da linha
        else:
            time.sleep(0.1)

threading.Thread(target=move_bot_fast, args=(bot1_pos, bot1_lock), daemon=True).start()
threading.Thread(target=move_bot_medium, args=(bot2_pos, bot2_lock), daemon=True).start()

# Tela inicial
def mostrar_tela_inicial():
    imagem_original = pygame.image.load("cenario/tela_inicial.png").convert()
    tela_inicial = pygame.transform.scale(imagem_original, (WIDTH, HEIGHT))
    botao_jogar = pygame.Rect(290, 340, 220, 50)

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
last_transition_time = time.time() # Reinicia o timer da transição após o countdown

running = True
while running:
    dt = clock.tick(FPS)
    animation_timer += dt
    bg_timer += dt
    
    if not game_over:
        elapsed_time = time.time() - start_time
        time_text = format_time(elapsed_time) ### NOVO ###

    if animation_timer >= ANIMATION_SPEED:
        frame_index = (frame_index + 1) % len(player_frames)
        animation_timer = 0

    if bg_timer >= BG_ANIMATION_SPEED:
        bg_index = (bg_index + 1) % len(bg_current_frames)
        bg_timer = 0

    bg_offset = player_pos.x * 0.8
    bg_offset = min(bg_offset, bg_width_extended - WIDTH)

    # Verifica se é hora de mudar de cenário (a cada 10 segundos)
    current_time = time.time()
    if not last_scenario and current_time - last_transition_time >= transition_interval and not game_over:
        if not transitioning:
            transitioning = True
            transition_start_time = current_time
            last_transition_time = current_time
            
            # Cicla entre os cenários
            bg_set_index = (bg_set_index + 1) % 5  # Agora temos 5 cenários
            if bg_set_index == 0:
                next_bg_frames = bg1_frames
            elif bg_set_index == 1:
                next_bg_frames = bg2_frames
            elif bg_set_index == 2:
                next_bg_frames = bg3_frames
            elif bg_set_index == 3:
                next_bg_frames = bg4_frames
            elif bg_set_index == 4:
                next_bg_frames = bg5_frames
                last_scenario = True  # Marca que chegamos no último cenário

    # Verifica se algum cavalo chegou ao final (apenas no último cenário)
    if last_scenario and not game_over:
        if player_pos.x >= finish_line:
            game_over = True
            result_text = "VOCÊ VENCEU!"
            final_time_str = time_text ### NOVO ###
            # ### NOVO ### - Verifica e salva o novo recorde
            if elapsed_time < record_time:
                record_time = elapsed_time
                save_record_time(record_time)
                new_record_achieved = True

        elif bot1_pos.x >= finish_line or bot2_pos.x >= finish_line:
            game_over = True
            result_text = "VOCÊ PERDEU!"

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
        screen.blit(bg_current_frames[bg_index], (-bg_offset, 0))

    draw_progress_bar()
    
    if not game_over:
        time_surface = small_font.render(time_text, True, BLACK)
        screen.blit(time_surface, (WIDTH - time_surface.get_width() - 50, 50))

    screen.blit(player_frames[frame_index], (player_pos.x - bg_offset, player_pos.y))
    with bot1_lock:
        screen.blit(bot1_frames[frame_index], (bot1_pos.x - bg_offset, bot1_pos.y))
    with bot2_lock:
        screen.blit(bot2_frames[frame_index], (bot2_pos.x - bg_offset, bot2_pos.y))

    # Desenha o resultado se o jogo acabou
    if game_over:
        # Cria uma superfície semi-transparente para o fundo do texto
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Preto semi-transparente
        screen.blit(overlay, (0, 0))
        
        # Desenha o texto do resultado
        text_surface = result_font.render(result_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(text_surface, text_rect)
        
        # ### NOVO ### - Mostra tempo e recorde se o jogador venceu
        if result_text == "VOCÊ VENCEU!":
            # Exibe o tempo final
            your_time_text = small_font.render(f"Seu tempo: {final_time_str}", True, WHITE)
            your_time_rect = your_time_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            screen.blit(your_time_text, your_time_rect)

            # Exibe o recorde
            record_str = format_time(record_time)
            record_text_surf = small_font.render(f"Recorde: {record_str}", True, WHITE)
            record_text_rect = record_text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            screen.blit(record_text_surf, record_text_rect)

            # Exibe mensagem de novo recorde
            if new_record_achieved:
                new_record_surf = record_font.render("NOVO RECORDE!", True, YELLOW)
                new_record_rect = new_record_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 70))
                screen.blit(new_record_surf, new_record_rect)
        
        # Adiciona instruções para reiniciar
        restart_text = small_font.render("Pressione R para reiniciar", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
        screen.blit(restart_text, restart_rect)
        
        # Adiciona instruções para sair
        quit_text = small_font.render("Pressione ESC para sair", True, WHITE)
        quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 200))
        screen.blit(quit_text, quit_rect)

    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:  # Reinicia o jogo
                    # Reseta todas as variáveis do jogo
                    game_over = False
                    result_text = ""
                    bg_set_index = 0
                    bg_current_frames = bg1_frames
                    last_scenario = False
                    player_pos.x = start_x
                    bot1_pos.x = start_x
                    bot2_pos.x = start_x
                    race_started = True
                    player_running = True
                    start_time = time.time()
                    last_transition_time = time.time()
                    new_record_achieved = False ### NOVO ###
                    final_time_str = "" ### NOVO ###
                    # Mostra countdown novamente
                    show_countdown()
                    # Garante que o tempo reinicie corretamente
                    start_time = time.time()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif race_started and not game_over:
                if event.key in [pygame.K_SPACE, pygame.K_RIGHT]:
                    player_pos.x += step_distance
                    player_running = True
    pygame.display.flip()

pygame.quit()
sys.exit()
