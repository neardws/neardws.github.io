# 🔬 Research 

<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">VCPS</div><img src='images/research_VCPS.png' alt="VCPS" width="100%"><div class="badge">System Model</div><img src='images/research_Sensing_Model.png' alt="System Model" width="100%"></div></div>

<div class='paper-box-text' markdown="1">

<a href="https://arxiv.org/abs/2209.12265" class="no-underline">Cooperative Sensing and Heterogeneous Information Fusion in VCPS: A Multi-agent Deep Reinforcement Learning Approach</a>     
**Xincao Xu**, Kai Liu<sup>**\***</sup>, Penglin Dai, Ruitao Xie, Jingjing Cao, and Jiangtao Luo

- A novel problem is investigated to maximize the quality of VCPS by integrating the sensing, uploading, modeling and evaluation of heterogeneous information in VCPS. In particular, a cooperative sensing model is derived based on the multi-class M/G/1 priority queue and the Shannon theory. On this basis, a new metric called Age of View (AoV) is designed to quantitatively measure the quality of information fusion by evaluating the timeliness, completeness, and consistency of heterogeneous information in VCPS. To the best of our knowledge, this is the first work on quantitatively evaluating the quality of VCPS with the consideration of unique characteristics captured by the newly designed metic AoV.
- A dedicated solution named multi-agent difference-reward based actor-critic with V2I bandwidth allocation (MDRAC-VBA) is proposed based on multi-agent actor-critic. Specifically, vehicles act as independent agents with action space of sensing frequencies and uploading priorities. The system state consists of vehicle sensed information, edge cached information, and view requirements. The system reward is defined as the achieved VCPS quality. Then, a difference reward (DR) based credit assignment scheme is designed to evaluate the contributions of individual vehicles on view construction by dividing the system reward into difference rewards, so as to enhance the evaluation accuracy in term of the action of each agent. Further, the solution manages to achieve smaller action space of each agent and speed up the convergency compared with conventional DRL algorithms. Meanwhile, a V2I bandwidth allocation (VBA) scheme is designed at the edge node based on vehicle trajectories and view requirements.
- A comprehensive performance evaluation is conducted based on real-world vehicular trajectories. The proposed MDRAC-VBA algorithm and four competitive algorithms, including random allocation (RA), centralized deep deterministic policy gradient (C-DDPG), multi-agent actor-critic (MAC) and MAC with VBA scheme (MAC-VBA) are implemented. The simulation results demonstrated that MDRAC-VBA outperforms RA, C-DDPG, MAC, and MAC-VBA by around 61.8%, 23.8%, 22.0%, and 8.0%, respectively, in terms of maximizing the VCPS quality, and speeds up the convergence by around 6.8x, 1.4x and 1.3x compared with C-DDPG, MAC, and MAC-VBA, respectively.
- Accepted by **IEEE Transactions on Intelligent Transportation Systems** [JCR Q1\|SCI Q1]

</div>
</div>

<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">DT-VEC</div><img src='images/research_DT_VEC.png' alt="DT-VEC" width="100%"><div class="badge">MAMO</div><img src='images/research_MAMO.png' alt="MAMO" width="100%"></div></div>

<div class='paper-box-text' markdown="1">

<a href="https://ieeexplore.ieee.org/document/10261503" class="no-underline">Cooperative Sensing and Uploading for Quality-Cost Tradeoff of Digital Twins in VEC</a>       
Kai Liu<sup>**\***</sup>, **Xincao Xu**<sup>**\***</sup>, Penglin Dai, and Biwen Chen

- We formulate a bi-objective problem for enabling Digital Twins in Vehicular Edge Computing (DT-VEC), where a cooperative sensing model and a V2I uploading model are derived, and novel metrics for quantitatively evaluating system quality and cost are designed.
- We propose a multi-agent multi-objective (MAMO) deep reinforcement learning model, which determines the sensing objects, sensing frequency, uploading priority, and transmission power of vehicles, as well as the V2I bandwidth allocation of edge nodes. The model includes distributed actors interacting with the environment and storing their interaction experiences in the replay buffer, a learner with a dueling critic network for evaluating actions of vehicles and edge nodes. 
- We give comprehensive performance evaluation by implementing three representative algorithms, including random allocation (RA), distributed distributional deep deterministic policy gradient (D4PG) and multi-agent D4PG (MAD4PG), and the simulation results demonstrate that the proposed MAMO significantly outperforms existing solutions under different scenarios with respect to both maximizing system quality and saving system cost.
- Accepted by **IEEE Transactions on Consumer Electronics** [JCR Q2\|SCI Q2]

</div>
</div>

<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">NOMA-based VEC</div><img src='images/research_NOMA_based_VEC.png' alt="NOMA-based VEC" width="100%"><div class="badge">GT-DRL</div><img src='images/research_GT_DRL.png' alt="GT-DRL" width="100%"></div></div>

<div class='paper-box-text' markdown="1">

<a href="https://www.sciencedirect.com/science/article/pii/S138376212200265X" class="no-underline">Joint Task Offloading and Resource Optimization in NOMA-based Vehicular Edge Computing: A Game-Theoretic DRL Approach</a>    
**Xincao Xu**, Kai Liu<sup>**\***</sup>, Penglin Dai, Feiyu Jin, Hualing Ren, Choujun Zhan, and Songtao Guo

- We present a NOMA-based VEC architecture, where the vehicles share the same frequency of bandwidth resources and communicate with the edge node with the allocated transmission power. The tasks arrive stochastically at vehicles and are heterogeneous regarding computation resource requirements and deadlines, which are uploaded by vehicles via V2I communications. Then, the edge nodes with heterogeneous computation capabilities, i.e., CPU clock speed, can either execute the tasks locally with allocated computation resources or offload the tasks to neighboring edge nodes through a wired network.
- We propose a cooperative resources optimization (CRO) problem by jointly offloading tasks and allocating communication and computation resources to maximize the service ratio, which is the number of tasks serviced before the deadlines divided by the number of requested tasks. Specifically, a V2I transmission model considering both intra-edge and inter-edge interference and a task offloading model considering the heterogeneous resources and cooperation of edge nodes are theoretically modeled, respectively.
- We decompose the CRO problem into two subproblems: 1) task offloading game model and 2) resource allocation convex problem. Specifically, we model the first subproblem as a non-cooperative game among edge nodes, which is further proved as an EPG with the existence and convergence of NE. Then, we design a MAD4PG algorithm, a multi-agent version of D4PG, to achieve the NE, where edge nodes act as independent agents to determine the task offloading decisions and receive the achieved potential as rewards. Further, we model the second subproblem as two independent convex problems and derive an optimal mathematical solution based on the gradient-based iterative method and KKT condition.
- Accepted by **Journal of Systems Architecture** [JCR Q1\|SCI Q2\|CCF B]

</div>
</div>