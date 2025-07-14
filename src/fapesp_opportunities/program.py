import os
import json
import sys
import signal
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, 
    QLineEdit, QTextEdit, QLabel, QScrollArea, QFrame, QMainWindow, QAction, QToolBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QDesktopServices, QTextOption
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

import fapesp_opportunities.modules.configure as configure 
import fapesp_opportunities.modules.fapesp as fapesp
import fapesp_opportunities.about as about

from fapesp_opportunities.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu
from fapesp_opportunities.modules.wabout  import show_about_window

# Caminho para o arquivo de configuração
CONFIG_PATH = os.path.expanduser("~/.config/fapesp_opportunities/config.json")
configure.verify_default_config(CONFIG_PATH)



# Função simulada que retornaria os dicionários com base em CONF
def buscar_oportunidades(config_path):
    conf = configure.load_config(config_path)
    
    opportunities = fapesp.get_open_opportunities(url=conf["url"])
    opportunities = fapesp.filter_grants_by_title(opportunities, conf["title-contents"])
    opportunities = fapesp.filter_grants_by_content(opportunities, conf["body-contents"])
    
    total_list = fapesp.parse_opportunities(opportunities, base_url="https://fapesp.br")
    
    lista_ordenada = sorted(
        total_list,
        key=lambda d: datetime.strptime(d["end-date"], "%d/%m/%Y") if d.get("end-date") else datetime.max
    )
    return lista_ordenada

# Widget principal
class FapespGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.setMinimumSize(600, 400)

        ## Icon
        # Get base directory for icons
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        self.setWindowIcon(QIcon(self.icon_path)) 
        
        # 
        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Caminho do arquivo de configuração
        # Linha única: [ QLabel | QLineEdit (expande) | QPushButton (compacto) ]
        linha_caminho = QHBoxLayout()

        label = QLabel("Configure:")
        linha_caminho.addWidget(label)

        self.path_line = QLineEdit(CONFIG_PATH)
        self.path_line.setReadOnly(True)
        self.path_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        linha_caminho.addWidget(self.path_line)

        self.btn_abrir_json = QPushButton("Open")
        self.btn_abrir_json.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_abrir_json.clicked.connect(self.abrir_editor)
        linha_caminho.addWidget(self.btn_abrir_json)

        self.layout.addLayout(linha_caminho)

        
        # Botão para buscar oportunidades
        self.btn_buscar = QPushButton("Search")
        self.btn_buscar.clicked.connect(self.buscar)
        self.layout.addWidget(self.btn_buscar)

        # Área de rolagem para mostrar resultados
        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_widget.setLayout(self.result_layout)
        self.result_area.setWidget(self.result_widget)
        self.layout.addWidget(self.result_area)
    
        # Adiciona a toolbar
        self.create_toolbar()
        
        self.buscar()


    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # 
        about_action = QAction(QIcon.fromTheme("help-about"),"About", self)
        about_action.triggered.connect(self.open_about)
        about_action.setToolTip("Show the information of program.")
        toolbar.addAction(about_action)
        
        # 
        oport_action = QAction(QIcon.fromTheme("applications-internet"),"Oportunities", self)
        oport_action.triggered.connect(self.open_oportunities)
        oport_action.setToolTip("Open the FAPESP site with oportunities.")
        toolbar.addAction(oport_action)

    def open_oportunities(self):
        conf = configure.load_config(CONFIG_PATH)
        QDesktopServices.openUrl(QUrl(conf["url"]))

    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)
        
    def abrir_editor(self):
        if os.name == 'nt':  # Windows
            os.startfile(CONFIG_PATH)
        elif os.name == 'posix':  # Linux/macOS
            subprocess.run(['xdg-open', CONFIG_PATH])

    def buscar(self):
        # Limpa resultados anteriores
        for i in reversed(range(self.result_layout.count())):
            widget_to_remove = self.result_layout.itemAt(i).widget()
            widget_to_remove.setParent(None)
        
        try: 
            resultados = buscar_oportunidades(CONFIG_PATH)
            L=len(resultados)
            for i, item in enumerate(resultados,1):
                self.result_layout.addWidget(self.criar_card(item,i,L))
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning) # Ícone de advertência
            msg.setWindowTitle("Atention")   # Título da janela
            msg.setText("Error detected!")   # Texto principal
            msg.setInformativeText(f"{e}")   # Texto adicional opcional
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Botões padrão
            msg.setDefaultButton(QMessageBox.Ok)
            retorno = msg.exec_()


    def criar_card(self, info,ID,L):
        card = QFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(0)
        common_style = "border: 0px solid #FFFFFF; border-radius: 0px; font-size: 11pt; margin: 0px; padding: 0px;"

        # Título
        str_title=info['title']
        title = QLabel(f"<b>{ID}/{L} - {str_title}</b>")
        title.setWordWrap(True)
        title.adjustSize()
        #title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title.setStyleSheet("color: #000000; "+common_style)
        layout.addWidget(title)

        # Corpo
        str_link=info["link"]
        str_body=info["body"]
        str_all=f'{str_body} <a href="{str_link}">link</a>'
        str_all = str_all.replace("\n"," ")
        body = QLabel(str_all)
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        body.adjustSize()
        #body.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        body.setStyleSheet("color: #333333; background-color: #FFFFFF; "+common_style)
        layout.addWidget(body)

        # Local
        location = QLabel(f"<i>{info['city']} - {info['institute']}</i>")
        location.setWordWrap(True)
        location.adjustSize()
        #location.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        location.setTextInteractionFlags(Qt.TextSelectableByMouse)
        location.setStyleSheet("color: #333333; background-color: #FFFFFF; "+common_style)
        layout.addWidget(location)

        # Data final
        end_date = QLabel(f"<i>End date: {info['end-date']}</i>")
        end_date.setWordWrap(True)
        end_date.adjustSize()
        #end_date.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        end_date.setTextInteractionFlags(Qt.TextSelectableByMouse)
        end_date.setStyleSheet("color: #333333; background-color: #FFFFFF; "+common_style)
        layout.addWidget(end_date)

        card.setStyleSheet("""
            QFrame {
                background-color: #f3f3f3;
                border: 3px solid #ddd;
                border-radius: 10px;
                margin: 0px; 
                padding: 2px;
            }
        """)

        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        return card

    
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file('~/.local/share/applications')
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.config/autostart', overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.local/share/applications', overwrite=True)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    gui = FapespGUI()
    gui.show()
    sys.exit(app.exec_())


# Execução
if __name__ == "__main__":
    main()
