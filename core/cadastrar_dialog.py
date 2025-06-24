from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class CadastrarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo")
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 12pt;
            }
            QLineEdit, QComboBox {
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
        """)

        self.resultado = None
        self.texto = ""

        layout = QVBoxLayout(self)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Tipo", "Fornecedor"])
        layout.addWidget(QLabel("Escolha o tipo de cadastro:"))
        layout.addWidget(self.combo_tipo)

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Digite o nome para cadastro")
        layout.addWidget(self.input_nome)

        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.clicked.connect(self.realizar_cadastro)
        layout.addWidget(btn_cadastrar)

    def realizar_cadastro(self):
        self.texto = self.input_nome.text().strip()
        if not self.texto:
            QMessageBox.warning(self, "Erro", "Digite um nome válido.")
            return
        self.resultado = self.combo_tipo.currentText().lower()
        self.accept()
