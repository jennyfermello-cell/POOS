import sys
import sqlite3

from PyQt6.QtCore import Qt, QRectF, QMarginsF
from PyQt6.QtGui import QPainter, QFont, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
    QHBoxLayout,
    QFileDialog
)

from atv import Janela_cadastro


class Janela_filtro(QMainWindow):
    def __init__(self, id_usuario=None, janela_anterior=None):
        super().__init__()
        self.id_usuario = id_usuario
        self.janela_anterior = janela_anterior
        self.topo = 100
        self.esquerda = 100
        self.largura = 1200
        self.altura = 750
        self.titulo = "Pesquisa de Usuários"
        self.setStyleSheet("QMainWindow {background-color: #f8f9fa;}")

        label1 = QLabel(self)
        label1.setText("Pesquisa de usuários")
        label1.move(0, 40)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label1.setStyleSheet('QLabel {font:bold;font-size:24px}')
        label1.resize(600, 30)

        label2 = QLabel(self)
        label2.setText("Palavra-chave:")
        label2.move(15, 110)
        label2.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label2.setStyleSheet('QLabel {font-size:15px}')
        label2.resize(145, 35)

        self.palavra_chave = QLineEdit(self)
        self.palavra_chave.move(165, 110)
        self.palavra_chave.resize(380, 35)
        self.palavra_chave.setPlaceholderText("Ex: João")

        self.botao_voltar = QPushButton("Voltar", self)
        self.botao_voltar.move(700, 110)
        self.botao_voltar.resize(130, 35)

        self.botao_voltar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        self.botao_voltar.clicked.connect(self.voltar)

        self.botao_pdf = QPushButton("Exportar PDF", self)
        self.botao_pdf.move(840, 110)
        self.botao_pdf.resize(130, 35)

        self.botao_pdf.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        self.botao_pdf.clicked.connect(self.exportar_pdf)

        self.botao_pesquisar = QPushButton(
            "Pesquisar", self
        )
        self.botao_pesquisar.move(560, 110)
        self.botao_pesquisar.resize(130, 35)
        self.botao_pesquisar.setStyleSheet(
            '''
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            '''
        )
        self.botao_pesquisar.clicked.connect(self.carregar_usuarios)
        self.tabela = QTableWidget(self)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.move(15, 180)
        self.tabela.resize(1170, 500)
        self.tabela.setColumnCount(14)
        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Nome",
            "Tipo Documento",
            "Documento",
            "E-mail",
            "Celular",
            "CEP",
            "Logradouro",
            "Número",
            "Complemento",
            "Bairro",
            "Cidade",
            "Estado",
            "Ações"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.tabela.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabela.setAlternatingRowColors(True)
        self.CarregarJanela()
        self.carregar_usuarios()

    def carregar_usuarios(self):
        palavra = self.palavra_chave.text().strip()
        try:
            conexao = sqlite3.connect("sistema_cadastro.db")
            cursor = conexao.cursor()
            if palavra:
                cursor.execute(
                    """
                    SELECT
                        id,
                        nome,
                        tipo_documento,
                        documento,
                        email,
                        celular,
                        cep,
                        logradouro,
                        numero,
                        complemento,
                        bairro,
                        cidade,
                        estado
                    FROM usuarios
                    WHERE
                        CAST(id AS TEXT) LIKE ?
                        OR nome LIKE ?
                        OR tipo_documento LIKE ?
                        OR documento LIKE ?
                        OR email LIKE ?
                        OR celular LIKE ?
                        OR cep LIKE ?
                        OR logradouro LIKE ?
                        OR numero LIKE ?
                        OR complemento LIKE ?
                        OR bairro LIKE ?
                        OR cidade LIKE ?
                        OR estado LIKE ?
                    ORDER BY nome
                    """,
                    tuple([f"%{palavra}%"] * 13)
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        id,
                        nome,
                        tipo_documento,
                        documento,
                        email,
                        celular,
                        cep,
                        logradouro,
                        numero,
                        complemento,
                        bairro,
                        cidade,
                        estado
                    FROM usuarios
                    ORDER BY nome
                    """
                )
            dados = cursor.fetchall()
            if palavra and not dados:
                QMessageBox.information(self,"Pesquisa", "Usuário não encontrado.")
            conexao.close()
            self.tabela.setRowCount(0)
            for linha, registro in enumerate(dados):
                self.tabela.insertRow(linha)

                for coluna, valor in enumerate(registro):
                    if valor is None:
                        valor = ""

                    item = QTableWidgetItem(str(valor))

                    self.tabela.setItem(
                        linha,
                        coluna,
                        item
                    )
                                # Widget para os botões de ação
                widget_acoes = QWidget()
                layout_acoes = QHBoxLayout(widget_acoes)

                layout_acoes.setContentsMargins(3, 3, 3, 3)
                layout_acoes.setSpacing(5)

                # Botão Atualizar
                botao_atualizar = QPushButton("Atualizar")
                botao_atualizar.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        font-size: 13px;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 5px;
                    }

                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)

                botao_atualizar.clicked.connect(
                    lambda _, linha=linha: self.atualizar_usuario(linha)
                )

                # Botão Excluir
                botao_excluir = QPushButton("Excluir")
                botao_excluir.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        font-size: 13px;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 5px;
                    }

                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)

                botao_excluir.clicked.connect(
                    lambda _, linha=linha: self.excluir_usuario(linha)
                )

                layout_acoes.addWidget(botao_atualizar)
                layout_acoes.addWidget(botao_excluir)

                self.tabela.setCellWidget(
                    linha,
                    13,
                    widget_acoes
                )
        except sqlite3.Error as e:

            QMessageBox.critical(
                self,
                "Erro no Banco de Dados",
                f"Não foi possível carregar os usuários:\n{e}"
            )

    def excluir_usuario(self, linha):
        id_usuario = self.tabela.item(linha, 0).text()

        resposta = QMessageBox.question(
            self,
            "Excluir usuário",
            f"Tem certeza que deseja excluir o usuário de ID {id_usuario}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            try:
                conexao = sqlite3.connect("sistema_cadastro.db")
                cursor = conexao.cursor()

                cursor.execute(
                    "DELETE FROM usuarios WHERE id = ?",
                    (id_usuario,)
                )

                conexao.commit()
                conexao.close()

                QMessageBox.information(
                    self,
                    "Exclusão",
                    "Usuário excluído com sucesso."
                )

                self.carregar_usuarios()

            except sqlite3.Error as e:
                QMessageBox.critical(
                    self,
                    "Erro no Banco de Dados",
                    f"Não foi possível excluir o usuário:\n{e}"
                )

    def atualizar_usuario(self, linha):
        item_id = self.tabela.item(linha, 0)
        if item_id is None:
            return
        id_usuario = int(item_id.text())
        self.janela_edicao = Janela_cadastro(
            id_usuario=id_usuario,
            janela_anterior=self
        )
        self.hide()

    def voltar(self):
        self.palavra_chave.clear()
        self.carregar_usuarios()

    def exportar_pdf(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF",
            "usuarios.pdf",
            "Arquivo PDF (*.pdf)"
        )

        if not caminho:
            return

        try:

            # ==========================================
            # CONFIGURAÇÃO DA IMPRESSORA/PDF
            # ==========================================

            printer = QPrinter(
                QPrinter.PrinterMode.HighResolution
            )

            printer.setOutputFormat(
                QPrinter.OutputFormat.PdfFormat
            )

            printer.setOutputFileName(caminho)

            # Configuração da página
            layout = printer.pageLayout()

            layout.setPageSize(
                QPageSize(QPageSize.PageSizeId.A4)
            )

            layout.setOrientation(
                QPageLayout.Orientation.Landscape
            )

            layout.setMargins(
                QMarginsF(10, 10, 10, 10)
            )

            printer.setPageLayout(layout)

            # ==========================================
            # INICIAR PAINT
            # ==========================================

            painter = QPainter()

            if not painter.begin(printer):
                raise Exception(
                    "Não foi possível iniciar a criação do PDF."
                )

            # Área imprimível
            area = printer.pageLayout().paintRectPixels(
                printer.resolution()
            )

            margem = 20

            x_inicio = area.left() + margem
            y = area.top() + margem

            largura_util = area.width() - (margem * 2)

            # ==========================================
            # TÍTULO
            # ==========================================

            painter.setFont(
                QFont(
                    "Arial",
                    16,
                    QFont.Weight.Bold
                )
            )

            painter.drawText(
                QRectF(
                    x_inicio,
                    y,
                    largura_util,
                    30
                ),
                Qt.AlignmentFlag.AlignCenter,
                "RELATÓRIO DE USUÁRIOS"
            )

            y += 40

            # ==========================================
            # PESQUISA
            # ==========================================

            painter.setFont(
                QFont("Arial", 9)
            )

            palavra = self.palavra_chave.text().strip()

            if palavra:
                texto_pesquisa = f"Pesquisa: {palavra}"
            else:
                texto_pesquisa = "Todos os usuários"

            painter.drawText(
                x_inicio,
                y,
                texto_pesquisa
            )

            y += 30

            # ==========================================
            # COLUNAS
            # ==========================================

            colunas = [
                ("ID", 40),
                ("Nome", 140),
                ("Tipo Doc.", 85),
                ("Documento", 100),
                ("E-mail", 150),
                ("Celular", 100),
                ("CEP", 70),
                ("Cidade", 110),
                ("Estado", 55)
            ]

            # Soma das larguras
            largura_total = sum(
                largura
                for _, largura in colunas
            )

            # Ajustar para caber na página
            fator = largura_util / largura_total

            colunas = [
                (
                    nome,
                    int(largura * fator)
                )
                for nome, largura in colunas
            ]

            # ==========================================
            # FUNÇÃO DO CABEÇALHO
            # ==========================================

            def desenhar_cabecalho():

                nonlocal y

                altura = 25

                painter.setFont(
                    QFont(
                        "Arial",
                        8,
                        QFont.Weight.Bold
                    )
                )

                x = x_inicio

                for nome, largura in colunas:

                    # Caixa
                    painter.drawRect(
                        QRectF(
                            x,
                            y,
                            largura,
                            altura
                        )
                    )

                    # Texto
                    painter.drawText(
                        QRectF(
                            x + 3,
                            y,
                            largura - 6,
                            altura
                        ),
                        Qt.AlignmentFlag.AlignCenter,
                        nome
                    )

                    x += largura

                y += altura

            # Primeiro cabeçalho
            desenhar_cabecalho()

            # ==========================================
            # DADOS DA TABELA
            # ==========================================

            indices = [
                0,   # ID
                1,   # Nome
                2,   # Tipo documento
                3,   # Documento
                4,   # E-mail
                5,   # Celular
                6,   # CEP
                11,  # Cidade
                12   # Estado
            ]

            altura_linha = 24

            painter.setFont(
                QFont("Arial", 7)
            )

            # ==========================================
            # PERCORRER USUÁRIOS
            # ==========================================

            for linha in range(
                self.tabela.rowCount()
            ):

                # Verificar fim da página
                if (
                    y + altura_linha
                    > area.bottom() - margem
                ):

                    printer.newPage()

                    y = area.top() + margem

                    desenhar_cabecalho()

                    painter.setFont(
                        QFont("Arial", 7)
                    )

                x = x_inicio

                # Cada coluna
                for indice, (_, largura) in zip(
                    indices,
                    colunas
                ):

                    item = self.tabela.item(
                        linha,
                        indice
                    )

                    if item:
                        texto = item.text()
                    else:
                        texto = ""

                    # Evitar texto invadindo outra coluna
                    quantidade = max(
                        5,
                        int(largura / 5)
                    )

                    if len(texto) > quantidade:

                        texto = (
                            texto[
                                :quantidade - 3
                            ]
                            + "..."
                        )

                    # Desenhar célula
                    painter.drawRect(
                        QRectF(
                            x,
                            y,
                            largura,
                            altura_linha
                        )
                    )

                    # Desenhar texto
                    painter.drawText(
                        QRectF(
                            x + 3,
                            y,
                            largura - 6,
                            altura_linha
                        ),
                        Qt.AlignmentFlag.AlignLeft
                        | Qt.AlignmentFlag.AlignVCenter,
                        texto
                    )

                    x += largura

                y += altura_linha

            # ==========================================
            # FINALIZAR PDF
            # ==========================================

            painter.end()

            QMessageBox.information(
                self,
                "PDF",
                "PDF exportado com sucesso!"
            )

        except Exception as e:

            try:
                if painter.isActive():
                    painter.end()
            except:
                pass

            QMessageBox.critical(
                self,
                "Erro ao exportar PDF",
                "Não foi possível salvar o PDF.\n\n"
                f"Erro:\n"
                f"{type(e).__name__}: {e}"
            )

    def CarregarJanela(self):
        self.setGeometry(self.esquerda, self.topo, self.largura, self.altura)
        self.setWindowTitle(self.titulo)
        self.show()

if __name__ == '__main__':
    aplicacao = QApplication(sys.argv)
    j = Janela_filtro()
    sys.exit(aplicacao.exec())
