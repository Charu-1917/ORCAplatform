"""
Direct Python Script: Fine-Tuning SFNO / PINN Models on In-Memory Copernicus & ARGO Data

Usage:
  PYTHONPATH=. python3 train_indian_ocean.py --epochs 10 --model SFNO
"""

import os
import argparse
import logging
from app.services.scidl.data_downloader import data_downloader
from app.services.scidl.finetune_engine import finetune_engine
from app.services.scidl.model_registry import scidl_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_indian_ocean")

def main():
    parser = argparse.ArgumentParser(description="Direct Python Fine-Tuning Script for Indian Ocean Models")
    parser.add_argument("--model", type=str, default="SFNO", help="Base model (SFNO, FOURCASTNET, PINN_SWIN)")
    parser.add_argument("--epochs", type=int, default=5, help="Number of fine-tuning epochs")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--source", type=str, default="COPERNICUS", help="Data source (COPERNICUS, ARGO, SYNTHETIC)")
    args = parser.parse_args()

    logger.info("================================================================================")
    logger.info("🌊 DIRECT PYTHON FINE-TUNING FOR INDIAN OCEAN DEEP LEARNING SURROGATES 🌊")
    logger.info("================================================================================")

    # 1. Direct Python Data Import
    logger.info(f"Step 1: Direct Python Data Import (Source: {args.source})...")
    if args.source.upper() == "ARGO":
        data_res = data_downloader.fetch_argo_profiles(
            bbox=[45.0, 100.0, -10.0, 30.0],
            depth_range=[0.0, 2000.0],
            date_range=["2025-01", "2025-02"]
        )
    elif args.source.upper() == "COPERNICUS":
        data_res = data_downloader.fetch_copernicus_subset(
            dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
            variables=["thetao", "so", "uo", "vo"],
            min_lon=45.0, max_lon=100.0, min_lat=-10.0, max_lat=30.0
        )
    else:
        data_res = data_downloader.create_synthetic_netcdf()

    logger.info(f"✅ Data Loaded: {data_res['source']} -> {data_res['file_path']}")

    # 2. Run Layer-Freezing Fine-Tuning
    logger.info(f"Step 2: Training {args.model} model for {args.epochs} epochs (LR={args.lr})...")
    ft_res = finetune_engine.run_fine_tuning(
        base_model_name=args.model,
        dataset_path=data_res["file_path"],
        epochs=args.epochs,
        learning_rate=args.lr,
        use_amp=True
    )

    logger.info(f"✅ Fine-Tuning Completed!")
    logger.info(f"   • Initial Loss: {ft_res['initial_loss']:.6f}")
    logger.info(f"   • Final Loss:   {ft_res['final_loss']:.6f}")
    logger.info(f"   • Saved Checkpoint: {ft_res['checkpoint_saved']}")

    # 3. Test Inference on Fine-Tuned Model
    logger.info("Step 3: Verification Inference on Fine-Tuned Model...")
    model_id = "SFNO_FINETUNED_INDIAN_OCEAN" if args.model.upper() == "SFNO" else "PINN_CORRECTOR_INDIAN_OCEAN"
    pred_res = scidl_registry.predict(lat=13.0827, lon=80.2707, forecast_hours=24, model_name=model_id)

    logger.info(f"✅ Model {model_id} Responded in {pred_res['inference_time_ms']} ms:")
    for var, val in pred_res["predictions"].items():
        unit = pred_res["units"].get(var, "")
        logger.info(f"   • {var:<20}: {val} {unit}")

    logger.info("================================================================================")
    logger.info("🎉 SUCCESS: Fine-tuned model is live and ready for FastAPI serving!")
    logger.info("================================================================================\n")

if __name__ == "__main__":
    main()
