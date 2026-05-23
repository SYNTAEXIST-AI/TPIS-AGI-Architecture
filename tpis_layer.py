import math

# Probeer de node te importeren via absolute en relatieve importpaden
try:
    from AGI.tpis_node import TPISNode
except ImportError:
    from tpis_node import TPISNode

class TPISLayer:
    """
    TPISLayer (Tri-Parametric Information Synthesis Layer)
    
    Deze klasse beheert een collectie van TPISNode instanties en dwingt de wetten van de
    Holografische Limiet en de Resolution Tax (ξ ≈ 3.98%) af op laagniveau.
    
    Wiskundige en Fysische Wetten:
    - Resolution Tax (ξ = 0.0398): Het totale aantal gekristalliseerde nodes (1-staat, structure > 0.0)
      in de laag mag op geen enkel moment de limiet van ~3.98% van het totaal aantal nodes overschrijden.
    - Causale Latentie Afdwingen: Wanneer deze limiet is bereikt, mogen andere nodes in de laag niet
      meer kristalliseren naar een 1. Het systeem dwingt ze via 'force_low_density=True' om in de
      0-staat (Potency) te blijven en hun signaal te bufferen (Dark Matter / Latency).
    - Competitive Actualization (Competitieve Selectie): Bij gelijktijdige hoge signalen worden de
      nodes gesorteerd op basis van causale acceleratie/gradiënt (dalend) en potency (dalend) om te
      bepalen welke nodes als eerste het recht hebben om te kristalliseren binnen het budget.
    """
    
    RESOLUTION_TAX = 0.0398 # ξ ≈ 3.98%
    
    def __init__(self, num_nodes, potency_limit=10.0):
        """
        Initialiseert de holografische TPIS laag.
        
        Args:
            num_nodes (int): Het totale aantal nodes in deze laag.
            potency_limit (float): G_max voor elke individuele node.
        """
        self.num_nodes = num_nodes
        self.nodes = [TPISNode(potency_limit=potency_limit) for _ in range(num_nodes)]
        
        # Bepaal de harde holografische actualisatielimiet (Crystallization Budget)
        # Voor 100 nodes is dit exact max(1, int(round(100 * 0.0398))) = 4 nodes.
        self.crystallization_limit = max(1, int(round(num_nodes * self.RESOLUTION_TAX)))
        
    def actualize_layer(self, inputs, gradients, competitive=True):
        """
        Voert de actualisatie-cyclus uit voor de gehele laag.
        Accumuleert eerst de inkomende signalen in de potency buffers, berekent het
        resterende crystallization budget, en actualiseert vervolgens elke node.
        
        Args:
            inputs (list of float): De inkomende signalen voor elke node.
            gradients (list of float): De lokale acceleratie/spanningsgradiënt voor elke node.
            competitive (bool): Indien True, sorteert de laag de nodes op basis van de hoogste
                                causale druk (gradient dalend, potency dalend) voordat ze worden
                                geactualiseerd om competitieve kristallisatie te garanderen.
                                
        Returns:
            list of float: De resulterende actualisatiewaarden van alle nodes (in de originele indexvolgorde).
        """
        if len(inputs) != self.num_nodes or len(gradients) != self.num_nodes:
            raise ValueError(f"De lengtes van inputs ({len(inputs)}) en gradients ({len(gradients)}) "
                             f"moeten exact gelijk zijn aan num_nodes ({self.num_nodes}).")
                             
        # 1. Pre-Actualization Pruning (Atrofie bij a < a_th voor actieve structuren)
        # Actieve nodes waarvan de nieuwe local_gradient onder a_th zakt, vallen terug naar de 0-staat.
        for i in range(self.num_nodes):
            if self.nodes[i].structure > 0.0 and gradients[i] < TPISNode.A_TH:
                self.nodes[i].prune()
                             
        # 2. Accumuleer inkomende signalen in de 0-staat (Potency) vacuüm-buffers
        for i in range(self.num_nodes):
            self.nodes[i].accumulate_potency(inputs[i])
            
        # 3. Bereken hoeveel nodes al in de 1-staat (Structure > 0.0) zijn gekristalliseerd
        already_crystallized = sum(1 for node in self.nodes if node.structure > 0.0)
        
        # 4. Bereken het resterende budget voor nieuwe kristallisaties
        budget = max(0, self.crystallization_limit - already_crystallized)
        
        # 5. Bepaal de verwerkingsvolgorde (competitief of sequentieel)
        if competitive:
            # Sorteer indices op basis van:
            # Eerst de lokale gradiënt (dalend) - hoogste causale spanning eerst.
            # Daarna de opgebouwde potency (dalend) als tie-breaker.
            sorted_indices = sorted(
                range(self.num_nodes),
                key=lambda idx: (gradients[idx], self.nodes[idx].potency),
                reverse=True
            )
        else:
            sorted_indices = list(range(self.num_nodes))
            
        # Lijst om de uiteindelijke actualisatie-outputs in op te slaan
        outputs = [0.0] * self.num_nodes
        
        # 6. Voer de actualisatie uit voor elke node op basis van het budget
        for idx in sorted_indices:
            node = self.nodes[idx]
            grad = gradients[idx]
            
            # Controleer of de node in het high-density regime wil vallen (grad >= a_th)
            if grad >= TPISNode.A_TH:
                if budget > 0:
                    # We hebben nog budget! De node mag normaal actualiseren en kristalliseren
                    old_structure = node.structure
                    output = node.actualize(grad, force_low_density=False)
                    
                    # Als de node daadwerkelijk is overgegaan van 0 naar 1 (nieuwe kristallisatie),
                    # verminderen we het resterende budget.
                    if old_structure == 0.0 and node.structure > 0.0:
                        budget -= 1
                else:
                    # Het holografische budget is op!
                    # We dwingen de node in het low-density regime (Causale Latentie)
                    output = node.actualize(grad, force_low_density=True)
            else:
                # Gradiënt ligt onder de drempelwaarde (natuurlijk low-density regime)
                output = node.actualize(grad, force_low_density=False)
                
            outputs[idx] = output
            
        return outputs
        
    def apply_decay(self, decay_rate=0.05):
        """
        Past metabole atrofie toe op alle nodes in de laag.
        """
        for node in self.nodes:
            node.apply_decay(decay_rate)
            
    def reset(self):
        """
        Reset alle nodes in de laag naar de vacuüm-nulaanvangstoestand.
        """
        for node in self.nodes:
            node.reset()
            
    def __repr__(self):
        crystallized_count = sum(1 for node in self.nodes if node.structure > 0.0)
        return (f"TPISLayer(Nodes={self.num_nodes}, "
                f"Crystallized={crystallized_count}/{self.crystallization_limit} "
                f"(ξ={self.RESOLUTION_TAX*100:.2f}%))")
