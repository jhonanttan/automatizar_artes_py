from flask import Flask, render_template, request, send_file, url_for
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

def criar_arte(trajeto, tipo_voo, ida, volta, preco, preco_cartao):
    try:
        # Escolher a base de arte com base no trajeto e tipo de voo
        if trajeto == "sp_jeri":
            caminho_base = os.path.join(app.static_folder, "sp_jeri_ida.png" if tipo_voo == "ida" else "sp_jeri_ida_e_volta.png")
        elif trajeto == "jeri_sp":
            caminho_base = os.path.join(app.static_folder, "jeri_sp_ida.png" if tipo_voo == "ida" else "jeri_sp_ida_e_volta.png")
        elif trajeto == "for_sp":
            caminho_base = os.path.join(app.static_folder, "for_sp_ida.png" if tipo_voo == "ida" else "for_sp_ida_e_volta.png")
        elif trajeto == "sp_for":
            caminho_base = os.path.join(app.static_folder, "sp_for_ida.png" if tipo_voo == "ida" else "sp_for_ida_e_volta.png")
        else:
            raise ValueError("Trajeto inválido")

        if not os.path.exists(caminho_base):
            raise FileNotFoundError(f"{caminho_base} não encontrado")

        imagem = Image.open(caminho_base)
        draw = ImageDraw.Draw(imagem)

        # Fontes - Usando caminho absoluto
        caminho_fonte_medium = os.path.join(app.static_folder, "Poppins-Medium.ttf")
        caminho_fonte_extra_bold = os.path.join(app.static_folder, "Poppins-ExtraBold.ttf")

        if not os.path.exists(caminho_fonte_medium):
            raise FileNotFoundError("Fonte Poppins-Medium.ttf não encontrada")
        if not os.path.exists(caminho_fonte_extra_bold):
            raise FileNotFoundError("Fonte Poppins-ExtraBold.ttf não encontrada")

        fonte_57 = ImageFont.truetype(caminho_fonte_medium, 57)
        fonte_extra_bold_128 = ImageFont.truetype(caminho_fonte_extra_bold, 128)

        largura_maxima = 2000 - 810 - 113
        altura_maxima_ida = 336
        espacamento_linhas = 10

        def quebrar_texto(texto, fonte, largura_maxima):
            palavras = texto.split()
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                if draw.textbbox((0, 0), f"{linha_atual} {palavra}", font=fonte)[2] <= largura_maxima:
                    linha_atual += f" {palavra}"
                else:
                    linhas.append(linha_atual.strip())
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual.strip())
            return linhas

        def renderizar_texto_multilinha(texto, pos_x, pos_y, fonte, largura_maxima, altura_maxima):
            linhas = quebrar_texto(texto, fonte, largura_maxima)
            y_atual = pos_y
            for linha in linhas:
                if y_atual + fonte.size > pos_y + altura_maxima:
                    break
                draw.text((pos_x, y_atual), linha, fill="black", font=fonte, anchor="lt")
                y_atual += fonte.size + espacamento_linhas

        # Formatação de preços
        preco_formatado = f"{int(preco):,}".replace(",", ".") + ",00"
        preco_cartao_formatado = f"R${int(preco_cartao):,}".replace(",", ".") + ",00 no cartão em até 3x sem juros"

        # Renderizando textos
        renderizar_texto_multilinha(ida, 810, 708 if tipo_voo == "ida_volta" else 879, fonte_57, largura_maxima, altura_maxima_ida)
        if tipo_voo == "ida_volta":
            renderizar_texto_multilinha(volta, 810, 1217, fonte_57, largura_maxima, altura_maxima_ida)

        # Preço à vista (fonte e cor específicas)
        draw.text((850, 1700), preco_formatado, fill="#FF7303", font=fonte_extra_bold_128, anchor="lt")
        # Preço no cartão
        draw.text((800, 1869), preco_cartao_formatado, fill="black", font=fonte_57, anchor="lt")

        # Salvando a imagem final
        nome_arquivo_saida = os.path.join(app.static_folder, "arte_promocao.png")
        imagem.save(nome_arquivo_saida)
        return nome_arquivo_saida
    except Exception as e:
        return str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        trajeto = request.form.get("trajeto")
        tipo_voo = request.form.get("tipo_voo")
        ida = request.form.get("ida")
        volta = request.form.get("volta", "") if tipo_voo == "ida_volta" else None
        preco = request.form.get("preco")
        preco_cartao = request.form.get("preco_cartao")
        caminho_arte = criar_arte(trajeto, tipo_voo, ida, volta, preco, preco_cartao)
        if caminho_arte.endswith(".png"):
            return send_file(caminho_arte, as_attachment=True)
        return f"Erro ao criar a arte: {caminho_arte}"
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
