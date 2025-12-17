import pygame
import random
import math
import os
from Explosion import Explosao

pygame.init()
pygame.mixer.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Space Wars")

FPS = 60
clock = pygame.time.Clock()
explosoes = []

script_dir = os.path.dirname(os.path.abspath(__file__))

caminho_bg = os.path.join(script_dir, "sprites", "backgrounds", "background_gamebase.png")
try:
    background_img = pygame.image.load(caminho_bg).convert()
    background_img = pygame.transform.scale(background_img, (LARGURA, ALTURA))
except:
    background_img = None

caminho_som_tiro = os.path.join(script_dir, "Sounds", "tiro_jogador.wav")
try:
    som_tiro = pygame.mixer.Sound(caminho_som_tiro)
    print("Sucesso: Som do tiro carregado!")
except Exception as e:
    print(f"Erro ao carregar som: {e}")
    som_tiro = None
caminho_tiro_img = os.path.join(script_dir, "sprites", "spacewars_naves", "tiro.png")
try:
    tiro_sprite = pygame.image.load(caminho_tiro_img).convert_alpha()
    tiro_sprite = pygame.transform.scale(tiro_sprite, (15, 30))
except:
    tiro_sprite = None

barra_vida_imgs = {}
nomes_vida = {
    5: "hp_5quadrados.png",
    4: "hp_4quadrados.png",
    3: "hp_3quadrados.png",
    2: "hp_2quadrados.png",
    1: "hp_1quadrado.png",
    0: "hp_vazio.png"
}

for vida, nome in nomes_vida.items():
    caminho = os.path.join(script_dir, "sprites", "barras_de_vida", nome)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        barra_vida_imgs[vida] = pygame.transform.scale(img, (150, 150))
    except Exception as e:
        print(f"Erro ao carregar imagem de vida: {nome}. Erro: {e}")
        barra_vida_imgs[vida] = None

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image.fill((0, 255, 0))
        self.vida = 5

        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "nave_jogador.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (70, 70))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((255, 0, 0))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.mover(0, -self.velocidade)
        if keys[pygame.K_s]:
            self.mover(0, self.velocidade)
        if keys[pygame.K_a]:
            self.mover(-self.velocidade, 0)
        if keys[pygame.K_d]:
            self.mover(self.velocidade, 0)
        self.rect.x = max(0, min(self.rect.x, LARGURA - 40))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 40))

class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        if tiro_sprite:
            self.image = tiro_sprite
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.image.fill((255, 255, 0))

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()

class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))
        self.vida = 1
    def atualizar_posicao(self):
        raise NotImplementedError
    def morreu(self, explosoes):
        explosoes.append(Explosao(self.rect.center))
        self.kill()

class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboZiguezague.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((255, 0, 0))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3
        if self.rect.x <= 0 or self.rect.x >= LARGURA - 40:
            self.direcao *= -1
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()

class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)
        self.vida = 4
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboLento.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((0, 255, 0))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()

class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)
        self.vida = 2
        self.contador = 0
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboSaltador.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((230, 255, 0))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.contador += 1
        if self.contador >= 60:
            self.rect.x = random.randint(0, LARGURA - self.rect.width)
            self.contador = 0
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()

class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=6)
        self.vida = 1
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboRapido.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((0,255,0))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()

class RoboCacador(Robo):
    def __init__(self,x,y):
        super().__init__(x,y,velocidade=3)
        self.vida = 3
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboCacador.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((0,0,255))
    def atualizar_posicao(self, nave):
        limit = ALTURA * 0.8
        if self.rect.centery < limit:
            direcao = pygame.math.Vector2(nave.rect.center) - pygame.math.Vector2(self.rect.center)
            if direcao.length() != 0:
                direcao = direcao.normalize()
            else:
                direcao = pygame.math.Vector2(0, 1)
            self.rect.x += direcao.x * (self.velocidade * 0.6)
            self.rect.y += direcao.y * self.velocidade
        else:
            self.rect.y += self.velocidade
    def update(self):
        global jogador
        self.atualizar_posicao(jogador)
        if self.rect.y > ALTURA:
            self.kill()

