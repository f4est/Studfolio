import os
import django
import random
from django.utils import timezone
from datetime import timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studfolio.settings')
django.setup()

# Импорт моделей после настройки Django
from django.contrib.auth import get_user_model
from users.models import (
    CustomUser, Skill, Certificate, Achievement, Review
)
from portfolio.models import Project, ProjectPost as Post, ProjectComment as Comment

# Функция для генерации случайного текста (замена lorem)
def generate_text(min_words=15, max_words=50):
    """Генерирует случайный текст из указанного количества слов"""
    words = [
        "проект", "разработка", "программирование", "технология", "система",
        "дизайн", "интерфейс", "данные", "анализ", "алгоритм", "метод",
        "решение", "задача", "результат", "процесс", "исследование", "тестирование",
        "производительность", "оптимизация", "функциональность", "архитектура",
        "пользователь", "клиент", "сервер", "база", "фреймворк", "библиотека",
        "компонент", "модуль", "тест", "документация", "интеграция", "внедрение",
        "эффективность", "качество", "современный", "инновационный", "автоматический",
        "мобильный", "веб", "облачный", "распределенный", "интерактивный", "гибкий",
        "удобный", "быстрый", "надежный", "безопасный", "масштабируемый", "поддерживаемый",
        "успешный", "интересный", "полезный", "практический", "теоретический", "опытный"
    ]
    
    num_words = random.randint(min_words, max_words)
    text = " ".join(random.choice(words) for _ in range(num_words))
    return text.capitalize() + "."

def generate_paragraph(min_sentences=3, max_sentences=6):
    """Генерирует абзац из нескольких предложений"""
    num_sentences = random.randint(min_sentences, max_sentences)
    return " ".join(generate_text() for _ in range(num_sentences))

# Функция для создания тестовых данных
def create_test_data():
    print("Начинаем создание тестовых данных...")
    
    # Удаляем существующие тестовые данные (опционально)
    clean_test_data()
    
    # Создаем тестовых пользователей
    users = create_test_users()
    
    # Создаем навыки для пользователей
    create_skills_for_users(users)
    
    # Создаем проекты для пользователей
    projects = create_projects_for_users(users)
    
    # Создаем сертификаты для пользователей
    create_certificates_for_users(users)
    
    # Создаем достижения для пользователей
    create_achievements_for_users(users)
    
    # Создаем отзывы (только для студентов)
    create_reviews_for_students(users)
    
    # Создаем посты в ленте новостей
    create_posts_for_projects(users, projects)
    
    print("Тестовые данные успешно созданы!")

def clean_test_data():
    """Очистка тестовых данных"""
    # Удаляем тестовых пользователей и связанные с ними данные
    print("Удаление существующих тестовых данных...")
    
    # Получаем тестовые имена пользователей
    test_usernames = [f"test_user_{i}" for i in range(1, 15)]
    
    # Удаляем тестовых пользователей (каскадное удаление удалит связанные объекты)
    CustomUser.objects.filter(username__in=test_usernames).delete()
    
    print("Существующие тестовые данные удалены.")

