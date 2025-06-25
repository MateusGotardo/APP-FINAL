import pdfplumber
import os
import re

def extrair_produtos_pdf(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

    produtos = []

    with pdfplumber.open(caminho_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"

    if not texto_completo.strip():
        raise ValueError("Nenhum texto foi extraído do PDF.")

    linhas = texto_completo.splitlines()

    for linha in linhas:
        # Confirma se a linha tem formato esperado: começa com código e contém UN
        if re.match(r"^\d{8,}\s+\d+,\d{2}\s+UN", linha):
            partes = linha.split()

            try:
                codigo = partes[0]
                quantidade = partes[1].replace(',', '.')
                unidade = partes[2]

                # Encontrar posição da segunda quantidade (para isolar descrição)
                idx_qtd2 = next(i for i in range(3, len(partes)) if re.match(r"\d+,\d{2}", partes[i]))
                descricao = " ".join(partes[3:idx_qtd2])
                preco_unitario = partes[idx_qtd2 + 1].replace(',', '.')

                produtos.append({
                    "nome": descricao.strip(),
                    "unidades": float(quantidade),
                    "preco_custo": float(preco_unitario)
                })
            except Exception:
                continue

    if not produtos:
        raise ValueError("Nenhum produto encontrado no PDF.")

    return produtos