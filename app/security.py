"""
Moduł odpowiedzialny za bezpieczne hashowanie i weryfikację haseł użytkowników.

Wykorzystuje bibliotekę `passlib` oraz algorytm `bcrypt`, który jest obecnie
jednym z najbezpieczniejszych standardów przechowywania haseł. Funkcje w tym
module służą do:
- generowania kryptograficznie bezpiecznych hashy haseł,
- sprawdzania poprawności hasła podanego przez użytkownika,
- abstrakcji nad konfiguracją Passlib, aby reszta aplikacji nie musiała
  zajmować się szczegółami implementacyjnymi.

Zmienne:
pwd_context : CryptContext
    Konfiguracja Passlib z algorytmem bcrypt. Ustawienie `deprecated="auto"`
    pozwala automatycznie oznaczać starsze hashe jako przestarzałe.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
        Generuje bezpieczny hash hasła przy użyciu algorytmu bcrypt.
        Funkcja powinna być używana podczas rejestracji użytkownika lub zmiany hasła.
        Zwracany hash zawiera wszystkie informacje potrzebne do późniejszej weryfikacji.
        Parametry:
            password: Hasło w postaci zwykłego tekstu (plaintext).
        Zwraca:
            Hash hasła jako string, gotowy do zapisania w bazie danych.
    """
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """
        Weryfikuje, czy podane hasło odpowiada zapisanemu hashowi.
        Funkcja porównuje plaintext hasło z jego zahashowaną wersją, korzystając
        z mechanizmów Passlib, które automatycznie obsługują:
        - porównanie odporne na timing attacks,
        - różne wersje hashy,
        - aktualizację przestarzałych hashy (jeśli konfiguracja to umożliwia).
        Parametry:
            password: Hasło podane przez użytkownika (plaintext).
            password_hash: Hash zapisany w bazie danych.
        Zwraca:
            True jeśli hasło jest poprawne, False w przeciwnym razie.
    """
    return pwd_context.verify(password, password_hash)
