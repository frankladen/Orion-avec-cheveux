package projetSynthese;
/**
 * classe tour servant à représenter la tour dans un jeu d'echec
 * 
 * @author Francois Allard
 */
public class Tour extends Piece {
	/** 
	 * Constructeur de la classe cavalier
	 * @param Prend en parametre la couleur de la tour
	 * 
	 */
	public Tour(String Couleur) {
		super("Tour", Couleur);
	}


	/**
	 * Methode estValide, sert a verifier la validite du deplacement du roi
	 * @return true ou false si le deplacement du roi est valide
	 * @param Deplacement de la piece
	 */
	public boolean estValide(Deplacement deplacement) {
		/*
		 * Si le produit du déplacement x et du déplacement y est égal à 0, c'est que
		 * un des deux déplacements est de 0. Se qui veux dire que le mouvement est uniquement vertical ou
		 * horizontale
		 */
		return deplacement.getDeplacementX() * deplacement.getDeplacementY() == 0 && !deplacement.isNul();
	}

}
