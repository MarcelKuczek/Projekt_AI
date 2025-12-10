import os
from service.travelbot_service import TravelBotService

# Ustawienie klucza API (w produkcji użyj pliku .env)
os.environ["OPENAI_API_KEY"] = "TU_WKLEJ_SWOJ_KLUCZ_OPENAI"


def main():
    # 1. Symulacja danych, które przyjdą z Reacta
    mock_frontend_data = {
        "destination": "Tokio, Japonia",
        "budget": "Wysoki",
        "recreation_type": "Kultura i Technologie",
        "interests": ["Anime", "Sushi", "Świątynie", "Gadżety"],
        "date_range": "10-20 Październik",
        "travelers_count": 2,
        "diet": "Brak alergii, lubimy ostre",
        "additional_info": "Chcemy zobaczyć dzielnicę Akihabara w nocy."
    }

    print("--- Generowanie planu podróży... ---")

    # 2. Uruchomienie serwisu
    try:
        service = TravelBotService()
        result_json = service.generate_trip_plan(mock_frontend_data)

        # 3. Wyświetlenie wyniku (to normalnie pójdzie jako response HTTP do Reacta)
        import json
        print(json.dumps(result_json, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    main()