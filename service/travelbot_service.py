import json
import os
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TravelBotService:
    def __init__(self):
        # 1. Pobieranie uniwersalnych zmiennych
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")

        self.model_name = os.getenv("LLM_MODEL", "gpt-4o")

        if not api_key:
            raise ValueError("Brak zmiennej LLM_API_KEY w pliku .env")

        # 2. Inicjalizacja klienta
        # Biblioteka nadal nazywa się "OpenAI", bo to standard branżowy dla interfejsów,
        # ale dzięki base_url połączy się z DeepSeek/Groq/czymkolwiek.
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        print(f"TravelBot połączony z: {base_url or 'OpenAI Default'} | Model: {self.model_name}")

    def generate_trip_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = self._get_system_instruction()
        user_prompt = self._construct_user_prompt(user_data)

        raw_response = self._call_llm_api(system_prompt, user_prompt)

        return self._parse_response(raw_response)

    def _get_system_instruction(self) -> str:
        # Treść promptu bez zmian
        return """
        Jesteś ekspertem planowania podróży.
        WYMAGANY FORMAT ODPOWIEDZI TO CZYSTY JSON.
        NIE UŻYWAJ ```json PRZED I PO WYGENEROWANYM JSONIE Z ODPOWIEDZI
        ... (reszta promptu systemowego) ...
        """

    def _construct_user_prompt(self, data: Dict[str, Any]) -> str:
        # Treść promptu bez zmian
        return f"""
        Zaplanuj podróż do: {data.get('destination')}
        ... (reszta promptu użytkownika) ...
        """

    def _call_llm_api(self, system_msg: str, user_msg: str) -> str:
        """
        Wysyła zapytanie do skonfigurowanego providera LLM.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,  # <--- Używamy modelu z .env
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                # UWAGA: Nie każdy model (np. starsze lokalne) obsługuje 'json_object'.
                # DeepSeek i GPT-4 to obsługują. Jeśli używasz egzotycznego modelu,
                # może być konieczne usunięcie response_format.
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Błąd LLM API: {e}")
            # Zwracamy pusty JSON w przypadku błędu, żeby aplikacja nie padła
            return json.dumps({"error": "Błąd generowania planu", "details": str(e)})

    def _parse_response(self, raw_json_str: str) -> Dict[str, Any]:
        """
        Konwertuje string JSON z API na słownik Pythona.
        Zawiera mechanizm czyszczący Markdown (```json ... ```).
        """
        try:
            # 1. Próba bezpośredniego parsowania (sytuacja idealna)
            return json.loads(raw_json_str)
        except json.JSONDecodeError:
            # 2. Jeśli się nie uda, próbujemy "wyczyścić" string
            try:
                # Szukamy pierwszej klamry otwierającej '{' i ostatniej zamykającej '}'
                # To ignoruje wszystko co model napisał "przed" i "po" JSONie
                start_index = raw_json_str.find('{')
                end_index = raw_json_str.rfind('}')

                if start_index != -1 and end_index != -1:
                    clean_json_str = raw_json_str[start_index: end_index + 1]
                    return json.loads(clean_json_str)
                else:
                    raise ValueError("Nie znaleziono obiektu JSON w odpowiedzi")

            except Exception as e:
                # 3. Jeśli nadal błąd, zwracamy info o błędzie
                return {
                    "error": "Błąd parsowania danych",
                    "details": str(e),
                    "raw_content": raw_json_str
                }