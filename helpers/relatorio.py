import os
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QRadioButton,
    QCalendarWidget, QMessageBox, QFileDialog
)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PyQt5.QtCore import QDate

DADOS_DIR = 'dados'
COMPRAS_CSV = os.path.join(DADOS_DIR, 'compras.csv')
LOGO_PATH = os.path.join('recursos', 'logo galeria.png')


class RelatorioHelper:
    @staticmethod
    def gerar_com_filtros(parent, tabela, tipos, fornecedores):
        dialog = QDialog(parent)
        dialog.setWindowTitle("Filtros do Relatório")
        layout = QVBoxLayout(dialog)

        # Aplica estilo ao diálogo
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 11pt;
            }
            QComboBox {
                color: #f0f0f0;
                background-color: #3b3b3b;
            }
            QLineEdit {
                color: #f0f0f0;
                background-color: #3b3b3b;
            }
            QRadioButton {
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #ff6600;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #e65c00;
            }
        """)

        # Tipo
        tipo_layout = QHBoxLayout()
        lbl_tipo = QLabel("Tipo:")
        tipo_layout.addWidget(lbl_tipo)
        tipo_cb = QComboBox()
        tipo_cb.setEditable(True)
        tipo_cb.addItem("")
        tipo_cb.addItems(tipos)
        tipo_layout.addWidget(tipo_cb)
        layout.addLayout(tipo_layout)

        # Fornecedor
        forn_layout = QHBoxLayout()
        lbl_forn = QLabel("Fornecedor:")
        forn_layout.addWidget(lbl_forn)
        forn_cb = QComboBox()
        forn_cb.setEditable(True)
        forn_cb.addItem("")
        forn_cb.addItems(fornecedores)
        forn_layout.addWidget(forn_cb)
        layout.addLayout(forn_layout)

        # Data
        data_layout = QVBoxLayout()
        periodo_completo_rb = QRadioButton("Período completo")
        periodo_completo_rb.setChecked(True)
        data_layout.addWidget(periodo_completo_rb)

        data_dia_rb = QRadioButton("Data específica")
        data_layout.addWidget(data_dia_rb)
        cal = QCalendarWidget()
        cal.setGridVisible(True)
        cal.setEnabled(False)
        data_layout.addWidget(cal)

        data_mes_rb = QRadioButton("Mês e Ano")
        data_layout.addWidget(data_mes_rb)
        mes_ano_layout = QHBoxLayout()
        mes_cb = QComboBox()
        mes_cb.addItems(['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                         'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
        ano_le = QLineEdit()
        ano_le.setPlaceholderText("AAAA")
        mes_cb.setEnabled(False)
        ano_le.setEnabled(False)
        mes_ano_layout.addWidget(mes_cb)
        mes_ano_layout.addWidget(ano_le)
        data_layout.addLayout(mes_ano_layout)

        layout.addLayout(data_layout)

        def atualizar_ui():
            cal.setEnabled(data_dia_rb.isChecked())
            mes_cb.setEnabled(data_mes_rb.isChecked())
            ano_le.setEnabled(data_mes_rb.isChecked())

        periodo_completo_rb.toggled.connect(atualizar_ui)
        data_dia_rb.toggled.connect(atualizar_ui)
        data_mes_rb.toggled.connect(atualizar_ui)

        # Botão gerar
        btn = QPushButton("Gerar")
        btn.clicked.connect(lambda: dialog.accept())
        layout.addWidget(btn)

        if not dialog.exec_():
            return

        # Leitura dos filtros
        tipo_filtro = tipo_cb.currentText().upper().strip()
        forn_filtro = forn_cb.currentText().upper().strip()

        data_escolhida = None
        mes_escolhido = None
        ano_escolhido = None
        if data_dia_rb.isChecked():
            data_escolhida = cal.selectedDate().toString("dd/MM/yyyy")
        elif data_mes_rb.isChecked():
            mes_escolhido = mes_cb.currentIndex()
            ano_escolhido = ano_le.text()

        # Filtrar dados
        dados_filtrados = [["Data", "Tipo", "Fornecedor", "Valor", "Tipo de Pedido"]]
        with open(COMPRAS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                data_ok = True
                tipo_ok = True
                forn_ok = True

                if tipo_filtro and tipo_filtro not in row[1].upper():
                    tipo_ok = False
                if forn_filtro and forn_filtro not in row[2].upper():
                    forn_ok = False

                if data_dia_rb.isChecked():
                    data_ok = row[0] == data_escolhida
                elif data_mes_rb.isChecked():
                    d = datetime.strptime(row[0], "%d/%m/%Y")
                    if mes_escolhido and d.month != mes_escolhido:
                        data_ok = False
                    if ano_escolhido and str(d.year) != ano_escolhido:
                        data_ok = False

                if tipo_ok and forn_ok and data_ok:
                    dados_filtrados.append(row[:5])

        if len(dados_filtrados) == 1:
            QMessageBox.warning(parent, "Sem dados", "Nenhum registro encontrado com os filtros informados.")
            return

        nome, _ = QFileDialog.getSaveFileName(
            parent, "Salvar Relatório", "relatorio_galeria_compras.pdf", "PDF Files (*.pdf)")
        if not nome:
            return

        doc = SimpleDocTemplate(nome, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=80, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []

        if os.path.exists(LOGO_PATH):
            story.append(Image(LOGO_PATH, width=140, height=90))

        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>RELATÓRIO - CONTROLE DE COMPRAS</b>", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Nome da Empresa: <b>Galeria dos Esportes</b>", styles['Normal']))
        story.append(Paragraph("CNPJ: <b>02.966.083/0001-01</b>", styles['Normal']))
        story.append(Paragraph("Endereço: <b>R SETE DE SETEMBRO Nº 654 BAIRRO CENTRO CAMPO GRANDE MS CEP 79002121</b>", styles['Normal']))
        story.append(Paragraph("Contato: <b>67 3384-2210</b>", styles['Normal']))
        story.append(Spacer(1, 20))

        t = Table(dados_filtrados, repeatRows=1, colWidths=[60, 110, 140, 80, 110])  # Valor aumentado de 60 para 80
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6600')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)

        def rodape(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            canvas.drawString(30, 20, f"Relatório gerado em: {data_atual}")
            canvas.drawRightString(A4[0] - 30, 20, f"Página {doc.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
        QMessageBox.information(parent, "Relatório", f"Relatório salvo em:\n{nome}")
