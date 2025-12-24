import pygame
import sys
import os
import math
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Space Wars - O Lado Sombrio")

clock = pygame.time.Clock()
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_path(*args):
    return os.path.join(script_dir, "sprites", *args)

def scale_proportional(image, new_width=None):
    w, h = image.get_size()
    if new_width:
        ratio = new_width / w
        return pygame.transform.smoothscale(image, (int(w * ratio), int(h * ratio)))
    return image

try:
    bg_raw = pygame.image.load(get_path("backgrounds", "background_easter_egg.png")).convert()
    bg_ee = pygame.transform.smoothscale(bg_raw, (LARGURA, ALTURA))
    sid_proposta = scale_proportional(pygame.image.load(get_path("easterEgg_images", "sidious_proposta.png")), 420)
    sid_feliz = scale_proportional(pygame.image.load(get_path("easterEgg_images", "sidious_feliz.png")), 420)
    sid_bravo = scale_proportional(pygame.image.load(get_path("easterEgg_images", "sidious_bravo.png")), 420)
    btn_sim_img = scale_proportional(pygame.image.load(get_path("botoes", "botao_sim.png")), 140)
    btn_nao_img = scale_proportional(pygame.image.load(get_path("botoes", "botao_nao.png")), 140)
    img_death_star = scale_proportional(pygame.image.load(get_path("easterEgg_images", "death_star_spacewars.png")), 240)
    img_nave_player = scale_proportional(pygame.image.load(get_path("spacewars_naves", "nave_jogador.png")), 60)
    img_ziguezague = scale_proportional(pygame.image.load(get_path("spacewars_naves", "roboZiguezague.png")), 50) 
except Exception as e:
    print(f"Erro assets: {e}")

class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao, dx=0):
        super().__init__()
        self.image = pygame.Surface((6, 20))
        cor = (0, 255, 255) if direcao < 0 else (255, 50, 50)
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 12 * direcao
        self.speed_x = dx
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.top > ALTURA: self.kill()

class RoboZigueZague(pygame.sprite.Sprite):
    def __init__(self, x, y_final):
        super().__init__()
        self.image = img_ziguezague
        self.rect = self.image.get_rect(center=(x, -50))
        self.y_final = y_final
        self.speed_x = random.choice([-2, 2])
        self.descendo = True
    def update(self):
        if self.descendo:
            self.rect.y += 3
            if self.rect.y >= self.y_final:
                self.descendo = False
        else:
            self.rect.x += self.speed_x
            if self.rect.left <= 50 or self.rect.right >= LARGURA - 50:
                self.speed_x *= -1

