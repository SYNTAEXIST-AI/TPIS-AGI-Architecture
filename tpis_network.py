import math
import random

try:
    from AGI.tpis_node import TPISNode
    from AGI.tpis_layer import TPISLayer
except ImportError:
    from tpis_node import TPISNode
    from tpis_layer import TPISLayer

class TPISNetwork:
    """
    TPISNetwork (Tri-Parametric Information Synthesis Network)
    
    This class connects multiple TPISLayers using the Operator Evolution Protocol.
    Rather than traditional flat matrix multiplications, the transfer of signals
    and gradients evolves structurally across three spatial dimensions, culminating
    in a volumetric output locked by the Cubic Operator (Dimensional Lock).
    
    Architectural Layers and Transitions:
    1. 1D Transition (Linear Symmetry): Input -> Layer 1
       - Operator: Addition (+)
       - S1_j = 1/N_in * sum(X_i + W1_ij)
       - g1_j = (1/N_in * sum(|X_i - W1_ij|)) * a_th
       
    2. 2D Transition (Orthogonal Expansion): Layer 1 -> Layer 2
       - Operator: Multiplication (*)
       - S2_j = (prod(A1_i * W2_ij + 0.01))^(1/N1)
       - g2_j = (prod(|A1_i - W2_ij| + 0.01))^(1/N1) * a_th
       
    3. 3D Transition (Volumetric Extrusion): Layer 2 -> Layer 3 (Output Layer)
       - Operator: Exponentiation (^)
       - S3_j = 1/N2 * sum(max(10^-15, A2_i) ^ W3_ij)
       - g3_j = (1/N2 * sum(|A2_i - W3_ij|^1.5)) * a_th
       
    Dimensional Lock:
    - The network depth is strictly limited to 3 spatial transitions.
    - The output layer (Layer 3) is hard-locked at exactly 8 nodes (2^3 = 8).
    - Resolution Tax on Layer 3 limits crystallization to exactly 1 active structure node (8 * 0.0398 = 0.3184 -> round to 0 -> limit to max(1, 0) = 1 node).
    """
    
    def __init__(self, input_dim=10, layer1_dim=100, layer2_dim=100):
        """
        Initializes the TPIS Neural Network.
        
        Args:
            input_dim (int): Number of inputs.
            layer1_dim (int): Number of nodes in Layer 1.
            layer2_dim (int): Number of nodes in Layer 2.
        """
        self.input_dim = input_dim
        self.layer1_dim = layer1_dim
        self.layer2_dim = layer2_dim
        self.output_dim = 8  # Hard-locked on 2^3 due to the Cubic Operator
        
        # Initialize the 3 layers
        self.layer1 = TPISLayer(num_nodes=layer1_dim)
        self.layer2 = TPISLayer(num_nodes=layer2_dim)
        self.layer3 = TPISLayer(num_nodes=self.output_dim)
        
        # Initialize weights with structural identity mapping within [0.5, 1.5]
        # This creates stable spatial highways projecting specific input dimensions onto Layer 3 outputs.
        # W1 maps input_dim -> layer1_dim
        self.W1 = []
        for i in range(self.input_dim):
            row = []
            for j in range(self.layer1_dim):
                if j % self.input_dim == i:
                    row.append(random.uniform(1.2, 1.5))
                else:
                    row.append(random.uniform(0.5, 0.8))
            self.W1.append(row)
            
        # W2 maps layer1_dim -> layer2_dim
        self.W2 = []
        for i in range(self.layer1_dim):
            row = []
            for j in range(self.layer2_dim):
                if i == j:
                    row.append(random.uniform(1.2, 1.5))
                else:
                    row.append(random.uniform(0.5, 0.8))
            self.W2.append(row)
            
        # W3 maps layer2_dim -> output_dim (8)
        self.W3 = []
        for i in range(self.layer2_dim):
            row = []
            for j in range(self.output_dim):
                if (i % 10) == j:
                    row.append(random.uniform(1.2, 1.5))
                else:
                    row.append(random.uniform(0.5, 0.8))
            self.W3.append(row)

        # Fractal opschaling (Fase 6)
        self.sub_domains = {}
        self.consecutive_activations = [0] * 8
        self.saturation_threshold = 3
        self.parent = None

    def spawn_sub_domain(self, node_index):
        """
        Spawns a self-similar sub-domain under Layer 3 output node_index.
        """
        sub = TPISNetwork(
            input_dim=self.input_dim,
            layer1_dim=self.layer1_dim,
            layer2_dim=self.layer2_dim
        )
        sub.parent = self
        self.sub_domains[node_index] = sub
        return sub

    def register_actualization(self, node_index):
        """
        Registers that node_index was crystallized. Increments its counter
        and resets all other counters. If it hits the saturation threshold,
        spawns a sub-domain.
        """
        for i in range(8):
            if i == node_index:
                self.consecutive_activations[i] += 1
            else:
                self.consecutive_activations[i] = 0
                
        if self.consecutive_activations[node_index] >= self.saturation_threshold:
            if node_index not in self.sub_domains:
                self.spawn_sub_domain(node_index)
            return True # Indicates transition / saturation triggered
        return False

    def prune_structures_recursive(self):
        """
        Prunes all active structure values in this network and all of its spawned sub-domains,
        preserving potency (Dark Matter).
        """
        for layer in [self.layer1, self.layer2, self.layer3]:
            for node in layer.nodes:
                node.prune()
        for sub in self.sub_domains.values():
            sub.prune_structures_recursive()

    def forward_recursive(self, X, competitive=True, force_low_gradient=False, current_path=None):
        """
        Propagates input vector X recursively down the spawned sub-domains based on Layer 3 activations.
        Enforces Hierarchical Attention Pruning globally.
        """
        if current_path is None:
            current_path = ()
            
        # 1. Run local forward pass
        local_out = self.forward(X, competitive=competitive, force_low_gradient=force_low_gradient)
        
        # 2. Check if a node is crystallized in Layer 3
        winner_k = None
        for i, node in enumerate(self.layer3.nodes):
            if node.structure > 0.0:
                winner_k = i
                break
                
        if winner_k is None:
            # Reset all counters if nothing crystallized
            for i in range(8):
                self.consecutive_activations[i] = 0
            return {
                "active_path": current_path,
                "active_network": self,
                "local_out": local_out,
                "winner_node": None,
                "spawned_transition": False
            }
            
        # 3. k is the winner node
        # Register actualization locally
        spawned_transition = self.register_actualization(winner_k)
        
        # 4. If a sub-domain exists for k, descend recursively
        if winner_k in self.sub_domains:
            # Hierarchical Attention Pruning: Prune all active structures in the tree
            self.prune_structures_recursive()
            
            # Recurse down
            sub_net = self.sub_domains[winner_k]
            sub_path = current_path + (winner_k,)
            res = sub_net.forward_recursive(
                X, 
                competitive=competitive, 
                force_low_gradient=force_low_gradient,
                current_path=sub_path
            )
            if spawned_transition:
                res["spawned_transition"] = True
            return res
        else:
            # We are at the active leaf network
            return {
                "active_path": current_path,
                "active_network": self,
                "local_out": local_out,
                "winner_node": winner_k,
                "spawned_transition": spawned_transition
            }


    def forward(self, X, competitive=True, force_low_gradient=False):
        """
        Propagates the input vector X through the network using the Operator Evolution Protocol.
        
        Args:
            X (list of float): The input vector of dimension input_dim.
            competitive (bool): Whether to use competitive crystallization in layers.
            force_low_gradient (bool): If True, sets all gradients to 0.0 to simulate absolute rest/collapse.
            
        Returns:
            dict: A dictionary containing the actualized outputs and metrics after each layer.
        """
        if len(X) != self.input_dim:
            raise ValueError(f"Input dimension mismatch. Expected {self.input_dim}, got {len(X)}")
            
        # =====================================================================
        # 1. 1D TRANSITION (Linear Symmetry, +): Input -> Layer 1
        # =====================================================================
        inputs_1 = [0.0] * self.layer1_dim
        grads_1 = [0.0] * self.layer1_dim
        
        for j in range(self.layer1_dim):
            sum_s = 0.0
            sum_g = 0.0
            for i in range(self.input_dim):
                sum_s += (X[i] + self.W1[i][j])
                sum_g += abs(X[i] - self.W1[i][j])
            
            inputs_1[j] = sum_s / self.input_dim
            grads_1[j] = (sum_g / self.input_dim) * TPISNode.A_TH
            
        if force_low_gradient:
            grads_1 = [0.0] * self.layer1_dim
            
        # Actualize Layer 1
        A1 = self.layer1.actualize_layer(inputs_1, grads_1, competitive=competitive)
        
        # =====================================================================
        # 2. 2D TRANSITION (Orthogonal Expansion, *): Layer 1 -> Layer 2
        # =====================================================================
        inputs_2 = [0.0] * self.layer2_dim
        grads_2 = [0.0] * self.layer2_dim
        
        # Compute product via log space for high numerical precision and stability
        for j in range(self.layer2_dim):
            log_prod_s = 0.0
            log_prod_g = 0.0
            for i in range(self.layer1_dim):
                term_s = max(1e-15, A1[i] * self.W2[i][j] + 0.01)
                term_g = max(1e-15, abs(A1[i] - self.W2[i][j]) + 0.01)
                
                log_prod_s += math.log(term_s)
                log_prod_g += math.log(term_g)
                
            inputs_2[j] = math.exp(log_prod_s / self.layer1_dim)
            grads_2[j] = math.exp(log_prod_g / self.layer1_dim) * TPISNode.A_TH
            
        if force_low_gradient:
            grads_2 = [0.0] * self.layer2_dim
            
        # Actualize Layer 2
        A2 = self.layer2.actualize_layer(inputs_2, grads_2, competitive=competitive)
        
        # =====================================================================
        # 3. 3D TRANSITION (Volumetric Extrusion, ^): Layer 2 -> Layer 3
        # =====================================================================
        inputs_3 = [0.0] * self.output_dim
        grads_3 = [0.0] * self.output_dim
        
        for j in range(self.output_dim):
            sum_s = 0.0
            sum_g = 0.0
            for i in range(self.layer2_dim):
                sum_s += (max(1e-15, A2[i]) ** self.W3[i][j])
                sum_g += (abs(A2[i] - self.W3[i][j]) ** 1.5)
                
            inputs_3[j] = sum_s / self.layer2_dim
            grads_3[j] = (sum_g / self.layer2_dim) * TPISNode.A_TH
            
        if force_low_gradient:
            grads_3 = [0.0] * self.output_dim
            
        # Actualize Layer 3 (Output Layer)
        A3 = self.layer3.actualize_layer(inputs_3, grads_3, competitive=competitive)
        
        return {
            "A1": A1,
            "A2": A2,
            "A3": A3,
            "inputs_1": inputs_1,
            "grads_1": grads_1,
            "inputs_2": inputs_2,
            "grads_2": grads_2,
            "inputs_3": inputs_3,
            "grads_3": grads_3
        }
        
    def apply_decay(self, decay_rate=0.05):
        """
        Applies metabolic decay/atrophy to all layers.
        """
        self.layer1.apply_decay(decay_rate)
        self.layer2.apply_decay(decay_rate)
        self.layer3.apply_decay(decay_rate)
        
    def reset(self):
        """
        Resets all layers to the vacuum zero starting state.
        """
        self.layer1.reset()
        self.layer2.reset()
        self.layer3.reset()

    def reset_recursive(self):
        """
        Resets all layers in this network and all of its spawned sub-domains.
        """
        self.reset()
        for sub in self.sub_domains.values():
            sub.reset_recursive()

    def apply_decay_recursive(self, decay_rate=0.05):
        """
        Applies metabolic decay/atrophy to this network and all of its spawned sub-domains.
        """
        self.apply_decay(decay_rate)
        for sub in self.sub_domains.values():
            sub.apply_decay_recursive(decay_rate)
        
    def __repr__(self):
        return (f"TPISNetwork(Input={self.input_dim}, "
                f"L1={self.layer1}, "
                f"L2={self.layer2}, "
                f"L3={self.layer3})")
