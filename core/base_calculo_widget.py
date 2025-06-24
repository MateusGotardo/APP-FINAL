import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView, QMessageBox,
    QSpinBox, QDoubleSpinBox, QFileDialog
)
from PyQt5.QtCore import Qt

def arredondar_090(valor):
    inteiro = int(valor)
    decimal = valor - inteiro
    if decimal > 0.9:
        return inteiro + 0.9
    else:
        return inteiro - 1 + 0.9 if decimal < 0.9 else inteiro + 0.9

class Produto:
    def __init__(self, nome, custo, qtd, incluir_frete, percentual_lucro=120):
        self.nome = nome
        self.custo = custo
        self.qtd = qtd
        self.incluir_frete = incluir_frete
        self.percentual_lucro = percentual_lucro

    def preco_com_lucro(self):
        return self.custo * (1 + self.percentual_lucro / 100)

class BaseCalculoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base de Cálculo 120%")
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

        self.produtos = []
        self.valor_frete = 0.0

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        entrada_layout = QHBoxLayout()

        entrada_layout.addWidget(QLabel("Produto:"))
        self.input_nome = QLineEdit()
        entrada_layout.addWidget(self.input_nome)

        entrada_layout.addWidget(QLabel("Qtd:"))
        self.input_qtd = QSpinBox()
        self.input_qtd.setRange(1, 1000000)
        entrada_layout.addWidget(self.input_qtd)

        entrada_layout.addWidget(QLabel("Custo unitário:"))
        self.input_custo = QDoubleSpinBox()
        self.input_custo.setRange(0.01, 1000000)
        self.input_custo.setPrefix("R$ ")
        self.input_custo.setDecimals(2)
        entrada_layout.addWidget(self.input_custo)

        entrada_layout.addWidget(QLabel("Lucro (%):"))
        self.input_lucro = QDoubleSpinBox()
        self.input_lucro.setRange(0, 500)
        self.input_lucro.setSuffix(" %")
        self.input_lucro.setValue(120)
        self.input_lucro.setMinimumWidth(100)  # Aumenta largura para não cortar %
        entrada_layout.addWidget(self.input_lucro)

        self.checkbox_frete = QCheckBox("Incluir frete")
        self.checkbox_frete.setChecked(True)
        entrada_layout.addWidget(self.checkbox_frete)

        self.btn_adicionar = QPushButton("Adicionar produto")
        self.btn_adicionar.clicked.connect(self.adicionar_produto)
        entrada_layout.addWidget(self.btn_adicionar)

        self.layout.addLayout(entrada_layout)

        frete_layout = QHBoxLayout()
        frete_layout.addWidget(QLabel("Valor total do frete da nota:"))
        self.input_valor_frete = QDoubleSpinBox()
        self.input_valor_frete.setRange(0, 1000000)
        self.input_valor_frete.setPrefix("R$ ")
        self.input_valor_frete.setDecimals(2)
        self.input_valor_frete.valueChanged.connect(self.atualizar_tabela)
        frete_layout.addWidget(self.input_valor_frete)
        self.layout.addLayout(frete_layout)

        self.tabela = QTableWidget(0, 7)
        self.tabela.setHorizontalHeaderLabels([
            "Produto", "Qtd", "Custo Unit.", "Lucro (%)", "Incluir Frete", "Preço Final (R$)", "Preço Arredondado (R$)"
        ])
        # Ajuste do redimensionamento das colunas:
        header = self.tabela.horizontalHeader()
        # Colunas 0 a 5 stretch normal
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        # Coluna "Preço Arredondado (R$)" largura fixa maior:
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.layout.addWidget(self.tabela)

        botoes_layout = QHBoxLayout()
        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        botoes_layout.addWidget(self.btn_exportar)

        self.btn_limpar = QPushButton("Limpar lista")
        self.btn_limpar.clicked.connect(self.limpar_lista)
        botoes_layout.addWidget(self.btn_limpar)

        self.layout.addLayout(botoes_layout)

        # Forçar a janela maximizada para teste layout tela cheia
        # self.showMaximized()

    # restante dos métodos seguem igual, igual código anterior...
    def adicionar_produto(self):
        nome = self.input_nome.text().strip()
        qtd = self.input_qtd.value()
        custo = self.input_custo.value()
        lucro = self.input_lucro.value()
        incluir_frete = self.checkbox_frete.isChecked()

        if not nome:
            QMessageBox.warning(self, "Erro", "Informe o nome do produto.")
            return
        if custo <= 0:
            QMessageBox.warning(self, "Erro", "Informe um custo válido (> 0).")
            return

        produto = Produto(nome, custo, qtd, incluir_frete, lucro)
        self.produtos.append(produto)

        self.input_nome.clear()
        self.input_qtd.setValue(1)
        self.input_custo.setValue(0)
        self.input_lucro.setValue(120)
        self.checkbox_frete.setChecked(True)

        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.valor_frete = self.input_valor_frete.value()
        total_unidades_com_frete = sum(p.qtd for p in self.produtos if p.incluir_frete)
        if total_unidades_com_frete == 0:
            total_unidades_com_frete = 1

        self.tabela.setRowCount(len(self.produtos))

        for row, produto in enumerate(self.produtos):
            self.tabela.setItem(row, 0, QTableWidgetItem(produto.nome))
            self.tabela.setItem(row, 1, QTableWidgetItem(str(produto.qtd)))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"R$ {produto.custo:.2f}"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{produto.percentual_lucro:.1f}%"))
            self.tabela.setItem(row, 4, QTableWidgetItem("Sim" if produto.incluir_frete else "Não"))

            preco_lucro = produto.preco_com_lucro()
            frete_rateado = (self.valor_frete / total_unidades_com_frete) if produto.incluir_frete else 0
            preco_final = preco_lucro + frete_rateado

            preco_final_arred = arredondar_090(preco_final)

            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {preco_final:.2f}"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"R$ {preco_final_arred:.2f}"))

    def exportar_csv(self):
        if not self.produtos:
            QMessageBox.warning(self, "Aviso", "Nenhum produto para exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", "precos_tabelados.csv", "CSV files (*.csv)")
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("Produto,Quantidade,Custo Unit.,Lucro (%),Incluir Frete,Preço Final,Preço Arredondado\n")
                total_unidades_com_frete = sum(p.qtd for p in self.produtos if p.incluir_frete)
                if total_unidades_com_frete == 0:
                    total_unidades_com_frete = 1

                for p in self.produtos:
                    preco_lucro = p.preco_com_lucro()
                    frete_rateado = (self.valor_frete / total_unidades_com_frete) if p.incluir_frete else 0
                    preco_final = preco_lucro + frete_rateado
                    preco_final_arred = arredondar_090(preco_final)
                    line = (
                        f"{p.nome},{p.qtd},{p.custo:.2f},{p.percentual_lucro:.1f},"
                        f"{'Sim' if p.incluir_frete else 'Não'},{preco_final:.2f},{preco_final_arred:.2f}\n"
                    )
                    f.write(line)
            QMessageBox.information(self, "Sucesso", f"Arquivo salvo em:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{e}")

    def limpar_lista(self):
        self.produtos = []
        self.atualizar_tabela()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    janela = BaseCalculoWidget()
    janela.show()
    sys.exit(app.exec())
