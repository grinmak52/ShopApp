# MicroShop

Учебное микросервисное приложение интернет-магазина на **FastAPI**: асинхронный SQLAlchemy, PostgreSQL, Redis, RabbitMQ, JWT-аутентификация, событийное взаимодействие и **Saga** с компенсирующими действиями для оформления заказа. Всё запускается одной командой через Docker Compose, единая точка входа это Nginx.

## Возможности

- Регистрация, вход, JWT (FastAPI Users), роль администратора в токене
- Каталог товаров: категории, поиск, фильтры, сортировка, пагинация, кеш в Redis
- Корзина в Redis (hash), проверка товара в Catalog при добавлении
- Заказы со снимком товара (название и цена на момент покупки)
- Резервирование остатков, подтверждение списания, освобождение резерва
- Mock-оплата с настраиваемой вероятностью успеха, возвраты
- Уведомления о заказах и платежах с API для чтения
- Saga: таймаут заказов, истечение резервов, возврат за отменённый заказ
- Nginx: маршрутизация и rate limiting

## Архитектура

```
                          Client
                            │
                            ▼
                  ┌───────────────────┐
                  │  Nginx  (:80)     │  routing, rate limiting
                  └─────────┬─────────┘
    ┌────────┬───────┬──────┼──────┬──────────┬──────────┬──────────────┐
    ▼        ▼       ▼      ▼      ▼          ▼          ▼              
  Auth    Catalog   Cart  Order  Inventory  Payment  Notification
    │        │       │      │       │          │          │
 shop_user shop_   Redis  shop_  shop_      shop_      shop_
          catalog  (db 1) order  inventory  payment    notification
          + Redis
          (db 0)
                              │
                              ▼
                    RabbitMQ (exchange shop.events)
```

Каждый сервис владеет своей БД, внешних ключей между сервисами нет. Синхронное взаимодействие идёт по HTTP (Order → Cart, Order → Cart/Catalog), асинхронное через RabbitMQ.

## Сервисы

| Сервис | Порт (dev) | Хранилище | Назначение |
|---|---|---|---|
| Auth | 8000 | `shop_user` | пользователи, JWT |
| Catalog | 8001 | `shop_catalog`, Redis db 0 | товары и категории, кеш |
| Cart | 8002 | Redis db 1 | корзина |
| Order | 8003 | `shop_order` | заказы, оркестрация Saga |
| Inventory | 8004 | `shop_inventory` | остатки и резервы |
| Payment | 8005 | `shop_payment` | оплата (mock), возвраты |
| Notification | 8006 | `shop_notification` | уведомления |
| Nginx | 80 | нет | единая точка входа |

Внутри Docker все сервисы слушают порт `8000`, наружу через Nginx доступен только порт `80`.

## Saga оформления заказа

```
Client ─POST /orders─▶ Order (PENDING) ──order.created──▶ Inventory
                                                              │
                         ┌──── stock.reservation_failed ◀─────┤
                         ▼                                    │ stock.reserved
                  Order → CANCELLED                           ▼
                                                          Payment
                         ┌──────── payment.failed ◀──────────┤
                         ▼                                   │ payment.succeeded
              Order → CANCELLED                              ▼
              Inventory: release reserve           Order → CONFIRMED
                                                   Inventory: commit sale
```

### События (routing key)

| Событие | Публикует | Слушают |
|---|---|---|
| `order.created` | Order | Inventory, Notification |
| `stock.reserved` | Inventory | Payment |
| `stock.reservation_failed` | Inventory | Order |
| `payment.succeeded` | Payment | Order, Inventory, Notification |
| `payment.failed` | Payment | Order, Inventory, Notification |
| `payment.refunded` | Payment | |
| `order.confirmed` | Order | Notification |
| `order.cancelled` | Order | Inventory, Payment, Notification |

Все сообщения идут через topic exchange `shop.events`. Очереди durable, сообщения persistent.

### Компенсации и защита от сбоев

