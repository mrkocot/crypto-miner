from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt6.QtGui import QPixmap, QFont
import sys
import os
import subprocess


os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "0"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"     

class GameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Miner")
        self.setFixedSize(1280, 1024)
        # Ekran powitalny
        self.welcome_screen()

    def welcome_screen(self):
        """Pokazuje ekran powitalny z obrazkiem i napisem"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Wyświetlenie obrazka powitalnego
        self.image_label = QLabel(self)

        # Ładowanie obrazka i sprawdzanie błędów
        pixmap = QPixmap('engine/assets/menu.png')
        if pixmap.isNull():
            print("Błąd: Obrazek nie został załadowany. Sprawdź ścieżkę.")
        else:
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.image_label)

        # Dodajemy obrazek do layoutu na samym dole
        layout.addWidget(self.image_label)

        # Ruchomy napis
        self.text_label = QLabel(">>> Kliknij aby zacząć grać <<<", self)
        self.text_label.setFont(QFont("Courier", 30))  
        self.text_label.setStyleSheet("color: #FFD700")  # Kolor złoty
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ustawiamy pozycję napisu na górze
        layout.insertWidget(0, self.text_label)

        # Tworzymy animację do powiększania i pomniejszania napisu
        self.font_size = 30  # Początkowy rozmiar czcionki
        self.growing = True  # Określenie kierunku animacji
        self.text_timer = QTimer(self)
        self.text_timer.timeout.connect(self.animate_text)
        self.text_timer.start(100)  # Animacja co 1 sekundę

        # Oczekiwanie na kliknięcie, aby przejść do gry
        self.text_label.mousePressEvent = self.start_game 
        self.image_label.mousePressEvent = self.start_game

    def animate_text(self):
        """Animacja zmieniająca rozmiar czcionki napisu"""
        if self.growing:
            self.font_size += 1
            if self.font_size >= 40:
                self.growing = False
        else:
            self.font_size -= 1
            if self.font_size <= 30:
                self.growing = True
        
        # Ustawienie rozmiaru czcionki
        self.text_label.setFont(QFont("Courier", self.font_size))
    def start_game(self, event):
        """Rozpoczynanie gry po kliknięciu"""
        self.text_label.setText("> Rozpoczynanie gry... <")  # Zmieniamy tekst na informację o starcie
        self.text_timer.stop()  # Zatrzymanie animacji czcionki

        # Teraz uruchamiamy grę, ukrywając ekran powitalny
        self.image_label.hide()
        self.text_label.hide()

        # Uruchomienie gry
        self.game_screen()

    def game_screen(self):

        # Ustawienie tła (tlo.png)
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap('engine/assets/terminal.png'))  # Ścieżka do tła
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setScaledContents(True)  # Tło wypełni okno
        self.background_label.setGeometry(self.rect())  # Dopasowanie tła do rozmiaru okna
        self.background_label.show()

        # Tworzenie terminala w czarnej przestrzeni na tle
        self.console_output = QLabel(self)
        self.console_output.setStyleSheet("background-color: black; color: #7CB9E8; font-family: monospace; padding: 10px;")
        self.console_output.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Przekazywanie informacji z terminala
        self.run_cli()

    
        # Ustawienie terminala wewnątrz tła
        self.console_output.setGeometry(40, 130, 1200, 420)  # Pozycja i rozmiar w obrębie czarnej przestrzeni
        self.console_output.show()


    def run_cli(self):
        """Uruchamia cli.py jako moduł Pythona"""
        try:
            # Ustalamy pełną ścieżkę do folderu 'engine'
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            engine_dir = os.path.join(project_root, 'engine')

            # Uruchamiamy cli.py jako moduł Pythona
            process = subprocess.Popen(
                [sys.executable, '-m', 'engine.cli'],  # Uruchamiamy cli.py jako moduł
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )

            # Odbieramy wynik
            stdout, stderr = process.communicate()

            if stderr:
                print("Błąd podczas uruchamiania cli.py:")
                print(stderr)

            # Przekształcamy wyjście na tekst
            output = stdout if stdout else "CLI wyświetlił pusty wynik"

            # Wyświetlanie wyniku w terminalu
            self.console_output.setText(output)

        except Exception as e:
            print(f"Błąd przy uruchamianiu CLI: {e}")
            self.console_output.setText("Wystąpił błąd przy uruchamianiu CLI.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameGUI()
    window.show()
    sys.exit(app.exec())
