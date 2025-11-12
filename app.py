from flask import Flask, render_template, request
import os

app = Flask(__name__)
CHUNK_SIZE = 10  # показувати по 10 слів

# --- Мапа схожих букв ---
pairs = {
    'б': 'п', 'п': 'б', 'д': 'т', 'т': 'д', 'г': 'х', 'х': 'г',
    'з': 'с', 'с': 'з', 'ж': 'ш', 'ш': 'ж', 'дж': 'ч', 'ч': 'дж',
    'щ': 'ш', 'дз': 'ц', 'ц': 'дз', 'в': 'ф', 'ф': 'в',
    'ц': 'с', 'е': 'и', 'и': 'е', 'а': 'о', 'о': 'а',
    'і': 'и', 'я': 'й', 'й': 'я', 'ю': 'й', 'є': 'й', 'ї': 'й'
}

# --- Функції ---
def read_words(file_path):
    """Зчитує слова з файлу, уникаючи дублювання."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sorted(set(f.read().split()), key=lambda w: (len(w), w))
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1251') as f:
            return sorted(set(f.read().split()), key=lambda w: (len(w), w))
    except FileNotFoundError:
        print("❌ Файл не знайдено.")
        return []


def matches_exact(word, letters):
    """Перевірка на точну послідовність букв."""
    pos = 0
    for ch in word:
        if pos < len(letters) and ch == letters[pos]:
            pos += 1
    return pos == len(letters)


def matches_similar(word, letters):
    """Перевірка з урахуванням схожих звуків."""
    pos = 0
    for ch in word:
        if pos < len(letters):
            target = letters[pos]
            if ch == target or ch == pairs.get(target):
                pos += 1
    return pos == len(letters)


# --- Ініціалізація ---
# FILE_PATH = os.path.join(os.path.dirname(__file__), "clean_words_cache.txt")



# # Цей рядок визначає шлях до файлу відносно поточного скрипта
# #FILE_PATH = os.path.join(os.path.dirname(__file__), "clean_words.txt")

# # Тепер ви можете використовувати змінну FILE_PATH у своєму коді:
# print(f"Шлях до файлу: {FILE_PATH}")

# try:
#     with open(FILE_PATH, 'r', encoding='utf-8') as file:
#         content = file.read()
#         print("Вміст файлу успішно прочитано.")
# except FileNotFoundError:
#     print(f"Помилка: Файл не знайдено за шляхом {FILE_PATH}")


# print("🚀 Завантаження словника...")



URL = "https://raw.githubusercontent.com/Sabo81/phonetic_app/main/clean_words_cache.txt"
FILE_PATH = os.path.join(os.path.dirname(__file__), "clean_words_cache.txt")

if not os.path.exists(FILE_PATH):
    print("⬇️ Завантаження clean_words_cache.txt з GitHub...")
    r = requests.get(URL)
    with open(FILE_PATH, "wb") as f:
        f.write(r.content)

WORDS = read_words(FILE_PATH)
print(f"✅ Завантажено {len(WORDS):,} слів.")


# --- Основний маршрут ---
@app.route("/", methods=["GET", "POST"])
def index():
    letters = ""
    table = []
    start_index = 0
    next_index = 0
    search_done = False

    if request.method == "POST":
        letters = request.form.get("letters", "").strip().lower()
        action = request.form.get("action", "")
        start_index = int(request.form.get("start_index", 0))

        # новий пошук → починаємо з 0
        if action != "next":
            start_index = 0

        if letters:
            letters_set = set(letters)

            # шукаємо всі збіги
            exact_matches = [w for w in WORDS if matches_exact(w, letters)]
            similar_matches = [w for w in WORDS if matches_similar(w, letters)]

            # сортування (як у твоєму CLI варіанті)
            exact_matches = sorted(exact_matches, key=len)
            similar_matches = sorted(similar_matches, key=lambda x: (len(set(x) & letters_set), len(x)))

            # порційна видача
            chunk_exact = exact_matches[start_index:start_index + CHUNK_SIZE]
            chunk_similar = similar_matches[start_index:start_index + CHUNK_SIZE]

            # якщо списки різної довжини — доповнюємо порожніми клітинками
            max_len = max(len(chunk_exact), len(chunk_similar))
            chunk_exact += [""] * (max_len - len(chunk_exact))
            chunk_similar += [""] * (max_len - len(chunk_similar))

            table = list(zip(chunk_exact, chunk_similar))

            next_index = start_index + CHUNK_SIZE
            if next_index >= max(len(exact_matches), len(similar_matches)):
                search_done = True

            return render_template(
                "index.html",
                letters=letters,
                table=table,
                start_index=next_index,  # <-- ключове: тепер передаємо ОНОВЛЕНИЙ індекс
                next_index=next_index,
                search_done=search_done
            )

    # перше завантаження сторінки
    return render_template(
        "index.html",
        letters=letters,
        table=None,
        start_index=0,
        next_index=0,
        search_done=False
    )


# --- Запуск ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