| Ситуация | Реакция |
|---|---|
| Нет остатка | заказ `CANCELLED`, платёж не создаётся |
| Оплата не прошла | заказ `CANCELLED`, резерв освобождается |
| Заказ завис в `PENDING` дольше таймаута (15 мин) | Order отменяет его |
| Платёж пришёл за уже отменённый заказ | Order повторно публикует `order.cancelled`, Payment делает возврат |
| Резерв в `RESERVED` дольше TTL (20 мин) | Inventory переводит в `EXPIRED` и освобождает остаток |

Все обработчики идемпотентны: статусы меняются атомарным `UPDATE ... WHERE status = ...`, у платежей уникальный `order_id`, у уведомлений уникальная пара `(order_id, type)`. Повторная доставка сообщений безопасна.

## Стек

Python, FastAPI, Pydantic / Pydantic Settings, SQLAlchemy 2.x (async), Alembic, FastAPI Users, PostgreSQL, Redis, RabbitMQ (aio-pika), HTTPX, Nginx, Docker, Docker Compose, Poetry.

## Быстрый старт

### Требования

- Docker Desktop (Docker Compose v2)
- PostgreSQL на хосте с шестью базами: `shop_user`, `shop_catalog`, `shop_inventory`, `shop_order`, `shop_payment`, `shop_notification`
- Для подключения из контейнеров PostgreSQL должен слушать не только `localhost`: `listen_addresses = '*'` в `postgresql.conf` и разрешающая строка в `pg_hba.conf` (например, `host all all 0.0.0.0/0 scram-sha-256`). Для локальной разработки это допустимо, на доступной из сети машине так делать нельзя.

### Настройка

Создай файл `.env` в корне проекта (он в `.gitignore`):

```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
JWT_SECRET=<длинная случайная строка>

# необязательные параметры для экспериментов
PAYMENT_SUCCESS_RATE=1
ORDER_PENDING_TIMEOUT=900
RESERVATION_TTL=1200
```

Секрет генерируется так:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

`JWT_SECRET` один для всех сервисов: Auth подписывает токены, остальные проверяют подпись.

### Запуск

```bash
docker compose up --build -d
docker compose ps
```

Миграции каждый сервис применяет сам при старте (`alembic upgrade head`). API доступно на `http://localhost`.

Файл `docker-compose.override.yml` открывает порты сервисов 8000–8006 для разработки (Swagger на `http://localhost:8001/docs` и так далее). Запуск без него:

```bash
docker compose -f docker-compose.yml up -d
```

В этом режиме наружу открыты только Nginx (80) и панель RabbitMQ (`http://localhost:15672`, `guest` / `guest`).

### Сделать пользователя администратором

Регистрация всегда создаёт обычного пользователя. Права выдаются в БД `shop_user`:

```sql
UPDATE users SET is_superuser = true WHERE email = 'admin@example.com';
```

После этого нужно войти заново, потому что роль записывается в токен при выдаче.

## API

Все запросы идут через Nginx: `http://localhost/api/v1/...`. Защищённые методы требуют заголовок `Authorization: Bearer <token>`.

| Группа | Основные маршруты | Доступ |
|---|---|---|
| Auth | `POST /auth/register`, `POST /auth/jwt/login`, `GET/PATCH /auth/users/me` | публично / пользователь |
| Catalog | `GET /products`, `GET /products/{id}`, `GET /categories` | публично |
| Catalog (запись) | `POST/PATCH/DELETE /products`, `/categories` | администратор |
| Cart | `GET/DELETE /cart`, `POST /cart/items`, `PATCH/DELETE /cart/items/{product_id}` | пользователь |
| Orders | `POST /orders`, `GET /orders`, `GET /orders/{id}` | пользователь |
| Inventory | `GET /inventory/{product_id}`, `POST/PATCH /inventory` | чтение любой пользователь, запись администратор |
| Payments | `GET /payments/order/{order_id}` | пользователь |
| Notifications | `GET /notifications`, `GET /notifications/unread-count`, `PATCH /notifications/{id}/read`, `POST /notifications/read-all` | пользователь |

Параметры списка товаров: `q`, `category_id`, `min_price`, `max_price`, `sort` (`price`, `-price`, `name`, `-created_at`), `limit`, `offset`.

