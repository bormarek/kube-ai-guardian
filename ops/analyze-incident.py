import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:4b"

SYSTEM_NAME = "Kubernetes AI DevSecOps Guardian"
NAMESPACE = "kube-ai-guardian"


# ---------------------------------------------------------
# Walidacja argumentów
# ---------------------------------------------------------

if len(sys.argv) != 2:
    print("Użycie:")
    print("python3 ops/analyze-incident.py <katalog-incydentu>")
    print()
    print("Przykład:")
    print("python3 ops/analyze-incident.py incidents/20260829-153500")
    sys.exit(1)


incident_dir = Path(sys.argv[1])

if not incident_dir.exists():
    print(f"BŁĄD: katalog nie istnieje: {incident_dir}")
    sys.exit(1)

if not incident_dir.is_dir():
    print(f"BŁĄD: podana ścieżka nie jest katalogiem: {incident_dir}")
    sys.exit(1)


# ---------------------------------------------------------
# Pliki z danymi diagnostycznymi
# ---------------------------------------------------------

evidence_files = [
    "pods.txt",
    "events.txt",
    "deployment.txt",
    "logs.txt",
    "rollout-history.txt",
]


# ---------------------------------------------------------
# Wczytywanie evidence
# ---------------------------------------------------------

evidence = []

print("Wczytywanie danych diagnostycznych...")

for filename in evidence_files:
    path = incident_dir / filename

    if path.exists():
        content = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        evidence.append(
            f"""
============================================================
PLIK: {filename}
============================================================

{content}
"""
        )

        print(f"  [OK] {filename}")

    else:
        print(f"  [BRAK] {filename}")


if not evidence:
    print()
    print("BŁĄD: nie znaleziono żadnych danych diagnostycznych.")
    sys.exit(1)


# ---------------------------------------------------------
# Informacje o analizie
# ---------------------------------------------------------

analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------
# System prompt
# ---------------------------------------------------------

system_prompt = """
Jesteś polskojęzycznym inżynierem Site Reliability Engineering,
DevSecOps oraz specjalistą Kubernetes.

BEZWZGLĘDNA ZASADA:

ODPOWIADASZ WYŁĄCZNIE W JĘZYKU POLSKIM.

Nie wolno Ci generować raportu po angielsku.

Wszystkie:
- nagłówki,
- opisy,
- diagnozy,
- wyjaśnienia,
- rekomendacje,
- wnioski,
- komentarze,
- oceny ryzyka

muszą być napisane po polsku.

Wyjątkiem są wyłącznie elementy techniczne, które powinny
pozostać w oryginalnej formie, takie jak:

- nazwy zasobów Kubernetes,
- nazwy pól,
- nazwy Podów,
- nazwy Deploymentów,
- namespace,
- komunikaty błędów,
- fragmenty logów,
- polecenia kubectl,
- polecenia shell,
- statusy takie jak OOMKilled, CrashLoopBackOff, Running,
- wartości techniczne.

Jeżeli dane diagnostyczne są po angielsku, NIE oznacza to,
że raport może być po angielsku.

Masz analizować dane techniczne po angielsku,
ale raport końcowy ma być po polsku.

Nie wykonujesz żadnych poleceń.
Nie modyfikujesz klastra.
Jedynie analizujesz dostarczone dane i rekomendujesz działania.
"""


# ---------------------------------------------------------
# Prompt użytkownika
# ---------------------------------------------------------

