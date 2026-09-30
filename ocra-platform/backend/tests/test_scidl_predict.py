import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PredictRequest
from app.services.scidl.model_registry import scidl_registry
from app.agents.scidl import run_scidl_agent

client = TestClient(app)


class TestSciDLPredictions(unittest.TestCase):

    def test_model_registry_list(self):
        models_resp = scidl_registry.list_models()
        self.assertGreaterEqual(models_resp.total, 5)
        model_ids = [m.id for m in models_resp.models]
        self.assertIn("SFNO", model_ids)
        self.assertIn("FOURCASTNET", model_ids)
        self.assertIn("GRAPHCAST", model_ids)
        self.assertIn("AURORA", model_ids)
        self.assertIn("PINN_SWIN", model_ids)

    def test_sfno_prediction(self):
        res = scidl_registry.predict(lat=13.0827, lon=80.2707, forecast_hours=24, model_name="SFNO")
        self.assertEqual(res["status"], "success")
        self.assertIn("predictions", res)
        self.assertIn("swh", res["predictions"])
        self.assertIn("wind_speed_ms", res["predictions"])

    def test_pinn_swin_prediction(self):
        res = scidl_registry.predict(lat=13.0827, lon=80.2707, forecast_hours=12, model_name="PINN_SWIN")
        self.assertEqual(res["status"], "success")
        self.assertIn("thermocline_depth_m", res["predictions"])
        self.assertIn("wave_power_kw_m", res["predictions"])

    def test_api_models_endpoint(self):
        response = client.get("/api/models")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("models", data)
        self.assertGreaterEqual(data["total"], 5)

    def test_post_predict_endpoint(self):
        payload = {
            "lat": 13.0827,
            "lon": 80.2707,
            "forecast_hours": 24,
            "variables": ["u10", "v10", "msl", "t2m", "swh"],
            "model_name": "SFNO",
            "data_source": "GFS"
        }
        response = client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["coordinates"]["lat"], 13.0827)
        self.assertIn("predictions", data)
        self.assertIn("swh", data["predictions"])

    def test_post_predict_pinn_endpoint(self):
        payload = {
            "lat": 15.0,
            "lon": 82.0,
            "forecast_hours": 48,
            "model_name": "PINN_SWIN"
        }
        response = client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("thermocline_depth_m", data["predictions"])

    def test_post_predict_batch_endpoint(self):
        payload = {
            "points": [
                {"lat": 13.0827, "lon": 80.2707, "point_id": "Chennai_Port"},
                {"lat": 15.0000, "lon": 82.0000, "point_id": "Offshore_BOB"}
            ],
            "forecast_hours": 24,
            "model_name": "SFNO"
        }
        response = client.post("/api/predict/batch", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_points"], 2)
        self.assertEqual(len(data["results"]), 2)


if __name__ == "__main__":
    unittest.main()
