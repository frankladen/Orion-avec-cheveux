package projetSynthese;

/**
 * classe Cavalier servant a representer le cavalier d'un jeu d'echec
 * 
 * @author Francois Allard
 */

public class Cavalier extends Piece {
	
	/** 
	 * Constructeur de la classe cavalier
	 * @param Prend en parametre la couleur du cavalier
	 * 
	 */
	public Cavalier(String Couleur) {
		super("Cavalier", Couleur);
	}

	/**
	 * Methode estValide, sert a verifier la validite du deplacement d'un cavalier
	 * @return true ou false si le deplacement du cavalier est valide
	 * @param Deplacement de la piece
	 */
	public boolean estValide(Deplacement deplacement) {
		/*Verifie si le quotient des deux deplacement est Žgal a 2 ou ˆ .5, se qui garantie que la
		 * piece ˆ fait un mouvement en "L".
		 */
		return (Math.abs(deplacement.getDeplacementX() / deplacement.getDeplacementY())) == 2 |
				(Math.abs(deplacement.getDeplacementX() / deplacement.getDeplacementY())) == .5;
	}
}
