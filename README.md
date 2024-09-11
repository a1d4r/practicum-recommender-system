# Рекомендательная система

# Схема сервиса

![Image alt](https://github.com/a1d4r/practicum-recommender-system/blob/main/diagrams/Scheme.png)

## Ссылки:
1. Сервис авторизации: **https://github.com/Fox13th/Auth_Service**
2. Ссылка на API CRUD закладок, лайков и рецензий: **https://github.com/EsterTar/ReviewHub**
3. Сервис выдачи контента: **https://github.com/Fox13th/Sprint_async_api**
4. Сервис UGC: **https://github.com/Fox13th/ugc_service**



## Запуск

### Запуск API
Из директории  `recommendation_api`:
```bash
docker compose up -d
```

### Запуск движка похожих кино

```bash
docker compose up -d
```

Для локальной разработки:

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build
```

### Запуск движка рекомендаций пользователя
Из директории  `recommend-engine-collabarative`:
```bash
docker compose up -d
```

