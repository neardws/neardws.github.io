# 🕒 Research 

<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">DT-VEC</div><img src='images/DT_VEC.png' alt="DT-VEC" width="50%"><div class="badge"></div><img src='images/MAMO.png' alt="MAMO" width="50%"></div></div> </div>

<div class='paper-box-text' markdown="1">

[Enabling Digital Twin in Vehicular Edge Computing: A Multi-Agent Multi-Objective Deep Reinforcement Learning Solution]() \\   
**Xincao Xu**, Kai Liu, Penglin Dai, and Biwen Chen

- We present a DT-VEC architecture, where the heterogeneous information can be sensed by vehicles and uploaded to the edge node via V2I communications. The DT-VEC are modeled at the edge node, forming a logical view to reflect the physical vehicular environment. 
- We model the DT-VEC by deriving an ISAC-assisted sensing model and a reliability-guaranteed uploading model. 
- We formulate the bi-objective problem to maximize the system quality and minimize the system cost, simultaneously. In particular, we define the quality of DT-VEC by considering the timeliness and consistency, and define the cost of DT-VEC by considering the redundancy, sensing cost, and transmission cost. 
- We propose a multi-agent multi-objective (MAMO) deep reinforcement learning solution implemented distributedly in the vehicles and the edge nodes. Specifically, a dueling critic network is proposed to evaluate the advantage of action over the average of random actions. 
- Submitted to **IEEE Transactions on Consumer Electronics** (under review)

</div>


<div class='paper-box'><div class='paper-box-image'><div><div class="badge">VCPS</div><img src='images/VCPS.png' alt="VCPS" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[Cooperative Sensing and Heterogeneous Information Fusion in VCPS: A Multi-agent Deep Reinforcement Learning Approach](https://arxiv.org/abs/2209.12265)\\
**Xincao Xu**, Kai Liu, Penglin Dai, Ruitao Xie, and Jiangtao Luo

- We present a VEC architecture, in which heterogeneous information can be cooperatively sensed and uploaded via V2I communications. Logical views can be constructed by fusing the heterogeneous information at edge nodes. 
- We derive a cooperative sensing model based on the multi-class M/G/1 priority queue. On this basis, we define a noval metric AoV by modeling the timeliness, completeness, and consistency of the logical views.
- We formulate the problem, which aims at maximizing the quality of VCPS. 
- We propose a multiagent DRL solution, where a difference-reward-based credit assignment is designed to divide the system reward into the difference reward for vehicles, reflecting their individual contributions.
- Submitted to **IEEE Transactions on Intelligent Transportation Systems** (under review)

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">JSA 2022</div><img src='images/NOMA_based_VEC.png' alt="JSA" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[Joint Task Offloading and Resource Optimization in NOMA-based Vehicular Edge Computing: A Game-Theoretic DRL Approach](https://arxiv.org/abs/2209.12749)\\
**Xincao Xu**, Kai Liu, Penglin Dai, Feiyu Jin, Hualing Ren, Choujun Zhan, and Songtao Guo

- We present a NOMA-based VEC architecture, where heterogeneous resources of edge nodes are cooperated for real-time task processing. 
- We derive a V2I transmission model by considering both intra-edge and inter-edge interference and formulate a cooperative resource optimization (CRO) problem by jointly optimizing real-time task offloading and heterogeneous resource allocation, aiming at maximizing the service ratio.
- We decompose the CRO into two subproblems, namely, task offloading and resource alloction. The first subproblem is modeled as an EPG with Nash equilibrium (NE) existence and converagence, and a multi-agent D4PG algorithm is proposed to achieve the NE by adopting the potential function as reward function. The second subproblem is divided into two independent convex optimization problems, and an optimal solution is proposed based on a gradient-based iterative method and KKT condition.
- Accepted by **Journal of Systems Architecture** [JCR Q1\|SCI Q2\|CCF B]

</div>
</div>