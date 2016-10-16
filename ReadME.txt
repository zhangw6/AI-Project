Wen Zhang （zhangw6@student.unimelb.edu.au）
Yunpeng Sun (syp0412@gmail.com)

Techniques for Agents:
The essential algorithm we applied in this project is heuristic search 

Strategy:
We have assigned two different roles for the two agents 
	 •	FullTimeAttackAgent: only deals with the attacking task, naming eating dots in opponent’s territory.
	‧	PartTimeAttackAgent: plays the role as both an attacker and defender according to the dynamic environment.  

We have three different modes in our project:
	•	Start: trigger for both FullTimeAttackAgent and PartTimeAttackAgent is when the game starts to play, at the start of the game, each agent moves to the border along the shorted path. 
	•	Attack: trigger for FullTimeAttackAgent is nothing instead of being assigned FullTimeAttackAgent; trigger for PartTimeAttackAgent is for ensuring there is no pacman at home. taking as the state of pacman, eating dots as many as possible while avoid the ghost
	•	Defend: trigger for PartTimeAttackAgent is detecting that there is one or two pacmen in its home territory.

Advantages of our Algorithm:
	•	We have a very comprehensive and detailed consideration upon almost every possible situation which could happen in this game.
	•	The agent can update its tactic mode according to the dynamic environment.
	•	When a pacman eats the capsule, it is actually meaningless to send a defender to block the pacman anymore. Rather than waste time chasing a powered pacman, the defender should better change to attacker. 
	•	What we observe when playing the game is that a pacman is usually eaten by ghost when the pacman enters a deadend with three walls around it. To avoid such situation, we have a feature named “thermals” to try to make the pacman keep away from this situation. 
	•	We noticed that the agents controlled by the baseline team is mainly around the border instead of pure attacking. In other words, having one defender at home would be very wasteful actually. The PartTimeAttackAgent provides a very flexible solution towards this problem

Disadvantages of our Algorithm:
	•	We have not realized the flexible switch of FullTimeAttackAgent and PartTimeAttackAgent between the two agents. Sometimes the agent who has been assigned as PartTimeAttackAgent is attacking and much further away than the FullTimeAttackAgent, but when he detects the danger, he has to go back home while the more effective approach is to find which agent is much closer to the their home and go home immediately. 
	•	The algorithm we applied here is pure heurisitic search algorithm while a combination of different algorithm is expected to be much stronger. 
