# django_chatbot

> **WARNING:** This repository may be unstable or non-functional. Use at your own risk.

A chatbot built with Django REST Framework (backend) and React (frontend). The bot conducts conversations using preloaded dialog trees defined as JSON questionnaires. Responses are driven by the current node in the tree — the user picks from predefined options.

## Stack

- **Backend:** Django + Django REST Framework, SQLite
- **Frontend:** React
- **Infrastructure:** Docker Compose

## Running

```bash
docker-compose build
docker-compose up
```

- Backend API: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:3000

Before chatting, load questionnaires via the Upload endpoint in the browsable DRF API at http://127.0.0.1:8000/upload/.

## Chat API Contract

- `GET /chat/questionnaires/`
  Returns available questionnaires:
  `[{ "id": 1, "name": "Questionnaire Name" }]`

- `POST /chat/start/`
  Request:
  `{ "questionnaire_id": 1 }`
  Response:
  `{ "session_id": "...", "question": { "id": 10, "text": "...", "answers": ["Yes", "No"], "is_leaf": false }, "completed": false }`

- `POST /chat/answer/`
  Request:
  `{ "session_id": "...", "question_id": 10, "answer": "Yes" }`
  Response:
  `{ "session_id": "...", "question": { "id": 11, "text": "...", "answers": [], "is_leaf": true }, "completed": true }`

## Questionnaire Format

Questionnaires are JSON files defining a dialog tree. Each node has a `text` (bot message) and optional `response` map (user choices → next nodes):

```json
[
  {
    "name": "My Questionnaire",
    "tree": {
      "text": "Bot question here",
      "response": {
        "Option A": {
          "text": "Bot reply to A"
        },
        "Option B": {
          "text": "Another question",
          "response": {
            "Yes": { "text": "Done." },
            "No":  { "text": "Ok." }
          }
        }
      }
    }
  }
]
```

See `data/questionnaire_example_1.json` and `data/questionnaire_example_2.json` for full examples.

## License

See `LICENSE`.
