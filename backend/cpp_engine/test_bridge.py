import os
import sys
import ctypes

# Determine shared library file extension based on OS
dir_path = os.path.dirname(os.path.realpath(__file__))
if sys.platform.startswith('win'):
    lib_path = os.path.join(dir_path, 'librisk_engine.dll')
else:
    lib_path = os.path.join(dir_path, 'librisk_engine.so')

# Load the C++ shared library
risk_lib = ctypes.CDLL(lib_path)

# Define function signature
risk_lib.calculate_adjusted_risk.argtypes = [
    ctypes.c_float, # base_ml_score
    ctypes.c_float, # comp_offered
    ctypes.c_float, # comp_demanded
    ctypes.c_int,   # litigation_cases
    ctypes.c_int    # forest_clearance_status
]
risk_lib.calculate_adjusted_risk.restype = ctypes.c_float

def run_cpp_risk_engine(ml_score, offered, demanded, litigations, clearance_code):
    return float(risk_lib.calculate_adjusted_risk(
        float(ml_score),
        float(offered),
        float(demanded),
        int(litigations),
        int(clearance_code)
    ))

if __name__ == "__main__":
    # Test Case: ML baseline = 50%, Gap = 50%, 2 Litigation cases, Clearance Pending
    final_score = run_cpp_risk_engine(50.0, 100.0, 150.0, 2, 1)
    print("--- C++ ENGINE TEST RESULT ---")
    print(f"Calculated Score: {final_score:.2f} / 100.0")
    assert final_score > 50.0, "Engine failed to apply risk multipliers!"
    print("SUCCESS: C++ Engine and Python bridge are fully operational!")