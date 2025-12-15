import sys
import os

# Zakładamy, że struktura katalogów to:
# /projekt
#   /service
#       __init__.py
#       travelbot_service.py
#   main.py
#   .env

from service.travelbot_service import TravelBotService


def main():
    # 1. PEŁNY MOCK DANYCH (symulacja wejścia z formularza na froncie)
    mock_frontend_data = {
        "destination": "Tokio, Japonia",
        "budget": "Wysoki",
        "recreation_type": "Kultura i Technologie",
        "interests": ["Anime", "Sushi", "Świątynie", "Gadżety", "Retro Gaming"],
        "date_range": "10-20 Październik",
        "travelers_count": 2,
        "diet": "Brak alergii, lubimy ostre jedzenie, chcemy spróbować Fugu",
        "additional_info": "Chcemy zobaczyć dzielnicę Akihabara w nocy oraz odwiedzić teamLab Planets."
    }

    print("Inicjalizacja serwisu...")
    service = TravelBotService()

    # ==========================================
    # KROK 1: Generowanie Planu
    # ==========================================
    print("\n--- [1] Generowanie planu podróży... ---")
    trip_plan = service.generate_trip_plan(mock_frontend_data)

    if "error" in trip_plan:
        print(f"Błąd: {trip_plan['error']}")
        return

    # Wyświetlenie fragmentu planu dla weryfikacji
    print(f"Sukces! Wygenerowano plan dla: {trip_plan.get('destination')}")

    itinerary = trip_plan.get('itinerary', [])
    print(f"Liczba dni w planie: {len(itinerary)}")

    if itinerary:
        # Obsługa różnych struktur (czasem model zwraca słownik zamiast listy)
        first_day = itinerary[0] if isinstance(itinerary, list) else list(itinerary.values())[0]
        theme = first_day.get('theme', 'Brak tematu') if isinstance(first_day, dict) else str(first_day)
        print("Przykładowy dzień 1:", theme)
    else:
        print("Brak szczegółów planu (itinerary).")

    # ==========================================
    # KROK 2: Symulacja Czatu
    # ==========================================
    print("\n--- [2] Symulacja Czatu z Botem ---")

    # Historia czatu (na początku pusta)
    chat_history = []

    # Lista pytań, które użytkownik mógłby zadać w interfejsie czatu
    pytania_testowe = [
        "Czy uwzględniłeś w planie teamLab Planets?",
        "Jaki jest dress code do restauracji z Fugu?",
        "Możesz zamienić atrakcje z dnia 3 na coś bardziej relaksującego?"
    ]

    for pytanie in pytania_testowe:
        print(f"\nUżytkownik: {pytanie}")

        # Wywołanie serwisu
        odpowiedz = service.chat_about_plan(trip_plan, chat_history, pytanie)

        print(f"Bot: {odpowiedz}")

        # Aktualizacja historii (niezbędne dla flow)
        chat_history.append({"role": "user", "content": pytanie})
        chat_history.append({"role": "assistant", "content": odpowiedz})

    # ==========================================
    # KROK 3: Zapis do PDF
    # ==========================================
    print("\n--- [3] Generowanie pliku PDF ---")
    plik_pdf = "Plan_Tokio_Full.pdf"

    # Przekazujemy pełny obiekt planu do generatora PDF
    sciezka = service.save_plan_to_pdf(trip_plan, plik_pdf)

    if sciezka:
        print(f"Gotowe! Plik zapisano pod ścieżką: {sciezka}")
    else:
        print("Nie udało się zapisać pliku PDF.")


if __name__ == "__main__":
    main()