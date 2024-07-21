import pygame as pg
import sys
import logging
import pyperclip

logging.basicConfig(filename='game.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
        
    def __truediv__(self, scalar):
        if scalar == 0:
            raise ValueError("Não é possível dividir por zero.")
        return Vector2D(self.x / scalar, self.y / scalar)

    def to_tuple(self):
        return (self.x, self.y)

class GameEngine:
    def __init__(self, gravidade, bola):
        self.__gravidade = gravidade
        self.bola = bola
        
    def apply_impulse(self, obj, vector_x, vector_y):
        adjusted_impulse = Vector2D(vector_x / obj['massa'], vector_y / obj['massa'])

        obj['velocidade'] = (obj['velocidade'][0] + adjusted_impulse.x, obj['velocidade'][1] + adjusted_impulse.y)
        self.__log_info(f"Impulso aplicado: {adjusted_impulse.x}, {adjusted_impulse.y}")


    def __update_velocity(self, obj, impulse):

        obj['velocidade'] = (obj['velocidade'][0] + impulse.x, obj['velocidade'][1] + impulse.y)
        self.__log_info(f"Impulso aplicado: {impulse.x}, {impulse.y}")

    def __log_info(self, message):

        print(message)

    @property
    def gravidade(self):

        return self.__gravidade

    @gravidade.setter
    def gravidade(self, value):
        if value > 0:
            self.__gravidade = value
        else:
            print("Gravidade deve ser positiva.")

    def get_posicao_bola(self):
        return self.bola['posicao']

    def execute_complex_command(self, obj, command):
        local_scope = {'Vector2D': Vector2D, 'game': self, 'obj': obj}


        try:
            exec(command, {}, local_scope)
            logging.info(f"Comando executado com sucesso: {command}")
        except Exception as e:  
            logging.warning(f"Erro ao executar o comando: {e}")
            print(f"Erro ao executar o comando: {e}")

def update_object(obj, gravidade, tela_largura, tela_altura, raio, atrito):
    x, y = obj['posicao']
    vx, vy = obj['velocidade']
    
    vy += gravidade

    if y + raio >= tela_altura:
        vx *= atrito

    x += vx
    y += vy

    if x - raio < 0 or x + raio > tela_largura:
        vx *= -1
        x = raio if x - raio < 0 else tela_largura - raio

    if y - raio < 0 or y + raio > tela_altura:
        vy *= -0.9 
        y = raio if y - raio < 0 else tela_altura - raio

    obj['posicao'] = (x, y)
    obj['velocidade'] = (vx, vy)


def main():
    pg.init()
    tela_largura, tela_altura = 1208, 700
    tela = pg.display.set_mode((tela_largura, tela_altura))
    preto, branco = pg.Color('black'), pg.Color('white')
    running = True
    gravidade = 1.5
    obj = {
        'posicao': (tela_largura / 2, tela_altura / 2),
        'velocidade': (0, 0),
        'massa': 1,
        'magnitude': 0
    }
    engine = GameEngine(gravidade, obj)
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()
    input_box = pg.Rect(100, 100, 140, 32)
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    txt_surface = font.render(text, True, color)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive

            
            if event.type == pg.KEYDOWN and active:
                if event.key == pg.K_RETURN:

                    logging.info(text)
                    engine.execute_complex_command(obj, text)
                    text = ''
                elif event.key == pg.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
                
                if event.key == pg.K_c and (pg.key.get_mods() & pg.KMOD_CTRL):
                    pyperclip.copy(text)
                    print("Texto copiado para o clipboard.")
 
                elif event.key == pg.K_v and (pg.key.get_mods() & pg.KMOD_CTRL):
                    text = pyperclip.paste()
                    txt_surface = font.render(text, True, color)
                    print("Texto colado do clipboard.")
                txt_surface = font.render(text, True, color)
                

        tela.fill((30, 30, 30))
        pg.draw.rect(tela, color, input_box, 2)
        input_box.w = max(200, txt_surface.get_width() + 10)
        tela.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        update_object(obj, gravidade, tela_largura, tela_altura, 20, 0.99)
        pg.draw.circle(tela, branco, (int(obj['posicao'][0]), int(obj['posicao'][1])), 20)
        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
    pg.quit()