import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <Board />
    </>
  );
}

function Square({ value, onSquareClick }) {
  return (
    <button className="square" onClick={onSquareClick}>
      {value}
    </button>
  );
}

function Board() {
  const [xIsNext, setXIsNext] = useState(true);
  const [squares, setSquares] = useState(Array(9).fill(null));
  const [selectedSquare, setSelectedSquare] = useState(null)

  function handleClick(i) {
    const currentPlayer = xIsNext ? "X" : "O"
    // state 1: game is completed
    if (calculateWinner(squares)) {
      return;
    }
    // state 2: player has not used all their pieces yet
    if (!hasUsedAllPieces(squares, currentPlayer)) {
      if (squares[i]) return;
      placeNewPiece(i);
    } 
    // state 3: player has used all their pieces
    else {
      if (squares[i] == currentPlayer) {
        setSelectedSquare(i)
        return;
      }
      if ((selectedSquare != null) && !squares[i]) {
        movePiece(i)
      }
    }
  }

  function placeNewPiece(i) {
    const nextSquares = squares.slice();
    nextSquares[i] = xIsNext ? "X" : "O"
    setSquares(nextSquares);
    setXIsNext(!xIsNext);
  }

  function movePiece(i) { 
    if (!isLegalMove(selectedSquare, i, squares)) return;
    const nextSquares = squares.slice();
    nextSquares[selectedSquare] = null;
    nextSquares[i] = xIsNext ? "X" : "O";
    setSquares(nextSquares)
    setSelectedSquare(null)
    setXIsNext(!xIsNext)
  }


  const winner = calculateWinner(squares);
  let status;
  if (winner) {
    status = "Winner: " + winner;
  } else {
    status = "Next player: " + (xIsNext ? "X" : "O");
  }

  return (
    <>
      <div className="status">{status}</div>
      <div className="board-row">
        <Square value={squares[0]} onSquareClick={() => handleClick(0)} />
        <Square value={squares[1]} onSquareClick={() => handleClick(1)} />
        <Square value={squares[2]} onSquareClick={() => handleClick(2)} />
      </div>
      <div className="board-row">
        <Square value={squares[3]} onSquareClick={() => handleClick(3)} />
        <Square value={squares[4]} onSquareClick={() => handleClick(4)} />
        <Square value={squares[5]} onSquareClick={() => handleClick(5)} />
      </div>
      <div className="board-row">
        <Square value={squares[6]} onSquareClick={() => handleClick(6)} />
        <Square value={squares[7]} onSquareClick={() => handleClick(7)} />
        <Square value={squares[8]} onSquareClick={() => handleClick(8)} />
      </div>
    </>
  );
}

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}

function hasUsedAllPieces(squares, player) {
  const numMoves = squares.filter((square) => square == player).length;
  if (numMoves > 3) console.log("ERROR: numMoves is greater than 3");
  return numMoves == 3;
}

function isLegalMove(selectedSquare, newSquare, squares) {
  
  // check squares are adjacent
  const player = squares[selectedSquare]
  const oldRow = Math.floor(selectedSquare/3)
  const oldCol = selectedSquare % 3
  const newRow = Math.floor(newSquare/3)
  const newCol = newSquare % 3
  const squaresAreAdjacent = (Math.abs(oldRow - newRow) <= 1) && (Math.abs(oldCol - newCol) <= 1);
  
  // if player has used all pieces, is holding the center, and is not planning on moving the center square
  let satisfyCenterCriterion = true;
  if (hasUsedAllPieces(squares, player) && squares[4] === player && selectedSquare != 4) {
    let proposedSquares = squares.slice()
    proposedSquares[selectedSquare] = null;
    proposedSquares[newSquare] = player;
    if (!(calculateWinner(proposedSquares) === player)) {
      satisfyCenterCriterion = false;
    }
  }

  return squaresAreAdjacent && satisfyCenterCriterion;
}

export default App;
