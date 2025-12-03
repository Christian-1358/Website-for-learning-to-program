











    

import pygame, sys, math, random

# --- Configurações Iniciais ---
pygame.init()
# OBS: Ajuste o tamanho da tela conforme sua preferência, 800x600 é o padrão
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Terror STEM - SANIDADE E BLACKOUTS")
clock = pygame.time.Clock()

# Adicionado fonte para o HUD
try:
    # Fontes Orbitron (se disponíveis)
    font = pygame.font.SysFont("Orbitron",28)
    small_font = pygame.font.SysFont("Orbitron",20)
    title_font = pygame.font.SysFont("Orbitron",60)
    alert_font = pygame.font.SysFont("Orbitron", 35) 
    hud_font = pygame.font.SysFont("Orbitron", 18)
    horror_font = pygame.font.SysFont("Courier New", 40, bold=True) 
except:
    # Fontes de fallback (padrão)
    font = pygame.font.SysFont("Arial", 28, bold=True)
    small_font = pygame.font.SysFont("Arial", 20)
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    alert_font = pygame.font.SysFont("Arial", 35, bold=True)
    hud_font = pygame.font.SysFont("Arial", 18, bold=True)
    horror_font = pygame.font.SysFont("Arial", 40, bold=True)


# --- Inicialização de Áudio (Caminhos dos sons são importantes!) ---
pygame.mixer.init()
# OBS: Ajuste estes caminhos. Assumi que você tem 3 músicas para fases.
# Se você não tiver os arquivos, o jogo CONTINUA A FUNCIONAR, mas sem som.
musica_fase = ["../assents/sounds/phase1.mp3", "../assents/sounds/phase2.mp3", "../assents/sounds/phase3.mp3"]
bg_music = None
sanity_scare_sound = None 
static_noise_sound = None 
heartbeat_slow_sound = None 
heartbeat_fast_sound = None 
enemy_whispers_sound = None 
enemy_steps_sound = None 

try:
    # OBSERVAÇÃO: Ajuste os caminhos dos arquivos de som conforme necessário.
    scream_sound = pygame.mixer.Sound("../assents/sounds/scare_scream_intense.mp3") 
    door_sound = pygame.mixer.Sound("../assents/sounds/door.mp3")
    stunt_sound = pygame.mixer.Sound("../assents/sounds/stunt.mp3") 
    heartbeat_slow_sound = pygame.mixer.Sound("../assents/sounds/heartbeat_slow.mp3")
    heartbeat_fast_sound = pygame.mixer.Sound("../assents/sounds/heartbeat_fast.mp3")
    enemy_whispers_sound = pygame.mixer.Sound("../assents/sounds/enemy_whispers.mp3")
    enemy_steps_sound = pygame.mixer.Sound("../assents/sounds/enemy_steps.mp3")
    static_noise_sound = pygame.mixer.Sound("../assents/sounds/static_noise.mp3") 
    sanity_scare_sound = pygame.mixer.Sound("../assents/sounds/sanity_scare.mp3") 
    
    # Configuração de volume inicial
    if heartbeat_slow_sound and heartbeat_fast_sound:
        heartbeat_slow_sound.set_volume(0.0); heartbeat_fast_sound.set_volume(0.0)
        heartbeat_slow_sound.play(-1); heartbeat_fast_sound.play(-1)
    
    if enemy_whispers_sound: enemy_whispers_sound.set_volume(0.0); enemy_whispers_sound.play(-1)
    if enemy_steps_sound: enemy_steps_sound.set_volume(0.0); enemy_steps_sound.play(-1)
    if static_noise_sound: static_noise_sound.set_volume(0.0); static_noise_sound.play(-1) 

except Exception as e:
    # Se houver erro ao carregar, crie objetos None para evitar crashes
    print(f"Erro ao carregar sons: {e}. Alguns efeitos sonoros podem estar desativados.")
    scream_sound = None; door_sound = None; stunt_sound = None 
    heartbeat_slow_sound = None; heartbeat_fast_sound = None
    enemy_whispers_sound = None; enemy_steps_sound = None
    static_noise_sound = None
    sanity_scare_sound = None 

def play_bg_music(path):
    global bg_music
    try:
        if bg_music: pygame.mixer.stop() # Parar todas as músicas (para garantir)
        bg_music = pygame.mixer.Sound(path)
        bg_music.set_volume(0.5)
        bg_music.play(-1)
    except:
        bg_music = None

# --- Funções Utilitárias ---

def draw_gradient_rect(surface, rect, color1, color2, horizontal=False):
    x,y,w,h = rect
    if horizontal:
        for i in range(w):
            ratio = i/w
            r = int(color1[0]*(1-ratio)+color2[0]*ratio)
            g = int(color1[1]*(1-ratio)+color2[1]*ratio)
            b = int(color1[2]*(1-ratio)+color2[2]*ratio)
            pygame.draw.line(surface,(r,g,b),(x+i,y),(x+i,y+h-1))
    else:
        for i in range(h):
            ratio = i/h
            r = int(color1[0]*(1-ratio)+color2[0]*ratio)
            g = int(color1[1]*(1-ratio)+color2[1]*ratio)
            b = int(color1[2]*(1-ratio)+color2[2]*ratio)
            pygame.draw.line(surface,(r,g,b),(x,y+i),(x+w-1,y+i))

