# main.py
import pygame
import sys
from enigma_engine import EnigmaEngine

# Initialize Pygame and Clipboard
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ENIGMA MACHINE SIMULATOR - BY HARSH LEUVA")

try:
    app_icon = pygame.image.load("icon.ico")
    pygame.display.set_icon(app_icon)
except Exception:
    pass

pygame.scrap.init() 
clock = pygame.time.Clock()

# --- THEME COLORS ---
BG_COLOR = (10, 15, 12)       
PANEL_COLOR = (20, 28, 24)    
TEXT_GREEN = (40, 255, 100)   
TEXT_DIM = (40, 100, 60)      
WHITE = (240, 255, 240)       
ACCENT_RED = (255, 60, 60)    
BAR_COLOR = (15, 20, 18)

try:
    FONT_MONO = pygame.font.SysFont("Courier New", 22, bold=True)
    FONT_LARGE = pygame.font.SysFont("Courier New", 36, bold=True)
except:
    FONT_MONO = pygame.font.Font(None, 24)
    FONT_LARGE = pygame.font.Font(None, 40)

# --- SYSTEM STATE TRACKING ---
STATE_START = "START"
STATE_AUTH = "AUTH"
STATE_ROTOR = "ROTOR"
STATE_KEY = "KEY"
STATE_LIVE = "LIVE"
current_state = STATE_START

auth_input = ""
available_rotors = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
selected_rotors = []
key_input = ""
input_text = ""
output_text = ""
clipboard_status = "" 
clipboard_timer = 0

ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ?,.()" 

def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

def draw_button(text, rect, is_hovered, color_override=None, secondary_text=None):
    color = color_override if color_override else (TEXT_GREEN if is_hovered else TEXT_DIM)
    pygame.draw.rect(screen, color, rect, 2)
    if is_hovered:
        fill_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        fill_surface.fill((*color[:3], 30)) 
        screen.blit(fill_surface, rect)
    draw_text(text, FONT_LARGE, WHITE, rect.centerx, rect.centery - (10 if secondary_text else 0), center=True)
    if secondary_text:
        draw_text(secondary_text, FONT_MONO, TEXT_DIM, rect.centerx, rect.centery + 15, center=True)