def create_test_users():
    """Создание тестовых пользователей"""
    print("Создание тестовых пользователей...")
    
    # Списки имен и фамилий для разнообразия
    first_names = [
        "Александр", "Екатерина", "Михаил", "Анна", "Дмитрий",
        "Ольга", "Иван", "Мария", "Сергей", "Наталья",
        "Андрей", "Елена", "Павел", "Татьяна"
    ]
    
    last_names = [
        "Иванов", "Смирнова", "Кузнецов", "Попова", "Соколов",
        "Лебедева", "Новиков", "Морозова", "Петров", "Волкова",
        "Соловьев", "Васильева", "Зайцев", "Павлова"
    ]
    
    # Списки университетов, факультетов и специализаций
    universities = [
        "МГУ им. М.В. Ломоносова", "МГТУ им. Н.Э. Баумана", "СПбГУ",
        "НИУ ВШЭ", "МФТИ", "ИТМО", "РЭУ им. Г.В. Плеханова",
        "РУДН", "КФУ", "НГУ", "ТГУ", "УрФУ", "ДВФУ", "Сколтех"
    ]
    
    faculties = [
        "Факультет информационных технологий", "Механико-математический факультет", 
        "Физический факультет", "Экономический факультет", "Юридический факультет",
        "Биологический факультет", "Факультет журналистики", "Химический факультет",
        "Филологический факультет", "Факультет психологии", "Географический факультет",
        "Факультет фундаментальной медицины", "Социологический факультет", "Исторический факультет"
    ]
    
    specializations = [
        "Программная инженерия", "Информационная безопасность", "Прикладная математика",
        "Экономика и финансы", "Гражданское право", "Молекулярная биология",
        "Международная журналистика", "Органическая химия", "Лингвистика",
        "Клиническая психология", "Картография и геоинформатика", "Кардиология",
        "Социология коммуникаций", "История России"
    ]
    
    users = []
    
    # Создаем 14 тестовых пользователей
    for i in range(1, 15):
        # Определяем тип пользователя (10 студентов, 3 преподавателя, 1 работодатель)
        if i <= 10:
            user_type = 'student'
        elif i <= 13:
            user_type = 'teacher'
        else:
            user_type = 'employer'
        
        # Создаем пользователя
        user = CustomUser.objects.create_user(
            username=f"test_user_{i}",
            email=f"test_user_{i}@example.com",
            password="testpassword",
            first_name=first_names[i-1],
            last_name=last_names[i-1],
            user_type=user_type,
            university=universities[i-1] if user_type != 'employer' else None,
            faculty=faculties[i-1] if user_type != 'employer' else None,
            specialization=specializations[i-1] if user_type != 'employer' else None,
            graduation_year=random.randint(2025, 2028) if user_type == 'student' else None,
            bio=generate_paragraph() if random.random() > 0.3 else "",
            is_public=True
        )
        
        users.append(user)
        print(f"Создан пользователь: {user.get_full_name()} ({user.get_user_type_display()})")
    
    return users

def create_skills_for_users(users):
    """Создание навыков для пользователей"""
    print("Создание навыков для пользователей...")
    
    # Список возможных навыков
    all_skills = [
        # Программирование
        "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Swift", "Kotlin", "Ruby", "Go",
        # Веб-технологии
        "HTML", "CSS", "React", "Angular", "Vue.js", "Django", "Laravel", "Node.js", "Express",
        # Базы данных
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Firebase",
        # Инструменты
        "Git", "Docker", "Kubernetes", "Jenkins", "CI/CD", "AWS", "Azure", "GCP",
        # Анализ данных
        "Data Science", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
        # Дизайн
        "UI/UX Design", "Adobe Photoshop", "Adobe Illustrator", "Figma", "Sketch",
        # Soft skills
        "Teamwork", "Communication", "Leadership", "Problem Solving", "Time Management"
    ]
    
    for user in users:
        # Для каждого пользователя выбираем от 5 до 12 случайных навыков
        num_skills = random.randint(5, 12)
        selected_skills = random.sample(all_skills, num_skills)
        
        for skill_name in selected_skills:
            # Создаем навык с случайным уровнем от 1 до 5
            Skill.objects.create(
                user=user,
                name=skill_name,
                level=random.randint(1, 5)
            )
        
        print(f"Добавлено {num_skills} навыков для пользователя {user.get_full_name()}")

