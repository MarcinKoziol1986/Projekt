# Projekt Symulatora meczu

"""Stwórz fantazyjną drużynę równą rzeczywistej (Flask/CLI)
 Aplikacja używa bazy danych z tabeli
 https://www.kaggle.com/aayushmishra1512/fifa-2021-complete-player-data
 Uzytkownik wybiera jeden z realnych klubów piłkarskich, aplikacja generuje dla niego
 fikcyjną drużynę przeciwną z którą mecz byłby najbardziej wyrównany
 (każda pozycja jest obsadzona, poszczególne formacje mają jak najbliższe sobie
  sumy overall rating)"""
  
  plik main.py pobiera z pliku csv informacje tworzy w folderze projektu instance pliko nazwie fifa.db
nastepnie uruchamia URL index i kolejno można wybierać drużyne z dostepnej puli.
nastepnie url teams pokazuje sklad druzyny po czym nastepuje symulacja meczu na postawie podbnienstw silowych druzyn 
