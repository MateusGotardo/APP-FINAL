
import sys
import os
import csv
import locale
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QCompleter, QTextEdit,
    QCalendarWidget
)
from PyQt5.QtCore import Qt
from cadastro import CadastroHelper, CadastrarDialog
from relatorio import RelatorioHelper

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

DADOS_DIR = 'dados'
COMPRAS_CSV = os.path.join(DADOS_DIR, 'compras.csv')
TIPOS_CSV = os.path.join(DADOS_DIR, 'tipos.csv')
FORNECEDORES_CSV = os.path.join(DADOS_DIR, 'fornecedores.csv')

if not os.path.exists(DADOS_DIR):
    os.makedirs(DADOS_DIR)

for arquivo, cabecalho in [
    (COMPRAS_CSV, ['Data', 'Tipo', 'Fornecedor', 'Valor', 'Tipo de Pedido', 'Observações']),
    (TIPOS_CSV, ['Tipo']),
    (FORNECEDORES_CSV, ['Fornecedor'])
]:
    if not os.path.exists(arquivo):
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(cabecalho)

class ControleComprasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle Compras Galeria dos Esportes")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #ff6600;
                color: white;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e65c00;
            }
            QHeaderView::section {
                background-color: #ff6600;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
        """)
        self.tipos = self.carregar_lista(TIPOS_CSV)
        self.fornecedores = self.carregar_lista(FORNECEDORES_CSV)
        self.setup_ui()
        self.carregar_tabela()

    def carregar_lista(self, arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return [row[0] for row in csv.reader(f)][1:]

    def setup_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        self.lbl_data = QLabel("Data")
        self.data_entry = QLineEdit()
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
        form_layout.addWidget(self.tipo_combo)
        self.lbl_forn = QLabel("Fornecedor")
        self.forn_combo = QComboBox()
        self.forn_combo.setEditable(True)
        self.forn_combo.addItems(self.fornecedores)
        self.forn_combo.setCompleter(QCompleter(self.fornecedores))
        form_layout.addWidget(self.lbl_forn)
        form_layout.addWidget(self.forn_combo)
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
        self.btn_salvar.clicked.connect(self.salvar_compra)
        self.btn_excluir = QPushButton("Excluir Compra")
        self.btn_excluir.clicked.connect(self.excluir_compra)
        self.btn_relatorio = QPushButton("Gerar Relatório")
        self.btn_relatorio.clicked.connect(lambda: RelatorioHelper.gerar(self, self.tabela))
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_excluir)
        btn_layout.addWidget(self.btn_relatorio)
        layout.addLayout(btn_layout)
        self.filtro_entry = QLineEdit()
        self.filtro_entry.setPlaceholderText("Filtro")
        self.filtro_entry.textChanged.connect(self.filtrar_tabela)
        layout.addWidget(self.filtro_entry)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["Data", "Tipo", "Fornecedor", "Valor", "Tipo de Pedido", "Observações"])
        self.tabela.horizontalHeader().setDefaultSectionSize(180)
        layout.addWidget(self.tabela)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def salvar_compra(self):
        data = self.data_entry.text()
        tipo = self.tipo_combo.currentText()
        fornecedor = self.forn_combo.currentText()
        valor_str = self.valor_entry.text().replace('R$', '').replace('.', '').replace(',', '.')
        obs = self.obs_entry.toPlainText()
        pedido = self.pedido_combo.currentText()
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
        cal = QCalendarWidget()
        cal.setGridVisible(True)
        cal.setWindowModality(Qt.ApplicationModal)
        cal.setWindowTitle("Escolha a Data")
        cal.setGeometry(400, 300, 300, 250)
        cal.show()
        cal.clicked.connect(lambda date: self.data_entry.setText(date.toString("dd/MM/yyyy")))

    def abrir_cadastrar_dialog(self):
        dialog = CadastrarDialog(self)
        if dialog.exec_():
            if dialog.resultado == 'tipo':
                CadastroHelper.cadastrar_tipo(self, self.tipos, self.tipo_combo)
            elif dialog.resultado == 'fornecedor':
                CadastroHelper.cadastrar_fornecedor(self, self.fornecedores, self.forn_combo)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ControleComprasApp()
    win.show()
    sys.exit(app.exec_())
