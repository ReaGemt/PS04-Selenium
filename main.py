import requests
from bs4 import BeautifulSoup
import argparse

# Получает содержимое страницы Википедии по запросу
def get_wikipedia_page(query, cache):
    # Проверка наличия запроса в кэше
    if query in cache:
        return cache[query]  # Возврат страницы из кэша, если она уже загружена

    # Формирование URL для запроса к Википедии
    url = f"https://ru.wikipedia.org/wiki/{query.replace(' ', '_')}"
    try:
        response = requests.get(url)  # Выполнение HTTP-запроса к указанному URL
        response.raise_for_status()  # Проверка на наличие ошибок HTTP
        cache[query] = response.text  # Сохранение страницы в кэш
        return response.text
    except requests.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return None

# Извлекает параграфы из HTML страницы
def parse_paragraphs(html):
    soup = BeautifulSoup(html, 'html.parser')  # Создание объекта BeautifulSoup для анализа HTML
    content = soup.find('div', {'class': 'mw-parser-output'})  # Поиск основного содержимого статьи
    paragraphs = content.find_all('p', recursive=False)  # Извлечение всех параграфов
    return paragraphs

# Извлекает ссылки на связанные страницы из HTML
def parse_links(html):
    soup = BeautifulSoup(html, 'html.parser')  # Создание объекта BeautifulSoup для анализа HTML
    content = soup.find('div', {'class': 'mw-parser-output'})  # Поиск основного содержимого статьи
    links = content.find_all('a', href=True)  # Извлечение всех ссылок с атрибутом href
    valid_links = [link for link in links if link['href'].startswith('/wiki/') and not ':' in link['href']]
    # Фильтрация ссылок, оставляя только те, которые ведут на другие статьи Википедии
    return valid_links

# Извлекает разделы статьи
def parse_sections(html):
    soup = BeautifulSoup(html, 'html.parser')  # Создание объекта BeautifulSoup для анализа HTML
    sections = soup.find_all('span', {'class': 'mw-headline'})  # Извлечение всех заголовков разделов статьи
    return sections

# Сохраняет историю посещенных страниц в файл
def save_history(history):
    try:
        with open("history.txt", "w", encoding="utf-8") as file:
            for page in history:
                file.write(page + "\n")  # Запись каждой статьи из истории в файл
        print("История сохранена в файл 'history.txt'.")
    except IOError as e:
        print(f"Ошибка при сохранении истории: {e}")

