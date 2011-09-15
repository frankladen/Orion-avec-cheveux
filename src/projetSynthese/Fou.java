package projetSynthese;

/**
 * classe Fou servant a representer un fou du jeu d'echec
 * 
 * @author Francois Allard
 */
public class Fou extends Piece{
	/** 
	 * Constructeur de la classe fou
	 * @param Prend en parametre la couleur du fou
	 * 
	 */
	public Fou(String Couleur) {
		super("Fou", Couleur);
	}
	


	/**
	 * Methode estValide, sert a verifier la validite du deplacement d'un fou
	 * @return true ou false si le deplacement du fou est valide
	 * @param Deplacement de la piece
	 */
	public boolean estValide(Deplacement deplacement) {
		/*Le mouvement du fou est une diagonale, ainsi si l'on fais la différence des valeurs absolu des dépalcements X et Y,
		 * le résultat devrait toujours être 0.
		 */
		return Math.abs(deplacement.getDeplacementX()) - Math.abs(deplacement.getDeplacementY()) == 0 && !deplacement.isNul();
		
	}
}
