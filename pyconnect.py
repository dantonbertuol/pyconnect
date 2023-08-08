import os
from sys import exit
from subprocess import check_output, CalledProcessError
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QComboBox, QInputDialog, QCheckBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QFont, QIcon, QPixmap
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
        self.tray = QSystemTrayIcon(self)
        self.menu = QMenu(self)

    def window_combobox(self) -> None:
        '''
        Function to create the combobox with the saved users
        '''
        cb_user = QComboBox()
        label_saved_user = QLabel('Usuários')
        users = self.database.select_all_users()
        cb_user.addItem('Selecione...')
        for user in users:
            cb_user.addItem(user[0])

        self.layout_form.addWidget(label_saved_user, 1, 0, 1, 1)
        self.layout_form.addWidget(cb_user, 1, 3, 1, 6)

    def window_form(self) -> None:
        '''
        Function to create the form
        '''
        label_title = QLabel('PyConnect')
        label_icon = QLabel()
        label_icon.setPixmap(QPixmap(ICON_PATH).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        myFont = QFont()
        myFont.setBold(True)
        myFont.setPointSize(20)
        label_title.setFont(myFont)
        self.layout_form.addWidget(label_icon, 0, 0, 1, 1, Qt.AlignCenter)
        self.layout_form.addWidget(label_title, 0, 1, 1, 6, Qt.AlignCenter)

        label_server = QLabel('Servidor')
        label_user = QLabel('Usuário')
        label_password = QLabel('Senha')
        label_server_cert = QLabel('Certificado')
        self.layout_form.addWidget(label_server, 3, 0, 1, 1)
        self.layout_form.addWidget(label_server_cert, 5, 0, 1, 1)
        self.layout_form.addWidget(label_user, 7, 0, 1, 1)
        self.layout_form.addWidget(label_password, 9, 0, 1, 1)

        tf_server = QLineEdit()
        tf_server_cert = QLineEdit()
        tf_user = QLineEdit()
        tf_password = QLineEdit()
        tf_password.setEchoMode(QLineEdit.Password)
        self.layout_form.addWidget(tf_server, 3, 3, 1, 6)
        self.layout_form.addWidget(tf_server_cert, 5, 3, 1, 6)
        self.layout_form.addWidget(tf_user, 7, 3, 1, 6)
        self.layout_form.addWidget(tf_password, 9, 3)

        check_save_password = QCheckBox()
        check_save_password.setToolTip('Marque se deseja salvar a senha')
        self.layout_form.addWidget(check_save_password, 9, 4)

        btn_save = QPushButton('Salvar')
        self.layout_form.addWidget(btn_save, 9, 5, 1, 4, Qt.AlignCenter)

    def window_buttons(self) -> None:
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

    def window_layout(self) -> None:
        '''
        Function to create the window layout
        '''
        self.layout_.addLayout(self.layout_form)
        self.layout_.addLayout(self.layout_buttons)
        self.setLayout(self.layout_)
        self.setFixedSize(350, 250)

    def tray_icon(self) -> None:
        '''
        Function to create the tray icon
        '''
        self.tray.setIcon(QIcon(ICON_PATH))
        self.tray.setVisible(True)

        action_open = QAction('Abrir', self)
        action_open.triggered.connect(self.show_window)
        action_open.setEnabled(True)

        action_connect = QAction('Conectar', self)
        action_connect.triggered.connect(self.connect_server)
        action_connect.setEnabled(True)

        action_reconnect = QAction('Reconectar', self)
        action_reconnect.triggered.connect(self.reconnect_server)
        action_reconnect.setEnabled(False)

        action_disconnect = QAction('Desconectar', self)
        action_disconnect.triggered.connect(self.disconnect_server)
        action_disconnect.setEnabled(False)

        action_exit = QAction('Sair', self)
        action_exit.triggered.connect(self.app.quit)

        self.menu.addAction(action_open)
        self.menu.addAction(action_connect)
        self.menu.addAction(action_reconnect)
        self.menu.addAction(action_disconnect)
        self.menu.addAction(action_exit)

        self.tray.setContextMenu(self.menu)

    def save(self) -> None:
        '''
        Function to save the user data
        '''
        server = self.layout_form.itemAt(8).widget()
        server_cert = self.layout_form.itemAt(9).widget()
        user = self.layout_form.itemAt(10).widget()
        psw = self.layout_form.itemAt(11).widget()
        check_psw = self.layout_form.itemAt(12).widget().isChecked()

        if len(self.database.select_user(user.text())) > 0:
            self.alert('Usuário já existe!')
            return

        if check_psw:
            psw = self.layout_form.itemAt(11).widget()

        if not self.valid_fields('save', [server, server_cert, user, psw, check_psw]):
            return

        self.database.insert_user(server.text(), user.text(), psw.text(), server_cert.text())
        self.alert('Salvo com sucesso!')
        self.cb_add(user.text())

    def connect_server(self) -> None:
        '''
        Function to connect to the OpenConnect
        '''
        server = self.layout_form.itemAt(8).widget()
        server_cert = self.layout_form.itemAt(9).widget()
        user = self.layout_form.itemAt(10).widget()
        psw = self.layout_form.itemAt(11).widget()

        if not self.valid_fields('connect', [server, server_cert, user, psw, True]):
            return

        os.system(
            f'echo "{self.sudopsw}" | sudo --stdin echo "{psw.text()}" | sudo openconnect --protocol=gp {server.text()}'
            f' --user={user.text()} --servercert {server_cert.text()} --passwd-on-stdin &')
        self.layout_buttons.itemAt(0).widget().setEnabled(False)  # Conectar
        self.layout_form.itemAt(8).widget().setEnabled(False)  # Servidor
        self.layout_form.itemAt(9).widget().setEnabled(False)  # Certificado
        self.layout_form.itemAt(10).widget().setEnabled(False)  # Usuário
        self.layout_form.itemAt(11).widget().setEnabled(False)  # Senha
        self.layout_form.itemAt(12).widget().setEnabled(False)  # Checkbox Salvar senha
        self.layout_form.itemAt(13).widget().setEnabled(False)  # Salvar
        self.layout_form.itemAt(1).widget().setEnabled(False)  # Combobox

        self.layout_buttons.itemAt(1).widget().setEnabled(True)  # Reconectar
        self.layout_buttons.itemAt(2).widget().setEnabled(True)  # Desconectar

        menu_actions = self.menu.actions()
        menu_actions[1].setEnabled(False)  # Conectar
        menu_actions[2].setEnabled(True)  # Reconectar
        menu_actions[3].setEnabled(True)  # Desconectar

        self.database.insert_last_user(user.text())

    def reconnect_server(self) -> None:
        '''
        Function to reconnect to OpenConnect
        '''
        self.disconnect_server()
        self.connect_server()

    def disconnect_server(self) -> None:
        '''
        Function to disconnect from OpenConnect
        '''
        # os.system(f'echo "{self.sudopsw}" | sudo --stdin kill -9 $(pidof openconnect)')
        os.system(f'echo "{self.sudopsw}" | sudo --stdin killall -e openconnect')
        self.layout_buttons.itemAt(0).widget().setEnabled(True)  # Conectar
        self.layout_form.itemAt(8).widget().setEnabled(True)  # Servidor
        self.layout_form.itemAt(9).widget().setEnabled(True)  # Certificado
        self.layout_form.itemAt(10).widget().setEnabled(True)  # Usuário
        self.layout_form.itemAt(11).widget().setEnabled(True)  # Senha
        self.layout_form.itemAt(12).widget().setEnabled(True)  # Checkbox Salvar senha
        self.layout_form.itemAt(13).widget().setEnabled(True)  # Salvar
        self.layout_form.itemAt(1).widget().setEnabled(True)  # Combobox

        self.layout_buttons.itemAt(1).widget().setEnabled(False)  # Reconectar
        self.layout_buttons.itemAt(2).widget().setEnabled(False)  # Desconectar

        menu_actions = self.menu.actions()
        menu_actions[1].setEnabled(True)  # Conectar
        menu_actions[2].setEnabled(False)  # Reconectar
        menu_actions[3].setEnabled(False)  # Desconectar

    def show_window(self) -> None:
        '''
        Function to show the window
        '''
        self.setVisible(True)
        self.activateWindow()

    def closeEvent(self, event) -> None:
        '''
        Function called when the window is closed

        Args:
            event (): event
        '''
        reply = QMessageBox.question(self, 'Sair', 'Deseja sair?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.system(f'echo "{self.sudopsw}" | sudo --stdin killall -e openconnect')
        else:
            event.ignore()

    def hideEvent(self, event) -> None:
        '''
        Function called when the window is hidden

        Args:
            event: event
        '''
        self.setVisible(False)

    def sudo_psw(self) -> None:
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

    def connect_buttons(self) -> None:
        '''
        Function to connect the buttons to their respective functions
        '''
        btn_save = self.layout_form.itemAt(13).widget()
        btn_save.clicked.connect(self.save)

        btn_connect = self.layout_buttons.itemAt(0).widget()
        btn_connect.clicked.connect(self.connect_server)

        btn_reconnect = self.layout_buttons.itemAt(1).widget()
        btn_reconnect.clicked.connect(self.reconnect_server)

        btn_disconnect = self.layout_buttons.itemAt(2).widget()
        btn_disconnect.clicked.connect(self.disconnect_server)

        cb_user = self.layout_form.itemAt(1).widget()
        cb_user.currentIndexChanged.connect(self.cb_change)

    def cb_change(self) -> None:
        '''
        Function to change the information in the form when the user changes
        '''
        cb_user = self.layout_form.itemAt(1).widget()
        if cb_user.currentIndex() == 0:
            self.layout_form.itemAt(8).widget().setText('')  # Servidor
            self.layout_form.itemAt(9).widget().setText('')  # Certificado
            self.layout_form.itemAt(10).widget().setText('')  # Usuário
            self.layout_form.itemAt(11).widget().setText('')  # Senha
            return

        infos = self.database.select_user(cb_user.currentText())
        self.layout_form.itemAt(8).widget().setText(infos[0][0])
        self.layout_form.itemAt(9).widget().setText(infos[0][1])
        self.layout_form.itemAt(10).widget().setText(infos[0][2])
        self.layout_form.itemAt(11).widget().setText(infos[0][3])

    def cb_add(self, user: str) -> None:
        '''
        Function to add a user to the combobox

        Args:
            user (str): user to be added
        '''
        cb_user = self.layout_form.itemAt(1).widget()
        cb_user.addItem(user)
        cb_user.setCurrentIndex(cb_user.findText(user))

    def load_last_user(self) -> None:
        '''
        Function to load the last user used in the application
        '''
        last_user = self.database.select_last_user()
        cb_user = self.layout_form.itemAt(1).widget()
        if len(last_user) > 0:
            cb_user.setCurrentIndex(cb_user.findText(last_user[0][0]))

    def alert(self, text: str) -> None:
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

    def valid_fields(self, operation: str, fields: list) -> bool:
        '''
        Function to verify if the fields are valid

        Args:
            operation (str): operation to be done

        Returns:
            bool: True if the fields are valid, False otherwise
        '''

        valid = (fields[0].text() == '' or fields[1].text() == '' or fields[2].text() == ''
                 or (fields[3].text() == '' and (fields[4] or operation == 'connect')))

        if valid:
            self.alert('Preencha todos os campos!')
            if fields[0].text() == '':
                fields[0].setFocus()
            elif fields[1].text() == '':
                fields[1].setFocus()
            elif fields[2].text() == '':
                fields[2].setFocus()
            elif fields[3].text() == '' and (fields[4] or operation == 'connect'):
                fields[3].setFocus()
            return False

        return True

    def verify_openconnect(self) -> None:
        '''
        Function to verify if openconnect is installed
        '''
        try:
            check_output('openconnect --version', shell=True)
        except CalledProcessError:
            QMessageBox.critical(self, 'OpenConnect', 'Openconnect não está instalado! Por favor instale e tente novamente.')
            exit()


if __name__ == '__main__':
    pyconnect = PyConnect()
    pyconnect.verify_openconnect()
    pyconnect.window_combobox()
    pyconnect.window_form()
    pyconnect.window_buttons()
    pyconnect.window_layout()
    pyconnect.connect_buttons()
    pyconnect.show()
    pyconnect.sudo_psw()
    pyconnect.tray_icon()
    pyconnect.load_last_user()
    pyconnect.app.exec_()
