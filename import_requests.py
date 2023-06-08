import requests
import re
from multiprocessing import Pool
import pdb
import json
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from time import sleep

with open("vacancies.json", "r", encoding="utf-8") as json_file:
    vacancies = json.load(json_file)  # {id: vacancy_name}

new_vacancy_counter = 0

user_agent = UserAgent().chrome

FILTER_URL = "https://hh.ru/search" \
             "/vacancy?text=NAME%3A%28frontend+NOT+fullstack%29&salary=&area=113&ored_clusters=true"

html = requests.get(FILTER_URL, headers={"User-Agent": user_agent}).text


soup = BeautifulSoup(html, "html.parser")

PAGINATOR_LAST_PAGE = soup.find_all(
    "a",
    attrs={"class": "bloko-button", "rel": "nofollow"},
    recursive=True,
)[-2]

LAST_PAGE_NUMBER = re.search(r'(\d+)', str(PAGINATOR_LAST_PAGE.encode_contents())).group()

for page_number in range(int(LAST_PAGE_NUMBER)):
    url = FILTER_URL

    if page_number > 0:
        url += f"&page={page_number}"

    html_ = requests.get(url, headers={"User-Agent": user_agent}).text
    soup_ = BeautifulSoup(html_, "html.parser")
    vacancies_on_page = soup_.find_all(
        "a",
        attrs={
            "class": "serp-item__title",
            "data-qa": "serp-item__title",
            "target": "_blank",
        }
    )

    for vacancy in vacancies_on_page:
        vacancy_name = str(vacancy.encode_contents(), encoding="utf-8")
        vacancy_id = vacancy["href"]

        vacancy_id = re.search(
            r"(?<=/vacancy/)(?P<id_>\d+)(?=[?]from)",
            vacancy_id,
        ).group("id_")
        vacancy_object = {vacancy_id: vacancy_name}
        
        vacancy_exist = vacancies.get(vacancy_id)

        if not vacancy_exist:
            new_vacancy_counter += 1
            vacancies.update(vacancy_object)
            print(f"Найдено {new_vacancy_counter} новых вакансий")
    else:
        sleep(0.2)
        print(f"Страница {page_number} просмотрена")
else:
    with open("vacancies.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(vacancies, ensure_ascii=False))

if new_vacancy_counter:
    def send_req(item):
        check = item[4].post(
            'https://hh.ru/applicant/vacancy_response/popup',
            data={
                "incomplete": False,
                "vacancy_id": int(item[0]),
                "resume_hash": f"{item[1]}",
                "ignore_postponed": True,
                "_xsrf": f"{item[2]}",
                "letter": f"{item[3]}",
                "lux": True,
                "withoutTest": "no",
                "hhtmFromLabel": "undefined",
                "hhtmSourceLabel": "undefined",
            }
        )

        print(check.status_code, item[0])
        if check.status_code != 200:
            if check.json()['error'] == 'negotiations-limit-exceeded':
                return False


    if __name__ == "__main__":
        n = 0
        req = requests.Session()

    """
    Привет! Чтобы скрипт заработал надо заполнить несколько полей, иначе HH не пустит запросы

    Введи сюда сво куки. Важно быть залогиненым на HH. Проще всего это сделав скопировав все как HAR . Дальше нас инетерсует все что после 'Cookie:' до следующего поля с ':' (это может быть 'X-hhtmFrom:') или что-то другое. Главное забрать все после кук
    """
    cookies = "Вставь сюда свои куки"

    if cookies == "Вставь сюда свои куки":
        raise Exception("Ты забыл вставить сюда свои куки")

    req.headers = {"Host": "hh.ru", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15", "Cookie": f"""{cookies}"""}

    """Здесь нам нужно вставить хеш резюме. Оно находиться в разделе https://hh.ru/applicant/resumes . Дальше ты должен перейти в одно из своих резюме и скопировать хеш после ссылки . Как пример https://hh.ru/resume/71010d6fff099f0ef20039ed1f497978653133 . Тут нам нужно забрать 71010d6fff099f0ef20039ed1f497978653133 и вставить в поле ниже"""

    resume_hash = "71010d6fff099f0ef20039ed1f497978653133"

    if resume_hash == "71010d6fff099f0ef20039ed1f497978653133":
        raise Exception("Ты забыл вставить сюда своё резюме")

    xsrf_token = re.search("_xsrf=(.*?);", cookies).group(1)

    """Ниже вставляем свое письмо. Советую сделать его максимально обобщенным. Больше об этом в мое треде https://twitter.com/ns0000000001/status/1612456900993650688?s=52&t=X3kUKCZQjFDJbTbg9aQWbw """

    letter = "Вставь сюда свое письмо"

    if letter == "Вставь сюда свое письмо":
        raise Exception("Ты забыл вставить сюда своё письмо")

    """Дальще переходи на страницу HH и в поиске вбиваем то, что вам интересно. После нажимает Enter и копируем ссыку на которую вас перебросило. Пример который получается при вводе 'автоматизация python': https://hh.ru/search/vacancy?text=автоматизация+python&salary=&schedule=remote&ored_clusters=true&enable_snippets=true"""

    search_link = "Вставь сюда свой поисковый запрос"

    if search_link == "Вставь сюда свой поисковый запрос":
        raise Exception("Ты забыл вставить сюда свой запрос")

    pool = Pool(processes=70)

    """Важно, что HH позволяет в день откликаться только на 200 вакансий. Поэтому, как только скрипт получит ошибку о привышения лимита, он автоматически отключиться. Если ты все сделал правильно, то ты будешь видеть в консоли такие записи

    400 76870753
    200 76613497

    400 и 200 статусы это ок. Если ты видишь только 403 или 404 проверь, правильно ли ты вставил куки
    """

    while True:
        data = req.get(f"{search_link}&page={n}").text
        links = re.findall(r'https://hh.ru/vacancy/(\d*)?', data, re.DOTALL)
        send_dict = []
        for link in links:
            send_dict.append((link, resume_hash, xsrf_token, letter, req))
        if links == []:
            break
        check = pool.map(send_req, send_dict)
        if False in check:
            break
        n += 1
    pool.close()
    pool.join()