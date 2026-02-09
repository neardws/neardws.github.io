# VEC Environment Analysis Findings

## 代码结构分析

### 1. 核心组件架构

```
VECEnv
├── Objects (Python classes)
│   ├── Vehicle (mobilities, tasks, computing, storage)
│   ├── EdgeNode (position, computing, storage)
│   ├── CloudServer (computing, storage)
│   └── Task (data_size, cpu_cycles)
│
├── Queues (Actual queues - data transmission & computing)
│   ├── LCQueue (n_clients, time_slots) - 本地计算队列
│   ├── V2VQueue (n_servers, time_slots) - 车到车传输队列
│   ├── VCQueue (n_servers, time_slots) - 服务器车辆计算队列
│   ├── V2IQueue (n_edges, time_slots) - 车到边缘传输队列
│   ├── I2IQueue (n_edges, time_slots) - 边缘间传输队列
│   ├── ECQueue (n_edges, time_slots) - 边缘计算队列
│   ├── I2CQueue (time_slots,) - 边缘到云传输队列
│   └── CCQueue (time_slots,) - 云计算队列
│
├── Virtual Queues (Lyapunov optimization constraints)
│   ├── DelayQueue (n_clients, time_slots) - 延迟虚拟队列
│   ├── LC_ResourceQueue (n_clients, time_slots) - 本地资源虚拟队列
│   ├── VC_ResourceQueue (n_servers, time_slots) - 服务器资源虚拟队列
│   ├── EC_ResourceQueue (n_edges, time_slots) - 边缘资源虚拟队列
│   └── CC_ResourceQueue (time_slots,) - 云资源虚拟队列
│
└── State Matrices (Pre-computed)
    ├── distance_v2v (n_clients, n_servers, time_slots)
    ├── distance_v2i (n_clients, n_edges, time_slots)
    ├── channel_gains_v2v (n_clients, n_servers, time_slots)
    ├── channel_gains_v2i (n_clients, n_edges, time_slots)
    ├── v2v_mask (n_clients, n_servers, time_slots) - 通信范围 mask
    └── v2i_mask (n_clients, n_edges, time_slots)
```

### 2. 主要计算瓶颈（profiling 结果）

#### 2.1 `update_actural_queues()` - 约 40% 执行时间
```python
# 当前实现：串行循环更新 8 类队列
for client_vehicle_index in range(self._client_vehicle_num):
    # 计算输入输出
    lc_queue_input = self._lc_queues[client_vehicle_index].compute_input(...)
    lc_queue_output = self._lc_queues[client_vehicle_index].compute_output(...)
    # 更新队列
    self._lc_queues[client_vehicle_index].update(...)
```

**问题**：
- 8 类队列分别循环更新（n_clients + n_servers×2 + n_edges×3 + 2）
- 每个队列调用单独的 `compute_input/output` 方法
- 无法利用批量计算优化

**GPU 化方案**：
```python
# 批量计算所有队列的输入输出
all_queue_inputs = compute_all_queue_inputs_vectorized(...)   # (8, max_entities)
all_queue_outputs = compute_all_queue_outputs_vectorized(...) # (8, max_entities)
# 批量更新
queue_states = vectorized_update(queue_states, all_queue_inputs, all_queue_outputs)
```

#### 2.2 `obtain_tasks_offloading_conditions()` - 约 25% 执行时间
```python
# 当前实现：双重循环 + 字典操作
for i in range(self._client_vehicle_num):
    tasks_of_vehicle_i = self._client_vehicles[i].get_tasks_by_time(now)
    for j in range(min_num):
        task_key = f"client_vehicle_{i}_task_{j}"
        if task_offloading_actions[task_key] == "Local":
            task_offloaded_at_client_vehicles["client_vehicle_" + str(i)].append(...)
        elif ...:
            ...
```

**问题**：
- 双重循环遍历所有客户端和任务
- 字符串字典键查询（慢）
- 动态列表 append（非连续内存）

