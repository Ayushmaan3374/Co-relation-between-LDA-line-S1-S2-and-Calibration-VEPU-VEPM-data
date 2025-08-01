# from flask import Flask, request, jsonify
# import pandas as pd
# import numpy as np
# import joblib
# from flask_cors import CORS
# from datetime import datetime
 
# app = Flask(__name__)
# CORS(app)
 
# # Load model and scaler
# xgb_model = joblib.load("xgb_model.pkl")
# scaler = joblib.load("scaler.pkl")
 
# # Load CSVs
# csv_data = pd.read_csv("s1_s2_ve_values.csv")  # Used for prediction + max S1/S2
# csv_data_time_series = pd.read_csv("s1_s2.csv")  # Used for time series graph
 
# # Parse date column
# csv_data_time_series['DATE'] = pd.to_datetime(
#     csv_data_time_series['CALIBRATION_DATE_LOCAL'], errors='coerce'
# )
 
# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         data = request.get_json()
#         lda = str(data.get("LDA_PARTNUMBER")).strip()
 
#         # Find matching row in prediction CSV
#         row = csv_data[csv_data['LDA_PARTNUMBER'].astype(str).str.strip() == lda]
 
#         if row.empty:
#             return jsonify({'error': 'LDA part number not found'}), 404
 
#         # Prepare input array
#         input_array = np.array([[  
#             float(lda),
#             float(row.iloc[0]['VEPM_MP']),
#             0.0,
#             float(row.iloc[0]['VEPU_MP']),
#             0.0,
#             float(row.iloc[0]['VEP_MP']),
#             0.0
#         ]])
#         scaled_input = scaler.transform(input_array)
 
#         # Predict using model
#         prediction = xgb_model.predict(scaled_input)
#         s1, s2 = float(prediction[0][0]), float(prediction[0][1])
 
#         # Get time series data
#         lda_time_data = csv_data_time_series[
#             csv_data_time_series['LDA_PARTNUMBER'].astype(str).str.strip() == lda
#         ].sort_values('DATE').tail(30)
 
#         past30 = [
#             {
#                 "date": row['DATE'].strftime('%Y-%m-%d'),
#                 "s1": row['S1'],
#                 "s2": row['S2']
#             }
#             for _, row in lda_time_data.iterrows()
#         ]
 
#         # Get max S1 and S2 for this part number from s1_s2_ve_values.csv
#         max_s1 = float(row['S1'].max())
#         max_s2 = float(row['S2'].max())
 
#         return jsonify({
#             's1': round(s1, 2),
#             's2': round(s2, 2),
#             'past30days': past30,
#             'max_s1': round(max_s1, 2),
#             'max_s2': round(max_s2, 2)
#         })
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
# if __name__ == '__main__':
#     app.run(debug=True)







from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------- Load model and scaler ----------
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

# ---------- Load CSVs ----------
csv_data = pd.read_csv("s1_s2_ve_values.csv")          # Prediction data
csv_data_time_series = pd.read_csv("s1_s2.csv")        # Time series graph
df_range = pd.read_csv("LDA_EPT_data.csv")             # Tolerance limits

# Convert date for time series
csv_data_time_series['DATE'] = pd.to_datetime(
    csv_data_time_series['CALIBRATION_DATE_LOCAL'], errors='coerce'
)

# ---------- Helper: Match LDA to PH_PART_NUMBER ----------
def find_row_range(df_range: pd.DataFrame, lda: str) -> pd.DataFrame:
    lda_clean = lda.replace(" ", "").strip().upper()

    # 1. Exact match
    mask_full = (
        df_range['PH_PART_NUMBER']
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.strip()
        .str.upper()
        == lda_clean
    )
    row_range = df_range[mask_full]

    # 2. Fallback: last 4 digits
    if row_range.empty and len(lda_clean) <= 4:
        mask_last4 = (
            df_range['PH_PART_NUMBER']
            .astype(str)
            .str.replace(" ", "", regex=False)
            .str.strip()
            .str.upper()
            .str[-4:]
            == lda_clean
        )
        row_range = df_range[mask_last4]

    return row_range

# ---------- Prediction Endpoint ----------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        print(f"[DEBUG] Received request: {data}")

        lda = str(data.get("LDA_PARTNUMBER")).strip()
        print(f"[DEBUG] LDA input: {lda}")

        # Step 1: Match row from prediction data
        row = csv_data[csv_data['LDA_PARTNUMBER'].astype(str).str.strip() == lda]
        if row.empty:
            print("[ERROR] No matching LDA in prediction CSV")
            return jsonify({'error': 'LDA part number not found in prediction data'}), 404

        # Step 2: Prepare input for the model
        input_array = pd.DataFrame([{
            "LDA_PARTNUMBER": float(lda),
            "VEPM_MP": float(row.iloc[0]['VEPM_MP']),
            "VEPM_TIME_TAKEN": 0.0,
            "VEPU_MP": float(row.iloc[0]['VEPU_MP']),
            "VEPU_TIME_TAKEN": 0.0,
            "VEP_MP": float(row.iloc[0]['VEP_MP']),
            "VEP_TIME_TAKEN": 0.0
        }])
        print("[DEBUG] Input array before scaling:")
        print(input_array)

        # Step 3: Scale input
        scaled_input = scaler.transform(input_array.values)
        print("[DEBUG] Scaled input:")
        print(scaled_input)

        # Step 4: Model prediction
        prediction = xgb_model.predict(scaled_input)
        print("[DEBUG] Model prediction output:")
        print(prediction)

        s1, s2 = float(prediction[0][0]), float(prediction[0][1])

        # Step 5: Prepare time series data
        lda_time_data = csv_data_time_series[
            csv_data_time_series['LDA_PARTNUMBER'].astype(str).str.strip() == lda
        ].sort_values('DATE').tail(30)

        past30 = [
            {
                "date": row['DATE'].strftime('%Y-%m-%d'),
                "s1": row['S1'],
                "s2": row['S2']
            }
            for _, row in lda_time_data.iterrows()
        ]

        # Step 6: Tolerance and reference data
        row_range = find_row_range(df_range, lda)
        if row_range.empty:
            print("[ERROR] No matching tolerance data found")
            return jsonify({'error': 'Tolerance data not found'}), 404

        tolerance_s1 = float(row_range.iloc[0]['MP1_S1_Setting_Tolerance'])
        reference_s1 = float(row_range.iloc[0]['MP1_S1_Value'])
        tolerance_s2 = float(row_range.iloc[0]['MP2_S2_Setting_Tolerance'])
        reference_s2 = float(row_range.iloc[0]['MP2_S2_Value'])

        lower_s1 = round(reference_s1 - tolerance_s1, 2)
        upper_s1 = round(reference_s1 + tolerance_s1, 2)
        lower_s2 = round(reference_s2 - tolerance_s2, 2)
        upper_s2 = round(reference_s2 + tolerance_s2, 2)

        # Step 7: Return final JSON response
        return jsonify({
            's1': round(s1, 2),
            's2': round(s2, 2),
            'past30days': past30,
            'Lowest_S1': lower_s1,
            'Upper_S1': upper_s1,
            'Lowest_S2': lower_s2,
            'Upper_S2': upper_s2
        })

    except Exception as e:
        print(f"[ERROR] Exception in /predict route: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ---------- Entry Point ----------
if __name__ == '__main__':
    app.run(debug=True)




