import os
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                            QPushButton, QLabel, QApplication, QWidget, QScrollArea)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lang.translations import TRANSLATIONS, t

class HelpWindow(QDialog):
    @staticmethod
    def show_help(parent=None, lang='en'):
        dialog = HelpWindow(parent, lang)
        dialog.exec_()
    
    def __init__(self, parent=None, lang='en'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(f"{t('app_title', lang)} - {t('help_menu', lang)}")
        self.setMinimumSize(800, 600)
        self.setWindowModality(Qt.ApplicationModal)
        
        main_layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(t('language_menu', lang))
        lang_layout.addWidget(lang_label)
        
        # Language buttons
        for lang_code in ['en', 'it', 'es', 'pt', 'de', 'fr', 'nl', 'ru', 'zh', 'jp', 'ar']:
            btn = QPushButton(t(lang_code, lang_code))
            btn.clicked.connect(lambda checked, l=lang_code: self.change_language(l))
            lang_layout.addWidget(btn)
        
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)
        
        # Title
        title = QLabel(f"{t('app_title', lang)} - {t('help_menu', lang)}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Help content
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(self.get_help_content())
        main_layout.addWidget(self.browser)
        
        # Close button
        close_btn = QPushButton(t('close', self.lang))
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        self.setLayout(main_layout)
    
    def change_language(self, new_lang):
        self.close()
        HelpWindow.show_help(self.parent(), new_lang)
    
    def get_help_content(self):
        # Get the appropriate help content based on language
        help_content = self.get_localized_help_content()
        
        # Use double curly braces for literal curly braces in the CSS
        return """
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #3498db; margin-top: 20px; }}
                h3 {{ color: #7f8c8d; }}
                ul, ol {{ margin: 10px 0 10px 20px; }}
                li {{ margin: 5px 0; }}
                .note {{ 
                    background-color: #f8f9fa; 
                    padding: 10px 15px;
                    border-left: 4px solid #3498db; 
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                .warning {{ 
                    background-color: #fff3cd; 
                    padding: 10px 15px;
                    border-left: 4px solid #ffc107; 
                    margin: 15px 0;
                    border-radius: 4px;
                }}
                code {{ 
                    background-color: #f8f9fa; 
                    padding: 2px 5px; 
                    border-radius: 3px; 
                    font-family: monospace;
                }}
                a {{ 
                    color: #3498db; 
                    text-decoration: none; 
                }}
                a:hover {{ 
                    text-decoration: underline; 
                }}
                .lang-btn {{ 
                    margin: 2px;
                    padding: 2px 8px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    background: #f8f9fa;
                    cursor: pointer;
                }}
                .lang-btn.active {{ 
                    background: #3498db;
                    color: white;
                    border-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <div class="note">
                <h2>{getting_started}</h2>
                <p>{welcome_message}</p>
            </div>
            
            <h2>{basic_usage}</h2>
            <ul>
                <li>{connect_device_help}</li>
                <li>{send_commands_help}</li>
                <li>{monitor_status_help}</li>
            </ul>
            
            <div class="warning">
                <h3>{need_help}</h3>
                <p>{visit_github} <a href="https://github.com/Nsfr750/Nidec_CommanderCDE">GitHub</a>.</p>
            </div>
            
            {help_content}
        </body>
        </html>
        """.format(
            getting_started=t('getting_started', self.lang),
            welcome_message=t('welcome_message', self.lang),
            basic_usage=t('basic_usage', self.lang),
            connect_device_help=t('connect_device_help', self.lang),
            send_commands_help=t('send_commands_help', self.lang),
            monitor_status_help=t('monitor_status_help', self.lang),
            need_help=t('need_help', self.lang),
            visit_github=t('visit_github', self.lang),
            help_content=help_content
        )
    
    def get_localized_help_content(self):
        """Return help content specific to the current language
        
        Returns:
            str: HTML formatted help content for the current language
        """
        # Help content for all supported languages
        help_texts = {
            'en': """
            <h2>Getting Started</h2>
            <p>Welcome to Nidec Commander CDE! This application allows you to control and monitor Nidec motor drives.</p>
            
            <h3>Connecting to a Drive</h3>
            <ol>
                <li>Select your drive model from the dropdown menu</li>
                <li>Choose the correct COM port from the list</li>
                <li>Set the appropriate baud rate and other connection parameters</li>
                <li>Click 'Connect' to establish communication</li>
            </ol>
            
            <h3>Basic Controls</h3>
            <ul>
                <li>Use the 'Start' and 'Stop' buttons to control the motor</li>
                <li>Adjust the speed using the slider or input field</li>
                <li>Change direction using the direction control buttons</li>
            </ul>
            
            <h3>Monitoring</h3>
            <p>The dashboard displays real-time information about the drive status, including:</p>
            <ul>
                <li>Output frequency</li>
                <li>Output current</li>
                <li>DC bus voltage</li>
                <li>Drive status and fault information</li>
            </ul>
            
            <div class="note">
                <h4>Note</h4>
                <p>Ensure the drive is properly connected and powered before attempting to control it.</p>
            </div>
            """,
            
            'it': """
            <h2>Per iniziare</h2>
            <p>Benvenuto in Nidec Commander CDE! Questa applicazione ti consente di controllare e monitorare gli azionamenti Nidec.</p>
            
            <h3>Connessione all'azionamento</h3>
            <ol>
                <li>Seleziona il modello del tuo azionamento dal menu a discesa</li>
                <li>Scegli la porta COM corretta dall'elenco</li>
                <li>Imposta la velocità di trasmissione e gli altri parametri di connessione</li>
                <li>Fai clic su 'Connetti' per stabilire la comunicazione</li>
            </ol>
            
            <h3>Controlli di base</h3>
            <ul>
                <li>Usa i pulsanti 'Avvia' e 'Ferma' per controllare il motore</li>
                <li>Regola la velocità usando il cursore o il campo di inserimento</li>
                <li>Cambia direzione usando i pulsanti di controllo della direzione</li>
            </ul>
            
            <h3>Monitoraggio</h3>
            <p>La dashboard mostra informazioni in tempo reale sullo stato dell'azionamento, tra cui:</p>
            <ul>
                <li>Frequenza di uscita</li>
                <li>Corrente di uscita</li>
                <li>Tensione del bus CC</li>
                <li>Stato dell'azionamento e informazioni sugli errori</li>
            </ul>
            
            <div class="note">
                <h4>Nota</h4>
                <p>Assicurati che l'azionamento sia correttamente collegato e alimentato prima di tentare di controllarlo.</p>
            </div>
            """,
            
            'es': """
            <h2>Primeros pasos</h2>
            <p>¡Bienvenido a Nidec Commander CDE! Esta aplicación te permite controlar y monitorear los variadores de Nidec.</p>
            
            <h3>Conexión al variador</h3>
            <ol>
                <li>Selecciona tu modelo de variador del menú desplegable</li>
                <li>Elige el puerto COM correcto de la lista</li>
                <li>Configura la velocidad de transmisión y otros parámetros de conexión</li>
                <li>Haz clic en 'Conectar' para establecer la comunicación</li>
            </ol>
            
            <h3>Controles básicos</h3>
            <ul>
                <li>Usa los botones 'Iniciar' y 'Detener' para controlar el motor</li>
                <li>Ajusta la velocidad usando el control deslizante o el campo de entrada</li>
                <li>Cambia la dirección usando los botones de control de dirección</li>
            </ul>
            
            <h3>Monitoreo</h3>
            <p>El panel muestra información en tiempo real sobre el estado del variador, incluyendo:</p>
            <ul>
                <li>Frecuencia de salida</li>
                <li>Corriente de salida</li>
                <li>Tensión del bus de CC</li>
                <li>Estado del variador e información de fallos</li>
            </ul>
            
            <div class="note">
                <h4>Nota</h4>
                <p>Asegúrate de que el variador esté correctamente conectado y alimentado antes de intentar controlarlo.</p>
            </div>
            """,
            
            'pt': """
            <h2>Introdução</h2>
            <p>Bem-vindo ao Nidec Commander CDE! Este aplicativo permite controlar e monitorar acionamentos Nidec.</p>
            
            <h3>Conexão ao acionamento</h3>
            <ol>
                <li>Selecione o modelo do seu acionamento no menu suspenso</li>
                <li>Escolha a porta COM correta na lista</li>
                <li>Defina a taxa de transmissão e outros parâmetros de conexão</li>
                <li>Clique em 'Conectar' para estabelecer a comunicação</li>
            </ol>
            
            <h3>Controles básicos</h3>
            <ul>
                <li>Use os botões 'Iniciar' e 'Parar' para controlar o motor</li>
                <li>Ajuste a velocidade usando o controle deslizante ou o campo de entrada</li>
                <li>Mude a direção usando os botões de controle de direção</li>
            </ul>
            
            <h3>Monitoramento</h3>
            <p>O painel exibe informações em tempo real sobre o status do acionamento, incluindo:</p>
            <ul>
                <li>Frequência de saída</li>
                <li>Corrente de saída</li>
                <li>Tensão do barramento CC</li>
                <li>Status do acionamento e informações de falhas</li>
            </ul>
            
            <div class="note">
                <h4>Nota</h4>
                <p>Certifique-se de que o acionamento esteja corretamente conectado e energizado antes de tentar controlá-lo.</p>
            </div>
            """,
            
            'de': """
            <h2>Erste Schritte</h2>
            <p>Willkommen bei Nidec Commander CDE! Diese Anwendung ermöglicht die Steuerung und Überwachung von Nidec Antrieben.</p>
            
            <h3>Verbindung zum Antrieb</h3>
            <ol>
                <li>Wählen Sie Ihr Antriebsmodell aus dem Dropdown-Menü</li>
                <li>Wählen Sie den richtigen COM-Port aus der Liste</li>
                <li>Stellen Sie die Übertragungsrate und andere Verbindungsparameter ein</li>
                <li>Klicken Sie auf 'Verbinden', um die Kommunikation herzustellen</li>
            </ol>
            
            <h3>Grundlegende Steuerung</h3>
            <ul>
                <li>Verwenden Sie die Schaltflächen 'Start' und 'Stopp', um den Motor zu steuern</li>
                <li>Stellen Sie die Geschwindigkeit mit dem Schieberegler oder dem Eingabefeld ein</li>
                <li>Ändern Sie die Richtung mit den Richtungstasten</li>
            </ul>
            
            <h3>Überwachung</h3>
            <p>Das Dashboard zeigt Echtzeitinformationen zum Antriebsstatus an, einschließlich:</p>
            <ul>
                <li>Ausgangsfrequenz</li>
                <li>Ausgangsstrom</li>
                <li>Gleichspannung</li>
                <li>Antriebsstatus und Fehlerinformationen</li>
            </ul>
            
            <div class="note">
                <h4>Hinweis</h4>
                <p>Stellen Sie sicher, dass der Antrieb ordnungsgemäß angeschlossen und eingeschaltet ist, bevor Sie versuchen, ihn zu steuern.</p>
            </div>
            """,
            
            'fr': """
            <h2>Pour commencer</h2>
            <p>Bienvenue dans Nidec Commander CDE ! Cette application vous permet de commander et de surveiller les variateurs Nidec.</p>
            
            <h3>Connexion au variateur</h3>
            <ol>
                <li>Sélectionnez votre modèle de variateur dans le menu déroulant</li>
                <li>Choisissez le port COM approprié dans la liste</li>
                <li>Définissez la vitesse de transmission et les autres paramètres de connexion</li>
                <li>Cliquez sur 'Connecter' pour établir la communication</li>
            </ol>
            
            <h3>Commandes de base</h3>
            <ul>
                <li>Utilisez les boutons 'Démarrer' et 'Arrêter' pour commander le moteur</li>
                <li>Ajustez la vitesse à l'aide du curseur ou du champ de saisie</li>
                <li>Changez le sens de rotation à l'aide des boutons de commande de direction</li>
            </ul>
            
            <h3>Surveillance</h3>
            <p>Le tableau de bord affiche en temps réel des informations sur l'état du variateur, notamment :</p>
            <ul>
                <li>Fréquence de sortie</li>
                <li>Courant de sortie</li>
                <li>Tension du bus continu</li>
                <li>État du variateur et informations sur les défauts</li>
            </ul>
            
            <div class="note">
                <h4>Remarque</h4>
                <p>Assurez-vous que le variateur est correctement connecté et alimenté avant de tenter de le commander.</p>
            </div>
            """,
            
            'nl': """
            <h2>Eerste stappen</h2>
            <p>Welkom bij Nidec Commander CDE! Deze applicatie laat u toe om Nidec aandrijvingen te bedienen en te bewaken.</p>
            
            <h3>Verbinding maken met de aandrijving</h3>
            <ol>
                <li>Selecteer uw aandrijvingsmodel uit het dropdown-menu</li>
                <li>Kies de juiste COM-poort uit de lijst</li>
                <li>Stel de transmissiesnelheid en andere verbindingparameters in</li>
                <li>Klik op 'Verbinden' om de communicatie tot stand te brengen</li>
            </ol>
            
            <h3>Basisbediening</h3>
            <ul>
                <li>Gebruik de knoppen 'Start' en 'Stop' om de motor te bedienen</li>
                <li>Pas de snelheid aan met de schuifregelaar of het invoerveld</li>
                <li>Wijzig de richting met de richtingstoetsen</li>
            </ul>
            
            <h3>Bewaking</h3>
            <p>Het dashboard toont real-time informatie over de status van de aandrijving, inclusief:</p>
            <ul>
                <li>Uitgangsfrequentie</li>
                <li>Uitgangsstroom</li>
                <li>Gelijkspanning</li>
                <li>Aandrijvingsstatus en foutinformatie</li>
            </ul>
            
            <div class="note">
                <h4>Opmerking</h4>
                <p>Zorg ervoor dat de aandrijving correct is aangesloten en ingeschakeld voordat u deze probeert te bedienen.</p>
            </div>
            """,
            
            'ru': """
            <h2>Первые шаги</h2>
            <p>Добро пожаловать в Nidec Commander CDE! Это приложение позволяет управлять и контролировать привод Nidec.</p>
            
            <h3>Подключение к приводу</h3>
            <ol>
                <li>Выберите модель привода из выпадающего меню</li>
                <li>Выберите правильный порт COM из списка</li>
                <li>Установите скорость передачи и другие параметры подключения</li>
                <li>Нажмите 'Подключить', чтобы установить связь</li>
            </ol>
            
            <h3>Базовое управление</h3>
            <ul>
                <li>Используйте кнопки 'Старт' и 'Стоп', чтобы управлять двигателем</li>
                <li>Регулируйте скорость с помощью ползунка или поля ввода</li>
                <li>Измените направление с помощью кнопок управления направлением</li>
            </ul>
            
            <h3>Мониторинг</h3>
            <p>Панель управления отображает информацию в режиме реального времени о состоянии привода, включая:</p>
            <ul>
                <li>Частота выхода</li>
                <li>Ток выхода</li>
                <li>Напряжение шины постоянного тока</li>
                <li>Состояние привода и информация об ошибках</li>
            </ul>
            
            <div class="note">
                <h4>Примечание</h4>
                <p>Убедитесь, что привод правильно подключен и включен перед тем, как попытаться управлять им.</p>
            </div>
            """,
            
            'zh': """
            <h2>开始使用</h2>
            <p>欢迎使用 Nidec Commander CDE！此应用程序允许您控制和监控 Nidec 驱动器。</p>
            
            <h3>连接驱动器</h3>
            <ol>
                <li>从下拉菜单中选择驱动器模型</li>
                <li>从列表中选择正确的 COM 端口</li>
                <li>设置传输速率和其他连接参数</li>
                <li>单击“连接”以建立通信</li>
            </ol>
            
            <h3>基本控制</h3>
            <ul>
                <li>使用“启动”和“停止”按钮控制电机</li>
                <li>使用滑块或输入字段调整速度</li>
                <li>使用方向控制按钮更改方向</li>
            </ul>
            
            <h3>监控</h3>
            <p>仪表板显示驱动器状态的实时信息，包括：</p>
            <ul>
                <li>输出频率</li>
                <li>输出电流</li>
                <li>直流总线电压</li>
                <li>驱动器状态和故障信息</li>
            </ul>
            
            <div class="note">
                <h4>注意</h4>
                <p>在尝试控制驱动器之前，请确保驱动器正确连接并通电。</p>
            </div>
            """,
            
            'jp': """
            <h2>はじめに</h2>
            <p>Nidec Commander CDEへようこそ！このアプリケーションは、Nidecのドライブを制御および監視することができます。</p>
            
            <h3>ドライブへの接続</h3>
            <ol>
                <li>ドロップダウンメニューからドライブモデルを選択してください</li>
                <li>リストから正しいCOMポートを選択してください</li>
                <li>送信速度とその他の接続パラメータを設定してください</li>
                <li>通信を確立するには、「接続」をクリックしてください</li>
            </ol>
            
            <h3>基本的な操作</h3>
            <ul>
                <li>「スタート」と「ストップ」のボタンを使用してモーターを制御します</li>
                <li>スライダーまたは入力フィールドを使用して速度を調整します</li>
                <li>方向制御ボタンを使用して方向を変更します</li>
            </ul>
            
            <h3>モニタリング</h3>
            <p>ダッシュボードは、ドライブの状態に関するリアルタイム情報を表示します。これには、以下のものがあります。</p>
            <ul>
                <li>出力周波数</li>
                <li>出力電流</li>
                <li>直流バスの電圧</li>
                <li>ドライブの状態とエラー情報</li>
            </ul>
            
            <div class="note">
                <h4>注意</h4>
                <p>ドライブを制御しようとする前に、ドライブが正しく接続され、電源が入っていることを確認してください。</p>
            </div>
            """,
            
            'ar': """
            <h2>البداية</h2>
            <p>مرحباً بك في Nidec Commander CDE! هذا التطبيق يسمح لك بالتحكم في محركات Nidec ومراقبتها.</p>
            
            <h3>اتصال المحرك</h3>
            <ol>
                <li>حدد نموذج المحرك من القائمة المنسدلة</li>
                <li>اختر المنفذ الصحيح من القائمة</li>
                <li>اضبط معدل الإرسال و معلمات الاتصال الأخرى</li>
                <li>انقر على "اتصال" لإنشاء الاتصال</li>
            </ol>
            
            <h3>التحكم الأساسي</h3>
            <ul>
                <li>استخدم أزرار "تشغيل" و "إيقاف" للتحكم في المحرك</li>
                <li>اضبط السرعة باستخدام الشريط أو حقل الإدخال</li>
                <li>غير الاتجاه باستخدام أزرار التحكم في الاتجاه</li>
            </ul>
            
            <h3>مراقبة</h3>
            <p>لوحة التحكم تعرض معلومات في الوقت الفعلي حول حالة المحرك، بما في ذلك:</p>
            <ul>
                <li>تردد الإخراج</li>
                <li>تيار الإخراج</li>
                <li>جهد خط التوصيل المستمر</li>
                <li>حالة المحرك ومعلومات الأخطاء</li>
            </ul>
            
            <div class="note">
                <h4>ملاحظة</h4>
                <p>تأكد من أن المحرك متصل بشكل صحيح ومشغل قبل محاولة التحكم به.</p>
            </div>
            """,
        }
        
        # For languages not yet translated, use English as fallback
        return help_texts.get(self.lang, help_texts['en'])
