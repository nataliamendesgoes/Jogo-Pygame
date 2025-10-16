

WIDTH = 800
HEIGHT = 600
TILE_SIZE = 8
MAP_COLS = WIDTH // TILE_SIZE
MAP_ROWS = HEIGHT // TILE_SIZE

import random
estado = "menu"
ganhou = False
perdeu = False
volume_on = True
menu_music_playing = False
game_music_playing = False

saida = Actor("sair")
volume = Actor("volume")




def gerar_mapa_roguelike(cols, rows, num_salas=8, min_tam=6, max_tam=16):
    mapa = [['parede' for _ in range(cols)] for _ in range(rows)]
    salas = []
    for _ in range(num_salas):
        w = random.randint(min_tam, max_tam)
        h = random.randint(min_tam, max_tam)
        x = random.randint(1, cols-w-2)
        y = random.randint(1, rows-h-2)
        nova_sala = (x, y, w, h)
        sobrepoe = False
        for sala in salas:
            if (x < sala[0]+sala[2] and x+w > sala[0] and y < sala[1]+sala[3] and y+h > sala[1]):
                sobrepoe = True
                break
        if not sobrepoe:
            salas.append(nova_sala)
            for i in range(x, x+w):
                for j in range(y, y+h):
                    mapa[j][i] = 'chao'
            if len(salas) > 1:
                x1, y1 = x + w//2, y + h//2
                x2, y2 = salas[-2][0] + salas[-2][2]//2, salas[-2][1] + salas[-2][3]//2
                for i in range(min(x1, x2), max(x1, x2)+1):
                    mapa[y1][i] = 'chao'
                for j in range(min(y1, y2), max(y1, y2)+1):
                    mapa[j][x2] = 'chao'
    return mapa


mapa = gerar_mapa_roguelike(MAP_COLS, MAP_ROWS, num_salas=12, min_tam=8, max_tam=18)

player_image_right = "personagem2"
player_image_left = "personagem5"

