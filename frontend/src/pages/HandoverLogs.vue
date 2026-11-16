<script setup>
import { onMounted, ref } from 'vue'
import { getJson } from '../api'

const rows = ref([])
const err = ref('')
const expanded = ref(null)

onMounted(async () => {
  try {
    rows.value = await getJson('/api/records')
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function toggle(row) {
  expanded.value = expanded.value === row.kind + row.id ? null : row.kind + row.id
}
</script>

<template>
  <div>
    <h1>交班记录</h1>
    <p class="lead">正向交班与补偿回拨分开留档：单据类型、对端单号、清单数量、最终状态；补偿单附回拨前后在途差证明。</p>
    <p v-if="err" class="msg">{{ err }}</p>
    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>类型</th><th>单号</th><th>关联单</th><th>回拨方/交班方</th>
            <th>接收方/接班方</th><th>数量</th><th>状态</th><th>开始</th><th>结束</th><th>差证明</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="r in rows" :key="r.kind + r.id">
            <tr>
              <td>
                <span class="tag" :class="{ on: r.kind === 'compensation' }">{{ r.doc_type }}</span>
              </td>
              <td>{{ r.doc_no }}</td>
              <td>{{ r.related_doc_no || '—' }}</td>
              <td>{{ r.from_shift_name }}</td>
              <td>{{ r.to_shift_name }}</td>
              <td>{{ r.count }} <span class="muted">{{ r.count_label }}</span></td>
              <td>{{ r.status }}</td>
              <td>{{ r.started_at }}</td>
              <td>{{ r.finished_at || '—' }}</td>
              <td>
                <button
                  v-if="r.kind === 'compensation' && r.proof"
                  class="btn ghost"
                  @click="toggle(r)"
                >
                  {{ expanded === r.kind + r.id ? '收起' : '查看' }}
                </button>
                <span v-else-if="r.kind === 'compensation'" class="muted">无（未完成）</span>
                <span v-else class="muted">—</span>
              </td>
            </tr>
            <tr v-if="r.kind === 'compensation' && r.proof && expanded === r.kind + r.id">
              <td colspan="10">
                <div class="proof">
                  <p class="muted">数据与批次归属同源，取自补偿单 #{{ r.id }} 落库的在途差证明</p>
                  <table>
                    <thead><tr><th>差证明字段</th><th>业务键集合</th></tr></thead>
                    <tbody>
                      <tr>
                        <td>回拨键集合</td>
                        <td>{{ r.proof['回拨键集合'].join('、') }}</td>
                      </tr>
                      <tr>
                        <td>接班方不再持有</td>
                        <td>{{ r.proof['接班方不再持有'].join('、') }}</td>
                      </tr>
                      <tr>
                        <td>原交班方恢复</td>
                        <td>{{ r.proof['原交班方恢复'].join('、') }}</td>
                      </tr>
                    </tbody>
                  </table>
                  <table style="margin-top: 10px">
                    <thead><tr><th>班次侧</th><th>回拨前在途集合</th><th>回拨后在途集合</th><th>计数（前 → 后）</th></tr></thead>
                    <tbody>
                      <tr>
                        <td>回拨方（接班方）</td>
                        <td>{{ r.proof['回拨方在途差'][0].join('、') || '空' }}</td>
                        <td>{{ r.proof['回拨方在途差'][1].join('、') || '空' }}</td>
                        <td>{{ r.proof['回拨前后计数']['回拨方'][0] }} → {{ r.proof['回拨前后计数']['回拨方'][1] }}</td>
                      </tr>
                      <tr>
                        <td>接收方（原交班方）</td>
                        <td>{{ r.proof['接收方在途差'][0].join('、') || '空' }}</td>
                        <td>{{ r.proof['接收方在途差'][1].join('、') || '空' }}</td>
                        <td>{{ r.proof['回拨前后计数']['接收方'][0] }} → {{ r.proof['回拨前后计数']['接收方'][1] }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </td>
            </tr>
          </template>
          <tr v-if="!rows.length">
            <td colspan="10">暂无单据</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
