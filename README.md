make build - once
make up - start
make superuser
make down - stop

API: http://localhost:8000/api/
API Docs (Swagger): http://localhost:8000/api/docs/
Django Admin: http://localhost:8000/admin/  ingazo@admin.com Admin123.

npm install
npm run dev


FOR DB:
docker run --rm \
  --network backend_ingazo_network \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4

  Then open http://localhost:5050 and connect with:
Host: db
Port: 5432
User: ingazo
Password: ingazo_secret

