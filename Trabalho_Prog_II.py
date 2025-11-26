import pygame
import sys
from fases import FASES_MATRIZ

'''Inicializa o Pygame'''
pygame.init()

'''Configurações da matriz/grid'''
TAMANHO_QUADRADO = 70
LINHAS = 10
COLUNAS = 10
LARGURA = COLUNAS * TAMANHO_QUADRADO
ALTURA = LINHAS * TAMANHO_QUADRADO

# Cores
CINZA_E = ('#A9A9A9')
PRETO = ('#000000')
AZUL = ('#0000FF')
VERMELHO = ('#FF0000')
VERDE = ('#13AF24')
AMARELO = ('#FFFF00')
ROXO = ('#800080')              

# Inicializa a tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Empurrar Objetos - Célula Alvo")

# Carrega as imagens
try:
    sprite_img = pygame.image.load("pim.png").convert_alpha()
    sprite_img = pygame.transform.scale(sprite_img, (TAMANHO_QUADRADO, TAMANHO_QUADRADO))
except:
    print("Erro ao carregar a imagem do sprite")
    sprite_img = pygame.Surface((TAMANHO_QUADRADO,TAMANHO_QUADRADO))
    sprite_img.fill(AZUL)

try:
    obstaculo_img = pygame.image.load("caixa.png").convert_alpha()
    obstaculo_img = pygame.transform.scale(obstaculo_img, (TAMANHO_QUADRADO,TAMANHO_QUADRADO))
except:
    print("Criando obstáculo padrão")
    obstaculo_img = pygame.Surface((TAMANHO_QUADRADO,TAMANHO_QUADRADO))
    obstaculo_img.fill(VERMELHO)
    
try:
    parede_img = pygame.image.load("muro.png").convert_alpha()
    parede_img = pygame.transform.scale(parede_img, (TAMANHO_QUADRADO,TAMANHO_QUADRADO))
except:
    print("Criando obstáculo padrão")
    parede_img = pygame.Surface((TAMANHO_QUADRADO,TAMANHO_QUADRADO))
    parede_img.fill(PRETO)
    

# --- Definições de Classes (Sprite, ObjetoMovel, CelulaAlvo) ---

class Sprite(pygame.sprite.Sprite):
    """
    Representa o personagem controlável pelo jogador.
    É uma subclasse de pygame.sprite.Sprite para facilitar o desenho e gerenciamento.
    """
    def __init__(self, x, y):
        """
        Inicializa o sprite na posição da matriz (x, y).
        :param x: Posição inicial da coluna (eixo X) na matriz.
        :param y: Posição inicial da linha (eixo Y) na matriz.
        """
        super().__init__()
        self.image = sprite_img
        self.rect = self.image.get_rect()
        self.posicao_matriz = [x, y]  # Posição na grade (coluna, linha)
        self.atualizar_posicao_pixel()

    def atualizar_posicao_pixel(self):
        """
        Converte a posição da matriz (grid) para a posição real em pixels na tela,
        e atualiza o retângulo de colisão (self.rect).
        """
        self.rect.x = self.posicao_matriz[0] * TAMANHO_QUADRADO
        self.rect.y = self.posicao_matriz[1] * TAMANHO_QUADRADO

    def encontrar_objeto_na_posicao(self, x, y, objetos):
        """
        Verifica se existe um objeto (móvel ou imóvel) na posição (x, y) da matriz.
        :param x: Coluna da matriz a verificar.
        :param y: Linha da matriz a verificar.
        :param objetos: Lista de objetos (sprites) a serem procurados.
        :return: O objeto encontrado ou None se a posição estiver vazia.
        """
        for obj in objetos:
            if obj.posicao_matriz[0] == x and obj.posicao_matriz[1] == y:
                return obj
        return None

    def mover(self, dx, dy, objetos_moveis, objetos_imoveis, celula_alvo): # Adiciona objetos_imoveis
        """
        Move o sprite para uma nova posição (baseada em dx, dy),
        lidando com colisões e a lógica de empurrar objetos móveis.

        :param dx: Mudança na coordenada X (e.g., -1 para Esquerda, 1 para Direita).
        :param dy: Mudança na coordenada Y (e.g., -1 para Cima, 1 para Baixo).
        :param objetos_moveis: Lista de objetos que podem ser empurrados (Caixas).
        :param objetos_imoveis: Lista de objetos que bloqueiam o movimento (Paredes).
        :param celula_alvo: A célula de destino para verificar a vitória.
        """
        nova_x = self.posicao_matriz[0] + dx
        nova_y = self.posicao_matriz[1] + dy
        
        # 1. VERIFICAÇÃO DE LIMITE E OBSTÁCULOS IMÓVEIS
        if 0 <= nova_x < COLUNAS and 0 <= nova_y < LINHAS:
            
            # CHAVE: Verifica se a nova posição está ocupada por um obstáculo imóvel
            obstaculo_na_nova_posicao = self.encontrar_objeto_na_posicao(nova_x, nova_y, objetos_imoveis)
            if obstaculo_na_nova_posicao:
                return # Sai da função, impedindo o movimento
            
            # 2. LÓGICA DE EMPURRAR
            objeto_alvo = self.encontrar_objeto_na_posicao(nova_x, nova_y, objetos_moveis)
            
            if objeto_alvo:
                objeto_nova_x = objeto_alvo.posicao_matriz[0] + dx
                objeto_nova_y = objeto_alvo.posicao_matriz[1] + dy
                
                # CHAVE: Verifica se o objeto empurrado colide com um obstáculo imóvel
                obstaculo_na_posicao_empurrada = self.encontrar_objeto_na_posicao(objeto_nova_x, objeto_nova_y, objetos_imoveis)
                
                # Verifica se a nova posição do objeto empurrado é válida (dentro do limite E sem obstáculo imóvel)
                if (0 <= objeto_nova_x < COLUNAS and 0 <= objeto_nova_y < LINHAS and 
                    not self.encontrar_objeto_na_posicao(objeto_nova_x, objeto_nova_y, objetos_moveis) and
                    not obstaculo_na_posicao_empurrada): # Impede que a caixa entre no obstáculo
                    
                    # Move o objeto
                    objeto_alvo.posicao_matriz[0] = objeto_nova_x
                    objeto_alvo.posicao_matriz[1] = objeto_nova_y
                    objeto_alvo.atualizar_posicao_pixel()
                    
                    # Move o personagem
                    self.posicao_matriz[0] = nova_x
                    self.posicao_matriz[1] = nova_y
                    self.atualizar_posicao_pixel()
                    
                    celula_alvo.verificar_vitoria(objetos_moveis)
            else:
                # Movimento normal sem objetos
                self.posicao_matriz[0] = nova_x
                self.posicao_matriz[1] = nova_y
                self.atualizar_posicao_pixel()

