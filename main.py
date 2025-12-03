import pygame, sys, math, random

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Terror STEM - SANIDADE E BLACKOUTS")
clock = pygame.time.Clock()

try:
    font = pygame.font.SysFont("Orbitron",28)
    small_font = pygame.font.SysFont("Orbitron",20)
    title_font = pygame.font.SysFont("Orbitron",60)
    alert_font = pygame.font.SysFont("Orbitron", 35) 
    hud_font = pygame.font.SysFont("Orbitron", 18)
    horror_font = pygame.font.SysFont("Courier New", 40, bold=True) 
except:
    font = pygame.font.SysFont("Arial", 28, bold=True)
    small_font = pygame.font.SysFont("Arial", 20)
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    alert_font = pygame.font.SysFont("Arial", 35, bold=True)
    hud_font = pygame.font.SysFont("Arial", 18, bold=True)
    horror_font = pygame.font.SysFont("Arial", 40, bold=True)


pygame.mixer.init()
musica_fase = ["../assents/sounds/phase1.mp3", "../assents/sounds/phase2.mp3", "../assents/sounds/phase3.mp3"]
bg_music = None
sanity_scare_sound = None 

try:
    scream_sound = pygame.mixer.Sound("../assents/sounds/scare_scream_intense.mp3") 
    door_sound = pygame.mixer.Sound("../assents/sounds/door.mp3")
    stunt_sound = pygame.mixer.Sound("../assents/sounds/stunt.mp3") 
    heartbeat_slow_sound = pygame.mixer.Sound("../assents/sounds/heartbeat_slow.mp3")
    heartbeat_fast_sound = pygame.mixer.Sound("../assents/sounds/heartbeat_fast.mp3")
    enemy_whispers_sound = pygame.mixer.Sound("../assents/sounds/enemy_whispers.mp3")
    enemy_steps_sound = pygame.mixer.Sound("../assents/sounds/enemy_steps.mp3")
    static_noise_sound = pygame.mixer.Sound("../assents/sounds/static_noise.mp3")
    sanity_scare_sound = pygame.mixer.Sound("../assents/sounds/sanity_scare.mp3") 
    
    heartbeat_slow_sound.set_volume(0.0); heartbeat_fast_sound.set_volume(0.0)
    heartbeat_slow_sound.play(-1); heartbeat_fast_sound.play(-1)
    
    enemy_whispers_sound.set_volume(0.0); enemy_whispers_sound.play(-1)
    enemy_steps_sound.set_volume(0.0); enemy_steps_sound.play(-1)
    static_noise_sound.set_volume(0.0); static_noise_sound.play(-1)

except Exception as e:
    print(f"Erro ao carregar sons: {e}. Alguns efeitos sonoros podem estar desativados.")
    scream_sound = None; door_sound = None; stunt_sound = None 
    heartbeat_slow_sound = None; heartbeat_fast_sound = None
    enemy_whispers_sound = None; enemy_steps_sound = None
    static_noise_sound = None
    sanity_scare_sound = None 

def play_bg_music(path):
    global bg_music
    try:
        if bg_music: bg_music.stop()
        bg_music = pygame.mixer.Sound(path)
        bg_music.set_volume(0.5)
        bg_music.play(-1)
    except:
        bg_music = None


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


