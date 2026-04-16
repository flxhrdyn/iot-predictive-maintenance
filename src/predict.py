\"\"\"
predict.py - CLI Prediction Script
Quick single sample inference from the command line.

Usage examples:
  python src/predict.py
  python src/predict.py --type M --air-temp 300 --proc-temp 310 --rpm 1500 --torque 40 --wear 100
\"\"\"

import argparse
import json
import os
import sys

import joblib

from preprocess import MachineFailurePreprocessor

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, "models", "model.joblib")
PREPROCESSOR_PATH = os.path.join(ROOT_DIR, "models", "preprocessor.joblib")
METADATA_PATH = os.path.join(ROOT_DIR, "models", "metadata.json")


def load_artefacts():
    if not os.path.exists(MODEL_PATH):
        print("  Model not found. Run `python train.py` first.")
        sys.exit(1)
    model = joblib.load(MODEL_PATH)
    preprocessor = MachineFailurePreprocessor.load(PREPROCESSOR_PATH)
    with open(METADATA_PATH) as f:
        metadata = json.load(f)
    return model, preprocessor, metadata


def predict_single(model, preprocessor, sensor_data: dict) -> dict:
    X = preprocessor.transform(sensor_data)
    prediction = int(model.predict(X)[0])
    prob_failure = float(model.predict_proba(X)[0][1])

    if prob_failure < 0.3:
        risk = "🟢 LOW"
    elif prob_failure < 0.7:
        risk = "🟡 MEDIUM"
    else:
        risk = "🔴 HIGH"

    return {
        "prediction": prediction,
        "label": "FAILURE" if prediction == 1 else "NO FAILURE",
        "failure_probability": round(prob_failure, 4),
        "risk_level": risk,
    }


def interactive_mode(model, preprocessor):
    """Prompt user for sensor values interactively."""
    print("\n" + "=" * 55)
    print("  Machine Failure Prediction   Interactive Mode")
    print("=" * 55)
    print("  Enter sensor readings (press Ctrl+C to quit)\n")

    while True:
        try:
            machine_type = input("  Machine type [L / M / H]: ").strip().upper()
            air_temp = float(input("  Air temperature (K)      [e.g. 298.0]: "))
            proc_temp = float(input("  Process temperature (K)  [e.g. 308.6]: "))
            rpm = float(input("  Rotational speed (RPM)   [e.g. 1500]: "))
            torque = float(input("  Torque (Nm)              [e.g. 40.0]: "))
            wear = float(input("  Tool wear (min)          [e.g. 100]: "))

            sensor_data = {
                "type": machine_type,
                "air_temperature_K": air_temp,
                "process_temperature_K": proc_temp,
                "rotational_speed_rpm": rpm,
                "torque_Nm": torque,
                "tool_wear_min": wear,
            }

            result = predict_single(model, preprocessor, sensor_data)

            print("\n  ┌ Prediction Result ┐")
            print(f"  │  Label       : {result'label':<26}│")
            print(f"  │  Probability : {result'failure_probability':<26}│")
            print(f"  │  Risk Level  : {result'risk_level':<26}│")
            print("  └┘\n")

        except KeyboardInterrupt:
            print("\n\n  👋 Exiting. Goodbye!")
            break
        except ValueError as e:
            print(f"  ⚠️  Invalid input: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Predict machine failure from sensor readings."
    )
    parser.add_argument("--type", default=None, choices=["L", "M", "H"],
                        help="Machine quality type")
    parser.add_argument("--air-temp", type=float, default=None,
                        help="Air temperature (K)")
    parser.add_argument("--proc-temp", type=float, default=None,
                        help="Process temperature (K)")
    parser.add_argument("--rpm", type=float, default=None,
                        help="Rotational speed (RPM)")
    parser.add_argument("--torque", type=float, default=None,
                        help="Torque (Nm)")
    parser.add_argument("--wear", type=float, default=None,
                        help="Tool wear (min)")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON")

    args = parser.parse_args()

    model, preprocessor, _ = load_artefacts()

    # If all args provided → one shot prediction
    all_args = [args.type, args.air_temp, args.proc_temp, args.rpm, args.torque, args.wear]
    if all(v is not None for v in all_args):
        sensor_data = {
            "type": args.type,
            "air_temperature_K": args.air_temp,
            "process_temperature_K": args.proc_temp,
            "rotational_speed_rpm": args.rpm,
            "torque_Nm": args.torque,
            "tool_wear_min": args.wear,
        }
        result = predict_single(model, preprocessor, sensor_data)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n  Label       : {result'label'}")
            print(f"  Probability : {result'failure_probability'}")
            print(f"  Risk Level  : {result'risk_level'}\n")
    else:
        interactive_mode(model, preprocessor)


if __name__ == "__main__":
    main()
