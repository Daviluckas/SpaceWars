import pygame
import random
import math
from Explosion import Explosao
pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")

FPS = 60
clock = pygame.time.Clock()
explosoes = []

# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image.fill((0, 255, 0))  # verde
        self.vida = 5

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

        # limites de tela
        self.rect.x = max(0, min(self.rect.x, LARGURA - 40))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 40))


# TIRO (DO JOGADOR)
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image.fill((255, 255, 0))  # amarelo

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))  # vermelho
        self.vida = 1
    def atualizar_posicao(self):
        raise NotImplementedError
    def morreu(self, explosoes):
        explosoes.append(Explosao(self.rect.center))
        self.kill()


# ROBO EXEMPLO — ZigueZague
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3

        if self.rect.x <= 0 or self.rect.x >= LARGURA - 40:
            self.direcao *= -1

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()
# ROBO — Lento
class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)
        self.image.fill((0,255,0))
        self.vida = 4
    def atualizar_posicao(self):
        self.rect.y += self.velocidade

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()
# ROBO — Saltador
class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)
        self.image.fill((230,255,0))
        self.vida = 2
        self.contador = 0
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.contador += 1
        if self.contador >= 60:
            self.rect.x = random.randint(0,LARGURA - self.rect.width)
            self.contador = 0
    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()
# ROBO — Rápido
class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=6)
        self.image.fill((0,255,0))
        self.vida = 1
    def atualizar_posicao(self):
        self.rect.y += self.velocidade

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()
# ROBO CAÇADOR
class RoboCacador(Robo):
    def __init__(self,x,y):
        super().__init__(x,y,velocidade=3)
        self.image.fill((0,0,255))
        self.vida = 3
    def atualizar_posicao(self, nave):
        limit = ALTURA * 0.8
        # Verifica se o alien está acima da metade da tela
        # e a nave está abaixo dele
        if self.rect.centery < limit:
            # Persegue a nave
            direcao = pygame.math.Vector2(nave.rect.center) - pygame.math.Vector2(self.rect.center)
            if direcao.length() != 0:
                direcao = direcao.normalize()
            else:
                direcao = pygame.math.Vector2(0, 1)

            self.rect.x += direcao.x * (self.velocidade * 0.6)
            self.rect.y += direcao.y * self.velocidade
        else:
            # Se a nave estiver acima ou o alien passou do condicionado, desce reto
            self.rect.y += self.velocidade
    
    def update(self):
        global jogador
        self.atualizar_posicao(jogador)
        if self.rect.y > ALTURA:
            self.kill()

# ROBO GIRO 
class Robogiro(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)
        self.vida = 3
        # ângulo do círculo
        self.angulo = 0

        # raio do círculo
        self.raio = 40

        # centro do círculo (caminha pra baixo)
        self.cx = x
        self.cy = y

    def atualizar_posicao(self):


        # centro desce devagar
        self.cy += self.velocidade

        # aumenta o ângulo para girar o círculo
        self.angulo += 0.1  # velocidade do giro

        # nova posição circular
        self.rect.x = self.cx + math.cos(self.angulo) * self.raio
        self.rect.y = self.cy + math.sin(self.angulo) * self.raio

    def update(self):
        self.atualizar_posicao()

        # se sair da tela, remove
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

    # timer de entrada dos inimigos
    spawn_timer += 1
    if spawn_timer > 40:
        tipo = random.choice([RoboZigueZague, Robogiro, RoboCacador,RoboSaltador,RoboLento,RoboRapido])
        robo = tipo(random.randint(40, LARGURA - 40), -40)
        todos_sprites.add(robo)
        inimigos.add(robo)
        spawn_timer = 0

    # colisão tiro x robô
    colisao = pygame.sprite.groupcollide(inimigos, tiros, False, True)
    for robo, lista_tiros in colisao.items():
        robo.vida -= len(lista_tiros)
        if robo.vida <= 0:
            robo.morreu(explosoes)
            pontos += 1
    # colisão robô x jogador
    if pygame.sprite.spritecollide(jogador, inimigos, True):
        jogador.vida -= 1
        if jogador.vida <= 0:
            print("GAME OVER!")
            rodando = False

    # atualizar
    todos_sprites.update()
    # Roda explosão
    for explosao in explosoes[:]:
        explosao.update()
        if explosao.ended():
            explosoes.remove(explosao)
    # desenhar
    TELA.fill((20, 20, 20))
    todos_sprites.draw(TELA)
    # Desenhar explosão
    for explosao in explosoes:
        explosao.draw(TELA)
    #Painel de pontos e vida
    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

    pygame.display.flip()

pygame.quit()