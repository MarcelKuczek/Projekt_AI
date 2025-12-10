import os
import json

from service.travelbot_service import TravelBotService

os.environ["OPENAI_API_KEY"] = "TU_WKLEJ_SWOJ_KLUCZ_OPENAI"


def main():
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

    try:
        service = TravelBotService()
        result_json = service.generate_trip_plan(mock_frontend_data)

        print(json.dumps(result_json, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()