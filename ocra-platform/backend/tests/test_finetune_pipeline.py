import os
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scidl.data_downloader import data_downloader
from app.services.scidl.finetune_engine import finetune_engine
from app.services.scidl.model_registry import scidl_registry

client = TestClient(app)


class TestFineTunePipeline(unittest.TestCase):

    def test_synthetic_data_download(self):
        res = data_downloader.create_synthetic_netcdf("test_indian_ocean.nc")
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["file_path"]))

    def test_fine_tuning_execution(self):
        res = finetune_engine.run_fine_tuning(
            base_model_name="SFNO",
            dataset_path="data/test_indian_ocean.nc",
            epochs=3,
            learning_rate=1e-4
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["epochs_completed"], 3)
        self.assertTrue(os.path.exists(res["checkpoint_saved"]))

    def test_finetuned_model_registry_inference(self):
        # Infer fine-tuned SFNO Indian Ocean model
        res = scidl_registry.predict(
            lat=13.0827,
            lon=80.2707,
            forecast_hours=24,
            model_name="SFNO_FINETUNED_INDIAN_OCEAN"
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("predictions", res)

        # Infer fine-tuned PINN Corrector Indian Ocean model
        res_pinn = scidl_registry.predict(
            lat=13.0827,
            lon=80.2707,
            forecast_hours=24,
            model_name="PINN_CORRECTOR_INDIAN_OCEAN"
        )
        self.assertEqual(res_pinn["status"], "success")
        self.assertIn("thermocline_depth_m", res_pinn["predictions"])

    def test_api_finetune_endpoints(self):
        # Trigger fine-tuning start endpoint
        payload = {
            "base_model_name": "FOURCASTNET",
            "epochs": 2,
            "learning_rate": 1e-4,
            "use_amp": True
        }
        start_resp = client.post("/api/finetune/start", json=payload)
        self.assertEqual(start_resp.status_code, 200)
        data = start_resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["epochs_completed"], 2)

        # Query status endpoint
        status_resp = client.get("/api/finetune/status")
        self.assertEqual(status_resp.status_code, 200)
        status_data = status_resp.json()
        self.assertEqual(status_data["status"], "completed")

    def test_api_data_download_endpoint(self):
        payload = {
            "source": "SYNTHETIC",
            "min_lon": 45.0,
            "max_lon": 100.0,
            "min_lat": -10.0,
            "max_lat": 30.0
        }
        resp = client.post("/api/data/download", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")


if __name__ == "__main__":
    unittest.main()