Чужие заказы, платежи и уведомления возвращают `404`, а не `403`.

### Пример сценария

1. `POST /auth/register`, затем `POST /auth/jwt/login` (форма: `username` = email, `password`)
2. Администратор: `POST /categories`, `POST /products`, `POST /inventory` с остатком
3. Пользователь: `POST /cart/items` с `product_id` и `quantity`
4. `POST /orders` с `{"shipping_address": "..."}`: заказ `PENDING`
5. Через секунду `GET /orders/{id}` показывает `CONFIRMED`, а `GET /notifications` содержит три уведомления

Чтобы проверить компенсации, поставь `PAYMENT_SUCCESS_RATE=0` и пересоздай Payment: `docker compose up -d payment`.

## Структура проекта

```
ShopApp/
├── docker-compose.yml
├── docker-compose.override.yml   # порты сервисов для разработки
├── nginx/nginx.conf
├── auth-service/
├── catalog-service/
├── cart-service/
├── order-service/
├── inventory-service/
├── payment-service/
└── notification-service/
    ├── Dockerfile
    ├── pyproject.toml
    └── src/
        ├── main.py
        ├── alembic/            # свои миграции у каждого сервиса
        ├── api/                # роутеры, зависимости, проверка JWT
        ├── database/           # конфиг, модели, DatabaseHelper
        ├── repositories/       # доступ к данным
        ├── service/            # бизнес-логика
        ├── schemas/            # Pydantic-схемы
        ├── messaging/          # брокер, события, consumer'ы
        └── workers/            # фоновые задачи (Order, Inventory)
```

## Принятые решения

- **База на сервис.** Один сервис не обращается к таблицам другого. Связь только через `user_id` и `product_id` без внешних ключей.
- **JWT проверяется в каждом сервисе.** Секрет общий, `user_id` берётся из `sub`, флаг `is_superuser` добавляется в токен кастомной стратегией. Nginx токены не разбирает.
- **Корзина как Redis hash.** Ключ `cart:{user_id}`, поле `product_id`, значение `quantity`. `HINCRBY` атомарный, поэтому параллельные запросы не затирают друг друга. TTL не задан.
- **Цены только с сервера.** Клиент передаёт лишь адрес доставки. Order берёт актуальные цены в Catalog и сохраняет снимок в `order_items`.
- **Резервирование без гонок.** `UPDATE inventory ... WHERE quantity - reserved_quantity >= qty` проверяет остаток и резервирует одной операцией, плюс `CHECK`-ограничения в БД.
- **Деньги в `Numeric`.** Цены никогда не хранятся как `float`, в событиях суммы передаются строками.
- **Мягкое удаление товаров.** `DELETE /products/{id}` ставит `is_active = false`, чтобы не оставлять висячих ссылок в заказах и остатках.
- **Кеш Catalog (cache-aside).** Карточка товара, список и категории. Для списков используется версия в ключе, которая увеличивается при любой записи. При недоступности Redis каталог продолжает работать напрямую с БД.

## Известные ограничения

- Событие публикуется после коммита, без паттерна Transactional Outbox. Сбой между этими двумя шагами может потерять событие.
- Роль и статус пользователя «замораживаются» в JWT до истечения токена (по умолчанию 30 минут). Logout токен не отзывает, для этого потребуется чёрный список в Redis.
- При ошибке обработки сообщение возвращается в очередь с паузой 5 секунд, без dead-letter очереди и лимита повторов.
- Возврат платежа реализован для mock-провайдера. С реальным провайдером нужен промежуточный статус `REFUND_PENDING` и повтор при сбое.
- Уведомления только сохраняются в БД. Email, Telegram и WebSocket добавляются в `NotificationService.create`.
- Автотесты не написаны.
- Один экземпляр брокера и баз, без отказоустойчивости.

## Что можно доработать

- Transactional Outbox и dead-letter очереди
- Чёрный список токенов в Redis
- Автотесты (pytest-asyncio, HTTPX)
- Реальный платёжный провайдер
- HTTPS в Nginx
- Метрики и трассировка (Prometheus, OpenTelemetry)
