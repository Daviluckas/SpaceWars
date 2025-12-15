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
    caminho = os.path.join(script_dir, "sprites", "barra_de_vida", nome)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        barra_vida_imgs[vida] = pygame.transform.scale(img, (150, 150))
    except:
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

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

pontos = 0
spawn_timer = 0

rodando = True
while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tiro = Tiro(jogador.rect.centerx, jogador.rect.y)
                todos_sprites.add(tiro)
                tiros.add(tiro)
                if som_tiro:
                    som_tiro.play()

    spawn_timer += 1
    if spawn_timer > 40:
        tipo = random.choice([RoboZigueZague, Robogiro, RoboCacador, RoboSaltador, RoboLento, RoboRapido])
        robo = tipo(random.randint(40, LARGURA - 40), -40)
        todos_sprites.add(robo)
        inimigos.add(robo)
        spawn_timer = 0

    colisao = pygame.sprite.groupcollide(inimigos, tiros, False, True)
    for robo, lista_tiros in colisao.items():
        robo.vida -= len(lista_tiros)
        if robo.vida <= 0:
            robo.morreu(explosoes)
            pontos += 1

    if pygame.sprite.spritecollide(jogador, inimigos, True):
        jogador.vida -= 1

    todos_sprites.update()
    for explosao in explosoes[:]:
        explosao.update()
        if explosao.ended():
            explosoes.remove(explosao)

    if background_img:
        TELA.blit(background_img, (0, 0))
    else:
        TELA.fill((20, 20, 20))

    todos_sprites.draw(TELA)
    for explosao in explosoes:
        explosao.draw(TELA)

    img_vida = barra_vida_imgs.get(jogador.vida)
    if img_vida:
    # X = 10 (alinhado com o texto)
    # Y = 45 (um pouco abaixo do texto)
        TELA.blit(img_vida, (3, 10))

    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vidas:", True, (255, 255, 255))
    TELA.blit(texto, (30, 30))

    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

    pygame.display.flip()
    
    if jogador.vida <= 0:
        pygame.time.delay(1000)
        rodando = False

pygame.quit()