# --- MAIN LOOP ---
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    click = False
    current_time = pygame.time.get_ticks()

    if clipboard_status and current_time - clipboard_timer > 2000:
        clipboard_status = ""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True

        if event.type == pygame.KEYDOWN:
            if current_state == STATE_AUTH:
                if event.key == pygame.K_BACKSPACE:
                    auth_input = auth_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if auth_input.upper() == "QWERTY":
                        current_state = STATE_ROTOR
                else:
                    if len(auth_input) < 10 and event.unicode.isalnum():
                        auth_input += event.unicode.upper()

            elif current_state == STATE_ROTOR:
                # [BUG FIX 1] Added 'event.unicode and...' to block empty Alt/Ctrl keys crashing the app
                if event.unicode and event.unicode in "123456789":
                    rotor_index = int(event.unicode) - 1
                    r_name = available_rotors[rotor_index]
                    if r_name not in selected_rotors and len(selected_rotors) < 3:
                        selected_rotors.append(r_name)
                elif event.key == pygame.K_BACKSPACE:
                    if len(selected_rotors) > 0:
                        selected_rotors.pop()

            elif current_state == STATE_KEY:
                if event.key == pygame.K_BACKSPACE:
                    key_input = key_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(key_input) == 3:
                        enigma = EnigmaEngine(selected_rotors, key_input)
                        current_state = STATE_LIVE
                else:
                    if len(key_input) < 3 and event.unicode.isalpha():
                        key_input += event.unicode.upper()

            elif current_state == STATE_LIVE:
                if event.key == pygame.K_BACKSPACE:
                    input_text = ""
                    output_text = ""
                    enigma = EnigmaEngine(selected_rotors, key_input)
                else:
                    char = event.unicode.upper()
                    # [BUG FIX 2] Safety check for empty strings here too
                    if char and char in ALLOWED_CHARS and len(input_text) < 400:
                        input_text += char
                        encrypted_char = enigma.encrypt_char(char)
                        output_text += encrypted_char

    # --- RENDERING STATES ---
    screen.fill(BG_COLOR)

    if current_state == STATE_START:
        draw_text("ENIGMA SYSTEM SIMULATOR", FONT_LARGE, TEXT_GREEN, WIDTH//2, 180, center=True)
        draw_text("DEVELOPED BY HARSH LEUVA", FONT_MONO, ACCENT_RED, WIDTH//2, 240, center=True)
        
        btn_start = pygame.Rect(WIDTH//2 - 100, 340, 200, 50)
        hover = btn_start.collidepoint(mx, my)
        
        color = TEXT_GREEN if hover else TEXT_DIM
        pygame.draw.rect(screen, color, btn_start, 2)
        if hover:
            fill_surface = pygame.Surface((btn_start.width, btn_start.height), pygame.SRCALPHA)
            fill_surface.fill((*color[:3], 30)) 
            screen.blit(fill_surface, btn_start)
        draw_text("INITIATE SYSTEM", FONT_MONO, WHITE, btn_start.centerx, btn_start.centery, center=True)
        
        if hover and click:
            current_state = STATE_AUTH

    elif current_state == STATE_AUTH:
        draw_text("SECURITY ACCESS REQUIRED", FONT_LARGE, ACCENT_RED, WIDTH//2, 180, center=True)
        draw_text("ENTER AUTHORIZATION PASSCODE:", FONT_MONO, WHITE, WIDTH//2, 260, center=True)
        
        masked_input = "*" * len(auth_input)
        draw_text(f"> {masked_input} <", FONT_LARGE, TEXT_GREEN, WIDTH//2, 330, center=True)
        draw_text("PRESS ENTER TO VERIFY", FONT_MONO, TEXT_DIM, WIDTH//2, 420, center=True)

    elif current_state == STATE_ROTOR:
        draw_text("SELECT 3 ROTORS (CLICK OR PRESS 1-9)", FONT_LARGE, TEXT_GREEN, WIDTH//2, 40, center=True)
        
        chosen_str = " -> ".join(selected_rotors) if selected_rotors else "[EMPTY]"
        draw_text(f"CURRENT SEQUENCE: {chosen_str}", FONT_MONO, WHITE, WIDTH//2, 90, center=True)

        for i, r_name in enumerate(available_rotors):
            row = i // 5  
            col = i % 5
            
            x_offset = 115 + col * 140
            if row == 1:
                x_offset = 185 + col * 140 

            r_rect = pygame.Rect(x_offset, 160 + row * 100, 110, 80)
            is_chosen = r_name in selected_rotors
            
            if is_chosen:
                pygame.draw.rect(screen, TEXT_DIM, r_rect)
                draw_text(r_name, FONT_LARGE, BG_COLOR, r_rect.centerx, r_rect.centery, center=True)
            else:
                h = r_rect.collidepoint(mx, my)
                draw_button(r_name, r_rect, h, secondary_text=f"[{i+1}]")
                if h and click and len(selected_rotors) < 3:
                    selected_rotors.append(r_name)

        btn_reset = pygame.Rect(250, 420, 160, 45)
        btn_next = pygame.Rect(490, 420, 160, 45)

        r_hover = btn_reset.collidepoint(mx, my)
        pygame.draw.rect(screen, TEXT_GREEN if r_hover else TEXT_DIM, btn_reset, 2)
        draw_text("RESET", FONT_MONO, WHITE, btn_reset.centerx, btn_reset.centery, center=True)
        if r_hover and click:
            selected_rotors.clear()

        if len(selected_rotors) == 3:
            n_hover = btn_next.collidepoint(mx, my)
            pygame.draw.rect(screen, TEXT_GREEN if n_hover else TEXT_DIM, btn_next, 2)
            draw_text("CONFIRM", FONT_MONO, WHITE, btn_next.centerx, btn_next.centery, center=True)
            if n_hover and click:
                current_state = STATE_KEY
        else:
            draw_text("[SELECT EXACTLY 3 ROTORS TO PROCEED]", FONT_MONO, TEXT_DIM, WIDTH//2, 500, center=True)

    elif current_state == STATE_KEY:
        draw_text("ESTABLISH PRE-SHARED SYSTEM KEY", FONT_LARGE, TEXT_GREEN, WIDTH//2, 180, center=True)
        draw_text("ENTER A 3-LETTER CONFIGURATION (E.G. HBF):", FONT_MONO, WHITE, WIDTH//2, 250, center=True)
        draw_text(f"> {key_input} <", FONT_LARGE, TEXT_GREEN, WIDTH//2, 330, center=True)
        
        if len(key_input) == 3:
            draw_text("PRESS ENTER TO LOAD CONFIGURATION", FONT_MONO, WHITE, WIDTH//2, 420, center=True)

    elif current_state == STATE_LIVE:
        top_bar = pygame.Rect(0, 0, WIDTH, 40)
        pygame.draw.rect(screen, BAR_COLOR, top_bar)
        pygame.draw.line(screen, TEXT_DIM, (0, 40), (WIDTH, 40), 2)
        
        pos_letters = f"{enigma.ALPHABET[enigma.p1]}{enigma.ALPHABET[enigma.p2]}{enigma.ALPHABET[enigma.p3]}"
        
        # [BUG FIX 3] Shortened the text significantly so it never overlaps!
        config_summary = f"CFG: {'-'.join(selected_rotors)} | KEY:{key_input} | POS:{pos_letters}"
        draw_text(config_summary, FONT_MONO, TEXT_GREEN, 15, 10)
        
        # Secured Watermark pushed safely to the right
        draw_text("BY: HARSH LEUVA", FONT_MONO, ACCENT_RED, WIDTH - 260, 10)

        draw_text("🔴 ENIGMA ONLINE CRYPTO-SYSTEM", FONT_MONO, ACCENT_RED, 40, 60)

        panel_width = (WIDTH - 100) // 2
        panel_height = 360
        left_panel = pygame.Rect(40, 100, panel_width, panel_height)
        right_panel = pygame.Rect(60 + panel_width, 100, panel_width, panel_height)

        pygame.draw.rect(screen, PANEL_COLOR, left_panel)
        pygame.draw.rect(screen, PANEL_COLOR, right_panel)
        pygame.draw.rect(screen, TEXT_DIM, left_panel, 1)
        pygame.draw.rect(screen, TEXT_DIM, right_panel, 1)

        draw_text("INPUT (PLAIN TEXT)", FONT_MONO, WHITE, 55, 115)
        draw_text("OUTPUT (ENIGMA CIPHER)", FONT_MONO, TEXT_GREEN, 75 + panel_width, 115)

        def render_wrapped_text(text, rect, color):
            max_chars = 23
            words = text.split(' ')
            lines = []
            current_line = ""

            for word in words:
                while len(word) > max_chars:
                    if current_line:
                        lines.append(current_line)
                        current_line = ""
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                
                if current_line:
                    if len(current_line) + 1 + len(word) <= max_chars:
                        current_line += " " + word
                    else:
                        lines.append(current_line)
                        current_line = word
                else:
                    if word: 
                        current_line = word
                        
            if current_line:
                lines.append(current_line)

            for line_num, line in enumerate(lines):
                if line_num * 30 < rect.height - 80:
                    draw_text(line, FONT_MONO, color, rect.x + 20, rect.y + 60 + (line_num * 30))

        render_wrapped_text(input_text, left_panel, WHITE)
        render_wrapped_text(output_text, right_panel, TEXT_GREEN)

        draw_text("TYPE TO ENCRYPT • BACKSPACE TO CLEAR", FONT_MONO, TEXT_DIM, 40, 560)
        if clipboard_status:
            draw_text(clipboard_status, FONT_MONO, WHITE, WIDTH//2, 560, center=True)

        btn_paste = pygame.Rect(40, 480, 160, 40)
        p_hover = btn_paste.collidepoint(mx, my)
        pygame.draw.rect(screen, TEXT_GREEN if p_hover else TEXT_DIM, btn_paste, 2)
        draw_text("PASTE INPUT", FONT_MONO, WHITE, btn_paste.centerx, btn_paste.centery, center=True)
        
        if p_hover and click:
            try:
                clip_bytes = pygame.scrap.get(pygame.SCRAP_TEXT)
                if clip_bytes:
                    pasted = clip_bytes.decode('utf-8').strip('\x00')
                    for char in pasted.upper():
                        if char in ALLOWED_CHARS and len(input_text) < 400:
                            input_text += char
                            output_text += enigma.encrypt_char(char)
                    clipboard_status = "[ TEXT PASTED ]"
                    clipboard_timer = pygame.time.get_ticks()
            except Exception:
                clipboard_status = "[ PASTE FAILED ]"
                clipboard_timer = pygame.time.get_ticks()

        btn_copy = pygame.Rect(60 + panel_width, 480, 160, 40)
        c_hover = btn_copy.collidepoint(mx, my)
        pygame.draw.rect(screen, TEXT_GREEN if c_hover else TEXT_DIM, btn_copy, 2)
        draw_text("COPY OUTPUT", FONT_MONO, WHITE, btn_copy.centerx, btn_copy.centery, center=True)

        if c_hover and click:
            try:
                pygame.scrap.put(pygame.SCRAP_TEXT, output_text.encode('utf-8'))
                clipboard_status = "[ CIPHER COPIED ]"
                clipboard_timer = pygame.time.get_ticks()
            except Exception:
                clipboard_status = "[ COPY FAILED ]"
                clipboard_timer = pygame.time.get_ticks()

        btn_terminate = pygame.Rect(WIDTH - 180, 540, 140, 40)
        t_hover = btn_terminate.collidepoint(mx, my)
        t_color = ACCENT_RED if t_hover else (120, 30, 30)
        pygame.draw.rect(screen, t_color, btn_terminate)
        pygame.draw.rect(screen, WHITE, btn_terminate, 2)
        draw_text("TERMINATE", FONT_MONO, WHITE, btn_terminate.centerx, btn_terminate.centery, center=True)
        
        if t_hover and click:
            running = False 

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()