def draw_text_outline(surface,text,font,color,outline_color,pos,center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos

    outline_surface = font.render(text, True, outline_color)
    
    # Desenha o contorno
    for dx in [-1,0,1]:
        for dy in [-1,0,1]:
            if dx!=0 or dy!=0:
                surface.blit(outline_surface, (text_rect.x+dx,text_rect.y+dy))
                
    surface.blit(text_surface, text_rect)


global_messages = []
MAX_MESSAGE_TIME = 150

def add_message(text, color):
    global global_messages
    global_messages.append({"text": text, "color": color, "time": MAX_MESSAGE_TIME})

# --- Classes de Personagens e Objetos ---

class Player:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,25,25)
        self.base_speed = 5 
        self.light_energy = 100 
        self.sprint_energy = 100 
        self.sanity = 100          
        self.keys = 0
        self.notes = 0 # IMPORTANTE: Zerado em cada fase nova
        self.emergency_lights = 0 
        self.light_bombs = 0 # Novo item
        self.speed_boost_timer = 0 # Novo efeito
        self.walk_anim = 0
        self.is_sprinting = False
        self.is_light_on = True 
        self.noise_level = 0    
        self.is_slowed = False 
        self.light_dir_vector = (0, 0) 
        self.is_hidden = False 
        self.current_locker = None 
        self.blackout_timer = 0    
        self.light_bomb_cooldown = 0

    def manage_stamina(self, is_sprint_key_down):
        """Gerencia o consumo/recarga de stamina (sprint)."""
        current_speed = self.base_speed
        
        # Efeito de Speed Boost (Novo)
        if self.speed_boost_timer > 0:
             self.speed_boost_timer -= 1
             self.sprint_energy = 100 # Stamina infinita
             current_speed *= 1.5 
             is_sprint_key_down = True # Força o sprint
        
        # Redução de velocidade por falta de luz
        if self.light_energy <= 0 and not self.is_slowed and self.speed_boost_timer <= 0:
            current_speed *= 0.5 
            self.is_slowed = True
        elif (self.light_energy > 0 or self.speed_boost_timer > 0) and self.is_slowed:
            self.is_slowed = False 
        
        # Reduz velocidade se sanidade estiver muito baixa
        if self.sanity < 20: current_speed *= 0.7 
        
        if is_sprint_key_down and self.sprint_energy > 0: 
            spd = current_speed * 1.8
            self.sprint_energy = max(0, self.sprint_energy - 0.7)
            self.is_sprinting = True
        else:
            spd = current_speed
            self.sprint_energy = min(100, self.sprint_energy + 0.3) 
            self.is_sprinting = False
            
        return spd, self.is_sprinting

    def manage_light(self):
        """Gerencia o consumo/recarga da lanterna e luz."""
        if self.is_hidden or self.blackout_timer > 0:
            if self.is_light_on and self.is_hidden:
                 self.light_energy = max(0, self.light_energy - 0.08)
            elif not self.is_sprinting and self.speed_boost_timer <= 0:
                 self.light_energy = min(100, self.light_energy + 0.1)
            return

        if self.is_light_on:
            consumption = 0.4 + (0.2 if self.is_sprinting else 0)
            if self.light_energy > 0: 
                self.light_energy = max(0, self.light_energy - consumption)
            else:
                self.is_light_on = False 
                self.light_energy = 0
        else:
            if not self.is_sprinting and self.speed_boost_timer <= 0:
                 self.light_energy = min(100, self.light_energy + 0.3) 

    def update_status(self, enemies, distance_to_closest):
        """Atualiza Sanidade e Blackout, e controla o ruído estático."""
        # 1. Atualiza Sanidade
        if self.is_hidden:
            self.sanity = min(100, self.sanity + 0.15) # Recupera mais rápido escondido
        else:
            if not self.is_light_on or self.light_energy <= 0:
                self.sanity = max(0, self.sanity - 0.25) # Perde mais no escuro
            
            if distance_to_closest < 150:
                loss_factor = (150 - distance_to_closest) / 150 * 0.5
                self.sanity = max(0, self.sanity - loss_factor) 
        
        # 2. Batimento Cardíaco (Novo - Depende da Sanidade/Proximidade)
        global heartbeat_slow_sound, heartbeat_fast_sound
        if heartbeat_slow_sound and heartbeat_fast_sound:
            if distance_to_closest < 250:
                 # Volume aumenta baseado na proximidade
                heart_vol = max(0.0, (250 - distance_to_closest) / 250) * 0.5 
            elif self.sanity < 30:
                 # Volume aumenta baseado na sanidade
                 heart_vol = max(0.0, (30 - self.sanity) / 30) * 0.4 
            else:
                heart_vol = 0.0

            heartbeat_slow_sound.set_volume(max(0.0, min(0.5, heart_vol)))
            heartbeat_fast_sound.set_volume(max(0.0, min(0.5, heart_vol * 1.5))) # Fast heartbeat é mais intenso

        # 3. Efeito de Ruído Estático (dependente da Sanidade)
        global static_noise_sound
        if static_noise_sound:
            if self.sanity < 80:
                noise_vol = (80 - self.sanity) / 80 * 0.4
                static_noise_sound.set_volume(max(0.0, min(0.4, noise_vol)))
            else:
                static_noise_sound.set_volume(0.0)

        # 4. Blackout
        if self.sanity < 50 and self.blackout_timer <= 0:
             if random.random() < (50 - self.sanity) / 50 * 0.005: 
                 self.blackout_timer = random.randint(60, 180) 
                 if self.is_light_on:
                     self.is_light_on = False
                 add_message("FALHA DE ENERGIA!", (255, 0, 0))
                 
        if self.blackout_timer > 0:
            self.blackout_timer -= 1
            if self.blackout_timer == 0 and self.light_energy > 0:
                 self.is_light_on = True
                 add_message("Energia Restaurada.", (0, 255, 0))

    def move(self, keys, collision_rects): 
        if self.is_hidden: return
        
        if self.light_bomb_cooldown > 0:
            self.light_bomb_cooldown -= 1

        spd, is_sprinting = self.manage_stamina(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        self.is_sprinting = is_sprinting
        
        dx=dy=0; moving=False

        if keys[pygame.K_w]: dy -= spd; moving=True
        if keys[pygame.K_s]: dy += spd; moving=True
        if keys[pygame.K_a]: dx -= spd; moving=True
        if keys[pygame.K_d]: dx += spd; moving=True
        
        # Movimentação e Colisão
        self.rect.x += dx
        for rect_obj in collision_rects:
            if self.rect.colliderect(rect_obj): self.rect.x -= dx
        
        self.rect.y += dy
        for rect_obj in collision_rects:
            if self.rect.colliderect(rect_obj): self.rect.y -= dy
            
        if moving: self.walk_anim += 0.2
        else: self.walk_anim = 0
        
        # Lógica de Ruído
        base_noise = 0
        if self.is_sprinting: base_noise = 4 if not self.is_light_on else 2
        elif moving: base_noise = 0.5

        if moving:
            self.noise_level = min(100, self.noise_level + base_noise) 
        else:
            self.noise_level = max(0, self.noise_level - 2) 

        # Penalidade de Ruído Adicional se a sanidade estiver baixa
        if self.sanity < 30 and moving:
            self.noise_level = min(100, self.noise_level + (30 - self.sanity) / 30 * 1.5)

    def update_light_direction(self, mouse_pos):
        if self.is_hidden: return
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0: self.light_dir_vector = (dx / dist, dy / dist)
        else: self.light_dir_vector = (0, -1) 

    def draw(self,surface):
        if self.is_hidden: return

        offset = math.sin(self.walk_anim*1.5)*3 
        player_color_base = (200, 200, 200) if self.is_light_on and self.light_energy > 0 else (80, 80, 80)
        player_color_dark = (100, 100, 100) if self.is_light_on and self.light_energy > 0 else (30, 30, 30)

        # Pisca em Blackout
        if self.blackout_timer > 0 and self.blackout_timer % 10 < 5:
            player_color_base = (50, 50, 50)
            player_color_dark = (10, 10, 10)
        
        # Pisca com Speed Boost
        if self.speed_boost_timer > 0 and self.speed_boost_timer % 5 < 3:
            player_color_base = (0, 255, 255)
            player_color_dark = (0, 100, 100)

        draw_gradient_rect(surface, (self.rect.x, self.rect.y + offset, self.rect.width, self.rect.height),
                           (player_color_base[0], player_color_base[1] + offset, player_color_base[2]), player_color_dark)
        
        pygame.draw.ellipse(surface, (player_color_base[0]*0.8, player_color_base[1]*0.8, player_color_base[2]*0.8),
                            (self.rect.x + self.rect.width//4, self.rect.y - 5 + offset, self.rect.width//2, self.rect.height//2))

        # Efeito visual de Lentidão (Armadilha)
        if self.is_slowed and self.speed_boost_timer <= 0:
             temp_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
             temp_surf.fill((255,0,0, random.randint(50, 100))) 
             surface.blit(temp_surf, self.rect.topleft)

# --- Classes Inimigas ---

class Enemy:
    def __init__(self, x, y, speed, alert_distance=250):
        self.rect = pygame.Rect(x,y,35,35) 
        self.speed = speed
        self.alert_distance = alert_distance 
        self.flash_timer = 0
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.patrol_timer = random.randint(60, 180) 
        self.is_stunned = False 
        self.stun_timer = 0
        self.teleport_cooldown = 0 
        self.teleport_active = False 

    def is_in_light_cone(self, player):
        if not player.is_light_on or player.light_energy <= 0 or player.blackout_timer > 0: 
            return False
            
        dx_enemy = self.rect.centerx - player.rect.centerx
        dy_enemy = self.rect.centery - player.rect.centery
        distance = math.hypot(dx_enemy, dy_enemy)
        
        light_radius = int(player.light_energy * 1.5) if player.light_energy > 0 else 20 
        if distance > light_radius: return False

        if distance > 0:
            v_to_enemy = (dx_enemy / distance, dy_enemy / distance)
            dot_product = player.light_dir_vector[0] * v_to_enemy[0] + player.light_dir_vector[1] * v_to_enemy[1]
            cone_angle_cos = 0.7 
            return dot_product >= cone_angle_cos
        
        return False
        
    def check_alert(self, player, distance):
        if self.is_in_light_cone(player): return True

        noise_threshold = 40 
        if player.noise_level > noise_threshold and distance < 250: 
            noise_factor = (player.noise_level - noise_threshold) / 60 * 0.1 
            if random.random() < noise_factor: return True
        
        return False

    def update(self, player, collision_rects): 
        if self.is_stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0: self.is_stunned = False
            return
            
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx,dy)
        
        if player.is_hidden: is_alerted = False
        else: is_alerted = self.check_alert(player, distance) 
            
        if is_alerted:
            if distance!=0:
                move_x = int(dx/distance*self.speed)
                move_y = int(dy/distance*self.speed)
                self.rect.x += move_x
                for rect_obj in collision_rects:
                    if self.rect.colliderect(rect_obj): self.rect.x -= move_x
                self.rect.y += move_y
                for rect_obj in collision_rects:
                    if self.rect.colliderect(rect_obj): self.rect.y -= move_y
                    
            self.flash_timer=5
            
            # Controle de volume do BGM e efeitos (Ativo apenas se não houver blackout)
            if player.blackout_timer <= 0:
                if bg_music: vol = max(0.1, min(0.9, 0.5 + (1 - distance/self.alert_distance) * 0.4)); bg_music.set_volume(vol)
                if enemy_whispers_sound and distance < 150: enemy_whispers_sound.set_volume(min(1.0, (150-distance)/150 * 0.7))
                if enemy_steps_sound and distance < 100: enemy_steps_sound.set_volume(min(1.0, (100-distance)/100 * 0.5))
                
        else: 
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                self.patrol_timer = random.randint(60, 180)
                
            move_x = self.dir[0]*self.speed; move_y = self.dir[1]*self.speed
            self.rect.x += move_x
            for rect_obj in collision_rects:
                if self.rect.colliderect(rect_obj): self.rect.x -= move_x; self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.rect.y += move_y
            for rect_obj in collision_rects:
                if self.rect.colliderect(rect_obj): self.rect.y -= move_y; self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

            self.flash_timer=max(self.flash_timer-0.1,0)
            
            # Diminui o volume se não estiver alertado (Ativo apenas se não houver blackout)
            if player.blackout_timer <= 0:
                if bg_music: bg_music.set_volume(max(0.1, min(0.5, bg_music.get_volume())))
                if enemy_whispers_sound: enemy_whispers_sound.set_volume(max(0.0, enemy_whispers_sound.get_volume() - 0.01))
                if enemy_steps_sound: enemy_steps_sound.set_volume(max(0.0, enemy_steps_sound.get_volume() - 0.01))

            # Lógica de teleporte
            if self.teleport_cooldown > 0: self.teleport_cooldown -= 1
            elif not is_alerted and distance > 300 and random.random() < 0.001: 
                self.teleport_active = True
                pygame.time.set_timer(pygame.USEREVENT + 1, 300) 
                
                new_x, new_y = self.rect.x, self.rect.y
                for _ in range(50): 
                    test_x = random.randint(50, 750); test_y = random.randint(50, 550)
                    test_rect = pygame.Rect(test_x, test_y, self.rect.width, self.rect.height)
                    # Verifica se o novo local está longe de paredes e do jogador
                    if not any(test_rect.colliderect(r) for r in collision_rects) and \
                       math.hypot(test_x - player.rect.centerx, test_y - player.rect.centery) > 150 and \
                       math.hypot(test_x - player.rect.centerx, test_y - player.rect.centery) < 400: 
                        new_x, new_y = test_x, test_y; break
                self.rect.x, self.rect.y = new_x, new_y
                self.teleport_cooldown = 60 * 5 
                add_message("Você ouviu algo se mover...", (255, 150, 0))

    def draw(self,surface):
        enemy_base_color = (180, 0, 0); enemy_dark_color = (80, 0, 0)
        if self.is_stunned:
             enemy_base_color = (0, 200, 200); enemy_dark_color = (0, 100, 100)
        elif self.flash_timer > 0:
            enemy_base_color = (255,255,255); enemy_dark_color = (150,150,150)
        elif self.teleport_active: 
            enemy_base_color = (100, 0, 200); enemy_dark_color = (50, 0, 100)
            if random.random() < 0.5: enemy_base_color = (255, 255, 255)

        draw_gradient_rect(surface,(self.rect.x,self.rect.y,self.rect.width,self.rect.height),enemy_base_color,enemy_dark_color)
        
        pygame.draw.circle(surface, (255, 0, 0), (self.rect.x + self.rect.width//3, self.rect.y + self.rect.height//3), 3)
        pygame.draw.circle(surface, (255, 0, 0), (self.rect.x + 2*self.rect.width//3, self.rect.y + self.rect.height//3), 3)

class Lurker(Enemy):
    def __init__(self, x, y, speed=1.0): 
        super().__init__(x, y, speed, alert_distance=350)
        self.rect = pygame.Rect(x,y,40,40)
        self.color1 = (100, 0, 150) 
        self.color2 = (50, 0, 75)
        self.alert_distance = 400 

    def check_alert(self, player, distance):
        if player.noise_level > 20: 
            if random.random() < (player.noise_level / 100) * 0.1: return True
                
        if self.is_in_light_cone(player) and distance < self.alert_distance / 3: return True

        return False
        
    def draw(self,surface):
        lurker_base_color = self.color1; lurker_dark_color = self.color2
        if self.is_stunned: lurker_base_color = (0, 255, 255); lurker_dark_color = (0, 150, 150)
        elif self.flash_timer > 0: lurker_base_color = (255,255,255); lurker_dark_color = (150,150,150)
        elif self.teleport_active: 
            lurker_base_color = (100, 0, 200); lurker_dark_color = (50, 0, 100)
            if random.random() < 0.5: lurker_base_color = (255, 255, 255)

        draw_gradient_rect(surface,(self.rect.x,self.rect.y,self.rect.width,self.rect.height),lurker_base_color,lurker_dark_color)
        
        if random.random() < 0.05 and not self.is_stunned: 
             pygame.draw.circle(surface, (255, 0, 0), (self.rect.centerx, self.rect.centery), 8) 
             
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height//2), pygame.SRCALPHA)
        shadow_surf.fill((0,0,0,50))
        surface.blit(shadow_surf, (self.rect.x, self.rect.y + self.rect.height//2))


# --- Classes de Ambientes e Itens ---
class Locker:
    def __init__(self, x, y, w=40, h=60):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_open = False
        self.color1 = (40, 40, 40)
        self.color2 = (80, 80, 80)

    def draw(self, surface):
        draw_gradient_rect(surface, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), self.color1, self.color2)
        pygame.draw.rect(surface, (20, 20, 20), (self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, self.rect.height - 8), 2)
        pygame.draw.circle(surface, (150, 150, 150), (self.rect.x + self.rect.width - 10, self.rect.centery), 3)
        if self.is_open:
            pygame.draw.circle(surface, (255, 0, 0), (self.rect.x + self.rect.width - 10, self.rect.centery), 3) 

class Item:
    def __init__(self,x,y,type):
        self.type = type
        self.rect = pygame.Rect(x,y,20,20)
        if type=="battery": self.color = (0,180,0) 
        elif type=="key": self.color = (255,220,0) 
        elif type=="note": self.color = (180,0,255) 
        elif type=="trap": self.color = (200,80,80) 
        elif type=="emerg_light": self.color = (0, 180, 180) 
        elif type=="light_bomb": self.color = (255, 100, 0) # Novo
        elif type=="speed_boost": self.color = (0, 255, 255) # Novo
        else: self.color = (255,255,255)
        
    def copy(self): return Item(self.rect.x, self.rect.y, self.type)
    
    def draw(self,surface):
        temp_surf = pygame.Surface((self.rect.width,self.rect.height), pygame.SRCALPHA)
        draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),self.color,(self.color[0]//2,self.color[1]//2,self.color[2]//2))
        
        if self.type == "trap":
            pygame.draw.line(temp_surf, (255,0,0), (0,0), (20,20), 2)
            pygame.draw.line(temp_surf, (255,0,0), (20,0), (0,20), 2)
        elif self.type == "key":
            pygame.draw.circle(temp_surf, (255,255,255), (self.rect.width//2, self.rect.height//4), 4)
            pygame.draw.rect(temp_surf, (255,255,255), (self.rect.width//2 - 2, self.rect.height//4, 4, self.rect.height//2))
        elif self.type == "note":
            pygame.draw.rect(temp_surf, (255,255,255), (3,3, self.rect.width-6, self.rect.height-6))
        elif self.type == "light_bomb":
            pygame.draw.circle(temp_surf, (255,255,255), (self.rect.width//2, self.rect.height//2), self.rect.width//3, 2)
            pygame.draw.line(temp_surf, (255,255,255), (self.rect.width//2, self.rect.height//2), (self.rect.width//2, self.rect.height//2 - 5), 2)
        elif self.type == "speed_boost":
            pygame.draw.polygon(temp_surf, (255,255,255), [(self.rect.width//2, 2), (self.rect.width-2, self.rect.height//2), (self.rect.width//2, self.rect.height-2), (2, self.rect.height//2)])

        surface.blit(temp_surf,(self.rect.x,self.rect.y))

class Wall:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)
        self.color1=(25,25,25) 
        self.color2=(45,45,45)
        
    def draw(self,surface):
        draw_gradient_rect(surface,(self.rect.x,self.rect.y,self.rect.width,self.rect.height),self.color1,self.color2,horizontal=True)
        for i in range(0, self.rect.height, 10):
            pygame.draw.line(surface, (20,20,20), (self.rect.x, self.rect.y + i), (self.rect.x + self.rect.width, self.rect.y + i), 1)
        for i in range(0, self.rect.width, 10):
            pygame.draw.line(surface, (20,20,20), (self.rect.x + i, self.rect.y), (self.rect.x + i, self.rect.y + self.rect.height), 1)

class Door:
    def __init__(self,x,y,w,h,key_required=1):
        self.rect=pygame.Rect(x,y,w,h)
        self.locked=True
        self.flash_timer=0
        self.color1=(80,40,0) 
        self.color2=(40,20,0)
        self.key_required = key_required
        
    def draw(self,surface):
        temp_surf=pygame.Surface((self.rect.width,self.rect.height))
        
        if self.flash_timer>0:
            draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),(255,255,255),(255,255,255))
        else:
            draw_gradient_rect(temp_surf,(0,0,self.rect.width,self.rect.height),self.color1,self.color2)
            
        pygame.draw.rect(temp_surf, (20,20,20), (self.rect.width//4, self.rect.height//4, self.rect.width//2, self.rect.height//2), 2)
        pygame.draw.circle(temp_surf, (100,100,100), (self.rect.width - 10, self.rect.height//2), 5) 

        if self.locked:
             pygame.draw.circle(temp_surf, (255,200,0), (self.rect.width - 10, self.rect.height//2), 3)
             
        surface.blit(temp_surf,(self.rect.x,self.rect.y))
        self.flash_timer=max(self.flash_timer-0.1,0)

class RandomScare: 
    def __init__(self):
        self.image = pygame.Surface((150,150), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,255,255,200), (75,75), 75)
        self.timer = 0
        self.active = False
        self.x = random.randint(100,650)
        self.y = random.randint(100,450)
        self.flash_timer = 0
        self.particle_timer = 0 
        self.particles = [] 
        self.scare_type = "VISUAL" 

    def trigger_scare(self, level, scare_type="VISUAL"):
        self.active = True
        self.timer = 25
        self.flash_timer = 5
        self.x = random.randint(100,650)
        self.y = random.randint(100,450)
        self.scare_type = scare_type

        try:
            if scare_type == "INSTANT" and scream_sound:
                scream_sound.set_volume(random.uniform(0.8,1.0))
                scream_sound.play()
            elif scare_type == "SANITY" and sanity_scare_sound:
                sanity_scare_sound.set_volume(random.uniform(0.5, 0.8))
                sanity_scare_sound.play()
        except: pass

    def update(self, level, player_sanity):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
                self.flash_timer = 0
                self.particles = []
        else:
            # Chance de susto VISUAL (tradicional)
            if random.random() < 0.003 + 0.0002*level:
                self.trigger_scare(level, "INSTANT")
            
            # Chance de susto de SANIDADE (mais frequente, mas menos intenso)
            if player_sanity < 40 and random.random() < (40 - player_sanity) / 40 * 0.005:
                self.trigger_scare(level, "SANITY")
        
        if self.active:
            self.particle_timer += 1
            if self.particle_timer % 3 == 0:
                for _ in range(5):
                    px = self.x + random.randint(0, 150)
                    py = self.y + random.randint(0, 150)
                    self.particles.append([px, py, random.randint(1, 4), random.randint(3, 7), random.choice([(255,0,0,150), (0,255,255,150), (255,255,255,100)])])

            for p in self.particles[:]:
                p[0] += random.uniform(-5, 5)
                p[1] += random.uniform(-5, 5)
                p[3] -= 0.2
                if p[3] <= 0: self.particles.remove(p)


    def draw(self, surface):
        if self.active:
            shake_x = random.randint(-15,15)
            shake_y = random.randint(-15,15)
            
            # Flash
            if self.flash_timer > 0 and self.scare_type == "INSTANT":
                flash = pygame.Surface((800,600), pygame.SRCALPHA)
                flash.fill((255,255,255, random.randint(80,150)))
                surface.blit(flash, (0,0))
                self.flash_timer -= 1
                
            # Desenha Partículas de Glitch
            for p in self.particles:
                color = (p[4][0], p[4][1], p[4][2]) 
                pygame.draw.rect(surface, color, (p[0] + shake_x, p[1] + shake_y, p[2], p[2]))

            # Susto Principal (Visual distorcido)
            if self.scare_type != "SANITY" or random.random() < 0.5: 
                temp_surf = self.image.copy()
                alpha = random.randint(100,255)
                temp_surf.set_alpha(alpha)
                surface.blit(temp_surf, (self.x+shake_x, self.y+shake_y))
            
            # Piscada de Tela
            if random.random() < 0.05:
                blink = pygame.Surface((800,600), pygame.SRCALPHA)
                blink.fill((255,255,255, random.randint(50,100)))
                surface.blit(blink, (0,0))


# --- Funções de Desenho Aprimoradas ---

def draw_light_cone(surface, player, light_radius):
    if light_radius <= 20 and player.light_energy > 0:
        light_radius = 50 
        for r in range(light_radius, 0, -5):
            alpha = max(0, min(10, int(10 * (r/light_radius))))
            pygame.draw.circle(surface, (255, 255, 255, alpha), player.rect.center, r)
        return
    elif light_radius <= 20 and player.light_energy <= 0:
        return

    cone_angle = math.radians(60)
    
    dir_x, dir_y = player.light_dir_vector
    base_angle = math.atan2(dir_y, dir_x)
    
    angle_start = base_angle - cone_angle / 2
    angle_end = base_angle + cone_angle / 2
    
    center = player.rect.center
    point_start = (center[0] + light_radius * math.cos(angle_start),
                   center[1] + light_radius * math.sin(angle_start))
    point_end = (center[0] + light_radius * math.cos(angle_end),
                 center[1] + light_radius * math.sin(angle_end))
                 
    cone_points = [center, point_start, point_end]

    pygame.draw.polygon(surface, (255, 255, 255, 120), cone_points)

    for r in range(light_radius, light_radius - 50, -10):
        alpha = max(0, min(150, int(150 * (1 - (light_radius - r) / 50))))
        pygame.draw.circle(surface, (255, 255, 255, alpha), center, r, 0)
        
def draw_failed_night_vision(surface, player, enemies):
    # Efeito de visão noturna (Night Vision) aprimorado
    if player.light_energy <= 0 and not player.is_hidden:
        night_surf = pygame.Surface((800, 600), pygame.SRCALPHA)
        # Tom esverdeado/escuro
        night_surf.fill((0, 50, 0, 150)) 
        
        # Círculo de visão fraca
        pygame.draw.circle(night_surf, (0, 200, 0, 80), player.rect.center, 80)

        # Ruído de estática verde
        for i in range(200):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            if random.random() < 0.2:
                # Usando RGB simples com a superfície SRCALPHA
                pygame.draw.rect(night_surf, (0, 255, 0), (x, y, 1, 1))

        # Destaque inimigo (vermelho)
        for enemy in enemies:
             dist_to_enemy = math.hypot(enemy.rect.centerx - player.rect.centerx, enemy.rect.centery - player.rect.centery)
             if dist_to_enemy < 150:
                 r = random.randint(50, 80)
                 alpha = max(0, int(200 * (1 - dist_to_enemy / 150)))
                 pygame.draw.circle(night_surf, (255, 0, 0, alpha), enemy.rect.center, r)

        surface.blit(night_surf, (0, 0))

def draw_game_elements(screen, player, walls, doors, items, enemies, scare, lockers):
    screen.fill((0,0,0))
    
    # Camada 1: Ambiente
    for wall in walls: wall.draw(screen)
    for door in doors: door.draw(screen)
    for item in items: item.draw(screen)
    for locker in lockers: locker.draw(screen) 
    
    # Camada 2: Iluminação e Visibilidade
    light_surface=pygame.Surface((800,600),pygame.SRCALPHA)
    light_radius = int(player.light_energy * 1.5) if player.light_energy > 0 and player.is_light_on and player.blackout_timer <= 0 else 20

    if player.light_energy > 0 and player.is_light_on and not player.is_hidden and player.blackout_timer <= 0:
        draw_light_cone(light_surface, player, light_radius)
    elif player.light_energy <= 0 and not player.is_hidden:
        draw_failed_night_vision(light_surface, player, enemies) 
    
    # Mistura a iluminação (adiciona luz à tela escura)
    screen.blit(light_surface,(0,0),special_flags=pygame.BLEND_RGBA_ADD)

    # Camada 3: Personagens
    for enemy in enemies: enemy.draw(screen)
    player.draw(screen)

    # Camada 4: Susto
    scare.draw(screen)
    
    # Camada 5: Efeitos de Pânico & Sanidade (Estática/Cor/Distorção)
    panic_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    
    min_dist = min([math.hypot(e.rect.centerx - player.rect.centerx, e.rect.centery - player.rect.centery) for e in enemies]) if enemies else 500
    
    # Fator de pânico unificado
    panic_factor = max(0, 1 - min_dist/200) + player.noise_level/150 + max(0, (100 - player.sanity)/100 * 1.5)
    
    # Efeito de Shake/Estática
    if random.random() < panic_factor:
        # Tremor (Shake)
        shake_x = random.randint(-int(panic_factor*3), int(panic_factor*3))
        shake_y = random.randint(-int(panic_factor*3), int(panic_factor*3))
        # Aplica o shake movendo a tela
        screen.blit(screen, (shake_x, shake_y)) 
        
        # Desenha estática (CORRIGIDO: usando 3 componentes de cor, o alpha vem da superfície)
        for i in range(int(300 * panic_factor)):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            pygame.draw.rect(panic_surface, (255, 255, 255), (x, y, 1, 1))

    # Efeito de cor vermelha (Sangue / Pânico)
    red_alpha = min(150, int(panic_factor * 150))
    pygame.draw.rect(panic_surface, (150, 0, 0, red_alpha), (0,0, 800, 600))
    
    # Efeito de distorção ("Stuttering") se a sanidade estiver crítica
    if player.sanity < 15:
         for y in range(0, 600, 50):
             offset = random.randint(-15, 15)
             # Linhas de glitch
             pygame.draw.line(panic_surface, (255, 255, 255, 50), (0, y), (800, y + offset), 5)
             
    # Efeito de Blackout
    if player.blackout_timer > 0:
        dark_alpha = 255 if player.blackout_timer > 10 else int(255 * (player.blackout_timer / 10))
        dark_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, dark_alpha))
        screen.blit(dark_surface, (0, 0))

    screen.blit(panic_surface, (0, 0))


# --- Funções do Jogo ---

def draw_hud(screen, player, level, required_notes, hud_font, title_font, small_font):
    # --- Barra de Luz ---
    LIGHT_W = 150; LIGHT_H = 15
    light_rect = pygame.Rect(10, 10, LIGHT_W, LIGHT_H)
    pygame.draw.rect(screen, (10, 10, 10), light_rect)
    current_light_width = int(LIGHT_W * (player.light_energy / 100))
    light_fill_rect = pygame.Rect(10, 10, current_light_width, LIGHT_H)
    light_color1 = (255, 255, 0)
    light_color2 = (150, 150, 0)
    draw_gradient_rect(screen, light_fill_rect, light_color1, light_color2, horizontal=True)
    pygame.draw.rect(screen, (255, 255, 255), light_rect, 2)
    draw_text_outline(screen, f"LUZ: {int(player.light_energy)}%", hud_font, (255, 255, 255), (0, 0, 0), (15, 8), center=False)

    # --- Barra de Estamina (Aproveitada para Light Cooldown) ---
    STAMINA_W = 150; STAMINA_H = 15
    stamina_rect = pygame.Rect(10, 30, STAMINA_W, STAMINA_H)
    pygame.draw.rect(screen, (10, 10, 10), stamina_rect)
    
    if player.is_sprinting or player.speed_boost_timer > 0:
        # Se correndo/boost, mostra stamina
        current_stamina_width = int(STAMINA_W * (player.sprint_energy / 100))
        stamina_fill_rect = pygame.Rect(10, 30, current_stamina_width, STAMINA_H)
        stamina_color1 = (0, 255, 255) if player.speed_boost_timer > 0 else (0, 150, 255)
        stamina_color2 = (0, 150, 150) if player.speed_boost_timer > 0 else (0, 50, 150)
        draw_gradient_rect(screen, stamina_fill_rect, stamina_color1, stamina_color2, horizontal=True)
        draw_text_outline(screen, f"STAMINA", hud_font, (255, 255, 255), (0, 0, 0), (15, 28), center=False)
    else:
        # Se parado/andando, mostra recarga de luz (cooldown)
        light_recharge_ratio = player.light_energy / 100
        cooldown_fill_rect = pygame.Rect(10, 30, int(STAMINA_W * light_recharge_ratio), STAMINA_H)
        cooldown_color1 = (50, 50, 50)
        cooldown_color2 = (10, 10, 10)
        draw_gradient_rect(screen, cooldown_fill_rect, cooldown_color1, cooldown_color2, horizontal=True)
        draw_text_outline(screen, f"RECARGA LUZ", hud_font, (150, 150, 150), (0, 0, 0), (15, 28), center=False)
        
    pygame.draw.rect(screen, (255, 255, 255), stamina_rect, 2)


    # --- Barra de Sanidade ---
    SANITY_W = 150; SANITY_H = 20
    sanity_rect = pygame.Rect(10, 50, SANITY_W, SANITY_H)
    pygame.draw.rect(screen, (10, 10, 10), sanity_rect) 

    current_sanity_width = int(SANITY_W * (player.sanity / 100))
    sanity_fill_rect = pygame.Rect(10, 50, current_sanity_width, SANITY_H)

    if player.sanity > 50:
        color1 = (0, 255, 0); color2 = (0, 150, 0)
    elif player.sanity > 20:
        color1 = (255, 255, 0); color2 = (150, 150, 0)
    else:
        color1 = (255, 0, 0); color2 = (150, 0, 0)

    draw_gradient_rect(screen, sanity_fill_rect, color1, color2, horizontal=True)

    if player.sanity < 50:
         glitch_offset = random.randint(-2, 2)
         if random.random() < 0.3:
            for _ in range(3):
                glitch_x = random.randint(sanity_rect.x, sanity_rect.x + SANITY_W)
                glitch_y = random.randint(sanity_rect.y, sanity_rect.y + SANITY_H)
                pygame.draw.rect(screen, (255, 255, 255, 100), (glitch_x, glitch_y, 5, 2))
         
         pygame.draw.rect(screen, (255, 255, 255), (sanity_rect.x + glitch_offset, sanity_rect.y + glitch_offset, SANITY_W, SANITY_H), 2)
    else:
         pygame.draw.rect(screen, (255, 255, 255), sanity_rect, 2) 

    draw_text_outline(screen, f"SANIDADE: {int(player.sanity)}%", hud_font, (255, 255, 255), (0, 0, 0), (15, 52), center=False)

    # --- Cooldown de Light Bomb (Novo) ---
    if player.light_bomb_cooldown > 0:
        COOLDOWN_W = 100; COOLDOWN_H = 15
        cooldown_ratio = player.light_bomb_cooldown / (60 * 10) # 10s de cooldown
        cooldown_rect = pygame.Rect(690, 80, COOLDOWN_W, COOLDOWN_H)
        pygame.draw.rect(screen, (10, 10, 10), cooldown_rect)
        
        # Preenche com o cooldown restante
        current_cooldown_width = int(COOLDOWN_W * (1 - cooldown_ratio))
        cooldown_fill_rect = pygame.Rect(690, 80, current_cooldown_width, COOLDOWN_H)
        draw_gradient_rect(screen, cooldown_fill_rect, (255, 100, 0), (150, 50, 0), horizontal=True)
        pygame.draw.rect(screen, (255, 255, 255), cooldown_rect, 2)
        draw_text_outline(screen, f"BOMBA (F) CD", hud_font, (255, 255, 255), (0, 0, 0), (695, 78), center=False)

    # --- Outras informações ---
    draw_text_outline(screen, f"Nível: {level}", hud_font, (255, 255, 255), (0, 0, 0), (700, 10), center=False)
    draw_text_outline(screen, f"Chaves: {player.keys}", hud_font, (255, 255, 255), (0, 0, 0), (700, 30), center=False)
    # Objetivo da Fase
    draw_text_outline(screen, f"Notas: {player.notes}/{required_notes}", hud_font, (180, 0, 255), (0, 0, 0), (700, 50), center=False)
    draw_text_outline(screen, f"Bomba(F): {player.light_bombs}", hud_font, (255, 100, 0), (0, 0, 0), (550, 10), center=False)
    
    # Mensagens
    for i, msg in enumerate(global_messages):
        draw_text_outline(screen, msg["text"], small_font, msg["color"], (0, 0, 0), (400, 570 - i*20), center=True)

    # Se escondido
    if player.is_hidden:
         draw_text_outline(screen, "ESCONDIDO", alert_font, (0, 255, 255), (0, 0, 0), (400, 300), center=True)
         
    # Se em blackout
    if player.blackout_timer > 0:
         draw_text_outline(screen, "BLACKOUT", title_font, (255, 0, 0), (0, 0, 0), (400, 200), center=True)
         
    # Se em Speed Boost
    if player.speed_boost_timer > 0:
         draw_text_outline(screen, f"SPEED BOOST: {int(player.speed_boost_timer/60)}s", alert_font, (0, 255, 255), (0, 0, 0), (400, 150), center=True)


def create_fases(difficulty_settings, musica_fase):
    # --- FUNÇÃO DE CRIAÇÃO DE FASES (COMPLETA) ---
    
    def choose_difficulty():
        return "normal"
        
    difficulty = choose_difficulty()
    diff = difficulty_settings[difficulty]

    fases = []
    # Cria 20 Níveis
    for lvl in range(1,21): 
        walls=[]
        doors=[]
        items=[]
        enemies=[]
        lockers=[] 
        
        # Paredes do mapa
        walls += [Wall(0,0,800,20), Wall(0,580,800,20), Wall(0,0,20,600), Wall(780,0,20,600)]
        
        spacing = 100
        attempts = 0
        # Aumenta a quantidade de paredes com o nível
        num_walls = int((5+lvl)*diff["wall_factor"])
        while len(walls)<num_walls+4 and attempts<200:
            w = random.randint(50, 300)
            h = random.randint(50, 300)
            x = random.randint(20, 800-w-20)
            y = random.randint(20, 600-h-20)
            new_wall = Wall(x,y,w,h)
            
            if not any(new_wall.rect.colliderect(w.rect) for w in walls):
                 center_rect = pygame.Rect(400-50, 300-50, 100, 100)
                 if not new_wall.rect.colliderect(center_rect):
                    walls.append(new_wall)
            attempts += 1
            
        # Adicionar Portas
        num_doors = int((1+lvl)*diff["door_factor"])
        for _ in range(num_doors):
            if walls:
                 wall = random.choice(walls[4:]) 
                 door_w = 40 if wall.rect.width > wall.rect.height else 10
                 door_h = 10 if wall.rect.width > wall.rect.height else 40
                 
                 door_x = random.randint(wall.rect.x, wall.rect.x + wall.rect.width - door_w)
                 door_y = random.randint(wall.rect.y, wall.rect.y + wall.rect.height - door_h)
                 
                 doors.append(Door(door_x, door_y, door_w, door_h, key_required=1 if lvl>1 else 0))

        # Adicionar Itens
        num_items = int((3+lvl)*diff["item_factor"])
        item_types = ["battery", "key", "note", "trap", "emerg_light", "light_bomb", "speed_boost"]
        for _ in range(num_items):
            # Aumenta a chance de itens de utility/combate
            item_type = random.choice(item_types) if random.random() < 0.7 else random.choice(["light_bomb", "speed_boost", "emerg_light", "note"])
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            items.append(Item(x, y, item_type))
            
        # Adicionar Inimigos
        num_enemies = int((1+lvl)*diff["enemy_factor"])
        # Aumenta a velocidade do inimigo gradualmente
        enemy_speed = diff["enemy_speed"] + (lvl * 0.1) 
        for i in range(num_enemies):
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            if i % 3 == 0:
                 enemies.append(Lurker(x, y, speed=enemy_speed * 0.7))
            else:
                 enemies.append(Enemy(x, y, speed=enemy_speed))
                 
        # Adicionar Armários (Lockers)
        num_lockers = int(2 * diff["locker_factor"])
        for _ in range(num_lockers):
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            lockers.append(Locker(x, y))

        fases.append({"walls": walls, "doors": doors, "items": items, "enemies": enemies, "lockers": lockers, "bg_music": musica_fase[(lvl-1)%len(musica_fase)]})
        
    return fases

def use_light_bomb(player, enemies, screen):
    if player.light_bombs > 0 and player.light_bomb_cooldown <= 0:
        player.light_bombs -= 1
        player.light_bomb_cooldown = 60 * 10 # 10 segundos de cooldown
        add_message("BOMBA DE LUZ ATIVADA!", (255, 150, 0))

        stun_radius = 300
        stunned_count = 0
        
        # Efeito visual de flash para o jogador
        temp_surf = pygame.Surface((800, 600), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (255, 255, 255, 180), player.rect.center, stun_radius) 
        screen.blit(temp_surf, (0, 0))
        pygame.display.flip()
        pygame.time.delay(100)
        
        for enemy in enemies:
             dist = math.hypot(enemy.rect.centerx - player.rect.centerx, enemy.rect.centery - player.rect.centery)
             if dist < stun_radius and not enemy.is_stunned:
                 enemy.is_stunned = True
                 enemy.stun_timer = 60 * 5 # 5 segundos de atordoamento
                 stunned_count += 1
                 
        if stunned_count > 0:
            player.sanity = min(100, player.sanity + 10 * stunned_count)
            add_message(f"{stunned_count} inimigo(s) atordoado(s)!", (0, 255, 255))
            if stunt_sound: stunt_sound.play()
        
    elif player.light_bomb_cooldown > 0:
        add_message("Bomba em COOLDOWN.", (255, 0, 0))
    else:
        add_message("Você não tem Bombas de Luz.", (255, 0, 0))


def game_loop():
    global global_messages
    
    # Configuração de Dificuldade
    difficulty_settings = {
        "easy": {"wall_factor": 0.5, "door_factor": 0.5, "item_factor": 1.5, "enemy_factor": 0.5, "enemy_speed": 2.5, "locker_factor": 2},
        "normal": {"wall_factor": 1.0, "door_factor": 1.0, "item_factor": 1.0, "enemy_factor": 1.0, "enemy_speed": 3.5, "locker_factor": 1},
        "hard": {"wall_factor": 1.5, "door_factor": 1.5, "item_factor": 0.5, "enemy_factor": 1.5, "enemy_speed": 4.5, "locker_factor": 0.5}
    }
    
    fases = create_fases(difficulty_settings, musica_fase)
    MAX_LEVEL = len(fases)
    current_level = 1
    
    # Inicialização do Jogador
    player = Player(400, 300)
    scare_engine = RandomScare()
    
    if not fases:
        print("Erro: Nenhuma fase criada. Verifique a função create_fases.")
        return

    # IMPORTANTE: Inicialização das variáveis para que 'nonlocal' funcione em setup_level
    walls = []
    doors = []
    items = []
    enemies = []
    lockers = []
    
    # Variáveis de Estado da Fase
    REQUIRED_NOTES = 3  # Número fixo de notas necessárias para o objetivo da fase
    exit_key_is_available = False
    
    # --- Função de Setup da Fase ---
    def setup_level(level_num):
        nonlocal walls, doors, items, enemies, lockers, exit_key_is_available
        if level_num > MAX_LEVEL:
            # FIM DO JOGO / VITÓRIA
            add_message("VITÓRIA! Você escapou de todos os níveis!", (0, 255, 0))
            return False 
            
        current_phase = fases[level_num - 1]
        walls, doors, items, enemies, lockers = current_phase["walls"], current_phase["doors"], current_phase["items"], current_phase["enemies"], current_phase["lockers"]
        
        # Reposiciona o jogador no centro da nova fase
        player.rect.x, player.rect.y = 400, 300 
        # Mantém itens não-essenciais, zera notas e chaves normais
        player.notes = 0 
        player.keys = 0
        exit_key_is_available = False
        
        # Reinicia o estado dos inimigos para evitar stun transferido
        for enemy in enemies:
             enemy.is_stunned = False
             enemy.stun_timer = 0
             
        play_bg_music(current_phase["bg_music"])
        add_message(f"--- NÍVEL {level_num} INICIADO ---", (0, 255, 0))
        add_message(f"Objetivo: Coletar {REQUIRED_NOTES} notas.", (255, 255, 0))
        return True

    # Inicia a primeira fase
    if not setup_level(current_level):
        return

    running = True
    while running:
        # --- 1. Entrada do Usuário ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: 
                    player.is_light_on = not player.is_light_on
                    player.blackout_timer = 0 # Cancela blackout se tentar ligar

                if event.key == pygame.K_f: # Novo atalho: Usa Light Bomb
                    # NOTE: screen is passed to draw the flash effect immediately
                    use_light_bomb(player, enemies, screen)

                if event.key == pygame.K_e: 
                    # Interação: Portas
                    door_opened = False
                    for door in doors:
                        if player.rect.colliderect(door.rect):
                            if door.locked:
                                if player.keys >= door.key_required:
                                    door.locked = False
                                    player.keys -= door.key_required
                                    if door_sound: door_sound.play()
                                    add_message(f"Porta destrancada! Chaves restantes: {player.keys}", (0, 255, 0))
                                    door_opened = True
                                else:
                                    add_message(f"Porta trancada. Requer {door.key_required} chave(s).", (255, 0, 0))
                            break
                            
                    # Interação: Armários (Lockers)
                    locker_interacted = False
                    if not door_opened:
                        for locker in lockers:
                            if player.rect.colliderect(locker.rect):
                                if player.is_hidden:
                                    player.is_hidden = False
                                    player.current_locker = None
                                    add_message("Você saiu do armário.", (0, 200, 255))
                                else:
                                    player.is_hidden = True
                                    player.current_locker = locker
                                    add_message("Você se escondeu no armário.", (0, 255, 0))
                                locker_interacted = True
                                break
                            
                    # Interação: Itens
                    items_to_remove = []
                    for item in items:
                        if player.rect.colliderect(item.rect):
                            if item.type == "battery": player.light_energy = min(100, player.light_energy + 30); items_to_remove.append(item); add_message("Bateria coletada (+30 Luz)", (0, 255, 0))
                            elif item.type == "key": 
                                # Verifica se é a chave de SAÍDA (A CHAVE DE SAÍDA É SEMPRE GERADA em (700, 500))
                                if exit_key_is_available and item.rect.x == 700 and item.rect.y == 500:
                                    current_level += 1
                                    if not setup_level(current_level): # Tenta ir para a próxima fase
                                        running = False # Fim do jogo
                                    break # Sai do loop de itens, pois a fase mudou
                                else:
                                    player.keys += 1; items_to_remove.append(item); add_message("Chave coletada", (255, 220, 0))
                            
                            elif item.type == "note": 
                                player.notes += 1
                                items_to_remove.append(item)
                                add_message(f"Nota {player.notes}/{REQUIRED_NOTES} coletada!", (180, 0, 255))
                                # Checa a condição de vitória e gera a chave
                                if player.notes >= REQUIRED_NOTES and not exit_key_is_available:
                                     items.append(Item(700, 500, "key")) # Adiciona a CHAVE DE SAÍDA (Item 'key')
                                     exit_key_is_available = True
                                     add_message("CHAVE DE SAÍDA APARECEU em (700, 500)!", (255, 255, 0))

                            elif item.type == "trap": 
                                player.sanity = max(0, player.sanity - 20) 
                                player.is_slowed = True 
                                pygame.time.set_timer(pygame.USEREVENT + 2, 3000) 
                                if stunt_sound: stunt_sound.play()
                                items_to_remove.append(item)
                                add_message("ARMADILHA! Sanidade -20", (255, 0, 0))
                            elif item.type == "light_bomb": player.light_bombs += 1; items_to_remove.append(item); add_message("Bomba de Luz coletada", (255, 100, 0)) 
                            elif item.type == "speed_boost": 
                                player.speed_boost_timer = 60 * 8 
                                items_to_remove.append(item)
                                add_message("Speed Boost ativado!", (0, 255, 255))
                            
                            
                    for item in items_to_remove: 
                        if item in items: # Garantir que o item ainda esteja na lista (evita erro após transição de fase)
                           items.remove(item)

                if event.key == pygame.K_q: # Usa item de emergência
                    if player.emergency_lights > 0:
                        player.emergency_lights -= 1
                        player.light_energy = 100
                        player.sanity = min(100, player.sanity + 25)
                        player.blackout_timer = 0
                        add_message("Luz de Emergência Ativada!", (0, 255, 255))
                        
            if event.type == pygame.USEREVENT + 2: # Fim do efeito de armadilha
                 player.is_slowed = False
                 pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                 
        
        # --- 2. Atualização Lógica ---
        
        mouse_pos = pygame.mouse.get_pos()
        player.update_light_direction(mouse_pos)
        
        min_dist_to_enemy = 500
        if enemies:
            for enemy in enemies:
                dist = math.hypot(enemy.rect.centerx - player.rect.centerx, enemy.rect.centery - player.rect.centery)
                min_dist_to_enemy = min(min_dist_to_enemy, dist)
        
        collision_rects = [w.rect for w in walls] + [d.rect for d in doors if d.locked] + [l.rect for l in lockers]
        
        player.move(pygame.key.get_pressed(), collision_rects)
        player.manage_light()
        player.update_status(enemies, min_dist_to_enemy) 
        
        # Atualiza inimigos e checa colisão com o jogador
        for enemy in enemies:
            enemy.update(player, collision_rects) 
            
            # Checa se o inimigo foi atordoado pela luz
            if enemy.is_in_light_cone(player) and player.is_light_on and player.light_energy > 80 and not enemy.is_stunned:
                 enemy.is_stunned = True
                 enemy.stun_timer = 60 * 3 
                 player.sanity = min(100, player.sanity + 5)
                 if stunt_sound: stunt_sound.play()
                 add_message("Inimigo atordoado!", (0, 255, 255))
            
            if enemy.rect.colliderect(player.rect) and not player.is_hidden:
                add_message("CAPTURA!", (255, 0, 0))
                running = False 
                
        # Atualiza mensagens
        global_messages[:] = [msg for msg in global_messages if msg["time"] > 0]
        for msg in global_messages: msg["time"] -= 1

        # Atualiza o motor de sustos
        scare_engine.update(current_level, player.sanity)

        # --- 3. Controle Global de Áudio e Blackout ---
        if player.blackout_timer > 0:
            if bg_music: bg_music.set_volume(0.05) 
            if enemy_whispers_sound: enemy_whispers_sound.set_volume(0.0)
            if enemy_steps_sound: enemy_steps_sound.set_volume(0.0)
        
        # --- 4. Desenho ---
        draw_game_elements(screen, player, walls, doors, items, enemies, scare_engine, lockers)
        # O HUD precisa do REQUIRED_NOTES agora
        draw_hud(screen, player, current_level, REQUIRED_NOTES, hud_font, title_font, small_font)
        
        pygame.display.flip()
        clock.tick(60)

    # Lógica de fim de jogo (se o loop terminar)
    if current_level > MAX_LEVEL:
        print("Fim de Jogo: VITÓRIA!")
    else:
        print("Fim de Jogo: CAPTURADO!")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()