class Robogiro(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)
        self.vida = 3
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboCiclico.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((230, 255, 0))
        self.angulo = 0
        self.raio = 40
        self.cx = x
        self.cy = y
    def atualizar_posicao(self):
        self.cy += self.velocidade
        self.angulo += 0.1
        self.rect.x = self.cx + math.cos(self.angulo) * self.raio
        self.rect.y = self.cy + math.sin(self.angulo) * self.raio
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA + 50:
            self.kill()

class BossTiro(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade=5):
        super().__init__()
        self.image = pygame.Surface((10, 18), pygame.SRCALPHA)
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade = velocidade
    def update(self):
        self.rect.y += self.velocidade
        if self.rect.y > ALTURA + 10:
            self.kill()

class BossVader(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.vida = 20  
        self.velocidade = 1.0
        try:
            img_path = os.path.join(script_dir, "sprites", "spacewars_naves", "boss_vader.png")
            img = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(img, (220, 220))
        except Exception:
            self.image = pygame.Surface((220, 220))
            self.image.fill((120, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        # modos:
        self.approach = False   
        self.active = False     
        self.pos_target_y = 90
        self.shoot_timer = 0
        self.shoot_interval = 60 
        self.descent_speed = 0.6  # velocidade mais lenta na descida
    def update(self):
        if self.approach:
            # desce reto (sem zig-zag) até a posição alvo, lentamente
            self.rect.y += self.descent_speed
            if self.rect.y >= self.pos_target_y:
                self.rect.y = self.pos_target_y
                self.approach = False
                self.active = True
                self.shoot_timer = 0
        elif self.active:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0
                t1 = BossTiro(self.rect.centerx - 30, self.rect.bottom + 10, velocidade=6)
                t2 = BossTiro(self.rect.centerx + 30, self.rect.bottom + 10, velocidade=6)
                todos_sprites.add(t1, t2)
                enemy_tiros.add(t1, t2)
        else:
            self.rect.x += math.cos(pygame.time.get_ticks() * 0.002) * 2
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > LARGURA:
                self.rect.right = LARGURA
    def morreu(self, explosoes):
        explosoes.append(Explosao(self.rect.center))
        for _ in range(8):
            explosoes.append(Explosao((
                self.rect.centerx + random.randint(-80,80),
                self.rect.centery + random.randint(-80,80)
            )))
        self.kill()

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
enemy_tiros = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

phase = 1
boss = None
boss_spawned = False
boss_active = False
phase2_hard = False  
boss_phase_start_time = 0
player_life_at_boss_start = None
boss_phase_won = False
easter_unlock_possible = False
BOSS_TRIGGER_POINTS = 30

pontos = 0
spawn_timer = 0

spawn_allowed = True
boss_spawn_delay_started = False
boss_spawn_start_time = 0
BOSS_SPAWN_DELAY_MS = 5000  # 5 segundos
player_can_shoot = True

rodando = True

def fade(screen, color=(0,0,0), mode='out', speed=8):
    overlay = pygame.Surface(screen.get_size())
    clock_local = pygame.time.Clock()
    if mode == 'out':
        for alpha in range(0, 255, speed):
            overlay.set_alpha(alpha)
            overlay.fill(color)
            screen.blit(overlay, (0,0))
            pygame.display.flip()
            clock_local.tick(60)
    else:
        for alpha in range(255, -1, -speed):
            overlay.set_alpha(alpha)
            overlay.fill(color)
            screen.blit(overlay, (0,0))
            pygame.display.flip()
            clock_local.tick(60)

def show_countdown(screen, start=3, color=(255,255,255), bg_color=(0,0,0)):
    clock_local = pygame.time.Clock()
    font_title = pygame.font.SysFont(None, 56, bold=True)
    font_big = pygame.font.SysFont(None, 140, bold=True)
    font_small = pygame.font.SysFont(None, 28)
    msg_top = "VOCÊ CONSEGUIU"
    msg_bottom = "FASE 2"
    started_msg = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - started_msg) < 2200:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(bg_color)
        screen.blit(overlay, (0,0))
        txt_top = font_title.render(msg_top, True, color)
        rect_top = txt_top.get_rect(center=(LARGURA//2, ALTURA//2 - 80))
        screen.blit(txt_top, rect_top)
        txt_bot = font_big.render(msg_bottom, True, color)
        rect_bot = txt_bot.get_rect(center=(LARGURA//2, ALTURA//2 + 20))
        screen.blit(txt_bot, rect_bot)
        pygame.display.flip()
        clock_local.tick(60)
    pygame.time.delay(200)
    number_duration = 1200
    for n in range(start, 0, -1):
        started = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - started) < number_duration:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit()
            overlay = pygame.Surface(screen.get_size())
            overlay.fill(bg_color)
            screen.blit(overlay, (0,0))
            hint = font_title.render("PRONTO?", True, color)
            rect_hint = hint.get_rect(center=(LARGURA//2, ALTURA//2 - 120))
            screen.blit(hint, rect_hint)
            numtxt = font_big.render(str(n), True, color)
            rect_num = numtxt.get_rect(center=(LARGURA//2, ALTURA//2))
            screen.blit(numtxt, rect_num)
            pygame.display.flip()
            clock_local.tick(60)
    pygame.time.delay(300)

def show_death_screen(screen, duration=1000):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((0,0,0))
    font = pygame.font.SysFont(None, 72, bold=True)
    txt = font.render("VOCÊ PERDEU", True, (255, 60, 60))
    rect = txt.get_rect(center=(LARGURA//2, ALTURA//2))
    screen.blit(overlay, (0,0))
    screen.blit(txt, rect)
    pygame.display.flip()
    pygame.time.delay(duration)

while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # só atira se player_can_shoot estiver True
                if player_can_shoot:
                    tiro = Tiro(jogador.rect.centerx, jogador.rect.y)
                    todos_sprites.add(tiro)
                    tiros.add(tiro)
                    if som_tiro:
                        som_tiro.play()

    spawn_timer += 1

    if phase == 1 and pontos >= BOSS_TRIGGER_POINTS and jogador.vida > 0:
        fade(TELA, mode='out', speed=12)
        try:
            show_countdown(TELA, start=3)
        except Exception:
            pass

        for ent in inimigos:
            ent.kill()
        for t in tiros:
            t.kill()
        for et in enemy_tiros:
            et.kill()

        # fase 2: pontos zerados, vida = 2 
        pontos = 0
        jogador.vida = 2
        spawn_timer = 0
        phase = 2
        boss_phase_start_time = pygame.time.get_ticks()
        player_life_at_boss_start = jogador.vida
        boss_spawned = False
        boss_active = False
        phase2_hard = False
        boss_phase_won = False
        easter_unlock_possible = False
        spawn_allowed = True
        boss_spawn_delay_started = False
        boss_spawn_start_time = 0
        player_can_shoot = True
        fade(TELA, mode='in', speed=12)
        print("Entrando na Fase 2: jogador com 2 vidas, pontos zerados")

    if phase == 1:
        if spawn_timer > 40:
            tipo = random.choice([RoboZigueZague, Robogiro, RoboCacador, RoboSaltador, RoboLento, RoboRapido])
            robo = tipo(random.randint(40, LARGURA - 40), -40)
            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0
    else:
        spawn_threshold = 18 if not phase2_hard else 12
        if spawn_allowed and spawn_timer > spawn_threshold and not boss_active:
            spawn_timer = 0
            if random.random() < 0.4:
                side = random.choice(['left', 'right'])
                y_pos = random.randint(60, ALTURA - 120)
                x_pos = -40 if side == 'left' else LARGURA + 40
                tipo = random.choice([RoboZigueZague, Robogiro, RoboCacador, RoboSaltador, RoboLento, RoboRapido])
                robo = tipo(x_pos, y_pos)
                todos_sprites.add(robo)
                inimigos.add(robo)
            else:
                tipo = random.choice([RoboZigueZague, Robogiro, RoboCacador, RoboSaltador, RoboLento, RoboRapido])
                robo = tipo(random.randint(40, LARGURA - 40), -40)
                todos_sprites.add(robo)
                inimigos.add(robo)

        if not phase2_hard and pontos >= 20:
            phase2_hard = True
            print("Fase 2: dificuldade aumentada (mais robôs)")

        if not boss_spawned and not boss_spawn_delay_started and pontos >= 15:
            boss_spawn_delay_started = True
            boss_spawn_start_time = pygame.time.get_ticks()
            spawn_allowed = False  
            player_can_shoot = True  
            print("Pontos >=25: iniciado delay de 5s antes de spawn do boss")

        if boss_spawn_delay_started and not boss_spawned:
            elapsed = pygame.time.get_ticks() - boss_spawn_start_time
            if elapsed >= BOSS_SPAWN_DELAY_MS:
                boss = BossVader(LARGURA // 2, -300)
                boss.approach = True
                todos_sprites.add(boss)
                inimigos.add(boss)
                boss_spawned = True
                boss_spawn_delay_started = False
                player_can_shoot = False
                print("Boss aparecendo: approach iniciado; jogador sem poder de atirar até boss ficar ativo")

        # quando boss.active True, remover as naves menores e permitir o jogador atirar
        if boss_spawned and boss is not None and boss.active and not boss_active:
            # matar todas as naves exceto o boss
            for ent in list(inimigos):
                if ent is not boss:
                    try:
                        ent.kill()
                    except:
                        pass
            boss_active = True
            player_can_shoot = True
            print("Boss ativo — outras naves removidas, jogador pode atirar")

    # colisões entre tiros do jogador e inimigos
    colisao = pygame.sprite.groupcollide(inimigos, tiros, False, True)
    for robo, lista_tiros in colisao.items():
        # contar somente os tiros que acertaram (cada tiro reduz 1 vida)
        robo.vida -= len(lista_tiros)
        if robo.vida <= 0:
            try:
                robo.morreu(explosoes)
            except Exception:
                explosoes.append(Explosao(robo.rect.center))
                robo.kill()
            pontos += 1

    # colisões entre tiros inimigos (boss) e jogador
    hits_bullets = pygame.sprite.spritecollide(jogador, enemy_tiros, True)
    if hits_bullets:
        jogador.vida -= len(hits_bullets)

    # colisões jogador x inimigos (naves que batem)
    hits = pygame.sprite.spritecollide(jogador, inimigos, True)
    if hits:
        jogador.vida -= len(hits)

    # atualizar sprites e explosões
    todos_sprites.update()
    for explosao in explosoes[:]:
        explosao.update()
        if explosao.ended():
            explosoes.remove(explosao)

    # checar vitória da fase 2: se boss morto volta pra fase 1
    if phase == 2 and boss_spawned:
        boss_alive = any(isinstance(e, BossVader) for e in inimigos)
        if not boss_alive:
            boss_phase_won = True
            if player_life_at_boss_start is not None and jogador.vida == player_life_at_boss_start:
                easter_unlock_possible = True
            else:
                easter_unlock_possible = False
            phase = 1
            spawn_timer = 0
            boss = None
            boss_spawned = False
            boss_active = False
            phase2_hard = False
            spawn_allowed = True
            boss_spawn_delay_started = False
            player_can_shoot = True
            print("Fase 2 vencida! easter_unlock_possible =", easter_unlock_possible)

    # desenhar
    if background_img:
        TELA.blit(background_img, (0, 0))
    else:
        if phase == 2:
            TELA.fill((30, 10, 30))
        else:
            TELA.fill((20, 20, 20))

    todos_sprites.draw(TELA)
    for explosao in explosoes:
        explosao.draw(TELA)

    # HUD: pontos em cima; vidas abaixo com a imagem alinhada ao lado do texto "Vidas:"
    font = pygame.font.SysFont(None, 30)
    texto_pontos = font.render(f"Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto_pontos, (10, 10))

    texto_vidas = font.render("Vidas:", True, (255, 255, 255))
    y_vidas = 10 + texto_pontos.get_height() + 8
    TELA.blit(texto_vidas, (10, y_vidas))

    img_vida = barra_vida_imgs.get(jogador.vida)
    if img_vida:
        image_x = 10 + texto_vidas.get_width() + 8
        image_y = y_vidas + (texto_vidas.get_height() - img_vida.get_height()) // 2
        TELA.blit(img_vida, (image_x, image_y))

    font_small = pygame.font.SysFont(None, 24)
    fase_txt = "Fase 1" if phase == 1 else "Fase 2 - Boss"
    TELA.blit(font_small.render(fase_txt, True, (200,200,200)), (650, 10))

    pygame.display.flip()

    # checar morte do jogador
    if jogador.vida <= 0:
        show_death_screen(TELA, duration=1000)
        pygame.time.delay(200)
        rodando = False

pygame.quit()