import pygame
import sys
import os
import math
import random

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Space Wars - O Lado Sombrio")

clock = pygame.time.Clock()
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_path(*args):
    return os.path.join(script_dir, "sprites", *args)

def scale_proportional(image, new_width=None, new_height=None):
    w, h = image.get_size()
    if new_width:
        ratio = new_width / w
        return pygame.transform.smoothscale(image, (int(w * ratio), int(h * ratio)))
    if new_height:
        ratio = new_height / h
        return pygame.transform.smoothscale(image, (int(w * ratio), int(h * ratio)))
    return image

try:
    bg_raw = pygame.image.load(get_path("backgrounds", "background_easter_egg.png")).convert()
    bg_ee = pygame.transform.smoothscale(bg_raw, (LARGURA, ALTURA))

    largura_sidious = 420 
    sid_proposta = scale_proportional(pygame.image.load(get_path("easterEgg_images", "sidious_proposta.png")), new_width=largura_sidious)
    sid_feliz = scale_proportional(pygame.image.load(get_path("easterEgg_images", "sidious_feliz.png")), new_width=largura_sidious)
    sid_bravo = scale_proportional(pygame.image.load(get_path("easterEgg_images", "sidious_bravo.png")), new_width=largura_sidious)

    btn_w = 140 
    btn_sim_img = scale_proportional(pygame.image.load(get_path("botoes", "botao_sim.png")), new_width=btn_w)
    btn_nao_img = scale_proportional(pygame.image.load(get_path("botoes", "botao_nao.png")), new_width=btn_w)
    
    img_death_star = scale_proportional(pygame.image.load(get_path("easterEgg_images", "death_star_spacewars.png")), new_width=240)
    
    try:
        img_nave_player = scale_proportional(pygame.image.load(get_path("spacewars_naves", "nave_player.png")), new_width=60)
    except:
        img_nave_player = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.polygon(img_nave_player, (0, 255, 0), [(30, 0), (0, 60), (60, 60)])

except Exception as e:
    print(f"Erro: {e}")
    pygame.quit(); sys.exit()

y_final_sidious = ALTURA - sid_proposta.get_height() - 5
rect_sim = btn_sim_img.get_rect(topleft=(215, ALTURA - 120))
rect_nao = btn_nao_img.get_rect(topleft=(290, ALTURA - 120))

class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        super().__init__()
        self.image = pygame.Surface((6, 20))
        cor = (0, 255, 255) if direcao < 0 else (255, 50, 50)
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12 * direcao
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > ALTURA:
            self.kill()

