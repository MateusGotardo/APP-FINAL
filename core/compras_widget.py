import os
import csv
import locale
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QCompleter, QTextEdit, QCalendarWidget, QDialog, QHeaderView
)
from PyQt5.QtCore import Qt
from core.cadastrar_dialog import CadastrarDialog
from core.cadastrar_helper import CadastroHelper

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

DADOS_DIR = 'dados'
COMPRAS_CSV = os.path.join(DADOS_DIR, 'compras.csv')
TIPOS_CSV = os.path.join(DADOS_DIR, 'tipos.csv')
FORNECEDORES_CSV = os.path.join(DADOS_DIR, 'fornecedores.csv')

class ComprasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tipos = self.carregar_lista(TIPOS_CSV)
        self.fornecedores = self.carregar_lista(FORNECEDORES_CSV)
        self.setup_ui()
        self.carregar_tabela()

    def carregar_lista(self, arquivo):
        if not os.path.exists(arquivo):
            return []
        with open(arquivo, 'r', encoding='utf-8') as f:
            return [row[0] for row in csv.reader(f)][1:]

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 12pt;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #ff6600;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e65c00;
            }
            QTableWidget {
                background-color: #1f1f1f;
                color: #f0f0f0;
                gridline-color: #444444;
            }
            QHeaderView::section {
                background-color: #ff6600;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.lbl_data = QLabel("Data")
        self.data_entry = QLineEdit()
        self.data_entry.setInputMask("00/00/0000")
        self.data_entry.setText(datetime.today().strftime('%d/%m/%Y'))
        self.btn_calendar = QPushButton("📅")
        self.btn_calendar.clicked.connect(self.abrir_calendario)
        form_layout.addWidget(self.lbl_data)
        form_layout.addWidget(self.data_entry)
        form_layout.addWidget(self.btn_calendar)

        self.lbl_tipo = QLabel("Tipo")
        self.tipo_combo = QComboBox()
        self.tipo_combo.setEditable(True)
        self.tipo_combo.addItems(self.tipos)
        self.tipo_combo.setCompleter(QCompleter(self.tipos))
        form_layout.addWidget(self.lbl_tipo)
        form_layout.addWidget(self.tipo_combo, 2)

        self.lbl_forn = QLabel("Fornecedor")
        self.forn_combo = QComboBox()
        self.forn_combo.setEditable(True)
        self.forn_combo.addItems(self.fornecedores)
        self.forn_combo.setCompleter(QCompleter(self.fornecedores))
        form_layout.addWidget(self.lbl_forn)
        form_layout.addWidget(self.forn_combo, 2)

        self.lbl_valor = QLabel("Valor")
        self.valor_entry = QLineEdit()
        self.valor_entry.setPlaceholderText("R$ 0,00")
        form_layout.addWidget(self.lbl_valor)
        form_layout.addWidget(self.valor_entry)

        self.lbl_pedido = QLabel("Tipo Pedido")
        self.pedido_combo = QComboBox()
        self.pedido_combo.addItems(["FORNECEDOR", "SITE"])
        form_layout.addWidget(self.lbl_pedido)
        form_layout.addWidget(self.pedido_combo)

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.clicked.connect(self.abrir_cadastrar_dialog)
        form_layout.addWidget(self.btn_cadastrar)

        layout.addLayout(form_layout)

        self.obs_entry = QTextEdit()
        self.obs_entry.setPlaceholderText("Observações (opcional)")
        self.obs_entry.setFixedHeight(60)
        layout.addWidget(self.obs_entry)

        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton("Salvar Compra")
        self.btn_excluir = QPushButton("Excluir Compra")
        self.btn_relatorio = QPushButton("Gerar Relatório")
        self.btn_backup = QPushButton("Gerar Backup CSV")
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_excluir)
        btn_layout.addWidget(self.btn_relatorio)
        btn_layout.addWidget(self.btn_backup)
        layout.addLayout(btn_layout)

        self.filtro_entry = QLineEdit()
        self.filtro_entry.setPlaceholderText("Filtro")
        layout.addWidget(self.filtro_entry)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Data", "Tipo", "Fornecedor", "Valor", "Tipo de Pedido", "Observações"
        ])
        self.tabela.setSortingEnabled(True)

        header = self.tabela.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(self.tabela.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        layout.addWidget(self.tabela)

        self.setLayout(layout)

        # Conexões
        self.btn_salvar.clicked.connect(self.salvar_compra)
        self.btn_excluir.clicked.connect(self.excluir_compra)
        self.btn_backup.clicked.connect(self.gerar_backup)
        self.btn_relatorio.clicked.connect(self.gerar_relatorio_placeholder)
        self.filtro_entry.textChanged.connect(self.filtrar_tabela)

    def abrir_calendario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Escolha a Data")
        layout = QVBoxLayout(dialog)
        cal = QCalendarWidget()
        cal.setGridVisible(True)
        layout.addWidget(cal)
        cal.clicked.connect(lambda date: (
            self.data_entry.setText(date.toString("dd/MM/yyyy")),
            dialog.accept()
        ))
        dialog.exec_()

    def abrir_cadastrar_dialog(self):
        dialog = CadastrarDialog(self)
        if dialog.exec_():
            if dialog.resultado == 'tipo':
                CadastroHelper.cadastrar_tipo(self, self.tipos, self.tipo_combo, dialog.texto, TIPOS_CSV)
            elif dialog.resultado == 'fornecedor':
                CadastroHelper.cadastrar_fornecedor(self, self.fornecedores, self.forn_combo, dialog.texto, FORNECEDORES_CSV)

    def salvar_compra(self):
            data = self.data_entry.text()
            tipo = self.tipo_combo.currentText()
            fornecedor = self.forn_combo.currentText()
            valor_str = self.valor_entry.text().replace('R$', '').replace('.', '').replace(',', '.')
            obs = self.obs_entry.toPlainText()
            pedido = self.pedido_combo.currentText()

            if not data or not tipo or not fornecedor or not valor_str.strip():
                QMessageBox.warning(self, "Erro", "Preencha todos os campos obrigatórios.")
                return

            try:
                valor = float(valor_str)
            except ValueError:
                QMessageBox.warning(self, "Erro", "Valor inválido.")
                return

            if tipo not in self.tipos:
                if QMessageBox.question(self, "Cadastrar Tipo", f"Cadastrar novo tipo '{tipo}'?") == QMessageBox.Yes:
                    self.tipos.append(tipo)
                    self.tipo_combo.addItem(tipo)
                    with open(TIPOS_CSV, 'a', encoding='utf-8', newline='') as f:
                        csv.writer(f).writerow([tipo])

            if fornecedor not in self.fornecedores:
                if QMessageBox.question(self, "Cadastrar Fornecedor", f"Cadastrar novo fornecedor '{fornecedor}'?") == QMessageBox.Yes:
                    self.fornecedores.append(fornecedor)
                    self.forn_combo.addItem(fornecedor)
                    with open(FORNECEDORES_CSV, 'a', encoding='utf-8', newline='') as f:
                        csv.writer(f).writerow([fornecedor])

            with open(COMPRAS_CSV, 'a', encoding='utf-8', newline='') as f:
                csv.writer(f).writerow([data, tipo, fornecedor, locale.currency(valor, grouping=True), pedido, obs])

            QMessageBox.information(self, "Salvo", "Compra registrada.")
            self.carregar_tabela()

    def carregar_tabela(self):
        self.tabela.setRowCount(0)
        if not os.path.exists(COMPRAS_CSV):
            return
        with open(COMPRAS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                pos = self.tabela.rowCount()
                self.tabela.insertRow(pos)
                for i, val in enumerate(row):
                    self.tabela.setItem(pos, i, QTableWidgetItem(val))

    def excluir_compra(self):
        linha = self.tabela.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Erro", "Selecione uma linha para excluir.")
            return
        self.tabela.removeRow(linha)
        with open(COMPRAS_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Data", "Tipo", "Fornecedor", "Valor", "Tipo de Pedido", "Observações"])
            for row in range(self.tabela.rowCount()):
                writer.writerow([self.tabela.item(row, col).text() for col in range(6)])

    def filtrar_tabela(self):
        filtro = self.filtro_entry.text().lower()
        for row in range(self.tabela.rowCount()):
            match = False
            for col in range(6):
                item = self.tabela.item(row, col)
                if filtro in item.text().lower():
                    match = True
                    break
            self.tabela.setRowHidden(row, not match)

    def abrir_calendario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Escolha a Data")
        layout = QVBoxLayout(dialog)
        cal = QCalendarWidget()
        cal.setGridVisible(True)
        layout.addWidget(cal)
        cal.clicked.connect(lambda date: (
            self.data_entry.setText(date.toString("dd/MM/yyyy")),
            dialog.accept()
        ))
        dialog.exec_()

    def abrir_cadastrar_dialog(self):
        dialog = CadastrarDialog(self)
        if dialog.exec_():
            if dialog.resultado == 'tipo':
                CadastroHelper.cadastrar_tipo(self, self.tipos, self.tipo_combo)
            elif dialog.resultado == 'fornecedor':
                CadastroHelper.cadastrar_fornecedor(self, self.fornecedores, self.forn_combo)

    def gerar_backup(self):
        nome, _ = QFileDialog.getSaveFileName(self, "Salvar Backup", "backup_compras.csv", "CSV Files (*.csv)")
        if nome:
            with open(nome, 'w', encoding='utf-8', newline='') as f_out:
                with open(COMPRAS_CSV, 'r', encoding='utf-8') as f_in:
                    for line in f_in:
                        f_out.write(line)
            QMessageBox.information(self, "Backup", f"Backup salvo em: {nome}")

    def gerar_relatorio_placeholder(self):
        QMessageBox.information(self, "Relatório", "Função gerar relatório ainda a ser implementada.")

