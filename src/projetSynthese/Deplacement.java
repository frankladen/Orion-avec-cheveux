package projetSynthese;

/**
 * classe deplacement servant à représenter le deplacement d'une piece dans un jeu d'echec
 * 
 * @author Francois Allard
 */
public class Deplacement {
	
	/**
	 * Deplacement sur l'axe des X
	 */
	private double deplacementX;
	
	/**
	 * Deplacement sur l'axe des Y
	 */
	private double deplacementY;
	
	/**
	 * Coordonnee de la case d'arrivee
	 */
	private Position arrivee;
	
	/**
	 * Coordonnee de la case de depart
	 */
	private Position depart;
	

	/**Constructeur d'un objet déplacement, calcul les déplacement sur les axes X et Y. Ces valeurs ne sont pas donné de
	 * manière absolue car le pion à besoin de connaître la direction dans laquelle il se déplace.
	 * @param Prend en paramètre les coordonnees de depart et d'arrive du deplacement
	 */
	public Deplacement(Position depart, Position arrivee)
	{
		this.arrivee = arrivee;
		this.depart = depart;
		this.deplacementX = arrivee.getColonne() - depart.getColonne();
		this.deplacementY = arrivee.getLigne() - depart.getLigne();
	}


	public double getDeplacementX() {
		return deplacementX;
	}

	public double getDeplacementY() {
		return deplacementY;
	}
	
	public Position getArrivee() {
		return arrivee;
	}

	public Position getDepart() {
		return depart;
	}
	
	//vérifie si le déplacement est nul.
	public boolean isNul(){
		return deplacementX == 0 && deplacementY == 0;
	}
	
}
