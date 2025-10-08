document.addEventListener("DOMContentLoaded", () => {
    const cells = document.querySelectorAll(".cell");
    const statusText = document.getElementById("status");
    const resetBtn = document.getElementById("reset");

    let currentPlayer = "X";
    let boardState = Array(9).fill("");
    let gameActive = true;

    const winPatterns = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ];

    function handleClick(e) {
        const index = e.target.dataset.index;
        if (boardState[index] !== "" || !gameActive) return;

        boardState[index] = currentPlayer;
        e.target.textContent = currentPlayer;

        if (checkWinner()) {
            statusText.textContent = `Player ${currentPlayer} wins!`;
            gameActive = false;
        } else if (boardState.every(cell => cell !== "")) {
            statusText.textContent = "It's a draw!";
            gameActive = false;
        } else {
            currentPlayer = currentPlayer === "X" ? "O" : "X";
            statusText.textContent = `Player ${currentPlayer}'s turn`;
        }
    }

    function checkWinner() {
        return winPatterns.some(pattern => 
            pattern.every(index => boardState[index] === currentPlayer)
        );
    }

    function resetGame() {
        boardState.fill("");
        currentPlayer = "X";
        gameActive = true;
        statusText.textContent = `Player X's turn`;
        cells.forEach(cell => cell.textContent = "");
    }

    cells.forEach(cell => cell.addEventListener("click", handleClick));
    resetBtn.addEventListener("click", resetGame);
});
