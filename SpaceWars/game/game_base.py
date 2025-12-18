import subprocess
import sys
import os
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
except:
    som_tiro = None

caminho_musica_bg = os.path.join(script_dir, "Sounds", "background_music.mp3")
try:
    pygame.mixer.music.load(caminho_musica_bg)
    pygame.mixer.music.set_volume(0.3)  
    pygame.mixer.music.play(-1) 
except:
    pass

caminho_musica_boss = os.path.join(script_dir, "Sounds", "music_darthvader.wav")
musica_atual = "bg"


caminho_tiro_img = os.path.join(script_dir, "sprites", "spacewars_naves", "tiro.png")
try:
    tiro_sprite = pygame.image.load(caminho_tiro_img).convert_alpha()
    tiro_sprite = pygame.transform.scale(tiro_sprite, (15, 30))
except:
    tiro_sprite = None

barra_vida_imgs = {}
nomes_vida = {5: "hp_5quadrados.png", 4: "hp_4quadrados.png", 3: "hp_3quadrados.png", 2: "hp_2quadrados.png", 1: "hp_1quadrado.png", 0: "hp_vazio.png"}
for vida, nome in nomes_vida.items():
    caminho = os.path.join(script_dir, "sprites", "barras_de_vida", nome)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        barra_vida_imgs[vida] = pygame.transform.scale(img, (150, 150))
    except:
        barra_vida_imgs[vida] = None

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.tipo = tipo
        self.velocidade = 3

        caminhos = {
            'tiro': "powerup_tiro3x.png",
            'velocidade': "powerup_velocidade.png",
            'vida': "powerup_vidaextra.png"
        }

        caminho_img = os.path.join(
            script_dir,
            "sprites",
            "powerups",
            caminhos[tipo]
        )

        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (80, 80))
        except Exception as e:
            print("ERRO AO CARREGAR POWERUP:", caminho_img)
            print(e)
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            self.image.fill((255, 0, 255)) 

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA:
            self.kill()

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
        super().__init__(x, y, 8)
        self.vida = 5
        self.cooldown_tiro = 0 
        self.tiro_triplo = False
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "nave_jogador.png")
        try:
            imagem_original = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(imagem_original, (70, 70))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            self.image.fill((255, 0, 0))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.mover(0, -self.velocidade)
        if keys[pygame.K_s]: self.mover(0, self.velocidade)
        if keys[pygame.K_a]: self.mover(-self.velocidade, 0)
        if keys[pygame.K_d]: self.mover(self.velocidade, 0)
        self.rect.x = max(0, min(self.rect.x, LARGURA - 40))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 40))
        if self.cooldown_tiro > 0: self.cooldown_tiro -= 1
        if keys[pygame.K_SPACE] and self.cooldown_tiro == 0 and player_can_shoot:
            self.atirar()

    def atirar(self):
        if self.tiro_triplo:
            offsets = [-20, 0, 20]
            for off in offsets:
                t = Tiro(self.rect.centerx + off, self.rect.y)
                todos_sprites.add(t)
                tiros.add(t)
        else:
            tiro = Tiro(self.rect.centerx, self.rect.y)
            todos_sprites.add(tiro)
            tiros.add(tiro)
        if som_tiro: som_tiro.play()
        self.cooldown_tiro = 8

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
        if self.rect.y < 0: self.kill()

class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))
        self.vida = 1
    def atualizar_posicao(self): raise NotImplementedError
    def morreu(self, explosoes):
        explosoes.append(Explosao(self.rect.center))
        self.kill()

class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboZiguezague.png")
        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except: self.image.fill((255, 0, 0))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3
        if self.rect.x <= 0 or self.rect.x >= LARGURA - 40: self.direcao *= -1
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA: self.kill()

class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)
        self.vida = 4
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboLento.png")
        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except: self.image.fill((0, 255, 0))
    def atualizar_posicao(self): self.rect.y += self.velocidade
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA: self.kill()

class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)
        self.vida = 2
        self.contador = 0
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboSaltador.png")
        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except: self.image.fill((230, 255, 0))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.contador += 1
        if self.contador >= 60:
            self.rect.x = random.randint(0, LARGURA - self.rect.width)
            self.contador = 0
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA: self.kill()

