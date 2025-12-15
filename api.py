import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import Twojego serwisu
from service.travelbot_service import TravelBotService

app = FastAPI(title="TravelBot API", description="API do planowania podróży z AI")

# --- KONFIGURACJA CORS ---
# Pozwala na zapytania z localhost (np. gdy frontend stoi na porcie 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji warto zmienić "*" na konkretny adres frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicjalizacja serwisu (raz przy starcie aplikacji)
service = TravelBotService()


# --- MODELE DANYCH (Pydantic) ---
# To definiuje, co frontend musi wysłać w JSONie

class UserPreferences(BaseModel):
    destination: str
    budget: str
    recreation_type: str = "Ogólny"
    interests: List[str]
    date_range: str
    travelers_count: int
    diet: str = "Brak"
    additional_info: Optional[str] = ""


class ChatRequest(BaseModel):
    plan: Dict[str, Any]  # Aktualny obiekt planu
    history: List[Dict[str, str]]  # Historia rozmowy [{"role": "user", ...}]
    question: str  # Nowe pytanie


class PdfRequest(BaseModel):
    plan: Dict[str, Any]  # Plan do wydruku


# --- ENDPOINTY ---

@app.get("/")
def read_root():
    return {"status": "TravelBot API is running"}


@app.post("/api/generate-plan")
def generate_plan(prefs: UserPreferences):
    """
    Przyjmuje preferencje użytkownika i zwraca wygenerowany plan podróży (JSON).
    """
    print(f"Otrzymano zapytanie o plan do: {prefs.destination}")

    # Konwersja modelu Pydantic na zwykły słownik
    data_dict = prefs.model_dump()

    result = service.generate_trip_plan(data_dict)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/api/chat")
def chat_about_plan(req: ChatRequest):
    """
    Odpowiada na pytanie użytkownika w kontekście planu.
    """
    answer = service.chat_about_plan(
        current_plan=req.plan,
        chat_history=req.history,
        user_question=req.question
    )
    return {"answer": answer}


@app.post("/api/save-pdf")
def save_pdf(req: PdfRequest, background_tasks: BackgroundTasks):
    """
    Generuje PDF z planu i zwraca go jako plik do pobrania.
    Usuwa plik z serwera po wysłaniu.
    """
    filename = "Moj_Plan_Podrozy.pdf"

    # Generowanie pliku fizycznie na serwerze
    file_path = service.save_plan_to_pdf(req.plan, filename)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Błąd generowania pliku PDF")

    # Funkcja sprzątająca (uruchomi się po wysłaniu odpowiedzi)
    def remove_file(path: str):
        try:
            os.remove(path)
            print(f"Usunięto plik tymczasowy: {path}")
        except Exception as e:
            print(f"Błąd usuwania pliku: {e}")

    # Dodanie zadania usunięcia pliku do tła
    background_tasks.add_task(remove_file, file_path)

    # Zwrot pliku
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/pdf'
    )