def create_projects_for_users(users):
    """Создание проектов для пользователей"""
    print("Создание проектов для пользователей...")
    
    # Список возможных названий проектов
    project_titles = [
        "Веб-приложение для управления задачами", "Мобильное приложение финансового учета",
        "Система распознавания изображений", "Платформа для онлайн-обучения",
        "Чат-бот для обслуживания клиентов", "Социальная сеть для профессионалов",
        "Приложение для отслеживания физической активности", "Агрегатор новостей",
        "Система управления контентом", "Интернет-магазин с рекомендательной системой",
        "Музыкальный стриминговый сервис", "Приложение для планирования путешествий",
        "Платформа для фрилансеров", "Игровое приложение с AR элементами",
        "Blockchain-решение для управления цепочкой поставок", "Приложение для изучения языков",
        "Система анализа данных для бизнеса", "Видео-стриминговый сервис",
        "Платформа для проведения мероприятий", "Приложение для удаленной работы команды"
    ]
    
    # Список возможных технологий
    technologies_list = [
        "Python, Django, React, PostgreSQL", "Java, Spring Boot, Vue.js, MySQL",
        "JavaScript, Node.js, Express, MongoDB", "C#, ASP.NET, Angular, SQL Server",
        "PHP, Laravel, jQuery, MySQL", "Swift, Core Data, Firebase",
        "Kotlin, Android SDK, Room", "Python, Flask, React, SQLite",
        "JavaScript, React Native, Firebase", "Python, TensorFlow, Flask",
        "JavaScript, HTML, CSS, Bootstrap", "Ruby, Rails, PostgreSQL",
        "Go, React, PostgreSQL", "Python, Django REST, React, Redux",
        "C++, Qt, SQLite", "JavaScript, Three.js, WebGL",
        "Python, PyTorch, Pandas, NumPy", "Java, Android, Kotlin, Room",
        "Swift, iOS, CoreML, Firebase", "TypeScript, React, Express, MongoDB"
    ]
    
    all_projects = []
    
    for user in users:
        # Для каждого пользователя создаем от 1 до 4 проектов
        num_projects = random.randint(1, 4)
        
        for _ in range(num_projects):
            # Выбираем случайное название проекта и технологии
            title = random.choice(project_titles)
            technologies = random.choice(technologies_list)
            
            # Создаем случайную дату создания (в пределах последних 2 лет)
            days_ago = random.randint(1, 730)
            created_at = timezone.now() - timedelta(days=days_ago)
            
            # Случайные даты для начала и окончания проекта
            start_date = (created_at - timedelta(days=random.randint(30, 180))).date()
            end_date = None
            if random.random() > 0.3:  # 70% проектов имеют дату окончания
                end_date = (created_at - timedelta(days=random.randint(0, 30))).date()
            
            # Случайное описание проекта
            description = "\n".join([generate_paragraph() for _ in range(random.randint(1, 3))])
            
            # Создаем проект
            project = Project.objects.create(
                user=user,
                title=title,
                description=description,
                technologies=technologies,
                url=f"https://example.com/projects/{title.lower().replace(' ', '-')}" if random.random() > 0.4 else "",
                github_url=f"https://github.com/{user.username}/{title.lower().replace(' ', '-')}" if random.random() > 0.6 else "",
                start_date=start_date,
                end_date=end_date,
                is_featured=random.random() > 0.7,  # 30% проектов будут избранными
                created_at=created_at,
                updated_at=created_at + timedelta(days=random.randint(0, 30))
            )
            
            all_projects.append(project)
        
        print(f"Добавлено {num_projects} проектов для пользователя {user.get_full_name()}")
    
    return all_projects

