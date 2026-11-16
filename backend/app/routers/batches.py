from fastapi import APIRouter, Query

from app.services import handover as svc

router = APIRouter(prefix="/batches", tags=["在途批次"])


@router.get("")
def get_batches(owner_shift_id: int | None = Query(default=None)):
    return svc.list_batches(owner_shift_id)


# 归属（batches.owner_shift_id）只能由两条单据链路写入：
#   1. 正向交班完成（handover.complete_handover）
#   2. 补偿回拨完成（compensation.complete_compensation）
# 系统不提供手工改归属接口；任何 PUT/PATCH/POST /api/batches/{id} 都会被
# 路由层拒绝（405/404），从入口上杜绝进行中单据期间私下改归属绕过补偿。
