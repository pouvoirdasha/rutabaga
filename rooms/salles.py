
#### IMPORTS #### 


##### SALLE - classe 

class Salle:
    """
    La classe Salle permet de calculer des informations sur les salles
    """

    def __init__(self,label : str):
        """
        Initialisation de la classe User.
        Args:
            label (str) : nom de la salle
        """
        self.label=label
        self.geometry=None
        #ajouter la géométrie !
    
    def distance(self, objet : str):
        """
        Idée : pour un objet donné on calcul la distance de la salle à l'objet 
        cf. Isssues
        """
    
    def projection_couloir(self):
        """
        Projection dans le couloir pour calcul des déplacements
        """

    def capacite(self):
        """
        Estimation capacité avec l'aire (trouver un ratio nb places / m2)
        """

    def info(self):
        """
        detection si salle info : teste la présence d'un i dans le label
        """
    

    