chao_livres = [(x, y) for y in range(MAP_ROWS) for x in range(MAP_COLS) if mapa[y][x] == 'chao']
player_start = random.choice(chao_livres)
player = Actor("personagem1", (player_start[0]*TILE_SIZE+TILE_SIZE//2, player_start[1]*TILE_SIZE+TILE_SIZE//2))
player.lives = 2
player_image = player.image

NUM_ESTRELAS = 3
estrelas = []
for _ in range(NUM_ESTRELAS):
    ex, ey = random.choice(chao_livres)
    estrelas.append(Actor("estrela_cheia", (ex*TILE_SIZE+TILE_SIZE//2, ey*TILE_SIZE+TILE_SIZE//2)))
estrelas_coletadas = 0

monstro_frames_right = ["monstro_2"]
monstro_frames_left = ["monstro_3"]
monstros = []
for i in range(2):
    mx, my = random.choice(chao_livres)
    m = Actor("monstro_1", (mx*TILE_SIZE+TILE_SIZE//2, my*TILE_SIZE+TILE_SIZE//2))
    m.frame_idx = 0
    m.anim_timer = 0
    m.vx = random.choice([-1,1])
    m.vy = random.choice([-1,1])
    monstros.append(m)



def draw():
    screen.clear()
    if estado == "menu":
        desenhar_menu()
    elif estado == "jogo":
        desenhar_jogo()

def desenhar_jogo():
    global menu_music_playing, game_music_playing, volume_on
    # Inicia música do jogo se ainda não estiver tocando
    if not game_music_playing:
        try:
            # ajusta volumes conforme flag
            sounds.audio_jogo.stop()
            if volume_on:
                sounds.audio_inicio.set_volume(1.0)
                sounds.audio_inicio.play(-1)
            else:
                sounds.audio_inicio.set_volume(0.0)
            game_music_playing = True
            menu_music_playing = False
        except Exception:
            pass
    for y, linha in enumerate(mapa):
        for x, tile in enumerate(linha):
            if tile == 'chao':
                screen.blit("chao", (x*TILE_SIZE, y*TILE_SIZE))  
            else:
                screen.blit("parede", (x*TILE_SIZE, y*TILE_SIZE))  
    for estrela in estrelas:
        estrela.draw()
    for monstro in monstros:
        monstro.draw()
    player.draw()
    for i in range(2):
        if player.lives > i:
            screen.blit("coracao_cheio", (10 + i*20, 10))
        else:
            screen.blit("coracao_vazio", (10 + i*20, 10))
    for i in range(NUM_ESTRELAS):
        if i < estrelas_coletadas:
            screen.blit("estrela_cheia", (WIDTH - 30 - i*30, 10))
        else:
            screen.blit("estrela_vazia", (WIDTH - 30 - i*30, 10))

    if ganhou:
        screen.draw.filled_rect(Rect((0,0),(WIDTH,HEIGHT)), (0,0,0))
        screen.draw.text("VOCE VENCEU!", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="yellow")
    elif perdeu:
        screen.draw.filled_rect(Rect((0,0),(WIDTH,HEIGHT)), (0,0,0))
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="red")

def update():
    global ganhou, perdeu, player_image
    if estado != "jogo" or ganhou or perdeu:
        return
    dx = dy = 0
    if keyboard.left:
        dx = -2
        player_image = "personagem5"
    elif keyboard.right:
        dx = 2
        player_image = "personagem2"
    if keyboard.up:
        dy = -2
    if keyboard.down:
        dy = 2
    mover_ator(player, dx, dy)
    player.image = player_image

    for monstro in monstros:
        mover_ator(monstro, monstro.vx, monstro.vy)
        frames = monstro_frames_left if monstro.vx < 0 else monstro_frames_right
        if not posicao_livre(monstro.x + monstro.vx, monstro.y, monstro):
            monstro.vx *= -1
        if not posicao_livre(monstro.x, monstro.y + monstro.vy, monstro):
            monstro.vy *= -1
        animar_sprite(monstro, frames, 0.12)

    global estrelas_coletadas
    for estrela in estrelas[:]:
        if player.colliderect(estrela):
            estrelas.remove(estrela)
            estrelas_coletadas += 1
    if estrelas_coletadas == NUM_ESTRELAS:
        ganhou = True

    for monstro in monstros:
        if player.colliderect(monstro):
            player.lives -= 1
            sounds.eep.play()
            player.image = "personagem4"
            player.pos = (player_start[0]*TILE_SIZE+TILE_SIZE//2, player_start[1]*TILE_SIZE+TILE_SIZE//2)
            if player.lives <= 0:
                perdeu = True
            else:
                clock.schedule_unique(lambda: setattr(player, 'image', player_image), 0.5)
            break

def mover_ator(ator, dx, dy):
    novo_x = ator.x + dx
    novo_y = ator.y + dy
    if posicao_livre(novo_x, ator.y, ator):
        ator.x = novo_x
    if posicao_livre(ator.x, novo_y, ator):
        ator.y = novo_y

def posicao_livre(x, y, ator):
    grid_x = int(x // TILE_SIZE)
    grid_y = int(y // TILE_SIZE)
    if 0 <= grid_x < MAP_COLS and 0 <= grid_y < MAP_ROWS:
        return mapa[grid_y][grid_x] == 'chao'
    return False

def animar_sprite(ator, frames, velocidade):
    ator.anim_timer += velocidade
    if ator.anim_timer >= 1:
        ator.anim_timer = 0
        ator.frame_idx = (ator.frame_idx + 1) % len(frames)
        ator.image = frames[ator.frame_idx]


def desenhar_menu():
    screen.fill((236, 180, 202))
    global menu_music_playing, game_music_playing, volume_on
    if not menu_music_playing:
        try:
            sounds.audio_inicio.stop()
            if volume_on:
                sounds.audio_jogo.set_volume(1.0)
                sounds.audio_jogo.play(-1)
            else:
                sounds.audio_jogo.set_volume(0.0)
            menu_music_playing = True
            game_music_playing = False
        except Exception:
            pass
    screen.draw.text("Labirinto das Estrelas", center=(WIDTH//2, 150), fontsize=80, color="white")
    global botao_rect
    botao_rect = Rect((WIDTH//2-100, 300), (200, 60))
    screen.draw.filled_rect(botao_rect, (179, 70, 113))
    volume.topright = (90, 10)
    saida.topright = (WIDTH - 10, 10)
    volume.draw()
    saida.draw()
    screen.draw.text("Iniciar", center=botao_rect.center, fontsize=40, color="White")



def on_mouse_down(pos, button):
    global estado, volume_on
    if estado == "menu":
        if botao_rect.collidepoint(pos):
            estado = "jogo"
            return
        elif volume.collidepoint(pos):
            volume_on = not volume_on
            for name in ("audio_jogo", "audio_inicio", "eep"):
                try:
                    snd = getattr(sounds, name)
                    snd.set_volume(1.0 if volume_on else 0.0)
                except Exception:
                    pass
            volume.image = "volume" if volume_on else "mudo"
            return
        elif saida.collidepoint(pos):
            import sys
            sys.exit()




