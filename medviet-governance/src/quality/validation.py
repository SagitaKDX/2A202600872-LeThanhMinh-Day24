# src/quality/validation.py
import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    Tạo expectation suite cho anonymized patient data.
    """
    context = gx.get_context()
    try:
        suite = context.add_expectation_suite("patient_data_suite")
    except Exception:
        suite = context.add_or_update_expectation_suite(expectation_suite_name="patient_data_suite")

    # Lấy validator
    df = pd.read_csv("data/raw/patients_raw.csv")
    validator = context.sources.pandas_default.read_dataframe(df)

    # --- TASK: Thêm các expectations ---

    # 1. patient_id không được null
    validator.expect_column_values_to_not_be_null("patient_id")

    # 2. cccd phải có đúng 12 ký tự
    validator.expect_column_value_lengths_to_equal(
        column="cccd",
        value=12
    )

    # 3. ket_qua_xet_nghiem phải trong khoảng [0, 50]
    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0.0,
        max_value=50.0
    )

    # 4. benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions
    )

    # 5. email phải match regex pattern
    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    # 6. Không được có duplicate patient_id
    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy
    # (sau anonymization, cccd phải là fake hoặc masked)
    try:
        raw_df = pd.read_csv("data/raw/patients_raw.csv")
        raw_cccids = set(raw_df["cccd"].astype(str).tolist())
        # Also include raw cccids stripped of leading zero
        raw_cccids_stripped = {c.lstrip('0') for c in raw_cccids}
        raw_cccids_all = raw_cccids.union(raw_cccids_stripped)
        
        anon_cccids = set(df["cccd"].astype(str).tolist())
        leaked_cccids = raw_cccids_all.intersection(anon_cccids)
        if leaked_cccids:
            results["success"] = False
            results["failed_checks"].append(f"PII Leakage: Original CCCDs found in anonymized data: {leaked_cccids}")
    except Exception as e:
        results["success"] = False
        results["failed_checks"].append(f"Error checking CCCD leakage: {str(e)}")

    # Check 2: Không có null values trong các cột quan trọng
    important_cols = ["patient_id", "ho_ten", "cccd", "so_dien_thoai", "email", "benh", "ket_qua_xet_nghiem"]
    for col in important_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                results["success"] = False
                results["failed_checks"].append(f"Null values in important column '{col}': {null_count} instances")

    # Check 3: Số rows phải bằng original
    try:
        raw_df = pd.read_csv("data/raw/patients_raw.csv")
        if len(df) != len(raw_df):
            results["success"] = False
            results["failed_checks"].append(f"Row count mismatch: anonymized has {len(df)} rows, raw has {len(raw_df)} rows")
    except Exception as e:
        results["success"] = False
        results["failed_checks"].append(f"Error checking row counts: {str(e)}")

    return results
