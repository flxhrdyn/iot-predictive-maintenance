export interface TelemetryReading {
  process_temperature_K: number;
  rotational_speed_rpm: number;
  torque_Nm: number;
  tool_wear_min: number;
  type: string;
}

export interface PredictionData {
  device_id: string;
  failure_probability: number;
  inference_time_ms: number;
  risk_level: 'SAFE' | 'MEDIUM' | 'HIGH';
}

export interface TelemetryResponse {
  reading: TelemetryReading;
  prediction: PredictionData;
}
