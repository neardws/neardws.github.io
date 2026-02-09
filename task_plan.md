# GPU-ification Plan for VEC Environment

## 目标
将 `/home/neardws/github/HARL_new/HARL/harl/envs/vec/vec_env.py` 完全 GPU 化，消除所有 Python for 循环，使用 JAX 或 CuPy 实现纯张量操作。

## 核心挑战

### 1. **对象化 → 张量化**
当前实现使用 Python 对象（vehicle, edge_node, task），需要转换为固定大小的张量：
- `List[vehicle]` → `(n_vehicles, time_slots, features)` 张量
- `List[task]` → `(n_clients, max_tasks, task_features)` 张量
- Queue 对象 → `(n_queues, time_slots)` 张量

### 2. **动态结构 → 静态张量**
当前代码包含大量动态结构：
- 任务列表长度不固定 → 需要用 padding 和 mask
- 字典存储任务分配 → 需要用索引张量
- 条件分支 → 需要用 `where` 操作

### 3. **串行逻辑 → 并行计算**
当前代码包含大量串行 for 循环：
- 队列更新循环 → 批量张量操作
- 任务分配循环 → 向量化索引
- 成本计算循环 → 批量矩阵运算

## 实现策略

### Phase 1: 数据结构设计（静态张量）

#### 1.1 Vehicle State Tensor
```python
# Shape: (n_vehicles, time_slots, features)
vehicle_states = {
    'positions': (n_vehicles, time_slots, 2),      # x, y
    'computing': (n_vehicles,),                    # 计算能力
    'storage': (n_vehicles,),                       # 存储能力
    'power': (n_vehicles,),                         # 传输功率
    'is_server': (n_vehicles,),                     # 是否为服务器车辆 (bool mask)
}
```

#### 1.2 Task State Tensor
```python
# Shape: (n_clients, time_slots, max_tasks, features)
task_states = {
    'data_size': (n_clients, time_slots, max_tasks),
    'cpu_cycles': (n_clients, time_slots, max_tasks),
    'arrival_rate': (n_clients, time_slots, max_tasks),
    'task_id': (n_clients, time_slots, max_tasks),
    'valid_mask': (n_clients, time_slots, max_tasks),  # 标记有效任务
}
```

#### 1.3 Queue State Tensor
```python
# 统一队列表示：(queue_type, entity_index, time_slots)
queue_states = {
    'lc_queues': (n_clients, time_slots),
    'v2v_queues': (n_servers, time_slots),
    'vc_queues': (n_servers, time_slots),
    'v2i_queues': (n_edges, time_slots),
    'i2i_queues': (n_edges, time_slots),
    'ec_queues': (n_edges, time_slots),
    'i2c_queue': (time_slots,),
    'cc_queue': (time_slots,),
}
```

#### 1.4 Connection Matrices
```python
# Shape: (n_clients, n_servers/n_edges, time_slots)
connections = {
    'v2v_distance': (n_clients, n_servers, time_slots),
    'v2i_distance': (n_clients, n_edges, time_slots),
    'v2v_mask': (n_clients, n_servers, time_slots),  # 通信范围内 mask
    'v2i_mask': (n_clients, n_edges, time_slots),
    'channel_gains_v2v': (n_clients, n_servers, time_slots),
    'channel_gains_v2i': (n_clients, n_edges, time_slots),
}
```

### Phase 2: 核心函数 GPU 化

#### 2.1 Task Offloading Decision (向量化)
```python
def vectorized_task_offloading(
    actions: jnp.ndarray,  # (n_clients, max_tasks)
    v2v_mask: jnp.ndarray,  # (n_clients, n_servers)
    v2i_mask: jnp.ndarray,  # (n_clients, n_edges)
    task_valid_mask: jnp.ndarray,  # (n_clients, max_tasks)
) -> Dict[str, jnp.ndarray]:
    """
    返回任务分配的索引张量，而不是字典
    """
    # 输出：
    # - offload_type: (n_clients, max_tasks) ∈ {0:local, 1:v2v, 2:edge, 3:cloud}
    # - target_index: (n_clients, max_tasks) # 目标 server/edge 的索引
    ...
```

#### 2.2 Queue Update (批量计算)
```python
def vectorized_queue_update(
    queue_state: jnp.ndarray,  # (n_entities, time_slots)
    inputs: jnp.ndarray,        # (n_entities,)
    outputs: jnp.ndarray,       # (n_entities,)
    current_time: int,
) -> jnp.ndarray:
    """
    批量更新所有队列：Q[t+1] = max(Q[t] + input - output, 0)
    """
    updated = queue_state.at[:, current_time + 1].set(
        jnp.maximum(queue_state[:, current_time] + inputs - outputs, 0)
    )
    return updated
```