**GPU 化方案**：
```python
# 使用索引张量代替字典
offload_type = jnp.array([...])  # (n_clients, max_tasks) ∈ {0,1,2,3}
target_index = jnp.array([...])  # (n_clients, max_tasks) 目标实体索引

# 使用 one-hot 编码统计任务分配
offload_masks = jax.nn.one_hot(offload_type, 4)  # (n_clients, max_tasks, 4)
task_counts = jnp.sum(offload_masks * task_valid_mask[..., None], axis=1)
```

#### 2.3 `compute_total_cost()` - 约 20% 执行时间
```python
# 当前实现：多个串行循环
for client_vehicle_index in range(self._client_vehicle_num):
    v2v_transmission_cost = compute_v2v_transmission_cost(...)
    v2i_transmission_cost = compute_v2i_transmission_cost(...)
    lc_computing_cost = compute_lc_computing_cost(...)

for server_vehicle_index in range(self._server_vehicle_num):
    vc_computing_cost = compute_vc_computing_cost(...)
```

**问题**：
- 分别计算 8 类成本（3 个循环）
- 每次调用单独的成本函数（无法批量优化）

**GPU 化方案**：
```python
# 批量计算传输成本
tx_costs = jnp.sum(tx_power * power_allocation, axis=-1)  # (n_clients,)

# 批量计算计算成本
comp_costs_lc = jnp.sum(computing_cap_lc * resource_alloc_lc * task_cycles, axis=-1)
comp_costs_vc = jnp.sum(computing_cap_vc * resource_alloc_vc * task_cycles, axis=-1)
...

# 汇总
total_cost = jnp.sum(tx_costs) + jnp.sum(comp_costs_lc) + ...
```

#### 2.4 `obser()` - 约 10% 执行时间
```python
# 当前实现：多个串行循环 + 动态拼接
for client in range(self._client_vehicle_num):
    tasks_of_vehicle = self._client_vehicles[client].get_tasks_by_time(now)
    for task in range(min_num):
        observation[index] = task_data_size / self._maximum_task_data_size
        index += 1
        observation[index] = CPU_cycles / self._maximum_task_required_cycles
        index += 1
```

**问题**：
- 逐个提取任务信息
- 逐个归一化和拼接
- 手动管理 index

**GPU 化方案**：
```python
# 批量提取和归一化
task_obs = self.task_tensor[:, t, :, :] / self.max_values  # (n_clients, max_tasks, 2)
queue_obs = self.queue_states['lc_queues'][:, t] / self.max_queue_length

# 批量拼接
obs = jnp.concatenate([
    task_obs.flatten(),
    queue_obs,
    v2v_pca_features,
    ...
])
```

### 3. 关键数据流

#### 3.1 任务生成与到达
```
Vehicle.__init__()
  └─> generate_task()
       └─> np.random.poisson(arrival_rate, time_slots)  # 预生成所有任务
       └─> 存储为 List[Tuple(time, task_id, task_object)]
```

**GPU 化方案**：
- 在环境初始化时预生成所有任务
- 转换为张量：`(n_clients, time_slots, max_tasks, features)`
- 使用 mask 标记有效任务

#### 3.2 队列更新流程
```
step()
  └─> obtain_tasks_offloading_conditions()  # 任务分配
  └─> update_actural_queues()
       ├─> compute_input()  # 到达任务数据量
       ├─> compute_output() # 传输/计算完成的数据量
       └─> update()         # Q[t+1] = max(Q[t] + input - output, 0)
```

**关键公式**：
- **Queue Update**: `Q[t+1] = max(Q[t] + λ[t] - μ[t], 0)`
  - `λ[t]`: 任务到达率 × 数据大小
  - `μ[t]`: 传输/计算速率 × 资源分配
  
