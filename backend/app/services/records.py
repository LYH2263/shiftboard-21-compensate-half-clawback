from __future__ import annotations

import json

from app.db import connect
from app.services import compensation as comp_svc
from app.services import handover as ho_svc


def _proof_summary(conn, compensation_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM compensation_proofs WHERE compensation_id = ?",
        (compensation_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "回拨键集合": json.loads(row["moved_biz_keys_json"]),
        "接班方不再持有": json.loads(row["removed_from_holder_json"]),
        "原交班方恢复": json.loads(row["restored_to_owner_json"]),
        "回拨方在途差": [
            json.loads(row["from_before_json"]),
            json.loads(row["from_after_json"]),
        ],
        "接收方在途差": [
            json.loads(row["to_before_json"]),
            json.loads(row["to_after_json"]),
        ],
        "回拨前后计数": {
            "回拨方": [row["before_count_from"], row["after_count_from"]],
            "接收方": [row["before_count_to"], row["after_count_to"]],
        },
    }


def list_records() -> list[dict]:
    """交班记录页的统一单据流：正向交班 + 补偿回拨，按单据类型区分。"""
    forward = []
    for h in ho_svc.list_handovers():
        forward.append(
            {
                "kind": "forward",
                "doc_type": "正向交班",
                "doc_no": h["doc_no"],
                "id": h["id"],
                "related_doc_no": None,
                "from_shift_name": h["from_shift_name"],
                "to_shift_name": h["to_shift_name"],
                "count": h["batch_count"],
                "count_label": "批次数",
                "status": h["status"],
                "started_at": h["started_at"],
                "finished_at": h["finished_at"],
                "reason": h["reason"],
                "proof": None,
            }
        )
    compensation = []
    with connect() as conn:
        for c in comp_svc.list_compensations():
            compensation.append(
                {
                    "kind": "compensation",
                    "doc_type": c["doc_type"],
                    "doc_no": c["doc_no"],
                    "id": c["id"],
                    "related_doc_no": c["related_doc_no"],
                    "from_shift_name": c["from_shift_name"],
                    "to_shift_name": c["to_shift_name"],
                    "count": c["key_count"],
                    "count_label": "业务键数",
                    "status": c["status"],
                    "started_at": c["started_at"],
                    "finished_at": c["finished_at"],
                    "reason": c["reason"],
                    # 差证明字段：与批次归属同源，只有成功完成的补偿单才有。
                    "proof": _proof_summary(conn, c["id"]),
                }
            )
    records = forward + compensation
    records.sort(key=lambda r: (r["started_at"], r["kind"]), reverse=True)
    return records
