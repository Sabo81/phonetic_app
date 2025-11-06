from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # ліміт 1 МБ

# --- Глобальні змінні ---
WORDS = []
pairs = {
    'б': 'п', 'п': 'б', 'д': 'т', 'т': 'д', 'г': 'х', 'х': 'г',
    'з': 'с', 'с': 'з', 'ж': 'ш', 'ш': 'ж', 'дж': 'ч', 'ч': 'дж',
    'щ': 'ш', 'дз': 'ц', 'ц': 'дз', 'в': 'ф', 'ф': 'в',
    'ц': 'с', 'е': 'и', 'и': 'е', 'а': 'о', 'о': 'а',
    'і': 'и', 'я': 'й', 'й': 'я', 'ю': 'й', 'є': 'й',
    'ї': 'й'
}

# --- Завантаження слів ---
def load_words_from_github(url):
    print("🌐 Завантаження clean_words.txt з GitHub...")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        words = sorted(
            [w.strip().lower() for w in resp.text.split() if 4 < len(w.strip()) <= 11]
        )
        print(f"✅ Завантажено {len(words):,} слів.")
        return words
    except Exception as e:
        print(f"❌ Помилка завантаження: {e}")
        return []

# --- Порівняння ---
def matches_exact(word, letters):
    pos = 0
    for ch in word:
        if pos < len(letters) and ch == letters[pos]:
            pos += 1
    return pos == len(letters)

def matches_similar(word, letters):
    pos = 0
    for ch in word:
        if pos < len(letters):
            target = letters[pos]
            if ch == target or ch == pairs.get(target):
                pos += 1
    return pos == len(letters)

# --- Завантаження при старті ---
@app.before_first_request
def init_words():
    global WORDS
    if not WORDS:
        WORDS = load_words_from_github(
            "https://raw.githubusercontent.com/Sabo81/phonetic_app/main/clean_words.txt"
        )

# --- Основний маршрут ---
@app.route("/", methods=["GET", "POST"])
def index():
    global WORDS
    table = None
    search_done = False
    letters_to_find = ""
    start_index = 0

    if request.method == "POST":
        letters_to_find = request.form.get("letters", "").strip().lower()
        start_index = int(request.form.get("start_index", 0))

        if letters_to_find:
            exact, similar = [], []
            i = start_index

            # шукаємо далі від того місця, де зупинились
            while i < len(WORDS) and len(exact) < 10 and len(similar) < 10:
                word = WORDS[i]
                if matches_exact(word, letters_to_find):
                    exact.append(word)
                elif matches_similar(word, letters_to_find):
                    similar.append(word)
                i += 1

            next_index = i
            if next_index >= len(WORDS):
                search_done = True
            else:
                search_done = False

            max_len = max(len(exact), len(similar))
            table = [
                (exact[j] if j < len(exact) else '', similar[j] if j < len(similar) else '')
                for j in range(max_len)
            ]

            return render_template(
                "index.html",
                table=table,
                letters=letters_to_find,
                start_index=next_index,
                search_done=search_done
            )

    return render_template("index.html", table=None, letters="", start_index=0, search_done=False)

# --- Запуск ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
