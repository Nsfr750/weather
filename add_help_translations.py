import json
import os

# Define the translations for each language
TRANSLATIONS = {
    "ar": {
        "help": "مساعدة",
        "help_menu": "&مساعدة",
        "help_menu_item": "مساعدة",
        "help_tip": "عرض وثائق المساعدة",
        "help_title": "مساعدة تطبيق الطقس",
        "help_close_btn": "إغلاق",
        "help_usage_tab": "طريقة الاستخدام",
        "help_features_tab": "الميزات",
        "help_tips_tab": "نصائح",
        "select_language": "اختر اللغة",
        "help_usage_text": "<h2>كيفية استخدام تطبيق الطقس</h2>\n<p>1. <b>ابحث عن موقع</b> عن طريق الكتابة في شريط البحث والضغط على Enter أو النقر على زر البحث.</p>\n<p>2. <b>عرض معلومات الطقس</b> بما في ذلك درجة الحرارة والرطوبة وسرعة الرياح والمزيد.</p>\n<p>3. <b>أضف المواقع إلى المفضلة</b> بالنقر على أيقونة النجمة.</p>\n<p>4. <b>قم بتبديل الوحدات</b> (مئوية/فهرنهايت) في الإعدادات.</p>",
        "help_features_text": "<h2>الميزات</h2>\n<ul>\n  <li>حالة الطقس الحالية</li>\n  <li>تنبؤات لمدة 5 أيام</li>\n  <li>معلومات طقس مفصلة</li>\n  <li>دعم متعدد اللغات</li>\n  <li>سمات فاتحة وداكنة</li>\n  <li>خرائط الطقس والرادار</li>\n  <li>تصغير إلى صينية النظام</li>\n</ul>",
        "help_tips_text": "<h2>نصائح</h2>\n<ul>\n  <li>اضغط F5 أو انقر على زر التحديث لتحديث بيانات الطقس</li>\n  <li>استخدم اختصار لوحة المفاتيح Ctrl+Q للخروج من التطبيق</li>\n  <li>انقر بزر الماوس الأيمن على أيقونة صينية النظام للوصول السريع</li>\n  <li>قم بتمكين التحديثات التلقائية في الإعدادات للحصول على أحدث إصدار دائمًا</li>\n  <li>اتصل بالدعم إذا واجهت أي مشاكل</li>\n</ul>"
    },
    "de": {
        "help": "Hilfe",
        "help_menu": "&Hilfe",
        "help_menu_item": "Hilfe",
        "help_tip": "Hilfedokumentation anzeigen",
        "help_title": "Wetter-App-Hilfe",
        "help_close_btn": "Schließen",
        "help_usage_tab": "Verwendung",
        "help_features_tab": "Funktionen",
        "help_tips_tab": "Tipps",
        "select_language": "Sprache auswählen",
        "help_usage_text": "<h2>So verwenden Sie die Wetter-App</h2>\n<p>1. <b>Nach einem Ort suchen</b>, indem Sie in die Suchleiste tippen und die Eingabetaste drücken oder auf die Schaltfläche Suchen klicken.</p>\n<p>2. <b>Wetterinformationen anzeigen</b> einschließlich Temperatur, Luftfeuchtigkeit, Windgeschwindigkeit und mehr.</p>\n<p>3. <b>Fügen Sie Orte zu Favoriten hinzu</b>, indem Sie auf das Sternsymbol klicken.</p>\n<p>4. <b>Wechseln Sie zwischen Einheiten</b> (Celsius/Fahrenheit) in den Einstellungen.</p>",
        "help_features_text": "<h2>Funktionen</h2>\n<ul>\n  <li>Aktuelle Wetterbedingungen</li>\n  <li>5-Tage-Vorhersage</li>\n  <li>Detaillierte Wetterinformationen</li>\n  <li>Mehrsprachige Unterstützung</li>\n  <li>Helle und dunkle Designs</li>\n  <li>Wetterkarten und Radar</li>\n  <li>In die Systemleiste minimieren</li>\n</ul>",
        "help_tips_text": "<h2>Tipps</h2>\n<ul>\n  <li>Drücken Sie F5 oder klicken Sie auf die Schaltfläche Aktualisieren, um die Wetterdaten zu aktualisieren</li>\n  <li>Verwenden Sie die Tastenkombination Strg+Q, um die Anwendung zu beenden</li>\n  <li>Klicken Sie mit der rechten Maustaste auf das Symbol in der Systemleiste für schnellen Zugriff</li>\n  <li>Aktivieren Sie automatische Updates in den Einstellungen, um immer die neueste Version zu haben</li>\n  <li>Kontaktieren Sie den Support, wenn Sie Probleme haben</li>\n</ul>"
    },
    "es": {
        "help": "Ayuda",
        "help_menu": "&Ayuda",
        "help_menu_item": "Ayuda",
        "help_tip": "Mostrar documentación de ayuda",
        "help_title": "Ayuda de la aplicación del tiempo",
        "help_close_btn": "Cerrar",
        "help_usage_tab": "Uso",
        "help_features_tab": "Características",
        "help_tips_tab": "Consejos",
        "select_language": "Seleccionar idioma",
        "help_usage_text": "<h2>Cómo usar la aplicación del tiempo</h2>\n<p>1. <b>Busca una ubicación</b> escribiendo en la barra de búsqueda y presionando Enter o haciendo clic en el botón de búsqueda.</p>\n<p>2. <b>Consulta la información del tiempo</b> incluyendo temperatura, humedad, velocidad del viento y más.</p>\n<p>3. <b>Añade ubicaciones a favoritos</b> haciendo clic en el icono de estrella.</p>\n<p>4. <b>Cambia entre unidades</b> (Celsius/Fahrenheit) en la configuración.</p>",
        "help_features_text": "<h2>Características</h2>\n<ul>\n  <li>Condiciones meteorológicas actuales</li>\n  <li>Pronóstico a 5 días</li>\n  <li>Información meteorológica detallada</li>\n  <li>Soporte para múltiples idiomas</li>\n  <li>Temas claros y oscuros</li>\n  <li>Mapas del tiempo y radar</li>\n  <li>Minimizar a la bandeja del sistema</li>\n</ul>",
        "help_tips_text": "<h2>Consejos</h2>\n<ul>\n  <li>Presiona F5 o haz clic en el botón de actualizar para actualizar los datos del tiempo</li>\n  <li>Usa el atajo de teclado Ctrl+Q para salir de la aplicación</li>\n  <li>Haz clic derecho en el icono de la bandeja del sistema para acceso rápido</li>\n  <li>Habilita las actualizaciones automáticas en la configuración para tener siempre la última versión</li>\n  <li>Contacta con el soporte si encuentras algún problema</li>\n</ul>"
    },
    "fr": {
        "help": "Aide",
        "help_menu": "&Aide",
        "help_menu_item": "Aide",
        "help_tip": "Afficher la documentation d'aide",
        "help_title": "Aide de l'application Météo",
        "help_close_btn": "Fermer",
        "help_usage_tab": "Utilisation",
        "help_features_tab": "Fonctionnalités",
        "help_tips_tab": "Conseils",
        "select_language": "Sélectionner la langue",
        "help_usage_text": "<h2>Comment utiliser l'application Météo</h2>\n<p>1. <b>Recherchez un lieu</b> en tapant dans la barre de recherche et en appuyant sur Entrée ou en cliquant sur le bouton de recherche.</p>\n<p>2. <b>Consultez les informations météorologiques</b> y compris la température, l'humidité, la vitesse du vent et plus encore.</p>\n<p>3. <b>Ajoutez des lieux aux favoris</b> en cliquant sur l'icône en forme d'étoile.</p>\n<p>4. <b>Changez d'unités</b> (Celsius/Fahrenheit) dans les paramètres.</p>",
        "help_features_text": "<h2>Fonctionnalités</h2>\n<ul>\n  <li>Conditions météorologiques actuelles</li>\n  <li>Prévisions sur 5 jours</li>\n  <li>Informations météorologiques détaillées</li>\n  <li>Support multilingue</li>\n  <li>Thèmes clair et sombre</li>\n  <li>Cartes météo et radar</li>\n  <li>Réduire dans la zone de notification</li>\n</ul>",
        "help_tips_text": "<h2>Conseils</h2>\n<ul>\n  <li>Appuyez sur F5 ou cliquez sur le bouton d'actualisation pour mettre à jour les données météo</li>\n  <li>Utilisez le raccourci clavier Ctrl+Q pour quitter l'application</li>\n  <li>Faites un clic droit sur l'icône de la zone de notification pour un accès rapide</li>\n  <li>Activez les mises à jour automatiques dans les paramètres pour toujours avoir la dernière version</li>\n  <li>Contactez le support si vous rencontrez des problèmes</li>\n</ul>"
    },
    "he": {
        "help": "עזרה",
        "help_menu": "&עזרה",
        "help_menu_item": "עזרה",
        "help_tip": "הצג תיעוד עזרה",
        "help_title": "עזרה ליישום מזג האוויר",
        "help_close_btn": "סגור",
        "help_usage_tab": "שימוש",
        "help_features_tab": "תכונות",
        "help_tips_tab": "טיפים",
        "select_language": "בחר שפה",
        "help_usage_text": "<h2>כיצד להשתמש ביישום מזג האוויר</h2><p>1. <b>חפש מיקום</b> על ידי הקלדה בשורת החיפוש ולחיצה על Enter או לחיצה על כפתור החיפוש.</p><p>2. <b>צפה במידע מזג האוויר</b> כולל טמפרטורה, לחות, מהירות רוח ועוד.</p><p>3. <b>הוסף מיקומים למועדפים</b> על ידי לחיצה על סמל הכוכב.</p><p>4. <b>החלף בין יחידות</b> (צלזיוס/פרנהייט) בהגדרות.</p>",
        "help_features_text": "<h2>תכונות</h2><ul><li>תנאי מזג אוויר נוכחיים</li><li>תחזית ל-5 ימים</li><li>מידע מפורט על מזג האוויר</li><li>תמיכה במספר שפות</li><li>ערכות נושא בהירות וכהה</li><li>מפות מזג אוויר ומכ"ם</li><li>מזעור לסרגל המשימות</li></ul>",
        "help_tips_text": "<h2>טיפים</h2><ul><li>לחץ F5 או לחץ על כפתור הרענון כדי לעדכן את נתוני מזג האוויר</li><li>השתמש בקיצור המקשים Ctrl+Q כדי לצאת מהאפליקציה</li><li>לחץ לחיצה ימנית על סמל סרגל הכלים לגישה מהירה</li><li>הפעל עדכונים אוטומטיים בהגדרות כדי לקבל תמיד את הגרסה העדכנית ביותר</li><li>צור קשר עם התמיכה אם אתה נתקל בבעיות</li></ul>"
    },
    "hu": {
        "help": "Súgó",
        "help_menu": "&Súgó",
        "help_menu_item": "Súgó",
        "help_tip": "Súgó megjelenítése",
        "help_title": "Időjárás alkalmazás súgó",
        "help_close_btn": "Bezárás",
        "help_usage_tab": "Használat",
        "help_features_tab": "Funkciók",
        "help_tips_tab": "Tippek",
        "select_language": "Nyelv kiválasztása",
        "help_usage_text": "<h2>Az Időjárás alkalmazás használata</h2>\n<p>1. <b>Keressen egy helyet</b> a keresősorba írással és az Enter megnyomásával vagy a keresés gombra kattintással.</p>\n<p>2. <b>Tekintse meg az időjárási információkat</b>, beleértve a hőmérsékletet, páratartalmat, szélsebességet és egyebeket.</p>\n<p>3. <b>Adjon hozzá helyeket a kedvencekhez</b> a csillag ikonra kattintva.</p>\n<p>4. <b>Váltson mértékegységek között</b> (Celsius/Fahrenheit) a beállításokban.</p>",
        "help_features_text": "<h2>Funkciók</h2>\n<ul>\n  <li>Aktuális időjárási viszonyok</li>\n  <li>5 napos előrejelzés</li>\n  <li>Részletes időjárási információk</li>\n  <li>Többnyelvű támogatás</li>\n  <li>Világos és sötét téma</li>\n  <li>Időjárási térképek és radar</li>\n  <li>Minimalizálás a tálcára</li>\n</ul>",
        "help_tips_text": "<h2>Tippek</h2>\n<ul>\n  <li>Nyomja meg az F5-öt vagy kattintson a frissítés gombra az időjárási adatok frissítéséhez</li>\n  <li>Használja a Ctrl+Q billentyűkombinációt az alkalmazásból való kilépéshez</li>\n  <li>Jobb kattintás a tálca ikonjára a gyors eléréshez</li>\n  <li>Engedélyezze az automatikus frissítéseket a beállításokban, hogy mindig a legújabb verziót használja</li>\n  <li>Vegye fel a kapcsolatot az ügyfélszolgálattal, ha problémája van</li>\n</ul>"
    },
    "ja": {
        "help": "ヘルプ",
        "help_menu": "ヘルプ(&H)",
        "help_menu_item": "ヘルプ",
        "help_tip": "ヘルプドキュメントを表示",
        "help_title": "天気アプリのヘルプ",
        "help_close_btn": "閉じる",
        "help_usage_tab": "使い方",
        "help_features_tab": "機能",
        "help_tips_tab": "ヒント",
        "select_language": "言語を選択",
        "help_usage_text": "<h2>天気アプリの使い方</h2>\n<p>1. 検索バーに場所を入力し、Enterキーを押すか検索ボタンをクリックして<b>場所を検索</b>します。</p>\n<p>2. 気温、湿度、風速などの<b>天気情報を表示</b>します。</p>\n<p>3. 星アイコンをクリックして<b>お気に入りに場所を追加</b>します。</p>\n<p>4. 設定で<b>単位を切り替え</b>ます（摂氏/華氏）。</p>",
        "help_features_text": "<h2>機能</h2>\n<ul>\n  <li>現在の天気状況</li>\n  <li>5日間の予報</li>\n  <li>詳細な天気情報</li>\n  <li>多言語サポート</li>\n  <li>ライト/ダークテーマ</li>\n  <li>天気図とレーダー</li>\n  <li>システムトレイに最小化</li>\n</ul>",
        "help_tips_text": "<h2>ヒント</h2>\n<ul>\n  <li>F5キーを押すか更新ボタンをクリックして天気データを更新します</li>\n  <li>Ctrl+Qキーを押してアプリケーションを終了します</li>\n  <li>システムトレイアイコンを右クリックしてクイックアクセス</li>\n  <li>設定で自動更新を有効にして常に最新バージョンを使用します</li>\n  <li>問題が発生した場合はサポートにお問い合わせください</li>\n</ul>"
    },
    "ko": {
        "help": "도움말",
        "help_menu": "도움말(&H)",
        "help_menu_item": "도움말",
        "help_tip": "도움말 문서 표시",
        "help_title": "날씨 앱 도움말",
        "help_close_btn": "닫기",
        "help_usage_tab": "사용 방법",
        "help_features_tab": "기능",
        "help_tips_tab": "팁",
        "select_language": "언어 선택",
        "help_usage_text": "<h2>날씨 앱 사용 방법</h2>\n<p>1. 검색창에 위치를 입력하고 Enter 키를 누르거나 검색 버튼을 클릭하여 <b>위치를 검색</b>합니다.</p>\n<p>2. 기온, 습도, 풍속 등을 포함한 <b>날씨 정보를 확인</b>합니다.</p>\n<p>3. 별 아이콘을 클릭하여 <b>위치를 즐겨찾기에 추가</b>합니다.</p>\n<p>4. 설정에서 <b>단위를 전환</b>합니다(섭씨/화씨).</p>",
        "help_features_text": "<h2>기능</h2>\n<ul>\n  <li>현재 날씨 상태</li>\n  <li>5일간의 일기 예보</li>\n  <li>상세한 날씨 정보</li>\n  <li>다국어 지원</li>\n  <li>라이트/다크 테마</li>\n  <li>날씨 지도 및 레이더</li>\n  <li>시스템 트레이로 최소화</li>\n</ul>",
        "help_tips_text": "<h2>팁</h2>\n<ul>\n  <li>F5 키를 누르거나 새로 고침 버튼을 클릭하여 날씨 데이터를 업데이트하세요</li>\n  <li>Ctrl+Q 단축키를 사용하여 애플리케이션을 종료하세요</li>\n  <li>시스템 트레이 아이콘을 마우스 오른쪽 버튼으로 클릭하여 빠르게 접근하세요</li>\n  <li>설정에서 자동 업데이트를 활성화하여 항상 최신 버전을 유지하세요</li>\n  <li>문제가 발생하면 지원팀에 문의하세요</li>\n</ul>"
    },
    "nl": {
        "help": "Help",
        "help_menu": "&Help",
        "help_menu_item": "Help",
        "help_tip": "Toon hulpdocumentatie",
        "help_title": "Weer App Help",
        "help_close_btn": "Sluiten",
        "help_usage_tab": "Gebruik",
        "help_features_tab": "Functies",
        "help_tips_tab": "Tips",
        "select_language": "Selecteer taal",
        "help_usage_text": "<h2>Hoe gebruik je de Weer App</h2>\n<p>1. <b>Zoek een locatie</b> door te typen in de zoekbalk en op Enter te drukken of op de zoekknop te klikken.</p>\n<p>2. <b>Bekijk weersinformatie</b> inclusief temperatuur, luchtvochtigheid, windsnelheid en meer.</p>\n<p>3. <b>Voeg locaties toe aan favorieten</b> door op het sterpictogram te klikken.</p>\n<p>4. <b>Schakel tussen eenheden</b> (Celsius/Fahrenheit) in de instellingen.</p>",
        "help_features_text": "<h2>Functies</h2>\n<ul>\n  <li>Huidige weersomstandigheden</li>\n  <li>5-daagse verwachting</li>\n  <li>Gedetailleerde weersinformatie</li>\n  <li>Meertalige ondersteuning</li>\n  <li>Lichte en donkere thema's</li>\n  <li>Weerkaarten en radar</li>\n  <li>Minimaliseren naar systeemvak</li>\n</ul>",
        "help_tips_text": "<h2>Tips</h2>\n<ul>\n  <li>Druk op F5 of klik op de vernieuwknop om de weersgegevens bij te werken</li>\n  <li>Gebruik de sneltoets Ctrl+Q om de applicatie te sluiten</li>\n  <li>Klik met de rechtermuisknop op het pictogram in het systeemvak voor snelkoppelingen</li>\n  <li>Schakel automatische updates in de instellingen in om altijd de nieuwste versie te hebben</li>\n  <li>Neem contact op met de ondersteuning als u problemen ondervindt</li>\n</ul>"
    },
    "pl": {
        "help": "Pomoc",
        "help_menu": "&Pomoc",
        "help_menu_item": "Pomoc",
        "help_tip": "Pokaż dokumentację pomocy",
        "help_title": "Pomoc - Aplikacja Pogodowa",
        "help_close_btn": "Zamknij",
        "help_usage_tab": "Użycie",
        "help_features_tab": "Funkcje",
        "help_tips_tab": "Wskazówki",
        "select_language": "Wybierz język",
        "help_usage_text": "<h2>Jak korzystać z aplikacji Pogodowej</h2>\n<p>1. <b>Wyszukaj lokalizację</b> wpisując nazwę w pasku wyszukiwania i naciskając Enter lub klikając przycisk wyszukiwania.</p>\n<p>2. <b>Wyświetl informacje o pogodzie</b> w tym temperaturę, wilgotność, prędkość wiatru i inne.</p>\n<p>3. <b>Dodaj lokalizacje do ulubionych</b> klikając ikonę gwiazdki.</p>\n<p>4. <b>Zmień jednostki</b> (Celsjusz/Fahrenheit) w ustawieniach.</p>",
        "help_features_text": "<h2>Funkcje</h2>\n<ul>\n  <li>Aktualne warunki pogodowe</li>\n  <li>Prognoza na 5 dni</li>\n  <li>Szczegółowe informacje pogodowe</li>\n  <li>Obsługa wielu języków</li>\n  <li>Jasny i ciemny motyw</li>\n  <li>Mapy pogodowe i radar</li>\n  <li>Minimalizuj do zasobnika systemowego</li>\n</ul>",
        "help_tips_text": "<h2>Wskazówki</h2>\n<ul>\n  <li>Naciśnij F5 lub kliknij przycisk odświeżania, aby zaktualizować dane pogodowe</li>\n  <li>Użyj skrótu klawiszowego Ctrl+Q, aby zamknąć aplikację</li>\n  <li>Kliknij prawym przyciskiem myszy ikonę w zasobniku systemowym, aby uzyskać szybki dostęp</li>\n  <li>Włącz automatyczne aktualizacje w ustawieniach, aby zawsze mieć najnowszą wersję</li>\n  <li>Skontaktuj się z pomocą techniczną, jeśli napotkasz problemy</li>\n</ul>"
    },
    "pt": {
        "help": "Ajuda",
        "help_menu": "A&juda",
        "help_menu_item": "Ajuda",
        "help_tip": "Mostrar documentação de ajuda",
        "help_title": "Ajuda do Aplicativo de Clima",
        "help_close_btn": "Fechar",
        "help_usage_tab": "Uso",
        "help_features_tab": "Recursos",
        "help_tips_tab": "Dicas",
        "select_language": "Selecionar idioma",
        "help_usage_text": "<h2>Como usar o Aplicativo de Clima</h2>\n<p>1. <b>Pesquise um local</b> digitando na barra de pesquisa e pressionando Enter ou clicando no botão de pesquisa.</p>\n<p>2. <b>Visualize as informações meteorológicas</b> incluindo temperatura, umidade, velocidade do vento e mais.</p>\n<p>3. <b>Adicione locais aos favoritos</b> clicando no ícone de estrela.</p>\n<p>4. <b>Altere as unidades</b> (Celsius/Fahrenheit) nas configurações.</p>",
        "help_features_text": "<h2>Recursos</h2>\n<ul>\n  <li>Condições meteorológicas atuais</li>\n  <li>Previsão para 5 dias</li>\n  <li>Informações meteorológicas detalhadas</li>\n  <li>Suporte a vários idiomas</li>\n  <li>Temas claro e escuro</li>\n  <li>Mapas meteorológicos e radar</li>\n  <li>Minimizar para a bandeja do sistema</li>\n</ul>",
        "help_tips_text": "<h2>Dicas</h2>\n<ul>\n  <li>Pressione F5 ou clique no botão de atualizar para atualizar os dados meteorológicos</li>\n  <li>Use o atalho de teclado Ctrl+Q para sair do aplicativo</li>\n  <li>Clique com o botão direito no ícone da bandeja do sistema para acesso rápido</li>\n  <li>Ative as atualizações automáticas nas configurações para sempre ter a versão mais recente</li>\n  <li>Entre em contato com o suporte se encontrar problemas</li>\n</ul>"
    },
    "ru": {
        "help": "Справка",
        "help_menu": "&Справка",
        "help_menu_item": "Справка",
        "help_tip": "Показать справочную документацию",
        "help_title": "Справка по приложению Погода",
        "help_close_btn": "Закрыть",
        "help_usage_tab": "Использование",
        "help_features_tab": "Функции",
        "help_tips_tab": "Советы",
        "select_language": "Выбрать язык",
        "help_usage_text": "<h2>Как использовать приложение Погода</h2>\n<p>1. <b>Найдите местоположение</b>, введя его в строку поиска и нажав Enter или кнопку поиска.</p>\n<p>2. <b>Просматривайте информацию о погоде</b>, включая температуру, влажность, скорость ветра и другое.</p>\n<p>3. <b>Добавляйте местоположения в избранное</b>, нажимая на значок звезды.</p>\n<p>4. <b>Изменяйте единицы измерения</b> (Цельсий/Фаренгейт) в настройках.</p>",
        "help_features_text": "<h2>Функции</h2>\n<ul>\n  <li>Текущие погодные условия</li>\n  <li>Прогноз на 5 дней</li>\n  <li>Подробная информация о погоде</li>\n  <li>Поддержка нескольких языков</li>\n  <li>Светлая и темная темы</li>\n  <li>Погодные карты и радар</li>\n  <li>Сворачивание в системный трей</li>\n</ul>",
        "help_tips_text": "<h2>Советы</h2>\n<ul>\n  <li>Нажмите F5 или кнопку обновления для обновления данных о погоде</li>\n  <li>Используйте сочетание клавиш Ctrl+Q для выхода из приложения</li>\n  <li>Щелкните правой кнопкой мыши по иконке в системном трее для быстрого доступа</li>\n  <li>Включите автоматические обновления в настройках, чтобы всегда иметь последнюю версию</li>\n  <li>Обратитесь в службу поддержки, если у вас возникли проблемы</li>\n</ul>"
    },
    "tr": {
        "help": "Yardım",
        "help_menu": "&Yardım",
        "help_menu_item": "Yardım",
        "help_tip": "Yardım belgelerini göster",
        "help_title": "Hava Durumu Uygulaması Yardımı",
        "help_close_btn": "Kapat",
        "help_usage_tab": "Kullanım",
        "help_features_tab": "Özellikler",
        "help_tips_tab": "İpuçları",
        "select_language": "Dil seçin",
        "help_usage_text": "<h2>Hava Durumu Uygulaması Nasıl Kullanılır</h2>\n<p>1. Arama çubuğuna yazıp Enter tuşuna basarak veya arama düğmesine tıklayarak <b>bir konum arayın</b>.</p>\n<p>2. Sıcaklık, nem, rüzgar hızı ve daha fazlasını içeren <b>hava durumu bilgilerini görüntüleyin</b>.</p>\n<p>3. Yıldız simgesine tıklayarak <b>konumları sık kullanılanlara ekleyin</b>.</p>\n<p>4. Ayarlardan <b>birimleri değiştirin</b> (Celsius/Fahrenheit).</p>",
        "help_features_text": "<h2>Özellikler</h2>\n<ul>\n  <li>Güncel hava durumu</li>\n  <li>5 günlük tahmin</li>\n  <li>Detaylı hava durumu bilgileri</li>\n  <li>Çoklu dil desteği</li>\n  <li>Açık ve koyu tema</li>\n  <li>Hava durumu haritaları ve radar</li>\n  <li>Sistem tepsisine küçült</li>\n</ul>",
        "help_tips_text": "<h2>İpuçları</h2>\n<ul>\n  <li>Hava durumu verilerini güncellemek için F5'e basın veya yenile düğmesine tıklayın</li>\n  <li>Uygulamadan çıkmak için Ctrl+Q klavye kısayolunu kullanın</li>\n  <li>Hızlı erişim için sistem tepsi simgesine sağ tıklayın</li>\n  <li>Her zaman en son sürüme sahip olmak için ayarlardan otomatik güncellemeleri etkinleştirin</li>\n  <li>Sorun yaşarsanız destek ekibiyle iletişime geçin</li>\n</ul>"
    },
    "zh": {
        "help": "帮助",
        "help_menu": "帮助(&H)",
        "help_menu_item": "帮助",
        "help_tip": "显示帮助文档",
        "help_title": "天气应用帮助",
        "help_close_btn": "关闭",
        "help_usage_tab": "使用",
        "help_features_tab": "功能",
        "help_tips_tab": "提示",
        "select_language": "选择语言",
        "help_usage_text": "<h2>如何使用天气应用</h2>\n<p>1. 在搜索栏中输入地点并按Enter或点击搜索按钮<b>搜索地点</b>。</p>\n<p>2. <b>查看天气信息</b>，包括温度、湿度、风速等。</p>\n<p>3. 点击星形图标<b>将地点添加到收藏夹</b>。</p>\n<p>4. 在设置中<b>切换单位</b>（摄氏度/华氏度）。</p>",
        "help_features_text": "<h2>功能</h2>\n<ul>\n  <li>当前天气状况</li>\n  <li>5天预报</li>\n  <li>详细的天气信息</li>\n  <li>多语言支持</li>\n  <li>浅色和深色主题</li>\n  <li>天气图和雷达</li>\n  <li>最小化到系统托盘</li>\n</ul>",
        "help_tips_text": "<h2>提示</h2>\n<ul>\n  <li>按F5或点击刷新按钮更新天气数据</li>\n  <li>使用Ctrl+Q快捷键退出应用程序</li>\n  <li>右键点击系统托盘图标快速访问</li>\n  <li>在设置中启用自动更新以始终使用最新版本</li>\n  <li>如遇问题请联系支持</li>\n</ul>"
    }
}

def add_translations():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(script_dir, 'lang', 'translations')
    
    # Process each language file
    for lang_code, translations in TRANSLATIONS.items():
        file_path = os.path.join(translations_dir, f"{lang_code}.json")
        
        # Skip if the language file doesn't exist
        if not os.path.exists(file_path):
            print(f"Skipping {lang_code}: File not found")
            continue
            
        try:
            # Read the existing translations
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add or update the help-related translations
            updated = False
            for key, value in translations.items():
                if key not in data or data[key] == "":
                    data[key] = value
                    updated = True
            
            # Save the updated translations if there were any changes
            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
                print(f"Updated {lang_code} translations")
            else:
                print(f"No updates needed for {lang_code}")
                
        except Exception as e:
            print(f"Error processing {lang_code}: {str(e)}")

if __name__ == "__main__":
    add_translations()