class ObjetoMovel(pygame.sprite.Sprite):
    """
    Representa os objetos que podem ser empurrados pelo Sprite (as caixas).
    Subclasse de pygame.sprite.Sprite.
    """
    def __init__(self, x, y):
        """
        Inicializa o objeto móvel na posição da matriz (x, y).
        """
        super().__init__()
        self.image = obstaculo_img
        self.rect = self.image.get_rect()
        self.posicao_matriz = [x, y]
        self.atualizar_posicao_pixel()

    def atualizar_posicao_pixel(self):
        """
        Converte a posição da matriz para pixels e atualiza self.rect.
        """
        self.rect.x = self.posicao_matriz[0] * TAMANHO_QUADRADO
        self.rect.y = self.posicao_matriz[1] * TAMANHO_QUADRADO

class CelulaAlvo:
    """
    Representa a célula de destino (target) onde o objeto móvel deve ser empurrado.
    Não é um sprite, mas desenha-se na tela.
    """
    def __init__(self, x, y):
        """
        Inicializa a célula alvo na posição da matriz (x, y).
        """
        self.posicao_matriz = [x, y]
        # Cria um retângulo para a posição de desenho e verificação de colisão
        self.rect = pygame.Rect(x * TAMANHO_QUADRADO, y * TAMANHO_QUADRADO,TAMANHO_QUADRADO,TAMANHO_QUADRADO)
        self.vitoria_alcancada = False
        self.cor_normal = ROXO
        self.cor_vitoria = VERDE

    def desenhar(self, tela):
        """
        Desenha a célula alvo na tela, mudando a cor se a vitória tiver sido alcançada.
        :param tela: A superfície de desenho do Pygame.
        """
        cor = self.cor_vitoria if self.vitoria_alcancada else self.cor_normal
        pygame.draw.rect(tela, cor, self.rect)
        pygame.draw.rect(tela, PRETO, self.rect, 1)

    def verificar_vitoria(self, objetos):
        """
        Verifica se pelo menos um ObjetoMovel (caixa) está na mesma posição da matriz
        que esta CelulaAlvo.
        :param objetos: Lista de ObjetoMovel (caixas) a verificar.
        """

        vitoria = False
        for obj in objetos:
            if (obj.posicao_matriz[0] == self.posicao_matriz[0] and 
                obj.posicao_matriz[1] == self.posicao_matriz[1]):
                vitoria = True
                break
    
        if vitoria and not self.vitoria_alcancada:
            
            self.vitoria_alcancada = True
            
        elif not vitoria:
            self.vitoria_alcancada = False


