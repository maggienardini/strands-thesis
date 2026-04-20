// unique
export const puzzle1 = {
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

// the theme is not unique - again not in original archive, but has different theme words
export const puzzle2 = {
    grid: [
        // minor cross overs within theme words & don't like spangram placement
        ["V", "E", "R", "U", "H", "C", "B", "A"],
        ["I", "R", "T", "C", "L", "K", "C", "T"],
        ["A", "A", "D", "T", "E", "S", "F", "I"],
        ["C", "R", "T", "O", "A", "N", "H", "S"],
        ["C", "E", "R", "T", "G", "R", "I", "R"],
        ["L", "E", "S", "E", "E", "G", "E", "A"]
    ],
    words: [
        { word: "STEERING", type: "theme" },
        { word: "ACCELERATOR", type: "theme" },
        { word: "CLUTCH", type: "theme" },
        { word: "GEARSHIFT", type: "theme" },
        { word: "BACKSEATDRIVER", type: "spangram" }
    ],
    theme: "In the driver's seat"
};

// unique
export const puzzle3 = {
    grid: [
        // eh... unnatural placements
       ["T", "T", "O", "O", "M", "A", "D", "M"],
       ["O", "D", "I", "A", "H", "E", "A", "S"],
       ["M", "R", "I", "P", "E", "O", "G", "I"],
       ["P", "Y", "O", "V", "L", "R", "R", "S"],
       ["I", "S", "A", "C", "X", "I", "B", "H"],
       ["G", "N", "M", "I", "M", "A", "C", "E"]
    ],
    words: [
        { word: "ADAGE", type: "theme" },
        { word: "SAYING", type: "theme" },
        { word: "MAXIM", type: "theme" },
        { word: "APHORISM", type: "theme" },
        { word: "IDIOM", type: "theme" },
        { word: "CLICHE", type: "theme" },
        { word: "MOTTO", type: "theme" },
        { word: "PROVERBS", type: "spangram" }
    ],
    theme: "Word to the wise"
};

// NOOOO theme and spangram are duplicates :( but not in original archive, and different theme words, so at least not consciously duplicated)
export const puzzle4 = {
    grid: [
        // could be better
        ["I", "L", "X", "O", "C", "R", "P", "E"],
        ["S", "A", "B", "E", "L", "A", "T", "L"],
        ["E", "N", "M", "R", "E", "T", "A", "L"],
        ["E", "N", "A", "I", "L", "M", "S", "I"],
        ["L", "V", "E", "M", "A", "T", "C", "P"],
        ["O", "P", "P", "E", "G", "A", "K", "A"]
    ],
    words: [
        { word: "PARCEL", type: "theme" },
        { word: "PACKAGE", type: "theme" },
        { word: "MAILBOX", type: "theme" },
        { word: "LETTER", type: "theme" },
        { word: "ENVELOPE", type: "theme" },
        { word: "STAMP", type: "theme" },
        { word: "SNAILMAIL", type: "spangram" }
    ],
    theme: "Signed, sealed..."
};

// unique
export const puzzle5 = {
    grid: [
            ["C", "U", "R", "P", "R", "I", "W", "E"],
            ["I", "T", "R", "O", "E", "T", "A", "G"],
            ["U", "C", "E", "W", "E", "L", "O", "C"],
            ["R", "N", "E", "R", "N", "V", "G", "A"],
            ["I", "T", "R", "A", "T", "E", "R", "B"],
            ["C", "G", "R", "I", "D", "O", "E", "L"]
]
//both these grids work! slightly prefer top one but eh
    //    ["G", "A", "T", "P", "R", "R", "T", "N"],
    //    ["E", "O", "L", "O", "U", "C", "E", "O"],
    //    ["V", "C", "L", "W", "N", "E", "R", "T"],
    //    ["I", "R", "B", "E", "E", "E", "R", "A"],
    //    ["C", "I", "T", "A", "C", "R", "G", "W"],
    //    ["U", "D", "I", "R", "G", "E", "R", "I"]
    ,
    words: [
        { word: "CIRCUIT", type: "theme" },
        { word: "VOLTAGE", type: "theme" },
        { word: "CURRENT", type: "theme" },
        { word: "WIRE", type: "theme" },
        { word: "CABLE", type: "theme" },
        { word: "GENERATOR", type: "theme" },
        { word: "POWERGRID", type: "spangram" }
    ],
    theme: "It's electric!"
};

// unique
export const puzzle6 = {
    grid: [
        ["R", "D", "E", "L", "S", "I", "A", "E"],
        ["O", "A", "I", "N", "O", "E", "H", "A"],
        ["B", "M", "R", "E", "G", "V", "R", "D"],
        ["A", "L", "I", "T", "P", "A", "A", "C"],
        ["E", "N", "T", "T", "E", "S", "O", "R"],
        ["S", "A", "A", "G", "S", "N", "Y", "R"]
        // don't like the spangram placement but eh
        // ["R", "A", "B", "T", "E", "A", "R", "R"],
        // ["S", "D", "O", "A", "N", "C", "Y", "O"],
        // ["E", "I", "G", "A", "I", "E", "L", "N"],
        // ["A", "H", "N", "G", "L", "M", "T", "S"],
        // ["T", "R", "E", "P", "A", "R", "E", "I"],
        // ["O", "V", "E", "A", "D", "S", "S", "A"]
    ],
    words: [
        { word: "GATE", type: "theme" },
        { word: "TERMINAL", type: "theme" },
        { word: "AISLE", type: "theme" },
        { word: "SEAT", type: "theme" },
        { word: "OVERHEAD", type: "theme" },
        { word: "CARRYON", type: "theme" },
        { word: "BOARDINGPASS", type: "spangram" }
    ],
    theme: "Ready for takeoff"
};

// NOT UNIQUE - but was not in the archive when i generated these lists, so at least it wasn't consciously duplicating
export const puzzle7 = {
    grid: [
        //not even gonna bother generating this
    ],
    words: [
        { word: "COUGH", type: "theme" },
        { word: "SNEEZE", type: "theme" },
        { word: "FEVER", type: "theme" },
        { word: "CHILLS", type: "theme" },
        { word: "ACHES", type: "theme" },
        { word: "TISSUE", type: "theme" },
        { word: "MUCUS", type: "spangram" },
        { word: "COMMONCOLD", type: "spangram" }
    ],
    theme: "Under the weather"
};

// unique
export const puzzle8 = {
    grid: [
        // LOVE THISSS
        ["B", "D", "N", "S", "O", "O", "O", "B"],
        ["T", "E", "H", "N", "S", "W", "L", "T"],
        ["E", "E", "O", "T", "E", "I", "N", "S"],
        ["K", "N", "A", "H", "S", "O", "E", "A"],
        ["F", "L", "H", "E", "F", "L", "F", "O"],
        ["H", "I", "T", "C", "E", "R", "O", "P"]
    ],
    words: [
        { word: "BOWLINE", type: "theme" },
        { word: "HALFHITCH", type: "theme" },
        { word: "SHEETBEND", type: "theme" },
        { word: "REEF", type: "theme" },
        { word: "NOOSE", type: "theme" },
        { word: "LOOP", type: "theme" },

        { word: "KNOTSOFAST", type: "spangram" }
    ],
    theme: "All tied up"
};

// unique but don't think this is good bc one theme word is technically two different words... only spangram can do that i think
export const puzzle9 = {
    grid: [
        // yes!
       ["S", "I", "D", "A", "S", "A", "C", "H"],
       ["K", "E", "H", "E", "I", "T", "S", "C"],
       ["I", "C", "N", "O", "V", "A", "R", "R"],
       ["C", "M", "L", "L", "I", "X", "E", "A"],
       ["K", "O", "A", "I", "P", "O", "O", "C"],
       ["V", "I", "E", "N", "L", "S", "I", "N"]
    ],
    words: [
        { word: "CHASE", type: "theme" },
        { word: "EXPLOSION", type: "theme" },
        { word: "VILLAIN", type: "theme" },
        { word: "SIDEKICK", type: "theme" },
        { word: "CARCRASH", type: "theme" },

        { word: "ACTIONMOVIE", type: "spangram" }
    ],
    theme: "Lights, camera..."
};

// unique
export const puzzle = {
    grid: [
        // YES YES YES!
        ["S", "S", "E", "R", "B", "L", "P", "I"],
        ["D", "A", "A", "T", "E", "O", "L", "M"],
        ["E", "H", "N", "L", "T", "D", "W", "R"],
        ["S", "K", "E", "B", "M", "A", "T", "A"],
        ["P", "A", "L", "T", "H", "S", "I", "L"],
        ["M", "S", "T", "E", "E", "E", "M", "A"]
    ],
    words: [
        { word: "PILLOW", type: "theme" },
        { word: "BLANKET", type: "theme" },
        { word: "SHEETS", type: "theme" },
        { word: "MATTRESS", type: "theme" },
        { word: "LAMPSHADE", type: "theme" },
        { word: "ALARM", type: "theme" },
        { word: "BEDTIME", type: "spangram" }
    ],
    theme: "Sweet dreams"
};
  