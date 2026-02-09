#!/usr/bin/env python3
"""
惊讶度计算和预测验证模块

当预测被验证时，计算惊讶度：
    surprise = |actual - predicted| × confidence

高惊讶度的预测失败会生成新的 knowledge gap。
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent / "curiosity-kernel"
PREDICTIONS_FILE = BASE_DIR / "predictions.json"
STATE_FILE = BASE_DIR / "state.json"
SURPRISE_THRESHOLD = 0.5  # 惊讶度超过此值生成新 gap


def load_predictions():
    with open(PREDICTIONS_FILE) as f:
        return json.load(f)["predictions"]


def save_predictions(predictions):
    with open(PREDICTIONS_FILE, "w") as f:
        json.dump({"predictions": predictions}, f, indent=2, ensure_ascii=False)


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def calculate_surprise(prediction, actual_outcome):
    """
    计算惊讶度
    
    对于二元预测：surprise = confidence if wrong else 0
    对于连续预测：surprise = |actual - predicted| × confidence
    """
    if prediction.get("verified"):
        return prediction.get("surprise_score", 0)
    
    confidence = prediction["confidence"]
    
    # 简化版：假设是二元预测
    # actual_outcome: True = 预测成真, False = 预测失败
    if actual_outcome:
        return 0  # 预测正确，没有惊讶
    else:
        return confidence  # 预测错误，惊讶度 = 置信度


def verify_prediction(pred_id, actual_outcome, notes=""):
    """验证一个预测"""
    predictions = load_predictions()
    pred = next((p for p in predictions if p["id"] == pred_id), None)
    
    if not pred:
        return {"error": f"Prediction {pred_id} not found"}
    
    surprise = calculate_surprise(pred, actual_outcome)
    
    pred["verified"] = True
    pred["actual"] = notes or ("correct" if actual_outcome else "incorrect")
    pred["surprise_score"] = surprise
    pred["verified_at"] = datetime.now().isoformat()
    
    save_predictions(predictions)
    
    # 高惊讶度 → 生成新 gap
    new_gap = None
    if surprise > SURPRISE_THRESHOLD:
        new_gap = generate_gap_from_surprise(pred, surprise)
        state = load_state()
        state["knowledge_gaps"].append(new_gap)
        state["stats"]["total_predictions"] = len(predictions)
        state["stats"]["predictions_verified"] = sum(1 for p in predictions if p.get("verified"))
        if actual_outcome:
            state["stats"]["predictions_correct"] = state["stats"].get("predictions_correct", 0) + 1
        save_state(state)
    
    return {
        "prediction_id": pred_id,
        "surprise_score": surprise,
        "high_surprise": surprise > SURPRISE_THRESHOLD,
        "new_gap_generated": new_gap is not None,
        "new_gap": new_gap
    }


def generate_gap_from_surprise(prediction, surprise):
    """从高惊讶度预测生成新的 knowledge gap"""
    import uuid
    
    return {
        "id": f"gap-{uuid.uuid4().hex[:8]}",
        "domain": prediction["domain"],
        "question": f"为什么我对 '{prediction['prediction'][:50]}...' 的预测错了？置信度 {prediction['confidence']:.1%}",
        "importance": min(surprise + 0.3, 1.0),
        "uncertainty": 0.9,
        "created": datetime.now().isoformat(),
        "source": "surprise_driven",
        "related_prediction": prediction["id"]
    }


def check_predictions_due():
    """检查需要验证的预测"""
    predictions = load_predictions()
    now = datetime.now(timezone.utc)
    
    due = []
    for pred in predictions:
        if pred.get("verified"):
            continue
        verify_time = datetime.fromisoformat(pred["verify_after"].replace("+08:00", "+00:00"))
        if now >= verify_time:
            due.append(pred)
    
    return due


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python surprise.py <command> [args]")
        print("Commands:")
        print("  due                 - show predictions due for verification")
        print("  verify <id> <0|1>   - verify prediction (0=wrong, 1=correct)")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "due":
        due = check_predictions_due()
        for pred in due:
            print(f"- {pred['id']}: {pred['prediction'][:60]}... (confidence: {pred['confidence']:.1%})")
    
    elif cmd == "verify":
        if len(sys.argv) < 4:
            print("Usage: python surprise.py verify <pred_id> <0|1> [notes]")
            sys.exit(1)
        
        pred_id = sys.argv[2]
        outcome = sys.argv[3] == "1"
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        
        result = verify_prediction(pred_id, outcome, notes)
        print(json.dumps(result, indent=2, ensure_ascii=False))
