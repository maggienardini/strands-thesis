export const puzzle = {
    grid: [
        // zero overlap grid!!!!
        ["H", "S", "P", "B", "O", "O", "F", "A"],
        ["A", "M", "O", "U", "T", "L", "L", "H"],
        ["E", "G", "O", "S", "B", "O", "W", "E"],
        ["N", "O", "C", "E", "B", "A", "C", "S"],
        ["P", "E", "N", "T", "D", "L", "N", "E"],
        ["S", "H", "T", "A", "B", "E", "D", "L"]
    ],
    words: [
        { word: "SHAMPOO", type: "theme" },
        { word: "SPONGE", type: "theme" },
        { word: "LOOFAH", type: "theme" },
        { word: "TOWEL", type: "theme" },
        { word: "SCENTED", type: "theme" },
        { word: "CANDLES", type: "theme" },
        { word: "BUBBLEBATH", type: "spangram" }
    ],
    theme: "You're soaking in it!"
};

// almost perfect grid!!! only one word that crosses over itself
// L E H A E N T D
// W T O O F C E H
// B O L B S E B T
// S U B G L O P A
// H O P E N L S A
// O A M S E D N C