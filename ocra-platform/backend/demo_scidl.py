import json
import time
from app.services.scidl.model_registry import scidl_registry
from app.agents.scidl import run_scidl_agent

def run_demonstration():
    print("================================================================================")
    print("🌊 ORCA SCIENTIFIC DEEP LEARNING (SciDL) OCEAN & WEATHER MODEL DEMONSTRATION 🌊")
    print("================================================================================\n")

    # Sample coordinates: Offshore Chennai, Bay of Bengal (Indian EEZ)
    lat = 13.0827
    lon = 80.2707
    forecast_hrs = 24

    print(f"📍 Target Coordinates: Lat {lat}° N, Lon {lon}° E (Bay of Bengal / Chennai Coast)")
    print(f"⏱️ Forecast Horizon: +{forecast_hrs} Hours\n")

    models_to_test = ["SFNO", "FOURCASTNET", "GRAPHCAST", "AURORA", "PINN_SWIN"]

    for model_name in models_to_test:
        print(f"--------------------------------------------------------------------------------")
        print(f"🔬 RUNNING MODEL: {model_name}")
        print(f"--------------------------------------------------------------------------------")
        
        start = time.time()
        res = scidl_registry.predict(
            lat=lat,
            lon=lon,
            forecast_hours=forecast_hrs,
            model_name=model_name,
            data_source="GFS"
        )
        elapsed = round((time.time() - start) * 1000, 2)

        print(f"✅ Status: {res['status'].upper()}")
        print(f"🤖 Model Identifier: {res['model_name']}")
        print(f"⚙️ Execution Engine: {res['execution_engine']}")
        print(f"💻 Device Backend: {res['execution_device']}")
        print(f"⚡ Inference Time: {res['inference_time_ms']} ms")
        print(f"📊 Predictions & Units:")
        
        preds = res["predictions"]
        units = res["units"]
        for var_name, val in preds.items():
            unit = units.get(var_name, "")
            print(f"   • {var_name:<22}: {val} {unit}")
        print()

    print("================================================================================")
    print("🤖 MULTI-AGENT SYNTHESIS DEMONSTRATION (SciDL Agent Integration)")
    print("================================================================================")
    agent_output = run_scidl_agent(lat=lat, lon=lon, forecast_hours=forecast_hrs, model_name="SFNO")
    print(f"Agent Name: {agent_output['agent_name']}")
    print(f"Data Citation: {agent_output['source']}")
    print(f"Synthesized Insight: {agent_output['info']}")
    print(f"Warning Triggered: {agent_output['has_warning']}")
    if agent_output['has_warning']:
        print(f"Warning Detail: {agent_output['warning_text']}")
    print("================================================================================\n")

if __name__ == "__main__":
    run_demonstration()
