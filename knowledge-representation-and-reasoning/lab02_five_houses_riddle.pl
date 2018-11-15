% Entities:
% HOUSES: redHouse, whiteHouse, blueHouse, yellowHouse, greenHouse
% PEOPLE: british, swedish, danish, norwegian, german
% DRINKS: milk, beer, tea, water, coffee
% CIGARETTES: pallMall, winfield, marlboro, dunhill, rothmans
% ANIMALS: bird, dog, horse, cat, fish
%
% Every person likes one drink, smokes one kind of cigarettes and has an animal,
% but they are all different. (so no two persons like the same drink / smoke the
% same cigarettes / have the same animal)
% 
% Who has fish ?
% getSolution(AllHouses, FishOwner).
%
% Gott hilf mir.


on_the_left_of(A, B) :- B is A + 1.
on_the_right_of(A, B) :- A is B + 1.
next_to(A, B) :- on_the_right_of(A, B).
next_to(A, B) :- on_the_left_of(A, B).

getSolution(AllHouses, FishOwner) :- 
	AllHouses = [ house(0, Color0, Who0, Pet0, Drink0, Smoke0), 
		      house(1, Color1, Who1, Pet1, Drink1, Smoke1), 
		      house(2, Color2, Who2, Pet2, Drink2, Smoke2), 
		      house(3, Color3, Who3, Pet3, Drink3, Smoke3), 
		      house(4, Color4, Who4, Pet4, Drink4, Smoke4) 
	], 
	member(house(_, red, british, _, _, _), AllHouses),     		% Britanicul locuieşte în casa roşie. 
	member(house(NorwHouseNum, _, norwegian, _, _, _), AllHouses),		% Norvegianul locuieşte lângă casa albastră. 
	member(house(BlueHouseNum, blue, _, _, _, _), AllHouses),
	next_to(NorwHouseNum, BlueHouseNum),
	member(house(GreenHouseNum, green, _, _, _, _), AllHouses),		% Casa verde se află în stânga casei albe.
	member(house(WhiteHouseNum, white, _, _, _, _), AllHouses),
	on_the_left_of(GreenHouseNum, WhiteHouseNum),										 
	member(house(_, green, _, _, coffee, _), AllHouses),			% Locatarul casei verzi bea cafea. 
	member(house(2, _, _, _, milk, _), AllHouses),				% Locatarul casei din mijloc bea lapte. 
	member(house(_, yellow, _, _, _, dunhill), AllHouses), 			% Locatarul din casa galbenă fumează Dunhill.
	member(house(0, _, norwegian, _, _, _), AllHouses),			% Norvegianul locuieşte în prima casă. 
	member(house(_, _, swedish, dog, _, _), AllHouses), 			% Suedezul are un câine. 
	member(house(_, _, _, bird, _, pallMall), AllHouses),			% Persoana care fumează Pall Mall are o pasăre. 			
	member(house(MarlboroHouseNum, _, _, _, _, marlboro), AllHouses),	% Fumătorul de Marlboro locuieşte lângă cel care are o pisică. 
	member(house(CatHouseNum, _, _, cat, _, _), AllHouses),
	next_to(MarlboroHouseNum, CatHouseNum),
	member(house(_, _, _, _, beer, winfield), AllHouses),			% Fumătorul de Winfield bea bere. 
	member(house(HorseHouseNum, _, _, horse, _, _), AllHouses),		% Locatarul care are un cal locuieşte lângă cel care fumează Dunhill. 
	member(house(DunhillHouseNum, _, _, _, _, dunhill), AllHouses),		
	next_to(HorseHouseNum, DunhillHouseNum),			
	member(house(_, _, german, _, _, rothmans), AllHouses), 		% Germanul fumează Rothmans. 
	member(house(WaterHouseNum, _, _, _, water, _), AllHouses),		% Fumătorul de Marlboro are un vecin care bea apă. 
	next_to(MarlboroHouseNum, WaterHouseNum), 
	member(house(_, _, FishOwner, fish, _, _), AllHouses).
  
