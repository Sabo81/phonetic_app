from flask import Flask, render_template, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # ліміт 1 МБ на запит

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


# --- Функції ---
def load_words(file_path: str):
    """Завантажує слова лише один раз при запуску додатку."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if 3 < len(line.strip()) <= 11)
    except Exception as e:
        print(f"Помилка при читанні файлу: {e}")
        return set()


def matches_exact(word: str, letters: str) -> bool:
    """Перевірка на точну послідовність букв."""
    pos = 0
    for ch in word:
        if pos < len(letters) and ch == letters[pos]:
            pos += 1
    return pos == len(letters)


def matches_similar(word: str, letters: str) -> bool:
    """Перевірка з урахуванням схожих звуків."""
    pos = 0
    for ch in word:
        if pos < len(letters):
            target = letters[pos]
            if ch == target or ch == pairs.get(target):
                pos += 1
    return pos == len(letters)


# --- Основний маршрут ---
@app.route("/", methods=["GET", "POST"])
def index():
    table = None
    letters_to_find = ""

    if request.method == "POST":
        letters_to_find = request.form.get("letters", "").strip().lower()
        if letters_to_find:
            letters_set = set(letters_to_find)

            # Використовуємо генератори для економії пам’яті
            exact_matches = (w for w in WORDS if matches_exact(w, letters_to_find))
            similar_matches = (w for w in WORDS if matches_similar(w, letters_to_find))

            # Обмежуємо кількість результатів
            exact_list = sorted(list(exact_matches), key=len)[:100]
            similar_list = sorted(list(similar_matches),
                                  key=lambda x: (len(set(x) & letters_set), len(x)))[:100]

            # Формуємо таблицю для HTML
            table = [
                (exact_list[i] if i < len(exact_list) else '',
                 similar_list[i] if i < len(similar_list) else '')
                for i in range(max(len(exact_list), len(similar_list)))
            ]

    return render_template("index.html", table=table, letters_to_find=letters_to_find)


# --- Завантаження при старті ---
if __name__ == "__main__":
    print("🔄 Завантаження слів...")
    WORDS = load_words("clean_words.txt")
    print(f"✅ Завантажено {len(WORDS):,} слів.")
    app.run(debug=False, host="0.0.0.0", port=5000)
