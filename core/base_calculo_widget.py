import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView, QMessageBox,
    QSpinBox, QDoubleSpinBox, QFileDialog
)
from PyQt5.QtCore import Qt
from helpers.relatorio import RelatorioHelper

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
        self.setStyleSheet("""... (estilo omitido por brevidade) ...""")

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
            "Produto", "Qtd", "Custo Unit.", "Lucro (%)",
            "Incluir Frete", "Preço Final (R$)", "Preço Arredondado (R$)"
        ])
        header = self.tabela.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.layout.addWidget(self.tabela)

        botoes_layout = QHBoxLayout()

        self.btn_limpar = QPushButton("Limpar lista")
        self.btn_limpar.clicked.connect(self.limpar_lista)
        botoes_layout.addWidget(self.btn_limpar)

        self.btn_importar_pdf = QPushButton("Importar PDF de Produtos")
        self.btn_importar_pdf.clicked.connect(self.importar_pdf_produtos)
        botoes_layout.addWidget(self.btn_importar_pdf)

        self.botao_atualizar = QPushButton("Atualizar")
        self.botao_atualizar.clicked.connect(self.atualizar_produtos_manualmente)
        botoes_layout.addWidget(self.botao_atualizar)

        self.btn_gerar_relatorio = QPushButton("Gerar Relatório")
        self.btn_gerar_relatorio.clicked.connect(self.gerar_relatorio)
        botoes_layout.addWidget(self.btn_gerar_relatorio)

        self.layout.addLayout(botoes_layout)

    def adicionar_produto(self):
        nome = self.input_nome.text().strip()
        qtd = self.input_qtd.value()
        custo = self.input_custo.value()
        lucro = self.input_lucro.value()
        incluir_frete = self.checkbox_frete.isChecked()

        if not nome or custo <= 0:
            QMessageBox.warning(self, "Erro", "Nome e custo precisam ser válidos.")
            return

        self.produtos.append(Produto(nome, custo, qtd, incluir_frete, lucro))
        self.input_nome.clear()
        self.input_qtd.setValue(1)
        self.input_custo.setValue(0)
        self.input_lucro.setValue(120)
        self.checkbox_frete.setChecked(True)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.valor_frete = self.input_valor_frete.value()
        total_frete_qtd = sum(p.qtd for p in self.produtos if p.incluir_frete) or 1
        self.tabela.setRowCount(len(self.produtos))

        for row, p in enumerate(self.produtos):
            self.tabela.setItem(row, 0, QTableWidgetItem(p.nome))
            self.tabela.setItem(row, 1, QTableWidgetItem(str(p.qtd)))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"R$ {p.custo:.2f}"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{p.percentual_lucro:.1f}%"))
            self.tabela.setItem(row, 4, QTableWidgetItem("Sim" if p.incluir_frete else "Não"))
            preco_final = p.preco_com_lucro() + (self.valor_frete / total_frete_qtd if p.incluir_frete else 0)
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {preco_final:.2f}"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"R$ {arredondar_090(preco_final):.2f}"))

    def atualizar_produtos_manualmente(self):
        self.produtos.clear()

        for row in range(self.tabela.rowCount()):
            try:
                nome = self.tabela.item(row, 0).text()
                qtd = float(self.tabela.item(row, 1).text().replace(",", "."))
                custo = float(self.tabela.item(row, 2).text().replace("R$", "").replace(",", "."))
                lucro = float(self.tabela.item(row, 3).text().replace("%", "").strip().replace(",", "."))
                incluir_frete = self.tabela.item(row, 4).text().strip().lower() == "sim"

                self.produtos.append(Produto(nome, custo, qtd, incluir_frete, lucro))
            except Exception as e:
                print(f"Erro na linha {row}: {e}")

        self.atualizar_tabela()

    def gerar_relatorio(self):
        if not self.produtos:
            QMessageBox.warning(self, "Aviso", "Nenhum produto para gerar relatório.")
            return

        tabela = [["Produto", "Qtd", "Custo Unit.", "Lucro (%)", "Frete", "Preço Final"]]
        total_frete_qtd = sum(p.qtd for p in self.produtos if p.incluir_frete) or 1

        for p in self.produtos:
            preco_lucro = p.preco_com_lucro()
            frete_rateado = (self.valor_frete / total_frete_qtd) if p.incluir_frete else 0
            preco_final = preco_lucro + frete_rateado

            tabela.append([
                p.nome,
                str(p.qtd),
                f"R$ {p.custo:.2f}",
                f"{p.percentual_lucro:.1f}%",
                "Sim" if p.incluir_frete else "Não",
                f"R$ {preco_final:.2f}"
            ])

        RelatorioHelper.gerar_com_filtros(self, tabela, [], [])

    def limpar_lista(self):
        self.produtos = []
        self.atualizar_tabela()

    def importar_pdf_produtos(self):
        from helpers.pdf_import import extrair_produtos_pdf

        path, _ = QFileDialog.getOpenFileName(self, "Selecionar PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        try:
            produtos_extraidos = extrair_produtos_pdf(path)
            for p in produtos_extraidos:
                self.produtos.append(Produto(
                    nome=p["nome"],
                    custo=p["preco_custo"],
                    qtd=p["unidades"],
                    incluir_frete=True,
                    percentual_lucro=self.input_lucro.value()
                ))
            self.atualizar_tabela()
            QMessageBox.information(self, "Importado", f"{len(produtos_extraidos)} produtos importados com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar PDF:\n{e}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    janela = BaseCalculoWidget()
    janela.show()
    sys.exit(app.exec())