def create_certificates_for_users(users):
    """Создание сертификатов для пользователей"""
    print("Создание сертификатов для пользователей...")
    
    # Список возможных сертификатов
    certificate_data = [
        {"title": "Python для начинающих", "issuer": "Coursera"},
        {"title": "Advanced JavaScript", "issuer": "Udemy"},
        {"title": "Machine Learning", "issuer": "Stanford Online"},
        {"title": "Веб-разработка с React", "issuer": "edX"},
        {"title": "Основы SQL", "issuer": "Stepik"},
        {"title": "Data Science с Python", "issuer": "DataCamp"},
        {"title": "Java Programming", "issuer": "Oracle Academy"},
        {"title": "Основы кибербезопасности", "issuer": "Cisco Networking Academy"},
        {"title": "Full Stack Developer", "issuer": "FreeCodeCamp"},
        {"title": "Cloud Computing", "issuer": "AWS Training"},
        {"title": "Agile Project Management", "issuer": "Scrum.org"},
        {"title": "UI/UX Design Fundamentals", "issuer": "Interaction Design Foundation"},
        {"title": "Mobile App Development", "issuer": "Google Developers"},
        {"title": "Deep Learning Specialization", "issuer": "DeepLearning.AI"},
        {"title": "DevOps Engineering", "issuer": "Linux Foundation"}
    ]
    
    for user in users:
        # Для каждого пользователя создаем от 1 до 3 сертификатов
        num_certificates = random.randint(1, 3)
        selected_certificates = random.sample(certificate_data, num_certificates)
        
        for cert_data in selected_certificates:
            # Создаем случайную дату выдачи (в пределах последних 3 лет)
            days_ago = random.randint(1, 1095)
            issue_date = timezone.now().date() - timedelta(days=days_ago)
            
            # Создаем сертификат
            Certificate.objects.create(
                user=user,
                title=cert_data["title"],
                issuer=cert_data["issuer"],
                description=generate_paragraph() if random.random() > 0.3 else "",
                issue_date=issue_date,
                link=f"https://example.com/certificates/{cert_data['issuer'].lower().replace(' ', '-')}/{cert_data['title'].lower().replace(' ', '-')}" if random.random() > 0.3 else ""
            )
        
        print(f"Добавлено {num_certificates} сертификатов для пользователя {user.get_full_name()}")

def create_achievements_for_users(users):
    """Создание достижений для пользователей"""
    print("Создание достижений для пользователей...")
    
    # Список возможных достижений
    achievement_data = [
        {"title": "Победитель хакатона", "organizer": "HackUniversity"},
        {"title": "Участник международной олимпиады", "organizer": "International Olympiad in Informatics"},
        {"title": "Финалист конкурса стартапов", "organizer": "Startup Village"},
        {"title": "Лауреат премии молодых ученых", "organizer": "Министерство образования"},
        {"title": "Победитель в номинации 'Лучший проект'", "organizer": "IT Contest"},
        {"title": "Участник всероссийской конференции", "organizer": "Russian AI Conference"},
        {"title": "Стипендиат правительственной программы", "organizer": "Правительство РФ"},
        {"title": "Автор научной публикации", "organizer": "IEEE Conference"},
        {"title": "Победитель кейс-чемпионата", "organizer": "Case Championship"},
        {"title": "Участник международного форума", "organizer": "Digital Summit"},
        {"title": "Спикер технической конференции", "organizer": "TechTalks"},
        {"title": "Призер соревнования по программированию", "organizer": "ACM ICPC"}
    ]
    
    places = ["1 место", "2 место", "3 место", "Финалист", "Призер", "Участник", "Лауреат"]
    
    for user in users:
        # Для каждого пользователя создаем от 0 до 3 достижений
        num_achievements = random.randint(0, 3)
        if num_achievements == 0:
            continue
            
        selected_achievements = random.sample(achievement_data, num_achievements)
        
        for achievement_info in selected_achievements:
            # Создаем случайную дату (в пределах последних 4 лет)
            days_ago = random.randint(1, 1460)
            date = timezone.now().date() - timedelta(days=days_ago)
            
            # Создаем достижение
            Achievement.objects.create(
                user=user,
                title=achievement_info["title"],
                organizer=achievement_info["organizer"],
                description=generate_paragraph() if random.random() > 0.3 else "",
                date=date,
                place=random.choice(places) if random.random() > 0.4 else ""
            )
        
        print(f"Добавлено {num_achievements} достижений для пользователя {user.get_full_name()}")

