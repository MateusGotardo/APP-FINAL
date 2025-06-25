import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QFrame
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from core.compras_widget import ComprasWidget  
from core.base_calculo_widget import BaseCalculoWidget

DADOS_DIR = 'dados'
RECURSOS_DIR = 'recursos'
LOGO_PATH = os.path.join(RECURSOS_DIR, 'logo galeria.png')

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galeria dos Esportes - Sistema Principal")
        self.setGeometry(100, 100, 1600, 900)
        self.showMaximized()

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 12pt;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QCheckBox {
                spacing: 5px;
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

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.menu_lateral = QWidget()
        self.menu_lateral.setFixedWidth(250)
        self.menu_lateral.setStyleSheet("background-color: #1f1f1f;")
        self.menu_lateral.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.container_principal = QHBoxLayout()
        self.central_widget.setLayout(self.container_principal)

        self.container_principal.addWidget(self.menu_lateral)

        # Área onde o módulo carregado ficará
        self.area_modulo = QWidget()
        self.area_modulo_layout = QVBoxLayout()
        self.area_modulo.setLayout(self.area_modulo_layout)
        self.area_modulo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container_principal.addWidget(self.area_modulo)

        self._build_menu_lateral()

        # Carrega módulo Compras automaticamente ao iniciar
        self.abrir_compras()

    def _build_menu_lateral(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.menu_lateral.setLayout(layout)

        # Logo
        if os.path.exists(LOGO_PATH):
            logo_lbl = QLabel()
            pixmap = QPixmap(LOGO_PATH)
            pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
            logo_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_lbl)

        # Informações da empresa
        info_lbl = QLabel(
            "Galeria dos Esportes\n"
            "CNPJ: 02.966.083/0001-01\n"
            "R Sete de Setembro Nº 654\n"
            "Centro, Campo Grande - MS\n"
            "CEP 79002-121\n"
            "Tel: (67) 3384-2210"
        )
        info_lbl.setAlignment(Qt.AlignCenter)
        info_lbl.setStyleSheet("font-size: 11pt; padding: 10px;")
        layout.addWidget(info_lbl)

        # Linha divisória
        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        linha.setFrameShadow(QFrame.Sunken)
        linha.setStyleSheet("color: #444444;")
        layout.addWidget(linha)

        # Botões do menu com estilo laranja
        btn_compras = QPushButton("Compras")
        self.estilo_botao_laranja(btn_compras)
        btn_compras.clicked.connect(self.abrir_compras)
        layout.addWidget(btn_compras)

        btn_base_calc = QPushButton("Base de cálculo 120%")
        self.estilo_botao_laranja(btn_base_calc)
        btn_base_calc.clicked.connect(self.abrir_base_calculo)
        layout.addWidget(btn_base_calc)

        btn_vazio1 = QPushButton("Vazio")
        self.estilo_botao_laranja(btn_vazio1)
        btn_vazio1.setDisabled(True)
        layout.addWidget(btn_vazio1)

        btn_vazio2 = QPushButton("Vazio")
        self.estilo_botao_laranja(btn_vazio2)
        btn_vazio2.setDisabled(True)
        layout.addWidget(btn_vazio2)

        layout.addStretch()

        btn_sair = QPushButton("Sair")
        self.estilo_botao_laranja(btn_sair)
        btn_sair.clicked.connect(self.close)
        layout.addWidget(btn_sair)

    def estilo_botao_laranja(self, botao):
        botao.setStyleSheet("""
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
        botao.setCursor(Qt.PointingHandCursor)

    def abrir_compras(self):
        self._limpar_area_modulo()
        self.compras_widget = ComprasWidget()
        self.area_modulo_layout.addWidget(self.compras_widget)

    def abrir_base_calculo(self):
        self._limpar_area_modulo()
        from core.base_calculo_widget import BaseCalculoWidget
        self.base_calc_widget = BaseCalculoWidget()
        self.area_modulo_layout.addWidget(self.base_calc_widget)

    def _limpar_area_modulo(self):
        # Remove widgets do layout da área principal antes de carregar novo módulo
        while self.area_modulo_layout.count():
            child = self.area_modulo_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
