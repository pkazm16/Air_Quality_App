# Instrukcja do kodu aplikacji monitorującej jakość powietrza Air Quality App
### Aplikacja została napisana w języku Python przy użyciu frameworku Flask do monitorowania jakości powietrza. Pozwala na pobieranie danych z serwisu REST API publikowanych bezpłatnie przez Główny Inspektorat Ochrony Środowiska, a także generowanie wykresu prezentującego jakość powietrza na podstawie indeksów jakości powietrza.
#### Wymagania systemowe:
Przed uruchomieniem aplikacji upewnij się, że masz zainstalowane poniższe
biblioteki Pythona:
* Flask
* requests
* sqlite3
* matplotlib
* pandas
* geopy

Dodatkowo do przeprowadzenia testów użyto biblioteki unittest.

#### Możesz je zainstalować za pomocą menedżera pakietów pip, wpisując w konsoli poniższą komendę:
pip install module_name
#### Pobieranie aplikacji:
Możesz pobrać projekt bezpośrednio ze strony GitHub i otworzyć go w
PyCharm, wykonując poniższe kroki:
1. Znajdź przycisk &quot;Code&quot; na stronie repozytorium. Kliknij na ten
przycisk.
2. Wybierz opcję &quot;Download ZIP&quot; aby pobrać repozytorium jako skompresowany
plik ZIP.
3. Po pobraniu pliku ZIP, rozpakuj go w wybranym przez Ciebie katalogu na
swoim komputerze.
4. Uruchom PyCharm i wybierz opcję &quot;Open&quot; z ekranu powitalnego lub z menu
&quot;File&quot; (Plik).
5. Przejdź do katalogu, w którym rozpakowałeś plik ZIP zawierający
repozytorium, a następnie wybierz folder projektu.
Gotowe: Teraz powinieneś mieć otwarty projekt pobrany bezpośrednio ze
strony GitHub w PyCharm.
### Uruchomienie aplikacji
1. Uruchom moduł „air_quality”.
2. Po uruchomieniu pojawi się komunikat „Running on http://127.0.0.1:5000”.
Po kliknięciu na adres http aplikacja otworzy się w oknie przeglądarki.
### Opis działania aplikacji
Aplikacja monitorowania jakości powietrza zawiera kilka stron
internetowych, które pozwalają na interakcję z danymi dotyczącymi stacji
monitorujących jakość powietrza.
#### Strona Główna
Użytkownik ma do wyboru trzy opcje:
* #### Strona z listą stacji
Ta strona wyświetla dane o stacjach pomiarowych.
Każda stacja na liście jest wierszem tabeli i zawiera informacje takie jak:
identyfikator stacji, nazwa stacji, szerokość geograficzna, długość
geograficzna, miasto, dzielnica, województwo oraz ulica.

Po kliknięciu na nazwę stacji aplikacja przenosi na stronę z szczegółami
danej stacji.
* #### Strona z szczegółami stacji
Strona ta wyświetla szczegółowe dane o wybranej stacji monitorującej
powietrze na podstawie podanego station_id.
Na stronie wyświetlane są informacje takie jak: nazwa stacji, parametry
pomiarowe, data pomiaru, wartość pomiaru oraz indeksy jakości powietrza dla
różnych zanieczyszczeń.
Wyświetlany jest również wygenerowany wykres słupkowy przedstawiający
jakość powietrza dla poszczególnych zanieczyszczeń na danej stacji.
* #### Strona z mapą z zaznaczonymi stacjami
Strona ta pobiera dane dotyczące stacji monitorujących powietrze i
wyświetla je na mapie.
Po kliknięciu na ikonę stacji na mapie, aplikacja przenosi na stronę z
szczegółami danej stacji.
* #### Strona z pobliskimi stacjami
Strona ta pozwala użytkownikowi na znalezienie pobliskich stacji
monitorujących powietrze na podstawie podanej lokalizacji i promienia.
Po wprowadzeniu lokalizacji i promienia, aplikacja pobiera dane o
wszystkich stacjach i filtruje tylko te, które znajdują się w zadanym
promieniu od podanej lokalizacji.
Znalezione stacje wyświetlane są w tabeli na stronie.
Po kliknięciu na nazwę stacji aplikacja przenosi na stronę z szczegółami
danej stacji.

## Podsumowanie
Aplikacja monitorowania jakości powietrza została napisana w języku Python
z wykorzystaniem frameworka Flask. Pozwala na interaktywne pobieranie
danych z serwisu REST API i wyświetlanie ich na stronach internetowych, a
także generowanie wykresów prezentujących jakość powietrza. Aplikacja
korzysta z bazy danych SQLite do przechowywania danych o stacjach i
indeksach jakości powietrza.
