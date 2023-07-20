import os
from sys import exit
from subprocess import check_output, CalledProcessError
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QComboBox, QInputDialog
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QFile, QTextStream
from database import Database

ICON_PATH = f'{os.environ.get("HOME")}/.local/bin/pyconnect_utils/pyconnect-icon.png'


class PyConnect(QWidget):
    '''
    Class to create the application PyConnect

    Args:
        QWidget: Class to create the window
    '''

    def __init__(self) -> None:
        '''
        Function to initialize the application
        '''
        self.app = QApplication([])
        super().__init__()
        self.app.setApplicationName('PyConnect')

        file = QFile(f'{os.environ.get("HOME")}/.local/bin/pyconnect_utils/pyconnect-dark.qss')
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)

        self.app.setStyleSheet(stream.readAll())
        self.app.setWindowIcon(QIcon(ICON_PATH))

        self.layout_ = QVBoxLayout()
        self.layout_buttons = QGridLayout()
        self.layout_form = QGridLayout()
        self.database = Database()
        self.database.create_struct()
        self.sudopsw: str = ''

    def window_combobox(self):
        '''
        Function to create the combobox with the saved users
        '''
        cb_user = QComboBox()
        label_saved_user = QLabel('Usuários')
        users = self.database.select_all()
        cb_user.addItem('Selecione...')
        for user in users:
            cb_user.addItem(user[2])

        self.layout_form.addWidget(label_saved_user, 1, 0, 1, 1)
        self.layout_form.addWidget(cb_user, 1, 3, 1, 5)

    def window_form(self):
        '''
        Function to create the form
        '''
        label_title = QLabel('PyConnect')
        myFont = QFont()
        myFont.setBold(True)
        myFont.setPointSize(20)
        label_title.setFont(myFont)
        self.layout_form.addWidget(label_title, 0, 0, 1, 8, Qt.AlignCenter)

        label_server = QLabel('Servidor')
        label_user = QLabel('Usuário')
        label_password = QLabel('Senha')
        label_server_cert = QLabel('Certificado')
        self.layout_form.addWidget(label_server, 3, 0, 1, 1)
        self.layout_form.addWidget(label_server_cert, 5, 0, 1, 1)
        self.layout_form.addWidget(label_user, 7, 0, 1, 1)
        self.layout_form.addWidget(label_password, 9, 0, 1, 1)

        tf_server = QLineEdit()
        tf_user = QLineEdit()
        tf_password = QLineEdit()
        tf_password.setEchoMode(QLineEdit.Password)
        tf_server_cert = QLineEdit()
        self.layout_form.addWidget(tf_server, 3, 3, 1, 5)
        self.layout_form.addWidget(tf_server_cert, 5, 3, 1, 5)
        self.layout_form.addWidget(tf_user, 7, 3, 1, 5)
        self.layout_form.addWidget(tf_password, 9, 3)

        btn_save = QPushButton('Salvar')
        self.layout_form.addWidget(btn_save, 9, 4, 1, 4, Qt.AlignCenter)

    def window_buttons(self):
        '''
        Function to create the buttons
        '''
        btn_connect = QPushButton('Conectar')
        btn_reconnect = QPushButton('Reconectar')
        btn_disconnect = QPushButton('Desconectar')
        btn_reconnect.setEnabled(False)
        btn_disconnect.setEnabled(False)
        self.layout_buttons.addWidget(btn_connect, 0, 0)
        self.layout_buttons.addWidget(btn_reconnect, 0, 1)
        self.layout_buttons.addWidget(btn_disconnect, 0, 2)

    def window_layout(self):
        '''
        Function to create the window layout
        '''
        self.layout_.addLayout(self.layout_form)
        self.layout_.addLayout(self.layout_buttons)
        self.setLayout(self.layout_)
        self.setFixedSize(350, 250)

    def save(self):
        '''
        Function to save the user data
        '''
        server = self.layout_form.itemAt(7).widget().text()
        server_cert = self.layout_form.itemAt(8).widget().text()
        user = self.layout_form.itemAt(9).widget().text()
        psw = self.layout_form.itemAt(10).widget().text()

        if server == '' or user == '' or psw == '' or server_cert == '':
            self.alert('Preencha todos os campos!')
            return

        if len(self.database.select(user)) > 0:
            self.alert('Usuário já existe!')
            return

        self.database.insert(server, user, psw, server_cert)
        self.alert('Salvo com sucesso!')
        self.cb_add(user)

    def connect(self):
        '''
        Function to connect to the OpenConnect
        '''
        server = self.layout_form.itemAt(7).widget().text()
        server_cert = self.layout_form.itemAt(8).widget().text()
        user = self.layout_form.itemAt(9).widget().text()
        psw = self.layout_form.itemAt(10).widget().text()

        if server == '' or user == '' or psw == '' or server_cert == '':
            self.alert('Preencha todos os campos!')
            return

        # subprocess.run(
        #     f'echo "{self.sudopsw}" | sudo --stdin echo "{psw}" | sudo openconnect --protocol=gp {server} '
        #     f'--user={user} --servercert {server_cert} --passwd-on-stdin &', shell=True)

        os.system(
            f'echo "{self.sudopsw}" | sudo --stdin echo "{psw}" | sudo openconnect --protocol=gp {server} '
            f'--user={user} --servercert {server_cert} --passwd-on-stdin &')
        self.layout_buttons.itemAt(0).widget().setEnabled(False)  # Conectar
        self.layout_form.itemAt(7).widget().setEnabled(False)  # Servidor
        self.layout_form.itemAt(8).widget().setEnabled(False)  # Certificado
        self.layout_form.itemAt(9).widget().setEnabled(False)  # Usuário
        self.layout_form.itemAt(10).widget().setEnabled(False)  # Senha
        self.layout_form.itemAt(11).widget().setEnabled(False)  # Salvar
        self.layout_form.itemAt(1).widget().setEnabled(False)  # Combobox

        self.layout_buttons.itemAt(1).widget().setEnabled(True)  # Reconectar
        self.layout_buttons.itemAt(2).widget().setEnabled(True)  # Desconectar

    def reconnect(self):
        '''
        Function to reconnect to OpenConnect
        '''
        # subprocess.run(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)', shell=True)
        os.system(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)')
        self.connect()

    def disconnect(self):
        '''
        Function to disconnect from OpenConnect
        '''
        # subprocess.run(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)', shell=True)
        os.system(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)')
        self.layout_buttons.itemAt(0).widget().setEnabled(True)  # Conectar
        self.layout_form.itemAt(7).widget().setEnabled(True)  # Servidor
        self.layout_form.itemAt(8).widget().setEnabled(True)  # Certificado
        self.layout_form.itemAt(9).widget().setEnabled(True)  # Usuário
        self.layout_form.itemAt(10).widget().setEnabled(True)  # Senha
        self.layout_form.itemAt(11).widget().setEnabled(True)  # Salvar
        self.layout_form.itemAt(1).widget().setEnabled(True)  # Combobox

        self.layout_buttons.itemAt(1).widget().setEnabled(False)  # Reconectar
        self.layout_buttons.itemAt(2).widget().setEnabled(False)  # Desconectar

    def closeEvent(self, event):
        '''
        Function called when the window is closed

        Args:
            event (): event
        '''
        reply = QMessageBox.question(self, 'Sair', 'Deseja sair?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # subprocess.run(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)', shell=True)
            os.system(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)')
        else:
            event.ignore()

    def sudo_psw(self):
        '''
        Function to get the sudo password from the user
        '''
        while True:
            text, ok = QInputDialog().getText(self, 'PyConnect', 'Digite a senha do root:', QLineEdit.Password)
            if ok:
                if text == '':
                    self.alert('Digite sua senha!')
                else:
                    if self.verify_sudo(text):
                        self.sudopsw = text
                        break
                    else:
                        self.alert('Senha incorreta!')
            else:
                exit()

    def connect_buttons(self):
        '''
        Function to connect the buttons to their respective functions
        '''
        btn_save = self.layout_form.itemAt(11).widget()
        btn_save.clicked.connect(self.save)

        btn_connect = self.layout_buttons.itemAt(0).widget()
        btn_connect.clicked.connect(self.connect)

        btn_reconnect = self.layout_buttons.itemAt(1).widget()
        btn_reconnect.clicked.connect(self.reconnect)

        btn_disconnect = self.layout_buttons.itemAt(2).widget()
        btn_disconnect.clicked.connect(self.disconnect)

        cb_user = self.layout_form.itemAt(1).widget()
        cb_user.currentIndexChanged.connect(self.cb_change)

    def cb_change(self):
        '''
        Function to change the information in the form when the user changes
        '''
        cb_user = self.layout_form.itemAt(1).widget()
        if cb_user.currentIndex() == 0:
            self.layout_form.itemAt(7).widget().setText('')  # Servidor
            self.layout_form.itemAt(8).widget().setText('')  # Certificado
            self.layout_form.itemAt(9).widget().setText('')  # Usuário
            self.layout_form.itemAt(10).widget().setText('')  # Senha
            return

        infos = self.database.select(cb_user.currentText())
        self.layout_form.itemAt(7).widget().setText(infos[0][0])
        self.layout_form.itemAt(8).widget().setText(infos[0][1])
        self.layout_form.itemAt(9).widget().setText(infos[0][2])
        self.layout_form.itemAt(10).widget().setText(infos[0][3])

    def cb_add(self, user: str):
        '''
        Function to add a user to the combobox

        Args:
            user (str): user to be added
        '''
        cb_user = self.layout_form.itemAt(1).widget()
        cb_user.addItem(user)
        cb_user.setCurrentIndex(cb_user.findText(user))

    def alert(self, text: str):
        '''
        Function to show an alert

        Args:
            text (str): text to be shown
        '''
        alert = QMessageBox(self)
        alert.setText(text)
        alert.exec_()

    def verify_sudo(self, text: str) -> bool:
        '''
        Function to verify if the sudo password is correct

        Args:
            text (str): sudo password

        Returns:
            bool: True if the password is correct, False otherwise
        '''
        try:
            check_output(f'echo "{text}" | sudo --stdin echo "e"', shell=True)
        except CalledProcessError:
            return False

        return True


if __name__ == '__main__':
    pyconnect = PyConnect()
    pyconnect.window_combobox()
    pyconnect.window_form()
    pyconnect.window_buttons()
    pyconnect.window_layout()
    pyconnect.connect_buttons()
    pyconnect.show()
    pyconnect.sudo_psw()
    pyconnect.app.exec_()
