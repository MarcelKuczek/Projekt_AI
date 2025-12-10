import json
import os
from typing import Dict, Any
from openai import OpenAI


class TravelBotService:
    def __init__(self):
        # Inicjalizacja klienta. Klucz API powinien być w zmiennych środowiskowych (.env)
        # dla bezpieczeństwa, ale w celach testowych możesz go podać tutaj.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Brak klucza API OPENAI_API_KEY w zmiennych środowiskowych.")

        self.client = OpenAI(api_key=api_key)

    def generate_trip_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Główna metoda orkiestrująca (Fasada).
        Przyjmuje surowe dane z formularza i zwraca gotowy JSON z planem.
        """
        # 1. Przygotowanie promptu (Data Transformation)
        system_prompt = self._get_system_instruction()
        user_prompt = self._construct_user_prompt(user_data)

        # 2. Komunikacja z API (External Service Call)
        raw_response = self._call_openai_api(system_prompt, user_prompt)

        # 3. Parsowanie i walidacja (Response Processing)
        parsed_plan = self._parse_response(raw_response)

        return parsed_plan

    def _get_system_instruction(self) -> str:
        """
        Zwraca instrukcję systemową definiującą zachowanie i format wyjściowy modelu.
        """
        return """
        Jesteś ekspertem planowania podróży. Twoim zadaniem jest przygotowanie szczegółowego planu wyjazdu.

        WYMAGANY FORMAT ODPOWIEDZI TO CZYSTY JSON (bez markdownów ```json).
        Struktura JSON ma wyglądać tak:
        {
            "trip_title": "Tytuł wycieczki",
            "summary": "Krótko o klimacie wyjazdu",
            "currency": "Waluta",
            "daily_itinerary": [
                {
                    "day_number": 1,
                    "date": "Data (jeśli podana) lub Dzień 1",
                    "focus": "Główny cel dnia",
                    "activities": [
                        {
                            "time_of_day": "Rano/Południe/Wieczór lub godzina",
                            "description": "Szczegóły aktywności",
                            "tip": "Praktyczna wskazówka (np. dojazd, bilety)"
                        }
                    ]
                }
            ]
        }
        """

    def _construct_user_prompt(self, data: Dict[str, Any]) -> str:
        """
        Formatuje dane wejściowe użytkownika do stringa zrozumiałego dla modelu.
        """
        # Możesz tutaj dodać logikę walidacji, czy pola obowiązkowe istnieją
        prompt = f"""
        Proszę o zaplanowanie podróży na podstawie poniższych danych:

        - Kierunek: {data.get('destination', 'Nieznany')}
        - Termin: {data.get('date_range', 'Nieokreślony')}
        - Ilość osób: {data.get('travelers_count', 1)}
        - Budżet: {data.get('budget', 'Standardowy')}
        - Typ rekreacji: {data.get('recreation_type', 'Mieszany')}
        - Zainteresowania: {', '.join(data.get('interests', []))}

        Dodatkowe informacje:
        - Dieta: {data.get('diet', 'Brak')}
        - Uwagi: {data.get('additional_info', 'Brak')}

        Przygotuj plan idealnie dopasowany do tych kryteriów.
        """
        return prompt

    def _call_openai_api(self, system_msg: str, user_msg: str) -> str:
        """
        Wysyła zapytanie do modelu OpenAI. 
        Używa response_format={"type": "json_object"} dla pewności struktury.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # lub gpt-3.5-turbo-0125 (tańszy, ale obsługuje JSON mode)
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"},  # Kluczowe dla backendu
                temperature=0.7  # Kreatywność
            )
            return response.choices[0].message.content
        except Exception as e:
            # Tutaj warto dodać logowanie błędu
            print(f"Błąd komunikacji z OpenAI: {e}")
            # Zwracamy pusty JSON lub błąd, by frontend nie "wybuchł"
            return json.dumps({"error": "Nie udało się wygenerować planu. Spróbuj ponownie."})

    def _parse_response(self, raw_json_str: str) -> Dict[str, Any]:
        """
        Konwertuje string JSON z API na słownik Pythona.
        """
        try:
            return json.loads(raw_json_str)
        except json.JSONDecodeError:
            return {
                "error": "Błąd parsowania danych",
                "raw_content": raw_json_str
            }