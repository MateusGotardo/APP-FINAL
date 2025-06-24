import csv
from PyQt5.QtWidgets import QMessageBox

class CadastroHelper:
    @staticmethod
    def cadastrar_tipo(parent, tipos_list, tipo_combo, novo_tipo, tipos_csv_path):
        if novo_tipo not in tipos_list:
            tipos_list.append(novo_tipo)
            tipo_combo.addItem(novo_tipo)
            with open(tipos_csv_path, 'a', encoding='utf-8', newline='') as f:
                csv.writer(f).writerow([novo_tipo])
            QMessageBox.information(parent, "Sucesso", f"Tipo '{novo_tipo}' cadastrado com sucesso.")
        else:
            QMessageBox.information(parent, "Aviso", f"Tipo '{novo_tipo}' já existe.")

    @staticmethod
    def cadastrar_fornecedor(parent, fornecedores_list, forn_combo, novo_forn, fornecedores_csv_path):
        if novo_forn not in fornecedores_list:
            fornecedores_list.append(novo_forn)
            forn_combo.addItem(novo_forn)
            with open(fornecedores_csv_path, 'a', encoding='utf-8', newline='') as f:
                csv.writer(f).writerow([novo_forn])
            QMessageBox.information(parent, "Sucesso", f"Fornecedor '{novo_forn}' cadastrado com sucesso.")
        else:
            QMessageBox.information(parent, "Aviso", f"Fornecedor '{novo_forn}' já existe.")