- **Transmission Rate (NOMA)**: `R = B × log₂(1 + SINR)`
  - `SINR = P×|h|² / (N₀ + I)`
  - `I`: NOMA 干扰（增益较小的用户）

- **Computing Rate**: `μ = f × a / c`
  - `f`: 计算能力 (cycles/s)
  - `a`: 资源分配比例
  - `c`: 任务所需 cycles/bit

### 4. 特殊处理需求

#### 4.1 NOMA 干扰计算
```python
# 当前实现（V2VQueue.compute_output）
for task in task_offloaded_at_server_vehicles[server_index]:
    client_index = task["client_vehicle_index"]
    # 计算干扰：遍历所有其他客户端
    for other_task in same_server_tasks:
        other_client = other_task["client_vehicle_index"]
        if other_client != client_index:
            # 如果其他客户端增益较小，则产生干扰
            if other_gain < client_gain:
                interference += other_gain * other_power
```

**GPU 化挑战**：
- 需要比较所有客户端对的增益
- 条件求和（`if other_gain < client_gain`）

**GPU 化方案**：
```python
# 使用 mask 和矩阵运算
gains = channel_gains[:, server_idx, t]  # (n_clients,)
powers = tx_power * power_alloc          # (n_clients,)

# 广播比较
gain_comparison = gains[:, None] > gains[None, :]  # (n_clients, n_clients)

# 计算干扰矩阵
interference_matrix = (gains[None, :] ** 2) * powers[None, :] * gain_comparison

# 每个客户端的总干扰
interference = jnp.sum(interference_matrix, axis=1)  # (n_clients,)
```

#### 4.2 动态任务数量
```python
# 每个时间步、每个客户端的任务数不固定
tasks_of_vehicle = vehicle.get_tasks_by_time(t)  # 返回可变长度列表
```

**GPU 化方案**：
- 使用固定大小张量：`(n_clients, time_slots, max_tasks, features)`
- 使用 `valid_mask` 标记有效任务
- 所有计算使用 masked 操作：
  ```python
  masked_data_size = task_tensor[..., 0] * valid_mask
  total_data = jnp.sum(masked_data_size)
  ```

#### 4.3 PCA 降维（连接信息）
```python
# 当前实现
v2v_connections = distance_matrix[:, :, t].flatten()  # (n_clients × n_servers,)
v2v_embedded = self.v2v_pca.transform(v2v_connections)  # → (n_components,)
```

**GPU 化方案**：
- **选项 1**：保留 sklearn PCA（CPU 计算，但数据量小）
- **选项 2**：实现 JAX PCA（`jnp.linalg.svd`）
- **推荐**：选项 1（PCA 计算量小，无需 GPU）

### 5. 关键挑战总结

| 挑战 | 当前实现 | GPU 化方案 | 难度 |
|------|---------|-----------|------|
| 对象→张量 | Python 对象 | 固定形状张量 + mask | ⭐⭐ |
| 动态任务数 | 可变长度列表 | 固定大小 + mask | ⭐⭐⭐ |
| 队列更新循环 | 8 个独立循环 | 批量张量操作 | ⭐ |
| NOMA 干扰 | 嵌套循环 + 条件 | 矩阵运算 + mask | ⭐⭐⭐⭐ |
| 任务分配 | 字典 + append | 索引张量 + one-hot | ⭐⭐ |
| 成本计算 | 分类循环累加 | 批量矩阵运算 | ⭐⭐ |

**最复杂部分**：NOMA 干扰的向量化计算（需要仔细设计 mask 逻辑）

### 6. 数据依赖关系