# Загружает историю из файла
def load_history():
    try:
        with open("history.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]  # Чтение истории из файла
    except FileNotFoundError:
        return []

# Сохраняет избранные статьи в файл
def save_favorites(favorites):
    try:
        with open("favorites.txt", "w", encoding="utf-8") as file:
            for page in favorites:
                file.write(page + "\n")  # Запись каждой статьи из избранного в файл
        print("Избранные статьи сохранены в файл 'favorites.txt'.")
    except IOError as e:
        print(f"Ошибка при сохранении избранного: {e}")

# Загружает избранные статьи из файла
def load_favorites():
    try:
        with open("favorites.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]  # Чтение избранного из файла
    except FileNotFoundError:
        return []

# Поиск по тексту параграфов
def search_in_paragraphs(paragraphs, search_term):
    found = False  # Флаг для отслеживания наличия найденного текста
    for i, paragraph in enumerate(paragraphs, 1):
        if search_term.lower() in paragraph.get_text(strip=True).lower():
            # Если искомый текст найден в параграфе, выводим его
            print(f"\nПараграф {i}:\n{paragraph.get_text(strip=True)}\n")
            found = True
    if not found:
        print("Текст не найден в текущей статье.")

def main(start_query=None):
    cache = {}  # Кэш для страниц
    history = load_history()  # Загрузка истории
    favorites = load_favorites()  # Загрузка избранного

    if start_query:
        query = start_query  # Используем начальный запрос, если он был передан
    else:
        query = input("Введите запрос для поиска на Википедии (или 'выход' для выхода): ").strip()

    while query.lower() != 'выход':
        html = get_wikipedia_page(query, cache)  # Получаем HTML страницы
        if html is None:  # Если страница не найдена, запрашиваем новый ввод
            if not start_query:
                query = input("Введите запрос для поиска на Википедии (или 'выход' для выхода): ").strip()
            else:
                break
            continue

        history.append(query)  # Добавляем текущий запрос в историю
        paragraphs = parse_paragraphs(html)  # Извлекаем параграфы статьи
        links = parse_links(html)  # Извлекаем ссылки на связанные статьи
        sections = parse_sections(html)  # Извлекаем разделы статьи

        while True:
            # Выводим меню действий для пользователя
            print("\nВыберите действие:")
            print("1. Листать параграфы текущей статьи")
            print("2. Перейти на одну из связанных страниц")
            print("3. Показать историю просмотренных страниц")
            print("4. Вернуться к предыдущей статье")
            print("5. Поиск по тексту в текущей статье")
            print("6. Добавить текущую статью в избранное")
            print("7. Показать избранные статьи")
            print("8. Просмотреть разделы текущей статьи")
            print("9. Выйти из программы")

            choice = input("Введите номер действия: ").strip()
            if choice == '1':
                # Листание параграфов статьи
                for i, paragraph in enumerate(paragraphs, 1):
                    print(f"\nПараграф {i}:\n{paragraph.get_text(strip=True)}\n")
                    more = input("Нажмите Enter, чтобы продолжить, или введите 'стоп', чтобы вернуться: ").strip().lower()
                    if more == 'стоп':
                        break

            elif choice == '2':
                if not links:
                    print("Нет доступных связанных страниц.")
                    continue

                # Вывод первых 20 ссылок на связанные страницы
                print("\nДоступные ссылки на связанные страницы (первые 20):")
                num_to_show = min(20, len(links))
                for i in range(num_to_show):
                    link = links[i]
                    print(f"{i+1}. {link.get_text(strip=True)} ({link['href']})")

                # Запрос на вывод всех ссылок
                show_all = input("Введите 'все', чтобы показать все доступные ссылки, или нажмите Enter, чтобы продолжить: ").strip().lower()
                if show_all == 'все':
                    for i in range(num_to_show, len(links)):
                        link = links[i]
                        print(f"{i+1}. {link.get_text(strip=True)} ({link['href']})")

                # Выбор ссылки для перехода
                link_choice = input("Введите номер ссылки для перехода, или 'назад', чтобы вернуться: ").strip()
                if link_choice.lower() == 'назад':
                    continue

                try:
                    link_index = int(link_choice) - 1
                    if 0 <= link_index < len(links):
                        new_query = links[link_index]['href'].split('/wiki/')[1]
                        query = new_query  # Устанавливаем новый запрос для перехода на другую статью
                        break
                    else:
                        print("Некорректный номер ссылки.")
                except ValueError:
                    print("Некорректный ввод.")

            elif choice == '3':
                # Вывод истории посещенных страниц
                if history:
                    print("\nИстория просмотренных страниц:")
                    for i, page in enumerate(history, 1):
                        print(f"{i}. {page.replace('_', ' ')}")
                else:
                    print("История пуста.")

            elif choice == '4':
                # Возвращение к предыдущей статье
                if len(history) > 1:
                    history.pop()  # Удаляем текущую статью из истории
                    previous_query = history[-1]
                    query = previous_query  # Устанавливаем предыдущий запрос
                    break
                else:
                    print("Нет предыдущей статьи в истории.")

            elif choice == '5':
                # Поиск по тексту в параграфах
                search_term = input("Введите текст для поиска в параграфах: ").strip()
                search_in_paragraphs(paragraphs, search_term)

            elif choice == '6':
                # Добавление текущей статьи в избранное
                if query not in favorites:
                    favorites.append(query)
                    print(f"Статья '{query.replace('_', ' ')}' добавлена в избранное.")
                else:
                    print("Эта статья уже в избранном.")

            elif choice == '7':
                # Вывод избранных статей
                if favorites:
                    print("\nИзбранные статьи:")
                    for i, page in enumerate(favorites, 1):
                        print(f"{i}. {page.replace('_', ' ')}")
                else:
                    print("Избранное пусто.")

            elif choice == '8':
                # Просмотр разделов текущей статьи
                if sections:
                    print("\nРазделы текущей статьи:")
                    for i, section in enumerate(sections, 1):
                        print(f"{i}. {section.get_text(strip=True)}")
                else:
                    print("Разделы не найдены.")

            elif choice == '9':
                # Сохранение данных и выход из программы
                save_history(history)
                save_favorites(favorites)
                print("Выход из программы.")
                return

            else:
                print("Некорректный ввод. Попробуйте снова.")

        if start_query:
            break

        query = input("Введите запрос для поиска на Википедии (или 'выход' для выхода): ").strip()

if __name__ == "__main__":
    # Настройка парсера аргументов командной строки
    parser = argparse.ArgumentParser(description='Wiki CLI tool')
    parser.add_argument('-q', '--query', type=str, help='Начальный запрос для поиска на Википедии')
    args = parser.parse_args()

    main(args.query)  # Запуск основной функции с возможным начальным запросом