#### 2.3 Transmission Rate Calculation (向量化 SINR)
```python
def vectorized_transmission_rate(
    channel_gains: jnp.ndarray,     # (n_clients, n_servers)
    tx_power: jnp.ndarray,          # (n_clients,)
    power_allocation: jnp.ndarray,  # (n_clients,)
    noise: float,
) -> jnp.ndarray:
    """
    批量计算所有客户端到服务器的传输速率
    """
    # 计算 SINR
    signal = (jnp.abs(channel_gains) ** 2) * (tx_power * power_allocation)[:, None]
    # 计算干扰（NOMA）
    interference = ...  # 向量化干扰计算
    sinr = signal / (noise + interference)
    rate = bandwidth * jnp.log2(1 + sinr)
    return rate
```

#### 2.4 Cost Computation (矩阵运算)
```python
def vectorized_cost_computation(
    task_assignments: jnp.ndarray,  # (n_clients, max_tasks, 4) one-hot
    resource_allocations: jnp.ndarray,
    tx_power: jnp.ndarray,
) -> jnp.ndarray:
    """
    使用矩阵运算批量计算所有成本
    """
    # 传输成本
    tx_cost = jnp.sum(tx_power * power_allocation)
    
    # 计算成本
    comp_cost = jnp.sum(resource_allocations * computing_capability * task_cycles)
    
    return tx_cost + comp_cost
```

### Phase 3: 主要模块重构

#### 3.1 `__init__` 重构
```python
class VECEnvGPU:
    def __init__(self, args):
        # 1. 生成所有静态数据（使用现有生成函数）
        tasks, vehicles, edges, cloud = generate_all_objects(args)
        
        # 2. 转换为张量表示
        self.vehicle_tensor = self._convert_vehicles_to_tensor(vehicles)
        self.task_tensor = self._convert_tasks_to_tensor(tasks, vehicles)
        self.edge_tensor = self._convert_edges_to_tensor(edges)
        
        # 3. 预计算所有时间步的连接矩阵
        self.distance_v2v = compute_distance_matrix_vectorized(...)
        self.distance_v2i = compute_distance_matrix_vectorized(...)
        
        # 4. 初始化队列张量（全零）
        self.queue_states = initialize_queue_tensors(...)
```

#### 3.2 `step` 重构
```python
def step(self, actions):
    # 1. 动作处理（向量化）
    task_offload, power_alloc, comp_alloc = self._process_actions_vectorized(actions)
    
    # 2. 任务分配（向量化）
    offload_masks = self._compute_offload_masks_vectorized(task_offload)
    
    # 3. 队列更新（批量）
    queue_inputs = self._compute_queue_inputs_vectorized(offload_masks)
    queue_outputs = self._compute_queue_outputs_vectorized(power_alloc, comp_alloc)
    self.queue_states = self._update_all_queues_vectorized(queue_inputs, queue_outputs)
    
    # 4. 虚拟队列更新（批量）
    self.virtual_queues = self._update_virtual_queues_vectorized(...)
    
    # 5. 奖励计算（矩阵运算）
    cost = self._compute_cost_vectorized(offload_masks, power_alloc, comp_alloc)
    phi_t = self._compute_phi_t_vectorized()
    reward = self._compute_reward(cost, phi_t)
    
    # 6. 观测生成（向量化）
    obs = self._generate_observation_vectorized()
    
    return obs, reward, done, info
```

#### 3.3 `obser` 重构（完全向量化）
```python
def obser(self):
    t = self.cur_step
    obs = []
    
    # 1. 任务信息（批量归一化）
    task_data = self.task_tensor[:, t, :, :]  # (n_clients, max_tasks, features)
    task_obs = task_data / jnp.array([self.max_data_size, self.max_cycles])
    obs.append(task_obs.flatten())
    
    # 2. 队列状态（批量归一化）
    lc_obs = self.queue_states['lc_queues'][:, t] / self.max_lc_queue
    obs.append(lc_obs)
    
    # 3. PCA 压缩的连接信息
    v2v_flat = self.distance_v2v[:, :, t].flatten()
    v2v_pca = self.v2v_pca_transform(v2v_flat)
    obs.append(v2v_pca)
    
    # ... 其他观测
    
    return jnp.concatenate(obs)
```

### Phase 4: 特殊挑战处理

#### 4.1 任务到达的泊松分布
```python
# 预生成所有时间步的任务
def pregenerate_all_tasks(vehicles, time_slots):
    task_arrivals = []
    for v in vehicles:
        for task_id in v.task_ids:
            arrival_rate = v.task_arrival_rate[task_id]
            # 预生成整个 episode 的泊松采样
            arrivals = np.random.poisson(arrival_rate, time_slots)
            task_arrivals.append(arrivals)
    return np.array(task_arrivals)
```