class ObstaculoImovel(pygame.sprite.Sprite):
    """
    Representa obstáculos que bloqueiam o movimento e não podem ser movidos
    (e.g., paredes ou muros). Subclasse de pygame.sprite.Sprite.
    """
    def __init__(self, x, y):
        """
        Inicializa o obstáculo imóvel na posição da matriz (x, y).
        """
        super().__init__()
        self.image = parede_img
        self.rect = self.image.get_rect()
        self.posicao_matriz = [x, y]
        self.atualizar_posicao_pixel()
        
    def atualizar_posicao_pixel(self):
        """Atualiza a posição em pixels com base na posição da matriz."""
        self.rect.x = self.posicao_matriz[0] * TAMANHO_QUADRADO
        self.rect.y = self.posicao_matriz[1] * TAMANHO_QUADRADO



# --- Sistema de Fases ---

fase_atual = 0

# Cria os objetos globalmente
sprite = Sprite(0, 0)
objetos_moveis = []  # Lista vazia inicial 
celula_alvo = CelulaAlvo(0, 0)
objetos_imoveis = []

# Grupos de sprites
todos_sprites = pygame.sprite.Group()
todos_sprites.add(sprite)


def carregar_fase(indice_fase):
    """
    Carrega o layout de um novo nível (fase) a partir da FASES_MATRIZ.
    Redefine as posições do Personagem (Sprite), Caixas (ObjetoMovel) e Alvo (CelulaAlvo).

    :param indice_fase: O índice (número) da fase na lista FASES_MATRIZ para carregar.
    :return: True se a fase foi carregada com sucesso, False se for o fim do jogo ou erro.
    """
    global fase_atual, objetos_imoveis, objetos_moveis
    
    if indice_fase >= len(FASES_MATRIZ):
        
        return False
        
    fase_matriz = FASES_MATRIZ[indice_fase]
    fase_atual = indice_fase
    print(f"--- Carregando Fase {fase_atual + 1} ---")
    
    # Listas para coletar as posições
    sprite_pos = None
    objetos_pos = []  # Para múltiplas caixas
    alvo_pos = None
    obstaculos_pos = []
    
    # Percorre a matriz para encontrar todos os elementos
    for y, linha in enumerate(fase_matriz):
        for x, simbolo in enumerate(linha):
            if simbolo == 'P':  # Personagem
                sprite_pos = [x, y]
            elif simbolo == 'C':  # Caixa
                objetos_pos.append([x, y])
            elif simbolo == 'A':  # Alvo
                alvo_pos = [x, y]
            elif simbolo == '#':  # Obstáculo
                obstaculos_pos.append([x, y])
    
    # Verifica se encontrou todos os elementos essenciais
    if sprite_pos is None:
        print("ERRO: Personagem não encontrado na fase!")
        return False
    if not objetos_pos:
        print("ERRO: Nenhuma caixa encontrada na fase!")
        return False
    if alvo_pos is None:
        print("ERRO: Alvo não encontrado na fase!")
        return False
    
    # 1. Atualiza o sprite
    sprite.posicao_matriz = sprite_pos
    sprite.atualizar_posicao_pixel()
    
    # 2. Limpa e recria objetos móveis (caixas)
    # Remove caixas antigas do grupo de sprites
    for obj in objetos_moveis:
        todos_sprites.remove(obj)
    objetos_moveis.clear()
    
    # Cria novas caixas
    for pos in objetos_pos:
        nova_caixa = ObjetoMovel(pos[0], pos[1])
        objetos_moveis.append(nova_caixa)
        todos_sprites.add(nova_caixa)
    
    # 3. Limpa e recria obstáculos imóveis
    objetos_imoveis.clear()
    # Remove obstáculos antigos do grupo de sprites
    for sprite_obj in todos_sprites:
        if isinstance(sprite_obj, ObstaculoImovel):
            todos_sprites.remove(sprite_obj)
    
    for pos in obstaculos_pos:
        novo_obstaculo = ObstaculoImovel(pos[0], pos[1])
        objetos_imoveis.append(novo_obstaculo)
        todos_sprites.add(novo_obstaculo)
    
    # 4. Atualiza a célula alvo
    celula_alvo.posicao_matriz = alvo_pos
    celula_alvo.rect.x = alvo_pos[0] * TAMANHO_QUADRADO
    celula_alvo.rect.y = alvo_pos[1] * TAMANHO_QUADRADO
    celula_alvo.vitoria_alcancada = False
    
    return True