class Player:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,25,25)
        self.base_speed = 5 
        self.light_energy = 100 
        self.sprint_energy = 100 
        self.sanity = 100          
        self.keys = 0
        self.notes = 0 
        self.emergency_lights = 0 
        self.walk_anim = 0
        self.is_sprinting = False
        self.is_light_on = True 
        self.noise_level = 0    
        self.is_slowed = False 
        self.light_dir_vector = (0, 0) 
        self.is_hidden = False 
        self.current_locker = None 
        self.blackout_timer = 0    

    def update_status(self, enemies, distance_to_closest):
      
        if self.is_hidden:
            self.sanity = min(100, self.sanity + 0.1)
        else:
            if not self.is_light_on or self.light_energy <= 0:
                self.sanity = max(0, self.sanity - 0.2) 
            
            if distance_to_closest < 150:
                loss_factor = (150 - distance_to_closest) / 150 * 0.5
                self.sanity = max(0, self.sanity - loss_factor) 
                
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

    def move(self,keys,walls):
        if self.is_hidden: return

        current_speed = self.base_speed
        if self.light_energy <= 0 and not self.is_slowed:
            current_speed *= 0.5 
            self.is_slowed = True
        elif self.light_energy > 0 and self.is_slowed:
            self.is_slowed = False 
        
        if self.sanity < 20: current_speed *= 0.7 
        
        dx=dy=0; moving=False
        is_sprint_key_down = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if is_sprint_key_down and self.sprint_energy > 0: 
            spd = current_speed * 1.8
            self.sprint_energy = max(0, self.sprint_energy - 0.7)
            self.is_sprinting = True
        else:
            spd = current_speed
            self.sprint_energy = min(100, self.sprint_energy + 0.3) 
            self.is_sprinting = False

        if keys[pygame.K_w]: dy -= spd; moving=True
        if keys[pygame.K_s]: dy += spd; moving=True
        if keys[pygame.K_a]: dx -= spd; moving=True
        if keys[pygame.K_d]: dx += spd; moving=True
        
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall.rect): self.rect.x -= dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect): self.rect.y -= dy
            
        if moving: self.walk_anim += 0.2
        else: self.walk_anim = 0
        
        if self.is_sprinting and not self.is_light_on:
            self.noise_level = min(100, self.noise_level + 4) 
        elif self.is_sprinting and self.is_light_on:
            self.noise_level = min(100, self.noise_level + 2) 
        else:
            self.noise_level = max(0, self.noise_level - 2) 

    def use_light(self):
        if self.is_hidden:
            if self.is_light_on:
                 self.light_energy = max(0, self.light_energy - 0.08) 
            return

        if self.is_light_on and self.blackout_timer <= 0: # Não consome se em blackout
            consumption = 0.4 
            if self.is_sprinting: consumption += 0.2 
            
            if self.light_energy > 0: 
                self.light_energy = max(0, self.light_energy - consumption)
            else:
                self.is_light_on = False 
                
        elif not self.is_sprinting and self.blackout_timer <= 0:
             self.light_energy = min(100, self.light_energy + 0.1)
             
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

        if self.blackout_timer > 0 and self.blackout_timer % 10 < 5:
            player_color_base = (50, 50, 50)
            player_color_dark = (10, 10, 10)

        draw_gradient_rect(surface, (self.rect.x, self.rect.y + offset, self.rect.width, self.rect.height),
                           (player_color_base[0], player_color_base[1] + offset, player_color_base[2]), player_color_dark)
        
        pygame.draw.ellipse(surface, (player_color_base[0]*0.8, player_color_base[1]*0.8, player_color_base[2]*0.8),
                            (self.rect.x + self.rect.width//4, self.rect.y - 5 + offset, self.rect.width//2, self.rect.height//2))

        if self.is_slowed:
             temp_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
             temp_surf.fill((255,0,0, random.randint(50, 100))) 
             surface.blit(temp_surf, self.rect.topleft)


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
        if not player.is_light_on or player.light_energy <= 0 or player.blackout_timer > 0: # Adicionado Blackout
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

    def update(self,player,walls):
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
                for wall in walls:
                    if self.rect.colliderect(wall.rect): self.rect.x -= move_x
                self.rect.y += move_y
                for wall in walls:
                    if self.rect.colliderect(wall.rect): self.rect.y -= move_y
                    
            self.flash_timer=5
            
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
            for wall in walls:
                if self.rect.colliderect(wall.rect): self.rect.x -= move_x; self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.rect.y += move_y
            for wall in walls:
                if self.rect.colliderect(wall.rect): self.rect.y -= move_y; self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

            self.flash_timer=max(self.flash_timer-0.1,0)
            if bg_music: bg_music.set_volume(max(0.1, min(0.5, bg_music.get_volume())))
            if enemy_whispers_sound: enemy_whispers_sound.set_volume(max(0.0, enemy_whispers_sound.get_volume() - 0.01))
            if enemy_steps_sound: enemy_steps_sound.set_volume(max(0.0, enemy_steps_sound.get_volume() - 0.01))

            if self.teleport_cooldown > 0: self.teleport_cooldown -= 1
            elif not is_alerted and distance > 300 and random.random() < 0.001: 
                self.teleport_active = True
                pygame.time.set_timer(pygame.USEREVENT + 1, 300) 
                
                new_x, new_y = self.rect.x, self.rect.y
                for _ in range(50): 
                    test_x = random.randint(50, 750); test_y = random.randint(50, 550)
                    test_rect = pygame.Rect(test_x, test_y, self.rect.width, self.rect.height)
                    if not any(test_rect.colliderect(w.rect) for w in walls) and \
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
            if scare_type == "INSTANT":
                scream_sound.set_volume(random.uniform(0.8,1.0))
                scream_sound.play()
            elif scare_type == "SANITY":
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
            if random.random() < 0.003 + 0.0002*level:
                self.trigger_scare(level, "INSTANT")

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
            
            if self.flash_timer > 0 and self.scare_type == "INSTANT":
                flash = pygame.Surface((800,600), pygame.SRCALPHA)
                flash.fill((255,255,255, random.randint(80,150)))
                surface.blit(flash, (0,0))
                self.flash_timer -= 1
                
            for p in self.particles:
                pygame.draw.rect(surface, p[4], (p[0] + shake_x, p[1] + shake_y, p[2], p[2]))

            if self.scare_type != "SANITY" or random.random() < 0.5: # Sanity scare é mais sutil
                temp_surf = self.image.copy()
                alpha = random.randint(100,255)
                temp_surf.set_alpha(alpha)
                surface.blit(temp_surf, (self.x+shake_x, self.y+shake_y))
            
            if random.random() < 0.05:
                blink = pygame.Surface((800,600), pygame.SRCALPHA)
                blink.fill((255,255,255, random.randint(50,100)))
                surface.blit(blink, (0,0))



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
    if player.light_energy <= 0 and not player.is_hidden:
        night_surf = pygame.Surface((800, 600), pygame.SRCALPHA)
        night_surf.fill((0, 50, 0, 150)) 
        
        pygame.draw.circle(night_surf, (0, 200, 0, 80), player.rect.center, 80)

        for i in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            if random.random() < 0.2:
                pygame.draw.rect(night_surf, (255, 255, 255, 50), (x, y, 1, 1))

        for enemy in enemies:
             if math.hypot(enemy.rect.centerx - player.rect.centerx, enemy.rect.centery - player.rect.centery) < 100:
                 r = random.randint(50, 100)
                 pygame.draw.circle(night_surf, (255, 0, 0, 80), enemy.rect.center, r)

        surface.blit(night_surf, (0, 0))

def draw_game_elements(screen, player, walls, doors, items, enemies, scare, lockers):
    screen.fill((0,0,0))
    
    for wall in walls: wall.draw(screen)
    for door in doors: door.draw(screen)
    for item in items: item.draw(screen)
    for locker in lockers: locker.draw(screen) 
    
    light_surface=pygame.Surface((800,600),pygame.SRCALPHA)
    light_radius = int(player.light_energy * 1.5) if player.light_energy > 0 and player.is_light_on and player.blackout_timer <= 0 else 20

    if player.light_energy > 0 and player.is_light_on and not player.is_hidden and player.blackout_timer <= 0:
        draw_light_cone(light_surface, player, light_radius)
    elif player.light_energy <= 0 and not player.is_hidden:
        draw_failed_night_vision(light_surface, player, enemies) 
    
    screen.blit(light_surface,(0,0),special_flags=pygame.BLEND_RGBA_ADD)

    for enemy in enemies: enemy.draw(screen)
    player.draw(screen)

    scare.draw(screen)
    
    panic_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    
    min_dist = min([math.hypot(e.rect.centerx - player.rect.centerx, e.rect.centery - player.rect.centery) for e in enemies]) if enemies else 500
    

    panic_factor = max(0, 1 - min_dist/200) + player.noise_level/150 + max(0, (100 - player.sanity)/100 * 1.5)
    
    if random.random() < panic_factor:
        shake_x = random.randint(-int(panic_factor*3), int(panic_factor*3))
        shake_y = random.randint(-int(panic_factor*3), int(panic_factor*3))
        screen.blit(screen, (shake_x, shake_y)) 
        
        for i in range(int(300 * panic_factor)):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            pygame.draw.rect(panic_surface, (255, 255, 255, random.randint(0, int(150 * panic_factor))), (x, y, 1, 1))

    red_alpha = min(150, int(panic_factor * 150))
    pygame.draw.rect(panic_surface, (150, 0, 0, red_alpha), (0,0, 800, 600))
    
    if player.sanity < 15:
         for y in range(0, 600, 50):
             offset = random.randint(-15, 15)
             pygame.draw.line(panic_surface, (255, 255, 255, 50), (0, y), (800, y + offset), 5)
             
    if player.blackout_timer > 0:
        dark_alpha = 255 if player.blackout_timer > 10 else int(255 * (player.blackout_timer / 10))
        dark_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, dark_alpha))
        screen.blit(dark_surface, (0, 0))

    screen.blit(panic_surface, (0, 0))