#### 4.2 动态任务数量的处理
```python
# 使用 mask 处理变长任务列表
task_valid_mask = (task_tensor[:, :, :, 0] > 0)  # (n_clients, time_slots, max_tasks)

# 在所有计算中使用 mask
masked_task_size = task_tensor[:, :, :, 0] * task_valid_mask
```

#### 4.3 NOMA 干扰计算（向量化）
```python
def compute_interference_vectorized(
    channel_gains: jnp.ndarray,  # (n_clients, n_servers, time_slots)
    tx_power: jnp.ndarray,       # (n_clients,)
    power_alloc: jnp.ndarray,    # (n_clients,)
    current_time: int,
) -> jnp.ndarray:
    """
    向量化 NOMA 干扰计算
    """
    gains = channel_gains[:, :, current_time]  # (n_clients, n_servers)
    power = (tx_power * power_alloc)[:, None]  # (n_clients, 1)
    
    # 计算所有客户端对的增益比较
    gain_square = jnp.abs(gains) ** 2  # (n_clients, n_servers)
    
    # 对每个服务器，找出增益较小的客户端
    # 使用 mask 和矩阵运算
    ...
```

## 技术选型

### JAX vs CuPy

**推荐：JAX**

理由：
1. **自动微分**：虽然当前不需要，但未来可能用于梯度优化
2. **JIT 编译**：`@jax.jit` 可自动优化计算图
3. **函数式编程**：强制无副作用，更容易调试
4. **向量化**：`jax.vmap` 可自动批量化操作

**CuPy 的优势**：
- API 更接近 NumPy，迁移成本低
- 适合简单的数组操作

**最终选择**：使用 JAX 实现主体逻辑，保留 NumPy/CuPy 用于数据准备。

## 实现路线图

### Step 1: 基础设施 (Task 7.1)
- [ ] 创建 `vec_env_gpu.py` 骨架
- [ ] 实现张量转换函数
- [ ] 测试数据结构一致性

### Step 2: 核心计算模块 (Task 7.2)
- [ ] 实现向量化队列更新
- [ ] 实现向量化传输速率计算
- [ ] 实现向量化成本计算

### Step 3: 环境主循环 (Task 7.3)
- [ ] 重构 `__init__` 为张量初始化
- [ ] 重构 `step` 为全向量化流程
- [ ] 重构 `obser` 为批量生成

### Step 4: 测试与验证 (Task 8-10)
- [ ] 创建单元测试（队列更新、成本计算）
- [ ] 创建集成测试（完整 episode）
- [ ] 验证数值一致性（原环境 vs GPU 环境）

## 预期性能提升

### 当前瓶颈（profiling）
- Queue 更新循环：~40% 时间
- 任务分配循环：~25% 时间
- 成本计算循环：~20% 时间
- 观测生成：~10% 时间

### 预期加速比
- **Queue 更新**：50-100x（批量张量操作）
- **任务分配**：20-50x（向量化索引）
- **成本计算**：30-80x（矩阵运算）
- **整体**：预计 20-50x 加速（考虑数据传输开销）

## 风险与缓解

### 风险 1：内存占用增加
- **原因**：预生成所有时间步数据
- **缓解**：使用 float32 而非 float64；分批处理长 episode

### 风险 2：数值精度差异
- **原因**：浮点运算顺序不同
- **缓解**：使用相对误差阈值验证（1e-5）

### 风险 3：调试困难
- **原因**：张量操作难以逐步调试
- **缓解**：保留小规模测试用例；使用 JAX debug 工具

## 验证标准

### 功能正确性
- [ ] 队列长度误差 < 1e-3
- [ ] 成本计算误差 < 1e-3
- [ ] 观测向量误差 < 1e-3
- [ ] 奖励误差 < 1e-2

### 性能指标
- [ ] step() 时间 < 5ms（原实现 ~100ms）
- [ ] GPU 利用率 > 70%
- [ ] 内存占用 < 8GB

## 文件结构

```
harl/envs/vec/
├── vec_env.py              # 原环境（保留）
├── vec_env_gpu.py          # GPU 环境（新建）
├── gpu_utils/
│   ├── tensor_conversion.py   # 对象 → 张量转换
│   ├── vectorized_ops.py      # 向量化操作（队列、成本）
│   └── channel_computation.py # 信道增益、传输速率
└── tests/
    ├── test_consistency.py    # 一致性测试
    └── test_performance.py    # 性能基准测试
```