class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=6)
        self.vida = 1
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboRapido.png")
        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except: self.image.fill((0,255,0))
    def atualizar_posicao(self): self.rect.y += self.velocidade
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA: self.kill()

class RoboCacador(Robo):
    def __init__(self,x,y):
        super().__init__(x,y,velocidade=3)
        self.vida = 3
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboCacador.png")
        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except: self.image.fill((0,0,255))
    def atualizar_posicao(self, nave):
        limit = ALTURA * 0.8
        if self.rect.centery < limit:
            direcao = pygame.math.Vector2(nave.rect.center) - pygame.math.Vector2(self.rect.center)
            if direcao.length() != 0: direcao = direcao.normalize()
            else: direcao = pygame.math.Vector2(0, 1)
            self.rect.x += direcao.x * (self.velocidade * 0.6)
            self.rect.y += direcao.y * self.velocidade
        else: self.rect.y += self.velocidade
    def update(self):
        self.atualizar_posicao(jogador)
        if self.rect.y > ALTURA: self.kill()

class Robogiro(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)
        self.vida = 3
        caminho_img = os.path.join(script_dir, "sprites", "spacewars_naves", "roboCiclico.png")
        try:
            img = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(img, (100, 100))
            self.rect = self.image.get_rect(center=(x, y))
        except: self.image.fill((230, 255, 0))
        self.angulo = 0
        self.raio = 40
        self.cx, self.cy = x, y
    def atualizar_posicao(self):
        self.cy += self.velocidade
        self.angulo += 0.1
        self.rect.x = self.cx + math.cos(self.angulo) * self.raio
        self.rect.y = self.cy + math.sin(self.angulo) * self.raio
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA + 50: self.kill()

class BossTiro(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade=5):
        super().__init__()
        self.image = pygame.Surface((10, 18), pygame.SRCALPHA)
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade = velocidade
    def update(self):
        self.rect.y += self.velocidade
        if self.rect.y > ALTURA + 10: self.kill()

