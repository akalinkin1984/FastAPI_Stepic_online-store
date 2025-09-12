Работа с Alembic:  
синхронные:  
alembic init app/migrations - создать среду миграций в каталоге app/migrations/  
alembic revision --autogenerate -m "Initial migration" - первая миграция  
alembic upgrade 4a7fc2a8d136 - выполнить миграцию определенной ревизии(head - последняя миграция)  
alembic upgrade +2 - две версии включая текущую для апгрейда  
alembic downgrade -1 - на предыдущую для даунгрейда  
alembic current - получить информацию о текущей версии  
alembic history --verbose - история миграций, более подробнее можно почитать в документации.  
alembic downgrade base даунгрейд - в самое начало миграций  
alembic upgrade head - применение самой последней созданной миграции  
асинхронные:  
alembic init -t async app/migrations - создать среду миграций в каталоге app/migrations/  
alembic revision --autogenerate -m "Initial migration" - создать миграции  
alembic upgrade head - выполнить миграции  
  
Запуск приложения:  
uvicorn app.main:app --port 8000 --reload  
  
Файл .env:  
PG_NAME=*****  
PG_USER=*****  
PG_PASSWORD=*****  
PG_HOST=*****  
PG_PORT=*****  
  
SECRET_KEY=*****  
ALGORITHM=*****  


Запуск с docker-compose:  
docker-compose down -v - удалим предыдущий контейнер  
docker-compose up -d --build - выполним билд и запуск наших контейнеров еще раз  
docker-compose exec web alembic upgrade head - выполним миграции
docker-compose exec db psql --username=postgres_user --dbname=postgres_database  
-   
- \l убедимся, что были созданы таблицы нашего проекта FastAPI  
- 

