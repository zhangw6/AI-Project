(define (domain ghost)
  (:requirements :typing :conditional-effects)
  (:types pos)				;; x-y positions are treated as a single variable
  (:predicates  (At ?p - pos) 		;; Position of Ghost
                (PacmanAt ?p - pos)	;; Position of Pacman
                (Path ?pos1 ?pos2 - pos)	;; Whether two positions are connected
                (Scared)		;; Whether Ghost is scared of Pacman
                (FoodAt ?pos - pos)
  )
  (:action move
        :parameters (?posCurr ?posNext - pos)
        :precondition (and (At ?posCurr)
                           (Path ?posCurr ?posNext)
                       )
        :effect   (and (At ?posNext)
                       (not  (At ?posCurr) )
                   )
   )
     (:action eatPacman
        :parameters (?pos - pos)
        :precondition (and (At ?pos)
                           (PacmanAt ?pos)
                           (not (Scared))
                       )
        :effect   (and (At ?pos)
                       (not  (PacmanAt ?pos) )
                   )
   )
)