class BossVader(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.vida = 80  
        self.velocidade = 1.0
        try:
            img_path = os.path.join(script_dir, "sprites", "spacewars_naves", "nave_darth_vader.png")
            img = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(img, (220, 220))
        except:
            self.image = pygame.Surface((220, 220))
            self.image.fill((120, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.approach = False   
        self.active = False     
        self.pos_target_y = 90
        self.shoot_timer = 0
        self.shoot_interval = 60 
        self.descent_speed = 2.0
    def update(self):
        if self.approach:
            self.rect.y += self.descent_speed
            if self.rect.y >= self.pos_target_y:
                self.rect.y = self.pos_target_y
                self.approach, self.active = False, True
                self.shoot_timer = 0
        elif self.active:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0
                t1 = BossTiro(self.rect.centerx - 30, self.rect.bottom + 10, 6)
                t2 = BossTiro(self.rect.centerx + 30, self.rect.bottom + 10, 6)
                todos_sprites.add(t1, t2)
                enemy_tiros.add(t1, t2)
            self.rect.x += math.cos(pygame.time.get_ticks() * 0.002) * 2
            if self.rect.left < 0: self.rect.left = 0
            if self.rect.right > LARGURA: self.rect.right = LARGURA
    def morreu(self, explosoes):
        explosoes.append(Explosao(self.rect.center))
        for _ in range(8):
            explosoes.append(Explosao((self.rect.centerx + random.randint(-80,80), self.rect.centery + random.randint(-80,80))))
        self.kill()

def fade(screen, color=(0,0,0), mode='out', speed=8):
    overlay = pygame.Surface(screen.get_size())
    clock_local = pygame.time.Clock()
    for alpha in (range(0, 255, speed) if mode == 'out' else range(255, -1, -speed)):
        overlay.set_alpha(alpha)
        overlay.fill(color)
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        clock_local.tick(60)

def show_countdown(screen, start=3, color=(255,255,255), bg_color=(0,0,0)):
    clock_local = pygame.time.Clock()
    font_title = pygame.font.SysFont(None, 56, bold=True)
    font_big = pygame.font.SysFont(None, 140, bold=True)
    started_msg = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - started_msg) < 2200:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); raise SystemExit()
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(bg_color)
        screen.blit(overlay, (0,0))
        txt_top = font_title.render("VOCÊ CONSEGUIU", True, color)
        screen.blit(txt_top, txt_top.get_rect(center=(LARGURA//2, ALTURA//2 - 80)))
        txt_bot = font_big.render("FASE 2", True, color)
        screen.blit(txt_bot, txt_bot.get_rect(center=(LARGURA//2, ALTURA//2 + 20)))
        pygame.display.flip()
        clock_local.tick(60)
    for n in range(start, 0, -1):
        started = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - started) < 1200:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); raise SystemExit()
            overlay = pygame.Surface(screen.get_size())
            overlay.fill(bg_color)
            screen.blit(overlay, (0,0))
            hint = font_title.render("PRONTO?", True, color)
            screen.blit(hint, hint.get_rect(center=(LARGURA//2, ALTURA//2 - 120)))
            numtxt = font_big.render(str(n), True, color)
            screen.blit(numtxt, numtxt.get_rect(center=(LARGURA//2, ALTURA//2)))
            pygame.display.flip()
            clock_local.tick(60)

def show_death_screen(screen, duration=1000):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((0,0,0))
    font = pygame.font.SysFont(None, 72, bold=True)
    txt = font.render("VOCÊ PERDEU", True, (255, 60, 60))
    screen.blit(overlay, (0,0))
    screen.blit(txt, txt.get_rect(center=(LARGURA//2, ALTURA//2)))
    pygame.display.flip()
    pygame.time.delay(duration)
    
def close_circle_wipe(screen, speed=12):
    center_x, center_y = LARGURA // 2, ALTURA // 2
    radius = int(math.hypot(LARGURA / 2, ALTURA / 2)) 

    while radius > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        
        temp_surface = pygame.Surface((LARGURA, ALTURA))
        temp_surface.fill((0, 0, 0)) # Fundo preto
        
        pygame.draw.circle(temp_surface, (255, 255, 255), (center_x, center_y), radius)
        temp_surface.set_colorkey((255, 255, 255)) 
        
        if background_img: screen.blit(background_img, (0, 0))
        else: screen.fill((30, 10, 30))
        
        screen.blit(temp_surface, (0, 0))
        
        radius -= speed
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill((0, 0, 0))
    pygame.display.flip()

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
enemy_tiros = pygame.sprite.Group()
powerups = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

phase, pontos, spawn_timer = 1, 0, 0
boss = None
boss_spawned = boss_active = False
spawn_allowed = player_can_shoot = True
boss_spawn_delay_started = False
BOSS_TRIGGER_POINTS = 30
BOSS_SPAWN_DELAY_MS = 2000
rodando = True

while rodando:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: rodando = False
        
    spawn_timer += 1
    if phase == 1 and pontos >= BOSS_TRIGGER_POINTS and jogador.vida > 0:
        fade(TELA, mode='out', speed=12)
        show_countdown(TELA)
        for ent in inimigos: ent.kill()
        for t in tiros: t.kill()
        for et in enemy_tiros: et.kill()
        pontos, jogador.vida, phase = 0, 3, 2
        jogador.tiro_triplo = True
        boss_spawned = boss_active = False
        spawn_allowed = player_can_shoot = True
        fade(TELA, mode='in', speed=12)

    if phase == 1:
        if spawn_timer > 40:
            tipo = random.choice([RoboZigueZague, Robogiro, RoboCacador, RoboSaltador, RoboLento, RoboRapido])
            robo = tipo(random.randint(40, LARGURA - 40), -40)
            todos_sprites.add(robo); inimigos.add(robo)
            spawn_timer = 0
    else:
        if spawn_allowed and spawn_timer > 18 and not boss_active:
            spawn_timer = 0
            robo = random.choice([RoboZigueZague, Robogiro, RoboCacador, RoboSaltador, RoboLento, RoboRapido])(random.randint(40, LARGURA - 40), -40)
            todos_sprites.add(robo); inimigos.add(robo)
        if not boss_spawned and not boss_spawn_delay_started and pontos >= 60:
            boss_spawn_delay_started = True
            boss_spawn_start_time = pygame.time.get_ticks()
            spawn_allowed = False
            for ent in list(inimigos):
                explosoes.append(Explosao(ent.rect.center))
                ent.kill()

        if boss_spawn_delay_started and not boss_spawned:
            if pygame.time.get_ticks() - boss_spawn_start_time >= BOSS_SPAWN_DELAY_MS:
                boss = BossVader(LARGURA // 2, -300)
                boss.approach = True
                todos_sprites.add(boss); inimigos.add(boss)
                boss_spawned, player_can_shoot = True, False
                boss_spawn_delay_started = False
        if boss_spawned and boss.active and not boss_active:
            for ent in list(inimigos):
                if ent is not boss:
                    ent.kill()

            boss_active = True
            player_can_shoot = True

            if musica_atual != "boss":
                pygame.mixer.music.stop()
                pygame.mixer.music.load(caminho_musica_boss)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                musica_atual = "music_darthvader"

        if boss_active and random.randint(1, 150) == 1:
            pu = PowerUp(random.randint(40, LARGURA-40), -40, random.choice(['tiro', 'velocidade', 'vida']))
            powerups.add(pu)

    todos_sprites.update()
    powerups.update()

    hits_pu = pygame.sprite.spritecollide(jogador, powerups, True)
    for pu in hits_pu:
        if pu.tipo == 'tiro': jogador.tiro_triplo = True
        elif pu.tipo == 'velocidade': jogador.velocidade = 12
        elif pu.tipo == 'vida':
            if jogador.vida < 5: jogador.vida += 1

    colisao = pygame.sprite.groupcollide(inimigos, tiros, False, True)
    
    for robo, lista_tiros in colisao.items():
        qtd_acertos = len(lista_tiros)
        if isinstance(robo, BossVader):
            pontos += qtd_acertos
            robo.vida -= qtd_acertos
            
            if pontos >= 150:
                robo.morreu(explosoes)
                tempo_inicio = pygame.time.get_ticks()
                while pygame.time.get_ticks() - tempo_inicio < 2000:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    
                    if background_img: TELA.blit(background_img, (0, 0))
                    else: TELA.fill((30, 10, 30))
        
                    for exp in explosoes[:]:
                        exp.update()
                        exp.draw(TELA)
                    TELA.blit(font.render(f"Pontos: {pontos}", True, (255, 255, 255)), (10, 10))
                    
                    pygame.display.flip()
                    clock.tick(60)

                close_circle_wipe(TELA, speed=15)
                pygame.mixer.music.stop()
                pygame.quit()
                import subprocess, sys
                caminho_ee = os.path.join(script_dir, "easter_egg.py")
                subprocess.Popen([sys.executable, caminho_ee])
                sys.exit()

        else:
            robo.vida -= qtd_acertos
            if robo.vida <= 0:
                robo.morreu(explosoes)
                pontos += 1

    if pygame.sprite.spritecollide(jogador, enemy_tiros, True) or pygame.sprite.spritecollide(jogador, inimigos, True):
        jogador.vida -= 1

    for exp in explosoes[:]:
        exp.update()
        if exp.ended(): explosoes.remove(exp)

    if phase == 2 and boss_spawned and not any(isinstance(e, BossVader) for e in inimigos):
        phase, pontos, boss_spawned = 1, 0, False
        boss_active = False
        jogador.tiro_triplo = False
        jogador.velocidade = 8

    if background_img: TELA.blit(background_img, (0, 0))
    else: TELA.fill((30, 10, 30) if phase == 2 else (20, 20, 20))
    
    todos_sprites.draw(TELA)
    powerups.draw(TELA)
    for exp in explosoes: exp.draw(TELA)
    
    font = pygame.font.SysFont(None, 30)
    TELA.blit(font.render(f"Pontos: {pontos}", True, (255, 255, 255)), (10, 10))
    TELA.blit(font.render("", True, (255, 255, 255)), (10, 40))
    if barra_vida_imgs.get(jogador.vida): TELA.blit(barra_vida_imgs[jogador.vida], (70, -15))
    
    pygame.display.flip()
    if jogador.vida <= 0: show_death_screen(TELA); rodando = False

pygame.quit()