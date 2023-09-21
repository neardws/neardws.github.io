# 🕒 Research 

<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">DT-VEC</div><img src='images/DT_VEC.png' alt="DT-VEC" width="100%"><div class="badge">MAMO</div><img src='images/MAMO.png' alt="MAMO" width="100%"></div></div>

<div class='paper-box-text' markdown="1">

[Cooperative Sensing and Uploading for Quality-Cost Tradeoff of Digital Twins in VEC](https://arxiv.org/abs/2210.17386)       
Kai Liu<sup>**\***</sup>, **Xincao Xu**<sup>**\***</sup>, Penglin Dai, and Biwen Chen

- We formulate a bi-objective problem for enabling Digital Twins in Vehicular Edge Computing (DT-VEC), where a cooperative sensing model and a V2I uploading model are derived, and novel metrics for quantitatively evaluating system quality and cost are designed.
- We propose a multi-agent multi-objective (MAMO) deep reinforcement learning model, which determines the sensing objects, sensing frequency, uploading priority, and transmission power of vehicles, as well as the V2I bandwidth allocation of edge nodes. The model includes distributed actors interacting with the environment and storing their interaction experiences in the replay buffer, a learner with a dueling critic network for evaluating actions of vehicles and edge nodes. 
- We give comprehensive performance evaluation by implementing three representative algorithms, including random allocation (RA), distributed distributional deep deterministic policy gradient (D4PG) and multi-agent D4PG (MAD4PG), and the simulation results demonstrate that the proposed MAMO significantly outperforms existing solutions under different scenarios with respect to both maximizing system quality and saving system cost.
- Accepted by **IEEE Transactions on Consumer Electronics** [JCR Q1\|SCI Q2]

</div>
</div>

<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">VCPS</div><img src='images/VCPS.png' alt="VCPS" width="100%"><div class="badge">System Model</div><img src='images/Sensing_Model.png' alt="System Model" width="100%"></div></div>

<div class='paper-box-text' markdown="1">

[Cooperative Sensing and Heterogeneous Information Fusion in VCPS: A Multi-agent Deep Reinforcement Learning Approach](https://arxiv.org/abs/2209.12265)     
**Xincao Xu**, Kai Liu<sup>**\***</sup>, Penglin Dai, Ruitao Xie, and Jiangtao Luo

- We present a cooperative sensing and heterogeneous information fusion architecture in VCPS via vehicular edge computing. The heterogeneous information can be sensed via either onboard sensors such as LIDAR, GPS, and cameras, or roadside infrastructures such as traffic lights. The sensed information is queued in vehicles for uploading via the V2I bandwidth, which is allocated by the corresponding edge node. Logical views can be constructed via the information fusion at edge nodes, and different views may be required to enable upper-layer applications.
- We formulate the problem to maximize the quality of VCPS. Specifically, we derive a cooperative sensing model, in which the information queuing and data uploading are modeled based on the multi-class M/G/1 priority queue and the Shannon theory, respectively. Then, we derive a heterogeneous information fusion model by modeling the timeliness, completeness, and consistency of views. On this basis, a new metric called Age of View (AoV) is defined to quantitatively measure the quality of information fusion. Finally, we model the quality of VCPS and present the optimization objective, which is to maximize the VCPS quality.
- We propose a multi-agent deep reinforcement learning solution. Specifically, the solution model is presented, in which vehicles act as independent agents with action space of determining the sensing frequencies and uploading priorities, and the edge action space is the V2I bandwidth allocation. The system state consists of vehicle sensed information, edge cached information, and view requirements. The system reward is defined as the achieved VCPS quality. In particular, the system reward is divided into the Difference Reward (DR) to capture vehicle individual contributions on view constructions by the DR-based credit assignment.
- Submitted to **IEEE Transactions on Intelligent Transportation Systems** (under review)

</div>
</div>


<div class='paper-images-box'><div class='paper-box-image'><div><div class="badge">NOMA-based VEC</div><img src='images/NOMA_based_VEC.png' alt="NOMA-based VEC" width="100%"><div class="badge">GT-DRL</div><img src='images/GT_DRL.png' alt="GT-DRL" width="100%"></div></div>

<div class='paper-box-text' markdown="1">

[Joint Task Offloading and Resource Optimization in NOMA-based Vehicular Edge Computing: A Game-Theoretic DRL Approach](https://www.sciencedirect.com/science/article/pii/S138376212200265X)    
**Xincao Xu**, Kai Liu<sup>**\***</sup>, Penglin Dai, Feiyu Jin, Hualing Ren, Choujun Zhan, and Songtao Guo

- We present a NOMA-based VEC architecture, where the vehicles share the same frequency of bandwidth resources and communicate with the edge node with the allocated transmission power. The tasks arrive stochastically at vehicles and are heterogeneous regarding computation resource requirements and deadlines, which are uploaded by vehicles via V2I communications. Then, the edge nodes with heterogeneous computation capabilities, i.e., CPU clock speed, can either execute the tasks locally with allocated computation resources or offload the tasks to neighboring edge nodes through a wired network.
- We propose a cooperative resources optimization (CRO) problem by jointly offloading tasks and allocating communication and computation resources to maximize the service ratio, which is the number of tasks serviced before the deadlines divided by the number of requested tasks. Specifically, a V2I transmission model considering both intra-edge and inter-edge interference and a task offloading model considering the heterogeneous resources and cooperation of edge nodes are theoretically modeled, respectively.
- We decompose the CRO problem into two subproblems: 1) task offloading game model and 2) resource allocation convex problem. Specifically, we model the first subproblem as a non-cooperative game among edge nodes, which is further proved as an EPG with the existence and convergence of NE. Then, we design a MAD4PG algorithm, a multi-agent version of D4PG, to achieve the NE, where edge nodes act as independent agents to determine the task offloading decisions and receive the achieved potential as rewards. Further, we model the second subproblem as two independent convex problems and derive an optimal mathematical solution based on the gradient-based iterative method and KKT condition.
- Accepted by **Journal of Systems Architecture** [JCR Q1\|SCI Q2\|CCF B]

</div>
</div>