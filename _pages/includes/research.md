# 🕒 Recent Research 

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">Cooperative Sensing and Heterogeneous Information Fusion in VCPS: A Multi-agent Deep Reinforcement Learning Approach</div><img src='https://neardws-1257861591.cos.ap-shanghai.myqcloud.com/2022/09/20220914075824VCPS554.png' alt="sym" width="20%"></div></div>
<div class='paper-box-text' markdown="1">

**Xincao Xu**, Kai Liu, Penglin Dai, Ruitao Xie, and Jiangtao Luo

- We present a vehicular edge computing (VEC) architecture, in which heterogeneous information can be cooperatively sensed and uploaded via Vehicle-to-Infrastructure (V2I) communications. Logical views can be constructed by fusing the heterogeneous information at edge nodes. 
- We derive a cooperative sensing model based on the multi-class M/G/1 priority queue. On this basis, we define a noval metric AoV by modeling the timeliness, completeness, and consistency of the logical views and formulate the problem, which aims at maximizing the quality of VCPS. 
- We propose a multiagent deep reinforcement learning solution, where the system state includes vehicle sensed information, edge cached information, and view requirements. The vehicle action space consists of the sensing frequencies and uploading priorities of information, and the edge action space is the V2I bandwidth allocation. The system reward is defined as the achieved VCPS quality. In particular, a difference-reward-based credit assignment is designed to divide the system reward into the difference reward for vehicles, reflecting their individual contributions.
- Submitted to **IEEE Transactions on Intelligent Transportation Systems** (under review)

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">Joint Task Offloading and Resource Optimization in NOMA-based Vehicular Edge Computing: A Game-Theoretic DRL Approach</div><img src='https://neardws-1257861591.cos.ap-shanghai.myqcloud.com/2022/09/20220914075805NOMA_based_VEC204.png' alt="sym" width="20%"></div></div>
<div class='paper-box-text' markdown="1">

**Xincao Xu**, Kai Liu, Penglin Dai, Feiyu Jin, Hualing Ren, Choujun
Zhan, and Songtao Guo

- We present a non-orthogonal multiple access (NOMA) based architecture
in VEC, where heterogeneous resources of edge nodes are cooperated for realtime
task processing. 
- We derive a vehicle-to-infrastructure (V2I) transmission model by considering both intra-edge and inter-edge interference and formulate a cooperative resource optimization (CRO) problem by jointly optimizing the task offloading and resource allocation, aiming at maximizing the service ratio.
- We decompose the CRO into two subproblems: 1) task offloading, it is modeled as an exact potential game, and a multi-agent distributed distributional deep deterministic policy gradient (MAD4PG) is proposed to achieve the Nash equilibrium by adopting the potential function as reward function; and 2) resource allocation, it is modeled as convex optimization problems to allocate communication/computation resources, and an optimal mathematical solution is proposed based on a gradient-based iterative method and KKT condition.
- Submitted to **Journal of Systems Architecture** (under review)