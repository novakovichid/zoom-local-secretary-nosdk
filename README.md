# Zoom Local Secretary (WASAPI)

Локальный «секретарь» для Zoom-встреч, который перехватывает системный звук Windows
и переводит его в текст офлайн через [faster-whisper](https://github.com/guillaumekln/faster-whisper).

## Установка

1. Установите Python 3.10+ и необходимые C-библиотеки для `sounddevice` и `faster-whisper`.
2. Перейдите в каталог `backend` и установите зависимости:
   ```bash
   pip install -e .
   ```
3. Скопируйте файл `.env.example` в `.env` и при необходимости измените параметры.

## Запуск сервера

```bash
uvicorn backend.src.server:app --reload
```

## Использование API

| Маршрут | Описание |
|---------|----------|
| `POST /api/start_recording` | Начать запись системного аудио. |
| `POST /api/stop_recording` | Остановить запись и сохранить `recordings/meeting.wav`. |
| `POST /api/transcribe` | Запустить распознавание. Сохраняет `recordings/transcript.txt`. |

Примеры:
```bash
# начать запись
curl -X POST http://localhost:8000/api/start_recording

# остановить запись
curl -X POST http://localhost:8000/api/stop_recording

# транскрипция
curl -X POST http://localhost:8000/api/transcribe
```

## Интерфейс

После запуска сервера откройте [http://localhost:8000/](http://localhost:8000/) — будет отображён простой веб-интерфейс, позволяющий управлять записью, запускать распознавание и просматривать транскрипт.

## Файлы
- `recordings/meeting.wav` – исходное аудио
- `recordings/transcript.txt` – расшифровка речи с временными метками
