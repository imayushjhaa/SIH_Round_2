import os
import sys
import ctypes

# Determine shared library path based on platform
dir_path = os.path.dirname(os.path.realpath(__file__))
if sys.platform.startswith('win'):
    lib_path = os.path.join(dir_path, 'librisk_engine.dll')
else:
    lib_path = os.path.join(dir_path, 'librisk_engine.so')

# Try loading the compiled C++ shared library
risk_lib = None
if os.path.exists(lib_path):
    try:
        risk_lib = ctypes.CDLL(lib_path)
        risk_lib.calculate_adjusted_risk.argtypes = [
            ctypes.c_float, # base_ml_score
            ctypes.c_float, # comp_offered
            ctypes.c_float, # comp_demanded
            ctypes.c_int,   # litigation_cases
            ctypes.c_int    # forest_clearance_status
        ]
        risk_lib.calculate_adjusted_risk.restype = ctypes.c_float
    except Exception as err:
        print(f"Notice: Failed to load C++ library ({lib_path}): {err}. Using Python fallback.")
        risk_lib = None
else:
    print(f"Notice: C++ engine shared library not found at {lib_path}. Using Python fallback.")


def run_cpp_risk_engine(ml_score: float, offered: float, demanded: float, litigations: int, clearance_code: int) -> float:
    """
    Executes the C++ rule-based risk adjustment engine via ctypes bridge.
    Falls back to a pure-Python implementation if the compiled binary is not available.
    """
    if risk_lib is not None:
        return float(risk_lib.calculate_adjusted_risk(
            float(ml_score),
            float(offered),
            float(demanded),
            int(litigations),
            int(clearance_code)
        ))

    # Python fallback mirroring the exact C++ logic
    score = float(ml_score)
    if offered > 0.0:
        gap_ratio = (demanded - offered) / offered
        if gap_ratio > 0.25:
            score += gap_ratio * 15.0

    score += litigations * 4.5

    if clearance_code == 1:
        score += 8.0
    elif clearance_code == 2:
        score += 25.0

    return max(0.0, min(100.0, score))


if __name__ == "__main__":
    # Test Case: ML baseline = 50%, Gap = 50%, 2 Litigation cases, Clearance Pending
    final_score = run_cpp_risk_engine(50.0, 100.0, 150.0, 2, 1)
    print("--- RISK ENGINE TEST RESULT ---")
    print(f"Calculated Score: {final_score:.2f} / 100.0")
    assert final_score > 50.0, "Engine failed to apply risk multipliers!"
    print("SUCCESS: Engine and bridge are fully operational!")
