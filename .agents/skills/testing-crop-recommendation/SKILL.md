---
name: testing-crop-recommendation
description: How to run and end-to-end test the Smart Agriculture app (crop recommendation UI + Flask backend) on a machine with no Arduino hardware attached.
---

# Testing the Smart Agriculture app locally

## Services

- Backend: `pip install -r backend/requirements.txt`, then `cd backend && python crop_recommendation.py`
  (Flask on 127.0.0.1:5001).
- Frontend: `cd frontend && npm install && BROWSER=none npm start` (CRA on :3000, hardcoded to call
  `http://127.0.0.1:5001`). CRA takes ~40-60s for the first compile; poll `curl -o /dev/null -w "%{http_code}" localhost:3000`
  instead of guessing.

## The Arduino blocker (most important)

`POST /crop-recommend` returns HTTP 400 unless the backend's in-memory `arduino_data` dict has
non-null `temperature`, `humidity` and `soil_moisture`, which normally arrives over a serial port
from real hardware. The UI's "🌱 Get Recommendations" button is also **disabled** until
`GET /sensor` reports `arduino_status.connected === true`.

On a VM with no Arduino, run the app through a **scratch harness kept outside the repo** (do not
commit it) that imports the backend module and injects sensor values:

```python
# /tmp/run_backend_fake_arduino.py
import sys
from datetime import datetime
sys.path.insert(0, '<repo>/backend')
import crop_recommendation as cr
from flask import request, jsonify

cr.arduino_data.update({'temperature': 21.0, 'humidity': 82.0, 'soil_moisture': 45.0})
cr.arduino_connection_status.update({'connected': True, 'message': 'Simulated Arduino (test harness)',
                                     'port': 'SIM', 'last_update': datetime.now().isoformat()})

@cr.app.route('/_test/sensor', methods=['POST'])   # change readings mid-test
def _test_sensor():
    data = request.get_json(force=True) or {}
    for k in ('temperature', 'humidity', 'soil_moisture'):
        if k in data:
            cr.arduino_data[k] = None if data[k] is None else float(data[k])
    return jsonify({'arduino_data': cr.arduino_data})

cr.app.run(host='0.0.0.0', port=5001)
```

The extra `/_test/sensor` route is what makes temperature/humidity-dependent predictions testable
through the UI: the front end polls `GET /sensor` every 2s, so a POST to `/_test/sensor` is
reflected in the "Live Arduino Sensors" panel within ~2 seconds without reloading.
A socat virtual serial pair emitting `{"temperature":21.0,...}` JSON lines is an alternative if you
need to exercise the serial parsing code itself.

## UI path

Dashboard → "Smart Crop Recommendation" card → "Get Started →". The form has Nitrogen, Phosphorus,
Potassium and pH number inputs (with `min`/`max` attributes 0-200 / 0-100 / 0-300 / 4-10, so values
outside those ranges may be blocked by the browser); submit with "🌱 Get Recommendations".
Results render as Top Recommendation, "All Crop Recommendations" (top 5 by probability) and
"Soil Analysis Summary". In-app return via "← Back to Dashboard".

Beware: submitting scrolls the page, so re-locate the input boxes with a fresh screenshot before
typing the next set of values — reusing stale coordinates silently types into the wrong field.

## Inputs that produce distinct crops

Useful for proving predictions actually vary with input (model features are
nitrogen, phosphorus, potassium, ph, temperature, humidity — soil moisture is NOT a model feature):

| N | P | K | pH | temp/hum | expected top crop |
|---|---|---|----|----------|-------------------|
| 90 | 42 | 43 | 6.5 | 21/82 | Rice (~98.6%) |
| 100 | 17 | 30 | 6.2 | 27/60 | Coffee (~94.2%) |
| 20 | 100 | 200 | 5.9 | 23/92 | Apple (~56%) |
| 0 | 0 | 0 | 4 | 23/92 | Orange (~83%) |
| 200 | 100 | 300 | 10 | 23/92 | Banana (~31%, Poor) |

Exact percentages shift whenever `crop_model.pkl` is retrained — assert on the crop name and on the
score being plausible/sub-100%, not on an exact number.

## Error paths worth checking without the UI

- Missing fields → 400 JSON with `required_features`.
- Any sensor value null → 400 JSON "Arduino sensor data not available".
- Model failed to load (`cr.crop_model = None` in a scratch instance) → **500** with a clean JSON
  error body. This is intentional (server-side misconfiguration), not a crash.

## Navigation

`frontend/src/App.js` switches views and syncs `window.history.state.view` via pushState/popstate,
so browser Back/Forward move between views and a reload restores the current view. Components
remount on popstate, so form values and results reset — that is expected, not a bug. Exhausting the
app's history entries leaves the site to the previous page/new-tab, which is normal browser behavior.

## Devin Secrets Needed

None — everything runs locally with no credentials.
