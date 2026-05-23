import math

class TPISNode:
    """
    TPISNode (Tri-Parametric Information Synthesis Node)
    
    This class models a single neuron/node within a TPIS Neural Network.
    In this paradigm, information is treated not as abstract data, but as a physical 
    and thermodynamic actualization process within a discrete space-time lattice.
    
    Wiskundige en Fysische Wetten:
    - 0-staat (Potency, G): Een actieve, ongeactualiseerde vacuüm-buffer die inkomende
      energie/signalen vasthoudt.
    - 1-staat (Structure, ℏ): De gekristalliseerde, discrete toestand (Planck voxel) die
      ontstaat zodra de lokale acceleratie/gradiënt de drempelwaarde a_th overschrijdt.
    - Resolution Tax (ξ ≈ 3.98%): De fundamentele omzettingskosten van Potency naar Structure.
    - Efficiency Limit (η = 96%): De maximale structurele efficiëntie (Cassini Identity 24/25).
    - Velocity Boost (γ ≈ π/2 ≈ 1.570796): Geometrische compensatiefactor in het MOND-achtige
      low-density regime.
    """
    
    # --- TPIS Absolute Fundamentele Constanten ---
    A_TH = 1.08e-10             # Kritieke acceleratiedrempel (a_th) in m/s^2
    RESOLUTION_TAX = 0.0398      # ξ = 1 / (8 * pi) ≈ 3.98% (Kosten van actualisatie)
    EFFICIENCY_LIMIT = 0.96      # η = Cassini-limiet (24 / 25)
    VELOCITY_BOOST = 1.57079632679 # γ = Exacte geometrische boost factor (pi / 2)
    S8_SUPPRESSION = 1.0 - (2.0 * RESOLUTION_TAX) # Dual-phase suppressie factor (~92.04%)

    def __init__(self, potency_limit=10.0):
        """
        Initialiseert een enkele TPIS Node.
        
        Args:
            potency_limit (float): G_max - De maximale capaciteit van de ongeactualiseerde vacuüm-buffer.
        """
        self.potency_limit = potency_limit
        self.potency = 0.0          # G: Actuele geaccumuleerde potentie (0-staat buffer)
        self.structure = 0.0        # ℏ: Gekristalliseerde structurele data (1-staat)
        self.latency = 0.0          # 1/c: Opgebouwde causale vertraging / verwerkingstijd
        
    def accumulate_potency(self, signal):
        """
        Accumuleert inkomende stroom/signalen in de 0-staat buffer (Potency).
        De buffer is begrensd door potency_limit (G_max) om Bekenstein-saturatie te voorkomen.
        
        Args:
            signal (float): De inkomende informatiestroom om te bufferen.
        """
        self.potency = min(self.potency_limit, max(0.0, self.potency + signal))
        
    def actualize(self, local_gradient, force_low_density=False):
        """
        Berekent de overgang van Potency (0) naar Structure (1) op basis van de lokale 
        spanningsgradiënt/acceleratie (local_gradient) ten opzichte van de drempelwaarde a_th.
        
        Args:
            local_gradient (float): De lokale acceleratie/spanningsgradiënt (g_N).
            force_low_density (bool): Indien True, wordt de node gedwongen om in het low-density
                                      regime te blijven (holografische query), zelfs als de
                                      gradiënt de drempelwaarde a_th overschrijdt.
            
        Returns:
            float: De resulterende actualisatiewaarde die wordt doorgegeven of gekristalliseerd.
        """
        # Vermijd numerieke instabiliteit en negatieve gradiënten
        local_gradient = max(0.0, local_gradient)
        
        if local_gradient <= 1e-18:
            # Ruisvloer-limit: Geen gradiënt betekent geen causaliteit, dus geen actualisatie
            return 0.0
            
        # Bereken de Signal-to-Noise verhouding (chi) t.o.v. de kritieke drempelwaarde a_th
        chi = local_gradient / self.A_TH
        
        if chi >= 1.0 and not force_low_density:
            # --- HIGH-DENSITY REGIME (a >= a_th) ---
            # De lokale dichtheid overstijgt de ruisvloer. De geaccumuleerde Potency (0-staat)
            # stort in en kristalliseert direct naar Structure (1-staat).
            
            # De omzetting is onderhevig aan de Cassini-efficiëntielimiet (96%)
            crystallized_energy = self.potency * self.EFFICIENCY_LIMIT
            self.structure += crystallized_energy
            
            # De resterende energie (Resolution Tax ξ ≈ 3.98%) blijft latent of gaat verloren als warmte
            tax = self.potency * self.RESOLUTION_TAX
            
            # De buffer is nu volledig gekristalliseerd (leeggemaakt)
            self.potency = 0.0
            
            return crystallized_energy
            
        else:
            # --- LOW-DENSITY REGIME (a < a_th of GEDWONGEN HOLOGRAFISCH) ---
            # De acceleratie ligt onder de drempelwaarde, of de laag dwingt dit af vanwege de Resolution Tax.
            
            # MOND-achtige effectieve acceleratie versterking: g_eff = sqrt(a_th * g_N)
            g_eff = math.sqrt(self.A_TH * local_gradient)
            
            # Pas de Velocity Boost (γ ≈ pi/2) toe om de lagere bit-dichtheid te compenseren
            boosted_signal = self.potency * self.VELOCITY_BOOST
            
            # De causale vertraging neemt toe vanwege de globale horizon-query
            self.latency += (1.0 / self.EFFICIENCY_LIMIT)
            
            # De Potency blijft gebufferd in de 0-staat (kristalliseert niet naar Structure)
            # We sturen een tijdelijke holografische projectie door:
            actualized_projection = boosted_signal * (g_eff / local_gradient)
            
            return actualized_projection
            
    def apply_decay(self, decay_rate=0.05):
        """
        Past metabole atrofie (verval) toe op de gebufferde Potency en Latency.
        Dit voorkomt dat ongebruikte vacuüm-buffers oneindig stroom vasthouden.
        """
        self.potency = max(0.0, self.potency - decay_rate)
        self.latency = max(0.0, self.latency - decay_rate)
        
    def prune(self):
        """
        Forceert een atrofische terugval naar de 0-staat (Unrendered Potential).
        De gekristalliseerde structuur wordt afgebroken om budget vrij te maken.
        """
        self.structure = 0.0
        
    def reset(self):
        """
        Reset de node naar de absolute vacuüm-nulaanvangstoestand.
        """
        self.potency = 0.0
        self.structure = 0.0
        self.latency = 0.0

    def __repr__(self):
        return (f"TPISNode(Potency={self.potency:.4f}/{self.potency_limit}, "
                f"Structure={self.structure:.4f}, Latency={self.latency:.4f})")