def circulo_wipe():
    raio = 0
    max_raio = int(math.hypot(LARGURA, ALTURA))
    while raio < max_raio:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        TELA.blit(bg_ee, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 0, 0))
        pygame.draw.circle(overlay, (255, 255, 255), (LARGURA//2, ALTURA//2), raio)
        overlay.set_colorkey((255, 255, 255))
        TELA.blit(overlay, (0, 0))
        raio += 20
        pygame.display.flip()
        clock.tick(60)

def animar_troca(img_velha, img_nova):
    y = y_final_sidious
    while y < ALTURA:
        y += 20
        TELA.blit(bg_ee, (0, 0))
        TELA.blit(img_velha, (0, y))
        pygame.display.flip()
        clock.tick(60)
    while y > y_final_sidious:
        y -= 20
        TELA.blit(bg_ee, (0, 0))
        TELA.blit(img_nova, (0, y))
        pygame.display.flip()
        clock.tick(60)

def tela_final(vitoria=None, recusou=False):
    fonte_msg = pygame.font.SysFont("Impact", 80)
    fonte_btn = pygame.font.SysFont("Arial", 30, True)
    
    if recusou:
        msg_texto = "" 
    else:
        msg_texto = "VOCÊ GANHOU" if vitoria else "VOCÊ PERDEU"
        msg_cor = (0, 100, 255) if vitoria else (255, 0, 0)
        txt_msg = fonte_msg.render(msg_texto, True, msg_cor)

    txt_btn = fonte_btn.render("VOLTAR AO INÍCIO", True, (255, 255, 255))
    rect_btn = txt_btn.get_rect(center=(LARGURA//2, ALTURA//2 + 150))
    
    esperando = True
    while esperando:
        if recusou:
            TELA.blit(bg_ee, (0, 0))
            TELA.blit(sid_bravo, (0, y_final_sidious))
        else:
            TELA.blit(bg_ee, (0, 0))
            TELA.blit(txt_msg, (LARGURA//2 - txt_msg.get_width()//2, ALTURA//2 - 50))
        
        TELA.blit(txt_btn, rect_btn)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_btn.collidepoint(event.pos):
                    esperando = False
        
        pygame.display.flip()
        clock.tick(60)

# --- LOOP PRINCIPAL ---
circulo_wipe()
img_atual = sid_proposta
mostrar_botoes = True
fase_combate = False
rodando = True

while rodando:
    TELA.blit(bg_ee, (0, 0))
    if not fase_combate:
        TELA.blit(img_atual, (0, y_final_sidious))
        if mostrar_botoes:
            TELA.blit(btn_sim_img, rect_sim)
            TELA.blit(btn_nao_img, rect_nao)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and mostrar_botoes:
            if rect_sim.collidepoint(event.pos):
                proxima, mostrar_botoes = sid_feliz, False
                animar_troca(img_atual, proxima)
                img_atual = proxima
                pygame.time.delay(5000) 
                
                y_sid = y_final_sidious
                while y_sid < ALTURA:
                    y_sid += 15
                    TELA.blit(bg_ee, (0, 0))
                    TELA.blit(img_atual, (0, y_sid))
                    pygame.display.flip()
                    clock.tick(60)
                
                ds_y, p_y_anim = -300, ALTURA + 100
                while ds_y < 40 or p_y_anim > ALTURA - 80:
                    if ds_y < 40: ds_y += 7
                    if p_y_anim > ALTURA - 80: p_y_anim -= 7
                    TELA.blit(bg_ee, (0, 0))
                    TELA.blit(img_death_star, (LARGURA//2 - 120, ds_y))
                    TELA.blit(img_nave_player, (LARGURA//2 - 30, p_y_anim))
                    pygame.display.flip()
                    clock.tick(60)
                
                font_count = pygame.font.SysFont("Impact", 120)
                for i in ["3", "2", "1"]:
                    TELA.blit(bg_ee, (0, 0))
                    TELA.blit(img_death_star, (LARGURA//2 - 120, 40))
                    TELA.blit(img_nave_player, (LARGURA//2 - 30, ALTURA - 80))
                    txt = font_count.render(i, True, (255, 255, 255))
                    TELA.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2))
                    pygame.display.flip()
                    pygame.time.delay(1000)
                
                fase_combate = True
                p_x, p_y = LARGURA//2, ALTURA - 80
                ds_x, ds_y_fixo = LARGURA//2 - 120, 40
                p_vida, ds_vida = 120, 120
                tiros_p, tiros_ds = pygame.sprite.Group(), pygame.sprite.Group()
                ds_dir = 1
            
            elif rect_nao.collidepoint(event.pos):
                proxima, mostrar_botoes = sid_bravo, False
                animar_troca(img_atual, proxima)
                img_atual = proxima
                pygame.time.delay(5000) 
                tela_final(recusou=True)
                rodando = False

    if fase_combate:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and p_x > 40: p_x -= 10
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and p_x < LARGURA - 40: p_x += 10
        if keys[pygame.K_SPACE]:
            if len(tiros_p) < 15:
                tiros_p.add(Tiro(p_x, p_y, -1))
                tiros_p.add(Tiro(p_x - 25, p_y + 10, -1))
                tiros_p.add(Tiro(p_x + 25, p_y + 10, -1))

        ds_x += 7 * ds_dir
        if ds_x <= 10 or ds_x >= LARGURA - 250: ds_dir *= -1
        if random.random() < 0.06:
            tiros_ds.add(Tiro(ds_x + 120, ds_y_fixo + 150, 1))
            tiros_ds.add(Tiro(ds_x + 50, ds_y_fixo + 130, 1))
            tiros_ds.add(Tiro(ds_x + 190, ds_y_fixo + 130, 1))

        tiros_p.update(); tiros_ds.update()
        
        rect_ds = pygame.Rect(ds_x + 30, ds_y_fixo + 20, 180, 150)
        for t in tiros_p:
            if rect_ds.collidepoint(t.rect.center):
                ds_vida -= 2; t.kill()
        
        rect_p = pygame.Rect(p_x - 25, p_y, 50, 50)
        for t in tiros_ds:
            if rect_p.collidepoint(t.rect.center):
                p_vida -= 5; t.kill()

        TELA.blit(img_death_star, (ds_x, ds_y_fixo))
        TELA.blit(img_nave_player, (p_x - 30, p_y))
        tiros_p.draw(TELA); tiros_ds.draw(TELA)
        
        pygame.draw.rect(TELA, (100, 0, 0), (20, 20, 240, 15))
        pygame.draw.rect(TELA, (255, 0, 0), (20, 20, max(0, 2 * ds_vida), 15))
        pygame.draw.rect(TELA, (0, 100, 0), (LARGURA - 260, 20, 240, 15))
        pygame.draw.rect(TELA, (0, 255, 0), (LARGURA - 260, 20, max(0, 2 * p_vida), 15))

        if p_vida <= 0 or ds_vida <= 0:
            tela_final(vitoria=(ds_vida <= 0))
            rodando = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()