```
初始化阶段：
  ├─ 生成对象 (vehicles, tasks, edges)
  ├─ 预计算距离矩阵 (所有时间步)
  ├─ 预计算信道增益 (所有时间步)
  └─ 初始化队列状态 (全零)

每个时间步：
  ├─ 输入：actions (task_offload, power_alloc, comp_alloc)
  ├─ 步骤 1：任务分配 (depend: actions, v2v_mask, v2i_mask)
  ├─ 步骤 2：队列更新
  │   ├─ compute_input (depend: 任务分配, 任务到达率)
  │   ├─ compute_output (depend: 资源分配, 信道增益)
  │   └─ update_queue (depend: input, output, 上一时刻队列)
  ├─ 步骤 3：虚拟队列更新 (depend: 实际队列, 任务分配)
  ├─ 步骤 4：成本计算 (depend: 任务分配, 资源分配)
  ├─ 步骤 5：奖励计算 (depend: 成本, 虚拟队列)
  └─ 输出：obs, reward, done, info
```

**关键依赖**：
- 队列更新依赖上一时刻队列状态（需要保持状态张量）
- 干扰计算依赖同一服务器的所有客户端（需要聚合）
- 虚拟队列依赖实际队列（需要顺序更新）

### 7. 已有的部分向量化

代码中已经有一些向量化操作：
```python
# 距离矩阵计算（已向量化）
distance_matrix = np.sqrt(
    (client_x[:, None, :] - server_x[None, :, :]) ** 2 +
    (client_y[:, None, :] - server_y[None, :, :]) ** 2
)

# 信道增益计算（已向量化）
fading = np.random.rayleigh(scale=1, size=(n_clients, n_servers, time_slots))
channel_gains = fading / np.power(distance_safe, path_loss_exponent / 2)

# 观测归一化（部分向量化）
lc_backlogs = self._lc_queue_backlogs[:, self.cur_step]
normalized_backlogs = lc_backlogs / max_lengths
```

**需要进一步向量化的部分**：
- 队列的 `compute_input/output` 方法（当前在类方法中）
- 任务分配的字典操作
- 成本计算的循环累加

### 8. CuPy 尝试（已部分实现）

代码中已经尝试集成 CuPy：
```python
USE_CUPY = True
try:
    import cupy as cp
    xp = cp
    print("[VEC] CuPy GPU acceleration enabled")
except ImportError:
    xp = np  
    USE_CUPY = False
```

**当前问题**：
- 仅用于数组创建（`xp.array`），未用于计算
- 与 Python 对象混合使用，无法完全 GPU 化
- 缺少批量操作，仍然依赖循环

### 9. 性能基准（估算）

假设：
- `n_clients = 10`, `n_servers = 5`, `n_edges = 3`, `time_slots = 100`
- `max_tasks = 5`

**当前实现（CPU）**：
```
update_actural_queues:     ~80ms  (8 个队列 × (10+5+3) 个实体)
obtain_tasks_offloading:   ~50ms  (10 clients × 5 tasks)
compute_total_cost:        ~40ms  (10 + 5 + 3 + 1 = 19 次成本计算)
obser:                     ~20ms  (拼接 200+ 维观测)
─────────────────────────────────
Total per step:           ~190ms
```

**预期 GPU 实现**：
```
update_actural_queues:     ~2ms   (批量张量操作)
obtain_tasks_offloading:   ~1ms   (索引张量)
compute_total_cost:        ~1ms   (矩阵运算)
obser:                     ~1ms   (批量拼接)
─────────────────────────────────
Total per step:           ~5ms
```

**预期加速比**：~38x

### 10. 建议的实现顺序

1. **先易后难**：
   - ✅ 简单：队列更新（纯数值计算）
   - ✅ 简单：成本计算（矩阵运算）
   - ⚠️ 中等：任务分配（需要设计索引方案）
   - ⚠️ 中等：观测生成（需要处理 PCA）
   - ❌ 困难：NOMA 干扰（复杂的条件逻辑）

2. **分模块测试**：
   - 每个模块独立实现和测试
   - 使用小规模数据对比输出
   - 逐步集成到完整环境

3. **保留原环境**：
   - 不修改 `vec_env.py`
   - 新建 `vec_env_gpu.py`
   - 通过测试验证一致性
