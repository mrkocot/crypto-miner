from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QThread, pyqtSignal, QUrl, QPoint, QEasingCurve
from PyQt6.QtGui import QPixmap, QFont, QTextCursor, QTransform
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import sys
import os
import subprocess
import time
import random

os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "0"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"     

class CLIThread(QThread):
    output_signal = pyqtSignal(str)  # Sygnalizowanie nowych danych do wyświetlenia w GUI

    def __init__(self):
        super().__init__()
        self.process = None
        self.running = False

    def run(self):
        """Uruchamia CLI w osobnym wątku i obsługuje interakcję z terminalem"""
        try:
            # Ustalamy pełną ścieżkę do folderu 'engine'
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            engine_dir = os.path.join(project_root, 'engine')

            # Uruchamiamy cli.py jako moduł Pythona
            self.process = subprocess.Popen(
                [sys.executable, '-m', 'engine.cli'],  # Uruchamiamy cli.py jako moduł
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )

            self.running = True
            
            while self.running:
                # Odczytujemy dane z wyjścia stdout
                output = self.process.stdout.readline()
                if output:
                    self.output_signal.emit(output)  # Wysyłanie danych do GUI
                time.sleep(0.1)  # Małe opóźnienie, aby uniknąć wysokiego zużycia CPU

        except Exception as e:
            self.output_signal.emit(f"Błąd przy uruchamianiu CLI: {e}")
        
    def send_input(self, command: str):
        """Wysyła dane do stdin procesu"""
        if self.process:
            self.process.stdin.write(command + '\n')
            self.process.stdin.flush()  # Wymusza zapis do stdin natychmiast
            time.sleep(0.1)  # Małe opóźnienie na bezpieczeństwo

    def stop(self):
        """Zatrzymuje proces"""
        if self.process:
            self.process.terminate()
        self.running = False

class GameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Miner")
        self.setFixedSize(1280, 1024)
        self.cli_thread = CLIThread()
        self.cli_thread.output_signal.connect(self.update_console_output) 
        self.cli_thread.start() 
        self.media_player = None
        self.is_game_screen_active = False
        self.is_lewa_strona = False

        self.cat_timer = QTimer(self)  
        self.cat_timer.timeout.connect(self.show_cat)
        self.cat_timer.start(8000)  
        self.current_cat = None 
        self.cat_images = [
            "engine/assets/cat1.png",
            "engine/assets/cat2.png",
            "engine/assets/cat3.png",
            "engine/assets/cat4.png",
            "engine/assets/cat5.png",
            "engine/assets/cat6.png",
            "engine/assets/cat7.png",
            "engine/assets/cat8.png",
            "engine/assets/cat9.png",
            "engine/assets/cat10.png"]
        # Ekran powitalny
        self.welcome_screen()

    def show_cat(self):
        """Funkcja do wyświetlania kota na ekranie gry z losowym obrazkiem"""
        if not self.is_game_screen_active:
            return  

        if self.current_cat: 
            return

        # Wybór losowego kota z listy obrazków
        cat_image = random.choice(self.cat_images)

        
        self.current_cat = QLabel(self)
        pixmap = QPixmap(cat_image)

        if pixmap.isNull():
            print(f"Nie udało się załadować obrazka kota: {cat_image}")
            return

        self.current_cat.setPixmap(pixmap)
        self.current_cat.setFixedSize(pixmap.width() // 4, pixmap.height() // 4)  
        self.current_cat.setScaledContents(True)
        self.current_cat.setAlignment(Qt.AlignmentFlag.AlignCenter)

        window_width = 1280
        window_height = 1024

        x_position = (window_width) * 2
        y_position = ((window_height) * 2)

        self.current_cat.move(x_position, y_position)

        self.current_cat.show()
        self.current_cat.raise_()

        # DEBUGLINE print(f"Pozycja kota: {self.current_cat.pos()}")  # Sprawdzamy pozycję kota po ustawieniu

        # Opóźniamy animację, by GUI mogło się zaktualizować
        QTimer.singleShot(100, self.animate_cat)  # 100ms opóźnienie przed rozpoczęciem animacji



    def animate_cat(self):
        """Animacja kota z wykorzystaniem czasu zamiast delta"""
        if not self.current_cat:
            print("Brak kota na ekranie. Animacja nie może się rozpocząć.")
            return

        # Wybór kierunku animacji (z lewej na prawą lub z prawej na lewą)
        if random.choice([True, False]): 
            start_position = QPoint(1280, 780)  # Prawa strona
            end_position = QPoint(-800, 780)   # Lewa strona
            self.current_cat.move(start_position)
        else:
            start_position = QPoint(-200, 780)    # Lewa strona
            end_position = QPoint(1280, 780)   # Prawa strona
            self.current_cat.move(start_position)
            transform = QTransform()
            transform.scale(-1, 1)  # Odbicie w poziomie (oś X)
            self.current_cat.setPixmap(self.current_cat.pixmap().transformed(transform))
            self.is_lewa_strona = True

        #DEBUGLINE print(f"Pozycja początkowa: {start_position}")
        #DEBUGLINE print(f"Pozycja końcowa: {end_position}")

        animation_duration = 10000  
        steps = 2000  
        step_time = animation_duration / steps  

        start_time = 0  # Czas początkowy

        def move_step():
            nonlocal start_time

            progress = min(start_time / animation_duration, 1.0)

            # Interpolacja liniowa w celu obliczenia pozycji
            new_x = start_position.x() + progress * (end_position.x() - start_position.x())
            new_y = start_position.y() + progress * (end_position.y() - start_position.y())

            self.current_cat.move(int(new_x), int(new_y))

            if progress >= 1.0:
                #DEBUGLINE print("Animacja zakończona!")
                self.current_cat.move(end_position)  # Ustawiamy kota dokładnie na końcowej pozycji
                self.timer.stop()  # Zatrzymujemy timer
                if self.is_lewa_strona:
                    transform.scale(-1, 1)  # Odbicie w poziomie (oś X)
                    self.current_cat.setPixmap(self.current_cat.pixmap().transformed(transform))
                    self.is_lewa_strona = False
                # Usuwanie kota po zakończeniu animacji
                self.current_cat.deleteLater()  # Usuń kota z widoku
                self.current_cat = None  # Resetujemy zmienną kota
                return

            # Zwiększamy czas trwania animacji
            start_time += step_time

        # Ustawiamy timer, który będzie wykonywał krok co odpowiedni czas
        self.timer = QTimer(self)
        self.timer.timeout.connect(move_step)
        self.timer.start(int(step_time))  # Konwertujemy step_time na int

        
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
        self.play_music()
        self.game_screen()


    def play_music(self):
        """Odtwarzanie dwóch piosenek na zmianę w pętli"""
        # Ścieżki do plików muzycznych
        self.music_files = [
            "engine/assets/music1.flac",  # Pierwsza piosenka
            "engine/assets/music2.flac"   # Druga piosenka
        ]

        # Sprawdzenie, czy pliki istnieją
        for music_file in self.music_files:
            if not os.path.exists(music_file):
                print(f"Błąd: Nie znaleziono pliku muzycznego {music_file}")
                return

        # Tworzenie odtwarzacza i ustawienia
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Ustawienie początkowego utworu
        self.current_track = 0
        self.media_player.setSource(QUrl.fromLocalFile(self.music_files[self.current_track]))

        # Ustawienie głośności
        self.audio_output.setVolume(0.2)  # 20% głośności

        # Po zakończeniu odtwarzania jednego utworu, przechodzimy do kolejnego
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        # Rozpoczęcie odtwarzania
        self.media_player.play()
        #DEBUGLINE print("Rozpoczęto odtwarzanie muzyki na zmianę.")

    def on_media_status_changed(self, status):
        """Metoda wywoływana po zakończeniu odtwarzania utworu"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Przechodzimy do kolejnego utworu w liście
            self.current_track = (self.current_track + 1) % len(self.music_files)
            
            # Ustawienie nowego źródła muzyki
            self.media_player.setSource(QUrl.fromLocalFile(self.music_files[self.current_track]))
            
            # Rozpoczęcie odtwarzania nowego utworu
            self.media_player.play()

    def game_screen(self):

        self.is_game_screen_active = True  # Ustawienie flagi, że ekran gry jest aktywny


        # Ustawienie tła (tlo.png)
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap('engine/assets/terminal.png'))  # Ścieżka do tła
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setScaledContents(True)  # Tło wypełni okno
        self.background_label.setGeometry(self.rect())  # Dopasowanie tła do rozmiaru okna
        self.background_label.show()

        # Tworzenie terminala w czarnej przestrzeni na tle
        self.console_output = QTextEdit(self)
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: #7CB9E8; font-family: monospace; font-size: 30px; padding: 10px;")
        self.console_output.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Tworzenie pola do wprowadzania komend
        self.console_input = QLineEdit(self)
        self.console_input.setStyleSheet("background-color: black; color: #7CB9E8; font-family: monospace; font-size: 20px; padding: 5px;")
        self.console_input.setGeometry(40, 570, 1200, 30)  # Pozycja pola w GUI
        self.console_input.setFocus()  # Ustawia fokus na pole tekstowe
        self.console_input.setPlaceholderText("Wpisz komendę...")
        self.console_input.show()

        if hasattr(self, 'console_output'):
            self.console_output.append("Oto twój terminal, tutaj możesz zarządzać światem kryptowalut\nCryptoMiner~ >")

        # Ustawienie terminala wewnątrz tła
        self.console_output.setGeometry(40, 130, 1200, 420)  # Pozycja i rozmiar w obrębie czarnej przestrzeni
        self.console_output.show()
        self.show_cat()

    def update_console_output(self, output: str):
        """Aktualizuje wyjście konsoli w GUI, usuwając nadmiarowe odstępy."""
        output = output.strip()  # Usuwa nadmiarowe białe znaki, w tym \n na początku i końcu
        if output:  # Dodaje tekst tylko, jeśli nie jest pusty po usunięciu białych znaków
            try:
                self.console_output.append(output)
                self.console_output.moveCursor(QTextCursor.MoveOperation.End)
            except AttributeError:
                pass

    def send_command_to_cli(self, command: str):
        """Funkcja umożliwiająca wysyłanie komend do CLI"""
        self.cli_thread.send_input(command)

    def keyPressEvent(self, event):
        """Override key press event to capture the Enter key."""
        key = event.key()
        if key == 16777220:  # Kod klawisza Enter (ASCII dla Return / Enter w PyQt6)
            print("Enter key pressed")
            self.run_cli_command()  # Zastąp własną funkcją
    
    def run_cli_command(self):
        """Metoda do uruchamiania komendy w CLI po naciśnięciu Enter."""
        command = self.console_input.text()  # Pobierz tekst z pola wejściowego
        print(f"Wysyłanie komendy: {command}")
        self.cli_thread.send_input(command)  # Wysyłanie komendy do CLI
        self.console_input.clear()  # Czyści pole wejściowe po wysłaniu komendy

        def closeEvent(self, event):
            """Zatrzymuje wątek i zamyka aplikację"""
            self.cli_thread.stop()
            super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameGUI()
    window.show()
    sys.exit(app.exec())
