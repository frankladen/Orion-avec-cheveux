package projetSynthese;
/**Verifie si le deplacement du cavalier est valide
 * @param Prend le deplacement du cavalier en parametre
 */


public class Pion extends Piece {
	
	/** 
	 * Constructeur de la classe pion
	 * @param Prend en parametre la couleur du pion
	 * 
	 */
	public Pion(String Couleur) {
		super("Pion", Couleur);
	}



	/**
	 * Methode estValide, sert a verifier la validite du deplacement d'un pion
	 * @return true ou false si le deplacement du pion est valide
	 * @param Deplacement de la piece
	 */
	public boolean estValide(Deplacement deplacement) {
		/*Verifie premierement que le deplacementX est bien nul, ensuite selon la couleur du pion, virifie que son deplacementY
		 * est egal à un ou deux en fonction de la position du pion. (les operateurs <= et >= servent a valider le cas que le pion
		 * avancent d'une seule case et ce même si il est sur la ligne de depart.
		 */
		if (deplacement.getDeplacementX() == 0)
			if (this.getCouleur().equals("noir")){
				/*si le deplacementY est plus petit ou egal a 2 si la ligne de depart est egal à 1, a 1 si la ligne de depart 
				 * n'est pas egal à 1, et que le deplacement n'est pas inferieur à 0 (que le pion ne recule pas). Si le pion est 
				 * Blanc, les conditions mais sont adaptes a unmouvement negatif et à une ligne de depart egal à 6.
				 */  
				return deplacement.getDeplacementY() <= (deplacement.getDepart().getLigne() == 1 ? 2 : 1) && deplacement.getDeplacementY() > 0;
			}
			else 
				return deplacement.getDeplacementY() >= (deplacement.getDepart().getLigne() == 6 ? -2 : -1) && deplacement.getDeplacementY() < 0;
		return false;				
	}
}
