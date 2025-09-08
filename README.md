# Zoom Local Secretary (WASAPI)

Локальный «секретарь» для Zoom-встреч, который перехватывает системный звук Windows, 
транскрибирует русскую речь офлайн через [faster-whisper](https://github.com/guillaumekln/faster-whisper)
и делает краткое резюме встречи через локальный сервер [LM Studio](https://lmstudio.ai/).

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
| `POST /start_recording` | Начать запись системного аудио. |
| `POST /stop_recording` | Остановить запись и сохранить `recordings/meeting.wav`. |
| `POST /transcribe_and_summarize` | Запустить распознавание и резюме. Сохраняет `recordings/transcript.txt` и `recordings/summary.md`. |

Примеры:
```bash
# начать запись
curl -X POST http://localhost:8000/start_recording

# остановить запись
curl -X POST http://localhost:8000/stop_recording

# транскрипция и резюме
curl -X POST http://localhost:8000/transcribe_and_summarize
```

## Фронтенд

В каталоге `frontend` есть простой статический интерфейс. Запустите сервер, а затем откройте файл `frontend/index.html` в браузере (или поднимите локальный HTTP-сервер через `python -m http.server` внутри каталога). Интерфейс позволяет запускать и останавливать запись, а также запускать распознавание и отображать транскрипт и резюме.

## Файлы
- `recordings/meeting.wav` – исходное аудио
- `recordings/transcript.txt` – расшифровка речи
- `recordings/summary.md` – краткое резюме встречи