def circulo_wipe():
    raio = 0
    while raio < 1000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        TELA.blit(bg_ee, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 0, 0))
        pygame.draw.circle(overlay, (255, 255, 255), (LARGURA//2, ALTURA//2), raio)
        overlay.set_colorkey((255, 255, 255))
        TELA.blit(overlay, (0, 0))
        raio += 10 
        pygame.display.flip(); clock.tick(60)

def animar_descida(img):
    y = ALTURA - img.get_height() - 5
    while y < ALTURA + 100:
        y += 8
        TELA.blit(bg_ee, (0, 0)); TELA.blit(img, (0, y))
        pygame.display.flip(); clock.tick(60)

def animar_troca(img_velha, img_nova, primeira_vez=False):
    y_alvo = ALTURA - img_nova.get_height() - 5
    y = ALTURA + 10 if primeira_vez else y_alvo
    if not primeira_vez and img_velha:
        while y < ALTURA + 10:
            y += 12
            TELA.blit(bg_ee, (0, 0)); TELA.blit(img_velha, (0, y))
            pygame.display.flip(); clock.tick(60)
    while y > y_alvo:
        y -= 4 
        TELA.blit(bg_ee, (0, 0)); TELA.blit(img_nova, (0, y))
        pygame.display.flip(); clock.tick(60)

def tela_final_congelada(vitoria=None, recusou=False):
    fonte_pequena = pygame.font.SysFont("Arial", 25, True)
    fonte_msg = pygame.font.SysFont("Impact", 80)
    while True:
        TELA.blit(bg_ee, (0, 0))
        if recusou:
            l1 = fonte_pequena.render("VOCÊ SE JUNTOU AO PIOR INIMIGO.", True, (255, 255, 255))
            l2 = fonte_pequena.render("TODO O ESFORÇO FOI EM VÃO.", True, (255, 255, 255))
            TELA.blit(l1, (LARGURA//2 - l1.get_width()//2, ALTURA//2 - 40))
            TELA.blit(l2, (LARGURA//2 - l2.get_width()//2, ALTURA//2))
        else:
            msg = "VOCÊ GANHOU" if vitoria else "VOCÊ PERDEU"
            txt = fonte_msg.render(msg, True, (255, 255, 255))
            TELA.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2 - 40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.flip(); clock.tick(60)

circulo_wipe()
TELA.blit(bg_ee, (0, 0))
pygame.display.flip()
pygame.time.delay(3000)
animar_troca(None, sid_proposta, primeira_vez=True)
img_atual, mostrar_botoes, fase_combate, rodando = sid_proposta, True, False, True
y_sid = ALTURA - sid_proposta.get_height() - 5
inimigos = pygame.sprite.Group()
tiros_p = pygame.sprite.Group()
tiros_ds = pygame.sprite.Group()

while rodando:
    TELA.blit(bg_ee, (0, 0))
    if not fase_combate:
        TELA.blit(img_atual, (0, y_sid))
        if mostrar_botoes:
            rect_sim = TELA.blit(btn_sim_img, (215, ALTURA - 120))
            rect_nao = TELA.blit(btn_nao_img, (290, ALTURA - 120))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and mostrar_botoes:
            if rect_sim.collidepoint(event.pos):
                mostrar_botoes = False
                animar_troca(sid_proposta, sid_feliz)
                pygame.time.delay(5000)
                tela_final_congelada(recusou=True)
            elif rect_nao.collidepoint(event.pos):
                mostrar_botoes = False
                animar_troca(sid_proposta, sid_bravo)
                pygame.time.delay(5000)
                animar_descida(sid_bravo)
                ds_y, p_y_anim = -300, ALTURA + 100
                while ds_y < 40:
                    ds_y += 7; p_y_anim -= 7
                    TELA.blit(bg_ee, (0, 0))
                    TELA.blit(img_death_star, (LARGURA//2 - 120, ds_y))
                    TELA.blit(img_nave_player, (LARGURA//2 - 30, p_y_anim))
                    pygame.display.flip(); clock.tick(60)
                for i in ["3", "2", "1"]:
                    TELA.blit(bg_ee, (0, 0))
                    TELA.blit(img_death_star, (LARGURA//2 - 120, 40))
                    TELA.blit(img_nave_player, (LARGURA//2 - 30, ALTURA - 80))
                    txt = pygame.font.SysFont("Impact", 120).render(i, True, (255, 255, 255))
                    TELA.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2 - 60))
                    pygame.display.flip(); pygame.time.delay(1000)
                fase_combate, p_vida, ds_vida = True, 300, 450
                p_x, p_y = LARGURA//2, ALTURA - 80
                ds_x, ds_dir = LARGURA//2 - 120, 1
                tiros_p, tiros_ds = pygame.sprite.Group(), pygame.sprite.Group()
                inimigos = pygame.sprite.Group()
                for c_i in range(8):
                    inimigos.add(RoboZigueZague(random.randint(100, 700), random.randint(220, 380)))
    if fase_combate:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and p_x > 40: p_x -= 10
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and p_x < LARGURA - 40: p_x += 10
        if keys[pygame.K_SPACE] and len(tiros_p) < 12:
            tiros_p.add(Tiro(p_x, p_y, -1))
        ds_x += 8 * ds_dir
        if ds_x <= 10 or ds_x >= LARGURA - 250: ds_dir *= -1
        if random.random() < 0.08:
            tiros_ds.add(Tiro(ds_x+120, 190, 1, 0))
            tiros_ds.add(Tiro(ds_x+120, 190, 1, -4))
            tiros_ds.add(Tiro(ds_x+120, 190, 1, 4))
        for c in inimigos:
            if not c.descendo and random.random() < 0.015:
                tiros_ds.add(Tiro(c.rect.centerx, c.rect.bottom, 1))
        tiros_p.update(); tiros_ds.update(); inimigos.update()
        rect_hit_ds = pygame.Rect(ds_x + 30, 60, 180, 150)
        for t in tiros_p:
            if rect_hit_ds.collidepoint(t.rect.center): ds_vida -= 2; t.kill()
            for c in inimigos:
                if c.rect.collidepoint(t.rect.center): c.kill(); t.kill() 
        for t in tiros_ds:
            if pygame.Rect(p_x-25, p_y, 50, 50).collidepoint(t.rect.center): p_vida -= 8; t.kill() 
        TELA.blit(img_death_star, (ds_x, 40))
        inimigos.draw(TELA)
        TELA.blit(img_nave_player, (p_x-30, p_y))
        tiros_p.draw(TELA); tiros_ds.draw(TELA)
        pygame.draw.rect(TELA, (50, 50, 50), (18, 18, 254, 19))
        pygame.draw.rect(TELA, (255, 0, 0), (20, 20, max(0, int(ds_vida * 250 / 450)), 15))
        pygame.draw.rect(TELA, (50, 50, 50), (LARGURA - 272, 18, 254, 19))
        pygame.draw.rect(TELA, (0, 255, 0), (LARGURA - 270, 20, max(0, int(p_vida * 250 / 300)), 15))
        if p_vida <= 0 or ds_vida <= 0:
            tela_final_congelada(vitoria=(ds_vida <= 0))
    pygame.display.flip(); clock.tick(60)