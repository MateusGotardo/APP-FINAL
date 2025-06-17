
import csv
import os
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

DADOS_DIR = 'dados'
TIPOS_CSV = os.path.join(DADOS_DIR, 'tipos.csv')
FORNECEDORES_CSV = os.path.join(DADOS_DIR, 'fornecedores.csv')

class CadastroHelper:
    @staticmethod
    def cadastrar_tipo(parent, tipos, tipo_combo):
        tipo, ok = QInputDialog.getText(parent, "Cadastrar Tipo", "Novo Tipo:")
        if ok and tipo:
            tipo = tipo.strip()
            if tipo and tipo not in tipos:
                tipos.append(tipo)
                tipo_combo.addItem(tipo)
                with open(TIPOS_CSV, 'a', encoding='utf-8', newline='') as f:
                    csv.writer(f).writerow([tipo])
                QMessageBox.information(parent, "Cadastro", f"Tipo '{tipo}' cadastrado.")
            elif tipo in tipos:
                QMessageBox.information(parent, "Cadastro", f"Tipo '{tipo}' já existe.")
            else:
                QMessageBox.warning(parent, "Cadastro", "Tipo inválido.")

    @staticmethod
    def cadastrar_fornecedor(parent, fornecedores, forn_combo):
        fornecedor, ok = QInputDialog.getText(parent, "Cadastrar Fornecedor", "Novo Fornecedor:")
        if ok and fornecedor:
            fornecedor = fornecedor.strip()
            if fornecedor and fornecedor not in fornecedores:
                fornecedores.append(fornecedor)
                forn_combo.addItem(fornecedor)
                with open(FORNECEDORES_CSV, 'a', encoding='utf-8', newline='') as f:
                    csv.writer(f).writerow([fornecedor])
                QMessageBox.information(parent, "Cadastro", f"Fornecedor '{fornecedor}' cadastrado.")
            elif fornecedor in fornecedores:
                QMessageBox.information(parent, "Cadastro", f"Fornecedor '{fornecedor}' já existe.")
            else:
                QMessageBox.warning(parent, "Cadastro", "Fornecedor inválido.")

class CadastrarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro")
        self.setFixedSize(250, 150)
        layout = QVBoxLayout()
        label = QLabel("O que deseja cadastrar?")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn_tipo = QPushButton("TIPO")
        btn_forn = QPushButton("FORNECEDOR")
        btn_tipo.clicked.connect(self.accept_tipo)
        btn_forn.clicked.connect(self.accept_forn)

        layout.addWidget(btn_tipo)
        layout.addWidget(btn_forn)
        self.setLayout(layout)
        self.resultado = None

    def accept_tipo(self):
        self.resultado = 'tipo'
        self.accept()

    def accept_forn(self):
        self.resultado = 'fornecedor'
        self.accept()
