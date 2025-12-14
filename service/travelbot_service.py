import json
import os
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from fpdf import FPDF

# Wymuszenie załadowania pliku .env
load_dotenv(find_dotenv())


class TravelBotService:
    def __init__(self):
        # 1. Pobieranie zmiennych (LLM_... zgodnie z Twoim screenem)
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        self.model_name = os.getenv("LLM_MODEL", "gpt-4o")

        # Zabezpieczenie przed brakiem klucza
        if not api_key:
            print("⚠️ OSTRZEŻENIE: Nie znaleziono LLM_API_KEY w pliku .env.")
            api_key = "missing-key"  # Dummy key, aby klient się zainicjalizował

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        print(f"TravelBot Service: Konfiguracja załadowana (Model: {self.model_name})")

    # --- 1. GENEROWANIE PLANU (Wersja kompatybilna z Amazon Nova) ---
    def generate_trip_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generuje plan podróży.
        Usunięto parametr 'response_format' (powodował błędy w modelu Nova).
        Dodano ręczne czyszczenie znaczników Markdown.
        """

        json_structure = """
        {
            "destination": "Miasto, Kraj",
            "summary": "Krótki opis wycieczki",
            "itinerary": [
                {
                    "day": 1,
                    "theme": "Tytuł dnia",
                    "activities": [
                        "Punkt 1",
                        "Punkt 2"
                    ]
                }
            ]
        }
        """

        system_msg = f"""
        Jesteś ekspertem planowania podróży.
        Twoim zadaniem jest stworzenie planu i zwrócenie go w formacie JSON.

        WAŻNE ZASADY:
        1. Zwróć WYŁĄCZNIE kod JSON. Nie dodawaj wstępu ani zakończenia.
        2. Użyj klucza "activities" jako listy stringów dla atrakcji każdego dnia.
        3. Trzymaj się struktury podanej w przykładzie.

        WYMAGANY FORMAT JSON:
        {json_structure}
        """

        user_msg = f"""
        Stwórz plan dla:
        - Cel: {user_data.get('destination')}
        - Budżet: {user_data.get('budget')}
        - Termin: {user_data.get('date_range')} (Oblicz liczbę dni)
        - Zainteresowania: {', '.join(user_data.get('interests', []))}
        - Info dodatkowe: {user_data.get('additional_info')}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                # USUNIĘTO response_format, bo powodował błąd w tym modelu
                temperature=0.5
            )
            content = response.choices[0].message.content

            # --- DEBUGOWANIE ---
            # Jeśli nadal będzie błąd, w konsoli zobaczysz co dokładnie zwrócił model
            print(f"DEBUG (Raw LLM Response): {content[:100]}...")

            if not content:
                return {"error": "Model zwrócił pustą odpowiedź."}

            # --- CZYSZCZENIE ODPOWIEDZI ---
            # Usuwamy ```json i ``` jeśli model je dodał
            clean_content = content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:]
            elif clean_content.startswith("```"):
                clean_content = clean_content[3:]

            if clean_content.endswith("```"):
                clean_content = clean_content[:-3]

            clean_content = clean_content.strip()

            return json.loads(clean_content)

        except json.JSONDecodeError as e:
            print(f"Błąd parsowania JSON. Treść nie jest poprawnym JSON-em.")
            return {"error": f"Błąd parsowania: {str(e)}", "raw": content}
        except Exception as e:
            print(f"Błąd generowania planu: {e}")
            return {"error": str(e)}

    # --- 2. CZAT (Standardowy) ---
    def chat_about_plan(self, current_plan: Dict[str, Any], chat_history: List[Dict[str, str]],
                        user_question: str) -> str:
        plan_str = json.dumps(current_plan, ensure_ascii=False)

        system_msg = f"""
        Jesteś asystentem podróży. Odpowiadasz na pytania dotyczące poniższego planu.
        PLAN: {plan_str}
        """

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_question})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Błąd czatu: {e}"

    # --- 3. ZAPIS DO PDF (Dostosowany do struktury activities) ---
    def save_plan_to_pdf(self, trip_plan: Dict[str, Any], filename: str = "plan.pdf") -> str:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        def clean_text(text):
            if not isinstance(text, str): text = str(text)
            return text.encode('latin-1', 'replace').decode('latin-1')

        # Tytuł
        pdf.set_font("Arial", 'B', 16)
        dest = trip_plan.get('destination', 'Plan Podrozy')
        pdf.cell(0, 10, clean_text(f"Plan: {dest}"), ln=True, align='C')
        pdf.ln(10)

        # Podsumowanie
        pdf.set_font("Arial", size=12)
        summary = trip_plan.get('summary', '')
        if summary:
            pdf.multi_cell(0, 8, clean_text(f"Opis: {summary}"))
            pdf.ln(5)

        # Itinerary
        itinerary = trip_plan.get('itinerary', [])

        if not itinerary:
            print("UWAGA: Lista 'itinerary' jest pusta. PDF będzie pusty.")

        for item in itinerary:
            day_num = item.get('day', '?')
            theme = item.get('theme', '')

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, clean_text(f"Dzien {day_num}: {theme}"), ln=True)

            pdf.set_font("Arial", size=11)

            # Pobieranie aktywności (wymuszone promptem jako lista 'activities')
            activities = item.get('activities', [])

            if isinstance(activities, list):
                for act in activities:
                    pdf.cell(10)  # wcięcie
                    pdf.multi_cell(0, 8, clean_text(f"- {act}"))
            else:
                pdf.multi_cell(0, 8, clean_text(str(activities)))

            pdf.ln(3)

        try:
            pdf.output(filename)
            return os.path.abspath(filename)
        except Exception as e:
            print(f"Błąd zapisu PDF: {e}")
            return None