def avancar_fase():
    """
    Função wrapper que tenta carregar a próxima fase após a vitória ser alcançada.
    Se não houver mais fases, define 'executando' como False para encerrar o jogo.
    """
    global executando, fase_atual
    proxima_fase = fase_atual + 1
    
    if not carregar_fase(proxima_fase):
        executando = False # Não há mais fases, encerra o jogo

# Carrega a fase inicial
if not carregar_fase(fase_atual):
    executando = False # Caso o dados_fases esteja vazio

# Loop principal
relogio = pygame.time.Clock()
executando = True
vitoria_exibida_tempo = 0 # Para controlar o tempo de exibição da vitória

while executando:
    """
    Processa o movimento do Sprite (jogador) com as teclas de seta.
    Chama o método sprite.mover() com os deslocamentos (dx, dy)
    e passando as listas de objetos para a lógica de colisão e empurrão.
    Também permite resetar a fase com a tecla 'R'.
    """
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        
        # O movimento só ocorre se a vitória ainda não foi alcançada
        elif evento.type == pygame.KEYDOWN and not celula_alvo.vitoria_alcancada:
            if evento.key == pygame.K_UP:
                sprite.mover(0, -1, objetos_moveis, objetos_imoveis, celula_alvo) 
            elif evento.key == pygame.K_DOWN:
                sprite.mover(0, 1, objetos_moveis, objetos_imoveis, celula_alvo) 
            elif evento.key == pygame.K_LEFT:
                sprite.mover(-1, 0, objetos_moveis, objetos_imoveis, celula_alvo) 
            elif evento.key == pygame.K_RIGHT:
                sprite.mover(1, 0, objetos_moveis, objetos_imoveis, celula_alvo) 
            elif evento.key == pygame.K_r:  # Reset para a fase atual
                carregar_fase(fase_atual)
    
    # --- Lógica de Mudança de Fase ---
    if celula_alvo.vitoria_alcancada:
        """
        Verifica se a condição de vitória foi atingida.
        Se sim, inicia uma contagem (1.5 segundos) para chamar avancar_fase().
        Isso dá um breve momento para o jogador ver a mensagem de vitória.
        """
        if vitoria_exibida_tempo == 0:
            vitoria_exibida_tempo = pygame.time.get_ticks()

        # Espera 1.5 segundos antes de avançar para a próxima fase
        if pygame.time.get_ticks() - vitoria_exibida_tempo > 1500:
            avancar_fase()
            vitoria_exibida_tempo = 0 # Reseta para a próxima verificação
            
    # Desenha a grade
    tela.fill(CINZA_E)
    for x in range(0, LARGURA, TAMANHO_QUADRADO):
        pygame.draw.line(tela, PRETO, (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, TAMANHO_QUADRADO):
        pygame.draw.line(tela, PRETO, (0, y), (LARGURA, y))

    # Desenha a célula alvo primeiro
    celula_alvo.desenhar(tela)

    # Desenha todos os sprites
    todos_sprites.draw(tela)

    # Exibe informações e mensagens
    fonte = pygame.font.SysFont(None, 24)
    texto_fase = fonte.render(f"Fase: {fase_atual + 1}/{len(FASES_MATRIZ)}", True, PRETO)
    tela.blit(texto_fase, (LARGURA - 100, 10))
    
    if celula_alvo.vitoria_alcancada:
        texto_vitoria = fonte.render(" ( 0o0) VITÓRIA ALCANÇADA! (0o0 ) ", True, VERDE)
        tela.blit(texto_vitoria, (LARGURA // 2 - texto_vitoria.get_width() // 2, 10))
    
    texto_controles = fonte.render("R = Reset", True, PRETO)
    tela.blit(texto_controles, (10, ALTURA - 30))

    pygame.display.flip()
    relogio.tick(60)

# Mensagem de encerramento do jogo, caso o loop tenha terminado
if fase_atual + 1 >= len(FASES_MATRIZ) and not executando:
    tela.fill(PRETO)
    fonte_final = pygame.font.SysFont(None, 48)
    texto_fim = fonte_final.render("FIM DO JOGO!", True, AMARELO)
    tela.blit(texto_fim, (LARGURA // 2 - texto_fim.get_width() // 2, ALTURA // 2 - texto_fim.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(4000) # Espera 4 segundos antes de fechar

pygame.quit()
sys.exit()


