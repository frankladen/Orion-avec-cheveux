
// Copyright (c) 2000 CVM
package Test;
import static org.junit.Assert.*;

import org.junit.*;

import projetSynthese.*;
/**
 * packageTP3.TestEchecsPartie1
 * <P>
 * @author Département d'informatique
 */
public class testJunit {

  /**
   * Constructor
   */
   


 
 
 
 @Test
  public void testRoi ()
  {
  Roi r1 = new Roi ("noir");
  Position depart = new Position(3,4);
  Position arrivee = new Position (4,5);

  assertEquals ( true, r1.estValide(new Deplacement (depart,arrivee)));
  }
@Test
  public void testRoi2 ()
  {
    Roi r1 = new Roi ("noir" );
    Position depart = new Position ( 3,2 );
    Position arrivee = new Position (6,2);
    assertEquals ( false, r1.estValide(new Deplacement (depart,arrivee) ));
  }
@Test
  public void testTour ()
  {
  Tour t1 = new Tour  ("noir" );
  Position depart = new Position(5,5);
  Position arrivee = new Position(1,3);
  assertEquals ( false, t1.estValide(new Deplacement (depart,arrivee) ));
  }
@Test
  public void testCavalier ()
  {
  Cavalier un = new Cavalier ("noir");
  Position depart = new Position(3, 5);
  Position arrivee = new Position(5, 4 );
  assertEquals ( true, un.estValide ( new Deplacement (depart,arrivee) ));
  }
 @Test 
  public void testCavalier2()
  {
    Cavalier deux = new Cavalier ("blanc");
    Position depart = new Position (3,6);
    Position arrivee = new Position ( 2,4);
    assertEquals ( true , deux.estValide( new Deplacement (depart,arrivee) ));
  }
@Test
  public void testPion1 ()
  {
  Pion deux = new Pion ("noir" );
  Position dep = new Position(1,1);
  Position arr = new Position(3,3);
  assertEquals ( false, deux.estValide(new Deplacement (dep,arr)));
  }
@Test
  public void testPion2 ()
  {
  Pion deux = new Pion ("noir");
  Position dep = new Position(0,1);
  Position arr = new Position(0,2);
  assertEquals( true, deux.estValide( new Deplacement (dep,arr) ));
  }
@Test
  public void testPion3 ()
  {
  Pion deux = new Pion ("noir" );
  Position dep = new Position(1,1);
  Position arr = new Position(3,1);
  assertEquals ( false, deux.estValide(new Deplacement (dep,arr)));
  }
  
@Test
  public void testPion4 ()
  {
	  Pion deux = new Pion ("noir" );
	  Position dep = new Position(3,1);
	  Position arr = new Position(3,2);
	  assertEquals ( true, deux.estValide(new Deplacement (dep,arr)));

  }
@Test
  public void testPion5 ()
  {
  Pion deux = new Pion ("noir" );
  Position dep = new Position(3,1);
  Position arr = new Position(3,3);
  assertEquals ( true, deux.estValide(new Deplacement (dep,arr)));
  }
@Test
  public void testFou1 ()
  {
  Fou deux = new Fou ("noir" );
  Position dep = new Position(1,4);
  Position arr = new Position(3,6);
  assertEquals ( true, deux.estValide(new Deplacement (dep,arr)));
  }
@Test
  public void testFou2 ()
  {
  Fou deux = new Fou ("noir" );
  Position dep = new Position(2,2);
  Position arr = new Position(1,4);
  assertEquals ( false, deux.estValide(new Deplacement (dep,arr)));
  }
@Test
  public void testReine1 ()
  {
  Reine r1 = new Reine("blanc" );
  Position depart = new Position(5,7);
  Position arrivee = new Position(7,5);
  assertEquals(true, r1.estValide(new Deplacement (depart,arrivee)));
  }
@Test
  public void testReine2 ()
  {
  Reine r1 = new Reine ("blanc");
  Position depart = new Position(4,7);
  Position arrivee = new Position(4,0);
  assertEquals ( true, r1.estValide(new Deplacement (depart,arrivee)));
  }
@Test
  public void testReine3 ()
  {
  Reine r1 = new Reine ("blanc");
  Position depart = new Position(4,7);
  Position arrivee = new Position(0,3);
  assertEquals ( true, r1.estValide(new Deplacement (depart,arrivee)));
  }


 
  public static void main ( String [] args ){
    org.junit.runner.JUnitCore.main("projetSynthese.TestEchecsPartie1Corr");
  }
}

