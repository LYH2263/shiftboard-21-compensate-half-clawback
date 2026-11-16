from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services import handover as svc

router = APIRouter(prefix="/batches", tags=["在途批次"])


class OwnerBody(BaseModel):
    owner_shift_id: int


@router.get("")
def get_batches(owner_shift_id: int | None = Query(default=None)):
    return svc.list_batches(owner_shift_id)


@router.put("/{batch_id}")
def set_owner(batch_id: int, body: OwnerBody):
    from app.db import connect

    with connect() as conn:
        conn.execute(
            "UPDATE batches SET owner_shift_id = ? WHERE id = ?",
            (body.owner_shift_id, batch_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
    return dict(row) if row else {}