def create_reviews_for_students(users):
    """Создание отзывов для студентов"""
    print("Создание отзывов для студентов...")
    
    # Получаем студентов и преподавателей
    students = [user for user in users if user.user_type == 'student']
    teachers = [user for user in users if user.user_type == 'teacher']
    
    # Если нет преподавателей, выходим из функции
    if not teachers:
        print("Нет преподавателей для создания отзывов")
        return
    
    for student in students:
        # Для каждого студента создаем от 0 до 2 отзывов
        num_reviews = random.randint(0, 2)
        if num_reviews == 0:
            continue
            
        # Выбираем случайных преподавателей для отзывов
        selected_teachers = random.sample(teachers, min(num_reviews, len(teachers)))
        
        for teacher in selected_teachers:
            # Создаем отзыв
            Review.objects.create(
                student=student,
                reviewer=teacher,
                text=generate_paragraph(),
                rating=random.randint(3, 5),  # Оценка от 3 до 5
                is_approved=True  # Отзыв уже одобрен
            )
        
        print(f"Добавлено {num_reviews} отзывов для студента {student.get_full_name()}")

def create_posts_for_projects(users, projects):
    """Создание постов в ленте новостей на основе проектов"""
    print("Создание постов в ленте новостей...")
    
    # Выбираем случайные проекты для постов (70% от всех проектов)
    num_posts = int(len(projects) * 0.7)
    selected_projects = random.sample(projects, num_posts)
    
    all_posts = []
    
    for project in selected_projects:
        # Создаем пост о проекте
        post = Post.objects.create(
            author=project.user,
            project=project,
            content=generate_paragraph(),
            created_at=project.updated_at + timedelta(hours=random.randint(1, 24))
        )
        
        all_posts.append(post)
        
        # Добавляем лайки к посту
        potential_likers = [user for user in users if user != project.user]
        num_likes = random.randint(0, min(10, len(potential_likers)))
        if num_likes > 0:
            likers = random.sample(potential_likers, num_likes)
            post.likes.add(*likers)
    
    print(f"Создано {len(all_posts)} постов в ленте новостей")
    
    # Добавляем комментарии к постам
    create_comments_for_posts(users, all_posts)

def create_comments_for_posts(users, posts):
    """Создание комментариев к постам"""
    print("Создание комментариев к постам...")
    
    # Возможные тексты комментариев
    comment_texts = [
        "Отличный проект! Мне очень понравилась реализация.",
        "Интересная идея, как вы пришли к такому решению?",
        "Впечатляет! А какие технологии использовали?",
        "Хороший результат, но можно было бы улучшить UI.",
        "Круто! Планируете дальше развивать проект?",
        "Здорово, что вы поделились этим проектом!",
        "Очень полезный инструмент, буду использовать.",
        "А как вы решили проблему производительности?",
        "Отличная работа! Желаю успехов в дальнейшем развитии.",
        "Какие планы на будущее у этого проекта?",
        "Мне нравится дизайн, очень современно.",
        "Как долго вы работали над этим?",
        "Впечатляющие результаты, особенно учитывая сложность задачи.",
        "Хотелось бы увидеть больше подробностей о реализации."
    ]
    
    total_comments = 0
    
    for post in posts:
        # Для каждого поста создаем от 0 до 5 комментариев
        num_comments = random.randint(0, 5)
        if num_comments == 0:
            continue
            
        # Выбираем случайных пользователей для комментариев
        potential_commenters = [user for user in users if user != post.author]
        commenters = random.sample(potential_commenters, min(num_comments, len(potential_commenters)))
        
        for commenter in commenters:
            # Создаем комментарий
            Comment.objects.create(
                post=post,
                author=commenter,
                text=random.choice(comment_texts),
                created_at=post.created_at + timedelta(hours=random.randint(1, 48))
            )
            
            total_comments += 1
    
    print(f"Добавлено {total_comments} комментариев к постам")

if __name__ == "__main__":
    try:
        create_test_data()
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}") 