prompt = f"""
WAŻNE:

CAŁY RAPORT KOŃCOWY MUSI BYĆ NAPISANY PO POLSKU.

Analizujesz incydent Kubernetes na podstawie rzeczywistych
danych diagnostycznych pobranych z klastra.

Informacje o środowisku:

System:
{SYSTEM_NAME}

Namespace:
{NAMESPACE}

Data analizy:
{analysis_date}


============================================================
ZASADY ANALIZY
============================================================

1. Opieraj diagnozę WYŁĄCZNIE na dostarczonych dowodach.

2. Nie wymyślaj problemów, zdarzeń ani przyczyn,
   których nie można potwierdzić na podstawie danych.

3. Jeśli danych jest za mało do jednoznacznej diagnozy,
   napisz to wyraźnie.

4. Oddzielaj:
   - fakty,
   - hipotezy,
   - rekomendacje.

5. Nie twierdź, że wykonałeś jakiekolwiek polecenia.

6. Możesz proponować bezpieczne polecenia diagnostyczne
   tylko do odczytu.

7. Preferuj trwałe poprawki wykonywane przez GitOps.

8. Nie rekomenduj ręcznego kubectl apply jako trwałej
   metody naprawy aplikacji zarządzanej przez ArgoCD.

9. AI nie może samodzielnie:
   - usuwać zasobów,
   - restartować Deploymentów,
   - skalować aplikacji,
   - wykonywać kubectl apply,
   - wykonywać helm upgrade,
   - modyfikować klastra.

10. Jeśli incydent może mieć znaczenie dla bezpieczeństwa,
    wyraźnie to zaznacz.

11. Wszystkie nagłówki i opisy mają być po polsku.

12. Nazwy techniczne i komunikaty błędów pozostaw
    w oryginalnej formie.


============================================================
FORMAT RAPORTU
============================================================

Wygeneruj raport Markdown dokładnie według poniższej struktury:


# Raport z incydentu Kubernetes


## Informacje podstawowe

Podaj:

- System
- Namespace
- Data analizy
- Rodzaj wykrytego incydentu


## Podsumowanie incydentu

W 2-4 zdaniach opisz, co się wydarzyło.


## Zaobserwowane objawy

Opisz najważniejsze symptomy widoczne
w dostarczonych danych.


## Przyczyna źródłowa

Wyjaśnij najbardziej prawdopodobną przyczynę problemu.

Jeżeli nie można jej jednoznacznie ustalić,
napisz to wyraźnie.


## Dowody

Przedstaw konkretne dowody potwierdzające diagnozę.

Uwzględnij, jeżeli występują:

- Pod status,
- Events,
- Deployment,
- logs,
- restart count,
- container state,
- resource limits,
- rollout history.


## Wpływ na usługę

Wyjaśnij potencjalny lub potwierdzony wpływ
incydentu na dostępność aplikacji.


## Zalecana naprawa

Zaproponuj rozwiązanie problemu.

Preferowana ścieżka trwałych zmian:

Git
→ ArgoCD
→ Kubernetes


## Zalecane polecenia diagnostyczne

Jeżeli potrzebna jest dalsza diagnostyka,
zaproponuj wyłącznie bezpieczne polecenia do odczytu.


## Aspekty bezpieczeństwa

Przeanalizuj incydent pod kątem bezpieczeństwa.

Jeżeli nie ma istotnego wpływu na bezpieczeństwo,
napisz to wprost.


## Działania zapobiegawcze

Zaproponuj działania, które mogą zapobiec
podobnemu incydentowi w przyszłości.


## Pewność diagnozy

Wybierz dokładnie jeden poziom:

NISKA
ŚREDNIA
WYSOKA

Następnie w jednym zdaniu uzasadnij ocenę.


============================================================
DANE DIAGNOSTYCZNE KUBERNETES
============================================================

{"".join(evidence)}

============================================================
KONIEC DANYCH DIAGNOSTYCZNYCH
============================================================


Ponownie przypomnienie:

RAPORT KOŃCOWY MA BYĆ W CAŁOŚCI PO POLSKU.

Rozpocznij analizę.
"""


# ---------------------------------------------------------
# Payload dla Ollama
# ---------------------------------------------------------

payload = json.dumps(
    {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
).encode("utf-8")


# ---------------------------------------------------------
# Request HTTP
# ---------------------------------------------------------

request = urllib.request.Request(
    OLLAMA_URL,
    data=payload,
    headers={
        "Content-Type": "application/json"
    },
    method="POST"
)


print()
print("AI Guardian analizuje incydent...")
print(f"Model: {OLLAMA_MODEL}")
print()


# ---------------------------------------------------------
# Wywołanie Ollama
# ---------------------------------------------------------

try:
    with urllib.request.urlopen(
        request,
        timeout=300
    ) as response:

        response_body = response.read()
        result = json.loads(response_body)

except urllib.error.URLError as exc:
    print("BŁĄD: nie można połączyć się z Ollama.")
    print()
    print(exc)
    print()
    print("Sprawdź:")
    print("  ollama list")
    print("  brew services list")
    sys.exit(1)

except TimeoutError:
    print("BŁĄD: przekroczono czas oczekiwania na odpowiedź Ollama.")
    sys.exit(1)

except Exception as exc:
    print(f"BŁĄD podczas komunikacji z Ollama: {exc}")
    sys.exit(1)


# ---------------------------------------------------------
# Walidacja odpowiedzi
# ---------------------------------------------------------

if "response" not in result:
    print("BŁĄD: Ollama zwróciła nieoczekiwaną odpowiedź.")
    print(result)
    sys.exit(1)


report = result["response"].strip()

if not report:
    print("BŁĄD: model zwrócił pusty raport.")
    sys.exit(1)


# ---------------------------------------------------------
# Zapis raportu
# ---------------------------------------------------------

output = incident_dir / "incident-report.md"

output.write_text(
    report + "\n",
    encoding="utf-8"
)


# ---------------------------------------------------------
# Wynik
# ---------------------------------------------------------

print("Analiza zakończona.")
print()
print("Raport zapisano w:")
print(f"  {output}")
print()
print("Aby wyświetlić raport:")
print(f'  cat "{output}"')
