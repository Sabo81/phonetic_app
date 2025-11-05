from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # ліміт 1 МБ

# --- Глобальні змінні ---
WORDS = set()
pairs = {
    'б': 'п', 'п': 'б', 'д': 'т', 'т': 'д', 'г': 'х', 'х': 'г',
    'з': 'с', 'с': 'з', 'ж': 'ш', 'ш': 'ж', 'дж': 'ч', 'ч': 'дж',
    'щ': 'ш', 'дз': 'ц', 'ц': 'дз', 'в': 'ф', 'ф': 'в',
    'ц': 'с', 'е': 'и', 'и': 'е', 'а': 'о', 'о': 'а',
    'і': 'и', 'я': 'й', 'й': 'я', 'ю': 'й', 'є': 'й',
    'ї': 'й'
}

# --- Завантаження слів з GitHub ---
def load_words_from_github(url):
    print("🌐 Завантаження clean_words.txt з GitHub...")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        words = {
            w.strip().lower()
            for w in resp.text.split()
            if 4 < len(w.strip()) <= 11
        }
        print(f"✅ Завантажено {len(words):,} слів.")
        return words
    except Exception as e:
        print(f"❌ Помилка завантаження слів: {e}")
        return set()

# --- Порівняння ---
def matches_exact(word: str, letters: str) -> bool:
    pos = 0
    for ch in word:
        if pos < len(letters) and ch == letters[pos]:
            pos += 1
    return pos == len(letters)

def matches_similar(word: str, letters: str) -> bool:
    pos = 0
    for ch in word:
        if pos < len(letters):
            target = letters[pos]
            if ch == target or ch == pairs.get(target):
                pos += 1
    return pos == len(letters)

# --- Завантаження при старті ---
@app.before_request
def initialize():
    global WORDS
    WORDS = load_words_from_github(
        "https://raw.githubusercontent.com/Sabo81/phonetic_app/main/clean_words.txt"
    )

# --- Основний маршрут ---
@app.route("/", methods=["GET", "POST"])
def index():
    table = None
    letters_to_find = ""

    if request.method == "POST":
        letters_to_find = request.form.get("letters", "").strip().lower()
        if letters_to_find:
            letters_set = set(letters_to_find)

            exact_matches = [w for w in WORDS if matches_exact(w, letters_to_find)]
            similar_matches = [w for w in WORDS if matches_similar(w, letters_to_find)]

            exact_list = sorted(exact_matches, key=len)[:100]
            similar_list = sorted(similar_matches,
                                  key=lambda x: (len(set(x) & letters_set), len(x)))[:100]

            table = [
                (exact_list[i] if i < len(exact_list) else '',
                 similar_list[i] if i < len(similar_list) else '')
                for i in range(max(len(exact_list), len(similar_list)))
            ]

    return render_template("index.html", table=table, letters_to_find=letters_to_find)

# --- Запуск ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
