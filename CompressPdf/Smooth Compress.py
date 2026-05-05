import os
import sys
import random
import io
import customtkinter as ctk
from tkinter import filedialog
import fitz  # PyMuPDF
from PIL import Image


def resource_path(relative_path):
    """Get absolute path to resource, works for both development and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# ==========================================
# Configurações Globais de Tema
# ==========================================
ctk.set_appearance_mode("Light")  # Fundo claro baseado no mockup
ctk.set_default_color_theme("blue")

class AppCompressorPDF(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela Principal
        self.title("S.C Compressor PDF - Otimize seus arquivos com facilidade!")
        self.geometry("1200x650")
        self.iconbitmap(resource_path("assets/compressaopdf.ico")) # Ícone personalizado (opcional)
        self.configure(fg_color="#E5E5E5") # Fundo cinza claro atrás dos painéis
        self.minsize(900, 600)

        self.caminho_entrada = None

        self.nivel_compressao = 3   # Nível de compressão padrão seguro (garbage=3)
        self.nivel_reducao_img = 0  # Padrão: 0% de redução nas imagens

        # ==========================================
        # Layout Principal (Grid - 3 Colunas)
        # ==========================================
        self.grid_columnconfigure(0, weight=1) # Coluna Esquerda (Assets)
        self.grid_columnconfigure(1, weight=4) # Coluna Central (Principal)
        self.grid_columnconfigure(2, weight=1) # Coluna Direita (Prévia)
        self.grid_rowconfigure(0, weight=1)

        # ------------------------------------------
        # 1. PAINEL ESQUERDO (Assets & Botões de Apoio)
        # ------------------------------------------
        self.frame_esq = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.frame_esq.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

        # Container para a imagem aleatória
        self.img_label = ctk.CTkLabel(self.frame_esq, text="")
        self.img_label.pack(pady=20, padx=20, expand=True)
        self.carregar_imagem_aleatoria()

        img = ctk.CTkImage(light_image=Image.open(resource_path("assets/settings.png")), dark_image=Image.open(resource_path("assets/settings.png")), size=(20, 20))

        # Botão Configuração
        self.btn_config = ctk.CTkButton(
            self.frame_esq, text="Configuração",
            command=self.abrir_modal_configuracao,
            fg_color="#00C853", hover_color="#009624", corner_radius=20, text_color="black", font=ctk.CTkFont(weight="bold"), image=img
        )
        self.btn_config.pack(pady=(10, 10), padx=20, fill="x", side="bottom")

        img1 = ctk.CTkImage(light_image=Image.open(resource_path("assets/interrogation (1).png")), dark_image=Image.open(resource_path("assets/interrogation (1).png")), size=(20, 20))

        # Botão Ajuda
        self.btn_help = ctk.CTkButton(
            self.frame_esq, text="Help!", 
            command=self.abrir_modal_ajuda,
            fg_color="#00C853", hover_color="#009624",corner_radius=20, text_color="black", font=ctk.CTkFont(weight="bold"), image=img1
        )
        self.btn_help.pack(pady=(0, 5), padx=20, fill="x", side="bottom")

        # ------------------------------------------
        # 2. PAINEL CENTRAL (Ações Principais)
        # ------------------------------------------
        self.frame_centro = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.frame_centro.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")
        
        # Centralizando conteúdo no frame central
        self.frame_centro.grid_rowconfigure(0, weight=1)
        self.frame_centro.grid_rowconfigure(5, weight=1)
        self.frame_centro.grid_columnconfigure(0, weight=1)

        self.label_titulo = ctk.CTkLabel(
            self.frame_centro, text="Compressor PDF", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.label_titulo.grid(row=1, column=0, pady=(0, 20))

        self.label_aviso = ctk.CTkLabel(
            self.frame_centro, text="⚠ Aviso: Comprimir demais o PDF pode perder a assinatura!", 
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#32CD32" # Verde claro do mockup
        )
        self.label_aviso.grid(row=2, column=0, pady=(0, 20))

        self.btn_selecionar = ctk.CTkButton(
            self.frame_centro, text="Selecionar PDF", 
            command=self.selecionar_arquivo,
            fg_color="#4A4DFF", hover_color="#3235CC", # Azul do mockup
            width=250, height=50, corner_radius=25, font=ctk.CTkFont(weight="bold")
        )
        self.btn_selecionar.grid(row=3, column=0, pady=10)

        self.btn_comprimir = ctk.CTkButton(
            self.frame_centro, text="Comprimir PDF", 
            command=self.comprimir_pdf,
            fg_color="#00C853", hover_color="#009624", # Verde do mockup
            width=250, height=50, corner_radius=25, font=ctk.CTkFont(weight="bold"),
            text_color="white", state="disabled"
        )
        self.btn_comprimir.grid(row=4, column=0, pady=10)

        # Rótulo de Status
        self.label_status = ctk.CTkLabel(self.frame_centro, text="", font=ctk.CTkFont(size=14))
        self.label_status.grid(row=5, column=0, pady=10, sticky="n")

        self.label_rodape = ctk.CTkLabel(
            self.frame_centro, text="V 3.0.0 - Copyright AMSL",
            font=ctk.CTkFont(size=10), text_color="darkgray"
        )
        self.label_rodape.grid(row=6, column=0, pady=(0, 20), sticky="s")

        # ------------------------------------------
        # 3. PAINEL DIREITO (Prévia)
        # ------------------------------------------
        self.frame_dir = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.frame_dir.grid(row=0, column=2, padx=(10, 20), pady=20, sticky="nsew")

        self.label_preview_titulo = ctk.CTkLabel(
            self.frame_dir, text="Prévia de capa:", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.label_preview_titulo.pack(pady=(40, 20))

        self.canvas_preview = ctk.CTkLabel(
            self.frame_dir, text="Sem PDF:", text_color="black", font=ctk.CTkFont(weight="bold"),
            width=220, height=320, fg_color="#D9D9D9", corner_radius=20 # Fundo cinza do mockup
        )
        self.canvas_preview.pack(pady=10, padx=20, expand=True)

        # Abre o modal de ajuda logo que o app inicia (opcional)
        # self.after(500, self.abrir_modal_ajuda)

    # ==========================================
    # Funções Lógicas
    # ==========================================

    def carregar_imagem_aleatoria(self):
        """Busca uma imagem aleatória na pasta 'assets' e exibe no painel esquerdo."""
        pasta_assets = resource_path("assets/layerleft")
        imagem_carregada = False

        if os.path.exists(pasta_assets):
            arquivos = [f for f in os.listdir(pasta_assets) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if arquivos:
                imagem_escolhida = random.choice(arquivos)
                caminho_img = os.path.join(pasta_assets, imagem_escolhida)
                try:
                    img = Image.open(caminho_img)
                    img.thumbnail((220, 300)) # Redimensiona mantendo proporção
                    ctk_img = ctk.CTkImage(light_image=img, size=img.size)
                    self.img_label.configure(image=ctk_img)
                    imagem_carregada = True
                except Exception as e:
                    print(f"Erro ao carregar imagem {imagem_escolhida}: {e}")
        
        # Se não encontrou imagens, gera um placeholder cinza para não quebrar a UI
        if not imagem_carregada:
            img_placeholder = Image.new("RGB", (200, 250), color="#e0e0e0")
            ctk_img = ctk.CTkImage(light_image=img_placeholder, size=img_placeholder.size)
            self.img_label.configure(image=ctk_img, text="Sem Assets", text_color="gray")


    def atualizar_nivel_compressao(self, valor):
        """Atualiza a variável global de compressão e o texto no modal."""
        # O slider retorna float, precisamos converter para int
        self.nivel_compressao = int(valor)
        
        # Se o label do modal estiver aberto, atualiza o texto dele
        if hasattr(self, 'label_valor_atual') and self.label_valor_atual.winfo_exists():
            self.label_valor_atual.configure(text=f"Nível de Compressão: {self.nivel_compressao}")
    
    def atualizar_reducao_img(self, valor):
        self.nivel_reducao_img = int(valor)
        if hasattr(self, 'label_reducao_atual') and self.label_reducao_atual.winfo_exists():
            self.label_reducao_atual.configure(text=f"Redução atual: {self.nivel_reducao_img}%")
    
    def abrir_modal_configuracao(self):
        """Abre um modal para configurar o nível de compressão."""
        modal = ctk.CTkToplevel(self)
        modal.title("Configurações Avançadas")
        modal.geometry("400x480") 
        modal.resizable(False, False)

        modal.after(200, lambda: modal.iconbitmap(resource_path("assets/compressaopdf.ico")))

        modal.grab_set() 
        modal.focus()

        frame_modal = ctk.CTkFrame(modal, fg_color="white")
        frame_modal.pack(fill="both", expand=True, padx=20, pady=20)

        # --- 1. Slider de Remoção de Dados (Garbage) ---
        ctk.CTkLabel(frame_modal, text="Limpeza de Dados Ocultos", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 0))
        self.label_valor_atual = ctk.CTkLabel(frame_modal, text=f"Nível de Limpeza: {self.nivel_compressao}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4A4DFF")
        self.label_valor_atual.pack(pady=5)
        
        slider_garbage = ctk.CTkSlider(frame_modal, from_=0, to=4, number_of_steps=4, command=self.atualizar_nivel_compressao)
        slider_garbage.set(self.nivel_compressao)
        slider_garbage.pack(pady=5)
        ctk.CTkLabel(frame_modal, text="0 = Mais rápido | 4 = Menor arquivo", font=ctk.CTkFont(size=10), text_color="gray").pack()

        # Separador visual
        ctk.CTkFrame(frame_modal, height=2, fg_color="#E5E5E5").pack(fill="x", pady=15, padx=20)

        # --- 2. Slider de Redução de Imagens (DPI) ---
        ctk.CTkLabel(frame_modal, text="Redução de Imagens (DPI)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 0))
        self.label_reducao_atual = ctk.CTkLabel(frame_modal, text=f"Redução atual: {self.nivel_reducao_img}%", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00C853")
        self.label_reducao_atual.pack()
        
        slider_img = ctk.CTkSlider(frame_modal, from_=0, to=100, number_of_steps=10, command=self.atualizar_reducao_img, fg_color="#D9D9D9", progress_color="#00C853", button_color="#009624", button_hover_color="#007A1C")
        slider_img.set(self.nivel_reducao_img)
        slider_img.pack(pady=5)
        ctk.CTkLabel(frame_modal, text="0% = Manter Original | 100% = Redução Máxima", font=ctk.CTkFont(size=10), text_color="gray").pack()

        btn_fechar = ctk.CTkButton(frame_modal, text="Salvar e Fechar", command=modal.destroy, corner_radius=15, fg_color="#00C853", hover_color="#009624")
        btn_fechar.pack(pady=(20, 10))

    def abrir_modal_ajuda(self):
        """Abre uma nova janela por cima da principal com instruções de uso."""
        modal = ctk.CTkToplevel(self)
        modal.title("Guia de Uso")
        modal.geometry("500x500")
        modal.resizable(False, False)

        modal.after(200, lambda: modal.iconbitmap(resource_path("assets/compressaopdf.ico")))
        
        # Faz a janela principal ficar "travada" enquanto o modal estiver aberto
        modal.grab_set() 
        modal.focus()

        # Fundo do modal
        frame_modal = ctk.CTkFrame(modal, fg_color="white")
        frame_modal.pack(fill="both", expand=True, padx=20, pady=20)

        titulo = ctk.CTkLabel(frame_modal, text="Guia de Uso do Compressor PDF", font=ctk.CTkFont(size=20, weight="bold"))
        titulo.pack(pady=(20, 10))

        instrucoes = (
            "Bem-vindo ao Compressor PDF!\n\n"
            "Como Usar:\n"
            "1. Selecionar PDF: Clique no botão azul para escolher seu arquivo.\n"
            "2. Configuração: Ajuste a força da compressão.\n"
            "3. Comprimir PDF: Clique no botão verde para otimizar.\n"
            "4. Salvar: Escolha onde salvar o novo arquivo.\n\n"
            "⚠ Dica: Arquivos assinados digitalmente podem ser invalidados\nse comprimidos agressivamente.\n\n\n"
            "Esperamos que esta ferramenta seja útil para você!\n - AMSL 🚀"
        )

        texto_instrucoes = ctk.CTkLabel(frame_modal, text=instrucoes, justify="left", font=ctk.CTkFont(size=14, weight="bold"), text_color="#32CD32")
        texto_instrucoes.pack(pady=10, padx=20)

        btn_fechar = ctk.CTkButton(frame_modal, text="Fechar", command=modal.destroy, corner_radius=15, fg_color="#4A4DFF")
        btn_fechar.pack(pady=(20, 20), side="bottom")

    def gerar_preview(self, caminho):
        """Gera a miniatura da capa do PDF."""
        try:
            doc = fitz.open(caminho)
            pagina = doc.load_page(0)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(0.4, 0.4))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((200, 280))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.canvas_preview.configure(image=ctk_img, text="")
            doc.close()
        except Exception:
            self.canvas_preview.configure(text="Erro na Prévia")

    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
        if caminho:
            self.caminho_entrada = caminho
            self.btn_comprimir.configure(state="normal")
            self.label_status.configure(text=f"Pronto para comprimir: {os.path.basename(caminho)}", text_color="gray")
            self.gerar_preview(caminho)

    def processar_imagens_pdf(self, doc):
        """Busca todas as imagens do PDF e reduz a resolução/DPI delas baseado no Slider."""
        if self.nivel_reducao_img <= 0:
            return # Se estiver em 0%, ignora esse processo

        # Calcula a escala: Se for 50%, escala é 0.5. Se for 90%, escala é 0.1
        escala = 1.0 - (self.nivel_reducao_img / 100.0)
        if escala < 0.1: escala = 0.1 
            
        xrefs_processados = set() 
        
        for pagina in doc:
            for img_info in pagina.get_images(full=True):
                xref = img_info[0]
                if xref in xrefs_processados: continue
                xrefs_processados.add(xref)
                
                try:
                    pix = fitz.Pixmap(doc, xref)
                    has_alpha = pix.alpha
                    
                    if pix.n >= 4 and not has_alpha: 
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    modo_img = "RGBA" if has_alpha else ("L" if pix.n == 1 else "RGB")
                    img_pil = Image.frombytes(modo_img, [pix.width, pix.height], pix.samples)
                    
                    nova_largura = int(pix.width * escala)
                    nova_altura = int(pix.height * escala)
                    
                    if nova_largura < 10 or nova_altura < 10: continue 
                        
                    img_pil = img_pil.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                    img_byte_arr = io.BytesIO()
                    
                    if has_alpha:
                        img_pil.save(img_byte_arr, format='PNG', optimize=True)
                        doc.xref_set_key(xref, "Filter", "/FlateDecode")
                    else:
                        img_pil.save(img_byte_arr, format='JPEG', quality=75)
                        doc.xref_set_key(xref, "Filter", "/DCTDecode")
                        doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")

                    doc.xref_set_key(xref, "Width", str(nova_largura))
                    doc.xref_set_key(xref, "Height", str(nova_altura))
                    doc.update_stream(xref, img_byte_arr.getvalue())
                    
                except Exception as e:
                    print(f"Aviso: Não foi possível otimizar a imagem {xref} - Erro: {e}")
                    continue

    def comprimir_pdf(self):
        if not self.caminho_entrada: return
        
        caminho_saida = filedialog.asksaveasfilename(
            initialfile=f"otimizado_{os.path.basename(self.caminho_entrada)}",
            defaultextension=".pdf", filetypes=[("Arquivos PDF", "*.pdf")]
        )

        if not caminho_saida: return

        self.label_status.configure(text="Comprimindo, aguarde...", text_color="#4A4DFF")
        self.update()

        try:
            doc = fitz.open(self.caminho_entrada)
            # --Eliminação de Metadados Ocultos (Redundâncias)--
            doc.set_metadata({})

            # -- Otimização Profunda de DPI (Imagens) --
            self.processar_imagens_pdf(doc)

            doc.save(caminho_saida,
                    garbage=int(self.nivel_compressao), # Usa o nível de compressão escolhido
                    deflate=True,
                    clean=True)
            doc.close()
            self.label_status.configure(text="✅ Sucesso! Arquivo comprimido salvo.", text_color="#00C853")
        except Exception as e:
            self.label_status.configure(text=f"❌ Erro: {str(e)}", text_color="red")

if __name__ == "__main__":
    app = AppCompressorPDF()
    app.mainloop()