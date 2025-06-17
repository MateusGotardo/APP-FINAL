
import csv
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyQt5.QtWidgets import QFileDialog, QMessageBox

DADOS_DIR = 'dados'
COMPRAS_CSV = os.path.join(DADOS_DIR, 'compras.csv')
LOGO_PATH = os.path.join('recursos', 'logo_galeria.png')

class RelatorioHelper:
    @staticmethod
    def gerar(parent, tabela):
        nome, _ = QFileDialog.getSaveFileName(parent, "Salvar Relatório", "relatorio_galeria_compras.pdf", "PDF Files (*.pdf)")
        if not nome:
            return

        c = canvas.Canvas(nome, pagesize=A4)
        c.setFont("Helvetica", 12)

        if os.path.exists(LOGO_PATH):
            c.drawImage(ImageReader(LOGO_PATH), 50, 770, width=100, height=50, mask='auto')

        c.drawString(200, 820, "RELATÓRIO - CONTROLE DE COMPRAS")
        c.drawString(200, 805, "Nome da Empresa: Galeria dos Esportes")
        c.drawString(200, 790, "CNPJ: 02.966.083/0001-01")
        c.drawString(200, 775, "Endereço: R SETE DE SETEMBRO Nº 654 BAIRRO CENTRO CAMPO GRANDE MS CEP 79002121")
        c.drawString(200, 760, "CONTATO: 67 3384-2210")

        y = 740
        for row in range(tabela.rowCount()):
            linha = [tabela.item(row, col).text() for col in range(tabela.columnCount())]
            c.drawString(50, y, ' | '.join(linha))
            y -= 20
            if y < 50:
                c.showPage()
                y = 800

        c.save()
        QMessageBox.information(parent, "Relatório", f"Relatório salvo em: {nome}")
