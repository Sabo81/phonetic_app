from flask import Flask, render_template, request

app = Flask(__name__)

# Мапа схожих букв для швидкого пошуку
pairs = {
    'б': 'п', 'п': 'б', 'д': 'т', 'т': 'д', 'г': 'х', 'х': 'г',
    'з': 'с', 'с': 'з', 'ж': 'ш', 'ш': 'ж', 'дж': 'ч', 'ч': 'дж',
    'щ': 'ш', 'дз': 'ц', 'ц': 'дз', 'в': 'ф', 'ф': 'в',
    'ц': 'с', 'е': 'и', 'и': 'е', 'а': 'о', 'о': 'а',
    'і': 'и', 'я': 'й', 'й': 'я', 'ю': 'й', 'є': 'й',
    'ї': 'й'
}

def read_words(file_path):
    """Зчитує слова з файлу, уникаючи дублювання."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return list(set(f.read().split()))
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1251') as f:
            return list(set(f.read().split()))
    except FileNotFoundError:
        print("Файл не знайдено.")
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

@app.route("/", methods=["GET", "POST"])
def index():
    table = None  # <-- Головна зміна!
    letters_to_find = ""

    if request.method == "POST":
        letters_to_find = request.form.get("letters", "").strip().lower()
        if letters_to_find:
            letters_set = set(letters_to_find)
            file_path = "clean_words.txt"
            words = read_words(file_path)

            exact_matches = [w for w in words if matches_exact(w, letters_to_find)]
            similar_matches = [w for w in words if matches_similar(w, letters_to_find)]

            exact_matches = sorted(exact_matches, key=len)[:100]
            similar_matches = sorted(similar_matches, key=lambda x: (len(set(x) & letters_set), len(x)))[:100]

            max_len = max(len(exact_matches), len(similar_matches))
            table = []
            for i in range(max_len):
                left_word = exact_matches[i] if i < len(exact_matches) else ''
                right_word = similar_matches[i] if i < len(similar_matches) else ''
                table.append((left_word, right_word))

    return render_template("index.html", table=table, letters=letters_to_find)


if __name__ == "__main__":
    app.run()  # або залишити app.run(debug=True) тільки локально

