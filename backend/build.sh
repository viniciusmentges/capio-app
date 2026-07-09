#!/usr/bin/env bash
# exit on error
set -o errexit

echo "[CAPIO BUILD] Instalando dependências do Python..."
pip install -r requirements.txt

echo "[CAPIO BUILD] Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "[CAPIO BUILD] Aplicando migrações e sincronizando acervo editorial..."
python manage.py migrate

echo "[CAPIO BUILD] Garantindo sincronização do acervo de 20 emoções e 147 devocionais..."
python manage.py import_editorial_staging

echo "[CAPIO BUILD] Build concluído com sucesso!"
