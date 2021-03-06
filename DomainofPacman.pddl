﻿(define (domain pacman)
  (:requirements :typing)
  (:types pos)

  (:predicates  (At ?p - pos)
                (FoodAt ?p - pos)
                (CapusuleAt ?p - pos)
                (GhostAt ?p - pos)
                (Eaten)
                (Powered)
                (Path ?pos1 ?pos2 - pos)
                
                
                
  )
  (:action move
        :parameters (?posCurr ?posNext - pos)
        :precondition (and (At ?posCurr)
                           (Path ?posCurr ?posNext)
                           (not (GhostAt ?posNext))
                       )
        :effect   (and (At ?posNext)
                       (not  (At ?posCurr) )

                   )
   )
    (:action eatCapsule
        :parameters (?pos - pos)
        :precondition (and (At ?pos)
                           (CapusuleAt ?pos)
                       )
        :effect   (and (At ?pos)
                       (Powered)
                       (not  (CapusuleAt ?pos) )
                       (not (Eaten))
                  )
   )
    (:action eatFood
        :parameters (?pos - pos)
        :precondition (and (At ?pos)
                            (FoodAt ?pos)
                       )
        :effect   (and (At ?pos)
                       (not  (FoodAt ?pos) )
                   )
   )
)