def create_fases(difficulty_settings, musica_fase):
    # ... (Mantido)
    difficulty = choose_difficulty()
    diff = difficulty_settings[difficulty]

    fases = []
    for lvl in range(1,21): 
        walls=[]
        doors=[]
        items=[]
        enemies=[]
        lockers=[] 
        
        walls += [Wall(0,0,800,20), Wall(0,580,800,20), Wall(0,0,20,600), Wall(780,0,20,600)]
        
        spacing = 100
        attempts = 0
        num_walls = int((5+lvl)*diff["wall_factor"])
        while len(walls)<num_walls+4 and attempts<200:
            x = random.randint(50,700)
            y = random.randint(50,500)
            if random.random()>0.5: w=random.randint(50,150); h=20
            else: w=20; h=random.randint(50,150)
            new_wall = Wall(x,y,w,h)
            too_close = any(new_wall.rect.colliderect(pygame.Rect(w.rect.x-spacing,w.rect.y-spacing,w.rect.width+2*spacing,w.rect.height+2*spacing)) for w in walls)
            if not too_close:
                walls.append(new_wall)
            attempts +=1
            
        doors.append(Door(760,540,20,40,key_required=1))
        
        total_items = diff["item_count"] + 1 
        items.append(Item(random.randint(50,750),random.randint(50,550),"key"))
        items.append(Item(random.randint(50,750),random.randint(50,550),"note"))
        
        if lvl >= 5: 
            items.append(Item(random.randint(50,750),random.randint(50,550),"trap"))
            lockers.append(Locker(random.randint(50,750), random.randint(50,500))) 
            
        if lvl >= 10: 
            items.append(Item(random.randint(50,750),random.randint(50,550),"trap"))
            items.append(Item(random.randint(50,750),random.randint(50,550),"emerg_light"))

        for _ in range(total_items - len(items)):
            items.append(Item(random.randint(50,750),random.randint(50,550),"battery"))
            
        for _ in range(diff["enemy_count"]):
            enemy_speed = diff["enemy_speed"]
            if lvl >= 10 and random.random() < 0.5:
                 enemy_speed += random.uniform(0.5, 1.5)
            
            enemies.append(Enemy(random.randint(50,750),random.randint(50,550),speed=enemy_speed))
            
        if lvl >= 7:
            enemies.append(Lurker(random.randint(50,750),random.randint(50,550)))
        
        fases.append({
            "walls":walls,
            "doors":doors,
            "enemies":enemies,
            "lockers":lockers, 
            "music":musica_fase[((lvl-1)//3)%len(musica_fase)],
            "original_items": [item.copy() for item in items] 
        })
    
    return fases, difficulty

def init_level(player, lvl, fases):
    if lvl >= len(fases):
        print("Parabéns! Você completou todas as fases!")
        return "FINISHED"
    
    player.rect.topleft=(50,550) 
    player.light_energy = 100
    player.sprint_energy = 100
    player.sanity = 100 
    player.is_light_on = True 
    player.noise_level = 0
    player.is_slowed = False 
    player.is_hidden = False 
    player.current_locker = None
    player.blackout_timer = 0 
    
    fase_data = fases[lvl]
    walls = fase_data["walls"]
    doors = fase_data["doors"]
    enemies = [type(e)(e.rect.x, e.rect.y, e.speed) for e in fase_data["enemies"]] 
    lockers = fase_data["lockers"]
    
    fase_itens_iniciais = [item.copy() for item in fase_data["original_items"]]
    items = [item.copy() for item in fase_data["original_items"]]
    
    play_bg_music(fase_data["music"])
    
    return walls, doors, enemies, items, fase_itens_iniciais, lockers

def next_level(player, current_level, fases):
    new_level = current_level + 1
    result = init_level(player, new_level, fases)
    if result == "FINISHED":
        return "MENU", new_level
    return result[0], result[1], result[2], result[3], result[4], result[5], new_level


def pause_menu():
    paused = True
    result = "PAUSE"
    buttons = [
        {"text":"RETOMAR","pos":(250,250),"color1":(0,255,100),"color2":(0,150,50),"action":"PAUSE"},
        {"text":"MENU PRINCIPAL","pos":(250,320),"color1":(255,200,0),"color2":(150,100,0),"action":"MENU"},
        {"text":"SAIR","pos":(250,390),"color1":(255,50,50),"color2":(150,0,0),"action":"QUIT"}
    ]
    pause_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    pause_surface.fill((0, 0, 0, 180))
    screen.blit(pause_surface, (0, 0))
    draw_text_outline(screen,"JOGO PAUSADO",title_font,(255,255,255),(0,0,0),(150,150))
    pygame.display.flip()
    while paused:
        mx,my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN: click=True
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: 
                paused=False
                result = "PAUSE"
        for b in buttons:
            rect = pygame.Rect(b["pos"][0],b["pos"][1],300,50)
            if rect.collidepoint((mx,my)):
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color2"],b["color1"])
                if click: 
                    paused=False
                    result = b["action"]
            else:
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color1"],b["color2"])
            draw_text_outline(screen,b["text"],small_font,(255,255,255),(0,0,0),(rect.x+60,rect.y+10))
        pygame.display.update(250, 150, 300, 300) 
        clock.tick(15)
    return result

def choose_difficulty():
    choosing = True
    selected = "medio"
    buttons = [
        {"text":"Fácil","pos":(250,220),"color1":(0,200,255),"color2":(0,100,200),"key":pygame.K_1,"value":"facil"},
        {"text":"Médio","pos":(250,290),"color1":(0,255,100),"color2":(0,150,50),"key":pygame.K_2,"value":"medio"},
        {"text":"Difícil","pos":(250,360),"color1":(255,100,0),"color2":(150,50,0),"key":pygame.K_3,"value":"dificil"},
        {"text":"INSANO","pos":(250,430),"color1":(255,50,50),"color2":(150,0,0),"key":pygame.K_4,"value":"insano"}
    ]
    while choosing:
        screen.fill((10,10,10)) 
        draw_text_outline(screen,"ESCOLHA A DIFICULDADE",font,(0,255,200),(0,0,0),(120,150))
        mx,my = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN: click=True
            if event.type==pygame.KEYDOWN:
                for b in buttons:
                    if event.key==b["key"]: selected=b["value"]; choosing=False
        for b in buttons:
            rect = pygame.Rect(b["pos"][0],b["pos"][1],300,50)
            if rect.collidepoint((mx,my)):
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color2"],b["color1"])
                if click: selected=b["value"]; choosing=False
            else:
                draw_gradient_rect(screen,(rect.x,rect.y,rect.width,rect.height),b["color1"],b["color2"])
            draw_text_outline(screen,b["text"],small_font,(255,255,255),(0,0,0),(rect.x+100,rect.y+10))
        pygame.display.flip()
        clock.tick(60)
    return selected

def death_screen():
    screen.fill((0,0,0))
    draw_text_outline(screen,"VOCÊ MORREU!", title_font, (255,0,0), (0,0,0), (150,200))
    if scream_sound: scream_sound.set_volume(1.0); scream_sound.play()
    pygame.display.flip()
    pygame.time.delay(1000)

def game_loop(fases, difficulty):
    global global_messages

    level = 0
    player = Player(50,550)
    scare = RandomScare()
    
    TELEPORT_END_EVENT = pygame.USEREVENT + 1
    
    init_result = init_level(player, level, fases)
    if init_result == "FINISHED": return "MENU"

    walls, doors, enemies, items, fase_itens_iniciais, lockers = init_result
    
    running = True
    while running:
        
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return "QUIT"
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    pause_result = pause_menu()
                    if pause_result == "QUIT": return "QUIT"
                    if pause_result == "MENU": return "MENU"
                
                if event.key==pygame.K_e:
                    if player.blackout_timer > 0:
                        add_message("Não é possível ligar/desligar a luz durante um Blackout!", (255, 100, 100))
                    elif player.light_energy > 0 or not player.is_light_on:
                        player.is_light_on = not player.is_light_on
                    else:
                        player.is_light_on = False 
                        add_message("BATERIA INSUFICIENTE. (E) sem efeito.", (255, 100, 100))
                        
                if event.key==pygame.K_h:
                    if not player.is_hidden:
                        for locker in lockers:
                            if player.rect.colliderect(locker.rect):
                                player.is_hidden = True
                                player.current_locker = locker
                                locker.is_open = True
                                player.rect.center = locker.rect.center
                                add_message("Escondido. Pressione H para sair.", (0, 255, 0))
                                break
                    else:
                        if all(math.hypot(e.rect.centerx - player.rect.centerx, e.rect.centery - player.rect.centery) > 100 for e in enemies):
                            player.is_hidden = False
                            player.current_locker.is_open = False
                            player.current_locker = None
                            add_message("Saiu. Cuidado!", (255, 255, 0))
                        else:
                            add_message("Não pode sair! Inimigo muito perto!", (255, 50, 50))
                            
                if event.key==pygame.K_SPACE and player.emergency_lights > 0 and not player.is_hidden:
                    player.emergency_lights -= 1
                    add_message("FLASH! Inimigos Atordoados!", (0, 255, 255))
                    if stunt_sound: stunt_sound.play()
                    for enemy in enemies:
                        enemy.is_stunned = True
                        enemy.stun_timer = 60 * 3
                        enemy.flash_timer = 10 
                        
                if event.key==pygame.K_F1: 
                    return "MENU"

            
            if event.type == TELEPORT_END_EVENT:
                for enemy in enemies:
                    if enemy.teleport_active:
                        enemy.teleport_active = False
                pygame.time.set_timer(TELEPORT_END_EVENT, 0) 

 
        min_dist = min([math.hypot(e.rect.centerx - player.rect.centerx, e.rect.centery - player.rect.centery) for e in enemies]) if enemies else 500
 
        player.move(keys,walls)
        player.use_light()
        player.update_light_direction(mouse_pos) 
        player.update_status(enemies, min_dist) 
        

        if player.sanity <= 0:
            death_screen()
            return "MENU"

        if heartbeat_slow_sound and heartbeat_fast_sound:
            if min_dist < 100:
                heartbeat_fast_sound.set_volume(min(1.0, (100 - min_dist) / 100))
                heartbeat_slow_sound.set_volume(0.0)
            elif min_dist < 250:
                 heartbeat_slow_sound.set_volume(min(1.0, (250 - min_dist) / 150 * 0.5))
                 heartbeat_fast_sound.set_volume(0.0)
            else:
                heartbeat_slow_sound.set_volume(0.0)
                heartbeat_fast_sound.set_volume(0.0)
        
        if static_noise_sound:
             static_vol = max(0.0, min(0.7, player.noise_level/100 * 0.3 + (1 - min_dist/200) * 0.4 + max(0, (100 - player.sanity)/100 * 0.5))) # Ruído ligado à sanidade
             static_noise_sound.set_volume(static_vol)
     
        for enemy in enemies:
            enemy.update(player,walls)
            if player.rect.colliderect(enemy.rect) and not player.is_hidden:
                death_screen()
                player = Player(50, 550) 
                
                level_result = init_level(player, level, fases)
                if level_result == "FINISHED": return "MENU"
                walls, doors, enemies, items, fase_itens_iniciais, lockers = level_result

        for item in items[:]:
            if player.rect.colliderect(item.rect):
                if item.type=="battery": 
                    player.light_energy=min(player.light_energy+50,100)
                    if not player.is_light_on: player.is_light_on = True; add_message("Bateria Coletada. Lanterna LIGADA.", (0, 255, 0))
                    player.sanity = min(100, player.sanity + 10) # Bateria recupera um pouco de sanidade
                elif item.type=="key": 
                    player.keys+=1; add_message("Chave Coletada.", (255, 255, 0))
                elif item.type=="note": 
                    player.notes+=1; add_message("Nota Coletada. Sanidade +20!", (150, 0, 255))
                    player.sanity = min(100, player.sanity + 20)
                elif item.type=="trap": 
                    player.light_energy = max(0, player.light_energy - 10)
                    player.sanity = max(0, player.sanity - 20)
                    if player.light_energy <= 0: player.is_light_on = False
                    scare.trigger_scare(level, "INSTANT"); add_message("Armadilha! Lanterna -10%, Sanidade -20%", (255, 50, 50))
                elif item.type=="emerg_light": 
                    player.emergency_lights += 1; add_message("Luz de Emergência Coletada. (SPACE)", (0, 255, 255))
                items.remove(item)

        for door in doors:
            if player.rect.colliderect(door.rect):
                if door.locked:
                    if player.keys >= door.key_required:
                        door.locked=False; player.keys -= door.key_required
                        if door_sound: door_sound.play()
                        
                        add_message(f"Nível {level+1} CONCLUÍDO!", (0, 255, 255))
                        level_result = next_level(player, level, fases)
                        if level_result == "MENU": return "MENU" 
                        walls, doors, enemies, items, fase_itens_iniciais, lockers, level = level_result
                    else:
                        door.flash_timer=5; add_message("Porta TRANCADA. Chave necessária.", (255, 100, 100))


        scare.update(level, player.sanity)

        draw_game_elements(screen, player, walls, doors, items, enemies, scare, lockers)
        
        global_messages = [m for m in global_messages if m["time"] > 0]
        y_offset = 200
        for msg in global_messages:
            draw_text_outline(screen, msg["text"], alert_font, msg["color"], (0,0,0), (800//2, y_offset), center=True)
            msg["time"] -= 1
            y_offset += 40

        hud_box_y = 10; hud_box_w = 200; hud_box_h = 20; 
        
        luz_status = "LIGADA" if player.is_light_on and player.blackout_timer <= 0 else "APAGADA"
        if player.blackout_timer > 0: luz_status = "BLACKOUT!"
        draw_text_outline(screen,f"Luz (E): {luz_status}",small_font,(255,255,255),(0,0,0),(10,hud_box_y))
        pygame.draw.rect(screen,(50,50,0),(240,hud_box_y,hud_box_w,hud_box_h))
        light_color = (255,200,0) if player.is_light_on and player.blackout_timer <= 0 else (100,80,0)
        pygame.draw.rect(screen,light_color,(240,hud_box_y,int(player.light_energy*2),hud_box_h))
        
        draw_text_outline(screen,"Sprint:",small_font,(255,255,255),(0,0,0),(10,hud_box_y + 30))
        pygame.draw.rect(screen,(50,50,50),(240,hud_box_y+30,hud_box_w,hud_box_h))
        pygame.draw.rect(screen,(0,150,255),(240,hud_box_y+30,int(player.sprint_energy*2),hud_box_h))
        
        draw_text_outline(screen,"Ruído:",small_font,(255,255,255),(0,0,0),(10,hud_box_y + 60))
        pygame.draw.rect(screen,(50,0,50),(240,hud_box_y+60,hud_box_w,hud_box_h))
        noise_color = (min(255, int(player.noise_level*2.5)), 0, max(50, 255 - int(player.noise_level*2.5)))
        pygame.draw.rect(screen,noise_color,(240,hud_box_y+60,int(player.noise_level*2),hud_box_h))
   
        draw_text_outline(screen,"Sanidade:",small_font,(255,255,255),(0,0,0),(10,hud_box_y + 90))
        pygame.draw.rect(screen,(80,0,0),(240,hud_box_y+90,hud_box_w,hud_box_h)) # Fundo escuro/vermelho
        
        sanity_color_r = min(255, int((100 - player.sanity) * 2.5))
        sanity_color_g = min(255, int(player.sanity * 2.5))
        
        draw_gradient_rect(screen, (240, hud_box_y+90, int(player.sanity*2), hud_box_h), 
                           (255, 255, 255), (sanity_color_r, sanity_color_g, 0), horizontal=True)
                           
        if player.sanity < 20: 
            sanity_text_color = (255, 0, 0) if clock.get_fps() % 20 < 10 else (255, 255, 255)
            draw_text_outline(screen,"CRÍTICO!", small_font, sanity_text_color,(0,0,0),(240 + hud_box_w + 10, hud_box_y+90))

        draw_text_outline(screen,f"Chaves: {player.keys} | Notas: {player.notes} | Emerg. Luz (SPACE): {player.emergency_lights}",
                          font,(255,255,255),(0,0,0),(10,130))
                          
        draw_text_outline(screen,f"Fase: {level+1}/20 | Dificuldade: {difficulty.capitalize()} | Menu: F1",
                          small_font,(255,255,255),(0,0,0),(10,160))
        
        pygame.display.flip()
        clock.tick(60)
        
    return "MENU"


def main_menu_loop():
    running = True
    
    difficulty_settings = {
        "facil": {"enemy_count":2, "enemy_speed":2, "item_count":4, "wall_factor":1},
        "medio": {"enemy_count":4, "enemy_speed":3, "item_count":3, "wall_factor":1.5},
        "dificil": {"enemy_count":6, "enemy_speed":4, "item_count":2, "wall_factor":2},
        "insano": {"enemy_count":8, "enemy_speed":5, "item_count":1, "wall_factor":2.5} 
    }

    while running:
        
        fases, difficulty = create_fases(difficulty_settings, musica_fase)

        game_result = game_loop(fases, difficulty)
        
        if game_result == "QUIT":
            running = False
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu_loop()

