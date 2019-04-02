var gameDisabled = false;
var p1 = [] //moves made by human
var p2 = [] //moves made by ai
//possible combinations of cells that make 3 in a row
var winlines = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6]
];

//setup event handlers when page loads
$(document).ready(function() {
	$('td').click(chooseCell);
	$('td').mouseover(mouseOverCell);
	$('td').mouseout(mouseOutCell);
	$('.playagain').click(restartGame);
});

function restartGame() {
	document.getElementById('clear').play(); //play sound effect
	gameDisabled = false; //re-enable game 
	p1 = []; 
	p2 = [];
	for (var i=0; i<9; i++) {
		$("#"+i).html("");
		$("#"+i).css('cursor','default');
		$("#"+i).css('color','rgba(255,255,255,0.2)');
	}
}

function chooseCell(cell) {
	if (!gameDisabled && !p1.includes(parseInt(cell.target.id)) && !p2.includes(parseInt(cell.target.id))) { //check if game is enabled and is not taken yet
		p1.push(parseInt(cell.target.id));  //add cell to player1's moves
		$("#"+cell.target.id).html("X");
		$("#"+cell.target.id).css('cursor','default');
		$("#"+cell.target.id).css('color','white');
		document.getElementById('X').play(); //play sound effect
		if(!winner()) {
			gameDisabled = true; //disable game while computer is making its move
			setTimeout(function() { aiMove(); }, 1000); //wait one second before the computer makes its move
		}
	}
}

//hover effect for cells
function mouseOverCell(cell) {
	if (!gameDisabled && !p1.includes(parseInt(cell.target.id)) && !p2.includes(parseInt(cell.target.id))) {
		$("#"+cell.target.id).css('color','rgba(255,255,255,0.2)');
		$("#"+cell.target.id).css('cursor','pointer');
		$("#"+cell.target.id).html("X");
	}
}

//hover effect for cells
function mouseOutCell(cell) {
	if (!gameDisabled && !p1.includes(parseInt(cell.target.id)) && !p2.includes(parseInt(cell.target.id))) {
		$("#"+cell.target.id).html("");
		$("#"+cell.target.id).css('cursor','default');
	}
}

//if there is a winner disable the game and show message
function winner() {
	if (checkWin(p1)) {
		$("#modalLabel").html("You win!");
		$("#modal").modal(); //show modal
		gameDisabled = true;
		return true;
	} 
	else if(checkWin(p2)) {
		$("#modalLabel").html("Computer wins.");
		$("#modal").modal();
		gameDisabled= true;
		return true;
	}
	else if(p1.length + p2.length >= 9) {
		$("#modalLabel").html("It's a draw.");
		$("#modal").modal();
		gameDisabled = true;
		return true;
	}
	return false;
}

function aiMove() {
	move = minimax(p1.slice(),p2.slice(),"ai"); //get the best possible move using the minimax algorithm
	p2.push(move.index); //add move to player2 list of moves
	$("#"+move.index).html("O");
	$("#"+move.index).css('cursor','default');
	$("#"+move.index).css('color','white');
	gameDisabled = false; //re-enable game
	document.getElementById('O').play(); //play sound effect
	winner(); //check for winner
}

//check if player has cells that are three in a row
function checkWin(player) {
	for (var i = 0; i < 8; i++) {
		if (winlines[i].every(val => player.includes(val)) && player.length > 0) {
			return true;
		} 
	}
	return false;
}

//return cells that are not occupied by either player
function getEmptyCells(player1,player2) {
	cells = [];
	for(i=0;i<9;i++) {
		if(!player1.includes(i) && !player2.includes(i)) cells.push(i);
	}
	return cells;
}

//minimax algorithm to determine best possible move
function minimax(human,ai,player) {
	spots = getEmptyCells(human,ai); //get available spots 
	//check if game is over, and return corresponding score from the computer's perspective
	if (checkWin(human))
		return {score:-1};
	else if(checkWin(ai))  
		return {score:1};
	else if(spots.length == 0) 
		return {score:0}; 
		
	var moves = []; //list of possible moves
	//for each available spot
	for (var i = 0; i < spots.length; i++) {
		var move = {}; //create move object, which will have properties index and score
		move.index = spots[i]; //set the index of the move to the current spot whose score is going to be calculated
		if (player == "ai") {
			//if the player is ai, add the move to the ai's array of moves, and call minimax as the human player
			var result = minimax(human,ai.concat([move.index]),"human");
			move.score = result.score; 
		} else {
			//if the player is human, add the move to the human's array of moves, and call minimax as the ai player
			var result = minimax(human.concat([move.index]),ai,"ai");
			move.score = result.score;
		}
		spots = getEmptyCells(human,ai); //reset empty spots (neccesary because arrays are mutable)
		moves.push(move); //add move to list of possible moves
	}
	if(player == "ai") {
		//if player is ai, get the move with the highest score
		bestMove = moves.sort((a, b) => b.score - a.score)[0]
	} else {
		//if player is the human, get the move with the lowest score 
		bestMove = moves.sort((a, b) => a.score - b.score)[0]
	}
	return bestMove;
}